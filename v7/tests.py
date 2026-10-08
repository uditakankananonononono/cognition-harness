import ast,json,unittest
from isolation import R,sha,json_equal
from judge import verify,preservation
from agent import expressions,source_for
class Controls(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.r=json.loads((R/'receipts'/'measurement.json').read_text());cls.h=json.loads((R/'receipts'/'dev-history.json').read_text())
 def test_pin(self):verify('9ea2e3b7fc850ed303797255a94162d525becffdbdb06077d806fa3b6bbb36b2')
 def test_bad_pin(self):
  with self.assertRaises(ValueError):verify('0'*64)
 def test_count_budget(self):self.assertEqual([h['evaluations'] for h in self.h],[512,512,512]);self.assertTrue(all(h['budget_hit'] for h in self.h))
 def test_unique_ordered_pool(self):
  pool=expressions();self.assertEqual(len(pool),512);self.assertEqual(len({p['expression'] for p in pool}),512)
  self.assertEqual([p['expression'] for p in pool[:6]],['x','-1','0','1','2','3'])
  self.assertEqual(pool[6]['expression'],'abs(x)')
 def test_cost_order(self):self.assertEqual([p['cost'] for p in expressions()],sorted(p['cost'] for p in expressions()))
 def test_trial_source_bytes(self):
  for h in self.h:
   for t in h['trials']:self.assertEqual(sha(source_for(h['task'],t['expression']).encode()),t['source_sha256'])
 def test_selections(self):
  for h in self.h:
   best=min(h['trials'],key=lambda t:(-t['report'].get('passed',-1),t['cost'],t['expression']))
   self.assertEqual(best,h['selected'])
 def test_retained_failed_gates(self):
  self.assertEqual(self.r['baseline']['passed'],2);c=self.r['candidates'][0]
  self.assertEqual(c['report']['passed'],56);self.assertFalse(c['aggregate_gate']);self.assertFalse(c['preservation_gate'])
 def test_retained_losses(self):self.assertEqual(sum(not c['passed'] for c in self.r['candidates'][0]['report']['cases']),112)
 def test_disjoint(self):
  d=json.loads((R/'frozen'/'dev.json').read_text());e=json.loads((R/'frozen'/'eval.json').read_text())
  self.assertFalse({(c['task'],c['input']) for c in d}&{(c['task'],c['input']) for c in e})
 def test_task_local(self):
  baseline=ast.parse((R/'candidates'/'baseline.py').read_text())
  changed=ast.parse(source_for('magnitude','abs(x)'))
  self.assertEqual([ast.dump(n) for n in baseline.body[1:]],[ast.dump(n) for n in changed.body[1:]])
 def test_typed_and_invalid(self):self.assertFalse(json_equal([True],[1]));self.assertFalse(preservation(None,None))
if __name__=='__main__':unittest.main(verbosity=2)
