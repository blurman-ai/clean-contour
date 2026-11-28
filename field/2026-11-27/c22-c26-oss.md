# Field measurement, 27 November 2026 — the stage-3 cards over the OSS corpus

Cards C22–C26 ran over the same twelve repositories. Protocol followed the
24.11 field run shape: `tools/search.py` candidates per (repo, card), up to 8
distinct files sampled per (repo, card), deepseek-v4-flash judged each fragment.
480 model answers were collected, 96 per card.

The table below recounts the saved rows after removing tests, docs, examples,
benchmarks, harnesses and fixtures by path. **453 verdicts remain.** This is
still a repository sample, not a production-only rate: `cookbook/`, `scripts/`,
`.github/`, vendored code, frontend code and generated static assets remain in
it. Use the dirty sets as places to inspect, not as incidence rates of production
code.

| Card | n | dirty | clean | unclear | what the dirty set is |
|---|---:|---:|---:|---:|---|
| C22 no deadline | 86 | 46 | 40 | 0 | `requests`/`fetch`/`http.Get`/`subprocess` without a `timeout=`/signal — dominated by subprocess calls to git/gh, provider fetches and frontend API helpers |
| C23 hidden side effect | 95 | 5 | 78 | 12 | constructors that open SQLite, call the Hub/GitLab API, or load ML models; the unclears are constructors whose callee bodies lie outside the fragment |
| C24 lost background failure | 91 | 13 | 65 | 13 | dropped `asyncio.create_task`, daemon threads without a handler, `void navigate(...)` in TSX; one verdict sits in bundled `static/assets/app.js` — build output the search should also skip |
| C25 clock/RNG in a rule | 93 | 20 | 73 | 0 | cache-, token- and retry-expiry rules comparing a stored deadline to `time.time()`/`Date.now()`/`datetime.now()` at decision time |
| C26 env in business logic | 88 | 55 | 32 | 1 | provider API keys and base URLs read by `os.getenv`/equivalent inside providers and tools, plus feature flags; the largest set, and the one whose boundary with configuration modules most often needs human judgment |
| **total** | **453** | **139** | **288** | **26** | |

The raw model rows are in `/tmp/field_scan/c22_26_final.jsonl` on the machine
where the run was made; they are not committed. The per-row hand-curation
verdicts were not recorded as data, so the committed table cannot be audited
row by row. A spot review after the run confirmed the shape of the largest
sets, but also found boundary cases — especially C26 reads used for telemetry
or provider-library configuration — that should be argued individually rather
than counted as automatic debt.

Examples that held up on direct reading:

- C22: `autogen-studio/frontend/src/components/views/playground/api.ts` calls
  `fetch` without an `AbortSignal`; `prefect/src/prefect/_internal/git.py`
  calls `subprocess.check_output` without `timeout=`.
- C23: `crewai/memory/storage/kickoff_task_outputs_storage.py` opens and
  initializes SQLite in the constructor; `langchain_classic/runnables/hub.py`
  pulls a prompt from the Hub in the constructor.
- C24: `autogenstudio/lite/studio.py` starts a daemon browser-opening thread
  with no error recording; `pydantic_ai_pax/gh_cli.py` starts a reader thread
  with no join, callback or registry.
- C25: `fastmcp/utilities/token_cache.py` decides cache expiry with a direct
  `time.time()`; `pydantic_ai/providers/openai_chatgpt.py` decides token
  expiry with `datetime.now(UTC)`.
- C26: provider constructors such as `pydantic_ai/providers/stav.py` and
  `vllm.py` read API keys and base URLs from the environment as fallbacks.
  Whether this library convention is debt or an intentional configuration
  boundary is a design decision; the card marks the shape, not the project's
  policy answer.

Two caveats the run feeds back: vendored build output (`static/assets/*.js`) is
not yet skipped by the search signs, and `benches/`/`integration-tests/` needed
the segment-anchored skip patterns added in the #37 work.
