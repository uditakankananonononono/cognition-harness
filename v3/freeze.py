import hashlib,json,random
from pathlib import Path
R=Path(__file__).parent

def oracle(tree):
    if type(tree) is int: return tree
    a,b=oracle(tree[1]),oracle(tree[2])
    if tree[0]=='+': return a+b
    if tree[0]=='-': return a-b
    if tree[0]=='*': return a*b
    raise ValueError()

def make(seed,n,prefix):
    rng=random.Random(seed); out=[]
    def tree(depth):
        if depth==0 or rng.random()<.35: return rng.randrange(-5,6)
        return [rng.choice(['+','-','*']),tree(depth-1),tree(depth-1)]
    for task in ['arithmetic','first_index']:
        for i in range(n):
            if task=='arithmetic':
                x=tree(4); y=oracle(x)
            else:
                vals=sorted(rng.randrange(-8,9) for _ in range(rng.randrange(24)))
                target=rng.randrange(-10,11); x=[vals,target]
                y=next((j for j,v in enumerate(vals) if v==target),-1)
            out.append({'id':f'{prefix}-{task}-{i:03d}','task':task,'input':x,'expected':y})
    return out

protocol={'version':3,'domain':'arithmetic: finite JSON binary expression trees depth<=4, int leaves -5..5, operators +,-,*; first_index: sorted integer lists length0..23 values -8..8, target integer -10..10, return first equal index or -1','tasks':['arithmetic','first_index'],'score':'240 equal-weight recursive exact typed JSON outputs,120/task','promotion':'total strictly greater than baseline AND no per-task decrease; independent review, no activation','proposer':'generic single-node AST operator mutation: Add/Sub/Mult; Eq/NotEq/Lt/LtE/Gt/GtE; repeatedly choose strict dev-score increase, deterministic source-order then operator-order ties; maximum 4 rounds, no eval feedback','dev_seed':7711,'eval_seed':9913,'dev_cases_per_task':12,'eval_cases_per_task':120,'resources':{'wall_seconds':3,'cpu_seconds':1,'address_space_bytes':134217728,'output_bytes':65536},'negative_control':'selected candidate with first_index returning -1','limits':['new synthetic 240-case suite, two bounded homogeneous valid domains','generic operator mutation only, no model/arbitrary invention/AGI','proposer eval-unseen, not author blind; host judge reads answers','git timestamps do not prove no private pre-freeze scoring','no cgroup/kernel/covert-channel guarantees; no activation authority','new domain chosen after M2b; results not directly comparable to prior suites']}
dev=make(7711,12,'dev'); seen={(c['task'],json.dumps(c['input'])) for c in dev}
pool=make(9913,600,'pool'); ev=[]
for task in protocol['tasks']:
    selected=[c for c in pool if c['task']==task and (task,json.dumps(c['input'])) not in seen][:120]
    assert len(selected)==120
    for i,c in enumerate(selected):c['id']=f'eval-{task}-{i:03d}'
    ev+=selected
assert not any((c['task'],json.dumps(c['input'])) in seen for c in ev)
for name,data in [('eval.json',ev),('dev.json',dev),('protocol.json',protocol)]:
    (R/'frozen'/name).write_text(json.dumps(data,indent=2)+'\n')
manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((R/'frozen').glob('*.json'))}
(R/'frozen'/'MANIFEST.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n')
print(hashlib.sha256((R/'frozen'/'MANIFEST.json').read_bytes()).hexdigest())
