"""RECONSTRUCTED after workspace loss. New review required."""
import argparse,hashlib,json,os,stat
from pathlib import Path
LIMIT=4*1024*1024
class Refusal(ValueError):pass
def digest(raw):return hashlib.sha256(raw).hexdigest()
def bytes_file(path):
 fd=os.open(Path(path),os.O_RDONLY|os.O_NOFOLLOW)
 try:
  if not stat.S_ISREG(os.fstat(fd).st_mode):raise Refusal('not_regular_file')
  chunks=[];size=0
  while True:
   chunk=os.read(fd,min(65536,LIMIT+1-size))
   if not chunk:break
   chunks.append(chunk);size+=len(chunk)
   if size>LIMIT:raise Refusal('file_limit')
  return b''.join(chunks)
 finally:os.close(fd)
def pairs(items):
 out={}
 for k,v in items:
  if k in out:raise Refusal('duplicate_json_key')
  out[k]=v
 return out
def decode(raw):return json.loads(raw.decode('utf-8'),object_pairs_hook=pairs,parse_constant=lambda x:(_ for _ in ()).throw(Refusal('nonfinite_json')))
def inspect_manifest(root,manifest,pin):
 root=Path(root).resolve(strict=True);raw=bytes_file(manifest)
 if digest(raw)!=pin:raise Refusal('manifest_pin_mismatch')
 mapping=decode(raw)
 if type(mapping)is not dict or not mapping:raise Refusal('invalid_manifest')
 verified=[]
 for name,expected in mapping.items():
  if type(name)is not str or not name or type(expected)is not str or len(expected)!=64 or any(c not in '0123456789abcdef'for c in expected):raise Refusal('invalid_manifest_entry')
  rel=Path(name)
  if rel.is_absolute()or '..'in rel.parts:raise Refusal('path_escape')
  current=root
  for component in rel.parts:
   current=current/component
   if current.is_symlink():raise Refusal('symlink_refused')
  data=bytes_file(root/rel)
  if digest(data)!=expected:raise Refusal('source_hash_mismatch')
  verified.append({'path':name,'sha256':expected,'bytes':len(data)})
 return {'status':'verified','manifest_sha256':pin,'files':verified,'activation':'not_authorized'}
def submit(root,manifest,pin,selection,out):
 before=inspect_manifest(root,manifest,pin);raw=bytes_file(selection);value=decode(raw)
 if type(value)is not dict or set(value)!={'method_manifest_sha256','arm','variant','purpose'}:raise Refusal('selection_schema')
 if value['method_manifest_sha256']!=pin or value['arm']not in ['A0','A1','A2']or type(value['variant'])is not int or not 0<=value['variant']<32 or value['purpose']!='independent_review':raise Refusal('selection_scope')
 if value['arm']!='A1'and value['variant']!=0:raise Refusal('variant_scope')
 receipt={'schema_version':1,'state':'pending_independent_review','method_manifest_sha256':pin,'selection_sha256':digest(raw),'selection':value,'verified_files':before['files'],'activation':'not_authorized','final_inputs_included':False,'limits':'local integrity only; no owner permission, score or kernel safety claim','build_provenance':'RECONSTRUCTED, new review required'}
 payload=(json.dumps(receipt,sort_keys=True,indent=2)+'\n').encode();out=Path(out);out.parent.mkdir(parents=True,exist_ok=True)
 fd=os.open(out,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 try:
  if inspect_manifest(root,manifest,pin)!=before:raise Refusal('sources_changed_before_receipt')
  with os.fdopen(fd,'wb',closefd=False)as stream:stream.write(payload);stream.flush();os.fsync(fd)
 except BaseException:
  out.unlink(missing_ok=True);raise
 finally:os.close(fd)
 return {'status':'submitted_for_review','receipt_path':str(out),'receipt_sha256':digest(payload),'activation':'not_authorized'}
def main():
 parser=argparse.ArgumentParser(description='RECONSTRUCTED review-only CLI. Never activates code.');sub=parser.add_subparsers(dest='command',required=True)
 for name in ['verify','submit']:
  p=sub.add_parser(name);p.add_argument('--root',required=True);p.add_argument('--manifest',required=True);p.add_argument('--pin',required=True)
  if name=='submit':p.add_argument('--selection',required=True);p.add_argument('--out',required=True)
 a=parser.parse_args()
 try:r=inspect_manifest(a.root,a.manifest,a.pin)if a.command=='verify'else submit(a.root,a.manifest,a.pin,a.selection,a.out)
 except (Refusal,OSError,ValueError,UnicodeError,RecursionError)as e:print(json.dumps({'status':'refused','reason':type(e).__name__,'activation':'not_authorized'}));return 2
 print(json.dumps(r,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
