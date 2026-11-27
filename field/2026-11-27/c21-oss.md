# Field run, 27 November 2026 — C21 over the OSS corpus

Twelve python repositories (method: `method.md`), production candidates of the
structural prefilter (`tools/structural_scan.py`), every one judged by
deepseek-v4-flash against the C21 card, every `dirty` and `unclear` verdict
read by hand against the source, plus a sample of `clean` (12 places read
across prefect, vllm, crewAI, fastmcp, browser-use, mem0).

Raw prefilter output 4053 candidates; after test/bench/example/venv filtering
— **1235 production candidates**. Model verdicts, hand-curated:

| Repo | n | dirty | clean | unclear |
|---|---:|---:|---:|---:|
| prefect | 129 | 0 | 129 | 0 |
| crewAI | 77 | 0 | 75 | 2 |
| fastmcp | 45 | 0 | 44 | 1 |
| vllm | 168 | 0 | 168 | 0 |
| browser-use | 36 | 0 | 36 | 0 |
| pydantic-ai | 358 | 2 | 356 | 0 |
| mem0 | 34 | 0 | 34 | 0 |
| llama_index | 45 | 0 | 45 | 0 |
| dspy | 48 | 0 | 48 | 0 |
| langchain | 25 | 0 | 25 | 0 |
| agno | 319 | 1 | 316 | 2 |
| autogen | 22 | 0 | 22 | 0 |
| **total** | **1235** | **3** | **1228** | **4** |

The dirty places (verdict, then one line: what comes from where):

| Place | verdict | what comes from where |
|---|---|---|
| `pydantic-ai/src/pydantic_ai_pax/pydantic_ai_pax/runtime/codex_sessions.py:210` | dirty | the task row keeps an `outcome`, but `tasks()` overwrites it with `cancelled` whenever the final answer is not found in the session log — the derived artifact outranks the stored state |
| `pydantic-ai/src/pydantic_ai_pax/pydantic_ai_pax/runtime/claude_code_sessions.py:153` | dirty | same shape in the Claude Code twin: `output is None` turns a delivered task into `cancelled` no matter what its stored outcome says |
| `agno/libs/agno/agno/db/sqlite/sqlite.py:3274` | dirty | the metrics-refresh row's `status` is written from a SQL `CASE` over `finished_at is not null` — the completion timestamp chooses completed/failed instead of the outcome the calculation knew |

The four `unclear` places are context gaps, not verdicts: a helper whose body
is outside the 45-line fragment (`crewai/a2a/task_helpers.py:138`,
`crewai/a2a/wrapper.py:1068`), a caller-supplied status whose origin lies
elsewhere (`fastmcp_tasks/handlers.py:285`), and a state chosen inside a
function the fragment only names (`agno/os/interfaces/a2a/executor.py:60`).

Read-side and write-side: the three dirty places are read-side. The scan's
write-side slice produced 635 candidates on pydantic-ai, 188 on ldgn-style
repos and none here survived the card: writers passing a lifecycle literal
under a condition are dominated by transition tables and worker queues, which
the card's "does not count" correctly absorbs.

Model behavior on real code: the canonical exam fragment still answers
`dirty | yes, yes, yes` through the same channel (verified before the run),
and hand reads of 12 `clean` verdicts and all `dirty`/`unclear` found no
model error — the mass of `clean` is the prefilter's known low precision, not
a lazy model: the flagged functions are config mappers, projections and view
builders that return lifecycle-shaped values from non-state inputs.
