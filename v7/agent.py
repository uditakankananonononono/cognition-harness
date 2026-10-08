import ast,json,subprocess,sys
from isolation import R,score,sha
from judge import verify

def expressions():
 by_cost={};seen=set();pool=[]
 def add(cost,expression):
  if expression in seen:return False
  seen.add(expression);by_cost.setdefault(cost,[]).append(expression);pool.append({'expression':expression,'cost':cost})
  return len(pool)>=512
 for t in ('x','-1','0','1','2','3'):add(1,t)
 for cost in range(2,6):
  for child in by_cost.get(cost-1,[]):
   if add(cost,f'abs({child})'):return pool
  for op in ('+','-','*'):
   for left_cost in range(1,cost-1):
    right_cost=cost-1-left_cost
    for left in by_cost.get(left_cost,[]):
     for right in by_cost.get(right_cost,[]):
      if add(cost,f'({left} {op} {right})'):return pool
 return pool

def source_for(task,expression):
 tree=ast.parse((R/'candidates'/'baseline.py').read_text())
 for n in tree.body:
  if isinstance(n,ast.FunctionDef) and n.name==task:n.body=ast.parse('return '+expression).body
 return ast.unparse(ast.fix_missing_locations(tree))+'\n'

def run(pin):
 verify(pin);dev=json.loads((R/'frozen'/'dev.json').read_bytes());pool=expressions();history=[];selected={}
 for task in ('magnitude','quadratic','affine'):
  cases=[c for c in dev if c['task']==task];trials=[]
  for index,p in enumerate(pool):
   source=source_for(task,p['expression']);r=score(source.encode(),cases)
   trials.append({**p,'index':index,'source_sha256':sha(source.encode()),'report':r})
  valid=[t for t in trials if t['report'].get('valid')]
  best=min(valid,key=lambda t:(-t['report']['passed'],t['cost'],t['expression']))
  selected[task]=best['expression']
  history.append({'task':task,'evaluations':len(trials),'budget_hit':len(trials)==512,'selected':best,'ties_at_best_score':[t['index'] for t in valid if t['report']['passed']==best['report']['passed']],'trials':trials})
 tree=ast.parse((R/'candidates'/'baseline.py').read_text())
 for n in tree.body:
  if isinstance(n,ast.FunctionDef):n.body=ast.parse('return '+selected[n.name]).body
 candidate=R/'candidates'/'candidate.py';candidate.write_text(ast.unparse(ast.fix_missing_locations(tree))+'\n')
 (R/'receipts'/'dev-history.json').write_text(json.dumps(history,indent=2)+'\n')
 r=subprocess.run([sys.executable,str(R/'judge.py'),pin,str(R/'candidates'/'baseline.py'),str(candidate),str(R/'candidates'/'baseline.py')],check=True,capture_output=True,text=True)
 (R/'receipts'/'measurement.json').write_text(r.stdout)
 result=json.loads(r.stdout)
 print('selected',selected)
 print('baseline',result['baseline']['passed'],result['baseline']['per_task'])
 for c in result['candidates']:print('candidate',c['report']['passed'],c['report']['per_task'],c['aggregate_gate'],c['preservation_gate'])
if __name__=='__main__':run(sys.argv[1])
