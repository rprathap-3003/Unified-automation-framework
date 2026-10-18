"""Allure reporting helper utilities and metadata environment generator."""

from __future__ import annotations

import platform
from pathlib import Path
from typing import Dict, Any

from config.settings import settings
from core.utils.logger import framework_logger


class AllureReportHelper:
    """Helper to attach rich data, logs, and environment metadata to Allure."""

    @staticmethod
    def write_environment_properties():
        """Writes environment.properties file into allure-results directory."""
        allure_dir = Path(__file__).resolve().parent.parent.parent / "reports" / "allure-results"
        allure_dir.mkdir(parents=True, exist_ok=True)
        env_file = allure_dir / "environment.properties"

        props = {
            "Environment": settings.env.upper(),
            "OS": platform.system() + " " + platform.release(),
            "Python_Version": platform.python_version(),
            "Web_Browser": settings.web.browser,
            "Web_Headless": str(settings.web.headless),
            "Web_Base_URL": settings.web.base_url,
            "API_Base_URL": settings.api.base_url,
            "Mobile_Platform": settings.mobile.platform,
            "Mobile_Server": settings.mobile.server_url,
            "Desktop_Backend": settings.desktop.backend,
        }

        try:
            with open(env_file, "w", encoding="utf-8") as f:
                for k, v in props.items():
                    f.write(f"{k}={v}\n")
            framework_logger.info(f"Generated Allure environment properties at {env_file}")
        except Exception as exc:
            framework_logger.warning(f"Could not write Allure environment.properties: {exc}")

    @staticmethod
    def attach_text(text: str, name: str = "Details"):
        """Attaches plain text snippet to Allure."""
        try:
            import allure

            allure.attach(text, name=name, attachment_type=allure.attachment_type.TEXT)
        except ImportError:
            pass

    @staticmethod
    def attach_json(data: Dict[str, Any] | str, name: str = "JSON Payload"):
        """Attaches formatted JSON data to Allure."""
        try:
            import allure
            import json

            content = json.dumps(data, indent=2) if isinstance(data, (dict, list)) else str(data)
            allure.attach(content, name=name, attachment_type=allure.attachment_type.JSON)
        except ImportError:
            pass
