import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from runner import run_batch
rows=[{'a':'x'*1000,'b':'y'*200}for _ in range(100)]
raw=json.dumps({'spec':{'version':1,'steps':[]},'records':rows},ensure_ascii=False,separators=(',',':'))
results=[]
for arm in ['A0','A1','A2']:
 r=run_batch(arm,0,[raw]*10)
 results.append({'arm':arm,'valid':r['valid'],'reason':r['reason'],'stdout_bytes':r['stdout_bytes'],'exit':r['exit'],'outputs':len(r['outputs']or[]),'all_exact':r['valid']and all(o['output']=={'status':'ok','records':rows}for o in r['outputs'])})
print(json.dumps(results,indent=2));assert all(r['all_exact']for r in results)
