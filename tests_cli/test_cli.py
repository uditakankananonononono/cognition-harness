"""New reconstructed-code tests, not reproduction of the lost receipt."""
import hashlib,json,subprocess,sys,tempfile,unittest
from pathlib import Path
from harness_cli.__main__ import inspect_manifest,submit,Refusal
class HarnessCLI(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.r=Path(self.tmp.name);(self.r/'method.py').write_text('def solve(x): return x\n');self.man=self.r/'manifest.json';self.man.write_text(json.dumps({'method.py':hashlib.sha256((self.r/'method.py').read_bytes()).hexdigest()}));self.pin=hashlib.sha256(self.man.read_bytes()).hexdigest();self.selection=self.r/'selection.json';self.selection.write_text(json.dumps({'method_manifest_sha256':self.pin,'arm':'A1','variant':0,'purpose':'independent_review'}))
 def tearDown(self):self.tmp.cleanup()
 def test_verify(self):self.assertEqual(inspect_manifest(self.r,self.man,self.pin)['status'],'verified')
 def test_pin(self):
  with self.assertRaises(Refusal):inspect_manifest(self.r,self.man,'0'*64)
 def test_tamper(self):
  (self.r/'method.py').write_text('tamper')
  with self.assertRaises(Refusal):inspect_manifest(self.r,self.man,self.pin)
 def test_symlink(self):
  (self.r/'method.py').unlink();(self.r/'method.py').symlink_to('/etc/passwd')
  with self.assertRaises(Refusal):inspect_manifest(self.r,self.man,self.pin)
 def test_escape(self):
  self.man.write_text(json.dumps({'../escape':'0'*64}));pin=hashlib.sha256(self.man.read_bytes()).hexdigest()
  with self.assertRaises(Refusal):inspect_manifest(self.r,self.man,pin)
 def test_duplicate(self):
  self.man.write_text('{"x":"a","x":"b"}');pin=hashlib.sha256(self.man.read_bytes()).hexdigest()
  with self.assertRaises(Refusal):inspect_manifest(self.r,self.man,pin)
 def test_submit(self):
  out=self.r/'receipt';submit(self.r,self.man,self.pin,self.selection,out);v=json.loads(out.read_text());self.assertEqual(v['state'],'pending_independent_review');self.assertEqual(v['activation'],'not_authorized');self.assertIn('RECONSTRUCTED',v['build_provenance']);self.assertEqual(out.stat().st_mode&0o777,0o600)
 def test_no_overwrite(self):
  out=self.r/'receipt';out.write_text('old')
  with self.assertRaises(FileExistsError):submit(self.r,self.man,self.pin,self.selection,out)
  self.assertEqual(out.read_text(),'old')
 def test_bool_variant(self):
  v=json.loads(self.selection.read_text());v['variant']=True;self.selection.write_text(json.dumps(v))
  with self.assertRaises(Refusal):submit(self.r,self.man,self.pin,self.selection,self.r/'out')
 def test_activation(self):
  v=json.loads(self.selection.read_text());v['purpose']='activate';self.selection.write_text(json.dumps(v))
  with self.assertRaises(Refusal):submit(self.r,self.man,self.pin,self.selection,self.r/'out')
 def test_cli(self):
  p=subprocess.run([sys.executable,'-m','harness_cli','verify','--root',str(self.r),'--manifest',str(self.man),'--pin',self.pin],capture_output=True,text=True);self.assertEqual(p.returncode,0);self.assertEqual(json.loads(p.stdout)['status'],'verified')
if __name__=='__main__':unittest.main(verbosity=2)
