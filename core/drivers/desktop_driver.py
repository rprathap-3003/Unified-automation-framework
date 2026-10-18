"""Desktop Application Automation Driver Manager.

Supports:
1. PyWinAuto: High-performance native Windows UIAutomation ('uia') and legacy ('win32').
2. WinAppDriver / Appium Windows Driver: Selenium-compatible WebDriver protocol for Windows.
"""

from __future__ import annotations

import os
from typing import Any, Optional

try:
    from pywinauto import Application
    HAS_PYWINAUTO = True
except ImportError:
    HAS_PYWINAUTO = False
    Application = None

from config.settings import settings
from core.utils.logger import framework_logger


class DesktopDriverManager:
    """Manages Desktop Application lifecycle for Windows automation."""

    @classmethod
    def start_application(
        cls,
        app_path: Optional[str] = None,
        backend: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> Any:
        """Launches a desktop executable using PyWinAuto.

        Args:
            app_path: Executable path (e.g., C:\\Windows\\System32\\notepad.exe).
            backend: 'uia' (UI Automation) or 'win32'.
            timeout: Timeout in seconds for application start.

        Returns:
            pywinauto.Application instance.
        """
        if not HAS_PYWINAUTO:
            raise ImportError(
                "pywinauto is not installed. Run: pip install pywinauto"
            )

        executable = app_path or settings.desktop.sample_app_path
        mode = backend or settings.desktop.backend
        wait_time = timeout or settings.desktop.timeout

        framework_logger.info(
            f"Launching Desktop Application: path='{executable}', backend='{mode}'"
        )

        app = Application(backend=mode).start(executable, timeout=wait_time)
        return app

    @classmethod
    def connect_application(
        cls,
        title: Optional[str] = None,
        process_id: Optional[int] = None,
        path: Optional[str] = None,
        backend: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> Any:
        """Connects to an already-running desktop application.

        Args:
            title: Window title regex or exact match.
            process_id: Process ID (PID).
            path: Path to executable.
            backend: 'uia' or 'win32'.
            timeout: Wait timeout.

        Returns:
            pywinauto.Application instance.
        """
        if not HAS_PYWINAUTO:
            raise ImportError(
                "pywinauto is not installed. Run: pip install pywinauto"
            )

        mode = backend or settings.desktop.backend
        wait_time = timeout or settings.desktop.timeout

        framework_logger.info(
            f"Connecting to Desktop Application: title='{title}', pid={process_id}, path='{path}'"
        )

        kwargs = {}
        if title:
            kwargs["title_re"] = title
        if process_id:
            kwargs["process"] = process_id
        if path:
            kwargs["path"] = path

        app = Application(backend=mode).connect(**kwargs, timeout=wait_time)
        return app
