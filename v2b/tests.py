import json, tempfile, unittest
from pathlib import Path
from isolation import R, execute, score, json_equal
from judge import promotion, verify
class Controls(unittest.TestCase):
    def test_recursive_exact_json_types(self):
        for a, e in [(True,1),(False,0),([True],[1]),([[False]],[[0]]),({'x':[True]},{'x':[1]}),([1.0],[1]),({'x':None},{'x':False})]:
            with self.subTest(actual=a,expected=e):
                self.assertFalse(json_equal(a,e))
                self.assertFalse(json_equal(e,a))
        self.assertTrue(json_equal({'x':[1,True,None,1.0]}, {'x':[1,True,None,1.0]}))
    def test_candidate_nested_bool_refused(self):
        for code,expected in [(b'def unique(x): return [True]\n',[1]), (b'def unique(x): return [[False]]\n',[[0]]), (b'def unique(x): return {"x":[True]}\n',{'x':[1]})]:
            r=score(code,[{'id':'probe','task':'unique','input':[],'expected':expected}])
            self.assertTrue(r['valid'])
            self.assertEqual(r['passed'],0)
            self.assertFalse(r['cases'][0]['passed'])
    def test_protocol_pin_unchanged(self):
        verify('d09124d5433181236f014411e6633d3e526e2e6c15c1216983aadf1cf3d53daf')
    def test_grammar_sizes(self):
        from agent import grammar
        self.assertEqual([len(grammar(t)) for t in ('canonical','unique','merge')],[12,5,8])
    def test_dev_eval_inputs_disjoint(self):
        dev=json.loads((R/'frozen'/'dev.json').read_text())
        ev=json.loads((R/'frozen'/'eval.json').read_text())
        ds={(c['task'],json.dumps(c['input'],sort_keys=True)) for c in dev}
        overlap=[c['id'] for c in ev if (c['task'],json.dumps(c['input'],sort_keys=True)) in ds]
        self.assertEqual(overlap,[])
    def test_hash_refusal(self):
        with self.assertRaises(ValueError): verify('0'*64)
    def test_changed_suite_refused(self):
        p=R/'frozen'/'dev.json'; before=p.read_bytes()
        try:
            p.write_bytes(before+b' ')
            with self.assertRaises(ValueError): verify((R/'receipts'/'frozen-pin.txt').read_text().strip())
        finally: p.write_bytes(before)
    def test_timeout(self):
        r=execute(b'def canonical(x):\n while True: pass\n', [{'id':'x','task':'canonical','input':'x'}])
        self.assertFalse(r['valid'])
    def test_syntax_error(self):
        self.assertFalse(execute(b'this is not Python!',[])['valid'])
    def test_host_canary(self):
        with tempfile.NamedTemporaryFile() as canary:
            code=f'def canonical(x):\n return open({canary.name!r}).read()\n'.encode()
            r=execute(code,[{'id':'x','task':'canonical','input':'x'}])
            self.assertTrue(r['valid']); self.assertEqual(r['values'][0]['error'],'FileNotFoundError')
    def test_network_namespace(self):
        code=b'import socket\ndef canonical(x):\n return socket.create_connection(("1.1.1.1",80),timeout=.2).send(b"x")\n'
        r=execute(code,[{'id':'x','task':'canonical','input':'x'}])
        self.assertTrue(r['valid']); self.assertEqual(r['values'][0]['error'],'OSError')
    def test_memory_cap(self):
        r=execute(b'def canonical(x):\n return "a"*(1024*1024*256)\n',[{'id':'x','task':'canonical','input':'x'}])
        self.assertTrue(r['valid']); self.assertEqual(r['values'][0]['error'],'MemoryError')
    def test_equal_rejected(self):
        report={'valid':True,'passed':2,'per_task':{'a':2}}
        self.assertFalse(promotion(report,report))
    def test_invalid_rejected(self):
        self.assertFalse(promotion({'valid':False},{'valid':False}))
    def test_regression_rejected_despite_total_gain(self):
        b={'valid':True,'passed':24,'per_task':{'canonical':5,'unique':10,'merge':9}}
        c={'valid':True,'passed':33,'per_task':{'canonical':16,'unique':1,'merge':16}}
        self.assertFalse(promotion(b,c))
    def test_measurement_receipt(self):
        r=json.loads((R/'receipts'/'measurement.json').read_text())
        self.assertEqual(r['baseline']['total'],360)
        self.assertGreater(r['candidates'][0]['report']['passed'],r['baseline']['passed'])
        self.assertTrue(r['candidates'][0]['measurement_gate'])
        self.assertFalse(r['candidates'][1]['measurement_gate'])
    def test_baseline_bytes_unchanged(self):
        r=json.loads((R/'receipts'/'measurement.json').read_text())
        from isolation import sha
        self.assertEqual(sha((R/'candidates'/'baseline.py').read_bytes()),r['baseline']['source_sha256'])
if __name__=='__main__': unittest.main(verbosity=2)
