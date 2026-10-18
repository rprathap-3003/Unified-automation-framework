"""Base HTTP Client with automatic logging, retries, and Allure reporting."""

from __future__ import annotations

import json
import time
from typing import Any, Dict, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

from config.settings import settings
from core.reporting.allure_listener import AllureReportHelper
from core.utils.logger import framework_logger


class BaseApiClient:
    """Enterprise HTTP REST client wrapping requests.Session."""

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = (base_url or settings.api.base_url).rstrip("/")
        self.session = requests.Session()
        self._configure_retries()
        self._set_default_headers()

    def _configure_retries(self):
        retries = Retry(
            total=settings.api.max_retries,
            backoff_factor=settings.api.backoff_factor,
            status_forcelist=[500, 502, 503, 504],
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _set_default_headers(self):
        self.session.headers.update(settings.api.default_headers)

    def set_header(self, key: str, value: str):
        self.session.headers[key] = value

    def set_bearer_token(self, token: str):
        self.session.headers["Authorization"] = f"Bearer {token}"

    def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        json_data: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        **kwargs,
    ) -> requests.Response:
        url = endpoint if endpoint.startswith("http") else f"{self.base_url}/{endpoint.lstrip('/')}"
        req_headers = dict(self.session.headers)
        if headers:
            req_headers.update(headers)

        req_timeout = timeout or settings.api.timeout

        # Curl command representation for fast debugging
        curl_cmd = self._generate_curl(method, url, req_headers, json_data or data)
        framework_logger.debug(f"[API Request] {curl_cmd}")

        start_time = time.time()
        try:
            response = self.session.request(
                method=method.upper(),
                url=url,
                params=params,
                data=data,
                json=json_data,
                headers=req_headers,
                timeout=req_timeout,
                verify=settings.api.verify_ssl,
                **kwargs,
            )
            elapsed_ms = round((time.time() - start_time) * 1000, 2)
            framework_logger.info(
                f"[API Response] {method.upper()} {url} -> Status: {response.status_code} ({elapsed_ms}ms)"
            )

            # Attach to Allure
            self._attach_allure_call(method, url, req_headers, json_data or data, response, elapsed_ms)
            return response

        except requests.RequestException as exc:
            elapsed_ms = round((time.time() - start_time) * 1000, 2)
            framework_logger.error(f"[API Error] {method.upper()} {url} failed after {elapsed_ms}ms: {exc}")
            raise

    def get(self, endpoint: str, **kwargs) -> requests.Response:
        return self.request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs) -> requests.Response:
        return self.request("POST", endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs) -> requests.Response:
        return self.request("PUT", endpoint, **kwargs)

    def patch(self, endpoint: str, **kwargs) -> requests.Response:
        return self.request("PATCH", endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        return self.request("DELETE", endpoint, **kwargs)

    def validate_schema(self, response_json: Any, schema: Dict[str, Any]):
        """Validates response JSON against a JSON schema."""
        if not HAS_JSONSCHEMA:
            framework_logger.warning("jsonschema not installed, skipping schema validation.")
            return
        jsonschema.validate(instance=response_json, schema=schema)
        framework_logger.info("JSON Schema validation passed successfully.")

    def _generate_curl(self, method: str, url: str, headers: Dict[str, str], payload: Any) -> str:
        parts = [f"curl -X {method.upper()} '{url}'"]
        for k, v in headers.items():
            parts.append(f"-H '{k}: {v}'")
        if payload:
            dumped = json.dumps(payload) if isinstance(payload, (dict, list)) else str(payload)
            parts.append(f"-d '{dumped}'")
        return " ".join(parts)

    def _attach_allure_call(
        self,
        method: str,
        url: str,
        headers: Dict[str, str],
        payload: Any,
        response: requests.Response,
        elapsed_ms: float,
    ):
        step_title = f"{method.upper()} {url} [{response.status_code}] ({elapsed_ms}ms)"
        allure_text = [
            f"URL: {url}",
            f"Method: {method.upper()}",
            f"Status Code: {response.status_code}",
            f"Duration: {elapsed_ms}ms",
            "\n--- Request Headers ---",
            json.dumps(headers, indent=2),
        ]
        if payload:
            allure_text.append("\n--- Request Body ---")
            allure_text.append(json.dumps(payload, indent=2) if isinstance(payload, (dict, list)) else str(payload))

        allure_text.append("\n--- Response Headers ---")
        allure_text.append(json.dumps(dict(response.headers), indent=2))
        allure_text.append("\n--- Response Body ---")
        allure_text.append(response.text)

        AllureReportHelper.attach_text("\n".join(allure_text), name=step_title)
