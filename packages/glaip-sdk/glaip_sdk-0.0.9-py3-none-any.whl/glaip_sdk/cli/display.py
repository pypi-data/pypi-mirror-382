"""CLI display utilities for success/failure panels and Rich renderers.

This module handles all display-related functionality for CLI commands,
including success messages, error handling, and output formatting.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

import json
from typing import Any

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from glaip_sdk.rich_components import AIPPanel

console = Console()


def display_creation_success(
    resource_type: str, resource_name: str, resource_id: str, **additional_fields: Any
) -> Panel:
    """Create standardized success message for resource creation.

    Args:
        resource_type: Type of resource (e.g., "Agent", "Tool", "MCP")
        resource_name: Name of the created resource
        resource_id: ID of the created resource
        **additional_fields: Additional fields to display

    Returns:
        Rich Panel object for display
    """
    # Build additional fields display
    fields_display = ""
    if additional_fields:
        fields_display = "\n" + "\n".join(
            f"{key}: {value}" for key, value in additional_fields.items()
        )

    return AIPPanel(
        f"[green]✅ {resource_type} '{resource_name}' created successfully![/green]\n\n"
        f"ID: {resource_id}{fields_display}",
        title=f"🤖 {resource_type} Created",
        border_style="green",
        padding=(0, 1),
    )


def display_update_success(resource_type: str, resource_name: str) -> Text:
    """Create standardized success message for resource update.

    Args:
        resource_type: Type of resource (e.g., "Agent", "Tool", "MCP")
        resource_name: Name of the updated resource

    Returns:
        Rich Text object for display
    """
    return Text(
        f"[green]✅ {resource_type} '{resource_name}' updated successfully[/green]"
    )


def display_deletion_success(resource_type: str, resource_name: str) -> Text:
    """Create standardized success message for resource deletion.

    Args:
        resource_type: Type of resource (e.g., "Agent", "Tool", "MCP")
        resource_name: Name of the deleted resource

    Returns:
        Rich Text object for display
    """
    return Text(
        f"[green]✅ {resource_type} '{resource_name}' deleted successfully[/green]"
    )


def display_api_error(error: Exception, operation: str = "operation") -> None:
    """Display standardized API error message.

    Args:
        error: The exception that occurred
        operation: Description of the operation that failed
    """
    error_type = type(error).__name__
    console.print(Text(f"[red]Error during {operation}: {error}[/red]"))
    console.print(Text(f"[dim]Error type: {error_type}[/dim]"))


def print_api_error(e: Exception) -> None:
    """Print API error with consistent formatting for both JSON and Rich views.

    Args:
        e: The exception to format and display

    Notes:
        - Extracts status_code, error_type, and payload from APIError exceptions
        - Provides consistent error reporting across CLI commands
        - Handles both JSON and Rich output formats
    """
    if hasattr(e, "__dict__"):  # Check if it's an APIError-like object
        error_info = {
            "error": str(e),
            "status_code": getattr(e, "status_code", None),
            "error_type": getattr(e, "error_type", None),
            "details": getattr(e, "payload", None),
        }

        # Filter out None values
        error_info = {k: v for k, v in error_info.items() if v is not None}

        # For JSON view, just return the structured error
        # (CLI commands handle the JSON formatting)
        if hasattr(e, "status_code"):
            console.print(f"[red]API Error: {e}[/red]")
            if hasattr(e, "status_code"):
                console.print(f"[yellow]Status: {e.status_code}[/yellow]")
            if hasattr(e, "payload"):
                console.print(f"[yellow]Details: {e.payload}[/yellow]")
        else:
            console.print(f"[red]Error: {e}[/red]")
    else:
        console.print(f"[red]Error: {e}[/red]")


_MISSING = object()


def build_resource_result_data(resource: Any, fields: list[str]) -> dict[str, Any]:
    """Return a normalized mapping of ``fields`` extracted from ``resource``."""

    result: dict[str, Any] = {}
    for field in fields:
        try:
            value = getattr(resource, field)
        except AttributeError:
            value = _MISSING
        except Exception:
            value = _MISSING

        result[field] = _normalise_field_value(field, value)

    return result


def _normalise_field_value(field: str, value: Any) -> Any:
    if value is _MISSING:
        return "N/A"
    if hasattr(value, "_mock_name"):
        return "N/A"
    if field == "id":
        return str(value)
    return value


def _get_context_object(ctx: Any) -> dict[str, Any]:
    """Get context object safely."""
    ctx_obj = getattr(ctx, "obj", {}) if ctx is not None else {}
    return ctx_obj if isinstance(ctx_obj, dict) else {}


def _should_output_json(ctx_obj: dict[str, Any]) -> bool:
    """Check if output should be in JSON format."""
    return ctx_obj.get("view") == "json"


def _build_error_output_data(error: Exception) -> dict[str, Any]:
    """Build error output data with additional error details."""
    output_data = {"error": str(error)}

    # Add additional error details if available
    if hasattr(error, "status_code"):
        output_data["status_code"] = error.status_code
    if hasattr(error, "error_type"):
        output_data["error_type"] = error.error_type
    if hasattr(error, "payload"):
        output_data["details"] = error.payload

    return output_data


def _build_success_output_data(data: Any) -> dict[str, Any]:
    """Build success output data."""
    return data if data is not None else {"success": True}


def handle_json_output(ctx: Any, data: Any = None, error: Exception = None) -> None:
    """Handle JSON output format for CLI commands.

    Args:
        ctx: Click context
        data: Data to output (for successful operations)
        error: Error to output (for failed operations)
    """
    ctx_obj = _get_context_object(ctx)

    if _should_output_json(ctx_obj):
        if error:
            output_data = _build_error_output_data(error)
        else:
            output_data = _build_success_output_data(data)

        click.echo(json.dumps(output_data, indent=2, default=str))


def handle_rich_output(ctx: Any, rich_content: Any = None) -> None:
    """Handle Rich output format for CLI commands.

    Args:
        ctx: Click context
        rich_content: Rich content to display
    """
    ctx_obj = getattr(ctx, "obj", {}) if ctx is not None else {}
    if not isinstance(ctx_obj, dict):
        ctx_obj = {}

    if ctx_obj.get("view") != "json" and rich_content:
        console.print(rich_content)


def display_confirmation_prompt(resource_type: str, resource_name: str) -> bool:
    """Display standardized confirmation prompt for destructive operations.

    Args:
        resource_type: Type of resource (e.g., "Agent", "Tool", "MCP")
        resource_name: Name of the resource

    Returns:
        True if user confirms, False otherwise
    """
    if not click.confirm(
        f"Are you sure you want to delete {resource_type.lower()} '{resource_name}'?"
    ):
        if console.is_terminal:
            console.print(Text("Deletion cancelled."))
        return False
    return True


def display_agent_run_suggestions(agent: Any) -> Panel:
    """Return a panel with post-creation suggestions for an agent."""

    return AIPPanel(
        f"[bold blue]💡 Next Steps:[/bold blue]\n\n"
        f"🚀 Start chatting with [bold]{agent.name}[/bold] right here:\n"
        f"   Type your message below and press Enter to run it immediately.\n\n"
        f"📋 Prefer the CLI instead?\n"
        f'   [green]aip agents run {agent.id} "Your message here"[/green]\n'
        f'   [green]aip agents run "{agent.name}" "Your message here"[/green]\n\n'
        f"🔧 Available options:\n"
        f"   [dim]--chat-history[/dim]  Include previous conversation\n"
        f"   [dim]--file[/dim]          Attach files\n"
        f"   [dim]--input[/dim]         Alternative input method\n"
        f"   [dim]--timeout[/dim]       Set execution timeout\n"
        f"   [dim]--save[/dim]          Save transcript to file\n"
        f"   [dim]--verbose[/dim]       Show detailed execution\n\n"
        f"💡 [dim]Input text can be positional OR use --input flag (both work!)[/dim]",
        title="🤖 Ready to Run Agent",
        border_style="blue",
        padding=(0, 1),
    )
