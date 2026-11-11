# clean-contour

Rules for code whose objects have a lifecycle (an order, a payment, a build, an attempt), check cards that let a coding agent find violations one code location at a time, and an exam that measures whether a given model can run those cards.

Background: [A clean room for coding agents](https://blurman-ai.github.io/clean-room/) (Russian version on [Habr](https://habr.com/ru/articles/1101314/)).

Measured results on agent-written open-source projects: [FIELD-RESULTS.md](FIELD-RESULTS.md).

## Files

| Path | What it is | Who reads it |
|---|---|---|
| `RULES.md` | 17 principles, signs of a dirty contour, how to move an entity into the clean contour | an agent that writes or changes an entity with a lifecycle |
| `skills/clean-contour-check/SKILL.md` | 17 cards (C1–C17): search pattern, closed questions, verdict rule, exclusions, dirty and clean example | an agent that checks code |
| `exam/` | runner and corpus of 377 labelled fragments | whoever edits a card or picks a model for checking |

## Install as a Claude Code plugin

```
/plugin marketplace add blurman-ai/plugins
/plugin install clean-contour@blurman-ai
```

The plugin gives the `clean-contour-check` skill. The rules still go into the project: copy `RULES.md` to `docs/clean-contour.md` and add the `AGENTS.md` line from the next section.

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

Measured on 11.11.2026, 3 answers per fragment, worst answer counts:

| Card | DeepSeek flash | Haiku | Sonnet |
|---|---|---|---|
| C2, C3, C5, C6, C9, C11, C12, C13, C16, C17 | pass | pass | pass, except C9 |
| C10 | pass | pass | pass |
| C4, C14 | fail | pass | pass |
| C1 | fail | pass | pass |
| C8 | fail | fail | pass |
| C7, C15 | fail | fail | fail |

C2, C5, C10 and C11 were rewritten on 11.11 so that the answer follows from the fragment: C2 judges the branch, not whether the entity also has a stored field; C5 compares outcomes, not phrasing; C10 asks whether the composition is declared, not whether parts "could" be accepted alone; C11 requires a way out for the death of the process too, not only for a refusal and a timeout. C1 passed on DeepSeek on 03.11 and fails on the same fragments now, which is model drift. Sonnet flags test parametrization on C9 that the card excludes.

| Cards | Who runs them |
|---|---|
| C2, C3, C5, C6, C9, C11, C12, C13, C16, C17 | a cheap model is enough |
| C1, C4, C7, C8, C10, C14, C15 | a strong model or a human |

C10 passes the exam but goes to a strong model: on a real backend 2 of 15 places it flagged were dirty. A dirty verdict from a cheap model on real code is a candidate for reading, not a finding: on that product 7 of the 60 places DeepSeek flagged held up when read, on the C# projects below about half.

For another model, run the exam first: [exam/README.md](exam/README.md).

The corpus is mostly Python and TypeScript (C17 also has C# view models and Django templates). The cards' search signs for Kotlin, Go and C# are written, but the exam does not measure them yet; a corpus for another language goes into its own directory and runs with `bin/exam --corpus exam/corpus-<lang>`.

## C#

The cards name C# signs for EF Core, Dapper, ASP.NET Core (controllers and minimal APIs), Blazor and MVVM clients (WPF, MAUI, Avalonia). `RULES.md` shows how the instruments look in C#: an assembly per entity with `private set`, an architecture test, `BannedApiAnalyzers` on old names, a field registry over `DbContext.Model`, and an exhaustive `switch` over the refusal code enum with CS8509 as an error. Install is the same; `.Tests` projects, EF migrations and generated `*.g.cs` are excluded from every search. `tools/cs_search.py <repo>` prints candidates for every card's C# signs, one line per hit; each hit is then read against the card.

## License

Apache 2.0, see [LICENSE](LICENSE).
