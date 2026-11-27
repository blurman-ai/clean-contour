"""Structural prefilter for C21 (state derived from another field of the same entity).

Finds functions that RETURN lifecycle values while their conditions read anything
besides the state field (read-side), and functions that WRITE a lifecycle value
through a writer call under a condition influenced by a non-state field (write-side).
Field names do not matter: the sign is the shape of the decision, not a vocabulary.

    python3 tools/structural_scan.py --selftest     control cases, no network
    python3 tools/structural_scan.py <path> [...]   scan trees, JSONL to stdout
"""
import ast, json, re, sys
from pathlib import Path

LIFECYCLE = {"ready","completed","complete","failed","done","success","succeeded","generating",
             "processing","pending","finished","running","queued","published","cancelled","canceled",
             "in_progress","draft","active","archived","partial","stalled","interrupted","validated",
             "skipped","timeout","scheduled","paused","retrying","crashed","submitted","accepted",
             "rejected","expired","extracted","quarantined","no_text","lost","waiting","review","current","stopped"}
LIFENAME = re.compile(r'READY|COMPLET|FAIL|DONE|SUCCESS|GENERAT|PROCESS|PENDING|FINISH|RUNNING|QUEU|PUBLISH|'
                      r'CANCEL|DRAFT|ACTIVE|ARCHIV|PARTIAL|STALL|INTERRUPT|VALID|SKIP|TIMEOUT|SCHEDULE|PAUSE|'
                      r'RETRY|CRASH|SUBMIT|ACCEPT|REJECT|EXPIR|EXTRACT|QUARANTIN|LOST|WAITING|REVIEW')
CTOR = re.compile(r'^(Completed|Failed|Running|Pending|Cancelled|Canceled|Crashed|Scheduled|Paused|'
                  r'Retrying|Ready|Finished|Succeeded|Success|Done|Skipped)$')
STATENAMES = {'state', 'status', 'lifecycle', 'stage', 'phase', 'step'}
SKIP = re.compile(r'(\.venv|venv|node_modules|\.git|__pycache__|dist|build|\.mypy_cache|\.pytest_cache|'
                  r'htmlcov|_migrations|migrations|alembic|\.claude/worktrees)')
NOISE_NAMES = {'self','cls','True','False','None','len','str','int','isinstance','type','enumerate','range','print'}

def field_refs(node):
    """Field references in an expression: attributes, subscript keys, .get() keys, plain names."""
    out = []
    for n in ast.walk(node):
        if isinstance(n, ast.Attribute):
            out.append(n.attr)
        elif isinstance(n, ast.Subscript) and isinstance(n.slice, ast.Constant) and isinstance(n.slice.value, str):
            out.append(n.slice.value)
        elif isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == 'get':
            if n.args and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str):
                out.append(n.args[0].value)
        elif isinstance(n, ast.Name):
            out.append(n.id)
    return out

def attr_chain(v):
    """All attribute names in a dotted chain, so SectionPodcastState.FAILED.value yields FAILED too."""
    names = []
    while isinstance(v, ast.Attribute):
        names.append(v.attr)
        v = v.value
    if isinstance(v, ast.Name):
        names.append(v.id)
    return names

def lifecycle_returns(fn):
    rets = []
    for n in ast.walk(fn):
        if not isinstance(n, ast.Return) or n.value is None:
            continue
        v = n.value
        vals = [v]
        if isinstance(v, ast.IfExp):
            vals = [v.body, v.orelse]
        for x in vals:
            if isinstance(x, ast.Constant) and isinstance(x.value, str) and x.value.lower() in LIFECYCLE:
                rets.append((n.lineno, x.value))
            elif isinstance(x, ast.Attribute):
                for a in attr_chain(x):
                    if LIFENAME.search(a):
                        rets.append((n.lineno, 'enum:' + a)); break
            elif isinstance(x, ast.Call):
                f = x.func
                nm = f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else '')
                if CTOR.match(nm or ''):
                    rets.append((n.lineno, 'ctor:' + nm))
    return rets

def assigns_state(fn):
    for n in ast.walk(fn):
        if isinstance(n, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            tgts = n.targets if isinstance(n, ast.Assign) else [n.target]
            for t in tgts:
                if isinstance(t, ast.Attribute) and t.attr in {'state', 'status'}:
                    return True
                if isinstance(t, ast.Subscript) and isinstance(t.slice, ast.Constant) and t.slice.value in {'state', 'status'}:
                    return True
    return False

def nonstate_inputs(fn, include_returns):
    other = set()
    for n in ast.walk(fn):
        exprs = []
        if isinstance(n, (ast.If, ast.While)):
            exprs.append(n.test)
        if isinstance(n, ast.BoolOp):
            exprs.append(n)
        if include_returns and isinstance(n, ast.Return) and n.value is not None:
            exprs.append(n.value)
        for e in exprs:
            for ref in field_refs(e):
                if ref.lower() in STATENAMES or ref in NOISE_NAMES or ref.startswith('__'):
                    continue
                other.add(ref)
    return sorted(other)

def scan_file(path):
    try:
        tree = ast.parse(Path(path).read_text(encoding='utf-8', errors='replace'))
    except (SyntaxError, OSError, ValueError):
        return []
    rows = []
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        # read-side: returns lifecycle values, conditions read non-state fields, not a writer
        rets = lifecycle_returns(fn)
        if rets and not assigns_state(fn):
            other = nonstate_inputs(fn, include_returns=True)
            if other:
                rows.append({'kind': 'read-side', 'line': fn.lineno, 'func': fn.name,
                             'rets': rets[:3], 'other': other[:10]})
        # write-side: a call passing a lifecycle literal/enum under a condition on non-state fields
        writes = []
        for n in ast.walk(fn):
            if isinstance(n, ast.Call):
                for a in list(n.args) + [k.value for k in n.keywords]:
                    if isinstance(a, ast.Constant) and isinstance(a.value, str) and a.value.lower() in LIFECYCLE:
                        writes.append((n.lineno, 'write:' + a.value))
                    elif isinstance(a, ast.Name) and LIFENAME.search(a.id) and a.id.upper() == a.id:
                        writes.append((n.lineno, 'write-const:' + a.id))
                    elif isinstance(a, ast.Attribute):
                        for x in attr_chain(a):
                            if LIFENAME.search(x):
                                writes.append((n.lineno, 'write-enum:' + x)); break
        if writes:
            other = nonstate_inputs(fn, include_returns=False)
            if other:
                rows.append({'kind': 'write-side', 'line': fn.lineno, 'func': fn.name,
                             'rets': writes[:3], 'other': other[:10]})
    return rows

def scan_tree(root):
    root = Path(root)
    for p in sorted(root.rglob('*.py')):
        if SKIP.search(str(p)):
            continue
        for r in scan_file(p):
            yield {'file': str(p), **r}

SELFTEST_CASES = [
    # (source, expect_func, expect_kind or None)
    ('def engine_payload_state(payload):\n    state = payload["state"]\n    if state == "ready" or payload.get("audio_path"):\n        return "ready"\n    return "generating"\n', 'engine_payload_state', 'read-side'),
    ('def stage(p):\n    if p.has_voiceover:\n        return StageStatus.DONE\n    return StageStatus.WAITING\n', 'stage', 'read-side'),
    ('def enumvalue(p):\n    if p.has_master:\n        return Status.FAILED.value\n    return Status.READY.value\n', 'enumvalue', 'read-side'),
    ('def parser_status(src):\n    if src.extraction_error in Q:\n        return "quarantined"\n    return src.extraction_error or "failed"\n', 'parser_status', 'read-side'),
    ('async def repair(rows, w):\n    for row in rows:\n        if not Path(row.audio_path).exists():\n            await w(row, "failed")\n', 'repair', 'write-side'),
    ('def writer(row, state, path):\n    row.state = state\n    row.audio_path = path\n', None, None),  # writer: assigns state -> excluded
    ('def passthrough(payload):\n    return payload["state"]\n', None, None),  # clean: no lifecycle literal
    ('def pure(s):\n    if s == "x":\n        return "unknown_literal"\n    return "also_unknown"\n', None, None),  # not lifecycle vocabulary
]

def selftest():
    ok = 0
    for i, (src, func, kind) in enumerate(SELFTEST_CASES):
        with open('/tmp/_c21_selftest.py', 'w') as f:
            f.write(src)
        rows = scan_file('/tmp/_c21_selftest.py')
        if func is None:
            passed = not rows
        else:
            passed = any(r['func'] == func and r['kind'] == kind for r in rows)
        ok += passed
        print(('ok  ' if passed else 'FAIL') + f' case {i}: expect {func}/{kind}, got {[(r["func"], r["kind"]) for r in rows]}')
    print(f'{ok}/{len(SELFTEST_CASES)}')
    return 0 if ok == len(SELFTEST_CASES) else 1

if __name__ == '__main__':
    if '--selftest' in sys.argv:
        sys.exit(selftest())
    for root in sys.argv[1:]:
        for row in scan_tree(root):
            print(json.dumps(row, ensure_ascii=False))
