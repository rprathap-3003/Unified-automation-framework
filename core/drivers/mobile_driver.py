"""Appium Driver Factory for Mobile Automation (Android & iOS).

Compliant with Appium 2.x and Appium Python Client v4+.
Supports:
- Android (UiAutomator2)
- iOS (XCUITest)
- Real devices and Emulators/Simulators
- Cloud grids (SauceLabs, BrowserStack)
"""

from __future__ import annotations

from typing import Any, Dict, Optional

try:
    from appium import webdriver as appium_webdriver
    from appium.options.android import UiAutomator2Options
    from appium.options.ios import XCUITestOptions
    HAS_APPIUM = True
except ImportError:
    HAS_APPIUM = False
    appium_webdriver = None

from config.settings import settings
from core.utils.logger import framework_logger


class MobileDriverManager:
    """Manages Appium Mobile WebDriver creation and lifecycle."""

    @classmethod
    def get_driver(
        cls,
        platform_name: Optional[str] = None,
        custom_caps: Optional[Dict[str, Any]] = None,
        server_url: Optional[str] = None,
    ) -> Any:
        if not HAS_APPIUM:
            raise ImportError(
                "Appium-Python-Client is not installed. Run: pip install Appium-Python-Client"
            )

        platform = (platform_name or settings.mobile.platform).lower()
        url = server_url or settings.mobile.server_url

        framework_logger.info(
            f"Initializing Mobile Driver: platform={platform}, server={url}"
        )

        if platform == "android":
            options = cls._build_android_options(custom_caps)
        elif platform == "ios":
            options = cls._build_ios_options(custom_caps)
        else:
            raise ValueError(f"Unsupported mobile platform: '{platform}'. Choose 'android' or 'ios'.")

        driver = appium_webdriver.Remote(
            command_executor=url,
            options=options,
        )
        return driver

    @classmethod
    def _build_android_options(cls, custom_caps: Optional[Dict[str, Any]] = None) -> UiAutomator2Options:
        options = UiAutomator2Options()
        base_caps = settings.mobile.android.to_capabilities()

        if custom_caps:
            base_caps.update(custom_caps)

        # Map to UiAutomator2Options attributes
        options.load_capabilities(base_caps)
        return options

    @classmethod
    def _build_ios_options(cls, custom_caps: Optional[Dict[str, Any]] = None) -> XCUITestOptions:
        options = XCUITestOptions()
        base_caps = settings.mobile.ios.to_capabilities()

        if custom_caps:
            base_caps.update(custom_caps)

        options.load_capabilities(base_caps)
        return options
