# clean-contour

Rules for code whose objects have a lifecycle (an order, a payment, a build, an attempt), check cards that let a coding agent find violations one code location at a time, and an exam that measures whether a given model can run those cards.

Background: [A clean room for coding agents](https://blurman-ai.github.io/clean-room/) (Russian version on [Habr](https://habr.com/ru/articles/1101314/)).

## Files

| Path | What it is | Who reads it |
|---|---|---|
| `RULES.md` | 17 principles, signs of a dirty contour, how to move an entity into the clean contour | an agent that writes or changes an entity with a lifecycle |
| `skills/clean-contour-check/SKILL.md` | 15 cards (C1–C15): search pattern, closed questions, verdict rule, exclusions, dirty and clean example | an agent that checks code |
| `exam/` | runner and corpus of 331 labelled fragments | whoever edits a card or picks a model for checking |

## Install into a project

Run from the root of the target project:

```bash
git clone --depth 1 https://github.com/blurman-ai/clean-contour /tmp/clean-contour
cp /tmp/clean-contour/RULES.md docs/clean-contour.md
mkdir -p .claude/skills .agents/skills
cp -r /tmp/clean-contour/skills/clean-contour-check .claude/skills/   # Claude Code
cp -r /tmp/clean-contour/skills/clean-contour-check .agents/skills/   # Codex, Cursor and others
```

Then add one line to `AGENTS.md` (or `CLAUDE.md`):

```markdown
Code of an entity with a lifecycle follows docs/clean-contour.md; check it with the clean-contour-check skill.
```

Keep the copies unchanged. To change a card, change it here and copy again; a local edit drifts from the exam corpus.

## When to run the check

- Before fixing a bug: on the file being fixed.
- Before closing a task: on your own diff.
- On request "hygiene <area>" or "clean-contour check <area>": on that area.

## How to run the check

Follow the "Procedure" section of `SKILL.md`. In short: for each card, run its **Search** over the files in scope; every hit is a candidate. Drop candidates listed under **Does not count**. Open 30–60 lines around the candidate and answer the card's **Questions** in order with `yes`, `no` or `unclear`, using only lines inside the fragment. Take the verdict from **Dirty if**. One output line per candidate:

```
file:line | C<N> | answers, comma separated | dirty / clean / unclear | one sentence: what comes from where
```

Example:

```
src/features/order/useSave.ts:21 | C15 | yes, yes, no, no | dirty | the error handler does not read the refusal code and shows one text for every cause
```

## What to do with the result

- `dirty` inside your diff: fix it before closing the task.
- `dirty` outside your diff: report the line; do not fix it "while at it".
- `unclear`: hand the location to a stronger model or a human.
- The same thing broke three times after three fixes: stop patching; the entity needs to move into the clean contour (`RULES.md`, the section on moving an entity into the clean contour).

## Which model may run which card

A card looks at one location, so a cheap model can run it if it passes the exam: at least 90% of dirty fragments found and at most 10% of clean ones flagged.

Measured on DeepSeek flash, 3 answers per fragment, worst answer counts (03.11.2026): 8 of 15 cards passed; over all cards 94% of dirty fragments found and 12% of clean ones flagged. Failures are mostly false flags on near misses: the model ignores a card's "Does not count" exclusion.

| Cards | Who runs them |
|---|---|
| C1, C3, C6, C7, C9, C11, C12, C15 | a cheap model is enough |
| C2, C4, C5, C8, C10, C13, C14 | a strong model or a human |

For another model, run the exam first: [exam/README.md](exam/README.md).

## License

Apache 2.0, see [LICENSE](LICENSE).
