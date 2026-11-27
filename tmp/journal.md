# Field run journal — branch glm-c21-field-run

Base: b04cc19 (feat: structural prefilter for C21 read-side and write-side shapes), local main.
Started 2026-11-27.

## Stage 0 — orientation and baseline instruments

Docs read: RULES.md (17 principles), README.md, skills/clean-contour-check/SKILL.md
(21 cards C1–C21), tools/structural_scan.py, exam/README.md, exam/results/2026-11-2{4,7}.
No AGENTS.md file exists in either tree (checked both); RULES.md is the rule doc
projects copy in. Noted: `exam/runs/` is gitignored — run JSONs stay local.

Baseline selftests, all green on b04cc19:

| Instrument | Result |
|---|---|
| `tools/structural_scan.py --selftest` | 8/8 |
| `tools/search.py --selftest` | ok |
| `tools/cs_search.py --selftest` | ok (exit 0) |
| `exam/bin/exam --check` | corpus valid: 497 fragments, 21 cards |
| `exam/bin/exam --selftest` | 29 of 29 passed |

Model channel: `pi -p --provider deepseek --model deepseek-chat --no-session --no-tools`,
`pi auth check --provider deepseek` → ready; stdin→stdout contract verified with a live call.

## Stage 1 — OSS corpus: candidate check and selection

Method: last ~200 commits of each candidate repo via GitHub API (commits endpoint,
2 pages), counting Co-authored-by: Claude/Copilot/Codex/... trailers, "Generated with",
robot emoji, agent sign-offs. Two passes (line-level and commit-level); numbers below
are the line-level pass over ~200 latest commit messages.

| Candidate | agentic hits / message lines | last commit | verdict |
|---|---|---|---|
| jlowin/fastmcp | 212/680 (31%) | 2026-11-26 | **take** |
| vllm-project/vllm | 114/573 (20%) | 2026-11-27 | **take** |
| All-Hands-AI/OpenHands | 75/477 (16%) | 2026-11-27 | **take** |
| browser-use/browser-use | 145/1434 (10%) | 2026-11-27 | **take** |
| pydantic/pydantic-ai | 14/251 (5.6%) | 2026-11-27 | **take** |
| mem0ai/mem0 | 11/247 (4.5%) | 2026-11-27 | **take** |
| run-llama/llama_index | 25/677 (3.7%) | 2026-11-26 | **take** |
| stanfordnlp/dspy | 55/2511 (2.2%) | 2026-11-25 | **take** |
| langchain-ai/langchain | 38/3322 (1.1%) | 2026-11-26 | **take** — squash-merge queue hides trailers; canonical langchain ecosystem, huge production Python |
| agno-agi/agno | 140/11091 (1.3%) | 2026-11-27 | **take** — Copilot bot merges hide trailers; very high commit velocity, large production Python |

Rejected on facts: Aider-AI/aider (15% trailers but last commit 2026-05-22 — not active),
letta-ai/letta (3%, last commit 2026-10-18), open-webui (0% trailers, mostly Svelte frontend),
langgraph (0.1%), google/adk-python (0%, squash), infiniflow/ragflow (0%),
microsoft/autogen (2.1%), deepset-ai/haystack (4%), modelcontextprotocol/python-sdk (1.6%) —
bench list in case a take fails.

Clones: `git clone --depth 1` into ~/projects/clean-contour-oss-2026-11-11/work/,
next to the existing prefect, crewAI, tuti. Clones are never committed.

## Stage 2 — exam instrument fixes (issues #25, #26, #27, #29, #30)

All five committed, one commit per issue, each fix with a control case that
the pre-fix code fails (verified by running a sabotaged copy in-process):

- #25 d2b81b5: model pipe pinned to UTF-8 (encoding='utf-8', errors='replace'),
  UnicodeError → call error (void 2). Control: a real pipe run in a child with
  UTF-8 mode off + locale patched to cp1252 breaks on ₽; this machine has
  PYTHONUTF8=1 globally, so the sensitivity leg must run in the child.
- #26 99312de: 'Which cards go to whom' paragraph moved below the --- after
  Procedure; parse_skill stops there, prompts stay clean. Control: paragraph
  re-inserted inside Procedure → prompt contains it → case red.
- #27 cef1744: HINT covers path (segment-bounded; src/cleanup/ stays legal).
  Control: path src/order/dirty_helpers.ts refused.
- #29 244cb31: the 15–60 exam window documented as deliberate (vs live 30–60);
  new cards aim at 30–60 where the scenario allows. Decision, no behavior change.
- #30 3f14088: eight nits — sabotage anchors in the card body; ASCII output;
  real sensitivity switches (expectations=, unique_ids=, file_cards=,
  Policy(max_false) for oracle-false); negated verdicts ('not clean') no
  longer parse as verdicts; failure listing shows the decisive answer; no
  sleep after the final attempt; report-write failure → void exit 2 (case runs
  a sabotaged copy showing the pre-fix traceback rc=1); corpus file name must
  match the card. Selftest 29 → 37 cases.

## Stage 3 — new cards (issues #33–#36, #32)

Numbering: issue #32's env card wanted 'C21', but C21 is taken by the card
from issue #39 (already measured, in the cheap list). The env card is C26,
the next free number; recorded here and in the report as a forced renumber.
Cards are done in ascending numeric order C22→C26 so the search selftest's
contiguous C1..C<N> range check stays green per commit.

- C22 (#33) 1dbc89f: external call without a deadline. Exam deepseek-v4-flash,
  whole corpus ×3 worst counts: 10/10 dirty, 0/10 clean → cheap list.
- C23 (#34) ed8f465: side effect in constructor/getter/ORM hook. First pass
  1/10 clean flagged: the model called @property-with-own-SELECT dirty, which
  is what the card's question 2 says — the fragment was mislabeled, rewritten
  to the card's clean case (card text untouched). Re-run: 10/10, 0/10 → cheap.
- C24 (#35) 0e37e15: background task with lost failure. 10/10 dirty, 1/10
  clean flagged = exactly the 10% gate (the flagged fragment is the card's own
  Does-not-count case, read dirty once in three). Pass → cheap list.
- C25 (#36): first pass FAILED — recall 8/10 (C25-07 boundary-caller read as
  clean; C25-10 was authored wrong: the GUID filled the row key, not the
  idempotency key) and 2/10 clean flagged (C25-12/C25-18: writers computing a
  stored deadline; the card had no writer-deadline exemption). Card text
  clarified: Q1 targets the rule itself (a thin boundary caller handing the
  value in is not the rule), does-not-count gains the writer-computing-stored-
  deadline case; C25-07 relabeled clean, C25-10 fixed to make the GUID the
  idempotency key, C25-21 (kt, rule reads the clock itself) added. Re-run
  pending.
- C26 (#32): environment variable reads inside business logic. Artifacts
  staged, exam pending.

## Stage 4 — existing card work (issues #37, #28, #17)

- #37 c715c06: skip lists gain testkit/acceptance/experiments + fixture/harness/
  proof file names (anchored to the last path segment so this repo's own
  tools/fixtures/ is not skipped whole); walk_files prunes directories in
  place with os.walk; check.py fragments widen up to 14 lines to include the
  topmost enclosing header above the centred window. Follow-up 6a93888: the
  skip lists had no .venv/venv — found when the field dumps carried
  site-packages candidates from a vendored virtualenv.
- #28 b43b630: Kotlin/Go signs for C12 and C13 (Compose getters/ladders,
  FuncMap/template ladders, lifecycleScope two-way writes; C13 Go declared
  not applicable), C14's Routes label named.
- #17 88b9025: C15 split into C15 (code not read) + C27 (one text for many
  causes) + C28 (client-declared code lists); C7 Q1 rewritten as a fragment
  test. DeepSeek: C7 10/10+0/12, C15 10/10+0/10, C27 10/10+1/10, C28 9/10+
  1/10 — all four pass, C7/C15/C27/C28 join the cheap list, strong list is
  C1/C4/C8/C10/C14. Two corpus corrections (C7-04/C7-10 were display-only,
  contradicting the card's own does-not-count; the first C27 clean set folded
  unknowns, contradicting Q2). Sonnet unmeasured — out of model budget.

## Stage 6 — field run (in progress)

Corpus: 12 python repos (prefect, crewAI, fastmcp, vllm, browser-use,
pydantic-ai, mem0, llama_index, dspy, langchain, agno, autogen; OpenHands
dropped — TS at HEAD). Structural prefilter raw 4053 → production 1319.
Pipeline: structural_scan candidates → 30–60-line fragments → deepseek-v4-
flash judges C21 questions → I curate every dirty/unclear and a sample of
clean. C22–C26: search.py candidates per repo, ≤8 distinct files per
(repo, card) following the 24.11 protocol (~480 sampled). idealab
(dgtlu_backend/cogline/ldgn): stratified samples (all read-side + 25
write-side per repo = 129) for recall checks; vocabulary fallback grep for
prefilter blind spots; anonymized counters only in commits.

## Final state (27.11, end of run)

Chain b04cc19..HEAD: 20 commits, one per issue/stage as planned. Issues
closed: #25 #26 #27 #29 #30 (stage 2), #33 #34 #35 #36 #32 (stage 3),
#37 #28 #17 (stage 4), #15 (stage 6), #18 (stage 7, table). Partial: #16
(C26 16+16, C27 15+15 measured; rest at 10+10). Open: #19 (out of budget),
#12-adjacent Haiku/Sonnet re-measurement. Field docs: field/2026-11-27/
(method, c21-oss, c22-c26-oss, recall-private). Final corpus 660 fragments /
28 cards; cheap list 23 cards; strong list C1/C4/C8/C10/C14.
