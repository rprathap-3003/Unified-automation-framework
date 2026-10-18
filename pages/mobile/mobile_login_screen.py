"""Page Object for Mobile Login Screen (Appium)."""

from __future__ import annotations

try:
    from appium.webdriver.common.appiumby import AppiumBy
except ImportError:
    from selenium.webdriver.common.by import By as AppiumBy

from pages.mobile.base_mobile_screen import BaseMobileScreen


class MobileLoginScreen(BaseMobileScreen):
    """Mobile Login Screen locators and user interactions."""

    # Locators (Accessibility IDs & UIAutomator/XPath)
    USERNAME_INPUT = (AppiumBy.ACCESSIBILITY_ID, "test-Username")
    PASSWORD_INPUT = (AppiumBy.ACCESSIBILITY_ID, "test-Password")
    LOGIN_BUTTON = (AppiumBy.ACCESSIBILITY_ID, "test-LOGIN")
    ERROR_CONTAINER = (AppiumBy.XPATH, "//android.view.ViewGroup[@content-desc='test-Error message']/android.widget.TextView")
    BIOMETRIC_BUTTON = (AppiumBy.ACCESSIBILITY_ID, "test-biometry")

    def enter_username(self, username: str):
        self.type_text(self.USERNAME_INPUT, username)

    def enter_password(self, password: str):
        self.type_text(self.PASSWORD_INPUT, password)

    def tap_login(self):
        self.tap(self.LOGIN_BUTTON)

    def login(self, username: str, password: str):
        """Helper to execute full mobile login flow."""
        self.enter_username(username)
        self.enter_password(password)
        self.tap_login()

    def get_error_message(self) -> str:
        return self.get_text(self.ERROR_CONTAINER)

    def is_login_button_displayed(self) -> bool:
        return self.is_visible(self.LOGIN_BUTTON)
