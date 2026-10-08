import ast,copy,json,subprocess,sys
from isolation import R,score,sha
from judge import verify

def mutate(source,task):
 tree=ast.parse(source);f=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==task)
 for index,n in enumerate(ast.walk(f)):
  for field,value in ast.iter_fields(n):
   if type(value) in (ast.Add,ast.Sub,ast.Mult):
    for op in (ast.Add,ast.Sub,ast.Mult):
     if type(value) is op:continue
     t=copy.deepcopy(tree);g=next(n for n in t.body if isinstance(n,ast.FunctionDef) and n.name==task)
     setattr(list(ast.walk(g))[index],field,op())
     yield ast.unparse(ast.fix_missing_locations(t))+'\n',{'owner':index,'field':field,'op':op.__name__}
  if isinstance(n,ast.Constant) and type(n.value) is int:
   for value in range(-3,4):
    if value==n.value:continue
    t=copy.deepcopy(tree);g=next(n for n in t.body if isinstance(n,ast.FunctionDef) and n.name==task)
    list(ast.walk(g))[index].value=value
    yield ast.unparse(ast.fix_missing_locations(t))+'\n',{'constant_node':index,'value':value}

def search(source,task,arm,dev):
 cache={};trials=[]
 def evaluate(s,parent=None,edit=None,depth=0):
  if s in cache:return cache[s]
  if len(cache)>=120:return None
  report=score(s.encode(),dev);cache[s]=report
  trials.append({'source':s,'sha256':sha(s.encode()),'report':report,'parent':parent,'edit':edit,'depth':depth})
  return report
 initial=evaluate(source);front=[source];current=source
 for depth in (1,2):
  children=[]
  for parent in front:
   for candidate,edit in mutate(parent,task):
    r=evaluate(candidate,sha(parent.encode()),edit,depth)
    if r is not None and r.get('valid'):children.append(candidate)
  if not children:break
  children=sorted(set(children),key=lambda s:(-cache[s]['passed'],s))
  if arm=='greedy':
   best=children[0]
   if cache[best]['passed']<=cache[current]['passed']:break
   current=best;front=[best]
  else:front=children[:16]
 if arm=='beam':current=min((s for s,r in cache.items() if r.get('valid')),key=lambda s:(-cache[s]['passed'],s))
 return current,{'task':task,'arm':arm,'evaluations':len(cache),'budget_hit':len(cache)>=120,'initial':initial,'selected_sha256':sha(current.encode()),'selected_dev':cache[current],'trials':trials}

def run(pin):
 verify(pin);dev=json.loads((R/'frozen'/'dev.json').read_bytes());histories=[];finals=[]
 for arm in ('greedy','beam'):
  source=(R/'candidates'/'baseline.py').read_text()
  for task in ('scale','shift'):
   source,history=search(source,task,arm,dev);histories.append(history)
  path=R/'candidates'/f'{arm}.py';path.write_text(source);finals.append(str(path))
 (R/'receipts'/'dev-history.json').write_text(json.dumps(histories,indent=2)+'\n')
 r=subprocess.run([sys.executable,str(R/'judge.py'),pin,str(R/'candidates'/'baseline.py'),*finals,str(R/'candidates'/'baseline.py')],capture_output=True,text=True,check=True)
 (R/'receipts'/'measurement.json').write_text(r.stdout)
 result=json.loads(r.stdout)
 print('baseline',result['baseline']['passed'])
 for c in result['candidates']:print(c['report']['passed'],c['report']['per_task'],c['aggregate_gate'],c['preservation_gate'])
if __name__=='__main__':run(sys.argv[1])
