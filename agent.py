"""Bounded repair agent: edits its own task implementation using dev feedback.
No general code invention or model. Cannot change the protocol or judge.
"""
import json, subprocess, sys
from pathlib import Path
from isolation import R, score, sha
from judge import verify
REPAIRS=[('canonical_whitespace',"text.lower().split(' ')",'text.lower().split()'),('unique_order','sorted(set(items))','list(dict.fromkeys(items))'),('merge_touching','start < out[-1][1]','start <= out[-1][1]')]

def run(pin):
    verify(pin)
    dev=json.loads((R/'frozen'/'dev.json').read_bytes())
    source=(R/'candidates'/'baseline.py').read_text()
    current=score(source.encode(),dev)
    history=[]
    for round_no in range(3):
        trials=[]
        for name,old,new in REPAIRS:
            if old in source:
                proposal=source.replace(old,new,1)
                report=score(proposal.encode(),dev)
                trials.append((report.get('passed',-1),name,proposal,report))
        if not trials: break
        best=max(trials,key=lambda t:(t[0],t[1]))
        accepted=best[0]>current['passed']
        history.append({'round':round_no,'dev_before':current['passed'],'trials':[{'operator':t[1],'report':t[3]} for t in trials],'selected':best[1] if accepted else None})
        if not accepted: break
        source=best[2]; current=best[3]
        (R/'candidates'/f'round-{round_no}.py').write_text(source)
    candidate=R/'candidates'/'candidate.py'; candidate.write_text(source)
    # Outside-search negative control: perfect other tasks but deliberately lose unique order.
    regression=source.replace('list(dict.fromkeys(items))','sorted(set(items))')
    (R/'candidates'/'regression.py').write_text(regression)
    (R/'receipts'/'dev-history.json').write_text(json.dumps(history,indent=2)+'\n')
    # Proposer has finished; held-out judge is invoked once for baseline + selected + control.
    judged=subprocess.run([sys.executable,str(R/'judge.py'),pin,str(R/'candidates'/'baseline.py'),str(candidate),str(R/'candidates'/'regression.py')],check=True,capture_output=True,text=True)
    (R/'receipts'/'measurement.json').write_text(judged.stdout)
    return json.loads(judged.stdout)

if __name__=='__main__':
    result=run(sys.argv[1])
    print(json.dumps({'baseline':result['baseline']['passed'],'candidates':[{'passed':x['report'].get('passed'),'per_task':x['report'].get('per_task'),'measurement_gate':x['measurement_gate'],'activation':x['activation']} for x in result['candidates']]},indent=2))
