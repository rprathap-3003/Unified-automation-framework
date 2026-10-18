"""Page Object for SauceDemo Web Login."""

from __future__ import annotations

from selenium.webdriver.common.by import By
from pages.web.base_web_page import BaseWebPage
from core.reporting.allure_listener import AllureReportHelper


class WebLoginPage(BaseWebPage):
    """SauceDemo login page locators and user actions."""

    # Locators
    USERNAME_INPUT = (By.ID, "user-name")
    PASSWORD_INPUT = (By.ID, "password")
    LOGIN_BUTTON = (By.ID, "login-button")
    ERROR_MESSAGE = (By.CSS_SELECTOR, "h3[data-test='error']")
    BOT_IMAGE = (By.CLASS_NAME, "bot_column")

    def __init__(self, driver):
        super().__init__(driver, path="")

    def enter_username(self, username: str):
        self.type_text(self.USERNAME_INPUT, username)

    def enter_password(self, password: str):
        self.type_text(self.PASSWORD_INPUT, password)

    def click_login(self):
        self.click(self.LOGIN_BUTTON)

    def login(self, username: str, password: str):
        """Complete login flow helper."""
        self.enter_username(username)
        self.enter_password(password)
        self.click_login()

    def get_error_message(self) -> str:
        return self.get_text(self.ERROR_MESSAGE)

    def is_error_displayed(self) -> bool:
        return self.is_visible(self.ERROR_MESSAGE, timeout=3)
