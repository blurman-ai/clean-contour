# Field run, 27 November 2026 — instrument recall on private code

Counters only: no paths, names or fragments of the private repositories leave
this file. Three python repositories were read (read-only): one large backend
(666 production prefilter candidates), one mid-size backend (70) and one
content-engine backend (203).

Sample: every read-side candidate (31/8/15) plus 25 random write-side
candidates per repository — 129 places. deepseek-v4-flash judged each with
the C21 card; every dirty verdict was read by hand against the source, 9
clean verdicts were spot-read, and a vocabulary fallback grep (artifact and
completion fields near state literals — the shapes the AST prefilter cannot
see) was run over all production files of the large backend (5 hits, read by
hand).

| Repository | sampled | model dirty | hand-confirmed dirty | prefilter missed |
|---|---:|---:|---:|---:|
| large backend | 56 | 2 | 2 | 0 |
| mid-size backend | 33 | 2 | 2 | 0 |
| content engine | 40 | 3 | 3 | 0 |
| **total** | **129** | **7** | **7** | **0** |

Recall of the instrument (prefilter + card) on the sampled read-side: 7/7 —
every hand-confirmed dirty place was in the prefilter's output, and the
vocabulary fallback added no dirty place the prefilter missed. The gate from
the plan ("recall on known places not below 6/6") holds, so no instrument
change was forced by the private code.

What the 7 are, without naming anything: two repositories derive a stage
status from artifact-presence booleans (`has_script`/`has_voiceover`/
`has_master`) ahead of the stored stage; one derives a payload state from
`audio_url`/`audio_path` presence; one lets an `extraction_error` outrank the
stored extraction status for the quarantine branch; one shows a check
verdict from `result_status` while the attempt's stored `status` says it is
not finished. All seven are read-side projections that the write-side sweep
(the single writer) does not fix: the stored field is written correctly, the
reads still consult the artifact first.

Limits: write-side recall is measured only on the sampled slice (75 of ~890
candidates; no dirty found there), and the sample covers the whole read-side
output of all three repositories.
