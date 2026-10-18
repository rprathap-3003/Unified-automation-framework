"""Mobile App Automation Tests using Appium."""

import pytest
import allure

from pages.mobile.mobile_login_screen import MobileLoginScreen
from pages.mobile.mobile_home_screen import MobileHomeScreen
from core.utils.file_reader import FileReader
from config.settings import BASE_DIR


@allure.epic("Mobile Automation")
@allure.feature("Mobile Authentication & Navigation")
@pytest.mark.mobile
class TestMobileAuthentication:
    """Mobile test suite covering Appium Android & iOS test cases."""

    @pytest.fixture(autouse=True)
    def setup_data(self):
        fixtures_path = BASE_DIR / "test_data" / "test_users.yaml"
        self.user_data = FileReader.load_yaml(fixtures_path)

    @allure.story("Valid Mobile Login & Product Browse")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_mobile_login_and_browse(self, mobile_driver):
        """Verify standard user can log in to mobile app and swipe through catalog."""
        login_screen = MobileLoginScreen(mobile_driver)
        home_screen = MobileHomeScreen(mobile_driver)

        with allure.step("Verify login screen is displayed"):
            assert login_screen.is_login_button_displayed()

        with allure.step("Enter credentials and tap Login"):
            std_user = self.user_data["standard_user"]
            login_screen.login(std_user["username"], std_user["password"])

        with allure.step("Verify Home Screen is displayed"):
            assert home_screen.is_on_home_screen()

        with allure.step("Perform swipe down gesture to browse products"):
            home_screen.swipe_up()  # Swipes up to reveal products lower on screen

        with allure.step("Logout from mobile app"):
            home_screen.logout()
            assert login_screen.is_login_button_displayed()

    @allure.story("Invalid Mobile Login Alert")
    @allure.severity(allure.severity_level.NORMAL)
    def test_mobile_locked_out_user(self, mobile_driver):
        """Verify locked-out user receives an error alert in mobile app."""
        login_screen = MobileLoginScreen(mobile_driver)

        locked_user = self.user_data["locked_out_user"]
        with allure.step("Attempt login with locked_out_user"):
            login_screen.login(locked_user["username"], locked_user["password"])

        with allure.step("Verify error message contains 'locked out'"):
            error_text = login_screen.get_error_message()
            assert "locked out" in error_text.lower()
