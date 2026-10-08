"""Pure declared transformation semantics. No task examples/reference answers."""
import json,math,functools
class Failure(Exception):pass
MISSING=object()
def fail(code):raise Failure(code)
def equal(a,b):
 if a is MISSING or b is MISSING:return a is b
 if type(a)is not type(b):return False
 if type(a)is list:return len(a)==len(b) and all(equal(x,y) for x,y in zip(a,b))
 if type(a)is dict:return a.keys()==b.keys() and all(equal(a[k],b[k]) for k in a)
 return a==b

def bounded(v,depth=0):
 if depth>5:return False
 if v is None or type(v)in(bool,int):return True
 if type(v)is float:return math.isfinite(v)
 if type(v)is str:return len(v)<=1000 and not any(0xD800<=ord(c)<=0xDFFF for c in v)
 if type(v)is list:return len(v)<=100 and all(bounded(x,depth+1) for x in v)
 if type(v)is dict:return len(v)<=100 and all(type(k)is str and len(k)<=1000 and not any(0xD800<=ord(c)<=0xDFFF for c in k) and bounded(x,depth+1) for k,x in v.items())
 return False

def records_ok(rows):return type(rows)is list and len(rows)<=100 and all(type(r)is dict and bounded(r) for r in rows)
def name(x):return type(x)is str and 1<=len(x)<=64 and not any(0xD800<=ord(c)<=0xDFFF for c in x)
def fields(x):return type(x)is list and len(x)<=20 and all(name(k) for k in x) and len(set(x))==len(x)
def depth(v):
 if type(v)is dict:return 1+max([depth(x) for x in v.values()]+[0])
 if type(v)is list:return 1+max([depth(x) for x in v]+[0])
 return 0
SCHEMAS={
'select':{'op','fields','missing'},'rename':{'op','mapping','missing','collision'},
'filter':{'op','field','relation','value','missing','nonnumeric'},
'sort':{'op','field','direction','missing','mixed'},
'dedup':{'op','fields','missing'},'group_count':{'op','fields','missing'}}
def spec_ok(spec):
 if type(spec)is not dict or set(spec)!={'version','steps'} or type(spec['version'])is not int or spec['version']!=1:fail('invalid_spec')
 if type(spec['steps'])is not list or len(spec['steps'])>6:fail('invalid_spec')
 try:
  if len(json.dumps(spec,ensure_ascii=False,separators=(',',':')).encode())>65536 or depth(spec)-1>6:fail('invalid_spec')
 except (ValueError,TypeError,OverflowError,UnicodeError):fail('invalid_spec')
 unknown=False
 for s in spec['steps']:
  if type(s)is not dict or type(s.get('op'))is not str:fail('invalid_spec')
  op=s['op']
  if op not in SCHEMAS:
   if set(s)!={'op'}:fail('invalid_spec')
   unknown=True;continue
  if set(s)!=SCHEMAS[op]:fail('invalid_spec')
  if 'fields'in s and not fields(s['fields']):fail('invalid_spec')
  if 'field'in s and not name(s['field']):fail('invalid_spec')
  if op=='select' and s['missing']not in ['omit','null','error']:fail('invalid_spec')
  if op=='rename':
   m=s['mapping']
   if type(m)is not dict or len(m)>20 or not all(name(k)and name(v) for k,v in m.items())or len(set(m.values()))!=len(m):fail('invalid_spec')
   if s['missing']not in ['ignore','error']or s['collision']not in ['error','overwrite']:fail('invalid_spec')
  if op=='filter':
   if s['relation']not in ['eq','ne','lt','le','gt','ge']or s['missing']not in ['drop','error']or s['nonnumeric']not in ['drop','error']:fail('invalid_spec')
   if type(s['value'])not in [type(None),bool,int,float,str]or not bounded(s['value']):fail('invalid_spec')
  if op=='sort' and (s['direction']not in ['asc','desc']or s['missing']not in ['first','last','error']or s['mixed']not in ['rank','error']):fail('invalid_spec')
  if op in ['dedup','group_count']and s['missing']not in ['distinct','null','error']:fail('invalid_spec')
 if unknown:fail('unsupported')

def typed(v):
 if v is None:return ['null',None]
 if type(v)is bool:return ['bool',v]
 if type(v)is int:return ['int',str(v)]
 if type(v)is float:return ['float','0.0'if v==0 else repr(v)]
 if type(v)is str:return ['str',v]
 if type(v)is list:return ['list',[typed(x)for x in v]]
 return ['dict',[[k,typed(v[k])]for k in sorted(v)]]
def canonical(v):return json.dumps(typed(v),ensure_ascii=False,separators=(',',':'))
def key(row,s,variant):
 result=[]
 for f in s['fields']:
  v=row.get(f,MISSING)
  if v is MISSING:
   if s['missing']=='error':fail('missing_field')
   if s['missing']=='null'or variant&8:v=None
  result.append(v)
 return result
def eq_variant(a,b,variant):
 if not variant&1:return equal(a,b)
 if a is MISSING or b is MISSING:return a is b
 if type(a)is list and type(b)is list:return len(a)==len(b) and all(eq_variant(x,y,variant)for x,y in zip(a,b))
 return a==b

def select_op(rows,s,variant):
 result=[]
 for r in rows:
  out={}
  for f in s['fields']:
   if f in r:out[f]=r[f]
   elif s['missing']=='null':out[f]=None
   elif s['missing']=='error':fail('missing_field')
  result.append(out)
 return result

def rename_op(rows,s,variant):
 result=[];m=s['mapping']
 for r in rows:
  if variant&2:
   out=dict(r)
   for a,b in m.items():
    if a not in out:
     if s['missing']=='error':fail('missing_field')
     continue
    v=out.pop(a)
    if b in out and s['collision']=='error':fail('rename_collision')
    out[b]=v
  else:
   if s['missing']=='error'and any(a not in r for a in m):fail('missing_field')
   unmapped={k:v for k,v in r.items()if k not in m}
   renamed={m[k]:v for k,v in r.items()if k in m}
   if s['collision']=='error'and unmapped.keys()&renamed.keys():fail('rename_collision')
   out={}
   for k,v in r.items():
    t=m.get(k,k)
    if k not in m and t in renamed:continue
    out[t]=v
  result.append(out)
 return result

def filter_op(rows,s,variant):
 out=[]
 for r in rows:
  v=r.get(s['field'],MISSING)
  if v is MISSING:
   if s['missing']=='error':fail('missing_field')
   continue
  rel=s['relation'];target=s['value']
  if rel in ['eq','ne']:
   keep=eq_variant(v,target,variant)
   if rel=='ne':keep=not keep
  else:
   if type(v)not in [int,float]or type(target)not in [int,float]:
    if s['nonnumeric']=='error':fail('nonnumeric_value')
    continue
   keep={'lt':lambda:v<target,'le':lambda:v<=target,'gt':lambda:v>target,'ge':lambda:v>=target}[rel]()
  if keep:out.append(r)
 return out

def sort_op(rows,s,variant):
 f=s['field'];present=[r for r in rows if f in r];absent=[r for r in rows if f not in r]
 if absent and s['missing']=='error':fail('missing_field')
 if s['mixed']=='error'and len({type(r[f])for r in present})>1:fail('mixed_type')
 rank={type(None):0,bool:1,int:2,float:3,str:4,list:5,dict:6}
 def compare(a,b):
  a,b=a[f],b[f];ra,rb=rank[type(a)],rank[type(b)]
  if ra!=rb:return (ra>rb)-(ra<rb)
  if a is None:return 0
  if type(a)in [list,dict]:a,b=canonical(a),canonical(b)
  return (a>b)-(a<b)
 desc=s['direction']=='desc'
 reverse_ties=bool(variant&4)and desc
 present=sorted(present,key=functools.cmp_to_key(compare),reverse=desc and not reverse_ties)
 if reverse_ties:present=list(reversed(present))
 first=s['missing']=='first'
 if variant&16 and desc:first=not first
 return absent+present if first else present+absent

def dedup_op(rows,s,variant):
 seen=[];out=[]
 for r in rows:
  k=key(r,s,variant)
  if any(eq_variant(k,p,variant)for p in seen):continue
  seen.append(k);out.append(r)
 return out

def group_count_op(rows,s,variant):
 keys=[];counts=[]
 for r in rows:
  k=key(r,s,variant)
  match=next((i for i,p in enumerate(keys)if eq_variant(k,p,variant)),None)
  if match is None:keys.append(k);counts.append(1)
  else:counts[match]+=1
 return [{'key':[{'present':v is not MISSING,'value':None if v is MISSING else v}for v in k],'count':n}for k,n in zip(keys,counts)]

def finish(rows):
 if not records_ok(rows):fail('output_limit')
 result={'status':'ok','records':rows}
 if len(json.dumps(result,ensure_ascii=False,separators=(',',':')).encode())>131072:fail('output_limit')
 return result

def solve(spec,rows,variant=0):
 try:
  spec_ok(spec)
  if not records_ok(rows):fail('invalid_records')
  for step in spec['steps']:
   rows=globals()[step['op']+'_op'](rows,step,variant)
   finish(rows)
  return finish(rows)
 except Failure as e:return {'status':'error','code':str(e)}
