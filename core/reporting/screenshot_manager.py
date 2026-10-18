"""Unified screenshot manager for Web, Mobile, and Desktop automation."""

from __future__ import annotations

import datetime
from pathlib import Path
from typing import Any, Optional

from core.utils.logger import framework_logger

SCREENSHOTS_DIR = Path(__file__).resolve().parent.parent.parent / "reports" / "screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)


class ScreenshotManager:
    """Captures and archives screenshots across Web, Mobile, and Desktop platforms."""

    @staticmethod
    def capture(driver_or_app: Any, test_name: str, platform: str = "web") -> Optional[str]:
        """Captures a screenshot and saves it to reports/screenshots/.

        Args:
            driver_or_app: Active driver or window application instance.
            test_name: Name of the test or action triggering the screenshot.
            platform: 'web', 'mobile', or 'desktop'.

        Returns:
            Absolute file path of the captured screenshot, or None if failed.
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:19]
        safe_name = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in test_name)
        filename = f"{platform}_{safe_name}_{timestamp}.png"
        filepath = SCREENSHOTS_DIR / filename

        try:
            # 1. Selenium WebDriver or Appium Mobile Driver
            if hasattr(driver_or_app, "save_screenshot"):
                driver_or_app.save_screenshot(str(filepath))
                framework_logger.info(f"[{platform.upper()}] Screenshot saved: {filepath}")

            # 2. PyWinAuto Window or Application
            elif hasattr(driver_or_app, "top_window"):
                img = driver_or_app.top_window().capture_as_image()
                img.save(str(filepath))
                framework_logger.info(f"[{platform.upper()}] Desktop screenshot saved: {filepath}")
            elif hasattr(driver_or_app, "capture_as_image"):
                img = driver_or_app.capture_as_image()
                img.save(str(filepath))
                framework_logger.info(f"[{platform.upper()}] Desktop screenshot saved: {filepath}")
            else:
                framework_logger.warning(
                    f"Unsupported driver type for screenshot: {type(driver_or_app)}"
                )
                return None

            # Attach to Allure report if allure is available
            ScreenshotManager.attach_to_allure(str(filepath), f"{platform}_{test_name}")
            return str(filepath)

        except Exception as exc:
            framework_logger.error(f"Failed to capture screenshot for {test_name}: {exc}")
            return None

    @staticmethod
    def attach_to_allure(filepath: str, name: str = "Screenshot"):
        """Attaches an existing screenshot file to the active Allure test step/case."""
        try:
            import allure

            if Path(filepath).exists():
                with open(filepath, "rb") as f:
                    allure.attach(
                        f.read(),
                        name=name,
                        attachment_type=allure.attachment_type.PNG,
                    )
        except ImportError:
            pass  # Allure is optional at runtime
        except Exception as exc:
            framework_logger.warning(f"Could not attach screenshot to Allure: {exc}")
