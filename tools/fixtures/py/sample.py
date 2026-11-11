# Python fixture: each pattern in signs.json must hit at least one line here.
# C1
def attempt_finished_from_events(events):
    return any(e.type == "attempt_completed" for e in events)

def compute_state_from_events(events):
    return reduce(lambda a, e: a, events, None)

def fold_events(events):
    return fold(lambda a, e: a, events, None)

def other(events):
    return any(e.type != "attempt_completed" for e in events)

# C2
def check(rows):
    if not rows:
        return "not_started"
    if session.query(Answer).filter_by(step_id=step.id).first() is None:
        step_state = "not_started"
    if rows.count() == 0:
        return "empty"
    if exists(rows):
        return "ok"
    if len(rows) == 0:
        return "empty"

# C3
def blueprint_status(bp, job):
    return "failed" if job.status == "failed" else "generating"

def other_status(bp):
    return bp.state != "ready"

def state_eq(bp):
    return bp.state == "ready"

def status_ne(bp):
    return bp.status != "ready"

# C4
version.processing_status = "ready"
version.status = "ready"
version.state = "ready"
version.stage = "ready"
version.phase = "ready"
version.outcome = "ready"
update(Version).values(status="ready")

# C5
def get_status(): pass
def get_state(): pass
def is_attempt_ready(): pass
def get_verdict(): pass
def get_outcome(): pass

# C6
if "timeout" in str(exc).lower():
    code = "provider_timeout"
if "timeout" in message:
    code = "timeout"
code = exc.text.removeprefix("ERR_")
code = exc.text.startswith("ERR_")

# C7
if label == "Foo":
    pass
if id.startswith("as-is:"):
    pass
if unit === "steps":
    pass
if columns.index("name"):
    pass

# C8
if not is_pallet(order):
    build_parcel_route(order)
if order.kind != Kind.PALLET:
    pass
if x !== y:
    pass

# C9
SIZES = set(["a", "b", "c"])
SIZES2 = frozenset(["a", "b", "c"])
SIZES3 = tuple(["a", "b", "c"])
SIZES4 = Literal["a", "b", "c"]
sql = "SELECT * FROM t WHERE status IN ('a','b','c')"

# C10
for section in sections:
    raise RuntimeError("boom")
status = "failed"
for part in parts:
    pass

# C11
status = 'PENDING'
status = 'PROCESSING'
status = 'RUNNING'
status = 'SYNCING'
status = ACTIVE
sql = "INSERT INTO t (status) VALUES (DEFAULT 'PENDING')"
while True:
    pass
attempts = attempts + 1

# C14
@router.get("/drafts")
def list_drafts(db):
    db.commit()
    db.add(x)
    db.update(x)
    db.insert(x)

@app.get("/drafts")
def list_drafts2(db):
    pass

@app.route("/drafts")
def list_drafts3(db):
    pass

# C15
except Exception:
    pass
except ValueError:
    pass
raise HTTPException(status_code=400, detail="boom")

# C16
def set_order_status(order): pass
def transition_order(order): pass
def mark_paid(order):
    if order.status == OrderStatus.STOCK_CONFIRMED:
        order.status = OrderStatus.PAID
def apply_event(order): pass
Model.objects.filter(pk=1, status="x")
session.execute(update(Order).where(Order.status == "x"))
order = Order.get_or_none(id=1)
order = Order.first()

# C17
def can_cancel(order):
    return order.status == "submitted"
def is_editable(order): pass
def show_retry(order): pass
disabled = order.status == "submitted"
if Date.now() < deadline: pass
if attempts < 3: pass
if role === "admin": pass
# C9
TERMINAL = set("done failed".split())
ORDER = tuple("new done".split())
