# C# batch B: Smartstore and elsa-core

Read on 11 November 2026 (shallow clones of the default branches): DeepSeek flash gave a verdict on every candidate found by the cards' C# search signs, and Sonnet read what it flagged, with whole files and callers. Not reproduced on a running instance.

Scope of reading: all 77 candidates were read. C11, C16, C17, C2, C3 were read in full for every candidate (C3 had none). C4 and C6 were read in full for Smartstore (23 C4) and for all 9 elsa-core C6; of the 27 elsa-core C4, about 20 were read with callers and the remaining ones (experiments, Studio view state, tool result) were judged by the surrounding method only.

"Dirty" means the card's sign is confirmed in code. Severity is stated in the sentence: "harm" means a user or operator sees a wrong status or a stuck object; "low" means the sign is real but the path is a fallback or a rare race.

## Smartstore (shop: orders, payments, shipments)

### Confirmed

| card | file:line | verdict | what comes from where and what the user sees |
|---|---|---|---|
| C16 | src/Smartstore.Core/Platform/DataExchange/Export/DataExporter.cs:1572 | dirty (harm) | After an order export, the admin's "set status to Processing/Complete" option runs one bulk update on every exported order id, with no check of the current status and no count check; with an empty status filter (the default) the export includes cancelled orders, so a cancelled order becomes Complete or Processing, and the bulk update also skips the order note, the customer e-mail and reward-point handling that the normal status change performs. |
| C4 | src/Smartstore.Core/Platform/DataExchange/Export/DataExporter.cs:1572 | dirty (harm) | Same place as the C16 row above: order status written by a bulk update outside the order service. |
| C4 | src/Smartstore.Modules/Smartstore.PayPal/Controllers/PayPalController.cs:924 | dirty (harm) | The PayPal authorization webhook with status denied, expired or pending sets OrderStatus to Pending with no check of the current status; a late, retried or out-of-order event (the handler returns 500 on any exception, so PayPal retries) turns a Processing, Complete or Cancelled order back into Pending, and the admin sees a cancelled order as Pending after its stock was already returned. |
| C4 | src/Smartstore.Modules/Smartstore.PayPal/Controllers/PayPalController.cs:957 | dirty (harm) | The capture webhook with status pending does the same unconditional OrderStatus = Pending; the neighbouring "declined" branch has a comment and a guard that a declined event must not overwrite a captured payment, the pending branch has none. |
| C4 | src/Smartstore.Modules/Smartstore.PayPal/Controllers/PayPalController.cs:987 | dirty (harm) | The capture webhook with status declined guards only Paid, PartiallyRefunded and Refunded; on a cancelled order it writes PaymentStatus = Pending and OrderStatus = Pending (when the "cancel orders for declined payments" setting is off), so a cancelled order reappears as pending. |
| C4 | src/Smartstore.Modules/Smartstore.WebApi/Controllers/Checkout/OrdersController.cs:335 | dirty (harm) | The API action PaymentPending sets PaymentStatus = Pending on any order for a caller with Order.Update permission, including Paid or Refunded orders, with no check and no order note; the shop then shows a paid order as unpaid. |
| C4 | src/Smartstore.Modules/Smartstore.Stripe/Controllers/StripeController.cs:513 | dirty (low) | In the payment_intent.succeeded webhook, when the intent amount differs from the order total, the handler sets PaymentStatus = Pending without looking at the current status; a retried event after the order was marked Paid (or after an admin edited the total) turns it back to Pending. |
| C4 | src/Smartstore.Web/Areas/Admin/Controllers/ReturnCaseController.cs:332 | dirty (harm) | Accept sets ReturnAuthorized and reduces the order item quantity, inventory and totals without checking the current return-case status; a second submit of Accept (or Accept after Reject) reduces the order item again. |

### False

| card | file:line | verdict | what comes from where and what the user sees |
|---|---|---|---|
| C11 | src/Smartstore.Modules/Smartstore.PayPal/Providers/PayPalInvoiceProvider.cs:114 | false | Pending is placed in an in-memory result object before the PayPal call; no order exists yet and the exception goes to the checkout, which shows an error. |
| C11 | src/Smartstore.Modules/Smartstore.PayPal/Providers/PayPalProviderBase.cs:70 | false | Same: Pending is in the result DTO, the catch clause rethrows and the user is sent back to payment selection; nothing is stored. |
| C11 | src/Smartstore.Web/Controllers/ReturnCaseController.cs:125 | false | A new return case is stored as Pending because staff must answer it; the following call is only a notification e-mail, not a wait on which the state depends. |
| C4 | src/Smartstore.Core/Checkout/Orders/Services/OrderProcessingService.Payment.cs:75 | false | Assignment inside the order service itself, after CanCaptureAsync; the service is the de facto writer (no transition table, but guarded). |
| C4 | src/Smartstore.Core/Checkout/Orders/Services/OrderProcessingService.Payment.cs:139 | false | Same: refund inside the service after CanRefundAsync. |
| C4 | src/Smartstore.Core/Checkout/Orders/Services/OrderProcessingService.Payment.cs:222 | false | Same: partial refund after CanPartiallyRefundAsync. |
| C4 | src/Smartstore.Core/Checkout/Orders/Services/OrderProcessingService.Payment.cs:290 | false | Same: void after CanVoidAsync. |
| C4 | src/Smartstore.Core/Checkout/Orders/Services/OrderProcessingService.PlaceOrder.cs:515 | false | Initial ShippingStatus of a new order. |
| C4 | src/Smartstore.Core/Checkout/Orders/Services/OrderProcessingService.PlaceOrder.cs:780 | false | Initial OrderStatus of a new order. |
| C4 | src/Smartstore.Core/Checkout/Orders/Services/OrderProcessingService.PlaceOrder.cs:810 | false | Initial PaymentStatus of a new order from the provider result. |
| C4 | src/Smartstore.Modules/Smartstore.AmazonPay/Providers/AmazonPayProvider.cs:199 | false | Field of the provider's result DTO; the order service writes the order. |
| C4 | src/Smartstore.Modules/Smartstore.AmazonPay/Providers/AmazonPayProvider.cs:279 | false | Same, result DTO. |
| C4 | src/Smartstore.Modules/Smartstore.PayPal/Client/PayPalHttpClient.cs:421 | false | Same, result DTO. |
| C4 | src/Smartstore.Modules/Smartstore.Stripe/Providers/StripeElementsProvider.cs:160 | false | Same, result DTO. |
| C4 | src/Smartstore.Modules/Smartstore.Stripe/Controllers/StripeController.cs:553 | false | Runs only after CanPartiallyRefundOffline passed and the charge is fully refunded; the outcome equals what the service would write. |
| C4 | src/Smartstore.Core/Common/Hooks/SoftDeletableHook.cs:23 | false | The hook is the writer of the Deleted flag; not a lifecycle. |
| C4 | src/Smartstore.Core/Platform/Security/Services/PermissionService.cs:125 | false | EF entity tracking state, not a business state. |
| C4 | src/Smartstore.Core/Platform/Theming/Services/DefaultThemeRegistry.cs:103 | false | In-memory theme descriptor flag recomputed at load. |
| C4 | src/Smartstore.Core/Platform/Theming/Services/DefaultThemeRegistry.cs:171 | false | Same. |

Count: 27 candidates (C4 23, C11 3, C16 1); 8 dirty (7 distinct places: the export bulk update is one place counted twice; 6 with harm, 1 low), 19 false.

## elsa-core (workflow engine: instances, bookmarks, activity states)

### Confirmed

| card | file:line | verdict | what comes from where and what the user sees |
|---|---|---|---|
| C11 | core/src/modules/Elsa.Alterations/Services/DefaultAlterationJobRunner.cs:44 | dirty (harm) | The job is saved as Running, then the alteration runs on an in-memory queue; if the run throws (the runner's guard, the workflow lookup or the pipeline can throw) or the process stops, nothing writes Failed, the job stays Running, the plan never completes (the plan counts Pending and Running jobs), and the Studio shows the plan as running forever. |
| C4 | core/src/modules/Elsa.Alterations/Services/DefaultAlterationJobRunner.cs:44 | dirty (harm) | Same place: job status written by the runner directly, with no failure transition for an exception. |
| C11 | core/src/modules/Elsa.Alterations/Activities/DispatchAlterationJobs.cs:70 | dirty (harm) | Plan saved as Dispatching, then each job is dispatched; if a dispatch throws, the plan stays Dispatching. The enum has Failed and the Studio draws it in red, but no code in the repository writes AlterationPlanStatus.Failed. |
| C4 | core/src/modules/Elsa.Alterations/Activities/DispatchAlterationJobs.cs:53 | dirty (harm) | Same place: plan status written in an activity, no failure state. |
| C11 | core/src/modules/Elsa.Alterations/Activities/GenerateAlterationJobs.cs:95 | dirty (harm) | Plan saved as Generating before the instance search and job creation; an exception leaves the plan in Generating with no way out. |
| C4 | core/src/modules/Elsa.Alterations/Activities/GenerateAlterationJobs.cs:75 | dirty (harm) | Same place. |
| C2 | core/src/modules/Elsa.Alterations/Services/AlterationPlanManager.cs:31 | dirty (harm) | "All jobs done" is a count of jobs in Pending or Running equal to zero, so jobs in Failed count as done; the plan is then stored as Completed and the user sees a completed plan whose jobs failed. |
| C4 | core/src/modules/Elsa.Alterations/Services/AlterationPlanManager.cs:37 | dirty (harm) | Same place: Completed is written with no look at job outcomes. |
| C11 | extensions/src/servicebus/Elsa.ServiceBus.MassTransit/Services/MassTransitWorkflowDispatcher.cs:48 | dirty (harm) | The instance is created and committed as Pending (status Running, sub-status Pending), then a message is sent; if the send fails the caller gets an exception, but the committed instance stays Pending and nothing else re-sends the message (only a repeat call with SkipIfInstanceExists and the same instance id repairs it), so the operator sees an instance that never starts. |
| C11 | core/src/modules/Elsa.UserTasks/Services/DefaultUserTaskInvitationService.cs:63 | dirty (low) | The invitation is committed as Pending and the delivery row is written afterwards in a separate commit; a crash between them leaves a Pending invitation that is never delivered; a manager can reissue or revoke it. |
| C16 | core/src/modules/Elsa.Workflows.Runtime/Services/IngressSourceRegistry.cs:71 | dirty (low) | RecordTransition and MarkPauseFailedAsync assign the state without a transition table, and GetState returns Running for an unknown source name; in-memory, shown in diagnostics only. |
| C17 | studio/src/modules/Elsa.Studio.Workflows/Components/WorkflowInstanceViewer/Components/WorkflowInstanceDesigner.razor:20 | dirty (low) | The "Alter" button is shown by the browser when WorkflowInstance.Status is Running and the user has the permission; the permission comes from the server, the status condition is the client's own rule, and the alteration runner has no status check. |
| C6 | core/src/modules/Elsa.Identity/Endpoints/Roles/Create/Endpoint.cs:57 | dirty (low) | The 409 for a duplicate role is chosen by the text "already exists" in the exception message; a changed message gives 500 instead of 409 (a second catch handles the unique-index exception). |
| C6 | core/src/modules/Elsa.Persistence.EFCore.Common/DbExceptionClassifier.cs:50 | dirty (low) | The SQL Server deadlock check falls back to message text after the error-number check; a localized message would not be retried. |
| C6 | core/src/modules/Elsa.Persistence.EFCore.Common/DbExceptionClassifier.cs:95 | dirty (low) | The duplicate-key check ends in message substrings after the typed checks; an unknown provider with a different message would give a generic error instead of a conflict. |

### False

| card | file:line | verdict | what comes from where and what the user sees |
|---|---|---|---|
| C11 | core/src/modules/Elsa.Connections/Services/DefaultConnectionLifecycleService.cs:937 | false | The Pending operation row is the stored next action, written together with the connection revision, claimed with a fence and a retry time; failure states exist (RetryScheduled, UnknownOutcome). |
| C11 | core/src/modules/Elsa.UserTasks.Persistence.EFCore/Repositories/EFCoreUserTaskGuestStores.cs:122 | false | This is the outbox itself: the Pending row is the durable wait, with attempts, availability time and expiry dropping. |
| C11 | core/src/modules/Elsa.Workflows.Core/Services/WorkflowRunner.cs:244 | false | The transition to Executing is in the in-memory context; an exception is stored on the context and the state is committed after the run. |
| C11 | core/src/modules/Elsa.Workflows.Runtime/Services/BookmarkQueueProcessor.cs:28 | false | Failures go to HandleFailureAsync with a dead-letter manager; the queue row stays until resolved. |
| C17 | studio/.../StateMachines/Presentation/StateMachineActivitySlot.razor:14 | false | IsReadOnly is a component parameter passed from the editor mode, not a rule about what a user may do. |
| C17 | studio/.../StateMachines/Presentation/StateMachineStateInspector.razor:17 | false | Same. |
| C6 | core/src/modules/Elsa.Workflows.Runtime/Services/DefaultWorkflowDefinitionStorePopulator.cs:436 | false | The message text only selects the log wording; the outcome (error result) is the same. |
| C6 | studio/src/framework/Elsa.Studio.Core/Extensions/RemoteFeatureProviderExtensions.cs:48 | false | Blazor framework message with no typed alternative; the result is "feature unavailable". |
| C6 | studio/src/framework/Elsa.Studio.Shared/Components/ExpressionInput.razor.cs:330 | false | JavaScript error text from the editor library; a silent skip of a refresh. |
| C6 | studio/src/modules/Elsa.Studio.Login.BlazorServer/Services/BlazorServerJwtAccessor.cs:66 | false | Same framework message as above. |
| C6 | apps/src/Elsa.Studio.BlazorServer/SafeBlazorServerJwtAccessor.cs:65 | false | Same. |
| C6 | scripts/integration-program/secrets-sqlite-bridge-contract/extensions-3.8.1/Program.cs:157 | false | A test script in a scripts folder. |
| C4 | core/experiments/NativeCompensation.E1/Activities.cs:66 | false | Experiment code, not shipped. |
| C4 | core/experiments/NativeCompensation.E1/Activities.cs:99 | false | Same. |
| C4 | core/src/modules/Elsa.AI.Host/Tools/Workflows/WorkflowValidateDraftTool.cs:28 | false | Status of a tool result object built in one expression. |
| C4 | core/src/modules/Elsa.Connections/Services/DefaultConnectionLifecycleService.cs:132 | false | Sets the returned metadata after the stored publish succeeded; failures set recovery-required states. |
| C4 | core/src/modules/Elsa.ExternalAuthentication/Services/PreviewSignInService.cs:69 | false | ClientState is an OAuth state string, not a lifecycle. |
| C4 | core/src/modules/Elsa.Persistence.EFCore/Modules/Alterations/AlterationJobStore.cs:145 | false | Generic store upsert that persists whatever the runner set; the defect is in the runner (see C11). |
| C4 | core/src/modules/Elsa.Persistence.EFCore/Modules/Alterations/AlterationPlanStore.cs:77 | false | Same, plan store. |
| C4 | core/src/modules/Elsa.Persistence.VNext.Runtime/Services/RuntimeEntityManager.cs:20 | false | SaveDraft writes Draft by design, with optimistic version check. |
| C4 | core/src/modules/Elsa.Persistence.VNext.Runtime/Services/RuntimeEntityManager.cs:58 | false | Explicit publish action with validation and a version check; re-publishing a retired definition is a user action, not a race. |
| C4 | core/src/modules/Elsa.Secrets/Services/DefaultSecretManager.cs:79 | false | Retiring old versions on rotate; rotate is refused for Revoked and Deleted secrets are hidden by the lookup. |
| C4 | core/src/modules/Elsa.Secrets/Services/DefaultSecretManager.cs:111 | false | Revoke on a lookup that hides Deleted secrets; revoking twice is idempotent. |
| C4 | core/src/modules/Elsa.Secrets/Services/DefaultSecretManager.cs:234 | false | Delete after the store payload was removed; hidden from later lookups. |
| C4 | core/src/modules/Elsa.UserTasks/Services/DefaultUserTaskManager.cs:411 | false | Timeout is guarded by terminal, in-progress, due-time and revision checks and has a retry path for a failed resume. |
| C4 | core/src/modules/Elsa.UserTasks.Persistence.EFCore/Repositories/EFCoreUserTaskRepository.cs:582 | false | Mapper copy between model and row. |
| C4 | core/src/modules/Elsa.Workflows.Admission.Persistence.EFCore/EFCoreAdmissionStore.cs:524 | false | Helper that first checks the capacity invariant and throws on violation. |
| C4 | core/src/modules/Elsa.Workflows.Management/Mappers/WorkflowStateMapper.cs:43 | false | Projection of the engine's state onto the stored instance row; the engine is the writer. |
| C4 | extensions/src/secrets/Elsa.Secrets.Management/Services/DefaultExpiredSecretsUpdater.cs:23 | false | Recurring task that selects only Active secrets past expiry; a race with revoke is possible but narrow. |
| C4 | extensions/src/secrets/Elsa.Secrets.Management/Services/DefaultSecretUpdater.cs:27 | false | Retires only Active versions when a new version is created. |
| C4 | studio/.../ConsoleLogViewer.razor.cs:451 | false | UI view state of a log viewer. |
| C4 | studio/.../ConsoleLogViewer.razor.cs:522 | false | Same. |
| C4 | studio/.../StructuredLogs.razor.cs:666 | false | Same. |
| C4 | studio/.../StructuredLogs.razor.cs:699 | false | Same. |
| C4 | studio/.../DeleteRoleDialog.razor.cs:189 | false | UI dialog state. |

Count: 50 candidates (C4 27, C6 9, C11 9, C17 3, C2 1, C16 1); 15 dirty (5 distinct harmful places: alteration job runner, dispatch activity, generate activity, plan completion over failed jobs, MassTransit dispatcher; the other dirty rows are duplicates of these or low-severity), 35 false.

## Heaviest confirmed places

### 1. elsa-core: alteration job and plan stuck in Running, or plan Completed over failed jobs

Steps to reproduce:
1. Submit an alteration plan that matches at least one instance that is owned by a running execution, so that the runner's ownership guard throws in `DefaultAlterationRunner.RunAsync` (or point the plan at an instance whose definition was removed and make the pipeline throw).
2. The background dispatcher runs `DefaultAlterationJobRunner.RunAsync`; the job is saved as Running before the exception.
3. The exception leaves the job in Running, `AlterationJobCompleted` is never sent, so `AlterationJobCompletedHandler` never completes the plan.
4. Open the plan in the Studio: it stays Running; no code writes `AlterationPlanStatus.Failed`.
5. Variant: let the run return an unsuccessful result; the job is Failed, the handler sees zero Pending or Running jobs and stores the plan as Completed.

Minimal fix: `DefaultAlterationJobRunner.RunAsync` (wrap the run in try/catch, write Failed with the log and send the notification) and `AlterationPlanManager.GetIsAllJobsCompletedAsync` / `CompletePlanAsync` (write Failed when any job failed); the same try/catch pattern in `DispatchAlterationJobs` and `GenerateAlterationJobs`.

Test without external services: yes. `DefaultAlterationJobRunner` takes interfaces only (two stores, the alteration runner, the notification sender, the clock); a unit test with in-memory fakes and an `IAlterationRunner` that throws asserts the job is not left in Running. It fails before the fix. The process-death case needs a sweeper and cannot be a unit test.

### 2. Smartstore: PayPal webhook resets order status to Pending

Steps to reproduce:
1. Create an order paid with PayPal, then either mark it paid (Processing) or cancel it in the admin.
2. Send a PAYMENT.CAPTURE.PENDING (or AUTHORIZATION.DENIED/EXPIRED/PENDING) webhook for that order's custom id, as PayPal does on retries or out-of-order delivery.
3. `PayPalController` sets `OrderStatus = Pending` and saves.
4. The order list shows Pending for a paid or cancelled order; for a cancelled order the stock stays returned.
5. Variant: send CAPTURE.DECLINED for a cancelled order; both statuses become Pending.

Minimal fix: the pending branches in `HandleAuthorizationAsync` and `HandleCaptureAsync` and the declined branch in `HandleCaptureAsync` in `PayPalController.cs`: skip when the order is Cancelled or Complete or the payment is already Paid (the guard that the declined branch has for Paid), preferably through one order-status writer with a transition table.

Test without external services: partly. `WebhookHandler` verifies the signature by calling PayPal, so the public action cannot run offline; the handlers are private methods taking the order and the resource, so a test needs reflection or a small extraction, plus a test database context. The repository has `OrderProcessingServiceTests` in `Smartstore.Core.Tests`, so the setup pattern exists. I did not try it.

### 3. Smartstore: export status change overwrites any order status

Steps to reproduce:
1. In the admin create an order export with "change order status after export" set to Complete and no status filter.
2. Have one cancelled order and one pending order.
3. Run the export.
4. `UpdateOrderStatus` issues one bulk update on all exported ids; the cancelled order becomes Complete with no note, no e-mail and no reward-point handling.

Minimal fix: `DataExporter.UpdateOrderStatus` (`DataExporter.cs`): add a where-clause on the current status or call the order service per order; log the count of skipped orders.

Test without external services: yes with a small change. The method is private and uses `_db.Orders.ExecuteUpdateAsync`, which works on SQLite; a test either calls it by reflection with a database context and a context object holding the loaded ids, or the status update is moved into a method taking ids and the target status. It fails before the fix.
