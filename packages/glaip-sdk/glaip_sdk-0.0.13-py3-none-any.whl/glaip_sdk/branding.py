"""AIP SDK Branding and Visual Identity.

Simple, friendly CLI branding for the GL AIP (GDP Labs AI Agent Package) SDK.

- Package name: GL AIP (GDP Labs AI Agent Package)
- Version: auto-detected (AIP_VERSION env or importlib.metadata), or passed in
- Colors: GDP Labs brand palette with NO_COLOR/AIP_NO_COLOR fallbacks

Author:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from __future__ import annotations

import os
import platform
import sys

from rich.console import Console

from glaip_sdk._version import __version__ as SDK_VERSION
from glaip_sdk.rich_components import AIPPanel

try:
    # Python 3.8+ standard way to read installed package version
    from importlib.metadata import PackageNotFoundError
    from importlib.metadata import version as pkg_version
except Exception:  # pragma: no cover
    pkg_version = None
    PackageNotFoundError = Exception


# ---- GDP Labs Brand Color Palette -----------------------------------------
PRIMARY = "#004987"  # Primary brand blue (dark blue)
SECONDARY_DARK = "#003A5C"  # Darkest variant for emphasis
SECONDARY_MEDIUM = "#005CB8"  # Medium variant for UI elements
SECONDARY_LIGHT = "#40B4E5"  # Light variant for highlights

BORDER = PRIMARY  # Keep borders aligned with primary brand tone
TITLE_STYLE = f"bold {PRIMARY}"
LABEL = "bold"


class AIPBranding:
    """GL AIP SDK branding utilities with ASCII banner and version display."""

    # GL AIP ASCII art - Modern block style with enhanced visibility
    AIP_LOGO = r"""
 ██████╗ ██╗         █████╗ ██╗██████╗
██╔════╝ ██║        ██╔══██╗██║██╔══██╗
██║  ███╗██║        ███████║██║██████╔╝
██║   ██║██║        ██╔══██║██║██╔═══╝
╚██████╔╝███████╗   ██║  ██║██║██║
 ╚═════╝ ╚══════╝   ╚═╝  ╚═╝╚═╝╚═╝
GDP Labs AI Agents Package
""".strip("\n")

    def __init__(
        self,
        version: str | None = None,
        package_name: str | None = None,
    ) -> None:
        """
        Args:
            version: Explicit SDK version (overrides auto-detection).
            package_name: If set, attempt to read version from installed package.
        """
        self.version = version or self._auto_version(package_name)
        self.console = self._make_console()

    # ---- small helpers --------------------------------------------------------
    @staticmethod
    def _auto_version(package_name: str | None) -> str:
        # Priority: env → package metadata → fallback
        env_version = os.getenv("AIP_VERSION")
        if env_version:
            return env_version
        if package_name and pkg_version:
            try:
                return pkg_version(package_name)
            except PackageNotFoundError:
                pass
        return SDK_VERSION

    @staticmethod
    def _make_console() -> Console:
        # Respect NO_COLOR/AIP_NO_COLOR environment variables
        no_color_env = (
            os.getenv("NO_COLOR") is not None or os.getenv("AIP_NO_COLOR") is not None
        )
        if no_color_env:
            color_system = None
            no_color = True
        else:
            color_system = "auto"
            no_color = False
        return Console(color_system=color_system, no_color=no_color, soft_wrap=True)

    # ---- public API -----------------------------------------------------------
    def get_welcome_banner(self) -> str:
        """Get AIP banner with version info."""
        banner = f"[{PRIMARY}]{self.AIP_LOGO}[/{PRIMARY}]"
        line = f"Version: {self.version}"
        banner = f"{banner}\n{line}"
        return banner

    def get_version_info(self) -> dict:
        return {
            "version": self.version,
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "platform": platform.platform(),
            "architecture": platform.architecture()[0],
        }

    def display_welcome_panel(self, title: str = "Welcome to AIP") -> None:
        banner = self.get_welcome_banner()
        panel = AIPPanel(
            banner,
            title=f"[{TITLE_STYLE}]{title}[/{TITLE_STYLE}]",
            border_style=BORDER,
            padding=(1, 2),
        )
        self.console.print(panel)

    def display_version_panel(self) -> None:
        v = self.get_version_info()
        version_text = (
            f"[{TITLE_STYLE}]AIP SDK Version Information[/{TITLE_STYLE}]\n\n"
            f"[{LABEL}]Version:[/] {v['version']}\n"
            f"[{LABEL}]Python:[/] {v['python_version']}\n"
            f"[{LABEL}]Platform:[/] {v['platform']}\n"
            f"[{LABEL}]Architecture:[/] {v['architecture']}"
        )
        panel = AIPPanel(
            version_text,
            title=f"[{TITLE_STYLE}]Version Details[/{TITLE_STYLE}]",
            border_style=BORDER,
            padding=(1, 2),
        )
        self.console.print(panel)

    def display_status_banner(self, status: str = "ready") -> None:
        # Keep it simple (no emoji); easy to parse in logs/CI
        banner = f"[{LABEL}]AIP[/{LABEL}] - {status.title()}"
        self.console.print(banner)

    @classmethod
    def create_from_sdk(
        cls, sdk_version: str | None = None, package_name: str | None = None
    ) -> AIPBranding:
        return cls(version=sdk_version, package_name=package_name)
