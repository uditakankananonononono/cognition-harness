import json,unittest
from isolation import R,sha,json_equal
from judge import verify,preservation
from agent import mutate
class Controls(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.r=json.loads((R/'receipts'/'measurement.json').read_text());cls.h=json.loads((R/'receipts'/'dev-history.json').read_text())
 def test_pin(self):verify('dd55e300c313855b3d7173b14636e110bfc6d1fe80732cf3142ccafc7c8d27eb')
 def test_disjoint(self):
  d=json.loads((R/'frozen'/'dev.json').read_text());e=json.loads((R/'frozen'/'eval.json').read_text())
  self.assertFalse({(x['task'],x['input']) for x in d}&{(x['task'],x['input']) for x in e})
 def test_budget(self):
  self.assertTrue(all(h['evaluations']<=120 for h in self.h));self.assertTrue(all(t['depth']<=2 for h in self.h for t in h['trials']))
 def test_trial_bytes(self):
  self.assertTrue(all(sha(t['source'].encode())==t['sha256'] for h in self.h for t in h['trials']))
 def test_no_duplicate_evaluations(self):
  for h in self.h:self.assertEqual(len({t['source'] for t in h['trials']}),h['evaluations'])
 def test_arm_scores(self):
  self.assertEqual(self.r['baseline']['passed'],1);self.assertEqual([x['report']['passed'] for x in self.r['candidates']],[81,160,1])
 def test_gates(self):self.assertEqual([x['preservation_gate'] for x in self.r['candidates']],[True,True,False])
 def test_plateau_retained(self):
  g=self.h[0];b=self.h[2]
  self.assertEqual(g['selected_dev']['passed'],0);self.assertEqual(b['selected_dev']['passed'],4)
  self.assertTrue(any(t['depth']==1 and t['report']['passed']==0 for t in b['trials']))
 def test_other_function_unchanged(self):
  import ast
  source=(R/'candidates'/'baseline.py').read_text()
  before=ast.dump(ast.parse(source).body[1])
  for candidate,e in mutate(source,'scale'):self.assertEqual(ast.dump(ast.parse(candidate).body[1]),before)
 def test_typed(self):self.assertFalse(json_equal([True],[1]))
 def test_malformed_refused(self):self.assertFalse(preservation(None,None))
 def test_invalid_pin(self):
  with self.assertRaises(ValueError):verify('0'*64)
if __name__=='__main__':unittest.main(verbosity=2)
