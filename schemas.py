"""Tool JSON schemas registered with Hermes Agent."""

HELVE_SEARCH_TOOLS_SCHEMA = {
    "name": "helve_search_tools",
    "description": (
        "Search Helve's live catalog of 330+ APIs across 260+ providers by "
        "capability or intent. Returns matching tool_id values, input JSON "
        "schemas, and upfront pricing_hint strings (0% markup). Free and "
        "requires no API key."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": (
                    "Natural-language capability or API query, e.g. "
                    "'sec 10-k filings', 'web search', 'audio transcription'."
                ),
            },
            "category": {
                "type": "string",
                "description": "Optional category filter (from helve_list_categories).",
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of tools to return (1-30, default 10).",
                "minimum": 1,
                "maximum": 30,
            },
        },
        "required": ["query"],
    },
}

HELVE_LIST_CATEGORIES_SCHEMA = {
    "name": "helve_list_categories",
    "description": (
        "List all categories in Helve's live 330+ API catalog with tool counts "
        "and sample tool_id values. Free and requires no API key."
    ),
    "parameters": {
        "type": "object",
        "properties": {},
    },
}

HELVE_CALL_TOOL_SCHEMA = {
    "name": "helve_call_tool",
    "description": (
        "Execute any Helve tool_id discovered via helve_search_tools. Uses "
        "HELVE_API_KEY under your prepaid USD balance (0% markup; $0.00 on "
        "free public APIs and failed upstream calls; respects API key "
        "spend_limit_usd caps). Always inspect the tool schema and pricing_hint "
        "with helve_search_tools first, and confirm paid calls with the user."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "tool_id": {
                "type": "string",
                "description": (
                    "Exact tool_id from helve_search_tools, e.g. "
                    "'helve.web_search', 'helve.web_extract', "
                    "'sec_edgar.search_filings', 'exa.answer'."
                ),
            },
            "arguments": {
                "type": "object",
                "description": "JSON object matching the tool's input_schema.",
            },
        },
        "required": ["tool_id"],
    },
}

HELVE_REQUEST_TOOL_SCHEMA = {
    "name": "helve_request_tool",
    "description": (
        "Report a missing third-party API or capability when helve_search_tools "
        "does not have what you need. Requires HELVE_API_KEY."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "tool_name": {
                "type": "string",
                "description": "Name of the missing API or tool (e.g. 'Stripe', 'Resend').",
            },
            "use_case": {
                "type": "string",
                "description": "Short description of what you are trying to accomplish.",
            },
            "provider": {
                "type": "string",
                "description": "Optional API provider or vendor name.",
            },
            "category": {
                "type": "string",
                "description": "Optional category (e.g. 'finance', 'search', 'dev').",
            },
            "docs_url": {
                "type": "string",
                "description": "Optional link to the API's official documentation.",
            },
        },
        "required": ["tool_name"],
    },
}
