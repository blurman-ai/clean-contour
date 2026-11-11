# Exam runs, 11 November 2026

Score tables printed by `bin/exam`, 3 answers per fragment, worst answer counts. The full JSON reports stay out of the repository (`exam/runs/` is ignored); rerun a card to get the raw answers.

| File | Model | Cards | Card text |
|---|---|---|---|
| `deepseek.txt` | DeepSeek flash | all 17 | C2, C5, C10, C11 rewritten, before the second edit of C2 and C16 |
| `haiku-recal.txt`, `sonnet-recal.txt` | Haiku, Sonnet | C2, C5, C9, C10, C11 | the same |
| `deepseek-v2.txt` | DeepSeek flash | C2, C10, C16, C17 | second edit of C2, C10 and C16 |
| `haiku-v2.txt` | Haiku | C2, C10, C16 | the same |
| `deepseek-c11.txt`, `haiku-c11.txt` | DeepSeek flash, Haiku | C11 | after C11-02 was relabelled dirty |
| `sonnet-v2.txt` | Sonnet | C2, C11, C16 | second edit of C2 and C16, C11-02 relabelled |

The second edit of C10 (an exclusion for validating one input) lowered recall to 9 of 11 on both models in the `-v2` runs and was reverted, so the C10 text in the repository is the one measured in `deepseek.txt` and `*-recal.txt`. The summary per model is in the root README, "Which model may run which card".
