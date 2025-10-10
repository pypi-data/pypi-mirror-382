from typing import Any, Dict, Optional, Tuple

import requests

from ..constants import BASE_URL, CONNECT_TIMEOUT_S, READ_TIMEOUT_S
from .errors import APIError


_session = requests.Session()
_TIMEOUT: Tuple[int, int] = (CONNECT_TIMEOUT_S, READ_TIMEOUT_S)


def _join_url(path: str) -> str:
    base = BASE_URL[:-1] if BASE_URL.endswith("/") else BASE_URL
    if not path.startswith("/"):
        path = "/" + path
    return base + path


def request(method: str, path: str, *, json: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None, timeout: Optional[Tuple[int, int]] = None) -> requests.Response:
    url = _join_url(path)
    resp = _session.request(method=method.upper(), url=url, json=json, params=params, timeout=timeout or _TIMEOUT)
    return resp


def request_json(method: str, path: str, *, json: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None, timeout: Optional[Tuple[int, int]] = None) -> Dict[str, Any]:
    resp = request(method, path, json=json, params=params, timeout=timeout)
    try:
        data = resp.json()
    except ValueError:
        raise APIError("Invalid JSON response", details=resp.text, status_code=resp.status_code)

    status = data.get("status")
    if status == "success":
        return data
    elif status == "error":
        err = data.get("error", {})
        message = err.get("message", "Unknown error")
        details = err.get("details")
        raise APIError(message, details=details, status_code=resp.status_code)
    else:
        # Fallback: treat as raw JSON when envelope is missing
        return data


