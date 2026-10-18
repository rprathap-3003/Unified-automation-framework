"""Windows Desktop Automation Tests using PyWinAuto."""

import pytest
import allure

from pages.desktop.notepad_window import NotepadWindow
from core.utils.data_generator import DataGenerator


@allure.epic("Desktop Automation")
@allure.feature("Windows Desktop App Automation")
@pytest.mark.desktop
class TestDesktopNotepad:
    """Desktop test suite covering Windows Notepad application automation."""

    @allure.story("Write Text and Verify Editor Content")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_notepad_write_and_verify(self, desktop_app):
        """Launches Notepad, writes synthetic text, and validates editor content."""
        notepad = NotepadWindow(desktop_app)

        with allure.step("Wait for Notepad window ready"):
            notepad.wait_for_ready(timeout=10)

        sample_text = f"Automated test run: {DataGenerator.random_string(10)}"

        with allure.step(f"Type test content into Notepad editor"):
            notepad.write_text(sample_text)

        with allure.step("Verify content was typed into editor"):
            content = notepad.get_text_content()
            assert sample_text in content, f"Expected '{sample_text}' in editor, got '{content}'"

        with allure.step("Close Notepad and discard unsaved changes"):
            notepad.exit_without_saving()
