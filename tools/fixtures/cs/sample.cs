// C# fixture: each pattern in signs.json must hit at least one line here.
// C1
var finished = events.Any(e => e.Type == "attempt_completed");
var latest = events.OrderByDescending(e => e.CreatedAt).FirstOrDefault();
var agg = events.Aggregate((a, e) => a);
await AggregateStreamAsync(stream, id);
var rn = "SELECT ROW_NUMBER() OVER (PARTITION BY id ORDER BY ts) FROM events";
// C2
var order = await db.Orders.FirstOrDefaultAsync(o => o.Id == id);
if (order is null) return OrderStatus.NotStarted;
if (await db.Orders.FirstOrDefaultAsync(o => o.Id == id) is null) return OrderStatus.NotStarted;
var st = order ?? OrderStatus.NotStarted;
if (!await db.Orders.AnyAsync(o => o.Id == id)) return OrderStatus.NotStarted;
var count = await db.Orders.CountAsync() == 0;
var coal = "SELECT COALESCE(status, 'not_started') FROM orders";
// C3
var s3 = job.Status == JobStatus.Failed;
var s3b = Status = run.Run.Status;
// C4
order.Status = OrderStatus.Ready;
var updated = order with { Status = OrderStatus.Draft };
db.Orders.ExecuteUpdateAsync(s => s.SetProperty(x => x.Status, OrderStatus.Done));
var sql4 = "SET status = 'ready'";
var orderStatus = OrderStatus.Draft;
// C6
if (ex.Message.Contains("timeout")) code = "provider_timeout";
if (ex.Message == "boom") code = "boom";
if (ex.ToString().Contains("timeout")) code = "timeout";
if (Regex.IsMatch(ex.Message, "timeout")) code = "timeout";
catch (Exception ex) when (ex.Message.Contains("timeout")) { }
// C7
var eq = string.Equals(label, "Foo", StringComparison.OrdinalIgnoreCase);
if (Id.StartsWith("as-is:")) Process();
if (x.GetType().Name == "Pallet") Process();
if (x.Name == "Pallet ") Process();
// C8
if (x is not Pallet) BuildParcelRoute(x);
if (!(x is Pallet)) BuildParcelRoute(x);
if (x.Kind != Kind.Pallet) BuildParcelRoute(x);
// C9
var sizes = new[] { "a", "b", "c" };
var sql9 = "SELECT * FROM t WHERE status IN ('a','b','c')";
switch (s) { case "a": case "b": break; }
// C10
await Task.WhenAll(parts.Select(p => Generate(p)));
Parallel.ForEach(parts, p => Generate(p));
// C11
order.Status = OrderStatus.Pending;
var retry = Policy.RetryForever();
while (!stoppingToken.IsCancellationRequested) { }
// C12
var timer = new DispatcherTimer();
var storage = ProtectedLocalStorage;
@if (Model.Status == X && Model.Error == null) { }
// C14
[HttpGet]
public IActionResult Get() => Ok();
app.MapGet("/drafts", () => Ok());
// C15
catch (Exception ex) { return BadRequest("boom"); }
return Problem(ex.Message);
return StatusCode(500, ex.Message);
await context.Response.WriteAsync(ex.Message);
ModelState.AddModelError("", "boom");
RuleFor(x => x.Name).WithMessage("boom");
// C16
public bool TryMarkPaid(Order o) { if (o.Status == X) { o.Status = Y; } return false; }
db.Orders.ExecuteUpdate(s => s.SetProperty(x => x.Status, OrderStatus.Done));
var sql16 = "UPDATE orders SET status = 'paid' WHERE status = 'confirmed'";
// C17
var tpl = "*ngIf=\"order.status == 'submitted'\"";
var dis = "[disabled]=\"order.status === 'submitted'\"";
var canCancel = order.Status == "submitted";
@if (order.Status != "submitted") { }
var vis = IsVisible = order.Status == "submitted";
// C3, C17
if (shipment.Order.Status == OrderStatus.Paid) { }
<div *ngIf="order.status == 1"></div>
<button [disabled]="order.status"></button>
