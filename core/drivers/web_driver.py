"""Selenium WebDriver Factory for Web Automation.

Supports:
- Chrome, Firefox, Edge, Safari
- Headless execution
- Selenium Grid / Remote WebDrivers
- Custom preferences (downloads, notification suppression)
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService

try:
    from webdriver_manager.chrome import ChromeDriverManager
    from webdriver_manager.firefox import GeckoDriverManager
    from webdriver_manager.microsoft import EdgeChromiumDriverManager
    HAS_WDM = True
except ImportError:
    HAS_WDM = False

from config.settings import settings
from core.utils.logger import framework_logger


class WebDriverManager:
    """Instantiates and configures Selenium WebDrivers."""

    @classmethod
    def get_driver(
        cls,
        browser_name: Optional[str] = None,
        headless: Optional[bool] = None,
        remote_url: Optional[str] = None,
    ) -> webdriver.Remote:
        browser = (browser_name or settings.web.browser).lower()
        is_headless = headless if headless is not None else settings.web.headless
        grid_url = remote_url or settings.web.remote_url

        framework_logger.info(
            f"Initializing WebDriver: browser={browser}, headless={is_headless}, remote={bool(grid_url)}"
        )

        if grid_url:
            return cls._create_remote_driver(browser, is_headless, grid_url)

        if browser == "chrome":
            return cls._create_chrome_driver(is_headless)
        elif browser == "firefox":
            return cls._create_firefox_driver(is_headless)
        elif browser == "edge":
            return cls._create_edge_driver(is_headless)
        elif browser == "safari":
            return cls._create_safari_driver()
        else:
            raise ValueError(
                f"Unsupported browser: '{browser}'. Choose from: chrome, firefox, edge, safari."
            )

    @classmethod
    def _create_chrome_driver(cls, headless: bool) -> webdriver.Chrome:
        options = ChromeOptions()
        if headless:
            options.add_argument("--headless=new")

        # Standard stability flags
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument(f"--window-size={settings.web.window_width},{settings.web.window_height}")
        options.add_argument("--disable-notifications")
        options.add_argument("--remote-allow-origins=*")

        # Custom download directory
        download_path = Path(settings.web.download_dir).resolve()
        download_path.mkdir(parents=True, exist_ok=True)
        prefs = {
            "download.default_directory": str(download_path),
            "download.prompt_for_download": False,
            "profile.default_content_setting_values.notifications": 2,
        }
        options.add_experimental_option("prefs", prefs)

        if HAS_WDM:
            try:
                service = ChromeService(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=options)
            except Exception as e:
                framework_logger.warning(f"ChromeDriverManager install failed, falling back to system PATH: {e}")
                driver = webdriver.Chrome(options=options)
        else:
            driver = webdriver.Chrome(options=options)

        cls._apply_timeouts(driver)
        return driver

    @classmethod
    def _create_firefox_driver(cls, headless: bool) -> webdriver.Firefox:
        options = FirefoxOptions()
        if headless:
            options.add_argument("-headless")
        options.add_argument(f"--width={settings.web.window_width}")
        options.add_argument(f"--height={settings.web.window_height}")

        if HAS_WDM:
            try:
                service = FirefoxService(GeckoDriverManager().install())
                driver = webdriver.Firefox(service=service, options=options)
            except Exception as e:
                framework_logger.warning(f"GeckoDriverManager install failed, falling back to system PATH: {e}")
                driver = webdriver.Firefox(options=options)
        else:
            driver = webdriver.Firefox(options=options)

        cls._apply_timeouts(driver)
        return driver

    @classmethod
    def _create_edge_driver(cls, headless: bool) -> webdriver.Edge:
        options = EdgeOptions()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument(f"--window-size={settings.web.window_width},{settings.web.window_height}")
        options.add_argument("--disable-gpu")

        if HAS_WDM:
            try:
                service = EdgeService(EdgeChromiumDriverManager().install())
                driver = webdriver.Edge(service=service, options=options)
            except Exception as e:
                framework_logger.warning(f"EdgeDriverManager install failed, falling back to system PATH: {e}")
                driver = webdriver.Edge(options=options)
        else:
            driver = webdriver.Edge(options=options)

        cls._apply_timeouts(driver)
        return driver

    @classmethod
    def _create_safari_driver(cls) -> webdriver.Safari:
        driver = webdriver.Safari()
        cls._apply_timeouts(driver)
        return driver

    @classmethod
    def _create_remote_driver(
        cls, browser: str, headless: bool, grid_url: str
    ) -> webdriver.Remote:
        if browser == "chrome":
            options = ChromeOptions()
            if headless:
                options.add_argument("--headless=new")
        elif browser == "firefox":
            options = FirefoxOptions()
            if headless:
                options.add_argument("-headless")
        elif browser == "edge":
            options = EdgeOptions()
            if headless:
                options.add_argument("--headless=new")
        else:
            options = ChromeOptions()

        driver = webdriver.Remote(command_executor=grid_url, options=options)
        cls._apply_timeouts(driver)
        return driver

    @classmethod
    def _apply_timeouts(cls, driver: webdriver.Remote):
        driver.set_page_load_timeout(settings.web.page_load_timeout)
        if settings.web.implicit_wait > 0:
            driver.implicitly_wait(settings.web.implicit_wait)
