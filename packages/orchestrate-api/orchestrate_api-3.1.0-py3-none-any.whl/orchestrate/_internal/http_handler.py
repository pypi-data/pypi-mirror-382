import json
import os
from ctypes import ArgumentError
from dataclasses import dataclass
from typing import Any, Mapping, Optional, Union

import requests
from orchestrate._internal.exceptions import (
    OrchestrateClientError,
    OrchestrateHttpError,
)

_BASE_URL_ENVIRONMENT_VARIABLE = "ORCHESTRATE_BASE_URL"
_IDENTITY_URL_ENVIRONMENT_VARIABLE = "ORCHESTRATE_IDENTITY_URL"
_IDENTITY_LOCAL_HASHING_URL_ENVIRONMENT_VARIABLE = (
    "ORCHESTRATE_IDENTITY_LOCAL_HASHING_URL"
)
_ADDITIONAL_HEADERS_ENVIRONMENT_VARIABLE = "ORCHESTRATE_ADDITIONAL_HEADERS"
_API_KEY_ENVIRONMENT_VARIABLE = "ORCHESTRATE_API_KEY"
_IDENTITY_API_KEY_ENVIRONMENT_VARIABLE = "ORCHESTRATE_IDENTITY_API_KEY"
_IDENTITY_METRICS_KEY_ENVIRONMENT_VARIABLE = "ORCHESTRATE_IDENTITY_METRICS_KEY"
_TIMEOUT_MS_ENVIRONMENT_VARIABLE = "ORCHESTRATE_TIMEOUT_MS"
_TIMEOUT_MS_DEFAULT = 120_000


def _get_priority_from_environment(
    argument: Optional[str], environment_variable: str
) -> Optional[str]:
    if argument is not None:
        return argument
    return os.environ.get(environment_variable)


def _get_priority_base_url(base_url: Optional[str]) -> str:
    return (
        _get_priority_from_environment(base_url, _BASE_URL_ENVIRONMENT_VARIABLE)
        or "https://api.careevolutionapi.com"
    )


def _get_priority_timeout_ms(timeout_ms: Optional[int]) -> int:
    env_timeout = _get_priority_from_environment(
        str(timeout_ms) if timeout_ms is not None else None,
        _TIMEOUT_MS_ENVIRONMENT_VARIABLE,
    )
    if env_timeout is not None:
        try:
            return int(env_timeout)
        except ValueError:
            raise ArgumentError(
                f"Invalid timeout value in environment variable '{_TIMEOUT_MS_ENVIRONMENT_VARIABLE}': {env_timeout}"
            )
    return timeout_ms if timeout_ms is not None else _TIMEOUT_MS_DEFAULT


def _get_additional_headers() -> Mapping[str, str]:
    return json.loads(
        _get_priority_from_environment(None, _ADDITIONAL_HEADERS_ENVIRONMENT_VARIABLE)
        or "{}"
    )


@dataclass
class _OperationalOutcomeIssue:
    severity: str
    code: str
    diagnostics: str
    details: str

    def __str__(self) -> str:
        s = f"{self.severity}: {self.code}"
        message = "; ".join(
            message for message in [self.details, self.diagnostics] if message
        )
        if message:
            s += f" - {message}"
        return s


def _read_json_outcomes(response: requests.Response) -> list[_OperationalOutcomeIssue]:
    try:
        json_response = response.json()
        if "issue" in json_response:
            return [
                _OperationalOutcomeIssue(
                    issue.get("severity", ""),
                    issue.get("code", ""),
                    issue.get("diagnostics", ""),
                    _get_issue_detail_string(issue.get("details", {})),
                )
                for issue in json_response["issue"]
            ]
        if (
            json_response.get("type")
            == "https://tools.ietf.org/html/rfc9110#section-15.5.1"
        ):
            return [
                _OperationalOutcomeIssue(
                    severity="error",
                    code=json_response.get("title", ""),
                    diagnostics=json_response.get("detail", ""),
                    details="",
                )
            ]
    except Exception:
        pass

    return []


def _get_issue_detail_string(detail: dict) -> str:
    if "text" in detail:
        return detail["text"]
    return next(
        (_get_detail_coding_string(coding) for coding in detail.get("coding", [])), ""
    )


def _get_detail_coding_string(coding: dict) -> str:
    return ": ".join(
        s for s in [coding.get("code", ""), coding.get("display", "")] if s
    )


def _read_operational_outcomes(response: requests.Response) -> list[str]:
    outcomes = _read_json_outcomes(response)
    if outcomes:
        return [str(outcome) for outcome in outcomes]

    return [response.text]


def _exception_from_response(response: requests.Response) -> OrchestrateHttpError:
    operational_outcomes = _read_operational_outcomes(response)
    if response.status_code >= 400 and response.status_code < 600:
        return OrchestrateClientError(response.text, operational_outcomes)
    return OrchestrateHttpError()


def _prepare_body(body: Union[bytes, str, Mapping[Any, Any]]) -> bytes:
    if isinstance(body, dict):
        return json.dumps(body).encode("utf-8")
    if isinstance(body, str):
        return body.encode("utf-8")

    return body  # type: ignore


class HttpHandler:
    def __init__(
        self,
        base_url: str,
        default_headers: dict,
        timeout_ms: int,
    ) -> None:
        self.base_url = base_url
        self.__default_headers = default_headers
        self.__timeout_ms = timeout_ms

    def __repr__(self) -> str:
        return f"HttpHandler(base_url={self.base_url})"

    def __merge_headers(self, headers: Optional[dict]) -> dict:
        if headers is None:
            return self.__default_headers
        return {**self.__default_headers, **headers}

    def post(
        self,
        path: str,
        body: Union[str, Mapping[Any, Any], bytes],
        headers: Optional[dict[str, str]] = None,
        parameters: Optional[Mapping[str, Optional[str]]] = None,
    ) -> Any:
        request_headers = self.__merge_headers(headers)

        prepared_body = _prepare_body(body)
        url = f"{self.base_url}{path}"

        response = requests.post(
            url,
            data=prepared_body,
            headers=request_headers,
            params=parameters,
            timeout=self.__timeout_ms / 1000,
        )
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as http_error:
            raise _exception_from_response(response) from http_error

        if (
            request_headers["Accept"] in ["application/zip", "application/pdf"]
        ) and response.content:
            return response.content

        if (request_headers["Accept"] == "application/json") and response.text:
            return response.json()

        return response.text

    def get(
        self,
        path: str,
        headers: Optional[dict] = None,
        parameters: Optional[Mapping[str, Optional[str]]] = None,
    ) -> Any:
        request_headers = self.__merge_headers(headers)

        url = f"{self.base_url}{path}"
        response = requests.get(
            url,
            headers=request_headers,
            params=parameters,
            timeout=self.__timeout_ms / 1000,
        )
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as http_error:
            raise _exception_from_response(response) from http_error

        if (request_headers["Accept"] == "application/json") and response.text:
            return response.json()

        return response.text


def create_http_handler(
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    timeout_ms: Optional[int] = None,
) -> HttpHandler:
    additional_headers = _get_additional_headers()
    priority_base_url = _get_priority_base_url(base_url)
    priority_timeout_ms = _get_priority_timeout_ms(timeout_ms)
    default_headers = {
        **(additional_headers or {}),
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    priority_api_key = _get_priority_from_environment(
        api_key, _API_KEY_ENVIRONMENT_VARIABLE
    )
    if priority_api_key is not None:
        default_headers["x-api-key"] = priority_api_key

    return HttpHandler(
        base_url=priority_base_url,
        default_headers=default_headers,
        timeout_ms=priority_timeout_ms,
    )


def create_identity_http_handler(
    api_key: Optional[str] = None,
    metrics_key: Optional[str] = None,
    base_url: Optional[str] = None,
    timeout_ms: Optional[int] = None,
) -> HttpHandler:
    additional_headers = _get_additional_headers()
    priority_url = _get_priority_from_environment(
        base_url, _IDENTITY_URL_ENVIRONMENT_VARIABLE
    )
    priority_timeout_ms = _get_priority_timeout_ms(timeout_ms)
    default_headers = {
        **(additional_headers or {}),
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    priority_api_key = _get_priority_from_environment(
        api_key, _IDENTITY_API_KEY_ENVIRONMENT_VARIABLE
    )
    priority_metrics_key = _get_priority_from_environment(
        metrics_key, _IDENTITY_METRICS_KEY_ENVIRONMENT_VARIABLE
    )

    if priority_url is None:
        raise ArgumentError(
            f"Identity URL is required. Specify in the constructor or set '{_IDENTITY_URL_ENVIRONMENT_VARIABLE}' environment variable."
        )

    if priority_api_key is not None:
        default_headers["x-api-key"] = priority_api_key
    if priority_metrics_key is not None:
        header_metrics_key = priority_metrics_key.replace("Basic ", "")
        default_headers["Authorization"] = f"Basic {header_metrics_key}"

    return HttpHandler(
        base_url=priority_url,
        default_headers=default_headers,
        timeout_ms=priority_timeout_ms,
    )


def create_local_hashing_http_handler(
    base_url: Optional[str] = None, timeout_ms: Optional[int] = None
) -> HttpHandler:
    additional_headers = _get_additional_headers()
    priority_url = _get_priority_from_environment(
        base_url, _IDENTITY_LOCAL_HASHING_URL_ENVIRONMENT_VARIABLE
    )
    priority_timeout_ms = _get_priority_timeout_ms(timeout_ms)

    default_headers = {
        **(additional_headers or {}),
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    if priority_url is None:
        raise ArgumentError(
            f"Local Hashing URL is required. Specify in the constructor or set '{_IDENTITY_LOCAL_HASHING_URL_ENVIRONMENT_VARIABLE}' environment variable."
        )

    return HttpHandler(
        base_url=priority_url,
        default_headers=default_headers,
        timeout_ms=priority_timeout_ms,
    )
