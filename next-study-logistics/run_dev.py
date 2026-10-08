"""Logistics only; invokes frozen methods, no edit or extra candidate proposal."""
import hashlib,json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'next-study'/'src'))
from runner import run_batch
sys.path.insert(0,str(ROOT/'v5'))
from isolation import json_equal
pack_path=Path(sys.argv[1]);pack_hash=hashlib.sha256(pack_path.read_bytes()).hexdigest()
if pack_hash!='f9be0ccf90833349a9486adeee23343fab78ccfeda7590b6855851650cee4c55':raise ValueError('dev hash')
M=ROOT/'next-study'/'PROPOSED-METHOD-MANIFEST.json'
if hashlib.sha256(M.read_bytes()).hexdigest()!='4ec33731c7da794850c7db1ff241681371935a0ccbd92f03875253ba381b506c':raise ValueError('method manifest')
def verify():
 for name,h in json.loads(M.read_text()).items():
  if hashlib.sha256((M.parent/name).read_bytes()).hexdigest()!=h:raise ValueError('frozen bytes changed')
verify();pack=json.loads(pack_path.read_text());tasks=pack['tasks']
if len(tasks)!=4 or any(t['split']!='dev'or len(t['cases'])!=10 for t in tasks):raise ValueError('dev count')
trials=[]
for arm,variant in [('A0',0),* [('A1',v)for v in range(32)],('A2',0)]:
 start=time.monotonic();used=0;case_reports=[];task_reports=[]
 for task in tasks:
  if used>=3000:raise ValueError('dev budget exhausted: final reserved')
  result=run_batch(arm,variant,[c['wire']for c in task['cases']]);used+=result['wall_seconds']
  outcomes=[]
  for i,c in enumerate(task['cases']):
   actual=result['outputs'][i]['output']if result['valid']else None
   passed=result['valid']and json_equal(actual,c['expected'])
   row={'id':c['id'],'task_id':task['id'],'actual':actual,'expected':c['expected'],'passed':passed,'violation':result['reason']}
   outcomes.append(row);case_reports.append(row)
  task_reports.append({'id':task['id'],'template':task['template'],'passed':sum(r['passed']for r in outcomes),'total':10,'runner':result})
 trials.append({'arm':arm,'variant':variant,'task_reports':task_reports,'cases':case_reports,'passed':sum(r['passed']for r in case_reports),'total':40,'worker_wall_seconds':used,'host_wall_seconds':time.monotonic()-start})
 # A1 aggregate dev budget spans all variants, not a separate budget per variant.
 if sum(t['worker_wall_seconds']for t in trials if t['arm']==arm)>3000:raise ValueError('arm dev cap reached')
selected=min([t for t in trials if t['arm']=='A1'],key=lambda t:(-t['passed'],t['variant']))
verify()
out={'dev_pack_sha256':pack_hash,'method_manifest_sha256':hashlib.sha256(M.read_bytes()).hexdigest(),'frozen_tip':'677d773374a68155d6f17c8f961040ab164609c4','A1_selected_variant':selected['variant'],'A1_tied_best_variants':[t['variant']for t in trials if t['arm']=='A1'and t['passed']==selected['passed']],'trials':trials,'accounting':{arm:{'worker_launches':sum(len(t['task_reports'])for t in trials if t['arm']==arm),'case_executions':sum(t['total']for t in trials if t['arm']==arm),'unique_method_trials':sum(t['arm']==arm for t in trials),'worker_wall_seconds':sum(t['worker_wall_seconds']for t in trials if t['arm']==arm),'final_reserved_seconds':600}for arm in ['A0','A1','A2']},'custody':'evaluator-retained, procedural author-hidden custody; access-control separation not independently verified','fresh_independent_transfer':'withheld'}
path=Path(__file__).parent/'receipts'/'development-selection.json';path.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'selected_variant':out['A1_selected_variant'],'ties':out['A1_tied_best_variants'],'A0':trials[0]['passed'],'A1':selected['passed'],'A2':trials[-1]['passed'],'accounting':out['accounting']},indent=2))
