# Field run, 27 November 2026 — method

Corpus: twelve open-source Python repositories cloned shallow on 27.11.2026
into `~/projects/clean-contour-oss-2026-11-11/work/`, next to the three repos
of the 11.11 batch (prefect, crewAI, tuti). The ten new repos were picked by a
measured agentic-commit share (Co-authored-by Claude/Copilot/... trailers over
the last ~200 commits via the GitHub API), current activity (last commit days
before the run) and enough production Python; the picks, the numbers and the
rejects are in `tmp/journal.md` of the branch.

| Repo | why it is in |
|---|---|
| fastmcp | highest measured trailer share (31%), pure production Python |
| vllm | 20% trailers, large production Python (inference engine) |
| OpenHands | 16% trailers, agent-written — dropped: a shallow 27.11 head is TypeScript (18 py files); autogen takes the slot |
| browser-use | 10% trailers, active |
| pydantic-ai | 5.6% trailers, agent-heavy team |
| mem0 | 4.5% trailers |
| llama_index | 3.7% trailers, large production Python |
| dspy | 2.2% trailers |
| langchain | 1.1% measured (squash-merge hides trailers); the canonical langchain ecosystem |
| agno | 1.3% measured (Copilot bot merges); very high commit velocity |
| autogen | bench replacement for OpenHands, 2.1% trailers |
| prefect, crewAI, tuti | from the 11.11 batch; tuti contributes no Python (C#) |

Pipeline.

1. `tools/structural_scan.py` (the C21 structural prefilter, no field
   vocabulary) over every repo: raw 4053 candidates; test/bench/venv paths
   filtered → production candidates.
2. Every production candidate becomes a 45-line fragment around the flagged
   function; deepseek-v4-flash (through `pi`) answers the C21 questions —
   dev/holdout do not apply here, this is a field exam on real places.
3. Every `dirty` and `unclear` verdict is read by hand against the source, as
   is a sample of `clean`; the counts below carry the curated numbers.
4. Cards C22–C26 of stage 3 run over the same repos: `tools/search.py`
   candidates per card, up to 8 distinct files per (repo, card) following the
   24.11 protocol, the same model, hand-curated.
5. Recall of the instruments on private code (dgtlu_backend, cogline, ldgn):
   stratified hand reads + a vocabulary fallback grep for shapes the AST
   prefilter cannot see; anonymized counters only.

Tool changes the run fed back into the instrument (each with a control case):
virtualenv trees were not skipped by `search.py` (6a93888); test-harness
paths (`integration-tests/`, `benches/`) needed segment-anchored skip
patterns — the #37 skip extensions (c715c06).
