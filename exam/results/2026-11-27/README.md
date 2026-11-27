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


## C22 on a weak model

C22 (an external call without a deadline) was measured on deepseek-v4-flash
through `pi`, 3 answers per fragment, worst answer counts, whole corpus
(20 fragments x 3 = 60 calls):

| Card | dirty found | recall | clean flagged | false | 90/10 |
|---|---:|---:|---:|---:|---|
| C22 | 10/10 | 100% | 0/10 | 0% | PASS |

Report: `exam/runs/2026-11-27-deepseek-c22.json`. C22 joins the cheap list in
`routing.json`.

## C23 on a weak model

C23 (a side effect hidden in a constructor, a getter, or an ORM hook) was
measured the same way (deepseek-v4-flash, 3 answers per fragment, worst
counts, whole corpus). The first pass flagged the clean C23-19 3/3 — a
@property that ran its own SELECT per access — and a careful read sides with
the model: the card's question 2 counts any own database statement in a
getter, reads included. The fragment was rewritten to the card's clean case
(a property over fields handed in at construction) and the card text was not
weakened. Re-run on the fixed corpus: 10/10 dirty found, 0/10 clean flagged.

Reports: `exam/runs/2026-11-27-deepseek-c23.json` (first pass, 1 clean
flagged), `exam/runs/2026-11-27-deepseek-c23-fix.json` (final). C23 joins the
cheap list in `routing.json`.

## C24 on a weak model

C24 (a background task whose failure is lost) measured the same way
(deepseek-v4-flash, 3 answers per fragment, worst counts, whole corpus):
10/10 dirty found, 1/10 clean flagged — exactly the 10% the gate allows.
The flagged clean fragment is the guarded thread whose body catches and
records the failure (the card's own Does-not-count case); two of three
answers read it clean, one read the fire-and-forget start and stopped
reading. Borderline but inside the gate; the card joins the cheap list.
One answer on a dirty fragment wavered between dirty and unclear (unstable
column), all three still landed dirty.

Report: `exam/runs/2026-11-27-deepseek-c24.json`.

## C25 on a weak model

C25 (the clock or the random generator called inside a rule) failed the first
pass: recall 8/10 — the boundary caller `apply = judge(coupon, Instant.now())`
was authored as dirty while two answers read it clean (the rule itself takes
the moment as a parameter), and C25-10 was authored wrong (the GUID filled the
row's primary key, not the idempotency key); false 2/10 — two clean fragments
were writers computing a stored deadline (`valid_until`, `holds_until`) from
the clock, and the card had no writer-deadline exemption. The card text was
clarified, not weakened into vagueness: question 1 targets the rule that
decides (a thin boundary caller handing the value in is not the rule), and
Does-not-count now names the writer computing a stored deadline as transition
data. C25-07 relabeled clean, C25-10 fixed so the GUID is the idempotency key
per attempt, C25-21 added (the rule reads the clock itself, Kotlin). Re-run on
deepseek-v4-flash, same settings: 10/10 dirty found, 0/11 clean flagged.

Reports: `exam/runs/2026-11-27-deepseek-c25.json` (first pass, fail),
`exam/runs/2026-11-27-deepseek-c25-fix.json` (final). C25 joins the cheap
list in `routing.json`.
