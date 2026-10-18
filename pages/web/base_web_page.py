"""Base class for Web Application pages."""

from __future__ import annotations

from selenium import webdriver
from pages.base_page import BasePage
from config.settings import settings


class BaseWebPage(BasePage):
    """Base web page providing base URL resolution and navigation."""

    def __init__(self, driver: webdriver.Remote, path: str = ""):
        super().__init__(driver)
        self.path = path.lstrip("/")
        self.base_url = settings.web.base_url.rstrip("/")

    def navigate(self):
        full_url = f"{self.base_url}/{self.path}" if self.path else self.base_url
        self.open_url(full_url)
