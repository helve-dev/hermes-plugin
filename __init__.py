"""Helve plugin for Hermes Agent.

Registers four zero-dependency native tools backed by https://helve.dev:
- ``helve_search_tools`` (free, no key required)
- ``helve_list_categories`` (free, no key required)
- ``helve_call_tool`` (requires ``HELVE_API_KEY`` via Hermes secret_scope)
- ``helve_request_tool`` (requires ``HELVE_API_KEY`` via Hermes secret_scope)

Also bundles the ``helve:helve`` skill (``skills/helve/SKILL.md``).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

try:
    from .client import call_tool, list_categories, request_tool, search_tools
    from .schemas import (
        HELVE_CALL_TOOL_SCHEMA,
        HELVE_LIST_CATEGORIES_SCHEMA,
        HELVE_REQUEST_TOOL_SCHEMA,
        HELVE_SEARCH_TOOLS_SCHEMA,
    )
except ImportError:
    from client import call_tool, list_categories, request_tool, search_tools
    from schemas import (
        HELVE_CALL_TOOL_SCHEMA,
        HELVE_LIST_CATEGORIES_SCHEMA,
        HELVE_REQUEST_TOOL_SCHEMA,
        HELVE_SEARCH_TOOLS_SCHEMA,
    )

_SKILL_MD = Path(__file__).parent / "skills" / "helve" / "SKILL.md"


def _handle_search_tools(params: Dict[str, Any], **kwargs: Any) -> str:
    del kwargs
    result = search_tools(
        query=str(params.get("query", "")),
        category=params.get("category"),
        limit=params.get("limit", 10),
    )
    return json.dumps(result, ensure_ascii=False)


def _handle_list_categories(params: Dict[str, Any], **kwargs: Any) -> str:
    del params, kwargs
    return json.dumps(list_categories(), ensure_ascii=False)


def _handle_call_tool(params: Dict[str, Any], **kwargs: Any) -> str:
    del kwargs
    result = call_tool(
        tool_id=str(params.get("tool_id", "")),
        arguments=params.get("arguments"),
    )
    return json.dumps(result, ensure_ascii=False)


def _handle_request_tool(params: Dict[str, Any], **kwargs: Any) -> str:
    del kwargs
    result = request_tool(
        tool_name=str(params.get("tool_name", "")),
        use_case=params.get("use_case"),
        provider=params.get("provider"),
        category=params.get("category"),
        docs_url=params.get("docs_url"),
    )
    return json.dumps(result, ensure_ascii=False)


def register(ctx: Any) -> None:
    """Register Helve tools and bundled skill with Hermes Agent."""
    ctx.register_tool(
        name="helve_search_tools",
        toolset="helve",
        schema=HELVE_SEARCH_TOOLS_SCHEMA,
        handler=_handle_search_tools,
    )
    ctx.register_tool(
        name="helve_list_categories",
        toolset="helve",
        schema=HELVE_LIST_CATEGORIES_SCHEMA,
        handler=_handle_list_categories,
    )
    ctx.register_tool(
        name="helve_call_tool",
        toolset="helve",
        schema=HELVE_CALL_TOOL_SCHEMA,
        handler=_handle_call_tool,
    )
    ctx.register_tool(
        name="helve_request_tool",
        toolset="helve",
        schema=HELVE_REQUEST_TOOL_SCHEMA,
        handler=_handle_request_tool,
    )
    ctx.register_skill(
        "helve",
        _SKILL_MD,
        description=(
            "Use Helve to discover and call 330+ external APIs across 260+ "
            "providers at 0% markup with spend_limit_usd caps and $0 failed-call "
            "escrow. Load when the user asks to use Helve."
        ),
    )


__all__ = ["register"]
