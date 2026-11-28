# Field run, 27 November 2026 — method

Corpus: twelve open-source Python repositories cloned shallow on 27.11.2026
into `~/projects/clean-contour-oss-2026-11-11/work/`, next to the three repos
of the 11.11 batch (prefect, crewAI, tuti). The ten new repos were picked by a
measured agentic-commit share (Co-authored-by Claude/Copilot/... trailers over
the last ~200 commits via the GitHub API), current activity (last commit days
before the run) and enough production Python; the picks and the numbers are in the table below;
the rejects were aider (stale), open-webui/ragflow/adk (no measured agentic trailers)
and letta (inactive for five weeks).

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
   filtered → path-filtered candidates.
2. Every path-filtered candidate becomes a 45-line fragment around the flagged
   function; deepseek-v4-flash (through `pi`) answers the C21 questions —
   dev/holdout do not apply here, this is a field exam on real places.
3. Dirty and unclear rows are the rows to re-read by hand. The original run
   did not record per-row curation as data; the published note therefore
   separates model verdicts from rows actually re-read.
4. Cards C22–C26 of stage 3 run over the same repos: `tools/search.py`
   candidates per card, up to 8 distinct files per (repo, card) following the
   24.11 protocol, the same model. The first sampling pass still let
   cookbook/script/vendor/build-output paths through; the published table
   therefore reports a repository sample, not a production-only rate.
5. Private code (dgtlu_backend, cogline, ldgn): stratified reads of the
   prefilter output plus a vocabulary fallback grep for shapes the AST
   prefilter cannot see; anonymized counters only. This measures precision
   on the prefilter output and gives a narrow recall probe, not a full recall
   measurement.

Tool changes the run fed back into the instrument (each with a control case):
virtualenv trees were not skipped by `search.py` (6a93888); test-harness
paths (`integration-tests/`, `benches/`) needed segment-anchored skip
patterns — the #37 skip extensions (c715c06).


Issue #15 is not closed by this run: it asks for `exam/corpus-field/C<N>.yaml`
fragments extracted from pinned commits and a model table over that corpus.
This run produced field measurements and notes, not that corpus.
