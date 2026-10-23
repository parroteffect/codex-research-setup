"""Tiny offline fixtures only; call the actual guard, never an experiment/executor."""
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
spec = importlib.util.spec_from_file_location("goal_guard", ROOT / "payload/.codex/tools/goal_guard.py")
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


def value(item):
    return json.dumps(item, ensure_ascii=False)


def markdown(config):
    lines = ['# User form', '```toml']
    for key, item in config.items():
        if not isinstance(item, dict):
            lines.append(f'{key} = {value(item)}')
    for section, items in config.items():
        if isinstance(items, dict):
            lines.append(f'[{section}]')
            lines.extend(f'{key} = {value(item)}' for key, item in items.items())
    return '\n'.join(lines) + '\n```\n'


class GoalTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.config_path = self.root / 'config.md'
        self.contract = self.root / 'proxy.md'
        self.source = self.root / 'evaluator.py'
        self.source.write_text('raise RuntimeError("MUST NEVER IMPORT OR EXECUTE")\n')
        self.state = self.root / 'run'
        self.cfg = {
            'schema_version': 1,
            'goal': {'enabled': True, 'monk': False, 'objective': 'Find distinct toy mechanisms',
                     'success_criteria': 'Independent valid evidence and distinct mechanism',
                     'target_directions': 3, 'accepted_evidence': ['proxy-supported'], 'stop_conditions': []},
            'paths': {'workspace': str(self.root), 'environment': 'existing-stdlib',
                      'read_roots': [str(self.root)], 'write_roots': [str(self.root)], 'artifact_root': str(self.root)},
            'proxy': {'contract_path': str(self.contract), 'revision': 'P1'},
            'limits': {'total_elapsed_seconds': 1000, 'per_attempt_seconds': 20,
                       'total_cpu_seconds': 40, 'total_gpu_seconds': 0, 'cpu_cores': 2,
                       'ram_mib': 64, 'gpu_ids': [], 'vram_mib': 0,
                       'disk_bytes': guard.METADATA_RESERVATION + 1000, 'max_attempts': 8,
                       'max_retries': 1, 'concurrency': 2, 'max_agent_calls': 5, 'max_reviews': 2, 'max_stagnation': 2},
            'accounting': {'token_cap': 'unselected', 'cost_cap': 'unselected', 'tokens_metered': False,
                           'tokens_enforced': False, 'cost_metered': False, 'cost_enforced': False},
        }
        self.write_config()
        fields = {key: 'Explicit predeclared policy' for key in guard.CONTRACT_KEYS - {'files', 'data_manifests'}}
        fields['revision'] = 'P1'
        fields['data_manifests'] = ['synthetic-v1']
        body = '\n'.join(f'{k} = {value(v)}' for k, v in fields.items())
        body += f'\n[[files]]\npath = {value(str(self.source))}\nsha256 = {value(guard.sha(self.source.read_bytes()))}'
        self.contract.write_text('# Contract\n```toml\n' + body + '\n```\n')
        self.clock = patch.object(guard.time, 'time', return_value=100.0)
        self.clock.start()
        self.addCleanup(self.clock.stop)

    def write_config(self):
        self.config_path.write_text(markdown(self.cfg))

    def start(self):
        self.write_config()
        return guard.init(self.config_path, self.state)

    def plan(self, name='a', **changes):
        plan = {'id': name, 'kind': 'experiment', 'retry_of': None, 'light': True, 'cost_known': True,
                'duration_seconds': 10, 'cpu_cores': 1, 'ram_mib': 16, 'gpu_ids': [], 'vram_mib': 0,
                'bounds': {'cpu_seconds': 10, 'gpu_seconds': 0, 'disk_bytes': 100,
                           'agent_calls': 0, 'reviews': 0, 'tokens': 0, 'cost': 0}}
        plan.update(changes)
        return plan

    def usage(self, outcome='VALID', **changes):
        usage = {'outcome': outcome, 'actual': {key: None for key in guard.DIMENSIONS},
                 'duration_seconds': None, 'cpu_cores': None, 'ram_mib': None, 'gpu_ids': None,
                 'vram_mib': None, 'evidence': {'executor': 'qa-thread', 'code_revision': 'C1',
                                              'config_revision': 'G1', 'artifact_ids': ['small-output-id']}}
        usage.update(changes)
        return usage

    def test_actual_parser_accepts_monk_both_and_disabled_is_not_started(self):
        for monk in (False, True):
            self.cfg['goal']['monk'] = monk
            self.write_config()
            cfg, _ = guard.config_from(self.config_path)
            self.assertEqual(cfg['goal']['monk'], monk)
        self.cfg['goal']['enabled'] = False
        self.write_config()
        with self.assertRaises(guard.GuardError):
            guard.init(self.config_path, self.state)
        self.assertFalse(self.state.exists())

    def test_config_bad_fields_types_and_numeric_edges(self):
        original = copy.deepcopy(self.cfg)
        for section, key, bad in [('goal', 'objective', ''), ('goal', 'monk', 1),
                                  ('limits', 'cpu_cores', True), ('limits', 'ram_mib', -1),
                                  ('limits', 'max_attempts', 1.5), ('limits', 'cpu_cores', 10**300),
                                  ('limits', 'extra', 1), ('accounting', 'token_cap', False),
                                  ('proxy', 'revision', '')]:
            with self.subTest(section=section, key=key, bad=bad):
                self.cfg = copy.deepcopy(original)
                self.cfg[section][key] = bad
                self.write_config()
                with self.assertRaises(guard.GuardError):
                    guard.config_from(self.config_path)
        for invalid in ('nan', 'inf', '-inf'):
            text = markdown(original).replace('cpu_cores = 2', f'cpu_cores = {invalid}')
            self.config_path.write_text(text)
            with self.assertRaises(guard.GuardError):
                guard.config_from(self.config_path)

    def test_duplicate_blocks_keys_malformed_and_template_are_not_ready(self):
        raw = markdown(self.cfg)
        for text in (raw + '\n```toml\nx=1\n```\n', raw.replace('schema_version = 1', 'schema_version = 1\nschema_version = 1'),
                     raw.replace('[goal]', '[broken'), raw.replace('success_criteria = ', 'unexpected = ')):
            self.config_path.write_text(text)
            with self.subTest(text=text[:50]), self.assertRaises(guard.GuardError):
                guard.config_from(self.config_path)
        with self.assertRaises(guard.GuardError):
            guard.config_from(ROOT / 'payload/research/GOAL_CONFIG.md')

    def test_zero_metadata_budget_refuses_before_writes(self):
        self.cfg['limits']['disk_bytes'] = 0
        self.assertEqual(self.start()['status'], 'BUDGET_EXHAUSTED')
        self.assertFalse(self.state.exists())
        self.cfg['limits']['disk_bytes'] = guard.METADATA_RESERVATION - 1
        self.assertEqual(self.start()['status'], 'BUDGET_EXHAUSTED')
        self.assertFalse(self.state.exists())

    def test_init_snapshots_and_metadata_charge(self):
        result = self.start()
        self.assertEqual(result['execution_authorization'], 'NOT_GRANTED')
        self.assertEqual(result['enforcement'], 'NOT_PROVIDED')
        self.assertEqual((self.state / 'config.md').read_bytes(), self.config_path.read_bytes())
        self.assertEqual(guard.status(self.config_path, self.state)['charged']['disk_bytes'], guard.METADATA_RESERVATION)
        with self.assertRaises(guard.GuardError):
            self.start()

    def test_freeze_rejects_config_contract_source_or_snapshot_change(self):
        self.start()
        for path in (self.config_path, self.contract, self.source, self.state / 'config.md'):
            before = path.read_bytes()
            path.write_bytes(before + b'\n# changed\n')
            with self.subTest(path=path), self.assertRaises(guard.GuardError):
                guard.status(self.config_path, self.state)
            path.write_bytes(before)

    def test_pending_failed_retry_accounting_no_refunds(self):
        self.start()
        guard.reserve(self.config_path, self.state, self.plan())
        self.assertEqual(guard.status(self.config_path, self.state)['pending'], ['a'])
        with self.assertRaises(guard.GuardError):
            guard.reserve(self.config_path, self.state, self.plan())
        with self.assertRaises(guard.GuardError):
            guard.reserve(self.config_path, self.state, self.plan('b', retry_of='a'))
        usage = self.usage('INFRA_ERROR')
        usage['actual']['cpu_seconds'] = 1
        guard.finish(self.config_path, self.state, 'a', usage)
        self.assertEqual(guard.status(self.config_path, self.state)['charged']['cpu_seconds'], 10)
        self.assertEqual(guard.reserve(self.config_path, self.state, self.plan('b', retry_of='a'))['status'], 'READY_FOR_LIGHT_REVIEW')
        guard.finish(self.config_path, self.state, 'b', self.usage('OOM'))
        result = guard.reserve(self.config_path, self.state, self.plan('c', retry_of='b'))
        self.assertEqual(result['status'], 'BUDGET_EXHAUSTED')
        self.assertEqual(result['scope'], 'ATTEMPT')
        self.assertEqual(guard.status(self.config_path, self.state)['charged']['cpu_seconds'], 20)
        with self.assertRaises(guard.GuardError):
            guard.finish(self.config_path, self.state, 'b', usage)

    def test_concurrency_and_collective_memory_then_other_work(self):
        self.cfg['limits']['ram_mib'] = 24
        self.start()
        guard.reserve(self.config_path, self.state, self.plan())
        result = guard.reserve(self.config_path, self.state, self.plan('b'))
        self.assertEqual(result['status'], 'BUDGET_EXHAUSTED')
        self.assertEqual(result['scope'], 'ATTEMPT')
        self.assertEqual(guard.reserve(self.config_path, self.state, self.plan('c', ram_mib=8))['status'], 'READY_FOR_LIGHT_REVIEW')
        result = guard.reserve(self.config_path, self.state, self.plan('d', ram_mib=1))
        self.assertEqual(result['status'], 'BUDGET_EXHAUSTED')

    def test_cumulative_cpu_attempt_limit_and_elapsed(self):
        self.cfg['limits']['max_attempts'] = 1
        self.start()
        guard.reserve(self.config_path, self.state, self.plan())
        guard.finish(self.config_path, self.state, 'a', self.usage())
        self.assertEqual(guard.status(self.config_path, self.state)['remaining_attempts'], 0)
        self.assertEqual(guard.reserve(self.config_path, self.state, self.plan('b'))['scope'], 'GOAL')
        with patch.object(guard.time, 'time', return_value=1101):
            self.assertEqual(guard.status(self.config_path, self.state)['status'], 'BUDGET_EXHAUSTED')
        with patch.object(guard.time, 'time', return_value=99), self.assertRaises(guard.GuardError):
            guard.status(self.config_path, self.state)

    def test_cumulative_budget_blocks_only_plan_and_checks_remaining_duration(self):
        self.cfg['limits']['total_cpu_seconds'] = 15
        self.start()
        guard.reserve(self.config_path, self.state, self.plan())
        guard.finish(self.config_path, self.state, 'a', self.usage())
        result = guard.reserve(self.config_path, self.state, self.plan('b'))
        self.assertEqual(result['remaining']['cpu_seconds'], 5)
        self.assertEqual(result['scope'], 'ATTEMPT')
        small = self.plan('c', duration_seconds=5)
        small['bounds']['cpu_seconds'] = 5
        self.assertEqual(guard.reserve(self.config_path, self.state, small)['status'], 'READY_FOR_LIGHT_REVIEW')
        with patch.object(guard.time, 'time', return_value=1099):
            self.assertEqual(guard.reserve(self.config_path, self.state, self.plan('d'))['status'], 'BUDGET_EXHAUSTED')

    def test_overshoot_recorded_and_blocks_future_reservations(self):
        self.start()
        guard.reserve(self.config_path, self.state, self.plan())
        usage = self.usage('TIMEOUT')
        usage['actual']['cpu_seconds'] = 12
        usage['duration_seconds'] = 12
        result = guard.finish(self.config_path, self.state, 'a', usage)
        self.assertTrue(result['breach'])
        state = guard.status(self.config_path, self.state)
        self.assertEqual(state['charged']['cpu_seconds'], 12)
        self.assertEqual(guard.reserve(self.config_path, self.state, self.plan('b'))['scope'], 'GOAL')

    def test_unknown_heavy_and_unmetered_caps_do_not_reserve(self):
        self.start()
        before = (self.state / 'ledger.jsonl').read_bytes()
        for changes in ({'light': False}, {'cost_known': False}):
            self.assertEqual(guard.reserve(self.config_path, self.state, self.plan(**changes))['status'], 'NEEDS_USER_RUN')
        self.assertEqual((self.state / 'ledger.jsonl').read_bytes(), before)
        self.cfg['accounting']['token_cap'] = 100
        self.write_config()
        self.assertEqual(guard.init(self.config_path, self.root / 'second')['status'], 'NEEDS_USER_RUN')
        self.assertFalse((self.root / 'second').exists())

    def test_agent_and_review_without_fake_local_resources(self):
        self.start()
        plan = self.plan(kind='review', cpu_cores=0, ram_mib=0)
        plan['bounds'].update(cpu_seconds=0, agent_calls=1, reviews=1)
        result = guard.reserve(self.config_path, self.state, plan)
        self.assertEqual(result['status'], 'READY_FOR_LIGHT_REVIEW')
        self.assertEqual(result['automatic_execution'], 'NOT_DETERMINED')
        guard.finish(self.config_path, self.state, 'a', self.usage())
        status = guard.status(self.config_path, self.state)
        self.assertEqual(status['charged']['agent_calls'], 1)
        self.assertEqual(status['charged']['reviews'], 1)
        self.assertEqual(status['charged']['cpu_seconds'], 0)

    def test_plan_understates_worst_case_cpu_gpu(self):
        plan = self.plan(cpu_cores=2)
        with self.assertRaises(guard.GuardError):
            guard.check_plan(plan)
        plan = self.plan(gpu_ids=['GPU-0'], vram_mib=1)
        plan['bounds']['gpu_seconds'] = 1
        with self.assertRaises(guard.GuardError):
            guard.check_plan(plan)

    def test_gpu_allocation_and_simultaneous_device_memory(self):
        self.cfg['limits'].update(gpu_ids=['GPU-0'], vram_mib=20, total_gpu_seconds=40)
        self.start()
        plan = self.plan(gpu_ids=['GPU-0'], vram_mib=15)
        plan['bounds']['gpu_seconds'] = 10
        self.assertEqual(guard.reserve(self.config_path, self.state, plan)['status'], 'READY_FOR_LIGHT_REVIEW')
        other = copy.deepcopy(plan); other['id'] = 'b'
        self.assertEqual(guard.reserve(self.config_path, self.state, other)['status'], 'BUDGET_EXHAUSTED')
        other['gpu_ids'] = ['GPU-1']
        self.assertEqual(guard.reserve(self.config_path, self.state, other)['status'], 'BUDGET_EXHAUSTED')

    def test_stagnation_persists_and_meaningful_progress_resets_only_counter(self):
        self.start()
        guard.progress(self.config_path, self.state, False, 'review-1')
        self.assertEqual(guard.status(self.config_path, self.state)['stagnant_reviews'], 1)
        guard.progress(self.config_path, self.state, True, 'new-counterexample')
        self.assertEqual(guard.status(self.config_path, self.state)['stagnant_reviews'], 0)
        guard.progress(self.config_path, self.state, False, 'review-2')
        guard.progress(self.config_path, self.state, False, 'review-3')
        self.assertEqual(guard.status(self.config_path, self.state)['status'], 'BUDGET_EXHAUSTED')
        self.assertEqual(len((self.state / 'ledger.jsonl').read_text().splitlines()), 5)

    def test_corrupt_partial_duplicate_and_locked_state_fail_closed(self):
        self.start()
        ledger = self.state / 'ledger.jsonl'
        original = ledger.read_bytes()
        for invalid in (original[:-1], original + b'{', original.replace(b'INIT', b'FAKE'), original + original):
            ledger.write_bytes(invalid)
            with self.subTest(invalid=invalid[-10:]), self.assertRaises(guard.GuardError):
                guard.status(self.config_path, self.state)
            self.assertEqual(ledger.read_bytes(), invalid)
        ledger.write_bytes(original)
        (self.state / '.lock').write_text('interrupted owner')
        with self.assertRaises(guard.GuardError):
            guard.reserve(self.config_path, self.state, self.plan())
        self.assertTrue((self.state / '.lock').exists())

    def test_paths_symlinks_and_bounded_inputs(self):
        for path in ('relative', str(self.root / '..' / 'outside')):
            with self.assertRaises(guard.GuardError):
                guard.safe_path(path)
        with self.assertRaises(guard.GuardError):
            guard.init(self.config_path, self.root.parent / 'not-allowed')
        link = self.root / 'link'
        link.symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(guard.GuardError):
            guard.init(self.config_path, link / 'run')
        self.source.write_bytes(b'x' * (guard.MANIFEST_FILE_LIMIT + 1))
        with self.assertRaises(guard.GuardError):
            self.start()
        self.assertFalse(self.state.exists())

    def test_json_duplicate_nonfinite_and_invalid_usage_are_rejected(self):
        for data in (b'{"x":1,"x":2}', b'{"x":NaN}'):
            with self.assertRaises(guard.GuardError):
                guard.parse_json(data)
        usage = self.usage('REJECTED')
        with self.assertRaises(guard.GuardError):
            guard.check_usage(usage)
        usage = self.usage(); usage['actual']['tokens'] = True
        with self.assertRaises(guard.GuardError):
            guard.check_usage(usage)

    def test_zero_calls_token_cap_and_review_limit(self):
        self.cfg['limits']['max_agent_calls'] = 0
        self.cfg['accounting'].update(token_cap=0, tokens_metered=True, tokens_enforced=True)
        self.start()
        plan = self.plan(kind='agent', cpu_cores=0, ram_mib=0)
        plan['bounds'].update(cpu_seconds=0, agent_calls=1)
        self.assertEqual(guard.reserve(self.config_path, self.state, plan)['status'], 'BUDGET_EXHAUSTED')
        plan = self.plan()
        plan['bounds']['tokens'] = 1
        self.assertEqual(guard.reserve(self.config_path, self.state, plan)['status'], 'BUDGET_EXHAUSTED')
        plan['bounds']['tokens'] = 0
        self.assertEqual(guard.reserve(self.config_path, self.state, plan)['status'], 'READY_FOR_LIGHT_REVIEW')

    def test_ledger_symlink_and_size_limit_do_not_touch_external_target(self):
        self.start()
        ledger = self.state / 'ledger.jsonl'
        external = self.root / 'external.txt'
        external.write_text('preserve user result')
        ledger.unlink()
        ledger.symlink_to(external)
        with self.assertRaises(guard.GuardError):
            guard.reserve(self.config_path, self.state, self.plan())
        self.assertEqual(external.read_text(), 'preserve user result')
        ledger.unlink()
        ledger.write_bytes(b'x' * (guard.LEDGER_LIMIT + 1))
        with self.assertRaises(guard.GuardError):
            guard.status(self.config_path, self.state)

    def test_reported_peak_breach_and_unknown_usage_remain_conservative(self):
        self.start()
        guard.reserve(self.config_path, self.state, self.plan())
        usage = self.usage(ram_mib=17)
        self.assertTrue(guard.finish(self.config_path, self.state, 'a', usage)['breach'])
        status = guard.status(self.config_path, self.state)
        self.assertEqual(status['charged']['cpu_seconds'], 10)
        self.assertEqual(status['status'], 'BUDGET_EXHAUSTED')
        result = guard.reserve(self.config_path, self.state, self.plan('heavy-after-breach', light=False))
        self.assertEqual(result['status'], 'BUDGET_EXHAUSTED')
        self.assertIn('breach', result['reason'])

    def test_global_elapsed_stop_precedes_heavy_unknown_and_finish_reports_stop(self):
        self.start()
        guard.reserve(self.config_path, self.state, self.plan())
        with patch.object(guard.time, 'time', return_value=1101):
            for changes in ({'light': False}, {'cost_known': False}):
                result = guard.reserve(self.config_path, self.state, self.plan('b', **changes))
                self.assertEqual(result['scope'], 'GOAL')
                self.assertEqual(result['status'], 'BUDGET_EXHAUSTED')
                self.assertIn('elapsed', result['reason'])
            result = guard.finish(self.config_path, self.state, 'a', self.usage())
            self.assertEqual(result['status'], 'BUDGET_EXHAUSTED')
            self.assertEqual(result['scope'], 'GOAL')

    def test_cli_validates_without_importing_evaluator_or_executing_commands(self):
        output = io.StringIO()
        before = set(self.root.iterdir())
        with patch.object(guard.sys, 'argv', ['goal_guard', 'validate', '--config', str(self.config_path)]), redirect_stdout(output):
            self.assertEqual(guard.main(), 0)
        result = json.loads(output.getvalue())
        self.assertEqual(result['scientific_decision'], 'NOT_COMPUTED')
        self.assertEqual(set(self.root.iterdir()), before)
        self.assertIn('MUST NEVER IMPORT', self.source.read_text())


if __name__ == '__main__':
    unittest.main()
