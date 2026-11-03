# Field results

What the rules and the check found in open-source projects written mostly by coding agents, measured on 3 November 2026. For anyone deciding whether to use this repository. Nothing here is needed to run the check.

## Short version

- Coding agents don't keep this hygiene on their own. They write statuses straight from request handlers, derive state from logs and files, and refuse with free text.
- Rules in `CLAUDE.md` alone help partly, because agents often don't open them. A check named in the task itself helps most.
- Across 15 agent-written projects the check found 540 dirty places, and 13 of the projects have no instruction about state, transitions or refusal codes.

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

## 15 agent-written projects

Open-source Python and TypeScript projects where a coding agent signed more than two thirds of the commits. The signature only gives a lower bound. Each project was checked whole with the skill on Sonnet, without running it.

| | |
|---|---|
| Candidates examined | 1220 |
| Dirty | 540 |
| Projects with no instruction on state, transitions or refusal codes | 13 of 15 |
| Risk scenarios confirmed by reading the code by hand, in 13 of the projects | 34 |
| Risk scenarios dropped by that reading | 4 |

So roughly one in ten of the strongest findings didn't survive a human-directed read. The 540 will contain mistakes too: only the strongest were read by hand.

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

### Fixes sent to the authors

| Project | Problem | Principle | Fix |
|---|---|---|---|
| prefect421/mvidarr | An anonymous `POST /skip` turned a finished setup wizard back into unfinished, which reopened endpoints that work without a login | transition with no check | [#582](https://github.com/prefect421/mvidarr/pull/582) |
| ander1044/wairz | A failed NVD lookup counted as "no CVEs", and later scans returned that as cached | unknown is not success | [#1](https://github.com/ander1044/wairz/pull/1) |
| omnivision-solutions/tuti | An upload stayed `PROCESSING` forever when the queue refused it | a wait with no way out | [#530](https://github.com/omnivision-solutions/tuti/pull/530) |

Each fix comes with a test that fails without it. These are open pull requests and the authors may decide otherwise.

## Bugs these projects already fixed

391 commits with "fix" or "bug" that touch statuses, error codes or exception handling, across four projects. 172 were classified by a model and the positive answers read by hand. In 24 of them (14%), following a principle would clearly have prevented the bug. Most often: a wait with no failure state, state derived from indirect signs, unknown counted as success, and a default substituted for a missing value.

- [revel-backend](https://github.com/letsrevel/revel-backend) `fffad3f`: token schemas filled in a default type, so a session token was accepted as a password-reset token. No agent signature on the commit that introduced it.
- [ai-trading-agent](https://github.com/flukelaster/ai-trading-agent) `8b2a9ba`: `except Exception: pass` hid an import error, and orders never reached the broker.
- [legalise](https://github.com/b1rdmania/legalise) `eed4b6c`: a transition function allowed a jump from any state.
