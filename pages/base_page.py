"""Universal Base Page Object for Selenium WebDriver.

Encapsulates explicit waits, safe element interactions, JavaScript execution,
and diagnostic highlighting.
"""

from __future__ import annotations

import time
from typing import List, Tuple, Union
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    StaleElementReferenceException,
    TimeoutException,
)

from config.settings import settings
from core.utils.logger import framework_logger

Locator = Tuple[Union[By, str], str]


class BasePage:
    """Foundational Page Object with robust synchronization and element interactions."""

    def __init__(self, driver: webdriver.Remote, timeout: int | None = None):
        self.driver = driver
        self.timeout = timeout or settings.web.explicit_wait
        self.wait = WebDriverWait(self.driver, self.timeout)

    def open_url(self, url: str):
        framework_logger.info(f"Navigating to URL: {url}")
        self.driver.get(url)

    def get_current_url(self) -> str:
        return self.driver.current_url

    def get_title(self) -> str:
        return self.driver.title

    def find(self, locator: Locator, timeout: int | None = None) -> WebElement:
        """Finds an element waiting until it is visible on screen."""
        custom_wait = WebDriverWait(self.driver, timeout or self.timeout)
        try:
            element = custom_wait.until(EC.visibility_of_element_located(locator))
            return element
        except TimeoutException as exc:
            framework_logger.error(f"Timed out waiting for element visible: {locator}")
            raise exc

    def find_all(self, locator: Locator, timeout: int | None = None) -> List[WebElement]:
        """Finds all matching elements present in DOM."""
        custom_wait = WebDriverWait(self.driver, timeout or self.timeout)
        try:
            return custom_wait.until(EC.presence_of_all_elements_located(locator))
        except TimeoutException:
            return []

    def click(self, locator: Locator, timeout: int | None = None):
        """Waits for element to be clickable and performs click with fallback to JS click."""
        custom_wait = WebDriverWait(self.driver, timeout or self.timeout)
        try:
            element = custom_wait.until(EC.element_to_be_clickable(locator))
            self.highlight_element(element)
            element.click()
            framework_logger.debug(f"Clicked element: {locator}")
        except (ElementClickInterceptedException, StaleElementReferenceException):
            framework_logger.warning(f"Standard click failed for {locator}. Attempting JS click fallback.")
            element = self.find(locator)
            self.driver.execute_script("arguments[0].click();", element)

    def type_text(self, locator: Locator, text: str, clear: bool = True):
        """Types text into an input field after ensuring visibility."""
        element = self.find(locator)
        self.highlight_element(element)
        if clear:
            element.clear()
        element.send_keys(text)
        framework_logger.debug(f"Typed text into {locator} (length={len(text)})")

    def get_text(self, locator: Locator) -> str:
        element = self.find(locator)
        return element.text.strip()

    def get_attribute(self, locator: Locator, attribute: str) -> str | None:
        element = self.find(locator)
        return element.get_attribute(attribute)

    def is_visible(self, locator: Locator, timeout: int = 3) -> bool:
        """Non-throwing visibility check."""
        try:
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(locator))
            return True
        except TimeoutException:
            return False

    def wait_for_invisibility(self, locator: Locator, timeout: int | None = None) -> bool:
        custom_wait = WebDriverWait(self.driver, timeout or self.timeout)
        return custom_wait.until(EC.invisibility_of_element_located(locator))

    def scroll_into_view(self, locator: Locator):
        element = self.find(locator)
        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
        time.sleep(0.3)

    def highlight_element(self, element: WebElement):
        """Highlights element briefly with a red border for visual debugging."""
        try:
            self.driver.execute_script(
                "arguments[0].style.border='2px solid red';", element
            )
        except Exception:
            pass
