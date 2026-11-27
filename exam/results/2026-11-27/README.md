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
"Does not count" names exactly this case; the false rate stays under the
threshold, so the fragment is kept as is.
