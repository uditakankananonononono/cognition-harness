import hashlib
from pathlib import Path
import unittest
from study_runner import run, METHODS, interpret

POOL = Path(__file__).with_name('public-pool.json')
PIN = hashlib.sha256(POOL.read_bytes()).hexdigest()

class RunnerTests(unittest.TestCase):
    def test_each_method_selects_one_without_scoring(self):
        for method in METHODS:
            r = run(method, [[0, 0]], POOL, PIN)
            self.assertEqual(r['status'], 'selected')
            self.assertEqual(r['correctness'], 'not_scored')
            self.assertIsNotNone(r['finalist'])
    def test_identical_actual_scalar_charges(self):
        rs = [run(m, [[0, 0], [1, 1]], POOL, PIN) for m in METHODS]
        for r in rs:
            self.assertEqual(r['charged']['dev_scalar'], 16)
            self.assertEqual(r['charged']['probe_scalar'], 64)
            self.assertEqual(r['charged']['pool_scan'], 64)
            self.assertLessEqual(r['charged']['ledger_bytes'], 32768)
    def test_cap_exits_no_finalist(self):
        for m in METHODS:
            r = run(m, [[0, 0]], POOL, PIN, execution_cap=10)
            self.assertEqual(r['status'], 'execution_cap_exhausted')
            self.assertIsNone(r['finalist'])
            self.assertEqual(r['charged']['dev_scalar']+r['charged']['probe_scalar'], 10)
            r = run(m, [[0, 0]], POOL, PIN, byte_cap=400)
            self.assertEqual(r['status'], 'byte_budget_exhausted')
            self.assertIsNone(r['finalist'])
    def test_pool_pin_refusal(self):
        with self.assertRaises(ValueError): run('first', [[0, 0]], POOL, '0'*64)
    def test_invalid_types(self):
        for dev in ([[True, 0]], [[0, False]], [[33, 0]], []):
            with self.assertRaises(ValueError): run('first', dev, POOL, PIN)
        with self.assertRaises(ValueError): run('other', [[0, 0]], POOL, PIN)
        with self.assertRaises(ValueError): interpret(('identity', 0), True)
    def test_determinism(self):
        self.assertEqual(run('disagreement', [[0, 0]], POOL, PIN), run('disagreement', [[0, 0]], POOL, PIN))
    def test_diversity_can_choose_worse_candidate(self):
        # Known abs fixture: development 0 and 1 does not separate abs from
        # identity. Disagreement preserves identity, which wins complexity
        # ranking but is wrong on the developer-known negative input fixture.
        first = run('first', [[0, 0], [1, 1]], POOL, PIN)
        diverse = run('disagreement', [[0, 0], [1, 1]], POOL, PIN)
        self.assertEqual(interpret(first['finalist']['expression'], -2), 2)
        self.assertEqual(interpret(diverse['finalist']['expression'], -2), -2)
    def test_restoration_is_logged(self):
        r = run('disagreement', [[0, 0]], POOL, PIN)
        self.assertIn('restore', [e['kind'] for e in r['ledger']['events']])

if __name__ == '__main__': unittest.main(verbosity=2)
