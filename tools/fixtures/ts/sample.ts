// TypeScript fixture: each pattern in signs.json must hit at least one line here.
// C1
const finished = events.some(e => e.type === "attempt_completed");
const notFinished = events.some(e => e.type !== "attempt_completed");
function computeStateFromEvents(events) { return events.reduce((a, e) => a, null); }
function attempt_finished_from_events(events) { return fold(events); }

// C2
if (!rows.length) return "not_started";
if (rows.first() === null) return "not_started";
if (rows.count() === 0) return "empty";
if (rows.length === 0) return "empty";

// C3
const bpStatus = job.status === "failed" ? "failed" : "generating";
const bpState = job.state === "failed";
const bpStatusNe = job.status !== "failed";
const bpStateNe = job.state !== "failed";

// C4
order.status = "ready";
order.state = "ready";
order.stage = "ready";
order.phase = "ready";
order.outcome = "ready";

// C5
const status = order.status;
const state = order.state;
const isReady = order.status === "ready";
const verdict = order.verdict;
const outcome = order.outcome;

// C6
if (message.includes("timeout")) code = "provider_timeout";
if (message.match(/timeout/)) code = "timeout";
if (/timeout/.test(message)) code = "timeout";
if (message.startsWith("ERR_")) code = "err";

// C7
if (label === "Foo") pass;
if (id.startsWith("as-is:")) process();
if (unit === "steps") pass;
if (label.includes("x")) pass;
if (columns.indexOf("name")) pass;

// C8
if (!isPallet(order)) buildParcelRoute(order);
if (order.kind != Kind.PALLET) pass;
if (x !== y) pass;

// C9
const sizes = new Set(["a", "b", "c"]);
const arr = ["a", "b", "c"];
switch (s) { case "a": case "b": break; }

// C10
await Promise.all(parts.map(p => generate(p)));
throw new Error("boom");
status = "failed";

// C11
status = 'PENDING';
status = 'PROCESSING';
status = 'RUNNING';
status = 'SYNCING';
status = ACTIVE;
setInterval(() => {}, 1000);
setTimeout(() => {}, 1000);

// C12
const [phase, setPhase] = useState("idle");
useEffect(() => { setPhase("failed"); }, []);
setTimeout(() => {}, 1000);
setInterval(() => {}, 1000);
localStorage.getItem("x");
if (deal.status === "failed") pass;
if (parts.every(p => p.done)) pass;
if (parts.some(p => p.done)) pass;
if (Date.now() > deadline) pass;
if (new Date() > deadline) pass;
el.innerHTML = "x";
el.value = "x";

// C13
prefill(form, data);
seed(form, data);
applyResponse(form, data);
onSuccess(data);
fetch(url).then(r => r.json());

// C14
router.get("/drafts", handler);
db.commit();
db.add(x);
db.update(x);
db.insert(x);

// C15
catch (e) { notify("boom"); }
onError(() => notify("boom"));
isError && notify("boom");
error && notify("boom");
failed && notify("boom");
const texts: Record<string, string> = {};
switch (code) { case "a": break; }
if (e.code === "a") pass;
fetch(url).catch(() => {});

// C16
order.setStatus("paid");
order.transitionTo("paid");
order.markPaid();
if (order.status === "submitted") pass;

// C17
const canCancel = order.status === "submitted";
const canEdit = order.status === "draft";
const canRetry = order.status === "failed";
const isEditable = order.status === "draft";
const showRetry = order.status === "failed";
const disabled = order.status === "submitted";
if (Date.now() < deadline) pass;
if (attempts < 3) pass;
if (role === "admin") pass;

// C18
fetch("/api/orders");
axios.post("/api/orders", body);
db.query("SELECT id FROM orders WHERE status = 'open'");
nodemailer.createTransport(opts);

// C19
import { Request } from "express";
import { OrderDto } from "../controllers/order";

// C20
const raw = JSON.parse(text);
const title = req.body["title"];
const host = config["host"];

// C21
function resolveRenderStatus(job) { return job.status; }
const implied = job.outputUrl ?? "ready";
const artifact = job.audioPath;

// C22
const r = await fetch("https://api.example.invalid/feed");
const res = axios.get("/drafts");
http.request({ host: "example.invalid" });

// C23
class Invoice {
  get total(): number {
    return fetchTotal(this.id).then((t) => t);
  }
  constructor(private readonly id: string) {
    warmCache(id);
  }
}

// C24
function onPaid(payment: Payment) {
  void receiptMailer.send(payment);
}
  void sendReceipt(payment);
pullFeed(supplier).then(() => {

// C25
const overdue = Date.now() > task.dueAt;
const bucket = Math.random() < 0.5 ? "a" : "b";
const stamped = new Date();

// C26
if (process.env.PAYMENTS_FAST_REFUND === "1") { return 60; }
const host = process.env["PAYMENTS_HOST"];

// C28
const table: Record<string, string> = { not_found: "refusal.notFound" };
const key = t(`error.${code}`);
const generic = "import.failure.generic";
