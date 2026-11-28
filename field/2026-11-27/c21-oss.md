# Field measurement, 27 November 2026 — C21 over the OSS corpus

Twelve Python repositories (method: `method.md`), unique path-filtered
candidates of the structural prefilter (`tools/structural_scan.py`), every one
judged by deepseek-v4-flash against the C21 card. The saved rows were recounted
on 28.11 after removing tests, docs, examples, benchmarks, harnesses, fixtures
and duplicate hits of the same function.

Raw prefilter output: 4053 candidates. After path filtering and deduplication:
**1235 unique candidates** — 94 read-side and 1141 write-side. Model verdicts:

| Repo | n | dirty | clean | unclear |
|---|---:|---:|---:|---:|
| prefect | 128 | 0 | 128 | 0 |
| crewAI | 77 | 0 | 75 | 2 |
| fastmcp | 36 | 0 | 35 | 1 |
| vllm | 151 | 0 | 151 | 0 |
| browser-use | 36 | 0 | 36 | 0 |
| pydantic-ai | 324 | 2 | 322 | 0 |
| mem0 | 34 | 0 | 34 | 0 |
| llama_index | 43 | 0 | 43 | 0 |
| dspy | 44 | 0 | 44 | 0 |
| langchain | 24 | 0 | 24 | 0 |
| agno | 316 | 1 | 314 | 1 |
| autogen | 22 | 0 | 22 | 0 |
| **total** | **1235** | **3** | **1228** | **4** |

All three model-dirty verdicts are on the **write side**, not the read side as
the first version of this note said. Direct review on 28.11 confirms one and
reclassifies two:

| Place | review verdict | what comes from where |
|---|---|---|
| `agno/libs/agno/agno/db/sqlite/sqlite.py:3218` | **dirty, confirmed** | in the stopped-refresh branch the row's `status` is written by a SQL `CASE` over `finished_at is not null`; the completion timestamp chooses completed/failed instead of a stored outcome of the calculation |
| `pydantic-ai/src/pydantic_ai_pax/pydantic_ai_pax/runtime/codex_sessions.py:205` | not counted | the importer constructs the task with `outcome='ok'` at the boundary and then uses absence of a final answer to make it `cancelled`; no pre-existing stored lifecycle state of the imported entity is visible, so C21 question 3 is not a yes |
| `pydantic-ai/src/pydantic_ai_pax/pydantic_ai_pax/runtime/claude_code_sessions.py:148` | not counted | same boundary-import shape as the Codex twin |

The confirmed dirty count is therefore **1 of 1235**, not 3 of 1235. The two
pydantic-ai rows remain useful borderline examples for the card: a model reads
“overwrite `outcome`” as an override of stored state even when that stored
value was manufactured in the same import step.

The four `unclear` places are context gaps, not verdicts: a helper whose body
is outside the 45-line fragment (`crewai/a2a/task_helpers.py:138`,
`crewai/a2a/wrapper.py:1068`), a caller-supplied status whose origin lies
elsewhere (`fastmcp_tasks/handlers.py:285`), and a state chosen inside a
function the fragment only names (`agno/os/interfaces/a2a/executor.py:60`).

Read-side and write-side:

- **Read side:** 94 candidates, 94 clean, no model-dirty and no unclear. The
  scan found no OSS read-side projection comparable to the private-code
  artifact-over-state projections in this sample.
- **Write side:** 1141 candidates, 1134 clean, 4 unclear, 3 model-dirty of
  which 1 held up on review. Most conditional lifecycle-literal writers are
  transition tables and worker queues, which the card's “does not count”
  absorbs.

The raw model rows are in `/tmp/field_scan/c21_final.jsonl` on the machine
where the run was made; they are not committed. Per-row hand-curation verdicts
were not recorded as data during the original run, so only the rows re-read on
28.11 are treated as curated here.
