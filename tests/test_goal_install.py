"""Goal distribution integration in temporary folders only."""
import copy
import json
import unittest
from unittest.mock import patch
import test_install as base

installer = base.installer
ROOT = base.ROOT


class GoalInstallTests(unittest.TestCase):
    setUp = base.InstallerTests.setUp
    write = base.InstallerTests.write
    install = base.InstallerTests.install
    snapshot = base.InstallerTests.snapshot

    def test_goal_user_form_is_create_only_and_history_survives(self):
        self.write('research/GOAL_CONFIG.md', 'User budget and monk choice')
        self.write('research/goals/existing/ledger.jsonl', 'Past pending reservation')
        self.install()
        self.assertEqual((self.target / 'research/GOAL_CONFIG.md').read_text(), 'User budget and monk choice')
        self.assertEqual((self.target / 'research/goals/existing/ledger.jsonl').read_text(), 'Past pending reservation')
        self.assertEqual(installer.check(self.target), 0)
        self.assertEqual(installer.make_plan(self.target, 'test-revision')[0], [])

    def test_setup_record_is_managed_and_user_setup_survives(self):
        self.write('research/goals/g1/SETUP.md', 'User authorized allocation and pending costs')
        self.install()
        self.assertEqual((self.target / 'research/goals/g1/SETUP.md').read_text(),
                         'User authorized allocation and pending costs')
        manifest, _, payload = installer.read_package()
        item = next(item for item in manifest['files'] if item['destination'] == 'research/_templates/GOAL_SETUP.md')
        self.assertEqual(item['mode'], 'managed-file')
        self.assertEqual((self.target / item['destination']).read_bytes(), payload[item['destination']])
        self.assertIn('GOAL_SETUP.md', payload['.codex/guides/goal.md'].decode())
        self.assertIn('SETUP', payload['research/_templates/GOAL_PROGRESS.md'].decode())

    def test_all_roles_unpinned_and_required_fields(self):
        self.install()
        for role in installer.ROLES:
            cfg = installer.load_toml((self.target / f'.codex/agents/{role}.toml').read_text(), role)
            self.assertEqual(cfg['name'], role)
            self.assertTrue(cfg['description'])
            self.assertTrue(cfg['developer_instructions'])
            self.assertNotIn('model', cfg)
            self.assertNotIn('model_reasoning_effort', cfg)

    def test_role_collisions_and_legacy_fail_before_writes(self):
        for role in ('supervisor', 'qa'):
            path = self.write('.codex/agents/other.toml', f'name="{role}"\ndescription="custom"\ndeveloper_instructions="keep"\n')
            before = self.snapshot()
            with self.assertRaises(installer.Conflict):
                installer.make_plan(self.target, 'test')
            self.assertEqual(before, self.snapshot())
            path.unlink()
            path = self.write('.codex/config.toml', f'[agents.{role}]\nconfig_file="old.toml"\n')
            with self.assertRaises(installer.Conflict):
                installer.make_plan(self.target, 'test')
            path.unlink()

    def test_review_role_pinned_effort_or_bad_name_fails_check(self):
        self.install()
        for role in ('supervisor', 'qa'):
            path = self.target / f'.codex/agents/{role}.toml'
            old = path.read_text()
            for text in ('model_reasoning_effort="high"\n' + old, old.replace(f'name = "{role}"', 'name="wrong"')):
                path.write_text(text)
                self.assertEqual(installer.check(self.target), 2)
            path.write_text(old)

    def test_v52_upgrade_adds_goal_without_resetting_state_and_reinstalls(self):
        manifest, legacy, payload = installer.read_package()
        old = copy.deepcopy(manifest)
        old['version'] = '5.2.0'
        new_paths = {item['destination'] for item in old['files'] if 'goal' in item['destination'].lower() or
                     item['destination'].endswith(('supervisor.toml', 'qa.toml', 'PROXY_CONTRACT.md', 'CANDIDATE.md'))}
        old['files'] = [item for item in old['files'] if item['destination'] not in new_paths]
        old_payload = {k: v for k, v in payload.items() if k not in new_paths}
        old_payload['.codex/guides/research.md'] = b'# Previous released research guidance\n'
        for item in old['files']:
            item['sha256'] = installer.digest(old_payload[item['destination']])
        with patch.object(installer, 'read_package', return_value=(old, legacy, old_payload)):
            self.install()
        self.assertFalse((self.target / '.codex/agents/qa.toml').exists())
        self.write('research/STATE.md', 'Existing monk task and evidence')
        self.write('research/GOAL_CONFIG.md', 'Already filled user goal')
        self.install()
        self.assertEqual((self.target / 'research/STATE.md').read_text(), 'Existing monk task and evidence')
        self.assertEqual((self.target / 'research/GOAL_CONFIG.md').read_text(), 'Already filled user goal')
        self.assertTrue((self.target / '.codex/agents/qa.toml').exists())
        self.assertEqual(installer.check(self.target), 0)
        self.assertEqual(installer.make_plan(self.target, 'test-revision')[0], [])
        self.assertEqual(json.loads((self.target / installer.META).read_text())['version'],
                         (ROOT / 'VERSION').read_text().strip())

    def test_v52_hashes_and_instruction_wiring(self):
        manifest, legacy, payload = installer.read_package()
        self.assertIn('51e3d37c2354c9fb1890fdb538e6f9c67ca4890c24604fb5683266dfdbb94881', legacy['.codex/agents/engineer.toml'])
        for relative in ('AGENTS.md', '.codex/RESEARCH_START.txt', '.codex/VERIFY_SETUP.md', '.codex/agents/engineer.toml',
                         '.codex/guides/research.md', '.codex/guides/monk.md'):
            self.assertIn('.codex/guides/goal.md', payload[relative].decode())
        goal = payload['.codex/guides/goal.md'].decode()
        for invariant in ('NEEDS_USER_RUN', 'GOAL_MET', '중복', 'USER_ONLY', 'bounded executor', 'medium', 'xhigh'):
            self.assertIn(invariant, goal)
        form = next(item for item in manifest['files'] if item['destination'] == 'research/GOAL_CONFIG.md')
        self.assertEqual(form['mode'], 'create-only')


if __name__ == '__main__':
    unittest.main()
