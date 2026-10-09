import hashlib,unittest
from probe_partition import split
class PartitionTests(unittest.TestCase):
 def fixture(self):return [{'sha256':hashlib.sha256(str(i).encode()).hexdigest()}for i in range(3)]
 def test_max_disagreement(self):
  c=self.fixture();v={c[0]['sha256']:[0,0],c[1]['sha256']:[0,1],c[2]['sha256']:[0,2]};r=split(c,v);self.assertEqual(r['selected_probe'],1);self.assertEqual(len(r['retained']),3);self.assertEqual(r['correctness'],'unknown')
 def test_typed_bool(self):
  c=self.fixture();v={c[0]['sha256']:[True],c[1]['sha256']:[1],c[2]['sha256']:[False]};self.assertEqual(len(split(c,v)['groups']),3)
 def test_tie_order(self):
  c=self.fixture();v={x['sha256']:[i,i]for i,x in enumerate(c)};self.assertEqual(split(c,v)['selected_probe'],0)
 def test_no_disagreement(self):
  c=self.fixture();v={x['sha256']:[0]for x in c};r=split(c,v);self.assertEqual(r['retained'],[c[0]['sha256']]);self.assertEqual(len(r['discarded']),2)
 def test_cap_retains_all_lineage(self):
  c=self.fixture();v={x['sha256']:[i]for i,x in enumerate(c)};r=split(c,v,1);self.assertTrue(r['cap_hit']);self.assertEqual(len(r['discarded']),2);self.assertEqual(sum(map(len,r['groups'])),3)
 def test_missing_vector(self):
  with self.assertRaises(ValueError):split(self.fixture(),{})
 def test_unequal_vectors(self):
  c=self.fixture();v={x['sha256']:[0]for x in c};v[c[0]['sha256']]=[]
  with self.assertRaises(ValueError):split(c,v)
 def test_unsupported_output(self):
  c=self.fixture();v={x['sha256']:[1.0]for x in c}
  with self.assertRaises(ValueError):split(c,v)
if __name__=='__main__':unittest.main(verbosity=2)
