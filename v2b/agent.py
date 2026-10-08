"""Deterministic AST-body grammar search, dev-only. No eval feedback in selection."""
import ast,json,subprocess,sys
from isolation import R,score,sha
from judge import verify

def grammar(task):
    if task=='canonical':
        return [f'return {transform}{split}' for transform in ['text.lower()','text','text.upper()','text.casefold()'] for split in [".split(' ')",'.split()',".split('\\t')"]]
    if task=='unique':
        return ['return sorted(set(items))','return items','return list(dict.fromkeys(items))','return list(reversed(list(dict.fromkeys(items))))','return []']
    return [f'''out = []
for start, end in {order}:
    if out and start {comparison} out[-1][1]:
        out[-1][1] = {boundary}
    else:
        out.append([start, end])
return out''' for order in ['sorted(intervals)','reversed(sorted(intervals))'] for comparison in ['<','<='] for boundary in ['end','max(out[-1][1], end)']]

def rewrite(source,task,body):
    tree=ast.parse(source)
    for node in tree.body:
        if isinstance(node,ast.FunctionDef) and node.name==task:
            node.body=ast.parse(body).body
            break
    else: raise ValueError('unknown task')
    return ast.unparse(ast.fix_missing_locations(tree))+'\n'

def run(pin):
    verify(pin)
    dev=json.loads((R/'frozen'/'dev.json').read_bytes())
    source=(R/'candidates'/'baseline.py').read_text()
    history=[]
    for task in ('canonical','unique','merge'):
        trials=[]
        for index,body in enumerate(grammar(task)):
            candidate=rewrite(source,task,body)
            report=score(candidate.encode(),dev)
            trials.append({'index':index,'body':body,'candidate_sha256':sha(candidate.encode()),'report':report})
        valid=[t for t in trials if t['report'].get('valid')]
        if not valid: raise ValueError('all trials invalid')
        best=max(valid,key=lambda t:(t['report']['passed'],-t['index']))
        before=score(source.encode(),dev)
        if best['report']['passed']>before['passed']:
            source=rewrite(source,task,best['body'])
        history.append({'task':task,'before':before,'trials':trials,'selected_index':best['index'],'tied_best_indices':[t['index'] for t in valid if t['report']['passed']==best['report']['passed']],'after_sha256':sha(source.encode())})
        (R/'candidates'/f'round-{task}.py').write_text(source)
    candidate=R/'candidates'/'candidate.py'; candidate.write_text(source)
    control=R/'candidates'/'regression.py'; control.write_text(rewrite(source,'unique','return []'))
    (R/'receipts'/'dev-history.json').write_text(json.dumps(history,indent=2)+'\n')
    judged=subprocess.run([sys.executable,str(R/'judge.py'),pin,str(R/'candidates'/'baseline.py'),str(candidate),str(control)],check=True,capture_output=True,text=True)
    (R/'receipts'/'measurement.json').write_text(judged.stdout)
    result=json.loads(judged.stdout)
    print(json.dumps({'baseline':{'passed':result['baseline']['passed'],'per_task':result['baseline']['per_task']},'candidate_and_control':[{'passed':c['report'].get('passed'),'per_task':c['report'].get('per_task'),'gate':c['measurement_gate']} for c in result['candidates']]},indent=2))
if __name__=='__main__':run(sys.argv[1])
