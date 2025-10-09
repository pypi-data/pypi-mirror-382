"""MCP management commands.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

import json
import sys
from pathlib import Path
from typing import Any

import click
from rich.console import Console
from rich.text import Text

from glaip_sdk.cli.display import (
    display_api_error,
    display_confirmation_prompt,
    display_creation_success,
    display_deletion_success,
    display_update_success,
    handle_json_output,
    handle_rich_output,
)
from glaip_sdk.cli.io import (
    fetch_raw_resource_details,
)
from glaip_sdk.cli.resolution import resolve_resource_reference
from glaip_sdk.cli.utils import (
    coerce_to_row,
    detect_export_format,
    get_client,
    get_ctx_value,
    output_flags,
    output_list,
    output_result,
    spinner_context,
)
from glaip_sdk.rich_components import AIPPanel
from glaip_sdk.utils import format_datetime
from glaip_sdk.utils.serialization import (
    build_mcp_export_payload,
    write_resource_export,
)

console = Console()


@click.group(name="mcps", no_args_is_help=True)
def mcps_group() -> None:
    """MCP management operations.

    Provides commands for creating, listing, updating, deleting, and managing
    Model Context Protocol (MCP) configurations.
    """
    pass


def _resolve_mcp(
    ctx: Any, client: Any, ref: str, select: int | None = None
) -> Any | None:
    """Resolve MCP reference (ID or name) with ambiguity handling.

    Args:
        ctx: Click context object
        client: API client instance
        ref: MCP reference (ID or name)
        select: Index to select when multiple matches found

    Returns:
        MCP object if found, None otherwise

    Raises:
        ClickException: If MCP not found or selection invalid
    """
    return resolve_resource_reference(
        ctx,
        client,
        ref,
        "mcp",
        client.mcps.get_mcp_by_id,
        client.mcps.find_mcps,
        "MCP",
        select=select,
    )


@mcps_group.command(name="list")
@output_flags()
@click.pass_context
def list_mcps(ctx: Any) -> None:
    """List all MCPs in a formatted table.

    Args:
        ctx: Click context containing output format preferences

    Raises:
        ClickException: If API request fails
    """
    try:
        client = get_client(ctx)
        with spinner_context(
            ctx,
            "[bold blue]Fetching MCPs…[/bold blue]",
            console_override=console,
        ):
            mcps = client.mcps.list_mcps()

        # Define table columns: (data_key, header, style, width)
        columns = [
            ("id", "ID", "dim", 36),
            ("name", "Name", "cyan", None),
            ("config", "Config", "blue", None),
        ]

        # Transform function for safe dictionary access
        def transform_mcp(mcp: Any) -> dict[str, Any]:
            row = coerce_to_row(mcp, ["id", "name", "config"])
            # Ensure id is always a string
            row["id"] = str(row["id"])
            # Truncate config field for display
            if row["config"] != "N/A":
                row["config"] = (
                    str(row["config"])[:50] + "..."
                    if len(str(row["config"])) > 50
                    else str(row["config"])
                )
            return row

        output_list(ctx, mcps, "🔌 Available MCPs", columns, transform_mcp)

    except Exception as e:
        raise click.ClickException(str(e))


@mcps_group.command()
@click.option("--name", required=True, help="MCP name")
@click.option("--transport", required=True, help="MCP transport protocol")
@click.option("--description", help="MCP description")
@click.option("--config", help="JSON configuration string")
@output_flags()
@click.pass_context
def create(
    ctx: Any, name: str, transport: str, description: str | None, config: str | None
) -> None:
    """Create a new MCP with specified configuration.

    Args:
        ctx: Click context containing output format preferences
        name: MCP name (required)
        transport: MCP transport protocol (required)
        description: Optional MCP description
        config: JSON configuration string for MCP settings

    Raises:
        ClickException: If JSON parsing fails or API request fails
    """
    try:
        client = get_client(ctx)

        # Parse config if provided
        mcp_config = {}
        if config:
            try:
                mcp_config = json.loads(config)
            except json.JSONDecodeError:
                raise click.ClickException("Invalid JSON in --config")

        with spinner_context(
            ctx,
            "[bold blue]Creating MCP…[/bold blue]",
            console_override=console,
        ):
            mcp = client.mcps.create_mcp(
                name=name,
                type="server",  # MCPs are always server type
                transport=transport,
                description=description,
                config=mcp_config,
            )

        # Handle JSON output
        handle_json_output(ctx, mcp.model_dump())

        # Handle Rich output
        rich_panel = display_creation_success(
            "MCP",
            mcp.name,
            mcp.id,
            Type="server",
            Transport=getattr(mcp, "transport", transport),
            Description=description or "No description",
        )
        handle_rich_output(ctx, rich_panel)

    except Exception as e:
        handle_json_output(ctx, error=e)
        if get_ctx_value(ctx, "view") != "json":
            display_api_error(e, "MCP creation")
        raise click.ClickException(str(e))


def _handle_mcp_export(
    ctx: Any,
    client: Any,
    mcp: Any,
    export_path: Path,
    no_auth_prompt: bool,
    auth_placeholder: str,
) -> None:
    """Handle MCP export to file with format detection and auth handling.

    Args:
        ctx: Click context for spinner management
        client: API client for fetching MCP details
        mcp: MCP object to export
        export_path: Target file path (format detected from extension)
        no_auth_prompt: Skip interactive secret prompts if True
        auth_placeholder: Placeholder text for missing secrets

    Note:
        Supports JSON (.json) and YAML (.yaml/.yml) export formats.
        In interactive mode, prompts for secret values.
        In non-interactive mode, uses placeholder values.
    """
    # Auto-detect format from file extension
    detected_format = detect_export_format(export_path)

    # Always export comprehensive data - re-fetch with full details
    try:
        with spinner_context(
            ctx,
            "[bold blue]Fetching complete MCP details…[/bold blue]",
            console_override=console,
        ):
            mcp = client.mcps.get_mcp_by_id(mcp.id)
    except Exception as e:
        console.print(
            Text(f"[yellow]⚠️  Could not fetch full MCP details: {e}[/yellow]")
        )
        console.print(Text("[yellow]⚠️  Proceeding with available data[/yellow]"))

    # Determine if we should prompt for secrets
    prompt_for_secrets = not no_auth_prompt and sys.stdin.isatty()

    # Warn user if non-interactive mode forces placeholder usage
    if not no_auth_prompt and not sys.stdin.isatty():
        console.print(
            Text(
                "[yellow]⚠️  Non-interactive mode detected. "
                "Using placeholder values for secrets.[/yellow]"
            )
        )

    # Build and write export payload
    if prompt_for_secrets:
        # Interactive mode: no spinner during prompts
        export_payload = build_mcp_export_payload(
            mcp,
            prompt_for_secrets=prompt_for_secrets,
            placeholder=auth_placeholder,
            console=console,
        )
        with spinner_context(
            ctx,
            "[bold blue]Writing export file…[/bold blue]",
            console_override=console,
        ):
            write_resource_export(export_path, export_payload, detected_format)
    else:
        # Non-interactive mode: spinner for entire export process
        with spinner_context(
            ctx,
            "[bold blue]Exporting MCP configuration…[/bold blue]",
            console_override=console,
        ):
            export_payload = build_mcp_export_payload(
                mcp,
                prompt_for_secrets=prompt_for_secrets,
                placeholder=auth_placeholder,
                console=console,
            )
            write_resource_export(export_path, export_payload, detected_format)

    console.print(
        Text(
            f"[green]✅ Complete MCP configuration exported to: "
            f"{export_path} (format: {detected_format})[/green]"
        )
    )


def _display_mcp_details(ctx: Any, client: Any, mcp: Any) -> None:
    """Display MCP details using raw API data or fallback to Pydantic model.

    Args:
        ctx: Click context containing output format preferences
        client: API client for fetching raw MCP data
        mcp: MCP object to display details for

    Note:
        Attempts to fetch raw API data first to preserve all fields.
        Falls back to Pydantic model data if raw data unavailable.
        Formats datetime fields for better readability.
    """
    # Try to fetch raw API data first to preserve ALL fields
    with spinner_context(
        ctx,
        "[bold blue]Fetching detailed MCP data…[/bold blue]",
        console_override=console,
    ):
        raw_mcp_data = fetch_raw_resource_details(client, mcp, "mcps")

    if raw_mcp_data:
        # Use raw API data - this preserves ALL fields
        formatted_data = raw_mcp_data.copy()
        if "created_at" in formatted_data:
            formatted_data["created_at"] = format_datetime(formatted_data["created_at"])
        if "updated_at" in formatted_data:
            formatted_data["updated_at"] = format_datetime(formatted_data["updated_at"])

        output_result(
            ctx,
            formatted_data,
            title="MCP Details",
            panel_title=f"🔌 {raw_mcp_data.get('name', 'Unknown')}",
        )
    else:
        # Fall back to Pydantic model data
        console.print("[yellow]Falling back to Pydantic model data[/yellow]")
        result_data = {
            "id": str(getattr(mcp, "id", "N/A")),
            "name": getattr(mcp, "name", "N/A"),
            "type": getattr(mcp, "type", "N/A"),
            "config": getattr(mcp, "config", "N/A"),
            "status": getattr(mcp, "status", "N/A"),
            "connection_status": getattr(mcp, "connection_status", "N/A"),
        }
        output_result(
            ctx, result_data, title="MCP Details", panel_title=f"🔌 {mcp.name}"
        )


@mcps_group.command()
@click.argument("mcp_ref")
@click.option(
    "--export",
    type=click.Path(dir_okay=False, writable=True),
    help="Export complete MCP configuration to file "
    "(format auto-detected from .json/.yaml extension)",
)
@click.option(
    "--no-auth-prompt",
    is_flag=True,
    help="Skip interactive secret prompts and use placeholder values.",
)
@click.option(
    "--auth-placeholder",
    default="<INSERT VALUE>",
    show_default=True,
    help="Placeholder text used when secrets are unavailable.",
)
@output_flags()
@click.pass_context
def get(
    ctx: Any,
    mcp_ref: str,
    export: str | None,
    no_auth_prompt: bool,
    auth_placeholder: str,
) -> None:
    """Get MCP details and optionally export configuration to file.

    Args:
        ctx: Click context containing output format preferences
        mcp_ref: MCP reference (ID or name)
        export: Optional file path to export MCP configuration
        no_auth_prompt: Skip interactive secret prompts if True
        auth_placeholder: Placeholder text for missing secrets

    Raises:
        ClickException: If MCP not found or export fails

    Examples:
        aip mcps get my-mcp
        aip mcps get my-mcp --export mcp.json    # Export as JSON
        aip mcps get my-mcp --export mcp.yaml    # Export as YAML
    """
    try:
        client = get_client(ctx)

        # Resolve MCP using helper function
        mcp = _resolve_mcp(ctx, client, mcp_ref)

        # Handle export option
        if export:
            _handle_mcp_export(
                ctx, client, mcp, Path(export), no_auth_prompt, auth_placeholder
            )

        # Display MCP details
        _display_mcp_details(ctx, client, mcp)

    except Exception as e:
        raise click.ClickException(str(e))


@mcps_group.command("tools")
@click.argument("mcp_ref")
@output_flags()
@click.pass_context
def list_tools(ctx: Any, mcp_ref: str) -> None:
    """List tools available from a specific MCP.

    Args:
        ctx: Click context containing output format preferences
        mcp_ref: MCP reference (ID or name)

    Raises:
        ClickException: If MCP not found or tools fetch fails
    """
    try:
        client = get_client(ctx)

        # Resolve MCP using helper function
        mcp = _resolve_mcp(ctx, client, mcp_ref)

        # Get tools from MCP
        with spinner_context(
            ctx,
            "[bold blue]Fetching MCP tools…[/bold blue]",
            console_override=console,
        ):
            tools = client.mcps.get_mcp_tools(mcp.id)

        # Define table columns: (data_key, header, style, width)
        columns = [
            ("name", "Name", "cyan", None),
            ("description", "Description", "green", 50),
            ("type", "Type", "yellow", None),
        ]

        # Transform function for safe dictionary access
        def transform_tool(tool: dict[str, Any]) -> dict[str, Any]:
            return {
                "name": tool.get("name", "N/A"),
                "description": tool.get("description", "N/A")[:47] + "..."
                if len(tool.get("description", "")) > 47
                else tool.get("description", "N/A"),
                "type": tool.get("type", "N/A"),
            }

        output_list(
            ctx, tools, f"🔧 Tools from MCP: {mcp.name}", columns, transform_tool
        )

    except Exception as e:
        raise click.ClickException(str(e))


@mcps_group.command("connect")
@click.option(
    "--from-file",
    "config_file",
    required=True,
    help="MCP config JSON file",
)
@output_flags()
@click.pass_context
def connect(ctx: Any, config_file: str) -> None:
    """Test MCP connection using a configuration file.

    Args:
        ctx: Click context containing output format preferences
        config_file: Path to MCP configuration JSON file

    Raises:
        ClickException: If config file invalid or connection test fails

    Note:
        Loads MCP configuration from JSON file and tests connectivity.
        Displays success or failure with connection details.
    """
    try:
        client = get_client(ctx)

        # Load MCP config from file
        with open(config_file) as f:
            config = json.load(f)

        view = get_ctx_value(ctx, "view", "rich")
        if view != "json":
            console.print(
                Text(
                    f"[yellow]Connecting to MCP with config from "
                    f"{config_file}...[/yellow]"
                )
            )

        # Test connection using config
        with spinner_context(
            ctx,
            "[bold blue]Connecting to MCP…[/bold blue]",
            console_override=console,
        ):
            result = client.mcps.test_mcp_connection_from_config(config)

        view = get_ctx_value(ctx, "view", "rich")
        if view == "json":
            handle_json_output(ctx, result)
        else:
            success_panel = AIPPanel(
                f"[green]✓[/green] MCP connection successful!\n\n"
                f"[bold]Result:[/bold] {result}",
                title="🔌 Connection",
                border_style="green",
            )
            console.print(success_panel)

    except Exception as e:
        raise click.ClickException(str(e))


@mcps_group.command()
@click.argument("mcp_ref")
@click.option("--name", help="New MCP name")
@click.option("--description", help="New description")
@click.option("--config", help="JSON configuration string")
@output_flags()
@click.pass_context
def update(
    ctx: Any,
    mcp_ref: str,
    name: str | None,
    description: str | None,
    config: str | None,
) -> None:
    """Update an existing MCP with new configuration values.

    Args:
        ctx: Click context containing output format preferences
        mcp_ref: MCP reference (ID or name)
        name: New MCP name (optional)
        description: New description (optional)
        config: New JSON configuration string (optional)

    Raises:
        ClickException: If MCP not found, JSON invalid, or no fields specified

    Note:
        At least one field must be specified for update.
        Uses PUT for complete updates or PATCH for partial updates.
    """
    try:
        client = get_client(ctx)

        # Resolve MCP using helper function
        mcp = _resolve_mcp(ctx, client, mcp_ref)

        # Build update data
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if description is not None:
            update_data["description"] = description
        if config is not None:
            try:
                update_data["config"] = json.loads(config)
            except json.JSONDecodeError:
                raise click.ClickException("Invalid JSON in --config")

        if not update_data:
            raise click.ClickException("No update fields specified")

        # Update MCP (automatically chooses PUT or PATCH based on provided fields)
        with spinner_context(
            ctx,
            "[bold blue]Updating MCP…[/bold blue]",
            console_override=console,
        ):
            updated_mcp = client.mcps.update_mcp(mcp.id, **update_data)

        handle_json_output(ctx, updated_mcp.model_dump())
        handle_rich_output(ctx, display_update_success("MCP", updated_mcp.name))

    except Exception as e:
        handle_json_output(ctx, error=e)
        if get_ctx_value(ctx, "view") != "json":
            display_api_error(e, "MCP update")
        raise click.ClickException(str(e))


@mcps_group.command()
@click.argument("mcp_ref")
@click.option("-y", "--yes", is_flag=True, help="Skip confirmation")
@output_flags()
@click.pass_context
def delete(ctx: Any, mcp_ref: str, yes: bool) -> None:
    """Delete an MCP after confirmation.

    Args:
        ctx: Click context containing output format preferences
        mcp_ref: MCP reference (ID or name)
        yes: Skip confirmation prompt if True

    Raises:
        ClickException: If MCP not found or deletion fails

    Note:
        Requires confirmation unless --yes flag is provided.
        Deletion is permanent and cannot be undone.
    """
    try:
        client = get_client(ctx)

        # Resolve MCP using helper function
        mcp = _resolve_mcp(ctx, client, mcp_ref)

        # Confirm deletion
        if not yes and not display_confirmation_prompt("MCP", mcp.name):
            return

        with spinner_context(
            ctx,
            "[bold blue]Deleting MCP…[/bold blue]",
            console_override=console,
        ):
            client.mcps.delete_mcp(mcp.id)

        handle_json_output(
            ctx,
            {
                "success": True,
                "message": f"MCP '{mcp.name}' deleted",
            },
        )
        handle_rich_output(ctx, display_deletion_success("MCP", mcp.name))

    except Exception as e:
        handle_json_output(ctx, error=e)
        if get_ctx_value(ctx, "view") != "json":
            display_api_error(e, "MCP deletion")
        raise click.ClickException(str(e))
