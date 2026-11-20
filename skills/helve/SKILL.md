---
name: helve
description: >-
  Discover and call 330+ external APIs across 260+ providers through Helve
  (https://helve.dev) at 0% per-call markup ($1 free credit ≈ 1,000 Serper
  searches or 1,000 Exa scrapes) with spend_limit_usd caps and $0 failed-call
  escrow. Load when the user explicitly asks to use Helve or calls Helve tools.
---

# Helve — Hermes Agent Skill

Helve (`https://helve.dev`) is a hosted API gateway giving Hermes access to **330+ APIs across 260+ providers** (multi-engine web search, page extraction, audio transcription, SEC EDGAR filings, GitHub, LLMs, TTS, finance, science, and developer data) through one prepaid balance at **0% per-call markup**.

- **$1 free credit** on signup (no credit card required) — `$1 free credit ≈ 1,000 Serper searches or 1,000 Exa scrapes at 0% markup`.
- **Non-expiring packs** start at `$5` (`$5 / $10 / $25 / $100`).
- **Failed calls cost `$0.00`**: upstream errors never debit your balance.
- **Deterministic budget caps**: set `spend_limit_usd` per API key at `https://helve.dev/dashboard` (server returns HTTP `402` if a call would exceed the cap).

## Workflow

1. **Discover first (free, no key needed):**
   Call `helve_search_tools(query="...")` or `helve_list_categories()` to find the exact `tool_id`, inspect its `input_schema`, and check `pricing_hint`.
2. **Confirm paid calls with the user:**
   - Free public-data tools (`$0.00`, e.g. `sec_edgar.search_filings`, `github.search_repositories`, `arxiv.search_papers`) cost nothing.
   - Before running a metered paid tool (anything with a non-zero `pricing_hint`), state the `tool_id`, key arguments, and `pricing_hint`, and confirm with the user unless they already approved the workflow and budget.
3. **Execute with schema-verified arguments:**
   Call `helve_call_tool(tool_id="...", arguments={...})`.
   Verified example payloads:
   - Web search: `tool_id="helve.web_search"`, `arguments={"query": "NVIDIA FY2026 revenue"}`
   - Page extract: `tool_id="helve.web_extract"`, `arguments={"urls": ["https://docs.helve.dev"]}`
   - SEC filings (free): `tool_id="sec_edgar.search_filings"`, `arguments={"q": "NVIDIA", "limit": 5}`
   - Exa research Q&A: `tool_id="exa.answer"`, `arguments={"query": "Compare MCP transports", "text": true}`
4. **Report cost transparently:**
   Surface the returned cost and any `402 spend_limit_exceeded` message clearly. Never paste or ask the user to paste `sk_live_...` keys into chat; direct them to configure `HELVE_API_KEY` in their Hermes profile `.env`.
5. **Missing API?**
   If `helve_search_tools` returns no match, call `helve_request_tool(tool_name="...", use_case="...")`.

## Optional MCP OAuth Transport

If you prefer Hermes's native remote MCP client with OAuth 2.1 (no API key needed), add this to `~/.hermes/config.yaml` and run `hermes mcp login helve`:

```yaml
mcp_servers:
  helve:
    url: https://helve.dev/mcp
    auth: oauth
    trust: untrusted
```

## Security & Disclosure

- Tool arguments are sent to `https://helve.dev` and forwarded to the selected upstream provider.
- `HELVE_API_KEY` is read exclusively through Hermes's profile-scoped secret store (`agent.secret_scope.get_secret("HELVE_API_KEY")`).
- This skill never instructs the agent to fetch or overwrite its own files; updates arrive only through `hermes plugins update`.
