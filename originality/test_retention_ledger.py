import copy
import json
import unittest
from retention_ledger import create, transition, validate, digest, encode, restored_source

class LedgerTests(unittest.TestCase):
    def state(self, limit=10000): return create('a' * 64, limit)
    def test_restore_exact_unicode_source_and_lineage(self):
        source = "def f(x): return 'é' + str(x)\n"
        key = digest(source)
        initial = self.state()
        retained = transition(initial, 'retain', source, 'grammar candidate 0')
        pruned = transition(retained, 'prune', key, 'development-vector collision 0')
        restored = transition(pruned, 'restore', key, 'probe-pool v1 index 2 splits bucket 0')
        self.assertEqual(restored_source(restored, key), source)
        self.assertEqual([e['kind'] for e in restored['events']], ['retain', 'prune', 'restore'])
        self.assertEqual(initial, self.state())
        self.assertEqual(pruned['sources'][key]['status'], 'pruned')
        self.assertEqual(validate(json.loads(encode(restored))), restored)
    def test_metadata_and_sources_count_toward_limit(self):
        base = self.state()
        one = transition(base, 'retain', 'return 0', 'fixture')
        exact = len(encode(one))
        # The encoded budget value affects encoded length. Fix it to a same-width value.
        one['max_bytes'] = exact
        exact = len(encode(one))
        one['max_bytes'] = exact
        self.assertEqual(len(encode(one)), exact)
        validate(one)
        before = copy.deepcopy(one)
        with self.assertRaisesRegex(ValueError, 'byte_budget_exhausted'):
            transition(one, 'prune', digest('return 0'), 'collision')
        self.assertEqual(one, before)
    def test_oversized_source_rejected_atomically(self):
        s = self.state(1000)
        with self.assertRaises(ValueError): transition(s, 'retain', 'x' * 2000, 'candidate')
        self.assertEqual(s, self.state(1000))
    def test_source_tamper(self):
        s = transition(self.state(), 'retain', 'source', 'candidate')
        s['sources'][digest('source')]['source'] = 'changed'
        with self.assertRaises(ValueError): validate(s)
    def test_event_tamper(self):
        s = transition(self.state(), 'retain', 'source', 'candidate')
        for field, value in [('seq', 3), ('kind', 'restore'), ('source_sha256', 'b' * 64)]:
            bad = copy.deepcopy(s); bad['events'][0][field] = value
            with self.assertRaises(ValueError): validate(bad)
    def test_status_tamper(self):
        s = transition(self.state(), 'retain', 'source', 'candidate')
        s['sources'][digest('source')]['status'] = 'restored'
        with self.assertRaises(ValueError): validate(s)
    def test_restore_requires_prune(self):
        s = transition(self.state(), 'retain', 'source', 'candidate')
        with self.assertRaises(ValueError): transition(s, 'restore', digest('source'), 'probe')
        with self.assertRaises(ValueError): restored_source(s, digest('source'))
    def test_duplicate_and_unknown_refusal(self):
        s = transition(self.state(), 'retain', 'source', 'candidate')
        with self.assertRaises(ValueError): transition(s, 'retain', 'source', 'candidate again')
        with self.assertRaises(ValueError): transition(s, 'prune', 'b' * 64, 'collision')
    def test_bad_limits_protocol_reason(self):
        for limit in (True, 0, 1000001):
            with self.assertRaises(ValueError): self.state(limit)
        with self.assertRaises(ValueError): create('z' * 64, 10000)
        with self.assertRaises(ValueError): transition(self.state(), 'retain', 's', 'é' * 257)
    def test_repeated_prune_restore_has_explicit_lineage(self):
        s = transition(self.state(), 'retain', 'source', 'candidate'); key = digest('source')
        for _ in range(2):
            s = transition(s, 'prune', key, 'collision')
            s = transition(s, 'restore', key, 'split')
        self.assertEqual(len(validate(s)['events']), 5)
    def test_source_cap(self):
        s = self.state(1_000_000)
        for i in range(256): s = transition(s, 'retain', str(i), 'candidate')
        with self.assertRaisesRegex(ValueError, 'source_limit'): transition(s, 'retain', '257', 'candidate')
    def test_unlogged_source_rejected(self):
        s = self.state(); s['sources'][digest('source')] = {'source': 'source', 'status': 'available'}
        with self.assertRaises(ValueError): validate(s)

if __name__ == '__main__': unittest.main(verbosity=2)
