// Kotlin fixture: each pattern in signs.json must hit at least one line here.
// C1
val q1 = "SELECT DISTINCT ON (id) * FROM events"
val q2 = "SELECT * FROM events ORDER BY created_at DESC LIMIT 1"
val latest = latestOfType(events, "attempt_completed")
val j = json_extract(data, "$.status")
for (e in range events) { }
if (events.any { it.type == "attempt_completed" }) { }

// C2
val status = firstOrNull() ?: Status.NOT_STARTED
val s2 = x ?: return "not_started"
when (x) { null -> Status.NOT_STARTED }
if (x?.status?.isX != true) return
if (errors.Is(err, sql.ErrNoRows)) return "not_started"
val q3 = "SELECT EXISTS (SELECT 1 FROM t)"
val q4 = "SELECT coalesce(status, 'not_started') FROM t"

// C3
val q5 = "SELECT * FROM t WHERE EXISTS (SELECT 1 FROM jobs WHERE status = 'active')"

// C4
val q6 = "UPDATE t SET status = 'ready'"
val copy = x.copy(status = Status.READY)
val copy2 = x.copy(state = State.READY)
it[Table.status] = Status.READY
x.SetStatus(Status.READY)
val q7 = "UPDATE t SET is_active = NOT is_active"

// C5
val isReady = status == Status.READY
val canOpen = CanOpen(x)
val q8 = "SELECT * FROM t WHERE status NOT IN ('a','b')"
val q9 = "SELECT * FROM t WHERE status <> 'a'"
val q10 = "SELECT CASE status WHEN 'a' THEN 1 END FROM t"
val q11 = "SELECT * FROM t WHERE payment_status != 'a'"

// C6
if (message.contains("timeout")) code = "timeout"
if (message?.contains("timeout") == true) code = "timeout"
if (e.message.startsWith("ERR_")) code = "err"
if (Regex("timeout").find(message) != null) code = "timeout"

// C7
if (HasPrefix(id, "as-is:")) process()
if (id.startsWith("as-is:")) process()
if (packageId == null) process()

// C8
if (x !is Pallet) buildParcelRoute(x)
if (x.Kind != Kind.Pallet) buildParcelRoute(x)
if (x != Kind.Pallet) buildParcelRoute(x)

// C9
val q12 = "SELECT * FROM t WHERE status IN ('a','b','c')"
val sizes = setOf("a", "b", "c")
val sizes2 = listOf("a", "b", "c")
val sizes3 = inList(listOf("a", "b", "c"))
@SerialName("a")
val q13 = "CHECK (status IN ('a','b'))"
when (x) { "a" -> 1 }
val q14 = "SELECT CASE status WHEN 'a' THEN 1 END"

// C10
throw IllegalStateException("boom")
return Outcome.Err("boom")
return@forEach
parts.map { generate(it) }
parts.forEach { generate(it) }

// C11
@Scheduled(fixedDelay = 1000)
fun sweep() { scope.launch { while (true) { delay(1000) } } }
val p = 'PENDING'
val pr = 'PROCESSING'
val r = 'RUNNING'

// C14
@GetMapping("/drafts")
fun get() = get("/drafts")
fun update() { db.update(x) }
val ins = "INSERT INTO t VALUES (1)"
db.Exec("...")
db.Save(x)
MarkUsed(x)

// C15
catch (_: Exception) { code = "boom" }
runCatching { work() }.getOrElse { "boom" }
@ExceptionHandler
fun handler() = *Fault
fun legacyOrNull() = null

// C16
if (status == Status.X) { status = Status.Y }
when (status) { Status.X -> status = Status.Y }
if (s.Status != Status.X) { return nil }
val q15 = "UPDATE t SET status = 'y' WHERE status = 'x'"
val rows = RowsAffected
db.execute("...")

// C17
val canCancel = status == "submitted"
val canEdit = status == "draft"
val canRetry = status == "failed"
val isEditable = status == "draft"
val showRetry = status == "failed"
val disabled = status == "submitted"
if (attempts < 3) pass
if (role == "admin") pass
