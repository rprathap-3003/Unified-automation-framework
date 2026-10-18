"""Configuration Settings Manager.

Loads hierarchical configuration:
1. config/config.yaml (defaults)
2. config/environments/{env}.yaml (environment overrides)
3. Environment variables / .env (runtime overrides)
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


def _deep_merge(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merges dict2 into dict1."""
    result = dict(dict1)
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


@dataclass
class WebConfig:
    browser: str = "chrome"
    headless: bool = False
    implicit_wait: int = 0
    explicit_wait: int = 15
    page_load_timeout: int = 30
    window_width: int = 1920
    window_height: int = 1080
    base_url: str = "https://www.saucedemo.com"
    download_dir: str = "reports/downloads"
    remote_url: Optional[str] = None


@dataclass
class AndroidConfig:
    automation_name: str = "UiAutomator2"
    platform_name: str = "Android"
    platform_version: str = "14.0"
    device_name: str = "Pixel_7_API_34"
    app: Optional[str] = None
    app_package: str = "com.swaglabsmobileapp"
    app_activity: str = "com.swaglabsmobileapp.MainActivity"
    no_reset: bool = False
    full_reset: bool = False
    auto_grant_permissions: bool = True

    def to_capabilities(self) -> Dict[str, Any]:
        caps = {
            "platformName": self.platform_name,
            "appium:automationName": self.automation_name,
            "appium:platformVersion": self.platform_version,
            "appium:deviceName": self.device_name,
            "appium:noReset": self.no_reset,
            "appium:fullReset": self.full_reset,
            "appium:autoGrantPermissions": self.auto_grant_permissions,
        }
        if self.app and os.path.exists(self.app):
            caps["appium:app"] = str(Path(self.app).resolve())
        elif self.app_package:
            caps["appium:appPackage"] = self.app_package
            caps["appium:appActivity"] = self.app_activity
        return caps


@dataclass
class IOSConfig:
    automation_name: str = "XCUITest"
    platform_name: str = "iOS"
    platform_version: str = "17.0"
    device_name: str = "iPhone 15 Pro"
    app: Optional[str] = None
    bundle_id: str = "com.saucelabs.SwagLabsMobileApp"
    no_reset: bool = False

    def to_capabilities(self) -> Dict[str, Any]:
        caps = {
            "platformName": self.platform_name,
            "appium:automationName": self.automation_name,
            "appium:platformVersion": self.platform_version,
            "appium:deviceName": self.device_name,
            "appium:noReset": self.no_reset,
        }
        if self.app and os.path.exists(self.app):
            caps["appium:app"] = str(Path(self.app).resolve())
        elif self.bundle_id:
            caps["appium:bundleId"] = self.bundle_id
        return caps


@dataclass
class MobileConfig:
    server_url: str = "http://127.0.0.1:4723"
    platform: str = "android"
    explicit_wait: int = 20
    new_command_timeout: int = 300
    android: AndroidConfig = field(default_factory=AndroidConfig)
    ios: IOSConfig = field(default_factory=IOSConfig)

    def get_capabilities(self, platform_override: Optional[str] = None) -> Dict[str, Any]:
        target_platform = (platform_override or self.platform).lower()
        if target_platform == "android":
            return self.android.to_capabilities()
        elif target_platform == "ios":
            return self.ios.to_capabilities()
        else:
            raise ValueError(f"Unsupported mobile platform: {target_platform}")


@dataclass
class ApiConfig:
    base_url: str = "https://petstore.swagger.io/v2"
    timeout: int = 15
    max_retries: int = 3
    backoff_factor: float = 0.5
    verify_ssl: bool = True
    default_headers: Dict[str, str] = field(
        default_factory=lambda: {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
    )


@dataclass
class DesktopConfig:
    backend: str = "uia"  # "uia" or "win32"
    app_type: str = "native"
    winappdriver_url: str = "http://127.0.0.1:4723"
    timeout: int = 15
    sample_app_path: str = r"C:\Windows\System32\notepad.exe"


@dataclass
class ReportingConfig:
    screenshot_on_failure: bool = True
    screenshot_dir: str = "reports/screenshots"
    allure_dir: str = "reports/allure-results"
    html_report_path: str = "reports/html/report.html"


class Settings:
    """Singleton class managing framework configuration."""

    _instance: Optional[Settings] = None

    def __init__(self, env: Optional[str] = None):
        self.base_dir = BASE_DIR
        self.env = env or os.getenv("ENV") or "dev"
        self._raw_config = self._load_config()

        # Instantiate sub-configurations
        web_data = self._raw_config.get("web", {})
        self.web = WebConfig(**web_data)

        mob_data = self._raw_config.get("mobile", {})
        android_data = mob_data.pop("android", {})
        ios_data = mob_data.pop("ios", {})
        self.mobile = MobileConfig(
            server_url=mob_data.get("server_url", "http://127.0.0.1:4723"),
            platform=mob_data.get("platform", "android"),
            explicit_wait=mob_data.get("explicit_wait", 20),
            new_command_timeout=mob_data.get("new_command_timeout", 300),
            android=AndroidConfig(**android_data),
            ios=IOSConfig(**ios_data),
        )

        api_data = self._raw_config.get("api", {})
        self.api = ApiConfig(**api_data)

        desk_data = self._raw_config.get("desktop", {})
        self.desktop = DesktopConfig(**desk_data)

        rep_data = self._raw_config.get("reporting", {})
        self.reporting = ReportingConfig(**rep_data)

    def _load_config(self) -> Dict[str, Any]:
        """Loads and merges base config, env-specific config, and env var overrides."""
        config_path = self.base_dir / "config" / "config.yaml"
        base_data: Dict[str, Any] = {}
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                base_data = yaml.safe_load(f) or {}

        # Environment-specific overrides
        env_file = self.base_dir / "config" / "environments" / f"{self.env}.yaml"
        if env_file.exists():
            with open(env_file, "r", encoding="utf-8") as f:
                env_data = yaml.safe_load(f) or {}
                base_data = _deep_merge(base_data, env_data)

        # Apply environment variable overrides if present
        if os.getenv("WEB_BROWSER"):
            base_data.setdefault("web", {})["browser"] = os.getenv("WEB_BROWSER")
        if os.getenv("WEB_HEADLESS"):
            base_data.setdefault("web", {})["headless"] = os.getenv("WEB_HEADLESS", "").lower() in ("true", "1")
        if os.getenv("WEB_BASE_URL"):
            base_data.setdefault("web", {})["base_url"] = os.getenv("WEB_BASE_URL")
        if os.getenv("API_BASE_URL"):
            base_data.setdefault("api", {})["base_url"] = os.getenv("API_BASE_URL")
        if os.getenv("APPIUM_SERVER_URL"):
            base_data.setdefault("mobile", {})["server_url"] = os.getenv("APPIUM_SERVER_URL")
        if os.getenv("MOBILE_PLATFORM"):
            base_data.setdefault("mobile", {})["platform"] = os.getenv("MOBILE_PLATFORM")

        return base_data

    @classmethod
    def get_instance(cls, env: Optional[str] = None) -> Settings:
        """Returns the singleton instance of Settings."""
        if cls._instance is None or (env is not None and cls._instance.env != env):
            cls._instance = cls(env=env)
        return cls._instance


# Global convenience instance
settings = Settings.get_instance()
