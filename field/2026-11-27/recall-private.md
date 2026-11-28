# Field measurement, 27 November 2026 — C21 on private code

Counters only: no paths, names or fragments of the private repositories leave
this file. Three Python repositories were read (read-only): one large backend
(666 production prefilter candidates after path filtering), one mid-size
backend (70) and one content-engine backend (203).

Sample: every read-side candidate that survived the path filter (31/8/15) plus
25 write-side candidates per repository — 129 places. deepseek-v4-flash judged
each with the C21 card; every dirty verdict was read by hand against the
source, 9 clean verdicts were spot-read, and a vocabulary fallback grep
(artifact and completion fields near state literals — the shapes the AST
prefilter cannot see) was run over the production files of the large backend
(5 hits, read by hand).

| Repository | sampled | model dirty | hand-confirmed dirty | prefilter missed |
|---|---:|---:|---:|---:|
| large backend | 56 | 2 | 2 | 0 |
| mid-size backend | 33 | 2 | 2 | 0 |
| content engine | 40 | 3 | 2 | 0 |
| **total** | **129** | **7** | **6** | **0** |

One model-dirty verdict in the content engine was a false positive caused by
the fragment window: the candidate function itself reads the stored step
status, while the artifact-derived branch belongs to the neighboring function
visible in the same fragment. It is not a second defect at that address.

What the 6 confirmed places are, without naming anything: one derives a
payload state from `audio_url`/`audio_path` presence; one shows a check verdict
from `result_status` while the attempt's stored `status` says it is not
finished; one lets an `extraction_error` outrank the stored extraction status
for the quarantine branch; one lets the same extraction error outrank the
published asset status for a no-text display state; two derive stage status
from artifact-presence booleans (`has_script`/`has_voiceover`/`has_master`)
ahead of the stored stage/run state. All six are read-side projections: the
stored field is written elsewhere, but the read still consults the artifact or
outcome first.

This run does **not** justify the originally reported “recall 7/7”. The sample
is drawn from the prefilter's own output, so it measures model precision on
those candidates, not prefilter recall. The only independent recall probe is
the vocabulary fallback over the large backend, and it added no dirty place.
That is evidence in favor of the prefilter, not a 7/7 recall measurement.
Write-side coverage is also thin: 75 of ~890 write-side candidates, with no
dirty place found in that slice.
