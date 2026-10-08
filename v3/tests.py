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
        for code,expected in [(b'def first_index(x): return [True]\n',[1]), (b'def first_index(x): return [[False]]\n',[[0]]), (b'def first_index(x): return {"x":[True]}\n',{'x':[1]})]:
            r=score(code,[{'id':'probe','task':'first_index','input':[],'expected':expected}])
            self.assertTrue(r['valid'])
            self.assertEqual(r['passed'],0)
            self.assertFalse(r['cases'][0]['passed'])
    def test_protocol_pin_unchanged(self):
        verify('21908b6fcdb8e5ef2d3153c1f0bd5319741479634e3be70a7118df6b7a9dc05d')
    def test_mutates_one_operator_site(self):
        from agent import proposals
        variants=[s for e,s in proposals('def arithmetic(x):\n return x + 1 + 2\n') if e['new']=='Sub']
        self.assertEqual(len(variants),2)
        self.assertTrue(all(s.count(' - ')==1 and s.count(' + ')==1 for s in variants))
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
        r=execute(b'def arithmetic(x):\n while True: pass\n', [{'id':'x','task':'arithmetic','input':'x'}])
        self.assertFalse(r['valid'])
    def test_syntax_error(self):
        self.assertFalse(execute(b'this is not Python!',[])['valid'])
    def test_host_canary(self):
        with tempfile.NamedTemporaryFile() as canary:
            code=f'def arithmetic(x):\n return open({canary.name!r}).read()\n'.encode()
            r=execute(code,[{'id':'x','task':'arithmetic','input':'x'}])
            self.assertTrue(r['valid']); self.assertEqual(r['values'][0]['error'],'FileNotFoundError')
    def test_network_namespace(self):
        code=b'import socket\ndef arithmetic(x):\n return socket.create_connection(("1.1.1.1",80),timeout=.2).send(b"x")\n'
        r=execute(code,[{'id':'x','task':'arithmetic','input':'x'}])
        self.assertTrue(r['valid']); self.assertEqual(r['values'][0]['error'],'OSError')
    def test_memory_cap(self):
        r=execute(b'def arithmetic(x):\n return "a"*(1024*1024*256)\n',[{'id':'x','task':'arithmetic','input':'x'}])
        self.assertTrue(r['valid']); self.assertEqual(r['values'][0]['error'],'MemoryError')
    def test_equal_rejected(self):
        report={'valid':True,'passed':2,'per_task':{'a':2}}
        self.assertFalse(promotion(report,report))
    def test_invalid_rejected(self):
        self.assertFalse(promotion({'valid':False},{'valid':False}))
    def test_regression_rejected_despite_total_gain(self):
        b={'valid':True,'passed':24,'per_task':{'arithmetic':5,'first_index':10,'merge':9}}
        c={'valid':True,'passed':33,'per_task':{'arithmetic':16,'first_index':1,'merge':16}}
        self.assertFalse(promotion(b,c))
    def test_measurement_receipt(self):
        r=json.loads((R/'receipts'/'measurement.json').read_text())
        self.assertEqual(r['baseline']['total'],240)
        self.assertGreater(r['candidates'][0]['report']['passed'],r['baseline']['passed'])
        self.assertTrue(r['candidates'][0]['measurement_gate'])
        self.assertFalse(r['candidates'][1]['measurement_gate'])
    def test_baseline_bytes_unchanged(self):
        r=json.loads((R/'receipts'/'measurement.json').read_text())
        from isolation import sha
        self.assertEqual(sha((R/'candidates'/'baseline.py').read_bytes()),r['baseline']['source_sha256'])
if __name__=='__main__': unittest.main(verbosity=2)
