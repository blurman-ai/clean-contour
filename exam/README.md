# Exam

Measures whether a model can run the [clean-contour-check](../skills/clean-contour-check/SKILL.md) cards: does it find dirty locations, and does it leave clean ones alone. Run it before giving the check to a new model, and after editing a card.

Requires Python 3.10+, no dependencies.

```bash
bin/exam --check                     # corpus and cards are intact; no model is called
bin/exam --selftest                  # control cases; no network
bin/exam --model-cmd '<command>' --label <model> --repeat 3 --jobs 8 --retries 2 --out runs/<date>-<model>.json
bin/exam --cards C7,C9 --model-cmd '<command>'    # selected cards only
bin/exam --show-prompt C7-03         # print the prompt the model will get
```

`--model-cmd` is a shell command that reads the prompt from stdin and prints one answer line in the skill's output format. Example with Claude Code:

```bash
--model-cmd 'claude -p --model haiku --tools "" --no-session-persistence --system-prompt "You review code. Answer with one line in the required format."'
```

Exit code: 0 — every selected card passed; 1 — some card failed; 2 — corpus, card or model call error, the measurement is void. A void run is rerun, not read.

## Scoring

Each fragment is sent with the skill's "Procedure" section and one card. The verdict is the fourth field of the answer line. Per card:

- **recall** — dirty fragments answered `dirty` / all dirty fragments;
- **false** — clean fragments answered `dirty` / all clean fragments;
- **pass** — recall ≥ 90% and false ≤ 10%.

`unclear` on a dirty fragment is a miss. On a clean fragment it is not an error and is counted in its own column: by the skill's order such a location goes to a stronger model.

With `--repeat N` each fragment is asked N times and the worst answer counts: a dirty fragment is found only if all N answers say `dirty`; a clean fragment is flagged if any answer says `dirty`. The same model under the same name answers differently between runs, so one lucky answer proves nothing. A card that passed earlier and fails now on unchanged fragments is model drift: move the card to the strong-model list.

## Corpus

`corpus/C<N>.yaml`, at least 10 dirty and 10 clean fragments per card, 15–60 lines each. Fields: `id`, `card`, `expected` (`dirty` or `clean`), `path`, `why`, `source`, `code`. Only `path` and `code` reach the model.

Fragments keep the shape of real code: conditions, comparisons, order of assignments. Names, paths and the domain (delivery, warehouse, reports) are invented. Every card's clean set contains near misses from its "Does not count" section.

## Adding a card

1. Add `## C<N>. <title>` to `SKILL.md` with the subsections **Search**, **Questions**, **Dirty if**, **Does not count**, **Dirty**, **Clean**.
2. Add `corpus/C<N>.yaml` with at least 10 + 10 fragments. The code of a fragment must not contain the words `dirty`, `clean`, `unclear` or a card number; `--check` refuses such hints.
3. Run `bin/exam --check`, then the exam on your model with `--cards C<N> --repeat 3`.
4. A card that fails goes to the strong-model list in the root README.
