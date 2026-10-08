"""Frozen-method proposal. General solve interface, no evaluator instances."""
import ast,json
from pathlib import Path
from semantics import spec_ok,records_ok,Failure,finish,solve as interpreter
SOURCE=Path(__file__).with_name('semantics.py').read_text()

def a0(spec,records):
    if not records_ok(records):return {'status':'error','code':'invalid_records'}
    try:return finish(records)
    except Failure as e:return {'status':'error','code':str(e)}

def a1(spec,records,variant):return interpreter(spec,records,variant)

def generate(spec):
    """Compose trusted AST and emit standalone source, not user Python text."""
    spec_ok(spec)
    tree=ast.parse(SOURCE)
    tree.body=[n for n in tree.body if not (isinstance(n,ast.FunctionDef)and n.name=='solve')]
    statements=ast.parse('if not records_ok(rows):\n fail("invalid_records")').body
    for s in spec['steps']:
        # Literal task spec is encoded as an AST Constant/container, never executable syntax.
        expression=ast.Call(func=ast.Name(id=s['op']+'_op',ctx=ast.Load()),args=[ast.Name(id='rows',ctx=ast.Load()),ast.parse(repr(s),mode='eval').body,ast.Constant(value=0)],keywords=[])
        statements.append(ast.Assign(targets=[ast.Name(id='rows',ctx=ast.Store())],value=expression))
        statements+=ast.parse('finish(rows)').body
    statements+=ast.parse('return finish(rows)').body
    function=ast.parse('def generated(rows):\n pass').body[0]
    function.body=[ast.Try(body=statements,handlers=[ast.ExceptHandler(type=ast.Name(id='Failure',ctx=ast.Load()),name='e',body=ast.parse('return {"status":"error","code":str(e)}').body)],orelse=[],finalbody=[])]
    tree.body.append(function)
    return ast.unparse(ast.fix_missing_locations(tree))+'\n'

def a2(spec,records):
    try:source=generate(spec)
    except Failure as e:return {'status':'error','code':str(e)}
    namespace={};exec(compile(source,'<trusted-generated>','exec'),namespace)
    return namespace['generated'](records)
