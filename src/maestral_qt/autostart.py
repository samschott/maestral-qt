# -*- coding: utf-8 -*-

# system imports
import sys
import platform
from typing import Optional

# external imports
from maestral.autostart import (
    AutoStartBase,
    AutoStartLaunchd,
    AutoStartXDGDesktop,
    SupportedImplementations,
    get_command_path,
)
from maestral.constants import BUNDLE_ID, FROZEN


class AutoStart:
    """Creates auto-start files in the appropriate system location to automatically
    start Maestral when the user logs in. Supports launchd on macOS and XDG desktop
    entries on Linux."""

    _impl: AutoStartBase

    def __init__(self, config_name: str) -> None:
        self.implementation = self._get_available_implementation()

        if FROZEN:
            start_cmd = [sys.executable, "--config-name", config_name]
        else:
            command_location = get_command_path("maestral-qt", "maestral_qt")
            start_cmd = [command_location, "--config-name", config_name]

        if self.implementation == SupportedImplementations.launchd:
            self._impl = AutoStartLaunchd(
                f"{BUNDLE_ID}.{config_name}", " ".join(start_cmd)
            )

        elif self.implementation == SupportedImplementations.xdg_desktop:
            additional_keys = {
                "Icon": "maestral",
                "X-GNOME-Autostart-enabled": "true",
                "X-GNOME-Autostart-Delay": "2",
                "X-KDE-autostart-after": "panel",
            }

            self._impl = AutoStartXDGDesktop(
                filename=f"maestral-{config_name}.desktop",
                app_name="Maestral",
                start_cmd=" ".join(start_cmd),
                **additional_keys,
            )
        else:
            self._impl = AutoStartBase()

    @property
    def enabled(self) -> bool:
        """True if autostart is enabled."""
        return self._impl.enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        if value:
            self.enable()
        else:
            self.disable()

    def toggle(self) -> None:
        """Toggles autostart on or off."""
        if self.enabled:
            self.disable()
        else:
            self.enable()

    def enable(self) -> None:
        """Setter: True if autostart is enabled."""
        if self.enabled:
            return
        self._impl.enable()

    def disable(self) -> None:
        """Setter: True if autostart is enabled."""
        if not self.enabled:
            return
        self._impl.disable()

    def _get_available_implementation(self) -> Optional[SupportedImplementations]:
        """Returns the supported implementation depending on the platform."""
        system = platform.system()

        if system == "Darwin":
            return SupportedImplementations.launchd
        elif system == "Linux":
            return SupportedImplementations.xdg_desktop
        else:
            return None
