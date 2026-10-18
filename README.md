# Unified Multi-Platform Test Automation Framework

An enterprise-grade, extensible test automation framework built in **Python** providing unified automation across **Web**, **Mobile**, **API**, and **Windows Desktop** applications.

---

## 🚀 Key Features

- **🌐 Web Automation**: Built with **Selenium 4**, supporting Chrome, Firefox, Edge, Safari, headless execution, and remote Selenium Grid / cloud testing.
- **📱 Mobile Automation**: Powered by **Appium Python Client (Appium 2.x standard)**, supporting native gestures, swipe, scroll, alerts, and element interaction on **Android** (UiAutomator2) and **iOS** (XCUITest).
- **🔌 API Automation**: Robust HTTP client wrapping **Requests** with session reuse, exponential backoff retries, curl command generation, JSON schema validation (`jsonschema`), and Pydantic data models.
- **💻 Desktop Automation**: Native Windows application automation powered by **PyWinAuto** (UIAutomation & Win32) with support for classic and modern Win11 desktop apps.
- **🏗️ Page Object Model (POM)**: Strictly decoupled test logic and UI locators across Web, Mobile Screen, and Desktop Window objects.
- **📊 Rich Reporting & Diagnostics**: Built-in **Allure** reporting, self-contained **HTML reports**, structured logging with rotation, and automatic screenshot capture on test failure.
- **⚙️ Multi-Environment Configuration**: Centralized YAML and `.env` configuration supporting `dev`, `staging`, and `prod` profiles with CLI overrides.
- **🔄 Parallel & CI/CD Ready**: Native support for parallel execution (`pytest-xdist`) and pre-configured **GitHub Actions CI/CD** pipeline.

---

## 📁 Architecture & Directory Structure

```
unified-automation-framework/
│
├── .github/workflows/
│   └── test-automation.yml          # GitHub Actions CI pipeline
│
├── config/                          # Central & environment configurations
│   ├── config.yaml                  # Master configuration
│   ├── settings.py                  # Typed configuration manager
│   └── environments/
│       ├── dev.yaml                 # Dev environment overrides
│       ├── staging.yaml             # Staging environment overrides
│       └── prod.yaml                # Production environment overrides
│
├── core/                            # Framework engine & core abstractions
│   ├── drivers/
│   │   ├── driver_factory.py        # Unified driver factory
│   │   ├── web_driver.py            # Selenium WebDriver manager
│   │   ├── mobile_driver.py         # Appium Android/iOS driver manager
│   │   └── desktop_driver.py        # PyWinAuto desktop app manager
│   ├── reporting/
│   │   ├── allure_listener.py       # Allure hooks & metadata
│   │   └── screenshot_manager.py    # Auto screenshot capturer
│   └── utils/
│       ├── logger.py                # Structured console & rotating file logging
│       ├── wait_utils.py            # Polling & retry decorators
│       ├── data_generator.py        # Faker synthetic test data
│       └── file_reader.py           # YAML/JSON/CSV fixture loaders
│
├── pages/                           # Page Object Model (POM) & Screen Objects
│   ├── base_page.py                 # Universal Web base page
│   ├── web/                         # Web pages (Login, Inventory)
│   ├── mobile/                      # Mobile screens (Gestures, Login, Home)
│   └── desktop/                     # Desktop windows (Notepad, Calculator)
│
├── api/                             # API Clients & Models
│   ├── clients/
│   │   ├── base_api_client.py       # HTTP client with retries & logging
│   │   └── petstore_client.py       # Domain-specific API client
│   └── models/
│       └── pet_model.py             # Pydantic request/response models
│
├── test_data/                       # Test data fixtures & JSON schemas
│   ├── schemas/user_schema.json     # Contract schema validation
│   └── test_users.yaml              # User credentials
│
├── tests/                           # Pytest Test Suites
│   ├── conftest.py                  # Global fixtures & driver lifecycle
│   ├── web/test_web_login.py        # Web UI tests
│   ├── mobile/test_mobile_login.py  # Mobile UI tests
│   ├── api/test_api_petstore.py     # API CRUD & schema tests
│   ├── desktop/test_desktop_notepad.py # Desktop app tests
│   └── e2e/test_unified_e2e.py      # Cross-platform integration tests
│
├── reports/                         # Test artifacts (Screenshots, Allure, HTML)
├── logs/                            # Rotating log files
├── pytest.ini                       # Pytest markers and execution options
├── runner.py                        # Interactive & CLI test suite runner
├── requirements.txt                 # Project dependencies
└── README.md                        # Documentation
```

---

## 🛠️ Prerequisites & Setup

### 1. Python Environment
Ensure Python 3.9+ is installed:
```bash
python --version
```

Clone the repository and set up a virtual environment:
```bash
cd unified-automation-framework
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate

# Install dependencies:
pip install -r requirements.txt
```

### 2. Platform-Specific Prerequisites

| Platform | Requirements |
| :--- | :--- |
| **Web** | Google Chrome, Firefox, or Edge. Drivers are automatically managed via `webdriver-manager`. |
| **API** | No external tools required; pure Python `requests`. |
| **Mobile** | [Node.js](https://nodejs.org/) + Appium 2.x (`npm i -g appium`).<br>Drivers: `appium driver install uiautomator2` (Android) and `appium driver install xcuitest` (iOS).<br>Android SDK & Emulator or connected device. |
| **Desktop** | Windows 10/11 (Uses native Windows Accessibility APIs via `pywinauto`). |

---

## 🏃 Running Tests

### Option A: Using the Interactive Runner
Run without arguments to access the interactive CLI menu:
```bash
python runner.py
```

Or pass flags:
```bash
# Run Web tests in Chrome (headless)
python runner.py --platform web --headless

# Run API tests
python runner.py --platform api

# Run Desktop tests
python runner.py --platform desktop

# Run Mobile tests
python runner.py --platform mobile --mobile-platform android

# Run Smoke tests across all platforms
python runner.py --smoke
```

---

### Option B: Using Standard Pytest Commands

```bash
# Web tests:
pytest -m web
pytest -m web --browser firefox --headless=true

# API tests:
pytest -m api

# Desktop tests:
pytest -m desktop

# Mobile tests:
pytest -m mobile --mobile-platform android --device-name "Pixel_7_API_34"

# Cross-platform E2E tests:
pytest -m e2e

# Run tests in parallel (4 workers):
pytest -n 4 -m api

# Target specific environment (dev, staging, prod):
pytest --env staging -m web
```

---

## 📊 Test Reporting

### 1. Pytest HTML Report
A standalone HTML report is automatically saved to:
```
reports/html/report.html
```

### 2. Allure Report
View rich interactive reports with steps, logs, and failure screenshots:
```bash
# Serve live Allure report
allure serve reports/allure-results

# Or generate static HTML report
allure generate reports/allure-results -o reports/allure-report --clean
allure open reports/allure-report
```

---

## ⚙️ Configuration Reference

Settings can be customized in `config/config.yaml` or overridden via environment variables / `.env`:

```yaml
web:
  browser: chrome              # chrome | firefox | edge | safari
  headless: false
  explicit_wait: 15
  base_url: "https://www.saucedemo.com"

mobile:
  server_url: "http://127.0.0.1:4723"
  platform: android
  android:
    automation_name: "UiAutomator2"
    device_name: "Pixel_7_API_34"

api:
  base_url: "https://petstore.swagger.io/v2"
  timeout: 15
  max_retries: 3

desktop:
  backend: "uia"               # "uia" or "win32"
  sample_app_path: "C:\\Windows\\System32\\notepad.exe"
```

---

## 🧩 Extending the Framework

1. **Add a new Web Page**: Create a class inheriting from `BaseWebPage` inside `pages/web/`. Define locators as tuples and user actions as methods.
2. **Add a new Mobile Screen**: Inherit from `BaseMobileScreen` inside `pages/mobile/`. Use AppiumBy locators and built-in gesture helpers (`swipe_up`, `scroll_to_text_android`).
3. **Add a new Desktop Window**: Inherit from `BaseDesktopWindow` inside `pages/desktop/`. Use control selectors (`child_window(auto_id=...)`).
4. **Add a new API Client**: Inherit from `BaseApiClient` inside `api/clients/` to inherit session management, curl generation, and retries.
