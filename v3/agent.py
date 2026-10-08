"""Generic AST operator mutation driven by dev feedback only."""
import ast,copy,json,subprocess,sys
from isolation import R,score,sha
from judge import verify
GROUPS=((ast.Add,ast.Sub,ast.Mult),(ast.Eq,ast.NotEq,ast.Lt,ast.LtE,ast.Gt,ast.GtE))

def proposals(source):
    tree=ast.parse(source)
    for index,node in enumerate(ast.walk(tree)):
        for field,value in ast.iter_fields(node):
            sites=[(None,value)] if isinstance(value,ast.AST) else list(enumerate(value)) if isinstance(value,list) else []
            for slot,current in sites:
                for group in GROUPS:
                    if type(current) not in group: continue
                    for op in group:
                        if type(current) is op: continue
                        clone=copy.deepcopy(tree)
                        owner=list(ast.walk(clone))[index]
                        if slot is None:setattr(owner,field,op())
                        else:getattr(owner,field)[slot]=op()
                        yield {'owner_index':index,'field':field,'slot':slot,'old':type(current).__name__,'new':op.__name__},ast.unparse(ast.fix_missing_locations(clone))+'\n'

def run(pin):
    verify(pin); dev=json.loads((R/'frozen'/'dev.json').read_bytes())
    source=(R/'candidates'/'baseline.py').read_text(); history=[]
    for round_no in range(4):
        before=score(source.encode(),dev); trials=[]
        for edit,candidate in proposals(source):
            report=score(candidate.encode(),dev)
            trials.append({'edit':edit,'candidate_sha256':sha(candidate.encode()),'report':report,'source':candidate})
        valid=[t for t in trials if t['report'].get('valid')]
        if not valid: break
        best=max(valid,key=lambda t:t['report']['passed'])
        accepted=best['report']['passed']>before['passed']
        history.append({'round':round_no,'before':before,'trials':trials,'tied_best_edits':[t['edit'] for t in valid if t['report']['passed']==best['report']['passed']],'selected':best['edit'] if accepted else None})
        if not accepted:break
        source=best['source']; (R/'candidates'/f'round-{round_no}.py').write_text(source)
    candidate=R/'candidates'/'candidate.py';candidate.write_text(source)
    tree=ast.parse(source)
    for n in tree.body:
        if isinstance(n,ast.FunctionDef) and n.name=='first_index':n.body=ast.parse('return -1').body
    control=R/'candidates'/'regression.py';control.write_text(ast.unparse(ast.fix_missing_locations(tree))+'\n')
    (R/'receipts'/'dev-history.json').write_text(json.dumps(history,indent=2)+'\n')
    r=subprocess.run([sys.executable,str(R/'judge.py'),pin,str(R/'candidates'/'baseline.py'),str(candidate),str(control)],check=True,capture_output=True,text=True)
    (R/'receipts'/'measurement.json').write_text(r.stdout)
    result=json.loads(r.stdout)
    print(json.dumps({'baseline':{'passed':result['baseline']['passed'],'per_task':result['baseline']['per_task']},'candidate_control':[{'passed':x['report']['passed'],'per_task':x['report']['per_task'],'gate':x['measurement_gate']} for x in result['candidates']]},indent=2))
if __name__=='__main__':run(sys.argv[1])
