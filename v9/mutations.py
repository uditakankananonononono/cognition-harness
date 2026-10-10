"""AST-level primitive program transforms for the v9 inventive proposer.

Each transform is a small local edit; the search space is the composition
closure of these primitives, far beyond exact enumeration at survey scale.
No learned model, no novel-operator invention claim: the grammar is
builder-chosen and every applied edit is recorded in the receipts.
"""
import ast, hashlib

INT_SET = (-2, -1, 0, 1, 2, 3)
CMP_OPS = (ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE)
ARITH_OPS = (ast.Add, ast.Sub, ast.Mult, ast.FloorDiv, ast.Mod)
CALL_FUNCS = ('min', 'max', 'abs', 'len', 'sum', 'sorted')

def sha(data):
    return hashlib.sha256(data).hexdigest()

def _enclosing_fn(parents, node):
    while node in parents:
        node = parents[node]
        if isinstance(node, ast.FunctionDef):
            return node
    return None

def _scope_names(fn):
    names = {a.arg for a in fn.args.args}
    for n in ast.walk(fn):
        if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store):
            names.add(n.id)
    return sorted(names)

def _primitives_at(node, i, parents):
    if isinstance(node, ast.Constant) and isinstance(node.value, int) and not isinstance(node.value, bool):
        for v in INT_SET:
            if v != node.value:
                yield {'kind': 'const', 'old': node.value, 'new': v, 'site': i}
    elif isinstance(node, ast.Compare) and len(node.ops) == 1:
        for op in CMP_OPS:
            if not isinstance(node.ops[0], op):
                yield {'kind': 'cmp', 'old': type(node.ops[0]).__name__, 'new': op.__name__, 'site': i}
    elif isinstance(node, ast.BinOp) and type(node.op) in ARITH_OPS:
        for op in ARITH_OPS:
            if not isinstance(node.op, op):
                yield {'kind': 'arith', 'old': type(node.op).__name__, 'new': op.__name__, 'site': i}
    elif isinstance(node, ast.BoolOp):
        other = ast.Or if isinstance(node.op, ast.And) else ast.And
        yield {'kind': 'bool', 'old': type(node.op).__name__, 'new': other.__name__, 'site': i}
    elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        if node.func.id in CALL_FUNCS:
            for f in CALL_FUNCS:
                if f != node.func.id:
                    yield {'kind': 'call', 'old': node.func.id, 'new': f, 'site': i}
        if len(node.args) >= 2:
            yield {'kind': 'argswap', 'old': 'arg0,arg1', 'new': 'arg1,arg0', 'site': i}
    elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
        fn = _enclosing_fn(parents, node)
        if fn is not None:
            for alt in _scope_names(fn):
                if alt != node.id:
                    yield {'kind': 'name', 'old': node.id, 'new': alt, 'site': i}

def _macro_at(m, node, i, parents):
    kind, old, new = m
    if kind == 'call' and isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == old:
        return {'kind': 'call', 'old': old, 'new': new, 'site': i}
    if kind == 'const' and isinstance(node, ast.Constant) and node.value == old and not isinstance(node.value, bool):
        return {'kind': 'const', 'old': old, 'new': new, 'site': i}
    if kind == 'cmp' and isinstance(node, ast.Compare) and len(node.ops) == 1 and type(node.ops[0]).__name__ == old:
        return {'kind': 'cmp', 'old': old, 'new': new, 'site': i}
    if kind == 'arith' and isinstance(node, ast.BinOp) and type(node.op).__name__ == old:
        return {'kind': 'arith', 'old': old, 'new': new, 'site': i}
    if kind == 'bool' and isinstance(node, ast.BoolOp) and type(node.op).__name__ == old:
        return {'kind': 'bool', 'old': old, 'new': new, 'site': i}
    if kind == 'name' and isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load) and node.id == old:
        fn = _enclosing_fn(parents, node)
        if fn is not None and new in _scope_names(fn):
            return {'kind': 'name', 'old': old, 'new': new, 'site': i}
    return None

def _apply(tree, desc):
    node = list(ast.walk(tree))[desc['site']]
    k = desc['kind']
    if k == 'const':
        node.value = desc['new']
    elif k == 'cmp':
        node.ops = [getattr(ast, desc['new'])()]
    elif k == 'arith':
        node.op = getattr(ast, desc['new'])()
    elif k == 'bool':
        node.op = getattr(ast, desc['new'])()
    elif k == 'call':
        node.func.id = desc['new']
    elif k == 'name':
        node.id = desc['new']
    elif k == 'argswap':
        node.args[0], node.args[1] = node.args[1], node.args[0]
    else:
        raise ValueError(k)

def extract_macro(desc):
    if desc['kind'] == 'argswap':
        return None
    return (desc['kind'], desc['old'], desc['new'])

def expand(source, macros=None):
    """All deduplicated one-step children of source: macro applications first
    (when given), then the full primitive enumeration. Deterministic order."""
    tree = ast.parse(source)
    nodes = list(ast.walk(tree))
    parents = {c: n for n in ast.walk(tree) for c in ast.iter_child_nodes(n)}
    out = []
    seen = {sha(source.encode())}
    def emit(desc):
        t = ast.parse(source)
        _apply(t, desc)
        ast.fix_missing_locations(t)
        child = ast.unparse(t)
        h = sha(child.encode())
        if h in seen:
            return
        seen.add(h)
        out.append((dict(desc), child))
    if macros:
        for m in macros:
            for i, node in enumerate(nodes):
                d = _macro_at(m, node, i, parents)
                if d:
                    emit(d)
    for i, node in enumerate(nodes):
        for d in _primitives_at(node, i, parents):
            emit(d)
    return out
