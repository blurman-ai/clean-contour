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
