"""Offline regression tests for v5 payload wiring, boundaries, and upgrade behavior.

These tests inspect configuration artifacts; they do not evaluate research quality.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
from unittest.mock import patch

import test_install as base

installer = base.installer
ROOT = base.ROOT


# Reuse fixture helpers without importing or inheriting their test methods.
import unittest
class ResearchUpdateTests(unittest.TestCase):
    setUp = base.InstallerTests.setUp
    write = base.InstallerTests.write
    install = base.InstallerTests.install
    snapshot = base.InstallerTests.snapshot

    def test_research_guide_is_routed_and_installed(self):
        self.install()
        agents = (self.target / "AGENTS.md").read_text(encoding="utf-8")
        guide = self.target / ".codex/guides/research.md"
        self.assertIn(".codex/guides/research.md", agents)
        self.assertEqual(guide.read_bytes(), (ROOT / "payload/.codex/guides/research.md").read_bytes())
        self.assertIn("conjecture", guide.read_text(encoding="utf-8"))
        self.assertIn("proof gap", guide.read_text(encoding="utf-8"))

    def test_hypotheses_have_memory_without_overwriting_user_state(self):
        self.assertIn("proof gap", (ROOT / "payload/research/STATE.md").read_text(encoding="utf-8"))
        old = "# Research state\nAn existing tentative hypothesis, not a verified fact.\n"
        self.write("research/STATE.md", old)
        self.install()
        self.assertEqual((self.target / "research/STATE.md").read_text(encoding="utf-8"), old)

    def test_research_upgrade_does_not_pin_model_or_effort(self):
        _, _, payload = installer.read_package()
        agent = installer.load_toml(payload[".codex/agents/engineer.toml"].decode(), "engineer")
        config = installer.load_toml(payload[".codex/config.toml"].decode(), "config")
        self.assertNotIn("model", agent)
        self.assertNotIn("model_reasoning_effort", agent)
        self.assertNotIn("model", config)
        self.assertNotIn("model_reasoning_effort", config)
        self.assertEqual(config["agents"], installer.SETTINGS)

    def old_package(self):
        manifest, legacy, payload = installer.read_package()
        manifest = copy.deepcopy(manifest)
        payload = dict(payload)
        manifest["version"] = "4.0.0"
        payload["AGENTS.md"] = b"# Research workflow\nPrevious release.\n"
        payload[".codex/guides/research.md"] = b"# Research guide\nPrevious release.\n"
        payload[".codex/RESEARCH_START.txt"] = b"Previous startup prompt.\n"
        for item in manifest["files"]:
            item["sha256"] = installer.digest(payload[item["destination"]])
        return manifest, legacy, payload

    def test_tracked_previous_version_updates_and_reinstall_is_idempotent(self):
        with patch.object(installer, "read_package", return_value=self.old_package()):
            self.install()
        self.write("research/STATE.md", "# Existing research\nKeep this hypothesis.\n")
        self.install()
        current = (ROOT / "payload/.codex/guides/research.md").read_bytes()
        self.assertEqual((self.target / ".codex/guides/research.md").read_bytes(), current)
        self.assertEqual((self.target / "research/STATE.md").read_text(encoding="utf-8"),
                         "# Existing research\nKeep this hypothesis.\n")
        metadata = json.loads((self.target / installer.META).read_text(encoding="utf-8"))
        self.assertEqual(metadata["version"], (ROOT / "VERSION").read_text().strip())
        self.assertEqual(installer.check(self.target), 0)
        changes, _ = installer.make_plan(self.target, "test-revision")
        self.assertEqual(changes, [])

    def test_locally_edited_old_research_guide_blocks_upgrade(self):
        with patch.object(installer, "read_package", return_value=self.old_package()):
            self.install()
        self.write(".codex/guides/research.md", "# User edited research guide\nKeep my rules.\n")
        before = self.snapshot()
        with self.assertRaises(installer.Conflict):
            installer.make_plan(self.target, "v5")
        self.assertEqual(before, self.snapshot())

    def test_payload_checksums_cover_research_update(self):
        manifest, _, payload = installer.read_package()
        self.assertEqual(manifest["version"], (ROOT / "VERSION").read_text().strip())
        for item in manifest["files"]:
            self.assertEqual(item["sha256"], installer.digest(payload[item["destination"]]))

if __name__ == "__main__":
    unittest.main()
