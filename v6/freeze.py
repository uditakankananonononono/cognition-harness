import hashlib,json
from pathlib import Path
R=Path(__file__).parent
# Distinct integer input ranges, fixed exact outputs, no model-written judge.
dev=[];ev=[]
for task in ('scale','shift'):
    for i,x in enumerate([4,5,6,7]):dev.append({'id':f'dev-{task}-{i}','task':task,'input':x,'expected':2*x if task=='scale' else x+3})
    for i,x in enumerate(list(range(-40,4))+list(range(8,44))):ev.append({'id':f'eval-{task}-{i}','task':task,'input':x,'expected':2*x if task=='scale' else x+3})
assert len(ev)==160
assert not {(c['task'],c['input']) for c in dev}&{(c['task'],c['input']) for c in ev}
protocol={'version':6,'study':'bounded plateau-preserving two-edit AST search vs strict greedy on coupled operator/constant bugs','domain':'integer inputs -40..43; functions scale returns2*x and shift returnsx+3','score':'160 equal exact typed eval cases80/task;8 dev cases4/task; disjoint known synthetic inputs','budget':'two independent proposer arms start same baseline: strict greedy vs beam; at most2 edit depths per function, at most120 unique dev candidate evaluations per function per arm; beam width16, preserve ties, deterministic enumeration and lexicographic source tie break; operator Add/Sub/Mult and literal integers -3..3 only; no eval feedback','selection':'beam chooses best dev score among all visited sources; greedy accepts only strict dev gain; function order scale,shift','gate':'M5 complete-report baseline-case-preservation gate for both final sources relative named same baseline','hypothesis':'beam finds coupled repairs across zero-gain intermediate states; greedy stalls; this is a synthetic search-mechanism probe, not general invention','controls':'baseline equal gate rejected; literal outputs wrong rejected as cases; exact typed comparison','limits':['bounded known AST operator and literal grammar, synthetic integer-only functions, no LLM/arbitrary invention/AGI/generalization/speedup claim','only proposer held-out-input blind, author knows answers; worker inputs-only','git timestamps cannot establish absence of private scoring','no cgroup/kernel/covert-channel guarantee, no activation authority','two intentionally constructed coupled bugs; no empirical broad advantage claim']}
for name,data in [('dev.json',dev),('eval.json',ev),('protocol.json',protocol)]:
 (R/'frozen'/name).write_text(json.dumps(data,indent=2)+'\n')
manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((R/'frozen').glob('*.json'))}
manifest['../candidates/baseline.py']=hashlib.sha256((R/'candidates'/'baseline.py').read_bytes()).hexdigest()
(R/'frozen'/'MANIFEST.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
print(hashlib.sha256((R/'frozen'/'MANIFEST.json').read_bytes()).hexdigest())
