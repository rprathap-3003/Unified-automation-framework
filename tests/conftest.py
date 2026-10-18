"""Global Pytest Fixtures, Configuration Hooks, and Driver Lifecycle Management.

Supports:
- Web: Selenium WebDriver (Chrome, Firefox, Edge, Safari, Remote Grid)
- Mobile: Appium Driver (Android UiAutomator2 & iOS XCUITest)
- Desktop: PyWinAuto Desktop Application
- API: BaseApiClient & PetStoreClient with automatic session management
- Automatic Failure Screenshots & Allure Report Attachments
"""

from __future__ import annotations

import os
from typing import Generator
import pytest

from config.settings import Settings, settings
from core.drivers.driver_factory import DriverFactory
from core.reporting.allure_listener import AllureReportHelper
from core.reporting.screenshot_manager import ScreenshotManager
from core.utils.logger import framework_logger
from api.clients.petstore_client import PetStoreClient


# ------------------------------------------------------------------------------
# Pytest CLI Options & Configuration Hooks
# ------------------------------------------------------------------------------

def pytest_addoption(parser):
    """Adds custom command-line options for test execution."""
    parser.addoption(
        "--env",
        action="store",
        default=None,
        help="Target environment (dev, staging, prod)",
    )
    parser.addoption(
        "--browser",
        action="store",
        default=None,
        help="Web browser (chrome, firefox, edge, safari)",
    )
    parser.addoption(
        "--headless",
        action="store",
        default=None,
        help="Run web browser in headless mode (true, false)",
    )
    parser.addoption(
        "--mobile-platform",
        action="store",
        default=None,
        help="Mobile OS (android, ios)",
    )
    parser.addoption(
        "--device-name",
        action="store",
        default=None,
        help="Target mobile device name or emulator ID",
    )
    parser.addoption(
        "--remote-url",
        action="store",
        default=None,
        help="Selenium Grid or Cloud Hub URL",
    )


def pytest_configure(config):
    """Initializes settings based on CLI overrides."""
    env = config.getoption("--env")
    if env:
        os.environ["ENV"] = env
        Settings.get_instance(env=env)

    # Initialize Allure environment properties
    AllureReportHelper.write_environment_properties()


# ------------------------------------------------------------------------------
# Test Failure Screenshot Hook
# ------------------------------------------------------------------------------

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Executes on test outcome. Automatically captures screenshot on failure."""
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call" and rep.failed:
        test_name = item.nodeid.replace("::", "_").replace("/", "_").replace("\\", "_")

        # Check for active driver fixtures in the failing test
        if "web_driver" in item.funcargs:
            driver = item.funcargs["web_driver"]
            ScreenshotManager.capture(driver, test_name, platform="web")

        elif "mobile_driver" in item.funcargs:
            driver = item.funcargs["mobile_driver"]
            ScreenshotManager.capture(driver, test_name, platform="mobile")

        elif "desktop_app" in item.funcargs:
            app = item.funcargs["desktop_app"]
            ScreenshotManager.capture(app, test_name, platform="desktop")


# ------------------------------------------------------------------------------
# Web Automation Fixtures (Selenium)
# ------------------------------------------------------------------------------

@pytest.fixture(scope="function")
def web_driver(request) -> Generator:
    """Provides an isolated Selenium WebDriver instance per test."""
    browser_cli = request.config.getoption("--browser")
    headless_cli = request.config.getoption("--headless")
    remote_cli = request.config.getoption("--remote-url")

    browser = browser_cli or settings.web.browser
    headless = (
        headless_cli.lower() in ("true", "1")
        if headless_cli is not None
        else settings.web.headless
    )

    driver = DriverFactory.get_web_driver(
        browser=browser,
        headless=headless,
        remote_url=remote_cli,
    )
    driver.maximize_window()
    framework_logger.info(f"Web session started: {browser} (headless={headless})")

    yield driver

    try:
        driver.quit()
        framework_logger.info("Web session terminated.")
    except Exception as exc:
        framework_logger.warning(f"Error terminating web driver: {exc}")


# ------------------------------------------------------------------------------
# Mobile Automation Fixtures (Appium)
# ------------------------------------------------------------------------------

@pytest.fixture(scope="function")
def mobile_driver(request) -> Generator:
    """Provides an isolated Appium Mobile WebDriver instance per test."""
    platform_cli = request.config.getoption("--mobile-platform")
    device_cli = request.config.getoption("--device-name")

    platform = platform_cli or settings.mobile.platform
    custom_caps = {}
    if device_cli:
        custom_caps["appium:deviceName"] = device_cli

    driver = DriverFactory.get_mobile_driver(
        platform=platform,
        custom_caps=custom_caps,
    )
    framework_logger.info(f"Mobile session started on {platform}")

    yield driver

    try:
        driver.quit()
        framework_logger.info("Mobile session terminated.")
    except Exception as exc:
        framework_logger.warning(f"Error terminating mobile driver: {exc}")


# ------------------------------------------------------------------------------
# Desktop Automation Fixtures (PyWinAuto)
# ------------------------------------------------------------------------------

@pytest.fixture(scope="function")
def desktop_app(request) -> Generator:
    """Launches and manages a desktop application instance for testing."""
    app_path = settings.desktop.sample_app_path
    backend = settings.desktop.backend

    app = DriverFactory.get_desktop_app(app_path=app_path, backend=backend)
    framework_logger.info(f"Desktop application started: {app_path}")

    yield app

    try:
        app.kill()
        framework_logger.info("Desktop application process killed.")
    except Exception as exc:
        framework_logger.warning(f"Error terminating desktop application: {exc}")


# ------------------------------------------------------------------------------
# API Automation Fixtures (Requests)
# ------------------------------------------------------------------------------

@pytest.fixture(scope="session")
def api_client() -> PetStoreClient:
    """Provides a shared API client session for REST API testing."""
    client = PetStoreClient()
    framework_logger.info("API Client session initialized.")
    return client
