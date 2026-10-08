import hashlib, json
from pathlib import Path
R=Path(__file__).parent
cases=[]
def add(task, inputs, expecteds):
    for i,(x,y) in enumerate(zip(inputs,expecteds)):
        cases.append(dict(id=f'{task}-{i:02d}', task=task, input=x, expected=y))
add('canonical', ['', 'A B', '  A  B  ', 'a\tb', 'a\nb', '\t', 'MiXeD', ' a ', 'a   b c', '123 X', 'a\r\nb', 'A\u2003B', 'Ä Ö', 'one\t two\n THREE', ' a  a ', 'x-y Z'], [[], ['a','b'], ['a','b'], ['a','b'], ['a','b'], [], ['mixed'], ['a'], ['a','b','c'], ['123','x'], ['a','b'], ['a','b'], ['ä','ö'], ['one','two','three'], ['a','a'], ['x-y','z']])
add('unique', [[], [1], [1,1], [2,1,2], ['b','a','b'], [0,0,1], [3,2,1], ['','a',''], [-1,2,-1], [1,2,3,1,2], [4,4,4], ['X','x','X'], [2,1], [0,-1,0,2], ['a','b','c','b','d'], [7,6,5,6,7]], [[],[1],[1],[2,1],['b','a'],[0,1],[3,2,1],['','a'],[-1,2],[1,2,3],[4],['X','x'],[2,1],[0,-1,2],['a','b','c','d'],[7,6,5]])
add('merge', [[], [[1,2]], [[1,2],[2,3]], [[3,4],[1,2]], [[1,5],[2,3]], [[1,2],[1,2]], [[0,0],[0,1]], [[-3,-1],[-1,2]], [[5,6],[1,3],[3,5]], [[1,2],[3,4]], [[1,1],[1,1]], [[2,4],[1,3]], [[0,10],[2,3],[9,12]], [[-2,-1],[0,1]], [[0,1],[1,2],[2,2]], [[3,5],[1,3],[8,9],[5,8]]], [[],[[1,2]],[[1,3]],[[1,2],[3,4]],[[1,5]],[[1,2]],[[0,1]],[[-3,2]],[[1,6]],[[1,2],[3,4]],[[1,1]],[[1,4]],[[0,12]],[[-2,-1],[0,1]],[[0,2]],[[1,9]]])
protocol={'version':1,'tasks':['canonical','unique','merge'],'domain':'canonical: Unicode string to lowercased whitespace tokens; unique: homogeneous str/int list, first occurrence order; merge: valid integer closed intervals, sorted union, touching endpoints merge','score':'exact JSON equality, 48 equal-weight cases','promotion':'candidate total strictly increases AND each task pass count does not decrease','budget':'three repair operators, dev score selection only, max 3 rounds; one deliberate regression control outside search','resources':{'wall_seconds':3,'cpu_seconds':1,'address_space_bytes':134217728,'output_bytes':65536},'seed':0,'limitations':['synthetic hand-authored tasks','no statistical generalization claim','deterministic repair menu, no language model','holdout not cryptographically hidden from author','no publication or product activation']}
dev=[{'id':'dev-c','task':'canonical','input':'  HELLO\tWorld  ','expected':['hello','world']},{'id':'dev-u','task':'unique','input':[3,1,3,2],'expected':[3,1,2]},{'id':'dev-m','task':'merge','input':[[0,2],[2,4]],'expected':[[0,4]]}]
for name,data in [('eval.json',cases),('protocol.json',protocol),('dev.json',dev)]:
    (R/'frozen'/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((R/'frozen').glob('*.json'))}
(R/'frozen'/'MANIFEST.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n')
print(hashlib.sha256((R/'frozen'/'MANIFEST.json').read_bytes()).hexdigest())
