# Exam runs, 24 November 2026

Two measurements, both on the upstream corpus and cards at `9a70fd8`:

1. **The three new cards C18–C20** (60 new fragments, 10 dirty + 10 clean each),
   measured with `bin/exam` before they were added to the cheap list.
2. **The discriminator judge Jev (`jev-latest`, TypeSafe AI)** over the existing
   C1–C17 corpus, measured through `tools/jev_judge.py`.

The full JSON reports stay out of the repository (`exam/runs/` is ignored);
rerun a card to get the raw answers.

## C18–C20 on a weak model and on Jev

Each card was edited while looking at `--split dev` only (three iterations);
the pass that counts is `--split holdout --repeat 3`, worst answer counts.
Holdout carries 3 dirty and 3 clean fragments per card.

| Run | dirty found | recall | clean flagged | false | unclear | 90/10 |
|---|---:|---:|---:|---:|---:|---|
| deepseek-flash, holdout × 3, C18 | 3/3 | 100% | 0/3 | 0% | 0/6 | PASS |
| deepseek-flash, holdout × 3, C19 | 3/3 | 100% | 0/3 | 0% | 0/6 | PASS |
| deepseek-flash, holdout × 3, C20 | 3/3 | 100% | 0/3 | 0% | 0/6 | PASS |
| deepseek-flash, whole corpus, r=3 | 30/30 | 100% | 0/30 | 0% | 0/60 | PASS |
| Jev, whole corpus, C18 | 9/10 | 90% | 0/10 | 0% | 5/20 | PASS |
| Jev, whole corpus, C19 | 10/10 | 100% | 0/10 | 0% | 0/20 | PASS |
| Jev, whole corpus, C20 | 10/10 | 100% | 0/10 | 0% | 1/20 | PASS |
| Jev, whole corpus, total | 29/30 | 97% | 0/30 | 0% | 6/60 | PASS |

All three cards clear the 90/10 threshold on both engines, so they join the
cheap list in `routing.json`.

## Jev on C1–C17

`jev-latest` judges one fragment at a time through `tools/jev_judge.py`; a
`choice({dirty, clean, unclear})` maps directly onto the exam verdicts. The
official gate (`--split holdout --repeat 3`, 107 fragments × 3 = 321 calls):

- **12 of 17 cards pass** — recall **47/52 (90.4%)**, false positives **3/55
  (5.5%)**, unstable **3 of 107**.
- On the same 90/10 gate (repeat 3): DeepSeek flash 11/17, **Jev 12/17**, Haiku
  14/17, Sonnet 14/17.
- Jev passes C1, C4, C7, C8 and C14 — the cards DeepSeek flash fails, and C7,
  which all three generative models fail.
- Whole corpus (377 fragments, one answer each): recall **165/188 (87.8%)**,
  false positives **6/189 (3.2%)** — 0 false positives on 14 of 17 cards.
- Cards that still need a strong model: C5, C6, C11, C12, C15 (recall or false
  positive below the gate on holdout); C15 is Jev's weakest (50% recall full
  corpus) and C11 over-flags (30% false positives full corpus).

### Calibrated prefilter

Because Jev returns calibrated probabilities, it can drop the fragments it is
confident are clean and leave the rest to a strong model (`tools/check.py`,
`--clean-threshold`). Measured on the full 377-fragment corpus:

| `p_clean` threshold | clean dropped | dirty missed | recall |
|---|---:|---:|---:|
| ≥ 0.90 | 95/189 (50.3%) | 0/188 | 100.0% |
| ≥ 0.85 | 120/189 (63.5%) | 1/188 | 99.5% |
| ≥ 0.80 | 134/189 (70.9%) | 4/188 | 97.9% |
| ≥ 0.75 | 140/189 (74.1%) | 4/188 | 97.9% |
| ≥ 0.70 | 147/189 (77.8%) | 5/188 | 97.3% |

### Cost

All 699 calls (1.48M input tokens, 0 failures) cost **$0.062**; the price is
$0.042 / 1M input tokens, $0 output, so **1 000 candidates ≈ $0.09**. A direct
HTTP call is one forward pass (~300–800 ms), which parallelises well.
