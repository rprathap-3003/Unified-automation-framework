"""Base Screen Object for Mobile Automation (Appium Android & iOS).

Encapsulates touch gestures, swipe, scroll, keyboard dismissal,
and native mobile OS interactions.
"""

from __future__ import annotations

import time
from typing import Tuple, Union
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

from config.settings import settings
from core.utils.logger import framework_logger

Locator = Tuple[Union[By, str], str]


class BaseMobileScreen:
    """Foundational Mobile Screen Object with touch gestures and lifecycle helpers."""

    def __init__(self, driver, timeout: int | None = None):
        self.driver = driver
        self.timeout = timeout or settings.mobile.explicit_wait
        self.wait = WebDriverWait(self.driver, self.timeout)

    def find_element(self, locator: Locator, timeout: int | None = None):
        custom_wait = WebDriverWait(self.driver, timeout or self.timeout)
        try:
            return custom_wait.until(EC.visibility_of_element_located(locator))
        except TimeoutException as exc:
            framework_logger.error(f"[Mobile] Timed out waiting for element: {locator}")
            raise exc

    def tap(self, locator: Locator, timeout: int | None = None):
        element = self.find_element(locator, timeout=timeout)
        element.click()
        framework_logger.debug(f"[Mobile] Tapped element: {locator}")

    def type_text(self, locator: Locator, text: str, hide_keyboard_after: bool = True):
        element = self.find_element(locator)
        element.clear()
        element.send_keys(text)
        framework_logger.debug(f"[Mobile] Entered text into {locator}")
        if hide_keyboard_after:
            self.hide_keyboard()

    def get_text(self, locator: Locator) -> str:
        element = self.find_element(locator)
        return element.text.strip()

    def is_visible(self, locator: Locator, timeout: int = 3) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(locator))
            return True
        except TimeoutException:
            return False

    def hide_keyboard(self):
        """Safely dismisses the on-screen keyboard."""
        try:
            if hasattr(self.driver, "hide_keyboard"):
                self.driver.hide_keyboard()
        except Exception:
            pass

    def swipe(self, start_x: float, start_y: float, end_x: float, end_y: float, duration_ms: int = 800):
        """Performs a swipe gesture using W3C Actions standard."""
        window_size = self.driver.get_window_size()
        width = window_size["width"]
        height = window_size["height"]

        sx = int(width * start_x)
        sy = int(height * start_y)
        ex = int(width * end_x)
        ey = int(height * end_y)

        framework_logger.debug(f"[Mobile] Swiping from ({sx}, {sy}) to ({ex}, {ey})")
        self.driver.swipe(sx, sy, ex, ey, duration_ms)

    def swipe_up(self, duration_ms: int = 800):
        """Swipes up (scrolls content down)."""
        self.swipe(0.5, 0.75, 0.5, 0.25, duration_ms)

    def swipe_down(self, duration_ms: int = 800):
        """Swipes down (scrolls content up)."""
        self.swipe(0.5, 0.25, 0.5, 0.75, duration_ms)

    def swipe_left(self, duration_ms: int = 800):
        """Swipes left (swipes carousel to right)."""
        self.swipe(0.8, 0.5, 0.2, 0.5, duration_ms)

    def swipe_right(self, duration_ms: int = 800):
        """Swipes right (swipes carousel to left)."""
        self.swipe(0.2, 0.5, 0.8, 0.5, duration_ms)

    def scroll_to_text_android(self, text: str):
        """Android-specific UiScrollable to find element containing text."""
        ui_automator_script = (
            f'new UiScrollable(new UiSelector().scrollable(true).instance(0))'
            f'.scrollIntoView(new UiSelector().textContains("{text}").instance(0));'
        )
        try:
            from appium.webdriver.common.appiumby import AppiumBy
            return self.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, ui_automator_script)
        except Exception as exc:
            framework_logger.error(f"[Mobile] Could not scroll to text '{text}': {exc}")
            raise

    def accept_alert(self):
        try:
            alert = self.driver.switch_to.alert
            alert.accept()
            framework_logger.info("[Mobile] Accepted system alert.")
        except Exception:
            pass

    def dismiss_alert(self):
        try:
            alert = self.driver.switch_to.alert
            alert.dismiss()
            framework_logger.info("[Mobile] Dismissed system alert.")
        except Exception:
            pass
