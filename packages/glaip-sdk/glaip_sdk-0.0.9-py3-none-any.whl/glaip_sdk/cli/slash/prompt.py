"""prompt_toolkit integration helpers for the slash session.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING, Any

_HAS_PROMPT_TOOLKIT = False

try:  # pragma: no cover - optional dependency
    from prompt_toolkit import PromptSession
    from prompt_toolkit.completion import Completer, Completion
    from prompt_toolkit.formatted_text import FormattedText
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.patch_stdout import patch_stdout
    from prompt_toolkit.styles import Style

    _HAS_PROMPT_TOOLKIT = True
except Exception:  # pragma: no cover - optional dependency
    PromptSession = None  # type: ignore[assignment]
    Completer = None  # type: ignore[assignment]
    Completion = None  # type: ignore[assignment]
    FormattedText = None  # type: ignore[assignment]
    KeyBindings = None  # type: ignore[assignment]
    Style = None  # type: ignore[assignment]
    patch_stdout = None  # type: ignore[assignment]

if TYPE_CHECKING:  # pragma: no cover - typing only
    from .session import SlashSession


if _HAS_PROMPT_TOOLKIT:

    class SlashCompleter(Completer):
        """Provide slash command completions inside the prompt."""

        def __init__(self, session: SlashSession) -> None:
            self._session = session

        def get_completions(
            self,
            document: Any,
            _complete_event: Any,  # type: ignore[no-any-return]
        ) -> Iterable[Completion]:  # pragma: no cover - UI
            if Completion is None:
                return

            text = document.text_before_cursor or ""
            if not text.startswith("/") or " " in text:
                return

            yield from _iter_command_completions(self._session, text)
            yield from _iter_contextual_completions(self._session, text)

else:  # pragma: no cover - fallback when prompt_toolkit is missing

    class SlashCompleter:  # type: ignore[too-many-ancestors]
        def __init__(self, session: SlashSession) -> None:  # noqa: D401 - stub
            self._session = session


def setup_prompt_toolkit(
    session: SlashSession,
    *,
    interactive: bool,
) -> tuple[Any | None, Any | None]:
    """Configure prompt_toolkit session and style for interactive mode."""

    if not (interactive and _HAS_PROMPT_TOOLKIT):
        return None, None

    if PromptSession is None or Style is None:
        return None, None

    bindings = _create_key_bindings()

    prompt_session = PromptSession(
        completer=SlashCompleter(session),
        complete_while_typing=True,
        key_bindings=bindings,
    )
    prompt_style = Style.from_dict(
        {
            "prompt": "bg:#0f172a #facc15 bold",
            "": "bg:#0f172a #e2e8f0",
            "placeholder": "bg:#0f172a #94a3b8 italic",
        }
    )

    return prompt_session, prompt_style


def _create_key_bindings() -> Any:
    """Create prompt_toolkit key bindings for the command palette."""

    if KeyBindings is None:
        return None

    bindings = KeyBindings()

    def _refresh_completions(buffer: Any) -> None:  # type: ignore[no-any-return]
        text = buffer.document.text_before_cursor or ""
        if text.startswith("/") and " " not in text:
            buffer.start_completion(select_first=False)
        elif buffer.complete_state is not None:
            buffer.cancel_completion()

    @bindings.add("/")  # type: ignore[misc]
    def _trigger_slash_completion(event: Any) -> None:  # pragma: no cover - UI
        buffer = event.app.current_buffer
        buffer.insert_text("/")
        _refresh_completions(buffer)

    @bindings.add("backspace")  # type: ignore[misc]
    def _handle_backspace(event: Any) -> None:  # pragma: no cover - UI
        buffer = event.app.current_buffer
        if buffer.document.cursor_position > 0:
            buffer.delete_before_cursor()
        _refresh_completions(buffer)

    @bindings.add("c-h")  # type: ignore[misc]
    def _handle_ctrl_h(event: Any) -> None:  # pragma: no cover - UI
        buffer = event.app.current_buffer
        if buffer.document.cursor_position > 0:
            buffer.delete_before_cursor()
        _refresh_completions(buffer)

    return bindings


def _iter_command_completions(
    session: SlashSession, text: str
) -> Iterable[Completion]:  # pragma: no cover - thin wrapper
    prefix = text[1:]
    seen: set[str] = set()

    if (
        session.get_contextual_commands()
        and not session.should_include_global_commands()
    ):
        return []

    commands = sorted(session._unique_commands.values(), key=lambda c: c.name)

    for cmd in commands:
        for alias in (cmd.name, *cmd.aliases):
            if alias in seen or alias.startswith("?"):
                continue
            if prefix and not alias.startswith(prefix):
                continue
            seen.add(alias)
            label = f"/{alias}"
            yield Completion(
                text=label,
                start_position=-len(text),
                display=label,
                display_meta=cmd.help,
            )


def _iter_contextual_completions(
    session: SlashSession, text: str
) -> Iterable[Completion]:  # pragma: no cover - thin wrapper
    prefix = text[1:]
    seen: set[str] = set()

    contextual_commands = sorted(
        session.get_contextual_commands().items(), key=lambda item: item[0]
    )

    for alias, help_text in contextual_commands:
        if alias in seen:
            continue
        if prefix and not alias.startswith(prefix):
            continue
        seen.add(alias)
        label = f"/{alias}"
        yield Completion(
            text=label,
            start_position=-len(text),
            display=label,
            display_meta=help_text,
        )


__all__ = [
    "SlashCompleter",
    "setup_prompt_toolkit",
    "FormattedText",
    "patch_stdout",
    "PromptSession",
    "Style",
    "_HAS_PROMPT_TOOLKIT",
]
