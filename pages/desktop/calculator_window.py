"""Desktop Page Object for Windows Calculator."""

from __future__ import annotations

import time
from typing import Any
from pages.desktop.base_desktop_window import BaseDesktopWindow
from core.utils.logger import framework_logger


class CalculatorWindow(BaseDesktopWindow):
    """Encapsulates Windows Calculator automation using UIAutomation."""

    def __init__(self, app: Any):
        super().__init__(app, window_title=".*Calculator.*")

    def click_digit(self, digit: int):
        self.window.child_window(auto_id=f"num{digit}Button", control_type="Button").click_input()

    def click_plus(self):
        self.window.child_window(auto_id="plusButton", control_type="Button").click_input()

    def click_minus(self):
        self.window.child_window(auto_id="minusButton", control_type="Button").click_input()

    def click_multiply(self):
        self.window.child_window(auto_id="multiplyButton", control_type="Button").click_input()

    def click_divide(self):
        self.window.child_window(auto_id="divideButton", control_type="Button").click_input()

    def click_equals(self):
        self.window.child_window(auto_id="equalButton", control_type="Button").click_input()

    def click_clear(self):
        self.window.child_window(auto_id="clearButton", control_type="Button").click_input()

    def get_result(self) -> str:
        """Retrieves text from Calculator results display."""
        time.sleep(0.5)
        display = self.window.child_window(auto_id="CalculatorResults", control_type="Text")
        raw_text = display.window_text()
        # raw_text is typically "Display is 42"
        return raw_text.replace("Display is", "").strip()
