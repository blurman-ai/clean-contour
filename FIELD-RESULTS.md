# Field results

What the rules and the check found in open-source projects written mostly by coding agents, measured on 3 November 2026. For anyone deciding whether to use this repository. Nothing here is needed to run the check.

## Short version

- Coding agents don't keep this hygiene on their own. They write statuses straight from request handlers, derive state from logs and files, and refuse with free text.
- Rules in `CLAUDE.md` alone help partly, because agents often don't open them. A check named in the task itself helps most.
- Across 40 agent-written projects the check found 1423 dirty places, and 33 of the projects have no instruction about state, transitions or refusal codes.
- In 15 popular projects where between 41 and 789 people commit with agents, the files those people change most hold the same share of dirty places. All 15 have agent instructions; none of them covers state, transitions or refusal codes.

## Same tasks, with and without the rules

Ten commits that introduced dirty code in two projects. A fresh agent (Sonnet, Claude Code) got the project as it was before the commit and the same task text. Reviewers saw the four versions under random names, with every trace of the condition removed.

| Condition | Dirty places in 10 tasks | Agent opened the rules |
|---|---|---|
| O: the project's original commit | 22 | n/a |
| A: the project's own `CLAUDE.md` only | 16 | n/a |
| B: A plus `RULES.md` and a line about it in `CLAUDE.md` | 10 | 2 of 10 tasks |
| C: B plus the skill, and "run the check on your diff and fix what is dirty" in the task | 6 | 7 of 10 tasks |

Compare A, B and C. O was written by a different model or version.

On one of these tasks, an API for task runs, the agent in A wrote `status = "cancelled"` in the handler and copied the status from the request. In B and C it built a transition table and one writer function on its own.

The same task on DeepSeek v4-pro gave 6, 3 and 0 dirty places for A, B and C. That is one task, so read it only as a sign that the effect isn't specific to one model.

Limits: 10 tasks, one run per condition, so run-to-run variation isn't measured. The reviewer reads added lines only and misses violations visible only across files.

## 40 agent-written projects

Open-source Python and TypeScript projects where a coding agent signed more than two thirds of the commits; in 20 of them, at least 90%. The signature only gives a lower bound. Each project was checked whole with the skill on Sonnet, without running it.

| | |
|---|---|
| Candidates examined | 3526 |
| Dirty | 1423 |
| Projects with no instruction on state, transitions or refusal codes | 33 of 40 |
| Risk scenarios confirmed by reading the code by hand | 58 |
| Risk scenarios dropped by that reading | 5 |

The 20 projects with at least 90% agent commits look the same as the other 20: 37% of candidates dirty against 44%, about 36 dirty places per project against 35.

So roughly one in ten of the strongest findings didn't survive a human-directed read. The 1423 will contain mistakes too: only the strongest were read by hand.

One project's `AGENTS.md` forbids refunding when a provider call has an unknown outcome. Its wallet purchase does exactly that after a timeout. A rule in a file doesn't stop the violation.

### Typical findings, without project names

The authors haven't been told about these yet.

| What the code does | What happens |
|---|---|
| A wallet purchase refunds after a timeout from the provider | The buyer has the money back and may still hold the account |
| A payment row is written as `processing` before the work | The process dies, every retry is refused forever, and the ledger can't say if it was booked |
| A status is set before the stock movement, and the movement is best-effort | The count shows posted, stock isn't corrected, and it can't be posted again |
| A worker's process dies during a task | The task shows complete, because only one agent status maps to failed |
| A webhook handler fails and returns 200 with an error in the body | The sender sees success and doesn't retry |
| A money decision matches the text of an exception | Rewording the message sends a paid order down the rollback path |
| A form fills in from an uploaded record and overwrites what the clinician already typed | Entered allergies can disappear before the patient is added |
| A payment settles, then writing the order record fails | The buyer is told it failed, and a retry settles again unless settlement is idempotent |
| Any admin page view moves an emergency account to active and drops the result | The job that sends the "activated" email finds nothing to send |
| A payment webhook with an unknown price logs a warning and returns | The customer paid, the event counts as handled, and no subscription exists |
| Budget and billing read different sets of "active" subscription statuses | A past-due customer is refused runs as unsubscribed and still charged |
| A removed member has no membership, so a GET re-adds them by email domain | Removal doesn't hold for anyone on the workspace's domain |
| A bulk import records each failure and then sets the upload to approved | The upload reads approved with nothing imported |

### Fixes sent to the authors

| Project | Problem | Principle | Fix |
|---|---|---|---|
| prefect421/mvidarr | An anonymous `POST /skip` turned a finished setup wizard back into unfinished, which reopened endpoints that work without a login | transition with no check | [#582](https://github.com/prefect421/mvidarr/pull/582) |
| ander1044/wairz | A failed NVD lookup counted as "no CVEs", and later scans returned that as cached | unknown is not success | [#1](https://github.com/ander1044/wairz/pull/1) |
| omnivision-solutions/tuti | An upload stayed `PROCESSING` forever when the queue refused it | a wait with no way out | [#530](https://github.com/omnivision-solutions/tuti/pull/530) |

Each fix comes with a test that fails without it. These are open pull requests and the authors may decide otherwise.

## Popular projects where many people use agents

786 Python and TypeScript projects with at least 1000 stars and commits after 15 October 2026. For each, the history since 1 May 2026 gives the number of different people (bots excluded) who committed with an agent's signature. 15 projects with many such people and with stateful code were checked: vLLM, Home Assistant, t3code, claude-mem, Superset, n8n, Grafana, Ray, Sentry, Paperclip, LiteLLM, Airflow, OpenHands, Langfuse and Actual Budget. Between 41 and 789 people per project committed with an agent in that time.

These projects are too large to check whole. In each, the check covered up to 40 files that the most different people had changed with agents since May.

| | |
|---|---|
| Files checked | 600 |
| Candidates | 810 |
| Dirty | 312 (39%, the same share as the small agent-written projects) |
| Projects with agent instructions | 15 of 15, often hundreds of lines |
| Of those, instructions that cover state, transitions or refusal codes | 0 |

The dirty places sit in files that dozens of people changed with their agents and that went through review. Typical ones, confirmed by reading the code:

| What the code does | What happens |
|---|---|
| The status of a failed run is chosen by whether the error text contains "cancel" | A tool error about a cancelled request records the run as cancelled by the user |
| "Success" is computed as "status is not error and no error object" | A crashed run without an error object reports success |
| "Everything except processing counts as completed" | A failed run counts as done, and re-triggering it does nothing |
| An exception handler logs every HTTP error and doesn't re-raise | Adding a user to a team fails silently whatever the cause |
| A repository declares that failed and cancelled are terminal; a route revives them with a raw UPDATE | Jobs restart past their attempt limit |
| An UPDATE that cancels pending items omits the filter its own preceding SELECT used | Finished items are rewritten as cancelled |
| A status lookup returns "pending" when the record is missing | An unknown, expired or abandoned job looks like it's still running |
| A "device not found" value is checked as "device off" | The thermostat shows idle while its heater is missing |
| A busy flag is set before an await and cleared after it, with no finally | After one failure, the action never runs again until reload |
| `title.startswith("add")` | "Address flaky test" is listed as a significant change |

None of these needs domain knowledge to spot. They are the kind of mistake the cards target: state decided by text, a missing value read as a valid one, a transition written past the place that guards it.

## Kotlin and Go

The cards were first written with Python and TypeScript signs. Without an ORM, state in Kotlin and Go projects lives in SQL strings, and a search for `.status =` there mostly hits `WHERE` predicates and constants. Each card now names signs for Kotlin (and Java) and Go: `SET … status =` with a guard on the old value, repeated `IN ('…')` lists, a waiting literal together with whatever moves it out. The signs were revised after the first four runs and tried again on three.

| Project | Language | Candidates | Dirty |
|---|---|---|---|
| [recurso](https://github.com/recurso-dev/recurso), billing | Go | 104 | 45 |
| [hardcount](https://github.com/gethardcount/hardcount), billing | Go | 101 | 36 |
| [arx](https://github.com/Jolls/arx), shop-floor ERP | Go | 134 | 40 |
| [task-orchestrator](https://github.com/jpicklyk/task-orchestrator) | Kotlin | 88 | 32 |
| [kanban-vision-api-kt](https://github.com/agnaldo4j/kanban-vision-api-kt) | Kotlin | 28 | 9 |
| a private marketplace with escrow and payouts | Kotlin | 113 | 60 |

Agent commits are 81–98% in the open projects. A run costs $1–3 on Sonnet.

Confirmed by reading the code:
- recurso: a late `payment_failed` webhook sets a paid invoice to `past_due`. The handler checks only tenant ownership, and the repository `Update` writes the status with no guard, so dunning can pursue a customer who already paid.
- the private marketplace: a refund that the payment provider keeps refusing is retried every five minutes with no limit. The table allows only `PENDING` and `PAID`, and nobody is told.

## The check next to a plain bug hunt

The same model was given the private marketplace with no rules and no description of the product, only "a Kotlin backend and a TypeScript frontend; find the bugs and risks a user or operator would hit". It took 48 steps and $0.95 and reported 12 findings.

The two lists barely overlap: one stuck payout timer is on both. The plain hunt found security and business-logic problems the cards do not cover: a JWT signing key with a default in the config, payouts blocked after a seller's payment account is re-approved, an electronic signature stubbed in production. It did not find the endless refund. The cards found it, along with refusal reasons lost on the way and a `GET` that writes to the database every five seconds.

On a second codebase the plain hunt stopped after 17 steps and $0.40 with seven minor findings, noting that it had not read most of the code. A free-form audit picks its own depth. The cards make the run cover every sign across the code, which costs more and finds a different class of problem. They are a check of how state is built, not a replacement for looking for bugs.

## Bugs these projects already fixed

391 commits with "fix" or "bug" that touch statuses, error codes or exception handling, across four projects. 172 were classified by a model and the positive answers read by hand. In 24 of them (14%), following a principle would clearly have prevented the bug. Most often: a wait with no failure state, state derived from indirect signs, unknown counted as success, and a default substituted for a missing value.

- [revel-backend](https://github.com/letsrevel/revel-backend) `fffad3f`: token schemas filled in a default type, so a session token was accepted as a password-reset token. No agent signature on the commit that introduced it.
- [ai-trading-agent](https://github.com/flukelaster/ai-trading-agent) `8b2a9ba`: `except Exception: pass` hid an import error, and orders never reached the broker.
- [legalise](https://github.com/b1rdmania/legalise) `eed4b6c`: a transition function allowed a jump from any state.
