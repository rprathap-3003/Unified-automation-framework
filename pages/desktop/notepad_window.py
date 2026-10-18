"""Desktop Page Object for Windows Notepad."""

from __future__ import annotations

import time
from typing import Any
from pages.desktop.base_desktop_window import BaseDesktopWindow
from core.utils.logger import framework_logger


class NotepadWindow(BaseDesktopWindow):
    """Encapsulates Windows Notepad automation."""

    def __init__(self, app: Any):
        super().__init__(app, window_title=".*Notepad.*")

    def get_editor_control(self):
        """Locates the text area control in either classic or modern Windows 11 Notepad."""
        self.wait_for_ready()
        # Modern Win11 Notepad uses RichEditD2DPT or Document; Win7/10 uses Edit
        try:
            return self.window.child_window(control_type="Document")
        except Exception:
            return self.window.child_window(class_name="Edit")

    def write_text(self, text: str):
        """Writes text into Notepad editor."""
        editor = self.get_editor_control()
        editor.set_focus()
        editor.type_keys(text, with_spaces=True)
        framework_logger.info(f"[Notepad] Wrote {len(text)} characters into editor.")

    def get_text_content(self) -> str:
        """Retrieves text from Notepad editor."""
        editor = self.get_editor_control()
        try:
            return editor.get_value() or ""
        except Exception:
            return editor.window_text()

    def exit_without_saving(self):
        """Closes Notepad and discards unsaved changes if prompt appears."""
        self.close()
        time.sleep(0.5)
        # Check if 'Don't Save' prompt appears
        try:
            dont_save_dialog = self.app.window(title_re=".*Notepad.*")
            # Look for "Don't Save" button
            dont_save_btn = dont_save_dialog.child_window(title_re=".*Don't [Ss]ave.*")
            if dont_save_btn.exists(timeout=2):
                dont_save_btn.click_input()
                framework_logger.info("[Notepad] Clicked 'Don't Save' button.")
        except Exception:
            pass
