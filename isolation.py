import hashlib, json, os, signal, subprocess, tempfile
from pathlib import Path
R=Path(__file__).resolve().parent

def sha(data):
    return hashlib.sha256(data).hexdigest()

def execute(source, cases):
    """bwrap namespaces; only fixed runtime plus candidate bytes and runner mounted."""
    with tempfile.TemporaryDirectory() as d:
        d=Path(d)
        (d/'candidate.py').write_bytes(source)
        (d/'worker.py').write_bytes((R/'worker.py').read_bytes())
        cmd=['bwrap','--unshare-all','--die-with-parent','--new-session','--cap-drop','ALL','--ro-bind','/usr','/usr','--ro-bind','/lib','/lib','--ro-bind','/lib64','/lib64','--proc','/proc','--dev','/dev','--tmpfs','/tmp','--ro-bind',str(d),'/work','--chdir','/work','--clearenv','--setenv','PYTHONHASHSEED','0','--setenv','PYTHONDONTWRITEBYTECODE','1','/usr/bin/python3','-S','-B','/work/worker.py']
        with (d/'stdout').open('wb') as out, (d/'stderr').open('wb') as err:
            proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stdout=out,stderr=err,start_new_session=True)
            try:
                proc.communicate(json.dumps([{k:c[k] for k in ('id','task','input')} for c in cases]).encode(),timeout=3)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid,signal.SIGKILL); proc.communicate()
                return {'valid':False,'reason':'timeout'}
        if proc.returncode:
            return {'valid':False,'reason':'process_failure','exit':proc.returncode,'stderr':(d/'stderr').read_bytes()[:4096].decode(errors='replace')}
        raw=(d/'stdout').read_bytes()
        if len(raw)>65536:
            return {'valid':False,'reason':'output_limit'}
        try:
            values=json.loads(raw)
            if not isinstance(values,list) or len(values)!=len(cases): raise ValueError()
            if [v['id'] for v in values] != [c['id'] for c in cases]: raise ValueError()
        except (ValueError,KeyError,TypeError):
            return {'valid':False,'reason':'malformed_output'}
        return {'valid':True,'values':values,'source_sha256':sha(source)}

def score(source,cases):
    execution=execute(source,cases)
    if not execution['valid']: return execution
    details=[{'id':c['id'],'task':c['task'],'expected':c['expected'],'actual':v.get('value'),'error':v.get('error'),'passed': ('error' not in v and type(v.get('value')) is type(c['expected']) and v.get('value')==c['expected'])} for c,v in zip(cases,execution['values'])]
    tasks={task:sum(c['passed'] for c in details if c['task']==task) for task in ('canonical','unique','merge')}
    return {'valid':True,'source_sha256':execution['source_sha256'],'passed':sum(tasks.values()),'total':len(cases),'per_task':tasks,'cases':details}
