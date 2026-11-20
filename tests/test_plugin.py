"""Unit and live-discovery tests for the Helve Hermes Agent plugin."""

from __future__ import annotations

import io
import json
import os
import sys
import types
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

import __init__ as plugin  # noqa: E402
import client  # noqa: E402


class _FakeContext:
    def __init__(self) -> None:
        self.tools = {}
        self.skills = {}

    def register_tool(self, name, toolset, schema, handler):
        self.tools[name] = {
            "toolset": toolset,
            "schema": schema,
            "handler": handler,
        }

    def register_skill(self, name, path, description=""):
        self.skills[name] = {"path": Path(path), "description": description}


class PluginStructureTests(unittest.TestCase):
    def test_register_matches_manifest(self) -> None:
        ctx = _FakeContext()
        plugin.register(ctx)

        expected_tools = [
            "helve_search_tools",
            "helve_list_categories",
            "helve_call_tool",
            "helve_request_tool",
        ]
        self.assertEqual(sorted(ctx.tools.keys()), sorted(expected_tools))
        for name, entry in ctx.tools.items():
            self.assertEqual(entry["toolset"], "helve")
            self.assertEqual(entry["schema"]["name"], name)
            self.assertTrue(entry["schema"]["description"])

        self.assertIn("helve", ctx.skills)
        skill_path = ctx.skills["helve"]["path"]
        self.assertTrue(skill_path.is_file(), f"Missing skill file: {skill_path}")
        skill_text = skill_path.read_text(encoding="utf-8")
        self.assertNotIn("agentmail.", skill_text)
        self.assertNotIn("hlv_", skill_text)
        self.assertNotIn("15%", skill_text)
        self.assertNotIn("$0.50", skill_text)

        manifest_text = (PLUGIN_ROOT / "plugin.yaml").read_text(encoding="utf-8")
        for name in expected_tools:
            self.assertIn(f"- {name}", manifest_text)
        self.assertIn("- HELVE_API_KEY", manifest_text)

    def test_secret_scope_preferred_over_os_environ(self) -> None:
        fake_agent = types.ModuleType("agent")
        fake_scope = types.ModuleType("agent.secret_scope")
        fake_scope.get_secret = lambda name: (
            "sk_live_from_hermes_scope" if name == "HELVE_API_KEY" else None
        )
        fake_agent.secret_scope = fake_scope

        with mock.patch.dict(
            sys.modules,
            {"agent": fake_agent, "agent.secret_scope": fake_scope},
        ), mock.patch.dict(os.environ, {"HELVE_API_KEY": "sk_live_from_env"}):
            self.assertEqual(client.get_api_key(), "sk_live_from_hermes_scope")

    def test_call_tool_missing_api_key_returns_clear_error(self) -> None:
        with mock.patch.object(client, "get_api_key", return_value=None):
            res = client.call_tool("helve.web_search", {"query": "hermes"})
        self.assertFalse(res["ok"])
        self.assertEqual(res["error"], "missing_api_key")
        self.assertIn("https://helve.dev/signup", res["message"])

    def test_402_spend_limit_exceeded_surfaces_budget_hint(self) -> None:
        err_body = io.BytesIO(
            json.dumps({"error": "spend_limit_exceeded"}).encode("utf-8")
        )
        http_err = urllib.error.HTTPError(
            url="https://helve.dev/v1/tools/call",
            code=402,
            msg="Payment Required",
            hdrs={},
            fp=err_body,
        )
        with mock.patch.object(
            client, "get_api_key", return_value="sk_live_test"
        ), mock.patch("urllib.request.urlopen", side_effect=http_err):
            res = client.call_tool("helve.web_search", {"query": "test"})

        self.assertFalse(res["ok"])
        self.assertEqual(res["status_code"], 402)
        self.assertIn("spend_limit_usd", res["hint"])

    def test_handler_serializes_json(self) -> None:
        ctx = _FakeContext()
        plugin.register(ctx)
        with mock.patch.object(
            plugin,
            "search_tools",
            return_value={"tools": [{"id": "helve.web_search"}]},
        ):
            raw = ctx.tools["helve_search_tools"]["handler"]({"query": "web search"})
        parsed = json.loads(raw)
        self.assertEqual(parsed["tools"][0]["id"], "helve.web_search")


class LiveDiscoverySmokeTests(unittest.TestCase):
    @unittest.skipIf(
        os.environ.get("SKIP_LIVE_TESTS") == "1",
        "Skipped via SKIP_LIVE_TESTS=1",
    )
    def test_live_search_and_categories_no_auth(self) -> None:
        with mock.patch.object(client, "get_api_key", return_value=None):
            search_res = client.search_tools("sec filings", limit=5)
            self.assertIn("tools", search_res)
            tool_ids = [t.get("id") for t in search_res["tools"]]
            self.assertTrue(
                any("sec_edgar" in str(tid) for tid in tool_ids),
                f"Expected sec_edgar tool in {tool_ids}",
            )

            cat_res = client.list_categories()
            self.assertTrue(cat_res.get("ok"))
            self.assertGreaterEqual(cat_res.get("total_tools", 0), 300)
            self.assertGreaterEqual(cat_res.get("category_count", 0), 5)


if __name__ == "__main__":
    unittest.main()
