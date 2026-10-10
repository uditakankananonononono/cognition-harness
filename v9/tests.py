"""v9 controls: freeze integrity, reference-implementation answer-key check,
gate semantics, comparator strictness, mutation determinism/reachability,
menu control behavior, sandbox refusal. Run: python3 tests.py
"""
import itertools, json, unittest
from pathlib import Path
from isolation import R, sha, score, json_equal
from judge import verify, promotion
import mutations, proposer

PIN = (R/'receipts'/'frozen-pin.txt').read_text().strip()
BASELINE = (R/'candidates'/'baseline.py').read_text()

REF = {
    'clamp_range': lambda v: min(max(v[0], v[1]), v[2]),
    'second_largest': lambda n: sorted(set(n))[-2],
    'count_even': lambda n: sum(1 for x in n if x % 2 == 0),
    'running_max': lambda n: list(itertools.accumulate(n, max)),
    'first_above': lambda p: next((x for x in p[0] if x > p[1]), None),
}

class Freeze(unittest.TestCase):
    def test_pin_verifies(self):
        verify(PIN)
    def test_tamper_refused(self):
        with self.assertRaises(ValueError):
            verify('0' * 64)
    def test_eval_literals_match_reference(self):
        cases = json.loads((R/'frozen'/'eval.json').read_bytes())
        self.assertEqual(len(cases), 80)
        self.assertEqual(len({c['id'] for c in cases}), 80)
        for c in cases:
            self.assertTrue(json_equal(REF[c['task']](json.loads(json.dumps(c['input']))), c['expected']), c['id'])
    def test_dev_literals_match_reference(self):
        dev = json.loads((R/'frozen'/'dev.json').read_bytes())
        self.assertEqual(len(dev), 10)
        for c in dev:
            self.assertTrue(json_equal(REF[c['task']](json.loads(json.dumps(c['input']))), c['expected']), c['id'])
    def test_dev_inputs_disjoint_from_eval(self):
        eval_inputs = {(c['task'], json.dumps(c['input'], sort_keys=True)) for c in json.loads((R/'frozen'/'eval.json').read_bytes())}
        for c in json.loads((R/'frozen'/'dev.json').read_bytes()):
            self.assertNotIn((c['task'], json.dumps(c['input'], sort_keys=True)), eval_inputs, c['id'])

class Gate(unittest.TestCase):
    def _rep(self, valid, passed, per):
        return {'valid': valid, 'passed': passed, 'per_task': per}
    def test_equal_rejected(self):
        self.assertFalse(promotion(self._rep(True, 40, {'a': 8}), self._rep(True, 40, {'a': 8})))
    def test_regression_rejected(self):
        self.assertFalse(promotion(self._rep(True, 40, {'a': 8, 'b': 8}), self._rep(True, 60, {'a': 7, 'b': 16})))
    def test_invalid_rejected(self):
        self.assertFalse(promotion(self._rep(False, 0, {}), self._rep(True, 80, {'a': 16})))
    def test_strict_gain_no_regression_accepted(self):
        self.assertTrue(promotion(self._rep(True, 40, {'a': 8, 'b': 8}), self._rep(True, 41, {'a': 9, 'b': 8})))

class Comparator(unittest.TestCase):
    def test_bool_is_not_int(self):
        self.assertFalse(json_equal(True, 1))
        self.assertFalse(json_equal([True], [1]))
    def test_nested_exact(self):
        self.assertTrue(json_equal({'a': [1, {'b': None}]}, {'a': [1, {'b': None}]}))
        self.assertFalse(json_equal({'a': [1]}, {'a': [1.0]}))

class Mutations(unittest.TestCase):
    def test_determinism(self):
        a = [d for d, _ in mutations.expand(BASELINE)]
        b = [d for d, _ in mutations.expand(BASELINE)]
        self.assertEqual(a, b)
    def test_depth1_reachability(self):
        texts = [c for _, c in mutations.expand(BASELINE)]
        for needle in ('min(max(x, lo), hi)', 'sorted(set(nums))[-2]', 'n % 2 == 0',
                       'm = max(m, n)', 'if v > limit:', 'return v'):
            self.assertTrue(any(needle in t for t in texts), needle)
    def test_depth2_first_above_full_fix(self):
        first = [c for _, c in mutations.expand(BASELINE) if 'return v' in c]
        self.assertTrue(first)
        second = [c for _, c in mutations.expand(first[0])]
        self.assertTrue(any('if v > limit:' in c and 'return v' in c for c in second))

class MenuControl(unittest.TestCase):
    def test_no_operator_applies(self):
        dev = json.loads((R/'frozen'/'dev.json').read_bytes())
        cand, hist = proposer.menu(BASELINE, dev)
        self.assertEqual(cand, BASELINE)
        self.assertEqual(sum(len(r['trials']) for r in hist['rounds']), 0)

class Sandbox(unittest.TestCase):
    def test_syntax_error_invalid(self):
        rep = score(b'def broken(:\n', json.loads((R/'frozen'/'dev.json').read_bytes()))
        self.assertFalse(rep['valid'])
    def test_baseline_dev_score_is_zero(self):
        rep = score(BASELINE.encode(), json.loads((R/'frozen'/'dev.json').read_bytes()))
        self.assertEqual(rep['passed'], 0, rep.get('cases'))

if __name__ == '__main__':
    unittest.main(verbosity=1)
