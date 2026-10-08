import hashlib,json
from pathlib import Path
R=Path(__file__).parent
shapes=[None,False,True,0,1,1.0,'', 'x', [], [None], {}, {'valid':False}, {'valid':True}, {'valid':True,'cases':None}, {'valid':True,'cases':'bad'}, {'valid':True,'cases':[]}, {'valid':1,'cases':[]}, {'valid':True,'cases':[None]}, {'valid':True,'cases':[[]]}]
case_shapes=[None,False,True,0,1,1.0,'', 'x', [], [None], {}, {'passed':True}, {'id':'fake','task':'first_index','expected':-1,'actual':-1,'passed':True}]
probes=[]
for target in ['baseline','candidate']:
    for i,value in enumerate(shapes):probes.append({'id':f'{target}-shape-{i}','target':target,'kind':'replace_report','value':value,'expected':False})
    for i,value in enumerate(case_shapes):probes.append({'id':f'{target}-case-{i}','target':target,'kind':'replace_case','value':value,'expected':False})
    for field in ['valid','cases','passed','total','per_task']:
        probes.append({'id':f'{target}-missing-{field}','target':target,'kind':'delete_field','field':field,'expected':False})
    for field in ['id','task','expected','actual','error','passed']:
        probes.append({'id':f'{target}-case-missing-{field}','target':target,'kind':'delete_case_field','field':field,'expected':False})
protocol={'version':5,'study':'bounded malformed JSON-report refusal totality and unchanged M4b gates on explicitly reused inputs','data':'M3/M4b known eval inputs/answers; baseline/candidate known','rule':'strict bool valid, dict top-level, list of complete dict cases with fixed required fields, exact JSON typed IDs/tasks/expected values, typed pass flag/counts, recomputed outcomes, strict aggregate gain plus all baseline successes retained','expected':'each frozen malformed probe returns False without raising; selected/control fixed-suite outcomes unchanged','limits':['only frozen JSON shapes tested, no never-raises claim outside matrix','no arbitrary hostile Python objects/custom mapping subclasses/non-JSON probe claims','reused known inputs, not blind/unseen performance','no new synthesis/model/arbitrary invention/AGI/generalization/speedup','host judge author-visible answers, worker inputs-only','git timestamps do not prove no private pre-freeze scoring','no cgroup/kernel/covert-channel guarantees; no activation authority']}
for name,data in [('protocol.json',protocol),('malformed.json',probes)]:
    (R/'frozen'/name).write_text(json.dumps(data,indent=2)+'\n')
manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((R/'frozen').glob('*.json'))}
manifest.update({'../candidates/'+p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((R/'candidates').glob('*.py'))})
(R/'frozen'/'MANIFEST.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n')
print(len(probes),hashlib.sha256((R/'frozen'/'MANIFEST.json').read_bytes()).hexdigest())
