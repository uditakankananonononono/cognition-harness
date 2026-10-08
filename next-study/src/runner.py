"""Runner to be installed in evaluator custody, no final inputs stored by builder."""
import json,os,signal,subprocess,tempfile,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def run_batch(arm,variant,raw_inputs):
    if arm not in ['A0','A1','A2']or type(variant)is not int or not 0<=variant<32 or len(raw_inputs)>10:raise ValueError('runner contract')
    payload=json.dumps({'arm':arm,'variant':variant,'inputs':raw_inputs},ensure_ascii=False).encode()
    # At most10 declared input batches; transport overhead allowed up to12MiB.
    if len(payload)>12582912:raise ValueError('batch wire limit')
    with tempfile.TemporaryDirectory() as d:
        d=Path(d);start=time.monotonic();reason=None
        cmd=['bwrap','--unshare-all','--die-with-parent','--new-session','--cap-drop','ALL','--ro-bind','/usr','/usr','--ro-bind','/lib','/lib','--ro-bind','/lib64','/lib64','--proc','/proc','--dev','/dev','--tmpfs','/tmp','--ro-bind',str(ROOT),'/work','--chdir','/work','--clearenv','--setenv','PYTHONHASHSEED','0','/usr/bin/python3','-S','-B','/work/worker.py']
        (d/'input').write_bytes(payload)
        with (d/'input').open('rb')as inp,(d/'stdout').open('wb')as out,(d/'stderr').open('wb')as err:
            p=subprocess.Popen(cmd,stdin=inp,stdout=out,stderr=err,start_new_session=True)
            try:p.wait(timeout=60)
            except subprocess.TimeoutExpired:
                reason='timeout';os.killpg(p.pid,signal.SIGKILL);p.wait(timeout=5)
        if p.returncode and reason is None:reason='process_failure'
        raw=(d/'stdout').read_bytes()
        values=None
        if reason is None:
            try:
                values=json.loads(raw)
                if type(values)is not list or len(values)!=len(raw_inputs):raise ValueError()
            except (ValueError,TypeError):reason='invalid_worker_output'
        # Only scorer receives outputs; stdout/stderr artifacts erased on return.
        return {'valid':reason is None,'reason':reason,'outputs':values,'wall_seconds':time.monotonic()-start,'exit':p.returncode,'stdout_bytes':len(raw),'stderr_bytes':(d/'stderr').stat().st_size}
