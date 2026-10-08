"""Public boundary probes, not evaluator data-repair task scoring."""
import json,sys
sys.path.insert(0,str(__import__('pathlib').Path(__file__).resolve().parents[1]/'src'))
from worker import invoke
probes=[b'{"spec":{"version":1,"steps":[]},"records":[{"x":"\uD800"}]}',b'{"spec":{"version":1,"steps":[]},"records":[{"\uDFFF":1}]}',b'{"spec":{"version":1,"steps":[]},"records":[{"x":"\uD83D\uDE00"}]}']
results=[]
for arm in ['A0','A1','A2']:
 for i,raw in enumerate(probes):
  out=invoke(raw,arm,0);expected={'status':'error','code':'invalid_wire'}if i<2 else {'status':'ok','records':[{'x':'😀'}]}
  results.append({'arm':arm,'probe':i,'passed':out==expected,'output':out})
print(json.dumps(results,ensure_ascii=False,indent=2));assert all(r['passed']for r in results)
