import ast,json,subprocess,sys
from isolation import R,score,sha
from judge import verify

def interpret(node,x):
 if isinstance(node,ast.Expression):return interpret(node.body,x)
 if isinstance(node,ast.Name) and node.id=='x':return x
 if isinstance(node,ast.Constant) and type(node.value)is int:return node.value
 if isinstance(node,ast.UnaryOp) and isinstance(node.op,ast.USub):return -interpret(node.operand,x)
 if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id=='abs' and len(node.args)==1:return abs(interpret(node.args[0],x))
 if isinstance(node,ast.BinOp):
  a,b=interpret(node.left,x),interpret(node.right,x)
  if isinstance(node.op,ast.Add):return a+b
  if isinstance(node.op,ast.Sub):return a-b
  if isinstance(node.op,ast.Mult):return a*b
 raise ValueError('outside grammar')

def pool(cases):
 groups={};vectors={};trials=[];retained=[];constructions=0;seen=set();stop=False
 def add(cost,expression):
  nonlocal constructions,stop
  if expression in seen:return
  seen.add(expression);constructions+=1
  tree=ast.parse(expression,mode='eval');values=[interpret(tree,c['input']) for c in cases];key=tuple(values)
  entry={'index':constructions-1,'cost':cost,'expression':expression,'vector':values,'retained':key not in vectors}
  if key not in vectors:
   vectors[key]=expression;groups.setdefault(cost,[]).append(expression);retained.append(entry)
  else:entry['representative']=vectors[key]
  trials.append(entry)
  stop=constructions>=10000 or len(retained)>=512
 for t in ('x','-1','0','1','2','3'):add(1,t)
 for cost in range(2,6):
  for child in groups.get(cost-1,[]):
   add(cost,f'abs({child})')
   if stop:return retained,trials
  for op in ('+','-','*'):
   for lc in range(1,cost-1):
    for left in groups.get(lc,[]):
     for right in groups.get(cost-1-lc,[]):
      add(cost,f'({left} {op} {right})')
      if stop:return retained,trials
 return retained,trials

def source_for(task,expression):
 tree=ast.parse((R/'candidates'/'baseline.py').read_text())
 for n in tree.body:
  if isinstance(n,ast.FunctionDef) and n.name==task:n.body=ast.parse('return '+expression).body
 return ast.unparse(ast.fix_missing_locations(tree))+'\n'

def run(pin):
 verify(pin);dev=json.loads((R/'frozen'/'dev.json').read_bytes());history=[];selected={}
 for task in ('magnitude','quadratic','affine'):
  cases=[c for c in dev if c['task']==task];retained,trials=pool(cases);worker=[]
  for p in retained:
   source=source_for(task,p['expression']);r=score(source.encode(),cases)
   if not r.get('valid') or [c['actual'] for c in r['cases']]!=p['vector']:raise ValueError('screen/worker mismatch')
   worker.append({**p,'source_sha256':sha(source.encode()),'report':r})
  best=min(worker,key=lambda t:(-t['report']['passed'],t['cost'],t['expression']))
  selected[task]=best['expression']
  history.append({'task':task,'constructions':len(trials),'scalar_screening_evals':len(trials)*len(cases),'worker_candidates':len(worker),'construction_cap_hit':len(trials)==10000,'semantic_cap_hit':len(worker)==512,'selected':best,'screening_trials':trials,'worker_trials':worker})
 tree=ast.parse((R/'candidates'/'baseline.py').read_text())
 for n in tree.body:
  if isinstance(n,ast.FunctionDef):n.body=ast.parse('return '+selected[n.name]).body
 candidate=R/'candidates'/'candidate.py';candidate.write_text(ast.unparse(ast.fix_missing_locations(tree))+'\n')
 (R/'receipts'/'dev-history.json').write_text(json.dumps(history,indent=2)+'\n')
 r=subprocess.run([sys.executable,str(R/'judge.py'),pin,str(R/'candidates'/'baseline.py'),str(candidate),str(R/'candidates'/'baseline.py')],check=True,capture_output=True,text=True)
 (R/'receipts'/'measurement.json').write_text(r.stdout)
 result=json.loads(r.stdout);print('selected',selected);print('baseline',result['baseline']['passed'])
 for c in result['candidates']:print(c['report']['passed'],c['report']['per_task'],c['aggregate_gate'],c['preservation_gate'])
if __name__=='__main__':run(sys.argv[1])
