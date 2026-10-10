"""Repair probes (2026-10-10 code review): each test reproduces one reviewer
scenario against the fixed code. Run: python3 tests_repairs.py
"""
import json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'v10'))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'v9'))
import proposer2, proposer3, run_one_suite

BASE = 'def f(x):\n    return x + 1\n'

def rep(passed, failing_actual=None, failing_expected=None, total=10):
    cases = [{'id': f'c{i}', 'task': 'f', 'expected': i, 'actual': i, 'passed': True} for i in range(passed)]
    for i in range(passed, total):
        cases.append({'id': f'c{i}', 'task': 'f', 'expected': failing_expected if failing_expected is not None else i,
                      'actual': failing_actual, 'error': None, 'passed': False})
    return {'valid': True, 'passed': passed, 'total': total, 'per_task': {'f': passed}, 'cases': cases,
            'source_sha256': 'x'}

def mock_score(mapping):
    def score(src, cases):
        return mapping.get(src.decode(), rep(0))
    return score

class Probe1_DirectionV9V10(unittest.TestCase):
    """Reviewer: baseline actual 0/expected 10 (dist 10) vs child 9/10 (dist 1)
    at equal pass count - old code kept baseline; fixed code picks the child."""
    def test_child_with_smaller_distance_wins(self):
        mapping = {BASE: rep(9, failing_actual=0, failing_expected=10)}
        def score(src, cases):
            return mapping.get(src.decode(), rep(9, failing_actual=9, failing_expected=10))
        cand, hist = proposer2.beam(BASE, [{'id': 'd', 'task': 'f', 'input': 1, 'expected': 1}],
                                    score, use_distance=True, width=4, depth=1, exec_cap=200)
        self.assertNotEqual(cand, BASE)
        self.assertEqual(hist['best_dev_passed'], 9)
        self.assertEqual(hist['best_dev_distance'], 1)

class Probe2_SuiteIsolation(unittest.TestCase):
    """Reviewer: v9 judge resolved v10's isolation.R. Fixed loader must bind
    each suite's own isolation, and loading the second suite must not disturb
    the first suite's already-loaded judge."""
    def test_suites_isolated(self):
        d9, iso9, judge9, _ = run_one_suite.load_suite('v9')
        self.assertEqual(iso9.R, d9)
        judge9.verify((d9/'receipts'/'frozen-pin.txt').read_text().strip())
        d10, iso10, judge10, _ = run_one_suite.load_suite('v10')
        self.assertEqual(iso10.R, d10)
        judge10.verify((d10/'receipts'/'frozen-pin.txt').read_text().strip())
        self.assertNotEqual(iso9.R, iso10.R)
        judge9.verify((d9/'receipts'/'frozen-pin.txt').read_text().strip())  # still valid after v10 load

class Probe3_GradedBaselineInit(unittest.TestCase):
    """Reviewer: v11 initialized baseline distance 0, so an equal-passed
    higher-distance child could displace a better baseline."""
    def test_higher_distance_child_rejected(self):
        def score(src, cases):
            return rep(5, failing_actual=0, failing_expected=40, total=6) if src.decode() == BASE else rep(5, failing_actual=0, failing_expected=50, total=6)
        cand, hist = proposer3.beam(BASE, [], score, use_distance=True, width=4, depth=1, exec_cap=200)
        self.assertEqual(cand, BASE)
        self.assertEqual(hist['best_dev_distance'], 40)
    def test_lower_distance_child_accepted(self):
        def score(src, cases):
            return rep(5, failing_actual=0, failing_expected=40, total=6) if src.decode() == BASE else rep(5, failing_actual=0, failing_expected=30, total=6)
        cand, hist = proposer3.beam(BASE, [], score, use_distance=True, width=4, depth=1, exec_cap=200)
        self.assertNotEqual(cand, BASE)
        self.assertEqual(hist['best_dev_distance'], 30)

class Probe4_RepresentativeTieBreak(unittest.TestCase):
    """Reviewer: behavior representative used reversed-sha descending. Fixed:
    equal fitness + equal behavior keeps the LOWEST sha, and that representative
    is the one expanded at the next depth."""
    def test_lowest_sha_representative_expanded(self):
        identical = rep(5, failing_actual=1, failing_expected=2)
        def score(src, cases):
            return rep(5, failing_actual=9, failing_expected=9) if src.decode() == BASE else identical
        import hashlib
        from mutations import expand
        children = [c for _, c in expand(BASE)]
        expected_parent = min(hashlib.sha256(c.encode()).hexdigest() for c in children)[:12]
        cand, hist = proposer3.beam(BASE, [], score, use_distance=False, width=1, depth=2, exec_cap=400)
        depth1_parents = {t['parent'] for t in hist['trials'] if t['depth'] == 1}
        self.assertTrue(hist['trials'])
        self.assertEqual(depth1_parents, {expected_parent})

if __name__ == '__main__':
    unittest.main(verbosity=1)
