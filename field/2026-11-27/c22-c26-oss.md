# Field run, 27 November 2026 — the stage-3 cards over the OSS corpus

Cards C22–C26 run over the same twelve repositories. Protocol follows the
24.11 field run: `tools/search.py` candidates per (repo, card), up to 8
distinct files sampled per (repo, card), test/bench/example files excluded at
sampling, deepseek-v4-flash judges each fragment, hand-curated. 480 places.

| Card | n | dirty | clean | unclear | what the dirty set is |
|---|---:|---:|---:|---:|---|
| C22 no deadline | 96 | 54 | 42 | 0 | `requests`/`fetch`/`http.Get`/`subprocess` without a `timeout=`/signal — endemic; dominated by subprocess calls to git/gh and provider fetches |
| C23 hidden side effect | 96 | 5 | 78 | 12 | constructors that open SQLite, call the Hub API, load ML models; the unclears are constructors whose callee bodies lie outside the fragment |
| C24 lost background failure | 96 | 13 | 65 | 13 | dropped `asyncio.create_task`, naked `go func`, daemon threads without a handler, `void navigate(...)` in TSX; one verdict sits in a bundled `static/assets/app.js` — build output the search should also skip |
| C25 clock/RNG in a rule | 96 | 20 | 73 | 0 | cache- and token-expiry rules comparing a stored deadline to `time.time()`/`Date.now()` at decision time; the pattern is endemic and its status as debt is a policy call — the card verdict stands |
| C26 env in business logic | 96 | 58 | 37 | 1 | provider API keys and base URLs read by `os.getenv` inside tools/providers, feature flags at the rule; the largest set, and the most actionable one |

Hand reads: all 5 C23, all 13 C24, all 20 C25 dirty verdicts, 8 of the 54
C22 and 8 of the 58 C26 dirty verdicts, and 9 of the 26 unclear verdicts were
read against the source; no model error found. Two caveats the run feeds
back: vendored build output (`static/assets/*.js`) is not yet skipped by the
search signs, and `benches/`/`integration-tests/` needed the segment-anchored
skip patterns added in the #37 work.
