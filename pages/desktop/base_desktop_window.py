"""Base Window Object for Windows Desktop Automation (PyWinAuto).

Encapsulates control resolution, typing, clicking, menu interactions,
and window state assertions.
"""

from __future__ import annotations

import time
from typing import Any, Optional
from core.utils.logger import framework_logger


class BaseDesktopWindow:
    """Base class for Windows Desktop Applications using PyWinAuto."""

    def __init__(self, app: Any, window_title: Optional[str] = None):
        self.app = app
        self._window_title = window_title
        self._window = None

    @property
    def window(self):
        """Resolves and returns the target top-level window."""
        if self._window is None:
            if self._window_title:
                self._window = self.app.window(title_re=self._window_title)
            else:
                self._window = self.app.top_window()
        return self._window

    def wait_for_ready(self, timeout: int = 10):
        """Waits until the window is visible and enabled."""
        self.window.wait("ready", timeout=timeout)
        framework_logger.debug(f"[Desktop] Window ready: {self.window.texts()}")

    def close(self):
        """Closes the main window."""
        framework_logger.info("[Desktop] Closing application window.")
        self.window.close()

    def kill(self):
        """Terminates the application process."""
        framework_logger.info("[Desktop] Terminating application process.")
        self.app.kill()

    def click_button(self, auto_id: Optional[str] = None, title: Optional[str] = None):
        """Clicks a button by automation_id or title."""
        kwargs = {"control_type": "Button"}
        if auto_id:
            kwargs["auto_id"] = auto_id
        if title:
            kwargs["title"] = title

        btn = self.window.child_window(**kwargs)
        btn.wait("visible", timeout=5)
        btn.click_input()
        framework_logger.debug(f"[Desktop] Clicked button {kwargs}")

    def type_keys(self, keys: str, with_spaces: bool = True):
        """Types keyboard input into the focused window/control."""
        framework_logger.debug(f"[Desktop] Sending keys: {keys}")
        self.window.type_keys(keys, with_spaces=with_spaces)

    def select_menu_item(self, menu_path: str):
        """Navigates hierarchical application menu (e.g., 'File->Save As...')."""
        framework_logger.info(f"[Desktop] Selecting menu: {menu_path}")
        self.window.menu_select(menu_path)
