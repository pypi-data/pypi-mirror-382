"""Custom Rich components with copy-friendly defaults."""

from __future__ import annotations

from rich import box
from rich.panel import Panel
from rich.table import Table


class AIPPanel(Panel):
    """Rich Panel configured without vertical borders by default."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("box", box.HORIZONTALS)
        kwargs.setdefault("padding", (0, 1))
        super().__init__(*args, **kwargs)


class AIPTable(Table):
    """Rich Table configured without vertical borders by default."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("box", box.HORIZONTALS)
        kwargs.setdefault("show_edge", False)
        kwargs.setdefault("pad_edge", False)
        super().__init__(*args, **kwargs)


__all__ = ["AIPPanel", "AIPTable"]
