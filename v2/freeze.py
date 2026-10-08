"""Construct fresh seeded stress inputs and separate reference outputs, before scoring."""
import hashlib,json,random,re
from pathlib import Path
R=Path(__file__).parent

def union_oracle(intervals):
    # Connected components of the overlap graph, not candidate's greedy sweep.
    groups=[]
    for interval in intervals:
        group=[interval]; pending=list(groups); groups=[]
        changed=True
        while changed:
            changed=False; remaining=[]
            for other in pending:
                if any(a<=d and c<=b for a,b in group for c,d in other):
                    group+=other; changed=True
                else: remaining.append(other)
            pending=remaining
        groups=pending+[group]
    return sorted([[min(a for a,b in g),max(b for a,b in g)] for g in groups])

def unique_oracle(items):
    result=[]
    for i,item in enumerate(items):
        if not any(item==earlier for earlier in items[:i]): result.append(item)
    return result

def generate(seed,n,prefix):
    rng=random.Random(seed); result=[]
    tokens=['Alpha','BETA','x-y','12','Ä','Ö','ß','Σ','I','MiXeD','é']
    whites=[' ','  ','\t','\n','\r\n','\u2003','\u00a0']
    for task in ['canonical','unique','merge']:
        for i in range(n):
            if task=='canonical':
                text=rng.choice(whites)*rng.randrange(3)
                text+=''.join(rng.choice(tokens)+rng.choice(whites) for _ in range(rng.randrange(9)))
                value=text; expected=re.findall(r'\S+',text.lower())
            elif task=='unique':
                pool=rng.choice([list(range(-4,5)),tokens])
                value=[rng.choice(pool) for _ in range(rng.randrange(20))]; expected=unique_oracle(value)
            else:
                value=[]
                for _ in range(rng.randrange(13)):
                    a,b=sorted([rng.randrange(-15,16),rng.randrange(-15,16)])
                    value.append([a,b])
                rng.shuffle(value); expected=union_oracle(value)
            result.append({'id':f'{prefix}-{task}-{i:03d}','task':task,'input':value,'expected':expected})
    return result

protocol={'version':2,'tasks':['canonical','unique','merge'],'domain':'same M1 valid domains; whitespace tokens lowercased (not casefold); homogeneous str/int uniqueness first-occurrence order; integer closed interval union touching endpoints merged','score':'recursive exact JSON-node types and values; 360 equally weighted cases, 120 per task','promotion':'total strictly increases relative to named baseline; no per-task decrease; no activation','proposal':'bounded AST-body synthesis grammar, 12 canonical bodies, 5 unique bodies, 8 merge bodies; best valid dev score per task, deterministic first-tie choice; 3 task rounds; candidate only sees 24 dev cases','eval_seed':208103,'dev_seed':98117,'eval_cases_per_task':120,'dev_cases_per_task':8,'resources':{'wall_seconds':3,'cpu_seconds':1,'address_space_bytes':134217728,'output_bytes':65536},'negative_controls':'return no unique values to test task regression; nested JSON bool/int probes','limitations':['frozen 48 exact-output cases only, 3 known repair-menu items, synthetic hand-authored cases, host judge reads answers (not author-blind), git timestamps don\'t prove absence of private pre-freeze scoring, no runtime/cgroup/covert-channel guarantees, no activation authority. This is the carried M1 limit, not the scope of M2.','M2 synthetic seeded stress inputs; author not blind; inputs unseen by proposer during search, not secret from builder','bounded handcrafted 25-body grammar, no language model/general invention/AGI','no statistical or real-world generalization, no speedup or product activation','independent review required before reporting verified improvement']}
for name,data in [('eval.json',generate(208103,120,'eval')),('dev.json',generate(98117,8,'dev')),('protocol.json',protocol)]:
    (R/'frozen'/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((R/'frozen').glob('*.json'))}
(R/'frozen'/'MANIFEST.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n')
print(hashlib.sha256((R/'frozen'/'MANIFEST.json').read_bytes()).hexdigest())
