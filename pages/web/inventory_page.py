"""Page Object for SauceDemo Inventory / Products Page."""

from __future__ import annotations

from typing import List
from selenium.webdriver.common.by import By
from pages.web.base_web_page import BaseWebPage


class WebInventoryPage(BaseWebPage):
    """Inventory dashboard page locators and user actions."""

    TITLE_HEADER = (By.CLASS_NAME, "title")
    INVENTORY_ITEMS = (By.CLASS_NAME, "inventory_item")
    INVENTORY_NAMES = (By.CLASS_NAME, "inventory_item_name")
    CART_BADGE = (By.CLASS_NAME, "shopping_cart_badge")
    ADD_TO_CART_BTN = (By.XPATH, "//button[contains(text(), 'Add to cart')]")
    BURGER_MENU = (By.ID, "react-burger-menu-btn")
    LOGOUT_LINK = (By.ID, "logout_sidebar_link")

    def __init__(self, driver):
        super().__init__(driver, path="inventory.html")

    def is_on_inventory_page(self) -> bool:
        return self.is_visible(self.TITLE_HEADER, timeout=5) and "inventory" in self.get_current_url()

    def get_title_text(self) -> str:
        return self.get_text(self.TITLE_HEADER)

    def get_item_count(self) -> int:
        return len(self.find_all(self.INVENTORY_ITEMS))

    def get_all_product_names(self) -> List[str]:
        elements = self.find_all(self.INVENTORY_NAMES)
        return [e.text.strip() for e in elements]

    def add_first_item_to_cart(self):
        self.click(self.ADD_TO_CART_BTN)

    def get_cart_count(self) -> int:
        if self.is_visible(self.CART_BADGE, timeout=2):
            return int(self.get_text(self.CART_BADGE))
        return 0

    def logout(self):
        self.click(self.BURGER_MENU)
        self.click(self.LOGOUT_LINK)
