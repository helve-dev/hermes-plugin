# Helve — Hermes Agent Plugin

[![Hermes Marketplace](https://img.shields.io/badge/Hermes%20Marketplace-official%20catalog-1e40af)](https://hermes-agent.nousresearch.com/marketplace/helve)
[![CI](https://github.com/helve-dev/hermes-plugin/actions/workflows/ci.yml/badge.svg)](https://github.com/helve-dev/hermes-plugin/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Give [Hermes Agent](https://github.com/NousResearch/hermes-agent) native access to **330+ APIs across 260+ providers** — multi-engine web search, page extraction, audio transcription, SEC EDGAR filings, GitHub, LLMs, TTS, finance, science, and developer data — through **one prepaid balance at 0% per-call markup**.

- **$1 free credit ≈ 1,000 Serper searches or 1,000 Exa scrapes at 0% markup** (no credit card required; non-expiring top-up packs from `$5`).
- **Deterministic `spend_limit_usd` caps** per API key (server-enforced HTTP `402` before overspend).
- **`$0.00` failed-call escrow**: upstream failures never debit your balance.
- **Zero Python dependencies**: pure Python standard library (`urllib.request`), zero conflicts with Hermes's core lockfile.

## Install

Helve is listed in the official [NousResearch Hermes Marketplace](https://hermes-agent.nousresearch.com/marketplace/helve):

```bash
hermes plugins install helve
```

Or install directly from GitHub:

```bash
hermes plugins install https://github.com/helve-dev/hermes-plugin --enable
```

During install, Hermes prompts for `HELVE_API_KEY` (get a free `sk_live_...` key with `$1.00` credit at [helve.dev/signup](https://helve.dev/signup)). Discovery tools (`helve_search_tools` and `helve_list_categories`) work immediately even without an API key.

### Optional: Native MCP OAuth (Zero API Keys)

Prefer OAuth 2.1 instead of an API key? Add Helve's hosted Streamable HTTP MCP server to `~/.hermes/config.yaml`:

```yaml
mcp_servers:
  helve:
    url: https://helve.dev/mcp
    auth: oauth
    trust: untrusted
```

Then authenticate once:

```bash
hermes mcp login helve
```

## Tools & Skill Provided

| Surface | Auth Required | What It Does |
|---|---|---|
| `helve_search_tools` | None (free) | Search 330+ APIs by intent or category; returns exact `tool_id`, JSON `input_schema`, and upfront `pricing_hint` |
| `helve_list_categories` | None (free) | Browse all catalog categories with tool counts and sample `tool_id` values |
| `helve_call_tool` | `HELVE_API_KEY` | Execute any discovered `tool_id` with arguments at 0% markup (`$0.00` on free tools and failed calls) |
| `helve_request_tool` | `HELVE_API_KEY` | Report a missing API or capability so Helve can prioritize onboarding it |
| `helve:helve` (skill) | — | Bundled workflow instructions (`skill_view("helve:helve")`) for schema inspection, cost confirmation, and budget caps |

## Example Prompts in Hermes

```text
Search Helve for SEC 10-K filing tools and pull NVIDIA's latest filings.
```

```text
Use Helve to search for recent benchmarks on Hermes Agent plugins and extract the top 3 pages.
```

## Disclosure

Helve ([helve.dev](https://helve.dev), maintained by `helve-dev`) is a hosted third-party API gateway. Before installing, note:

- **Network calls:** `helve_search_tools` and `helve_list_categories` call `https://helve.dev/v1/tools*`. `helve_call_tool` sends your `tool_id` and `arguments` to `https://helve.dev/v1/tools/call` and on to the upstream provider.
- **Billing:** Discovery and 300+ public-data tools cost `$0.00`. Metered paid tools debit your prepaid Helve balance at exact upstream cost (`0%` per-call markup); failed calls debit `$0.00`. You can set hard per-key `spend_limit_usd` caps at [helve.dev/dashboard](https://helve.dev/dashboard).
- **Credentials:** `HELVE_API_KEY` is read exclusively via Hermes's profile-scoped `agent.secret_scope.get_secret("HELVE_API_KEY")`. The plugin never reads `.env` files, keychains, or other credential stores directly.
- **No hooks, telemetry, background processes, or self-updating code:** This plugin registers four tools and one bundled skill. Updates reach users only through `hermes plugins update`.

## Local Tests

```bash
python3 -m unittest discover -s tests -v
```

## Related Repositories

- [helve-dev/helve-mcp](https://github.com/helve-dev/helve-mcp) — Hosted MCP server, npm/PyPI stdio bridges, framework adapters, and Agent Skills
- [helve-dev/company-dossier](https://github.com/helve-dev/company-dossier) — Runnable zero-dependency Company & SEC Research Dossier CLI
- [helve-dev/langsmith-tool-gateway-starter](https://github.com/helve-dev/langsmith-tool-gateway-starter) — Runnable starter kit for LangSmith Tool Gateway + Helve

## License

MIT — see [LICENSE](LICENSE).
