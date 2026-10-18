"""Unified Driver Factory for Web, Mobile, and Desktop platforms."""

from __future__ import annotations

from typing import Any, Optional

from core.drivers.web_driver import WebDriverManager
from core.drivers.mobile_driver import MobileDriverManager
from core.drivers.desktop_driver import DesktopDriverManager
from core.utils.logger import framework_logger


class DriverFactory:
    """Universal factory to instantiate platform-specific drivers."""

    @staticmethod
    def get_web_driver(
        browser: Optional[str] = None,
        headless: Optional[bool] = None,
        remote_url: Optional[str] = None,
    ) -> Any:
        return WebDriverManager.get_driver(
            browser_name=browser,
            headless=headless,
            remote_url=remote_url,
        )

    @staticmethod
    def get_mobile_driver(
        platform: Optional[str] = None,
        custom_caps: Optional[dict] = None,
        server_url: Optional[str] = None,
    ) -> Any:
        return MobileDriverManager.get_driver(
            platform_name=platform,
            custom_caps=custom_caps,
            server_url=server_url,
        )

    @staticmethod
    def get_desktop_app(
        app_path: Optional[str] = None,
        backend: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> Any:
        return DesktopDriverManager.start_application(
            app_path=app_path,
            backend=backend,
            timeout=timeout,
        )
