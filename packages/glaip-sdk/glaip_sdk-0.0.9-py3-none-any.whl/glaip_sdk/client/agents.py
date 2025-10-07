#!/usr/bin/env python3
"""Agent client for AIP SDK.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

import io
import json
import logging
from collections.abc import AsyncGenerator
from time import monotonic
from typing import Any, BinaryIO

import httpx
from rich.console import Console as _Console

from glaip_sdk.client.base import BaseClient
from glaip_sdk.config.constants import (
    DEFAULT_AGENT_FRAMEWORK,
    DEFAULT_AGENT_PROVIDER,
    DEFAULT_AGENT_RUN_TIMEOUT,
    DEFAULT_AGENT_TYPE,
    DEFAULT_AGENT_VERSION,
    DEFAULT_MODEL,
)
from glaip_sdk.exceptions import NotFoundError
from glaip_sdk.models import Agent
from glaip_sdk.utils.client_utils import (
    aiter_sse_events,
    create_model_instances,
    extract_ids,
    find_by_name,
    iter_sse_events,
    prepare_multipart_data,
)
from glaip_sdk.utils.rendering.models import RunStats
from glaip_sdk.utils.rendering.renderer import RichStreamRenderer
from glaip_sdk.utils.rendering.renderer.config import RendererConfig
from glaip_sdk.utils.validation import validate_agent_instruction

# API endpoints
AGENTS_ENDPOINT = "/agents/"

# SSE content type
SSE_CONTENT_TYPE = "text/event-stream"

# Set up module-level logger
logger = logging.getLogger("glaip_sdk.agents")


class AgentClient(BaseClient):
    """Client for agent operations."""

    def __init__(
        self,
        *,
        parent_client: BaseClient | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the agent client.

        Args:
            parent_client: Parent client to adopt session/config from
            **kwargs: Additional arguments for standalone initialization
        """
        super().__init__(parent_client=parent_client, **kwargs)

    def list_agents(
        self,
        agent_type: str | None = None,
        framework: str | None = None,
        name: str | None = None,
        version: str | None = None,
        sync_langflow_agents: bool = False,
    ) -> list[Agent]:
        """List agents with optional filtering.

        Args:
            agent_type: Filter by agent type (config, code, a2a)
            framework: Filter by framework (langchain, langgraph, google_adk)
            name: Filter by partial name match (case-insensitive)
            version: Filter by exact version match
            sync_langflow_agents: Sync with LangFlow server before listing (only applies when agent_type=langflow)

        Returns:
            List of agents matching the filters
        """
        params = {}
        if agent_type is not None:
            params["agent_type"] = agent_type
        if framework is not None:
            params["framework"] = framework
        if name is not None:
            params["name"] = name
        if version is not None:
            params["version"] = version
        if sync_langflow_agents:
            params["sync_langflow_agents"] = "true"

        if params:
            data = self._request("GET", AGENTS_ENDPOINT, params=params)
        else:
            data = self._request("GET", AGENTS_ENDPOINT)
        return create_model_instances(data, Agent, self)

    def sync_langflow_agents(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
    ) -> dict[str, Any]:
        """Sync LangFlow agents by fetching flows from the LangFlow server.

        This method synchronizes agents with LangFlow flows. It fetches all flows
        from the configured LangFlow server and creates/updates corresponding agents.

        Args:
            base_url: Custom LangFlow server base URL. If not provided, uses LANGFLOW_BASE_URL env var.
            api_key: Custom LangFlow API key. If not provided, uses LANGFLOW_API_KEY env var.

        Returns:
            Response containing sync results and statistics

        Raises:
            ValueError: If LangFlow server configuration is missing
        """
        payload = {}
        if base_url is not None:
            payload["base_url"] = base_url
        if api_key is not None:
            payload["api_key"] = api_key

        return self._request("POST", "/agents/langflow/sync", json=payload)

    def get_agent_by_id(self, agent_id: str) -> Agent:
        """Get agent by ID."""
        data = self._request("GET", f"/agents/{agent_id}")

        if isinstance(data, str):
            # Some backends may respond with plain text for missing agents.
            message = data.strip() or f"Agent '{agent_id}' not found"
            raise NotFoundError(message, status_code=404)

        if not isinstance(data, dict):
            raise NotFoundError(
                f"Agent '{agent_id}' not found (unexpected response type)",
                status_code=404,
            )

        return Agent(**data)._set_client(self)

    def find_agents(self, name: str | None = None) -> list[Agent]:
        """Find agents by name."""
        params = {}
        if name:
            params["name"] = name

        data = self._request("GET", AGENTS_ENDPOINT, params=params)
        agents = create_model_instances(data, Agent, self)
        if name is None:
            return agents
        return find_by_name(agents, name, case_sensitive=False)

    def _build_create_payload(
        self,
        name: str,
        instruction: str,
        model: str = DEFAULT_MODEL,
        tools: list[str | Any] | None = None,
        agents: list[str | Any] | None = None,
        timeout: int = DEFAULT_AGENT_RUN_TIMEOUT,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Build payload for agent creation with proper LM selection and metadata handling.

        CENTRALIZED PAYLOAD BUILDING LOGIC:
        - LM exclusivity: Uses language_model_id if provided, otherwise provider/model_name
        - Always includes required backend metadata
        - Preserves mem0 keys in agent_config
        - Handles tool/agent ID extraction from objects

        Args:
            name: Agent name
            instruction: Agent instruction
            model: Language model name (used when language_model_id not provided)
            tools: List of tools to attach
            agents: List of sub-agents to attach
            timeout: Agent execution timeout
            **kwargs: Additional parameters (language_model_id, agent_config, etc.)

        Returns:
            Complete payload dictionary for agent creation
        """
        # Prepare the creation payload with required fields
        payload: dict[str, Any] = {
            "name": name.strip(),
            "instruction": instruction.strip(),
            "type": DEFAULT_AGENT_TYPE,
            "framework": DEFAULT_AGENT_FRAMEWORK,
            "version": DEFAULT_AGENT_VERSION,
        }

        # Language model selection with exclusivity:
        # Priority: language_model_id (if provided) > provider/model_name (fallback)
        if kwargs.get("language_model_id"):
            # Use language_model_id - defer to kwargs update below
            pass
        else:
            # Use provider/model_name fallback
            payload["provider"] = DEFAULT_AGENT_PROVIDER
            payload["model_name"] = model or DEFAULT_MODEL

        # Include execution timeout if provided
        if timeout is not None:
            payload["timeout"] = str(timeout)

        # Ensure minimum required metadata for visibility
        if "metadata" not in kwargs:
            kwargs["metadata"] = {}
        if "type" not in kwargs["metadata"]:
            kwargs["metadata"]["type"] = "custom"

        # Extract IDs from tool and agent objects
        tool_ids = extract_ids(tools)
        agent_ids = extract_ids(agents)

        # Add tools and agents if provided
        if tool_ids:
            payload["tools"] = tool_ids
        if agent_ids:
            payload["agents"] = agent_ids

        # Add any additional kwargs (including language_model_id, agent_config, etc.)
        payload.update(kwargs)

        return payload

    def _build_basic_update_payload(
        self, current_agent: "Agent", name: str | None, instruction: str | None
    ) -> dict[str, Any]:
        """Build the basic update payload with required fields."""
        return {
            "name": name if name is not None else current_agent.name,
            "instruction": instruction
            if instruction is not None
            else current_agent.instruction,
            "type": DEFAULT_AGENT_TYPE,  # Required by backend
            "framework": DEFAULT_AGENT_FRAMEWORK,  # Required by backend
            "version": DEFAULT_AGENT_VERSION,  # Required by backend
        }

    def _handle_language_model_selection(
        self,
        update_data: dict[str, Any],
        current_agent: "Agent",
        model: str | None,
        language_model_id: str | None,
    ) -> None:
        """Handle language model selection with proper priority and fallbacks."""
        if language_model_id:
            # Use language_model_id if provided
            update_data["language_model_id"] = language_model_id
        elif model is not None:
            # Use explicit model parameter
            update_data["provider"] = DEFAULT_AGENT_PROVIDER
            update_data["model_name"] = model
        else:
            # Use current agent config or fallbacks
            self._set_language_model_from_current_agent(update_data, current_agent)

    def _set_language_model_from_current_agent(
        self, update_data: dict[str, Any], current_agent: "Agent"
    ) -> None:
        """Set language model from current agent config or use defaults."""
        if hasattr(current_agent, "agent_config") and current_agent.agent_config:
            agent_config = current_agent.agent_config
            if "lm_provider" in agent_config:
                update_data["provider"] = agent_config["lm_provider"]
            if "lm_name" in agent_config:
                update_data["model_name"] = agent_config["lm_name"]
        else:
            # Default fallback values
            update_data["provider"] = DEFAULT_AGENT_PROVIDER
            update_data["model_name"] = DEFAULT_MODEL

    def _handle_tools_and_agents(
        self,
        update_data: dict[str, Any],
        current_agent: "Agent",
        tools: list | None,
        agents: list | None,
    ) -> None:
        """Handle tools and agents with proper ID extraction."""
        # Handle tools
        if tools is not None:
            tool_ids = extract_ids(tools)
            update_data["tools"] = tool_ids if tool_ids else []
        else:
            update_data["tools"] = self._extract_current_tool_ids(current_agent)

        # Handle agents
        if agents is not None:
            agent_ids = extract_ids(agents)
            update_data["agents"] = agent_ids if agent_ids else []
        else:
            update_data["agents"] = self._extract_current_agent_ids(current_agent)

    def _extract_current_tool_ids(self, current_agent: "Agent") -> list[str]:
        """Extract tool IDs from current agent."""
        if current_agent.tools:
            return [
                tool["id"] if isinstance(tool, dict) else tool
                for tool in current_agent.tools
            ]
        return []

    def _extract_current_agent_ids(self, current_agent: "Agent") -> list[str]:
        """Extract agent IDs from current agent."""
        if current_agent.agents:
            return [
                agent["id"] if isinstance(agent, dict) else agent
                for agent in current_agent.agents
            ]
        return []

    def _handle_agent_config(
        self,
        update_data: dict[str, Any],
        current_agent: "Agent",
        agent_config: dict | None,
    ) -> None:
        """Handle agent_config with proper merging and cleanup."""
        if agent_config is not None:
            # Use provided agent_config, merging with current if needed
            update_data["agent_config"] = self._merge_agent_configs(
                current_agent, agent_config
            )
        elif hasattr(current_agent, "agent_config") and current_agent.agent_config:
            # Preserve existing agent_config
            update_data["agent_config"] = current_agent.agent_config.copy()
        else:
            # Default agent_config
            update_data["agent_config"] = {
                "lm_provider": DEFAULT_AGENT_PROVIDER,
                "lm_name": DEFAULT_MODEL,
                "lm_hyperparameters": {"temperature": 0.0},
            }

        # Clean LM keys from agent_config to prevent conflicts
        self._clean_agent_config_lm_keys(update_data)

    def _merge_agent_configs(self, current_agent: "Agent", new_config: dict) -> dict:
        """Merge current agent config with new config."""
        if hasattr(current_agent, "agent_config") and current_agent.agent_config:
            merged_config = current_agent.agent_config.copy()
            merged_config.update(new_config)
            return merged_config
        return new_config

    def _clean_agent_config_lm_keys(self, update_data: dict[str, Any]) -> None:
        """Remove LM keys from agent_config to prevent conflicts."""
        if "agent_config" in update_data and isinstance(
            update_data["agent_config"], dict
        ):
            agent_config = update_data["agent_config"]
            lm_keys_to_remove = {
                "lm_provider",
                "lm_name",
                "lm_base_url",
                "lm_hyperparameters",
            }
            for key in lm_keys_to_remove:
                agent_config.pop(key, None)

    def _finalize_update_payload(
        self,
        update_data: dict[str, Any],
        current_agent: "Agent",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Finalize the update payload with metadata and additional kwargs."""
        # Handle metadata preservation
        if hasattr(current_agent, "metadata") and current_agent.metadata:
            update_data["metadata"] = current_agent.metadata.copy()

        # Add any other kwargs (excluding already handled ones)
        excluded_keys = {"tools", "agents", "agent_config", "language_model_id"}
        for key, value in kwargs.items():
            if key not in excluded_keys:
                update_data[key] = value

        return update_data

    def _build_update_payload(
        self,
        current_agent: "Agent",
        name: str | None = None,
        instruction: str | None = None,
        model: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Build payload for agent update with proper LM selection and current state preservation.

        Args:
            current_agent: Current agent object to update
            name: New agent name (None to keep current)
            instruction: New instruction (None to keep current)
            model: New language model name (None to use current or fallback)
            **kwargs: Additional parameters including language_model_id, agent_config, etc.

        Returns:
            Complete payload dictionary for agent update

        Notes:
            - LM exclusivity: Uses language_model_id if provided, otherwise provider/model_name
            - Preserves current values as defaults when new values not provided
            - Handles tools/agents updates with proper ID extraction
        """
        # Build basic payload
        update_data = self._build_basic_update_payload(current_agent, name, instruction)

        # Handle language model selection
        language_model_id = kwargs.get("language_model_id")
        self._handle_language_model_selection(
            update_data, current_agent, model, language_model_id
        )

        # Handle tools and agents
        tools = kwargs.get("tools")
        agents = kwargs.get("agents")
        self._handle_tools_and_agents(update_data, current_agent, tools, agents)

        # Handle agent config
        agent_config = kwargs.get("agent_config")
        self._handle_agent_config(update_data, current_agent, agent_config)

        # Finalize payload
        return self._finalize_update_payload(update_data, current_agent, **kwargs)

    def create_agent(
        self,
        name: str,
        instruction: str,
        model: str = DEFAULT_MODEL,
        tools: list[str | Any] | None = None,
        agents: list[str | Any] | None = None,
        timeout: int = DEFAULT_AGENT_RUN_TIMEOUT,
        **kwargs: Any,
    ) -> "Agent":
        """Create a new agent."""
        # Client-side validation
        if not name or not name.strip():
            raise ValueError("Agent name cannot be empty or whitespace")

        # Validate instruction using centralized validation
        instruction = validate_agent_instruction(instruction)

        # Build payload using centralized builder
        payload = self._build_create_payload(
            name=name,
            instruction=instruction,
            model=model,
            tools=tools,
            agents=agents,
            timeout=timeout,
            **kwargs,
        )

        # Create the agent and fetch full details
        full_agent_data = self._post_then_fetch(
            id_key="id",
            post_endpoint=AGENTS_ENDPOINT,
            get_endpoint_fmt=f"{AGENTS_ENDPOINT}{{id}}",
            json=payload,
        )
        return Agent(**full_agent_data)._set_client(self)

    def update_agent(
        self,
        agent_id: str,
        name: str | None = None,
        instruction: str | None = None,
        model: str | None = None,
        **kwargs: Any,
    ) -> "Agent":
        """Update an existing agent."""
        # First, get the current agent data
        current_agent = self.get_agent_by_id(agent_id)

        # Build payload using centralized builder
        update_data = self._build_update_payload(
            current_agent=current_agent,
            name=name,
            instruction=instruction,
            model=model,
            **kwargs,
        )

        # Send the complete payload
        data = self._request("PUT", f"/agents/{agent_id}", json=update_data)
        return Agent(**data)._set_client(self)

    def delete_agent(self, agent_id: str) -> None:
        """Delete an agent."""
        self._request("DELETE", f"/agents/{agent_id}")

    def _prepare_sync_request_data(
        self,
        message: str,
        files: list[str | BinaryIO] | None,
        tty: bool,
        **kwargs: Any,
    ) -> tuple[dict | None, dict | None, list | None, dict, Any | None]:
        """Prepare request data for synchronous agent runs with renderer support.

        Args:
            message: Message to send
            files: Optional files to include
            tty: Whether to enable TTY mode
            **kwargs: Additional request parameters

        Returns:
            Tuple of (payload, data_payload, files_payload, headers, multipart_data)
        """
        headers = {"Accept": SSE_CONTENT_TYPE}

        if files:
            # Handle multipart data for file uploads
            multipart_data = prepare_multipart_data(message, files)
            if "chat_history" in kwargs and kwargs["chat_history"] is not None:
                multipart_data.data["chat_history"] = kwargs["chat_history"]
            if "pii_mapping" in kwargs and kwargs["pii_mapping"] is not None:
                multipart_data.data["pii_mapping"] = kwargs["pii_mapping"]

            return (
                None,
                multipart_data.data,
                multipart_data.files,
                headers,
                multipart_data,
            )
        else:
            # Simple JSON payload for text-only requests
            payload = {"input": message, "stream": True, **kwargs}
            if tty:
                payload["tty"] = True
            return payload, None, None, headers, None

    def _get_timeout_values(
        self, timeout: float | None, **kwargs: Any
    ) -> tuple[float, float]:
        """Get request timeout and execution timeout values.

        Args:
            timeout: Request timeout (overrides instance timeout)
            **kwargs: Additional parameters including execution timeout

        Returns:
            Tuple of (request_timeout, execution_timeout)
        """
        request_timeout = timeout or self.timeout
        execution_timeout = kwargs.get("timeout", DEFAULT_AGENT_RUN_TIMEOUT)
        return request_timeout, execution_timeout

    def _create_renderer(
        self, renderer: RichStreamRenderer | None, **kwargs: Any
    ) -> RichStreamRenderer:
        """Create appropriate renderer based on configuration."""
        if isinstance(renderer, RichStreamRenderer):
            return renderer

        verbose = kwargs.get("verbose", False)

        if isinstance(renderer, str):
            if renderer == "silent":
                return self._create_silent_renderer()
            elif renderer == "minimal":
                return self._create_minimal_renderer()
            else:
                return self._create_default_renderer(verbose)
        elif verbose:
            return self._create_verbose_renderer()
        else:
            return self._create_default_renderer(verbose)

    def _create_silent_renderer(self) -> RichStreamRenderer:
        """Create a silent renderer that suppresses all output."""
        silent_config = RendererConfig(
            live=False,
            persist_live=False,
            show_delegate_tool_panels=False,
            render_thinking=False,
        )
        return RichStreamRenderer(
            console=_Console(file=io.StringIO(), force_terminal=False),
            cfg=silent_config,
            verbose=False,
        )

    def _create_minimal_renderer(self) -> RichStreamRenderer:
        """Create a minimal renderer with basic output."""
        minimal_config = RendererConfig(
            live=False,
            persist_live=False,
            show_delegate_tool_panels=False,
            render_thinking=False,
        )
        return RichStreamRenderer(
            console=_Console(),
            cfg=minimal_config,
            verbose=False,
        )

    def _create_verbose_renderer(self) -> RichStreamRenderer:
        """Create a verbose renderer for detailed output."""
        verbose_config = RendererConfig(
            theme="dark",
            style="debug",
            live=False,
            show_delegate_tool_panels=True,
            append_finished_snapshots=False,
        )
        return RichStreamRenderer(
            console=_Console(),
            cfg=verbose_config,
            verbose=True,
        )

    def _create_default_renderer(self, verbose: bool) -> RichStreamRenderer:
        """Create the default renderer."""
        if verbose:
            return self._create_verbose_renderer()
        else:
            default_config = RendererConfig(show_delegate_tool_panels=True)
            return RichStreamRenderer(console=_Console(), cfg=default_config)

    def _initialize_stream_metadata(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        """Initialize stream metadata."""
        return {
            "agent_name": kwargs.get("agent_name", ""),
            "model": kwargs.get("model"),
            "run_id": None,
            "input_message": "",  # Will be set from kwargs if available
        }

    def _capture_request_id(
        self,
        stream_response: httpx.Response,
        meta: dict[str, Any],
        renderer: RichStreamRenderer,
    ) -> None:
        """Capture request ID from response headers."""
        req_id = stream_response.headers.get(
            "x-request-id"
        ) or stream_response.headers.get("x-run-id")
        if req_id:
            meta["run_id"] = req_id
            renderer.on_start(meta)

    def _should_start_timer(self, ev: dict[str, Any]) -> bool:
        """Check if timer should be started for this event."""
        return "content" in ev or "status" in ev or ev.get("metadata")

    def _handle_content_event(self, ev: dict[str, Any], final_text: str) -> str:
        """Handle content events."""
        content = ev.get("content", "")
        if not content.startswith("Artifact received:"):
            return content
        return final_text

    def _handle_usage_event(
        self, ev: dict[str, Any], stats_usage: dict[str, Any]
    ) -> None:
        """Handle usage events."""
        stats_usage.update(ev.get("usage") or {})

    def _handle_run_info_event(
        self, ev: dict[str, Any], meta: dict[str, Any], renderer: RichStreamRenderer
    ) -> None:
        """Handle run info events."""
        if ev.get("model"):
            meta["model"] = ev["model"]
            renderer.on_start(meta)
        if ev.get("run_id"):
            meta["run_id"] = ev["run_id"]
            renderer.on_start(meta)

    def _process_single_event(
        self,
        event: dict[str, Any],
        renderer: RichStreamRenderer,
        final_text: str,
        stats_usage: dict[str, Any],
        meta: dict[str, Any],
    ) -> tuple[str, dict[str, Any]]:
        """Process a single streaming event."""
        try:
            ev = json.loads(event["data"])
        except json.JSONDecodeError:
            logger.debug("Non-JSON SSE fragment skipped")
            return final_text, stats_usage

        kind = (ev.get("metadata") or {}).get("kind")
        renderer.on_event(ev)

        # Skip artifacts from content accumulation
        if kind == "artifact":
            return final_text, stats_usage

        # Handle different event types
        if kind == "final_response" and ev.get("content"):
            final_text = ev.get("content", "")
        elif ev.get("content"):
            final_text = self._handle_content_event(ev, final_text)
        elif kind == "usage":
            self._handle_usage_event(ev, stats_usage)
        elif kind == "run_info":
            self._handle_run_info_event(ev, meta, renderer)

        return final_text, stats_usage

    def _process_stream_events(
        self,
        stream_response: httpx.Response,
        renderer: RichStreamRenderer,
        timeout_seconds: float,
        agent_name: str | None,
        kwargs: dict[str, Any],
    ) -> tuple[str, dict[str, Any], float | None, float | None]:
        """Process streaming events and accumulate response."""
        final_text = ""
        stats_usage = {}
        started_monotonic = None
        finished_monotonic = None

        meta = self._initialize_stream_metadata(kwargs)
        self._capture_request_id(stream_response, meta, renderer)

        for event in iter_sse_events(stream_response, timeout_seconds, agent_name):
            # Start timer at first meaningful event
            if started_monotonic is None:
                try:
                    ev = json.loads(event["data"])
                    if self._should_start_timer(ev):
                        started_monotonic = monotonic()
                except json.JSONDecodeError:
                    pass

            final_text, stats_usage = self._process_single_event(
                event, renderer, final_text, stats_usage, meta
            )

        finished_monotonic = monotonic()
        return final_text, stats_usage, started_monotonic, finished_monotonic

    def run_agent(
        self,
        agent_id: str,
        message: str,
        files: list[str | BinaryIO] | None = None,
        tty: bool = False,
        *,
        renderer: RichStreamRenderer | str | None = "auto",
        **kwargs,
    ) -> str:
        """Run an agent with a message, streaming via a renderer."""
        # Prepare request payload and headers
        (
            payload,
            data_payload,
            files_payload,
            headers,
            multipart_data,
        ) = self._prepare_sync_request_data(message, files, tty, **kwargs)

        # Create renderer
        r = self._create_renderer(renderer, **kwargs)

        # Initialize renderer
        meta = {
            "agent_name": kwargs.get("agent_name", agent_id),
            "model": kwargs.get("model"),
            "run_id": None,
            "input_message": message,
        }
        r.on_start(meta)

        try:
            # Make streaming request
            response = self.http_client.stream(
                "POST",
                f"/agents/{agent_id}/run",
                json=payload,
                data=data_payload,
                files=files_payload,
                headers=headers,
            )

            with response as stream_response:
                stream_response.raise_for_status()

                # Process streaming events
                timeout_seconds = kwargs.get("timeout", DEFAULT_AGENT_RUN_TIMEOUT)
                agent_name = kwargs.get("agent_name")

                (
                    final_text,
                    stats_usage,
                    started_monotonic,
                    finished_monotonic,
                ) = self._process_stream_events(
                    stream_response, r, timeout_seconds, agent_name, kwargs
                )

        except KeyboardInterrupt:
            try:
                r.close()
            finally:
                raise
        except Exception:
            try:
                r.close()
            finally:
                raise
        finally:
            # Ensure cleanup
            if multipart_data:
                multipart_data.close()

        # Finalize and return result
        st = RunStats()
        st.started_at = started_monotonic or st.started_at
        st.finished_at = finished_monotonic or st.started_at
        st.usage = stats_usage

        # Get final content
        if hasattr(r, "state") and hasattr(r.state, "buffer"):
            rendered_text = "".join(r.state.buffer)
        else:
            rendered_text = ""

        final_payload = final_text or rendered_text or "No response content received."
        r.on_complete(st)
        return final_payload

    def _prepare_request_data(
        self,
        message: str,
        files: list[str | BinaryIO] | None,
        **kwargs,
    ) -> tuple[dict | None, dict | None, dict | None, dict | None]:
        """Prepare request data for async agent runs.

        Returns:
            Tuple of (payload, data_payload, files_payload, headers)
        """
        if files:
            # Handle multipart data for file uploads
            multipart_data = prepare_multipart_data(message, files)
            # Inject optional multipart extras expected by backend
            if "chat_history" in kwargs and kwargs["chat_history"] is not None:
                multipart_data.data["chat_history"] = kwargs["chat_history"]
            if "pii_mapping" in kwargs and kwargs["pii_mapping"] is not None:
                multipart_data.data["pii_mapping"] = kwargs["pii_mapping"]

            headers = {"Accept": SSE_CONTENT_TYPE}
            return None, multipart_data.data, multipart_data.files, headers
        else:
            # Simple JSON payload for text-only requests
            payload = {"input": message, "stream": True, **kwargs}
            headers = {"Accept": SSE_CONTENT_TYPE}
            return payload, None, None, headers

    def _create_async_client_config(
        self, timeout: float | None, headers: dict | None
    ) -> dict:
        """Create async client configuration with proper headers and timeout."""
        config = self._build_async_client(timeout or self.timeout)
        if headers:
            config["headers"] = {**config["headers"], **headers}
        return config

    async def _stream_agent_response(
        self,
        async_client: httpx.AsyncClient,
        agent_id: str,
        payload: dict | None,
        data_payload: dict | None,
        files_payload: dict | None,
        headers: dict | None,
        timeout_seconds: float,
        agent_name: str | None,
    ) -> AsyncGenerator[dict, None]:
        """Stream the agent response and yield parsed JSON chunks."""
        async with async_client.stream(
            "POST",
            f"/agents/{agent_id}/run",
            json=payload,
            data=data_payload,
            files=files_payload,
            headers=headers,
        ) as stream_response:
            stream_response.raise_for_status()

            async for event in aiter_sse_events(
                stream_response, timeout_seconds, agent_name
            ):
                try:
                    chunk = json.loads(event["data"])
                    yield chunk
                except json.JSONDecodeError:
                    logger.debug("Non-JSON SSE fragment skipped")
                    continue

    async def arun_agent(
        self,
        agent_id: str,
        message: str,
        files: list[str | BinaryIO] | None = None,
        *,
        timeout: float | None = None,
        **kwargs,
    ) -> AsyncGenerator[dict, None]:
        """Async run an agent with a message, yielding streaming JSON chunks.

        Args:
            agent_id: ID of the agent to run
            message: Message to send to the agent
            files: Optional list of files to include
            timeout: Request timeout in seconds
            **kwargs: Additional arguments (chat_history, pii_mapping, etc.)

        Yields:
            Dictionary containing parsed JSON chunks from the streaming response

        Raises:
            AgentTimeoutError: When agent execution times out
            httpx.TimeoutException: When general timeout occurs
            Exception: For other unexpected errors
        """
        # Prepare request data
        payload, data_payload, files_payload, headers = self._prepare_request_data(
            message, files, **kwargs
        )

        # Create async client configuration
        async_client_config = self._create_async_client_config(timeout, headers)

        # Get execution timeout for streaming control
        timeout_seconds = kwargs.get("timeout", DEFAULT_AGENT_RUN_TIMEOUT)
        agent_name = kwargs.get("agent_name")

        try:
            # Create async client and stream response
            async with httpx.AsyncClient(**async_client_config) as async_client:
                async for chunk in self._stream_agent_response(
                    async_client,
                    agent_id,
                    payload,
                    data_payload,
                    files_payload,
                    headers,
                    timeout_seconds,
                    agent_name,
                ):
                    yield chunk

        finally:
            # Ensure cleanup - this is handled by the calling context
            # but we keep this for safety in case of future changes
            pass
