"""Zero-dependency HTTP client for the Helve API gateway (https://helve.dev)."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any, Dict, Optional

DEFAULT_BASE_URL = "https://helve.dev"
DEFAULT_TIMEOUT_SECONDS = 45
USER_AGENT = "helve-hermes-plugin/0.1.0"


def get_api_key() -> Optional[str]:
    """Read HELVE_API_KEY through Hermes's profile-scoped secret store first.

    Per Hermes Plugin Catalog Rule 11, plugins read declared secrets via
    ``agent.secret_scope.get_secret`` so multi-profile sessions stay isolated.
    Falls back to ``os.environ`` only when imported outside Hermes (e.g. unit
    tests or standalone CLI smoke checks).
    """
    try:
        from agent.secret_scope import get_secret  # type: ignore

        value = get_secret("HELVE_API_KEY")
        if value and str(value).strip():
            return str(value).strip()
        return None
    except ImportError:
        value = os.environ.get("HELVE_API_KEY")
        if value and value.strip():
            return value.strip()
        return None


def get_base_url() -> str:
    """Return the Helve API base URL (defaults to https://helve.dev)."""
    try:
        from agent.secret_scope import get_secret  # type: ignore

        custom = get_secret("HELVE_BASE_URL")
        if custom and str(custom).strip():
            return str(custom).strip().rstrip("/")
    except ImportError:
        custom = os.environ.get("HELVE_BASE_URL")
        if custom and custom.strip():
            return custom.strip().rstrip("/")
    return DEFAULT_BASE_URL


def request_json(
    method: str,
    path: str,
    body: Optional[Dict[str, Any]] = None,
    require_auth: bool = False,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> Dict[str, Any]:
    """Send a JSON HTTP request to Helve and return a structured dictionary."""
    base_url = get_base_url()
    url = f"{base_url}{path}"
    headers: Dict[str, str] = {
        "Accept": "application/json",
        "User-Agent": USER_AGENT,
    }

    api_key = get_api_key()
    if require_auth:
        if not api_key:
            return {
                "ok": False,
                "error": "missing_api_key",
                "message": (
                    "HELVE_API_KEY is not set. Create a free key at "
                    "https://helve.dev/signup ($1 free credit ≈ 1,000 Serper "
                    "searches or 1,000 Exa scrapes at 0% markup) and set "
                    "HELVE_API_KEY in your Hermes profile .env."
                ),
            }
        headers["Authorization"] = f"Bearer {api_key}"
    elif api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    data: Optional[bytes] = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            parsed = json.loads(raw) if raw else {}
            if isinstance(parsed, dict):
                return parsed
            return {"ok": True, "data": parsed}
    except urllib.error.HTTPError as exc:
        raw_err = ""
        try:
            raw_err = exc.read().decode("utf-8", errors="replace")
            parsed_err = json.loads(raw_err)
        except Exception:
            parsed_err = {"raw": raw_err}

        error_payload: Dict[str, Any] = {
            "ok": False,
            "status_code": exc.code,
            "error": parsed_err,
        }
        if exc.code == 402:
            error_payload["hint"] = (
                "Balance exhausted or API key spend_limit_usd cap reached. "
                "Top up or adjust spend_limit_usd at https://helve.dev/dashboard."
            )
        elif exc.code == 401:
            error_payload["hint"] = (
                "Invalid or revoked HELVE_API_KEY (expected sk_live_...). "
                "Verify your key at https://helve.dev/dashboard."
            )
        return error_payload
    except urllib.error.URLError as exc:
        return {
            "ok": False,
            "error": "network_error",
            "message": f"Failed to reach {url}: {exc.reason}",
        }
    except TimeoutError:
        return {
            "ok": False,
            "error": "timeout",
            "message": f"Request to {url} timed out after {timeout}s.",
        }


def search_tools(
    query: str,
    category: Optional[str] = None,
    limit: int = 10,
) -> Dict[str, Any]:
    """Search Helve's catalog of 330+ APIs (no API key required)."""
    bounded_limit = max(1, min(int(limit or 10), 30))
    payload: Dict[str, Any] = {"query": query, "limit": bounded_limit}
    if category:
        payload["category"] = category
    return request_json("POST", "/v1/tools/search", body=payload, require_auth=False)


def list_categories() -> Dict[str, Any]:
    """Summarize Helve's live tool catalog by category (no API key required)."""
    res = request_json("GET", "/v1/tools", require_auth=False)
    tools = res.get("tools")
    if not isinstance(tools, list):
        return res

    buckets: Dict[str, Dict[str, Any]] = {}
    for tool in tools:
        cat = str(tool.get("category") or "other")
        entry = buckets.setdefault(
            cat, {"category": cat, "count": 0, "sample_tool_ids": []}
        )
        entry["count"] += 1
        if len(entry["sample_tool_ids"]) < 5 and tool.get("id"):
            entry["sample_tool_ids"].append(tool["id"])

    categories = sorted(buckets.values(), key=lambda c: (-c["count"], c["category"]))
    return {
        "ok": True,
        "total_tools": len(tools),
        "category_count": len(categories),
        "categories": categories,
    }


def call_tool(
    tool_id: str,
    arguments: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Execute any discovered Helve tool_id with arguments (requires HELVE_API_KEY)."""
    if not tool_id or not str(tool_id).strip():
        return {
            "ok": False,
            "error": "invalid_tool_id",
            "message": "tool_id is required. Run helve_search_tools first to discover tool IDs.",
        }
    payload: Dict[str, Any] = {
        "tool_id": str(tool_id).strip(),
        "arguments": arguments if isinstance(arguments, dict) else {},
    }
    return request_json("POST", "/v1/tools/call", body=payload, require_auth=True)


def request_tool(
    tool_name: str,
    use_case: Optional[str] = None,
    provider: Optional[str] = None,
    category: Optional[str] = None,
    docs_url: Optional[str] = None,
) -> Dict[str, Any]:
    """Request a missing API or tool in Helve's catalog (requires HELVE_API_KEY)."""
    if not tool_name or not str(tool_name).strip():
        return {
            "ok": False,
            "error": "invalid_tool_name",
            "message": "tool_name is required.",
        }
    payload: Dict[str, Any] = {"tool_name": str(tool_name).strip()}
    if use_case:
        payload["use_case"] = use_case
    if provider:
        payload["provider"] = provider
    if category:
        payload["category"] = category
    if docs_url:
        payload["docs_url"] = docs_url
    return request_json("POST", "/v1/tools/request", body=payload, require_auth=True)
