"""Web UI Tests for SauceDemo using Selenium WebDriver and Page Object Model."""

import pytest
import allure

from pages.web.login_page import WebLoginPage
from pages.web.inventory_page import WebInventoryPage
from core.utils.file_reader import FileReader
from config.settings import BASE_DIR


@allure.epic("Web Automation")
@allure.feature("Authentication & Catalog")
@pytest.mark.web
class TestWebAuthentication:
    """Test suite covering Web UI login flows and product interactions."""

    @pytest.fixture(autouse=True)
    def setup_data(self):
        fixtures_path = BASE_DIR / "test_data" / "test_users.yaml"
        self.user_data = FileReader.load_yaml(fixtures_path)

    @allure.story("Successful Login")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_valid_login_navigates_to_inventory(self, web_driver):
        """Verify standard user can log in and view product inventory."""
        login_page = WebLoginPage(web_driver)
        inventory_page = WebInventoryPage(web_driver)

        with allure.step("Navigate to Login Page"):
            login_page.navigate()

        with allure.step("Enter credentials for standard_user and submit"):
            std_user = self.user_data["standard_user"]
            login_page.login(std_user["username"], std_user["password"])

        with allure.step("Verify inventory dashboard displayed"):
            assert inventory_page.is_on_inventory_page(), "User not redirected to inventory page."
            assert inventory_page.get_title_text().upper() == "PRODUCTS"

        with allure.step("Verify product list contains items"):
            products = inventory_page.get_all_product_names()
            assert len(products) > 0, "No products displayed on inventory page."
            assert "Sauce Labs Backpack" in products

    @allure.story("Add Item to Cart")
    @allure.severity(allure.severity_level.NORMAL)
    def test_add_item_to_cart(self, web_driver):
        """Verify user can add a product to the shopping cart."""
        login_page = WebLoginPage(web_driver)
        inventory_page = WebInventoryPage(web_driver)

        login_page.navigate()
        std_user = self.user_data["standard_user"]
        login_page.login(std_user["username"], std_user["password"])

        with allure.step("Add first product to cart"):
            inventory_page.add_first_item_to_cart()

        with allure.step("Verify cart badge reflects 1 item"):
            assert inventory_page.get_cart_count() == 1, "Cart badge count does not match 1."

    @allure.story("Locked Out User Error")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_locked_out_user_shows_error(self, web_driver):
        """Verify locked-out user receives an error alert upon attempting login."""
        login_page = WebLoginPage(web_driver)
        login_page.navigate()

        locked_user = self.user_data["locked_out_user"]
        with allure.step("Attempt login with locked_out_user"):
            login_page.login(locked_user["username"], locked_user["password"])

        with allure.step("Verify error message matches expected locked out text"):
            assert login_page.is_error_displayed(), "Error message was not displayed."
            error_msg = login_page.get_error_message()
            assert "locked out" in error_msg.lower(), f"Unexpected error message: {error_msg}"
