"""v10 controls: freeze integrity, answer-key check, plateau property (no single
edit improves dev), distance-metric sanity, determinism. Run: python3 tests.py
"""
import itertools, json, sys, unittest
from pathlib import Path
from isolation import R, sha, score, json_equal
from judge import verify, promotion
from fitness import distance, fitness
import importlib.util
_spec = importlib.util.spec_from_file_location('v9mutations', Path(__file__).resolve().parent.parent / 'v9' / 'mutations.py')
mutations = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mutations)

PIN = (R/'receipts'/'frozen-pin.txt').read_text().strip()
BASELINE = (R/'candidates'/'baseline.py').read_text()

REF = {
    'scale_offset': lambda x: x * 2 + 1,
    'in_open_interval': lambda v: v[1] < v[0] < v[2],
    'sign3': lambda x: 1 if x > 0 else (-1 if x < 0 else 0),
    'midpoint': lambda p: (p[0] + p[1]) // 2,
    'evens_list': lambda n: [x for x in n if x % 2 == 0],
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
        for c in cases:
            self.assertTrue(json_equal(REF[c['task']](json.loads(json.dumps(c['input']))), c['expected']), c['id'])
    def test_dev_literals_match_reference(self):
        for c in json.loads((R/'frozen'/'dev.json').read_bytes()):
            self.assertTrue(json_equal(REF[c['task']](json.loads(json.dumps(c['input']))), c['expected']), c['id'])
    def test_dev_inputs_disjoint_from_eval(self):
        # sign3 exception: x=0 is the ONLY discriminating input of this coupled bug,
        # so it must appear in dev (guidance) and eval (verification). Expected
        # outputs stay hidden from proposers; only judge.py reads eval expectations.
        eval_inputs = {(c['task'], json.dumps(c['input'], sort_keys=True)) for c in json.loads((R/'frozen'/'eval.json').read_bytes())}
        for c in json.loads((R/'frozen'/'dev.json').read_bytes()):
            if c['task'] == 'sign3':
                continue
            self.assertNotIn((c['task'], json.dumps(c['input'], sort_keys=True)), eval_inputs, c['id'])

class Plateau(unittest.TestCase):
    def test_no_single_edit_improves_dev(self):
        dev = json.loads((R/'frozen'/'dev.json').read_bytes())
        base = score(BASELINE.encode(), dev)
        self.assertEqual(base['passed'], 1, base.get('cases'))  # only sign3 x=7 passes
        children = mutations.expand(BASELINE)
        self.assertGreater(len(children), 50)
        for desc, child in children:
            rep = score(child.encode(), dev)
            p = rep.get('passed', -1)
            self.assertLessEqual(p, 1, f"single edit improves dev: {desc}")
    def test_each_fix_reachable(self):
        depth1 = mutations.expand(BASELINE)
        needles2 = {'scale_offset': 'x * 2 + 1', 'midpoint': '(lo + hi) // 2', 'evens_list': 'n % 2 == 0'}
        sign3_ok = interval_step = False
        interval_children = []
        for desc, child in depth1:
            if 'lo < x or x <= hi' in child:
                interval_children.append(child)
            for _, grand in mutations.expand(child):
                for k, needle in needles2.items():
                    if needle and needle in grand:
                        needles2[k] = None
                if 'if x > 0:' in grand and 'if x < 0:' in grand:
                    sign3_ok = True
        self.assertEqual({k: v for k, v in needles2.items() if v is not None}, {})
        self.assertTrue(sign3_ok, 'sign3 fix unreachable in 2 edits')
        # in_open_interval is a documented 3-edit plateau: verify the 3-edit path.
        self.assertTrue(interval_children, 'interval step-1 missing')
        step2 = [g for c in interval_children for _, g in mutations.expand(c) if 'lo < x and x <= hi' in g]
        self.assertTrue(step2, 'interval step-2 missing')
        step3 = [g for c in step2 for _, g in mutations.expand(c) if 'lo < x and x < hi' in g]
        self.assertTrue(step3, 'interval step-3 missing')

class Distance(unittest.TestCase):
    def test_zero_when_equal(self):
        self.assertEqual(distance([1, [2, 'a']], [1, [2, 'a']]), 0)
    def test_numeric(self):
        self.assertEqual(distance(2, 5), 3)
        self.assertEqual(distance(-1, 1), 2)
    def test_none_and_type(self):
        self.assertEqual(distance(None, 5), 10)
        self.assertEqual(distance(True, 1), 10)
    def test_list(self):
        self.assertEqual(distance([1, 2], [1]), 10)
        self.assertEqual(distance([1, 9], [1, 2]), 7)
    def test_fitness_invalid_worst(self):
        self.assertEqual(fitness({'valid': False}), (-1, 10 ** 9))

class MenuSanity(unittest.TestCase):
    def test_v9_menu_operators_absent(self):
        for _, old, _ in [('a', "text.lower().split(' ')", ''), ('b', 'sorted(set(items))', ''), ('c', 'start < out[-1][1]', '')]:
            self.assertNotIn(old, BASELINE)

if __name__ == '__main__':
    unittest.main(verbosity=1)
