"""Small, offline tests. Never import target-project code or start a model."""
from __future__ import annotations

from contextlib import redirect_stdout
import copy
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("installer", ROOT / "scripts/install.py")
installer = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(installer)


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.target = Path(self.tmp.name) / "project"
        self.target.mkdir()
        self.output = io.StringIO()
        self.redirect = redirect_stdout(self.output)
        self.redirect.__enter__()
        self.addCleanup(self.redirect.__exit__, None, None, None)

    def write(self, relative, text):
        p = self.target / relative
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        return p

    def install(self):
        changes, _ = installer.make_plan(self.target, "test-revision")
        installer.apply_plan(self.target, changes)
        return changes

    def snapshot(self):
        return {str(p.relative_to(self.target)): p.read_bytes()
                for p in self.target.rglob("*") if p.is_file() and not p.is_symlink()}

    def test_dry_run_writes_nothing(self):
        changes, notes = installer.make_plan(self.target, "test")
        self.assertGreater(len(changes), 5)
        self.assertEqual(self.snapshot(), {})

    def test_fresh_install_passes_static_check(self):
        self.install()
        self.assertEqual(installer.check(self.target), 0)
        cfg = installer.load_toml((self.target / ".codex/config.toml").read_text(encoding="utf-8"), "test")
        self.assertEqual(cfg["agents"], installer.SETTINGS)
        self.assertNotIn("model", cfg)
        self.assertNotIn("model_reasoning_effort", cfg)

    def test_reinstall_is_idempotent(self):
        self.install()
        before = self.snapshot()
        changes, _ = installer.make_plan(self.target, "test-revision")
        self.assertEqual(changes, [])
        installer.apply_plan(self.target, changes)
        self.assertEqual(before, self.snapshot())

    def test_existing_model_security_comments_preserved(self):
        self.write(".codex/config.toml", '# project note\nmodel="chosen-model"\nmodel_reasoning_effort="max"\nsandbox_mode="read-only"\n[agents]\nenabled=false # keep comment\nmax_threads=6\ndefault_subagent_reasoning_effort="xhigh"\n[agents.helper]\ndescription="keep helper"\n')
        self.install()
        text = (self.target / ".codex/config.toml").read_text(encoding="utf-8")
        cfg = installer.load_toml(text, "test")
        self.assertEqual(cfg["model"], "chosen-model")
        self.assertEqual(cfg["model_reasoning_effort"], "max")
        self.assertEqual(cfg["sandbox_mode"], "read-only")
        self.assertEqual(cfg["agents"]["helper"]["description"], "keep helper")
        self.assertNotIn("max_threads", cfg["agents"])
        self.assertIn("# project note", text)
        self.assertIn("keep comment", text)

    def test_existing_agents_text_preserved(self):
        old = "# Project instructions\nUse existing style and preserve data.\n"
        self.write("AGENTS.md", old)
        self.install()
        text = (self.target / "AGENTS.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith(old))
        self.assertEqual(text.count(installer.BEGIN), 1)

    def test_state_code_results_and_readme_preserved(self):
        for rel in ("research/STATE.md", "train.py", "experiments/existing/raw.txt", "README.md", "START.txt"):
            self.write(rel, "user-owned " + rel)
        self.install()
        for rel in ("research/STATE.md", "train.py", "experiments/existing/raw.txt", "README.md", "START.txt"):
            self.assertEqual((self.target / rel).read_text(encoding="utf-8"), "user-owned " + rel)

    def test_custom_engineer_conflict_prevents_all_writes(self):
        self.write(".codex/agents/engineer.toml", 'name="engineer"\ndescription="custom"\ndeveloper_instructions="keep"\n')
        before = self.snapshot()
        with self.assertRaises(installer.Conflict):
            installer.make_plan(self.target, "test")
        self.assertEqual(before, self.snapshot())

    def test_custom_guide_conflict_prevents_all_writes(self):
        self.write(".codex/guides/research.md", "custom research rules")
        before = self.snapshot()
        with self.assertRaises(installer.Conflict):
            installer.make_plan(self.target, "test")
        self.assertEqual(before, self.snapshot())

    def test_modified_managed_block_not_overwritten(self):
        self.install()
        p = self.target / "AGENTS.md"
        p.write_text(p.read_text(encoding="utf-8").replace("# Research workflow", "# Local changes"), encoding="utf-8")
        before = self.snapshot()
        with self.assertRaises(installer.Conflict):
            installer.make_plan(self.target, "new-version")
        self.assertEqual(before, self.snapshot())

    def test_edits_outside_managed_block_preserved(self):
        self.install()
        p = self.target / "AGENTS.md"
        p.write_text("# New project rule\n" + p.read_text(encoding="utf-8"), encoding="utf-8")
        self.install()
        self.assertTrue(p.read_text(encoding="utf-8").startswith("# New project rule"))
        self.assertEqual(p.read_text(encoding="utf-8").count(installer.BEGIN), 1)

    def test_known_legacy_agents_migrates(self):
        old = b"# Research workflow\nKnown released instructions.\n"
        self.write("AGENTS.md", old.decode())
        manifest, legacy, files = installer.read_package()
        legacy = copy.deepcopy(legacy)
        legacy["AGENTS.md"].append(installer.digest(old))
        with patch.object(installer, "read_package", return_value=(manifest, legacy, files)):
            self.install()
        text = (self.target / "AGENTS.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith(installer.BEGIN))
        self.assertNotIn("Known released instructions", text)

    def test_unknown_legacy_agents_needs_review(self):
        self.write("AGENTS.md", "# Research workflow\nUser changes not in a release.\n")
        with self.assertRaises(installer.Conflict):
            installer.make_plan(self.target, "test")

    def test_inline_agents_fails_closed(self):
        text = 'model="keep"\nagents={enabled=false}\n'
        self.write(".codex/config.toml", text)
        before = self.snapshot()
        with self.assertRaises(installer.Conflict):
            installer.make_plan(self.target, "test")
        self.assertEqual(self.snapshot(), before)

    def test_implicit_parent_table_supported(self):
        merged = installer.merge_config('[agents.helper]\ndescription="keep"\n')
        cfg = installer.load_toml(merged, "test")
        self.assertEqual(cfg["agents"]["enabled"], True)
        self.assertEqual(cfg["agents"]["helper"]["description"], "keep")

    def test_fake_header_inside_multiline_not_changed(self):
        text = 'developer_instructions="""\n[agents]\nenabled=false\n"""\n'
        with self.assertRaises(installer.Conflict):
            installer.merge_config(text)

    def test_backups_preserve_exact_prior_bytes(self):
        old = b"# User rules\nDo not delete results.\n"
        self.write("AGENTS.md", old.decode())
        self.install()
        backups = list((self.target / installer.BACKUPS).iterdir())
        self.assertEqual(len(backups), 1)
        self.assertEqual((backups[0] / "AGENTS.md").read_bytes(), old)
        records = json.loads((backups[0] / "RESTORE.json").read_text(encoding="utf-8"))
        self.assertTrue(any(r["path"] == "AGENTS.md" and r["existed"] for r in records))

    def test_gitignore_preserves_existing_and_is_idempotent(self):
        self.write(".gitignore", "data/\n# keep\n")
        self.install()
        self.install()
        text = (self.target / ".gitignore").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("data/\n# keep\n"))
        self.assertEqual(text.count(installer.IGNORE_BEGIN), 1)

    def test_pinned_engineer_effort_detected(self):
        self.install()
        p = self.target / ".codex/agents/engineer.toml"
        p.write_text('model_reasoning_effort="max"\n' + p.read_text(encoding="utf-8"), encoding="utf-8")
        self.assertEqual(installer.check(self.target), 2)

    def test_root_override_requires_explicit_merge(self):
        self.write("AGENTS.override.md", "# Existing stricter rules\n")
        self.install()
        self.assertEqual(installer.check(self.target), 2)
        payload = (ROOT / "payload/AGENTS.md").read_text(encoding="utf-8")
        self.write("AGENTS.override.md", "# Existing stricter rules\n\n" + payload)
        self.assertEqual(installer.check(self.target), 0)

    def test_duplicate_agent_fails_before_writes(self):
        self.write(".codex/agents/another.toml", 'name="engineer"\ndescription="duplicate"\ndeveloper_instructions="keep"\n')
        before = self.snapshot()
        with self.assertRaises(installer.Conflict):
            installer.make_plan(self.target, "test")
        self.assertEqual(self.snapshot(), before)

    def test_legacy_registration_requires_review(self):
        self.write(".codex/config.toml", '[agents.engineer]\nconfig_file="old.toml"\n')
        with self.assertRaises(installer.Conflict):
            installer.make_plan(self.target, "test")

    def test_symlink_is_not_followed(self):
        outside = Path(self.tmp.name) / "outside"
        outside.mkdir()
        try:
            (self.target / ".codex").symlink_to(outside, target_is_directory=True)
        except OSError:
            self.skipTest("Symlink creation unavailable")
        with self.assertRaises(installer.Conflict):
            installer.make_plan(self.target, "test")
        self.assertEqual(list(outside.iterdir()), [])

    def test_home_source_root_and_escape_rejected(self):
        for value in (str(Path.home()), str(ROOT), str(ROOT / "payload"), str(Path(self.tmp.name).anchor)):
            with self.assertRaises(installer.Conflict):
                installer.target_root(value)
        with self.assertRaises(installer.Conflict):
            installer.safe_path(self.target, "../outside")
        with self.assertRaises(installer.Conflict):
            installer.safe_path(self.target, ".git/config")

    def test_provenance_has_no_absolute_target_path(self):
        self.install()
        meta = (self.target / installer.META).read_text(encoding="utf-8")
        self.assertNotIn(str(self.target), meta)
        self.assertEqual(json.loads(meta)["runtime_status"], "NOT_VERIFIED")

    def test_concurrent_change_detected_before_write(self):
        self.write("AGENTS.md", "# Before\n")
        changes, _ = installer.make_plan(self.target, "test")
        self.write("AGENTS.md", "# Changed concurrently\n")
        before = self.snapshot()
        with self.assertRaises(installer.Conflict):
            installer.apply_plan(self.target, changes)
        self.assertEqual(before, self.snapshot())

    def test_malformed_markers_fail_closed(self):
        self.write("AGENTS.md", installer.BEGIN + "\nmissing end\n")
        with self.assertRaises(installer.Conflict):
            installer.make_plan(self.target, "test")

    def test_engineer_has_no_effort_or_model_pin(self):
        cfg = installer.load_toml((ROOT / "payload/.codex/agents/engineer.toml").read_text(encoding="utf-8"), "payload")
        self.assertNotIn("model_reasoning_effort", cfg)
        self.assertNotIn("model", cfg)


if __name__ == "__main__":
    unittest.main()
