"""Evaluator-owned batch execution. Outputs only to its parent scorer, no logs."""
import json,resource,sys,time,math
resource.setrlimit(resource.RLIMIT_AS,(268435456,268435456))
resource.setrlimit(resource.RLIMIT_CPU,(5,5))
resource.setrlimit(resource.RLIMIT_NPROC,(0,0))
resource.setrlimit(resource.RLIMIT_FSIZE,(1048576,1048576))
from methods import a0,a1,a2
class WireError(Exception):pass

def pairs(items):
    out={}
    for k,v in items:
        if k in out:raise WireError()
        out[k]=v
    return out

def finite_tree(v):
    if type(v)is float and not math.isfinite(v):raise WireError()
    if type(v)is list:
        for item in v:finite_tree(item)
    if type(v)is dict:
        for item in v.values():finite_tree(item)

def parse(raw):
    if len(raw)>1048576:raise WireError()
    try:value=json.loads(raw.decode('utf-8'),object_pairs_hook=pairs,parse_constant=lambda x:(_ for _ in ()).throw(WireError()))
    except (ValueError,UnicodeError,RecursionError):raise WireError()
    try:finite_tree(value)
    except RecursionError:raise WireError()
    if type(value)is not dict or set(value)!={'spec','records'}:raise WireError()
    return value

def invoke(raw,arm,variant=0):
    try:wire=parse(raw)
    except WireError:return {'status':'error','code':'invalid_wire'}
    if arm=='A0':return a0(wire['spec'],wire['records'])
    if arm=='A1':return a1(wire['spec'],wire['records'],variant)
    if arm=='A2':return a2(wire['spec'],wire['records'])
    raise ValueError('unknown frozen arm')

if __name__=='__main__':
    # Evaluator batches wrap cases in raw wire strings; no expected outputs admitted.
    envelope=json.load(sys.stdin)
    if type(envelope)is not dict or set(envelope)!={'arm','variant','inputs'}:raise ValueError('runner wire')
    if len(envelope['inputs'])>10:raise ValueError('batch cap')
    results=[]
    for raw in envelope['inputs']:
        start=time.monotonic();output=invoke(raw.encode('utf-8'),envelope['arm'],envelope['variant'])
        results.append({'output':output,'wall_seconds':time.monotonic()-start})
    print(json.dumps(results,ensure_ascii=False,allow_nan=False,separators=(',',':')))
