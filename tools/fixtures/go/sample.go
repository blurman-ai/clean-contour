package sample

// Go fixture: each pattern in signs.json must hit at least one line here.
// C1
var q1 = "SELECT DISTINCT ON (id) * FROM events"
var q2 = "SELECT * FROM events ORDER BY created_at DESC LIMIT 1"
var latest = latestOfType(events, "attempt_completed")
var j = json_extract(data, "$.status")
for _, e := range events { _ = e }
if events.any { }

// C2
if errors.Is(err, sql.ErrNoRows) { return "not_started" }
var q3 = "SELECT EXISTS (SELECT 1 FROM t)"
var q4 = "SELECT coalesce(status, 'not_started') FROM t"
var q5 = "SELECT COUNT(*) > 0 FROM t"

// C3
var q6 = "SELECT * FROM t WHERE EXISTS (SELECT 1 FROM jobs WHERE status = 'active')"

// C4
var q7 = "UPDATE t SET status = 'ready'"
inv.Status = StatusReady
inv.SetStatus(StatusReady)
var q8 = "UPDATE t SET is_active = NOT is_active"

// C5
var isReady = status == StatusReady
var canOpen = CanOpen(x)
var q9 = "SELECT * FROM t WHERE status NOT IN ('a','b')"
var q10 = "SELECT * FROM t WHERE status <> 'a'"
var q11 = "SELECT CASE status WHEN 'a' THEN 1 END FROM t"
var q12 = "SELECT * FROM t WHERE payment_status != 'a'"

// C6
if strings.Contains(err.Error(), "timeout") { code = "timeout" }
if err.Error() == "boom" { code = "boom" }
if MatchString("timeout", err.Error()) { code = "timeout" }

// C7
if HasPrefix(id, "as-is:") { process() }
if packageId == nil { process() }

// C8
if x.Kind != Kind.Pallet { buildParcelRoute(x) }
if x != Kind.Pallet { buildParcelRoute(x) }

// C9
var q13 = "SELECT * FROM t WHERE status IN ('a','b','c')"
var sizes = []string{"a", "b", "c"}
switch s { case "a", "b": }
var q14 = "SELECT CASE status WHEN 'a' THEN 1 END"

// C10
return err
for _, p := range parts { _ = p }
var g errgroup.Group

// C11
t := time.NewTicker(time.Second)
for { <-t.C }
var p = 'PENDING'
var pr = 'PROCESSING'
var r = 'RUNNING'

// C14
r.GET("/drafts", handler)
r.Get("/drafts", handler)
http.MethodGet
db.update(x)
var ins = "INSERT INTO t VALUES (1)"
db.Exec("...")
db.Save(x)
MarkUsed(x)

// C15
http.Error(w, err.Error(), 500)
c.JSON(500, gin.H{"error": err.Error()})

// C16
if s.Status != StatusX { return nil }
var q15 = "UPDATE t SET status = 'y' WHERE status = 'x'"
var rows = RowsAffected
db.execute("...")

// C17
var canCancel = status == "submitted"
var canEdit = status == "draft"
var canRetry = status == "failed"
var isEditable = status == "draft"
var showRetry = status == "failed"
var disabled = status == "submitted"
if attempts < 3 { }
if role == "admin" { }
// C11
var t *time.Ticker
