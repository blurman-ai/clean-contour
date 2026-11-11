# nopCommerce: review of the places flagged by DeepSeek flash

Read on 11 November 2026 (shallow clone of the default branch at cc26104): DeepSeek flash gave a verdict on every candidate found by the C# search signs, and Sonnet read what it flagged, with whole files and callers. Not reproduced on a running instance.

Paths are relative to the repository root. The list has 102 places (C17: 1, C4: 12, C6: 2, C15: 87).
For C15 the "dirty" criterion is narrowed below to cases where the user or operator loses the reason for a refusal, receives the internal text of an exception, or is left in an undefined state. In a project without a contract of refusal codes, the check "code is not from the enumeration" fires on every catch and distinguishes nothing.

## Confirmed, by descending consequence

| Card | File:line | Verdict | Where the value comes from and what the user sees |
|---|---|---|---|
| C15 (+C10) | src/Libraries/Nop.Services/Tax/TaxService.cs:276, :753; Nop.Services/Orders/OrderTotalCalculationService.cs:1309; Plugins/Nop.Plugin.Tax.Avalara/Services/AvalaraTaxManager.cs:190 | dirty | When Avalara fails, the provider returns `Errors`, and `TaxService` keeps the rate at 0 and writes the error to the log only if the `LogErrors` setting is on (a `bool` field with no default in the schema). The total uses `TaxTotal ?? 0`, so the customer places the order without tax, the store under-collects tax, and the operator sees nothing. |
| C15 | src/Libraries/Nop.Services/Orders/OrderProcessingService.cs:1663 (PlaceOrderAsync), 1612-1651; CheckoutController.cs:1332, 2072, 2178 | dirty | Payment goes through `GetProcessPaymentResultAsync`; then, without a transaction, come saving the order, moving the cart, the PDF and emails (`SendNotificationsAndSaveNotesAsync`), and the `OrderPlacedEvent` handlers. An exception at any step after the charge becomes `result.AddError(exc.Message)`: the customer sees the raw exception text, and the order is left without `CheckOrderStatus` and `ProcessOrderPaid` (status Pending, no payment email, no reward points or gift cards). There is no state "money charged, order not completed". |
| C4 (+C13) | src/Plugins/Nop.Plugin.Payments.PayPalCommerce/Services/PayPalCommerceServiceManager.cs:3209, 3259 | dirty | A PENDING webhook from PayPal sets `PaymentStatus = Pending` without checking the current status and saves the order. PayPal does not guarantee delivery order, so a late PENDING after COMPLETED returns a paid (or refunded) order to "Pending payment", and a repeated COMPLETED may never arrive. |
| C17 | src/Presentation/Nop.Web/Factories/OrderModelFactory.cs:576 and Controllers/OrderController.cs:217-240 | dirty | The "Cancel" button is shown only when `PaymentStatus == Pending`, but the `CancelOrder` action (a GET link) checks `CanCancelOrder`, which forbids only an already cancelled order. With the setting on, a customer can cancel a paid or shipped order by a direct URL: no refund is made, reward points are returned, gift cards are deactivated. |
| C15 | src/Libraries/Nop.Services/Orders/OrderProcessingService.cs:2667 (RefundAsync), 2535 (CaptureAsync), 3039 (VoidAsync) | dirty | The provider has already returned the money; then `UpdateOrderAsync`, events and emails run in the same try. A failure after the success gives the operator "Error: … Full exception: stack trace", and the order status may stay "Paid" although the refund was made (so the refund can be repeated). `PaymentStatus` is taken from the plugin's `result.NewPaymentStatus` with no check of the transition. |
| C15 | src/Plugins/Nop.Plugin.Misc.PunchOut/Services/PunchOutService.cs:431 | dirty | Any exception during session setup (including a failure on our side) goes to the client's procurement system as 400 "Bad Request" with the exception text. The system treats the request as invalid and does not retry. |
| C6 | src/Libraries/Nop.Data/DataProviders/PostgreSqlDataProvider.cs:280, 306 | dirty | The choice "insert without identity" is made by `ex.Message.StartsWith("Identity field must be defined for")`. After a linq2db update with a different message, these inserts will start failing. |
| C4 | src/Libraries/Nop.Services/Orders/OrderTotalCalculationService.cs:547 | dirty | When an administrator edits an order, `ShippingStatus` is recomputed from its own previous value (Shipped and Delivered become PartiallyShipped), while `OrderStatus` stays Complete. The operator sees a fully delivered order as partially shipped. |
| C4 | src/Libraries/Nop.Services/Orders/OrderProcessingService.cs:2667 | dirty | See the refund row above: the status is written from the plugin's response without a transition table. |
| C4 | src/Libraries/Nop.Services/Orders/OrderProcessingService.cs:2763, 2953 | dirty (low harm) | `RefundOfflineAsync` and `PartiallyRefundOfflineAsync` write `PaymentStatus` themselves. The guard is the `CanRefundOffline` predicate in the same method, not a transition table. User-visible behaviour does not differ. |
| C4 | src/Libraries/Nop.Services/ExportImport/ImportManager.cs:3395, 3398, 3401 | dirty (low harm) | Order import writes the order, payment and shipping statuses from the file without events (stock, points, gift cards and emails do not fire). For migrating history this is expected; for a paid order from a file, stock is not decremented. |
| C4 | src/Plugins/Nop.Plugin.Misc.RFQ/Services/EventConsumer.cs:222; RfqService.cs:286, 841 | dirty (low harm) | `ChangeAndLogQuoteStatusAsync` exists, but the event handler, the expiry check and quote deletion write `Status` around it (no log note, no transition check). The status "Expired" is written when a quote is read. |
| C6 | src/Presentation/Nop.Web.Framework/Factories/TranslationModelFactory.cs:156 | dirty (low harm) | Stopping the translation is decided by the text of the DeepL error. If the text changes, the administrator gets hundreds of identical errors instead of one. |
| C15 | src/Libraries/Nop.Services/Html/HtmlFormatter.cs:64; Plugins/Nop.Plugin.Misc.Forums/Services/ForumService.cs:122 | dirty (low harm) | When formatting fails, the page shows "Text cannot be formatted. Error: {exception text}" instead of the message text, so the reason reaches the visitor. |
| C15 | src/Presentation/Nop.Web/Areas/Admin/Controllers/DownloadController.cs:144 | dirty (low harm) | Any failure to save a file (permissions, database, size) is shown as the single line "File cannot be saved" (in English, not localized); the reason is only in the log. |
| C15 | src/Presentation/Nop.Web/Controllers/CustomerController.cs:976, 1712, 2123; CheckoutController.cs:304, 1355, 1665 (and the same kind: 1784, 1872, 1944, 2122) | dirty (medium harm) | Public actions (password change, profile, avatar, address, checkout) show the customer `exc.Message` as is, including database and library texts. |
| C15 | src/Plugins/Nop.Plugin.Shipping.UPS/Services/UPSService.cs:835 | dirty (medium harm) | When UPS fails, an empty list of shipping methods is returned together with an error text that is shown only in the log. The customer sees no shipping options and no reason. |

## False positives, by reason

| Reason | Card | File:line | Where the value comes from and what the user sees |
|---|---|---|---|
| Initial state when an entity is created | C4 | OrderProcessingService.cs:475; RfqService.cs:401 | `ShippingStatus` in the container of the order being created and `Submitted` on a newly created request are set at creation; they do not change a lifecycle. |
| Not a lifecycle: result of the last check | C4 | CheckoutController.cs:255 | `VatNumberStatus` is the result of the last call to the VAT check service; there are no transitions. The customer sees a warning about the number. |
| Reason shown with its own text, single case | C15 | CheckoutController.cs:1557, 1982 (messages with a specific reason inside try); OrderController.cs (Admin):2231, 2348; VendorController.cs:328; CommonController.cs:300 | "Enter shipped date", "Enter delivery date", the vendor image error: each text matches a single reason and reaches the operator. |
| Operator error with the real exception text (the project has no codes) | C15 | OrderController.cs (Admin):909; CustomerController.cs (Admin):582; InstallController.cs:344; BrevoManager.cs:105 | The operator gets the exception text and does not lose the reason. There is neither an enumeration of codes nor a client table, so the card applies only formally. |
| Not a refusal path | C15 | CustomerController.cs:1048, 1522; InstallValidator.cs:13 | A list of attribute warnings, a start of action, a FluentValidation validator: each rule has its own localized text and there is no catch. |

Not opened (only the DeepSeek flash description template was read; no verdict given): C15 — the remaining Brevo places (338-1464), Forums (BoardsController 512, 648, 803, 911; ForumModelFactory 847), Zettle 108, PayPal 194, Twilio 67, ChatGptShopping 188, AI service 206/318, Admin controllers Campaign, CheckoutAttribute, Customer (769-1556), ElFinder, EmailAccount, MessageTemplate, Product (1545-4240), Setting, CommonModelFactory 1061, Customer (public) 1778, 2329, PrivateMessages 276, Order (Admin) 2200, Checkout 1784, 1872, 1944 (same template as the read 304 and 2122), OrderProcessingService 2876, 3039 (same template as 2689), Order (Admin) 2200, 2290.

## Count

Opened with context: 44 of 102: C17 — 1, C4 — 12, C6 — 2, C15 — 29 (a sample; 58 C15 places were not opened, listed above).
Confirmed: 28 (C17 — 1, C4 — 9, C6 — 2, C15 — 16). False positives: 16 (C4 — 3, C15 — 13). The places 3039, 1784, 1872, 1944 in the confirmed table follow the template of the neighbouring places that were read (2689, the 1665 group) and are not included in the count.
DeepSeek flash was wrong most often on C15 (13 false positives of 29 opened; most of them were marked "unclear") and on C4 for entity creation and for values that are not a lifecycle (3 of 12). No errors were found on C6 and C17.
DeepSeek flash did not flag the heaviest places: the zero tax on provider failure was found through adjacent code (`TaxService`), and the failure after the charge and the PayPal webhook were flagged only as "a line without a code" and "an assignment without a check", with no consequences for the order noted.

## Three heaviest: reproduction and minimal fix

### 1. Zero tax when the provider fails (C15)

1. Install the Avalara plugin with a wrong key or cut the network to Avalara; `TaxSettings.LogErrors` is `false` by default.
2. Add a taxable product to the cart and go to order confirmation: the total has no tax.
3. Place the order: the tax in the order is 0, nothing in the log.
4. Minimal fix: in `TaxService.GetTaxTotalAsync` and `GetTaxRateAsync`, on `!Success` throw a refusal with a reason (checkout does not continue) instead of substituting 0; in `OrderTotalCalculationService.cs:1309` do not take `?? decimal.Zero` on an unsuccessful result.

### 2. Failure after the charge at checkout (C15)

1. Turn on `AttachPdfInvoiceToOrderPlacedEmail` and make the PDF directory not writable (or add an `OrderPlacedEvent` subscriber that throws).
2. Place an order with a payment method that charges immediately.
3. The money is charged, the order is created, the cart is empty, and the customer sees the exception text on the confirmation page; the order is in status Pending and there is no payment email.
4. Minimal fix: in `OrderProcessingService.cs`, after `ProcessPaymentAsync` succeeds, keep an order state "paid, post-processing not completed" with a retry of the step, and when `result.PlacedOrder != null` show the customer the order page, not the exception text.

### 3. Late PayPal webhook (C4)

1. Pay for an order through PayPal Commerce: a COMPLETED capture arrives and the order becomes "Paid".
2. Send a late PENDING capture event with the same `custom_id` to the webhook.
3. `PayPalCommerceServiceManager.cs:3259` sets `Pending`, and `CheckOrderStatusAsync` saves the order: the admin area shows the paid order as "Pending payment".
4. Minimal fix: before writing, check a `CanMarkOrderAsPaid`-like condition (do not change the order status from Paid, Refunded or Voided to Pending); the same for the authorization branch at 3209.

Fourth by severity: C17, cancelling a paid order by a direct link (`CanCancelOrder` in `OrderProcessingService.cs:2375` does not know about `PaymentStatus`; fix: move the condition `PaymentStatus == Pending` from `OrderModelFactory.cs:576` into `CanCancelOrder`, and give the model the result of that function).
