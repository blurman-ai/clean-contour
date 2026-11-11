# Python batch: prefect, celery, netbox, crewAI

Read on 11 November 2026 (shallow clones of the default branches): DeepSeek flash gave a verdict on every candidate found by the cards' Python search signs, and Sonnet read what it flagged, with whole files and callers. Not reproduced on a running instance.

The list has 66 places: prefect 43, crewAI 12, netbox 8, celery 3. All 66 were read, including all 29 C6 places of prefect/crewAI/netbox that the brief allowed to sample. Severity words (high, medium, low) are the reader's estimate of user harm. "Formal" means the card matches but nothing user-visible depends on it.

Overall: the card C4 ("state written around the writer") mostly hits in-memory objects, response models and creation of a fresh row, and is false in 25 of 30 cases. The confirmed C4 and C11 findings are in two places: the prefect transfer graph and the NetBox data source. C6 (decision by error text) is real in 24 of 29 places but mostly low; the exceptions are listed first.

## prefect

### Confirmed, by consequence

| Card | File:line | Verdict | What comes from where and what the user sees |
|---|---|---|---|
| C11 (the DeepSeek verdict was wrong about the line, the defect is elsewhere in the same function) | src/prefect/cli/transfer/_dag.py:297-303 (`except TransferSkipped` in `execute_concurrent`) | dirty, high | A node that raises `TransferSkipped` ("Already exists" for a flow, work pool, block, variable) gets state SKIPPED, and its dependents (deployments, work queues) are neither started nor marked: the readiness loop that starts dependents runs only after a successful `process_node`, and the failure branch is the only one that cascades. The work-pool and flow resources store the destination object before raising, so they are written to let dependents continue. In `prefect transfer` into a workspace that already holds a same-named flow or pool, the deployments stay PENDING, are not created, and are absent from the result table (the table is built from `results`, which has no entry for them). The same happens to dependents of a failed node when `skip_on_failure=False`. |
| C6 | src/prefect/server/api/deployments.py:1293 | dirty, medium | `IntegrityError` text is compared with the PostgreSQL wording "duplicate key value violates unique constraint". On SQLite (the default server database) the text is "UNIQUE constraint failed", the branch is skipped, and the app-wide handler returns 409 "Data integrity conflict... See server logs" instead of "Schedule slugs must be unique within a deployment." The existing test checks only the status code, so it passes. |
| C6 | src/integrations/prefect-aws/prefect_aws/workers/ecs_worker.py:1733 | dirty, medium | `kill_infrastructure` turns an ECS `InvalidParameterException` into `InfrastructureNotFound` only if the text contains "task was not found". Any other wording goes to the generic handler in the worker base, which logs "Error killing infrastructure" and returns without marking the flow run cancelled, so the run stays in its cancelling state. |
| C6 | src/prefect/_internal/version_checking.py:156; src/prefect/client/orchestration/__init__.py:1134 and :1525 | dirty, low | A failed version request is treated as an authentication error if `"Unauthorized" in str(e)`; otherwise it is reported as "Failed to reach API at ...". Any other 401 wording (proxy, custom reason phrase) shows the user a connectivity error instead of a credentials error. The status code is on the exception. |
| C6 | src/prefect/runner/_limit_manager.py:85 | dirty, low | A duplicate borrower is detected by the text "already holding" of an anyio `RuntimeError`. If a newer anyio words it differently, the error propagates out of `acquire_for_flow_run` instead of returning False and the runner fails to submit the run. |
| C6 | src/prefect/client/orchestration/_deployments/client.py:170; _work_pools/client.py:201 and :528 | dirty, low | A 403 is turned into `ObjectLimitReached` / `ObjectUnsupported` by the server's message ("maximum number", "plan does not support"). If the server text changes, the user gets a plain HTTP error instead of the plan-limit message. |
| C6 | src/prefect/server/api/flow_runs.py:920 | dirty, low | Duplicate flow run input is recognised by "unique constraint" in the lowered error text, otherwise the endpoint answers 404 "Flow run not found". On a PostgreSQL server with a non-English `lc_messages`, a duplicate key is reported as a missing flow run. |
| C6 | src/prefect/server/models/workers.py:920 | dirty, low | "Can't delete a pool's default queue" is chosen by "foreign key constraint" in the text; on a localized PostgreSQL the user gets a raw 500. |
| C6 | src/integrations/prefect-docker/prefect_docker/worker.py:1189 | dirty, low | A container name conflict is detected by "Conflict" and "container name" in the error text; the exception has `status_code` 409. If the text changes, the run fails instead of retrying with another name. |
| C6 | src/integrations/prefect-docker/prefect_docker/worker.py:167 | dirty, low | A missing container on Podman (HTTP 500) is recognised by "no such container". Deliberate workaround, named in the docstring; breaks silently if Podman rewords it. |
| C6 | src/integrations/prefect-redis/prefect_redis/messaging.py:56 | dirty, low | A missing stream is recognised by "no such key"; a Redis-compatible server with other wording makes stream trimming fail instead of skipping. |
| C6 | src/integrations/prefect-aws/prefect_aws/_cli/utils.py:306 | dirty, low | "No updates are to be performed" in a CloudFormation `ClientError` text decides between "already up to date" and a failure; the error carries a code. |
| C6 | src/integrations/prefect-sqlalchemy/prefect_sqlalchemy/database.py:141 | dirty, low | The code raises its own `ValueError` inside a `try` and tells it apart from the enum's `ValueError` by the text "async driver". Works today, breaks if either message is edited. |
| C6 | src/prefect/cli/deploy/_commands.py:136 | dirty, low | "Unknown recipe" is matched in a `ValueError` raised by `initialize_project` in the same repository (deployments/base.py:142); a rewording drops the user into a traceback. |
| C6 | src/prefect/cli/_utilities.py:101 | dirty, low | `--param key=text` is retried as a quoted string if the JSON error text contains "Extra data" or "Expecting value"; catching `JSONDecodeError` would do. |
| C6 | src/prefect/_internal/result_records.py:141; src/prefect/cache_policies.py:329 | dirty, low | The first only chooses a hint text ("cannot pickle"). The second chooses hashing fallback versus re-raise by "source code" in an `OSError` text from the standard library. |
| C4 | src/prefect/cli/transfer/_dag.py:253, :288, :321 | dirty, formal | The graph writes node state in several places with no table; the real defect in this class is the one in the first row. |

### False, by reason

**Local copy of a state the server already wrote (4).**
- C4 src/prefect/flow_engine.py:1302: `self.flow_run.state = state` after the state-change API call that the engine already made.
- C4 src/prefect/flow_engine.py:2037: same, async engine (DeepSeek said unclear).
- C4 src/prefect/task_worker.py:361: sets the local task run to Pending and emits an event; the engine performs the API transition.
- C4 src/prefect/server/events/actions.py:564: rebuilds the state from event data on a copy used to render a template; nothing is saved.

**Creation in the initial state (2).**
- C4 src/prefect/server/api/deployments.py:989: `Scheduled()` on a new flow run before `create_flow_run`.
- C4 src/prefect/server/api/task_runs.py:76: `Pending()` on a new task run.

**Not a lifecycle, or a response model (2).**
- C4 src/prefect/server/schemas/core.py:1179: `status = None` for agent pools in a response model.
- C16 src/prefect/_internal/analytics/milestones.py:139: a local telemetry flag, no transitions.

**Class owns its state in memory, and the writer exists (3).**
- C4 src/prefect/transactions.py:215, :313, :471: the transaction object sets ACTIVE and COMMITTED inside its own methods; nothing persisted.

**Writer goes through orchestration rules (2).**
- C16 src/prefect/server/api/flow_runs.py:835 and src/prefect/server/models/flow_runs.py:589: `set_flow_run_state` compiles rules per (old type, proposed type) pair and returns ACCEPT/REJECT/ABORT/WAIT to the caller (DeepSeek said unclear).

**A transition with one legal source (1).**
- C16 src/prefect/server/models/deployments.py:1426: `mark_deployments_not_ready` sets NOT_READY for every locked row; the only other value is READY (DeepSeek said unclear).

**C6 where the text only chooses a log line or an ignorable case (5).**
- src/prefect/flows.py:1191 and src/integrations/prefect-redis/prefect_redis/client.py:155: "no running event loop", stable CPython text.
- src/prefect/logging/handlers.py:393: "closed file" suppresses a logging error.
- src/prefect/server/models/logs.py:81: a known CPython 3.12.2 shutdown bug, the log write is dropped on purpose.
- src/integrations/prefect-docker/prefect_docker/worker.py:1089: "marked for removal" only picks the warning text; other errors are logged with a traceback.

Count, prefect: 43 places. Dirty: 24 (20 C6: 1 medium on SQLite wording, 1 medium on ECS cancel, the rest low; 3 C4 formal in the transfer graph; 1 C11 high). False: 19 (C4 10, C16 4, C6 5). The DeepSeek C11 verdict named a line that is clean (`except Exception` writes FAILED); the defect is in the skip branch beside it.

## crewAI

### Confirmed, by consequence

| Card | File:line | Verdict | What comes from where and what the user sees |
|---|---|---|---|
| C6 | lib/crewai/src/crewai/tools/mcp_tool_wrapper.py:198 (and :125-150, same file, not on the list) | dirty, medium | `_execute_tool` converts any exception that has a `__cause__`, or whose text contains "TaskGroup" or "unhandled errors", into `asyncio.TimeoutError`. The caller treats `TimeoutError` as retryable and shows the model "Connection timed out after 60 seconds", after up to 3 attempts of the whole call including `call_tool`. A connection error from the MCP client's task group (for example an HTTP 401 or 404 inside an exception group) therefore reaches the agent as a timeout and is retried; the authentication and "not found" branches of `_execute_single_attempt` are never reached for it. Those branches also choose by text ("not found", "network", "json"), so a tool error such as "file not found" is reported as "Tool 'x' not found on MCP server". The exception-group claim was read from the code, not run against an MCP server. |
| C6 | lib/crewai/src/crewai/knowledge/storage/knowledge_storage.py:124 and :205 | dirty, medium | The friendly error with reset instructions is chosen by "dimension mismatch" in the text. ChromaDB's own text is "Embedding dimension N does not match collection dimensionality M" (checked in the chromadb 1.5.9 sources), which does not contain that phrase, so the branch is not reached for the default store; the user sees "Failed to upsert documents: ..." and the raw error without the advice to reset. The test mocks an exception with the text "dimension mismatch detected", so it passes. |
| C6 | lib/crewai/src/crewai/mcp/exceptions.py:146 | dirty, low | `error_type` of the failed-tool event is "timeout" or "authentication" by the text of the error; only the telemetry event is wrong when the text differs. |
| C6 | lib/crewai/src/crewai/llms/providers/gemini/completion.py:319 | dirty, low | "No API key was provided" prefix of a `ValueError` from the Google SDK decides between a missing-key message and the original error; the code says in a comment that the SDK has no typed error. If the SDK rewords it, the user sees the SDK error instead of the instruction. |
| C6 | lib/crewai-files/src/crewai_files/uploaders/bedrock.py:47 | dirty, low | The S3 error code is checked first; "Throttl" in the type name or text is a fallback, and anything unknown becomes `TransientUploadError`, so an unknown permanent S3 error is retried. |
| C16 | lib/crewai/src/crewai/utilities/planning_types.py:90 | dirty, formal | `mark_completed` / `mark_failed` / `mark_running` assign without checking the old status. The only caller (agent_executor `_mark_todo_*`) reads the previous status itself and emits events once; memory only, no stored plan. |

### False, by reason

**Guarded writer inside the owning class, result returned to the caller (4).**
- C4 lib/crewai/src/crewai/experimental/flow_turns.py:205: sets "interrupted" only `if reply.status == "generating"`.
- C4 lib/crewai/src/crewai/experimental/flow_turns.py:418: completion and failure are set under the lock after checking `reply.interrupted`, in the stream generator that owns the reply.
- C16 lib/crewai/src/crewai/experimental/flow_replies.py:353: `mark_covered` and `settle` check the old status and return False for the caller (DeepSeek said unclear).
- C4 lib/crewai/src/crewai/a2a/utils/task.py:501: the function first returns the task unchanged when it is completed, failed or canceled; then it sets canceled on the in-memory object after enqueuing the final event.

**Text decides only an intentional drop (1).**
- C6 lib/crewai/src/crewai/memory/unified_memory.py:653: "cannot schedule new futures" (CPython shutdown message) abandons a save during exit; the comment names it and other errors propagate.

Count, crewAI: 12 places. Dirty: 7 (3 medium: mcp_tool_wrapper.py:198, knowledge_storage.py:124 and :205; 3 low; 1 formal). False: 5 (DeepSeek called 4 of them dirty and 1 unclear). One more dirty place, mcp_tool_wrapper.py:125-150, was found beside a listed line and is not counted.

## netbox

### Confirmed, by consequence

| Card | File:line | Verdict | What comes from where and what the user sees |
|---|---|---|---|
| C11 / C4 | netbox/core/models/data.py:194 and :261 (the writes inside `sync()`), with netbox/core/jobs.py:36 (`enqueue` writes QUEUED) | dirty, medium | `DataSource.status` is written to SYNCING before the fetch, by three code paths (job, model, command), with no table. If the worker process is killed after that write (restart, out-of-memory kill), nothing moves the source out of SYNCING: no sweeper and no timestamp. The detail page and the list hide the Sync button when `ready_for_sync` is false (QUEUED or SYNCING), and `sync()` itself refuses with "syncing already in progress". Ways out: the REST sync action or the next scheduled sync (both go through `enqueue`, which writes QUEUED), or running the management command twice (the first run fails and writes FAILED). The first failure path (an exception in the job or command) does write FAILED. Not run. |
| C6 | netbox/extras/api/serializers_/scripts.py:82 | dirty, low | "A script module with this file name already exists" is chosen by `'file_path' in str(e)` of an `IntegrityError`; any other integrity error is re-raised as a 500. The PostgreSQL detail names the columns, so it works. |

### False, by reason

**Guarded writer with a lock and a returned row count (2).**
- C4 netbox/extras/jobs.py:172: `.update(status=ACTIVE)` has `WHERE status = PROVISIONING` under an advisory lock, returns whether it applied, re-checks status after the lock; `delete()` re-enqueues the purge job when the first one never ran (comment at extras/models/customfields.py:690).
- C4 netbox/core/management/commands/syncdatasource.py:42: writes FAILED after an exception in the sync; same exit as the job path, no wrong state.

**A read, not a write (1).**
- C4 netbox/extras/models/customfields.py:569: `self.status = self._lock_status(using)` refreshes the instance from the database under a row lock.

**Text of the project's own trigger, gated by SQLSTATE (1).**
- C6 netbox/netbox/models/ltree.py:423: "cycle detected" and "tab character" are raised by NetBox's own trigger and are checked together with SQLSTATE 23514.

Count, netbox: 8 places. Dirty: 4 (3 in the first row, medium; scripts.py:82, low). False: 4.

## celery

### Confirmed, by consequence

| Card | File:line | Verdict | What comes from where and what the user sees |
|---|---|---|---|
| C2 | celery/backends/database/__init__.py:244 | dirty, medium | `_get_task_meta_for` builds a row with status PENDING when no row exists, so an id with no stored result is reported as PENDING: a task whose result row was removed by expiry, a mistyped id, and a task not yet written all look the same. `AsyncResult.get()` on such an id waits until its own timeout. This is documented Celery behaviour, so changing it changes the public state set. |

### False, by reason

**Class owns its state in memory (1).**
- C4 celery/bootsteps.py:110: `Blueprint.start()` sets RUN on the blueprint object; this method is the writer, and the state is process-local.

**The writer, with an ordering rule (1).**
- C4 celery/events/state.py:329: `Task.event` is the one place that applies an incoming event; it uses `states.precedence` to keep or merge a late event instead of overwriting.

Count, celery: 3 places. Dirty: 1. False: 2.

## Heaviest places, with steps to reproduce

### 1. prefect transfer: dependents of a skipped node are never run or reported

Steps:
1. Run two Prefect servers (or one server and a second profile). On the source create a flow, a work pool `P`, and a deployment of the flow on `P`.
2. On the destination create a work pool named `P` (or run `prefect transfer` once and delete only the deployment).
3. Run `prefect transfer --from <source> --to <destination>`.
4. The result table lists the pool as Skipped "Already exists". The deployment is not in the table and `prefect deployment ls` on the destination does not show it.
5. The same happens with a flow that already exists on the destination.

Minimal fix: the `except TransferSkipped` branch in `TransferDAG.execute_concurrent` (src/prefect/cli/transfer/_dag.py, after the line that sets SKIPPED). Either release the dependents as the success branch does when the skip means "already exists" (the resource already holds the destination object), or run the same descendant loop as the failure branch so the dependents get SKIPPED and a result.

Failing test without external services: yes. tests/cli/transfer/test_dag.py already has `MockMigratableResource` with a skip mode and a test for failure propagation. Add a root that depends on a skipped resource and assert either `root.migrate_called` or that `results` has an entry for it; it fails now because the root has no entry and its state stays PENDING. Needs the prefect test dependencies installed, no server.

### 2. crewAI MCP tool wrapper: any wrapped error becomes a timeout and is retried

Steps:
1. Point an `MCPToolWrapper` at a streamable HTTP MCP server that answers 401 (or a URL that returns 404).
2. Call the tool from an agent.
3. `_execute_tool` receives an exception group "unhandled errors in a TaskGroup" and raises `asyncio.TimeoutError`; the wrapper retries three times with waits of 1 and 2 seconds.
4. The agent receives "MCP tool execution failed after 3 attempts: Connection timed out after 60 seconds", not an authentication message.
5. Not run against a server; steps 3-4 are read from the code.

Minimal fix: the final `except Exception` block of `_execute_tool` in lib/crewai/src/crewai/tools/mcp_tool_wrapper.py: stop mapping by `__cause__` and message text, let the original exception reach `_execute_single_attempt`, and classify there by exception type or status code.

Failing test without external services: yes. Patch `mcp.client.streamable_http.streamablehttp_client` to raise `ExceptionGroup("unhandled errors in a TaskGroup", [<401 error>])`, call `_run_async`, assert the message mentions authentication and that the patched client was called once. It fails now (3 calls, timeout text). The `mcp` package must be importable or stubbed in `sys.modules`.

### 3. prefect: duplicate schedule slug shows a generic message on SQLite

Steps:
1. Start the default server (SQLite).
2. POST two schedules with the same slug to `/deployments/{id}/schedules`.
3. Response is 409 with "Data integrity conflict. This usually means a unique or foreign key constraint was violated. See server logs for details."; the expected text is "Schedule slugs must be unique within a deployment."

Minimal fix: src/prefect/server/api/deployments.py, the `except sa.exc.IntegrityError` at line 1292: decide by the driver's error (SQLite error code or `sqlstate` 23505 on PostgreSQL) instead of the PostgreSQL message text.

Failing test without external services: yes. `test_schedule_slug_must_be_unique_within_deployment` in tests/server/orchestration/api/test_deployment_schedules.py already posts the duplicate; add `assert response.json()["detail"] == "Schedule slugs must be unique within a deployment."`. It fails on SQLite now and runs in the standard test setup.

### Not in the top three

- NetBox DataSource stuck in SYNCING after a killed worker: a test needs PostgreSQL (the sync takes an advisory lock) and a new recovery rule; there is no timestamp field to build it on, so the fix is not minimal.
- crewAI knowledge storage dimension message: a failing test is possible with an in-process ChromaDB and a custom embedding function, no network; harm is a missing hint.
