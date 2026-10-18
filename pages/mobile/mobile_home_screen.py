"""Page Object for Mobile Product Catalog / Home Screen."""

from __future__ import annotations

try:
    from appium.webdriver.common.appiumby import AppiumBy
except ImportError:
    from selenium.webdriver.common.by import By as AppiumBy

from pages.mobile.base_mobile_screen import BaseMobileScreen


class MobileHomeScreen(BaseMobileScreen):
    """Mobile catalog screen locators and gestures."""

    HEADER_TITLE = (AppiumBy.XPATH, "//android.widget.TextView[@text='PRODUCTS']")
    FIRST_PRODUCT = (AppiumBy.XPATH, "(//android.view.ViewGroup[@content-desc='test-Item'])[1]")
    CART_ICON = (AppiumBy.ACCESSIBILITY_ID, "test-Cart")
    MENU_BUTTON = (AppiumBy.ACCESSIBILITY_ID, "test-Menu")
    LOGOUT_BUTTON = (AppiumBy.ACCESSIBILITY_ID, "test-LOGOUT")

    def is_on_home_screen(self) -> bool:
        return self.is_visible(self.HEADER_TITLE, timeout=10)

    def tap_first_product(self):
        self.tap(self.FIRST_PRODUCT)

    def tap_cart(self):
        self.tap(self.CART_ICON)

    def logout(self):
        self.tap(self.MENU_BUTTON)
        self.tap(self.LOGOUT_BUTTON)
