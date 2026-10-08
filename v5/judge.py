"""Independent of proposer implementation; separate scoring process, fixed answers."""
import json, sys
from pathlib import Path
from isolation import R, sha, score

def verify(pin):
    manifest=(R/'frozen'/'MANIFEST.json').read_bytes()
    if sha(manifest)!=pin: raise ValueError('manifest pin mismatch')
    for name,digest in json.loads(manifest).items():
        if sha((R/'frozen'/name).read_bytes()) != digest: raise ValueError('frozen bytes changed')

def promotion(baseline,candidate):
    if not baseline.get('valid') or not candidate.get('valid'): return False
    return candidate['passed']>baseline['passed'] and all(candidate['per_task'][t]>=baseline['per_task'][t] for t in baseline['per_task'])

def preservation(baseline,candidate):
    """Match reports to the pinned suite, recompute counts, then preserve baseline passes."""
    expected=json.loads((R/'frozen'/'eval.json').read_bytes())
    def validate(report):
        if type(report) is not dict or report.get('valid') is not True or not isinstance(report.get('cases'),list):return False
        if len(report['cases'])!=len(expected):return False
        for c,e in zip(report['cases'],expected):
            if type(c) is not dict or not {'id','task','expected','actual','error','passed'}.issubset(c):return False
            if type(c['id']) is not str or type(c['task']) is not str:return False
            if c['error'] is not None and type(c['error']) is not str:return False
            if c.get('id')!=e['id'] or c.get('task')!=e['task']:return False
            from isolation import json_equal
            if not json_equal(c.get('expected'),e['expected']):return False
            passed=c.get('error') is None and json_equal(c.get('actual'),e['expected'])
            if type(c.get('passed')) is not bool or c['passed']!=passed:return False
        counts={t:sum(c['passed'] for c in report['cases'] if c['task']==t) for t in sorted({e['task'] for e in expected})}
        from isolation import json_equal
        return type(report.get('passed')) is int and report['passed']==sum(counts.values()) and type(report.get('total')) is int and report['total']==len(expected) and json_equal(report.get('per_task'),counts)
    if not validate(baseline) or not validate(candidate):return False
    return promotion(baseline,candidate) and all(not b['passed'] or c['passed'] for b,c in zip(baseline['cases'],candidate['cases']))

if __name__=='__main__':
    verify(sys.argv[1])
    cases=json.loads((R/'frozen'/'eval.json').read_bytes())
    reports=[score(Path(p).read_bytes(),cases) for p in sys.argv[2:]]
    verify(sys.argv[1])
    print(json.dumps({'manifest_pin':sys.argv[1],'baseline':reports[0],'candidates':[{'report':c,'aggregate_gate':promotion(reports[0],c),'preservation_gate':preservation(reports[0],c),'baseline_pass_losses':[b['id'] for b,v in zip(reports[0].get('cases',[]),c.get('cases',[])) if b['passed'] and not v['passed']],'activation':'no_authority'} for c in reports[1:]]},indent=2))
