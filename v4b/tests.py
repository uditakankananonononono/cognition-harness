import copy,json,unittest
from isolation import R,execute,json_equal
from judge import verify,promotion,preservation
class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r=json.loads((R/'receipts'/'measurement.json').read_text())
        cls.b=cls.r['baseline'];cls.c=cls.r['candidates'][0]['report']
    def test_pin(self):verify('f13f43ed36151052b253b2776a2088b0dcabbb246ea8a6c00e8da8d463b45892')
    def test_bad_pin(self):
        with self.assertRaises(ValueError):verify('0'*64)
    def test_source_tamper_refused(self):
        p=R/'candidates'/'candidate.py';old=p.read_bytes()
        try:
            p.write_bytes(old+b' ')
            with self.assertRaises(ValueError):verify(self.r['manifest_pin'])
        finally:p.write_bytes(old)
    def test_selected(self):self.assertTrue(preservation(self.b,self.c))
    def test_always_minus_one_preserves(self):
        c=self.r['candidates'][1];self.assertTrue(c['preservation_gate']);self.assertEqual(c['baseline_pass_losses'],[])
    def test_counterexample(self):
        c=self.r['candidates'][3]
        self.assertEqual(c['report']['passed'],238);self.assertTrue(c['aggregate_gate']);self.assertFalse(c['preservation_gate']);self.assertEqual(len(c['baseline_pass_losses']),2)
    def test_invalid_rejected(self):self.assertFalse(preservation(self.b,{'valid':False}))
    def test_equal_rejected(self):self.assertFalse(preservation(self.b,self.b))
    def test_truncated_rejected(self):
        c=copy.deepcopy(self.c);c['cases'].pop();self.assertFalse(preservation(self.b,c))
    def test_reordered_rejected(self):
        c=copy.deepcopy(self.c);c['cases'][0],c['cases'][1]=c['cases'][1],c['cases'][0];self.assertFalse(preservation(self.b,c))
    def test_wrong_task_rejected(self):
        c=copy.deepcopy(self.c);c['cases'][0]['task']='other';self.assertFalse(preservation(self.b,c))
    def test_wrong_expected_rejected(self):
        c=copy.deepcopy(self.c);c['cases'][0]['expected']=True;self.assertFalse(preservation(self.b,c))
    def test_wrong_count_rejected(self):
        c=copy.deepcopy(self.c);c['passed']=999;self.assertFalse(preservation(self.b,c))
    def test_forged_pass_rejected(self):
        c=copy.deepcopy(self.c);c['cases'][0]['actual']=None;self.assertFalse(preservation(self.b,c))
    def test_nonbool_pass_rejected(self):
        c=copy.deepcopy(self.c);c['cases'][0]['passed']=1;self.assertFalse(preservation(self.b,c))
    def test_bool_nested_refused(self):self.assertFalse(json_equal({'x':[True]},{'x':[1]}))
    def test_worker_host_canary(self):
        r=execute(b'def arithmetic(x): return open("/etc/passwd").read()\n',[{'id':'x','task':'arithmetic','input':1}])
        self.assertTrue(r['valid']);self.assertEqual(r['values'][0]['error'],'FileNotFoundError')
    def test_baseline_expected_score(self):self.assertEqual(self.b['passed'],111)
if __name__=='__main__':unittest.main(verbosity=2)
