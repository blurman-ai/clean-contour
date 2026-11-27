# Field run report — branch glm-c21-field-run, base b04cc19, 27.11.2026

## What was done, by stage

**Stage 0 (orientation, baseline).** RULES.md / README / SKILL.md / structural_scan.py /
exam layout read (no AGENTS.md file exists in either tree — RULES.md is the doc projects
copy). Baseline on b04cc19: structural_scan selftest 8/8, search/cs_search selftests ok,
exam --check 497 fragments / 21 cards, exam --selftest 29/29. Journal: tmp/journal.md.

**Stage 1 (OSS corpus).** 10 new repos picked by measured agentic-commit trailer share
(GitHub API, last ~200 commits), activity, and production Python mass; rejects recorded
(aider stale 6 months, open-webui/ragflow/adk ~0% trailers, letta 5 weeks quiet).
OpenHands dropped later: a shallow 27.11 head is TypeScript (18 py files) — microsoft/autogen
took its slot. Clones in ~/projects/clean-contour-oss-2026-11-11/work/, never committed.

**Stage 2 (instrument, issues #25 #26 #27 #29 #30).** All five closed, one commit each,
every fix with a control case that the pre-fix code fails (verified by running sabotaged
copies): #25 UTF-8 pinning of the model pipe; #26 routing paragraph out of the exam prompt;
#27 HINT over the fragment path; #29 the 15–60 exam window documented as deliberate, new
cards aim at 30–60; #30 eight runner nits (selftest 29→37 cases, each former hardcoded-True
sensitivity leg now real).

**Stage 3 (new cards, issues #33–#36, #32).** Five cards, one commit each, full canon
(card text → signs for five languages + fixtures → corpus 10+10 → exam on deepseek-v4-flash
×3 worst counts → cheap list):

| Card | issue | exam (whole corpus, worst of 3) | notes |
|---|---|---|---|
| C22 no deadline | #33 | 10/10 dirty, 0/10 clean | — |
| C23 hidden side effect | #34 | 10/10, 0/10 after one clean fragment rewritten | the model judged a @property-with-own-SELECT dirty, which is what the card says; the fragment was mislabeled, card text untouched |
| C24 lost background failure | #35 | 10/10, 1/10 — exactly at the gate | the flagged fragment is the card's own Does-not-count case, read dirty once in three |
| C25 clock/RNG in a rule | #36 | first pass FAILED 8/10 recall, 2/10 false; after card clarification + corpus fixes: 10/10, 0/11 | the boundary caller and the writer-computed stored deadline are now named explicitly; one dirty fragment was authored wrong (GUID in the row key, not the idempotency key) |
| C26 env in business logic | #32 | 10/10, 0/10 | numbered C26, not C21: issue #32 asked for C21, but C21 was already taken by issue #39's card (measured, in the cheap list); renumbering recorded here and in README |

**Stage 4 (existing cards, issues #37 #28 #17).**
- #37: skip lists gain testkit/acceptance/experiments + fixture/harness/proof file names;
  walk_files prunes skipped directories in place (os.walk); check.py fragments widen up to
  14 lines to an enclosing header. Follow-up found in this field run: virtualenv trees were
  not skipped at all (committed separately, with a fixture tree as control).
- #28: Kotlin/Go signs for C12 and C13 (C13 Go declared not applicable), C14's Routes label
  named — the "every card names the signs" claim now holds.
- #17: C15 split into C15 (code not read) / C27 (one text for many causes) / C28 (client-
  declared code lists); C7 question 1 rewritten as a test the fragment answers. DeepSeek:
  C7 10/10+0/12, C15 10/10+0/10, C27 10/10+1/10, C28 9/10+1/10 — all four join the cheap
  list; strong list is now C1, C4, C8, C10, C14. The issue's "done when" asked for Sonnet —
  Sonnet is outside this run's model budget, the pass is DeepSeek-only, Haiku/Sonnet columns
  stand as of 11.11 and are marked not comparable.

**Stage 5 (corpora, issue #16).** Best effort, not closed: C26 grew to 16+16, C27 to
15+15, measured: C26 16/16 + 0/16, C27 14/15 + 1/15 — both inside the gate. The remaining cards are at 10+10 (C7 at 10+12); 30+30
everywhere did not fit the budget.

**Stage 6 (field corpus, issue #15).** Closed.
- C21: 1235 production candidates over twelve repos, model-judged, hand-curated:
  1228 clean / 4 unclear / 3 dirty. The three dirty places are hand-confirmed (two
  pydantic-ai `tasks()` overwriters, one agno SQL-CASE-over-finished_at). Field docs:
  field/2026-11-27/.
- C22–C26: 480 sampled places; 46+5+13+20+55 dirty verdicts by card; all small-card dirty
  sets and samples of the big ones hand-read; no model error found.
- Private-code recall: 129 sampled places over three repositories, 7 dirty, all 7 in the
  prefilter's output, vocabulary fallback added none — recall 7/7, gate ≥6/6 holds, no
  instrument change forced. Counters only; no private paths or names in the commit.

**Stage 7 (measurements).** #18 closed as a dated DeepSeek table for all 28 cards
(exam/results/2026-11-27/README.md), assembled from documented runs; one provider, no
mixing. #19 (rules experiment 30×3) — out of budget, stays open.

**Stage 8.** This report.

## Exam numbers, before and after

Corpus: 497 fragments / 21 cards → 660 fragments / 28 cards. Selftest: 29 → 37 cases.
All instrument selftests green at every commit (verified per commit before pushing the
commit in). Cheap list: 14 cards → 23 (C7 and C15 left the strong list after the #17
rewrite; C22–C28 joined). Strong list: C1, C4, C8, C10, C14.

## Field noise and recall

- Prefilter precision is low by design: 1235 flagged → 3 real C21 places on OSS; the mass
  is config mappers and projections the card correctly calls clean. The card on real code
  behaves like on the exam: the canonical fragment answers dirty through the same channel,
  and no hand read found a model error.
- Recall on private code: 7/7 on the sampled read-side (gate ≥6/6). Write-side recall is
  measurable only on the sampled slice (75 places, 0 dirty) — a limit, not a result.
- Endemic real-code patterns the cards now name: external calls without deadlines (C22,
  48% of sampled places), env reads at the point of use (C26, 57%), clock-at-decision-time
  expiry rules (C25, 22%).

## Contested decisions, with reasons

1. **C26 not C21** (issue #32's numbering): C21 was taken by issue #39's card, which is
   already measured and routed. Two cards cannot share a number; the next free number won.
2. **#29 alignment**: aligning the exam window to the live 30–60 would re-lengthen ~22
   fragments and break comparability with every past run; documented the deliberate window
   instead, and new cards aim at 30–60.
3. **#17 without Sonnet**: the issue's done-when names Sonnet; the run's hard model rule
   is DeepSeek-only. Measured on DeepSeek, the Sonnet column left unmeasured rather than
   mixed.
4. **C23-19/C25-07 relabels and C25 card wording**: in both cases the model's read matched
   the card's own questions; the fragments were rewritten or relabeled, the card text was
   only clarified where a whole class (boundary callers, writer-computed deadlines) had no
   name in the text.
5. **OpenHands → autogen**: the pick criterion said production Python; at a shallow 27.11
   head OpenHands is a TS repo. Replaced by the bench candidate and recorded.

## Not done (budget)

- #16: 30+30 fragments per card — only C26 (16+16) and C27 (15+15) were extended and
  measured; the rest stand at 10+10.
- #19: the rules experiment (30 tasks × 3 conditions) — not run; needs a task corpus and
  several full model passes.
- Haiku/Sonnet re-measurement after the split and the new cards.
- C24 field caveat: one verdict sits in a bundled `static/assets/*.js` — build output the
  search does not skip yet (recorded as instrument debt, not fixed in this run).
- The stage-3 cards were run on OSS samples (≤8 files per repo,card), not on every
  candidate: 61k raw hits are beyond any budget; the sampling follows the 24.11 protocol.
