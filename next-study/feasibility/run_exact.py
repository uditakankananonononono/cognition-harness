import json,os,signal,subprocess,tempfile,time
from pathlib import Path
R=Path(__file__).resolve().parent
result=[]
for mode in ['fork','memory','cpu','stdout','stderr','sleep','runtime']:
 with tempfile.TemporaryDirectory() as d:
  d=Path(d);out=d/'out';err=d/'err'
  cmd=['bwrap','--unshare-all','--die-with-parent','--new-session','--cap-drop','ALL','--ro-bind','/usr','/usr','--ro-bind','/lib','/lib','--ro-bind','/lib64','/lib64','--proc','/proc','--dev','/dev','--tmpfs','/tmp','--ro-bind',str(R),'/work','--chdir','/work','--clearenv','--setenv','PYTHONHASHSEED','0','/usr/bin/python3','-S','-B','/work/exact_probe.py',mode]
  start=time.monotonic();killed=False
  with out.open('wb') as o,err.open('wb') as e:
   p=subprocess.Popen(cmd,stdout=o,stderr=e,start_new_session=True)
   try:p.wait(timeout=60)
   except subprocess.TimeoutExpired:
    killed=True;os.killpg(p.pid,signal.SIGKILL);p.wait(timeout=5)
  try:os.killpg(p.pid,0);gone=False
  except ProcessLookupError:gone=True
  result.append({'mode':mode,'exit':p.returncode,'wall':time.monotonic()-start,'timeout':killed,'process_group_gone':gone,'stdout_bytes':out.stat().st_size,'stderr_bytes':err.stat().st_size,'stdout_first200':out.read_bytes()[:200].decode(errors='replace'),'stderr_first200':err.read_bytes()[:200].decode(errors='replace')})
print(json.dumps(result,indent=2))
