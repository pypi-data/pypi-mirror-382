from __future__ import annotations

import os
import time
from typing import Any, Dict, Iterable, Optional

import requests
import logging


OCS_HEADERS = {"OCS-APIRequest": "true"}


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Environment variable {name} is required but not set. "
            "Set it via .env or export before running."
        )
    return value


def http_request_with_retries(
    method: str,
    url: str,
    *,
    data: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
    timeout: int = 15,
    retries: int = 2,
    verbose: bool = False,
):
    logger = logging.getLogger("ncbulk.nc_api")
    last_exc: Optional[Exception] = None
    for attempt in range(retries + 1):
        try:
            if verbose:
                logger.debug(
                    "HTTP %s %s (attempt %s/%s)",
                    method,
                    url,
                    attempt + 1,
                    retries + 1,
                )
            resp = requests.request(
                method,
                url,
                auth=(
                    _require_env("NEXTCLOUD_ADMIN_USERNAME"),
                    _require_env("NEXTCLOUD_ADMIN_PASSWORD"),
                ),
                headers=OCS_HEADERS,
                data=data,
                params=params,
                timeout=timeout,
            )
            return resp
        except requests.RequestException as exc:  # type: ignore[name-defined]
            last_exc = exc
            if attempt < retries:
                time.sleep(1.0 * (attempt + 1))
    if last_exc:
        raise last_exc


def is_user_absent(
    username: str, *, timeout: int = 15, retries: int = 2, verbose: bool = False
) -> bool:
    resp = http_request_with_retries(
        "GET",
        f"{_require_env('NEXTCLOUD_URL')}/ocs/v2.php/cloud/users/{username}",
        timeout=timeout,
        retries=retries,
        verbose=verbose,
    )
    if resp.status_code == 404:
        return True
    if resp.status_code == 200:
        try:
            data = resp.json()
            ocs = data.get("ocs", {})
            # If data payload present, treat as exists
            if "data" in ocs:
                return False
            meta = ocs.get("meta", {})
            # Nextcloud OCS success usually has ocs/meta/statuscode == 200
            code = int(meta.get("statuscode", 0))
            return code != 200
        except Exception:
            # Fall back to considering user present on any 200 without parseable body
            return False
    # For other 2xx codes treat as present; otherwise absent
    return resp.status_code >= 400


def update_user_field(
    username: str,
    key: str,
    value: str,
    *,
    timeout: int = 15,
    retries: int = 2,
    verbose: bool = False,
):
    return http_request_with_retries(
        "PUT",
        f"{_require_env('NEXTCLOUD_URL')}/ocs/v2.php/cloud/users/{username}",
        data={"key": key, "value": value},
        timeout=timeout,
        retries=retries,
        verbose=verbose,
    )


def create_nextcloud_user(
    username: str,
    password: Optional[str],
    groups: Iterable[str],
    *,
    language: Optional[str] = None,
    timeout: int = 15,
    retries: int = 2,
    verbose: bool = False,
):
    data: Dict[str, Any] = {"userid": username}
    if password:
        data["password"] = password
    for i, g in enumerate(groups):
        data[f"groups[{i}]"] = g
    if language:
        data["language"] = language

    resp = http_request_with_retries(
        "POST",
        f"{_require_env('NEXTCLOUD_URL')}/ocs/v2.php/cloud/users",
        data=data,
        timeout=timeout,
        retries=retries,
        verbose=verbose,
    )
    if resp.status_code == 200:
        return True
    return resp.text


def assign_user_to_group(
    username: str,
    group: str,
    *,
    timeout: int = 15,
    retries: int = 2,
    verbose: bool = False,
):
    return http_request_with_retries(
        "POST",
        f"{_require_env('NEXTCLOUD_URL')}/ocs/v2.php/cloud/users/{username}/groups",
        data={"groupid": group},
        timeout=timeout,
        retries=retries,
        verbose=verbose,
    )
