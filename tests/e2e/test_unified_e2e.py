"""Unified Cross-Platform End-to-End Tests.

Demonstrates seamless multi-platform integration across:
- REST API (Data Seeding & Verification)
- Web UI (User Interaction & Checkout)
"""

import pytest
import allure

from pages.web.login_page import WebLoginPage
from pages.web.inventory_page import WebInventoryPage
from core.utils.file_reader import FileReader
from config.settings import BASE_DIR


@allure.epic("E2E Integration")
@allure.feature("Cross-Platform Workflow")
@pytest.mark.e2e
class TestUnifiedE2E:
    """Demonstrates cross-platform interaction linking API and Web layers."""

    @allure.story("API Healthcheck and Web User Journey")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_api_status_and_web_journey(self, api_client, web_driver):
        """Validates backend service health via API before executing Web UI checkout journey."""
        with allure.step("1. API Health Check: Verify backend is reachable"):
            api_res = api_client.find_by_status("available")
            assert api_res.status_code == 200, "Backend API service unavailable."

        with allure.step("2. Web UI Flow: Load test credentials"):
            fixtures_path = BASE_DIR / "test_data" / "test_users.yaml"
            user_data = FileReader.load_yaml(fixtures_path)["standard_user"]

        with allure.step("3. Web UI: Log in to application"):
            login_page = WebLoginPage(web_driver)
            inventory_page = WebInventoryPage(web_driver)

            login_page.navigate()
            login_page.login(user_data["username"], user_data["password"])
            assert inventory_page.is_on_inventory_page()

        with allure.step("4. Web UI: Add product to cart"):
            inventory_page.add_first_item_to_cart()
            assert inventory_page.get_cart_count() == 1

        with allure.step("5. Web UI: Logout"):
            inventory_page.logout()
            assert login_page.is_visible(login_page.LOGIN_BUTTON)
