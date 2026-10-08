import ast,json,unittest
from isolation import R,sha,json_equal
from judge import verify,preservation
from agent import interpret,pool,source_for
class Controls(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=json.loads((R/'receipts'/'measurement.json').read_text());cls.h=json.loads((R/'receipts'/'dev-history.json').read_text())
 def test_pin(self):verify('63a9b95d22eb6809373f3f084c754bbb87673653229851b7a5246b456dc1391d')
 def test_budget(self):self.assertTrue(all(h['constructions']<=10000 and h['worker_candidates']<=512 for h in self.h));self.assertEqual(sum(h['scalar_screening_evals'] for h in self.h),14400)
 def test_retained_exact_vector_unique(self):
  for h in self.h:self.assertEqual(len({tuple(t['vector']) for t in h['worker_trials']}),h['worker_candidates'])
 def test_order_and_first_representative(self):
  for h in self.h:
   seen={}
   for t in h['screening_trials']:
    v=tuple(t['vector']);self.assertEqual(t['retained'],v not in seen)
    if v in seen:self.assertEqual(t['representative'],seen[v])
    else:seen[v]=t['expression']
 def test_worker_crosschecks(self):
  for h in self.h:
   for t in h['worker_trials']:self.assertEqual([c['actual'] for c in t['report']['cases']],t['vector'])
 def test_source_hashes(self):
  for h in self.h:
   for t in h['worker_trials']:self.assertEqual(sha(source_for(h['task'],t['expression']).encode()),t['source_sha256'])
 def test_select_from_dev_only(self):
  for h in self.h:self.assertEqual(min(h['worker_trials'],key=lambda t:(-t['report']['passed'],t['cost'],t['expression'])),h['selected'])
 def test_result_gates(self):
  self.assertEqual(self.r['baseline']['passed'],2);c=self.r['candidates'][0];self.assertEqual(c['report']['passed'],168);self.assertTrue(c['preservation_gate']);self.assertFalse(self.r['candidates'][1]['preservation_gate'])
 def test_reused_data_identity(self):
  for name in ['dev.json','eval.json']:self.assertEqual((R/'frozen'/name).read_bytes(),(R.parent/'v7'/'frozen'/name).read_bytes())
 def test_interpreter_known(self):
  for text,x,y in [('abs(x)',-4,4),('(-1 + (x * x))',3,8),('(2 + (x * 3))',-2,-4)]:self.assertEqual(interpret(ast.parse(text,mode='eval'),x),y)
 def test_interpreter_refuses_outside_grammar(self):
  with self.assertRaises(ValueError):interpret(ast.parse('open(x)',mode='eval'),1)
 def test_types_invalid(self):self.assertFalse(json_equal([True],[1]));self.assertFalse(preservation(None,None))
if __name__=='__main__':unittest.main(verbosity=2)
