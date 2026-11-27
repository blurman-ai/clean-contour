# Exam run, 27 November 2026

Measurement of C18–C20 after the corpus of the three cards was extended from
Python-only to five languages: 10 new fragments per card (4 TypeScript, 2
Kotlin, 2 Go, 2 C#), half dirty and half clean. Each new fragment is the same
scenario as one of the Python originals, rewritten idiomatically; every dirty
fragment carries at least one search sign of its language from `signs.json`.
The cards' search sections in `SKILL.md` gained the missing `**C#:**` notes and
fuller Kotlin/Go notes in the same pass.

Run: `bin/exam --cards C18,C19,C20 --repeat 3` on deepseek-v4-flash (worst
answer of 3 counts), whole corpus, 90 fragments × 3 = 270 calls. Report:
`exam/runs/2026-11-27-deepseek-c18-c20.json`.

| Card | dirty found | recall | clean flagged | false | 90/10 |
|---|---:|---:|---:|---:|---|
| C18 | 15/15 | 100% | 0/15 | 0% | PASS |
| C19 | 15/15 | 100% | 0/15 | 0% | PASS |
| C20 | 15/15 | 100% | 1/15 | 7% | PASS |

All 30 new fragments answered the same in all three repeats: every dirty one
found 3/3, every clean one left alone 3/3, in TypeScript, Kotlin, Go and C#
alike.

The one flagged clean fragment is the older Python C20-15 (`app/service.py`,
single environment values at the composition root), answered dirty once in
three: the model called the separate accessors "no single decoder". The card's
"Does not count" names exactly this case, but the wording "one scalar
environment variable" read as exactly-one.

Follow-up the same day: the exclusion was reworded to "scalar environment
variables read into typed parameters, even several of them", and the C20
python signs gained `reply`/`response` next to `payload`/`body`/`raw` — the
card's search text names "a reply of another system", and the dirty C20-04
reads exactly such a variable. C20 was re-measured with the new card text,
same model and settings (`exam/runs/2026-11-27-deepseek-c20-envfix.json`):
15/15 dirty found, 0/15 clean flagged, and C20-15 is clean in all three
answers. The widened signs add no hits in any clean fragment of the corpus.

## C21 on a weak model

C21 (state derived from another field of the same entity) was measured on
deepseek-v4-flash through `claude-ds`, 3 answers per fragment, worst answer
counts. Dev and holdout are disjoint and together cover the card's 30 fragments.

| Run | dirty found | recall | clean flagged | false | 90/10 |
|---|---:|---:|---:|---:|---|
| deepseek-v4-flash, dev × 3, C21 | 10/10 | 100% | 0/10 | 0% | PASS |
| deepseek-v4-flash, holdout × 3, C21 | 5/5 | 100% | 0/5 | 0% | PASS |

Reports: `exam/runs/2026-11-27-deepseek-c21-dev.json` and
`exam/runs/2026-11-27-deepseek-c21-holdout.json`. The exact
`engine_payload_state` fragment from issue #39 was also checked separately and
answered `dirty` (`yes, yes, yes`). C21 joins the cheap list in `routing.json`.

