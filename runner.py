"""Interactive and Command-Line Test Suite Runner.

Provides a unified interface to execute Web, Mobile, API, Desktop,
or E2E test suites with simple flags or an interactive prompt.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(cmd_args: list[str]) -> int:
    """Executes a command and streams output to terminal."""
    print(f"\n[EXEC] {' '.join(cmd_args)}\n" + "=" * 60)
    process = subprocess.run(cmd_args)
    return process.returncode


def generate_allure_report():
    """Generates and serves Allure HTML report."""
    results_dir = Path("reports/allure-results")
    if not results_dir.exists() or not any(results_dir.iterdir()):
        print("\n[!] No Allure results found in reports/allure-results. Run tests first.")
        return

    print("\n[+] Serving Allure Report (Ctrl+C to stop)...")
    subprocess.run(["allure", "serve", "reports/allure-results"])


def interactive_menu():
    """Interactive CLI menu when no arguments are provided."""
    print("=" * 60)
    print("  UNIFIED MULTI-PLATFORM TEST AUTOMATION RUNNER")
    print("=" * 60)
    print("Select test suite to run:")
    print("  1. Web Automation Tests (Selenium)")
    print("  2. API Automation Tests (Requests)")
    print("  3. Desktop Automation Tests (PyWinAuto)")
    print("  4. Mobile Automation Tests (Appium)")
    print("  5. End-to-End Multi-Platform Tests")
    print("  6. Smoke Suite (All platforms)")
    print("  7. All Tests (Full Regression)")
    print("  8. View Allure Test Report")
    print("  0. Exit")
    print("=" * 60)

    choice = input("Enter choice [0-8]: ").strip()
    mapping = {
        "1": ["-m", "web"],
        "2": ["-m", "api"],
        "3": ["-m", "desktop"],
        "4": ["-m", "mobile"],
        "5": ["-m", "e2e"],
        "6": ["-m", "smoke"],
        "7": [],
    }

    if choice == "8":
        generate_allure_report()
        return
    elif choice in ("0", "exit", "q"):
        print("Exiting runner.")
        sys.exit(0)
    elif choice in mapping:
        cmd = [sys.executable, "-m", "pytest"] + mapping[choice]
        sys.exit(run_command(cmd))
    else:
        print("[!] Invalid selection. Please choose a valid option.")
        interactive_menu()


def main():
    parser = argparse.ArgumentParser(
        description="Unified Automation Framework Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--platform",
        choices=["web", "api", "mobile", "desktop", "e2e", "all"],
        help="Target platform test suite to execute",
    )
    parser.add_argument("--smoke", action="store_true", help="Run only @pytest.mark.smoke tests")
    parser.add_argument("--regression", action="store_true", help="Run @pytest.mark.regression tests")
    parser.add_argument("--env", help="Target environment: dev | staging | prod")
    parser.add_argument("--browser", help="Browser: chrome | firefox | edge | safari")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")
    parser.add_argument("--mobile-platform", choices=["android", "ios"], help="Mobile platform")
    parser.add_argument("--parallel", "-n", type=str, help="Number of workers for pytest-xdist (e.g. 2, auto)")
    parser.add_argument("--report", action="store_true", help="Generate and serve Allure report after tests")

    args = parser.parse_args()

    # If no flags passed, launch interactive prompt
    if len(sys.argv) == 1:
        interactive_menu()
        return

    cmd = [sys.executable, "-m", "pytest"]

    # Platform filtering
    if args.platform and args.platform != "all":
        cmd += ["-m", args.platform]
    elif args.smoke:
        cmd += ["-m", "smoke"]
    elif args.regression:
        cmd += ["-m", "regression"]

    # Parameter forwarding
    if args.env:
        cmd += ["--env", args.env]
    if args.browser:
        cmd += ["--browser", args.browser]
    if args.headless:
        cmd += ["--headless=true"]
    if args.mobile_platform:
        cmd += ["--mobile-platform", args.mobile_platform]
    if args.parallel:
        cmd += ["-n", str(args.parallel)]

    return_code = run_command(cmd)

    if args.report:
        generate_allure_report()

    sys.exit(return_code)


if __name__ == "__main__":
    main()
