---
name: clean-contour-check
description: Check code against the signs of a dirty contour (RULES.md), one place at a time, with closed questions. Use before fixing a bug in a file, when closing a task over your own diff, and on the command "hygiene <area>".
---

# Clean contour check

The cards below apply to **one place in the code**: a fragment of 30-60 lines
around the line that was found. You do not need to know the whole project:
everything required for an answer is in the fragment, or the answer is
"unclear".

## Procedure

1. Take a card. Run its **search** over the files being checked (your own diff,
   the file being fixed, or an area the owner named). Every hit is a
   candidate.
2. Discard candidates that fall under **does not count**.
3. Open the fragment around the candidate and answer the card's **questions**
   in order: `yes`, `no` or `unclear`. An answer rests on a line of the
   fragment; a guess about code outside it is `unclear`.
4. The verdict follows the card's **dirty if** line. `unclear` on a question
   the verdict depends on makes the verdict `unclear`, and the place goes to a
   human or a strong model.
5. Write the output line.

Output is one line per candidate:

```
file:line | C<number> | answers, comma separated | dirty / clean / unclear | one sentence: what comes from where
```

A dirty place in your own diff is fixed before the task is closed. A dirty
place outside the diff is a line in the report, not a fix "while at it".

**Which cards go to whom.** A weak model (cheap, without reasoning) gets the
cards that passed the exam from the `exam/` directory with threshold 90/10; on
03.11.2026 (DeepSeek flash) cards C2, C4, C5, C8, C10, C13 and C14 were not
passed, so their candidates are checked by a strong model or a human.

Signs that a machine looks for without reading, such as a new state field
without a declaration or a set of values outside the declaring module, sit in
the project's CI; here they appear only where a question to the code is needed.

---

## C1. State derived from an event log

**Search:** functions that walk over events and return a state, stage, result,
or "is it finished": `*_from_events`, `compute_*state*`, `fold`, `reduce` over
a list of events; a loop over `events` with `return` of a status;
`any(e.type == …)`, `.some(e => e.type === …)`.

**Questions:**
1. Does the fragment return or set a state, stage, result, or a
   "finished / interrupted / checked" flag of an **entity**? The answer to a
   query ("did this key already arrive?") is not an entity state.
2. Is the value taken from a list of events (a log), not from a field of the
   entity?
3. Does the entity have a stored field with the same meaning (`status`,
   `state`, `result_status`, `stage` and the like), in the fragment or in its
   imports?

**Dirty if:** 1 = yes and 2 = yes. Question 3 = yes makes the place worse: the
stored field exists, yet the log is what gets read.

**Does not count:** a data migration module (a migration, `*_backfill`) that
folds the log into a stored field once; a report that counts the time or
frequency of events, not a state; a repeated-request check by an idempotency
key; tests.

**Dirty:**
```python
def attempt_finished(events):
    return any(e.type == "attempt_completed" for e in events)
```
**Clean:**
```python
def attempt_finished(attempt):
    return attempt.status in AttemptStatus.FINAL
```

## C2. A missing row is read as a state

**Search:** a branch on an empty selection or on `None` from a query:
`if not rows`, `if row is None`, `.first() is None`, `count() == 0`,
`exists(`, `len(…) == 0`, followed by a return or an assignment of a state. The
fragment also includes the declaration of the entity with its state fields.

**Questions:**
1. Does the branch on an empty selection decide the state of an entity ("not
   started", "not ready", "no access", "no account")?
2. Is this state not stored as a field of the entity the decision is about?

**Dirty if:** 1 = yes and 2 = yes.

**Does not count:** a 404 for a request for a nonexistent object; an "already
created?" check before creating that same row; tests.

**Dirty:**
```python
if session.query(Answer).filter_by(step_id=step.id).first() is None:
    step_state = "not_started"
```
**Clean:**
```python
step_state = step.state
```

## C3. State taken from a neighboring entity

**Search:** reading `status`/`state` of another table or object, after which
the state of its own entity is set; comparing the status of a job, queue, or
run inside a function that returns the status of a draft, blueprint, or
assignment.

**Questions:**
1. Does the fragment return or write the state of entity A?
2. Is the state of A **derived** from a field of entity B (another table,
   another object, another service's response)? If the status of B is only
   returned next to the status of A as a separate field, the answer is "no".
3. Does A have its own state field that takes no part in the decision or takes
   part second?

**Dirty if:** 1 = yes and 2 = yes.

**Does not count:** a writer of A that, on an event of B, **moves** A to a new
stored state in one transaction; tests.

**Dirty:**
```python
def blueprint_status(bp, job):
    return "failed" if job.status == "failed" else "generating"
```
**Clean:**
```python
def blueprint_status(bp):
    return bp.status  # the writer moves it on the job's outcome
```

## C4. A state field written around the writer

**Search:** assignments `.status =`, `.state =`, `.stage =`, `.phase =`,
`.outcome =`, `.processing_status =`, `update(...).values(status=…)`.

**Questions:**
1. Is this an assignment to the state field of an entity with a lifecycle?
2. Is the fragment not the write function of this field itself (its name is
   usually `set_*_status`, `transition_*`, `*_writer`)?
3. Does the fragment contain no call to a write function that checks the
   transition?

**Dirty if:** 1, 2 and 3 = yes.

**Does not count:** the write function; a migration; a factory in tests;
creating an entity with an initial state from the list inside its own module.

**Dirty:**
```python
version.processing_status = "ready"
```
**Clean:**
```python
set_version_processing_status(version, ProcessingStatus.READY)
```

## C5. One state computed in several places

**Search:** the machine collects functions with similar names (`*_status`,
`*_state`, `is_*_ready`, `*_verdict`, `*_outcome`) for one aggregate and gives
the model pairs.

**Questions (about a pair of fragments):**
1. Put the question of each fragment as a phrase "<verb> <object>" ("did the
   attempt pass", "can the order be opened"). Do the phrases match entirely? If
   the verb or the object differs (open / close, cancel / refund, was applied /
   is in force now, order / shipment), the answer is "no" and questions 2-3 are
   not asked.
2. Is the answer computed, rather than read from one stored field or one shared
   function?
3. Do the calculation rules in the fragments differ by at least one branch?

**Dirty if:** 1 = yes and 2 = yes. Question 3 = yes means the divergence is
already visible to the user.

**Does not count:** one function and its thin wrapper that only calls it.

**Dirty:**
```python
# a.py
def passed(att): return att.score >= 80
# b.py
def passed(att): return att.score > 80 and not att.disputed
```
**Clean:**
```python
# both places
from attempts import attempt_passed
```

## C6. A decision by error text or code prefix

**Search:** `in str(exc)`, `in message`, `.lower()` on error text,
`.startswith(` / `.removeprefix(` on a refusal code; in the frontend
`.includes(` on `detail`, `message`, `error`.

**Questions:**
1. Does the branch choose behavior (refusal code, retry, text for the user,
   kind of failure)?
2. Is the choice made by the message text or by the start of a code string,
   rather than by a member of a list or an exception class?

**Dirty if:** 1 = yes and 2 = yes.

**Does not count:** writing to a log; a test that checks the message text.

**Dirty:**
```python
if "timeout" in str(exc).lower():
    code = "provider_timeout"
```
**Clean:**
```python
except ProviderTimeout:
    code = FailureCode.PROVIDER_TIMEOUT
```

## C7. A kind or role guessed from an indirect sign

**Search:** comparisons with a label, a literal in natural language, an id
prefix, a unit of measure, or cell text: `== "…"` against a natural-language UI
label literal, `.startswith("<prefix>:")`, `unit === "steps"`,
`label.includes(`, `columns.index("…")`, `id.includes(" ")`.

**Questions:**
1. What does the branch do: does it decide **what the thing is** and how the
   object is processed next (the kind of an object, the role of a column,
   whether a variant is a service one, whether the text has a space, an order or
   a refund), or does it only choose display text? If both sides of the branch
   only return display text, the answer is "no".
2. Is the answer obtained from a label, text, prefix, unit, or the shape of a
   string, rather than from a kind field (`kind`, `type`, `role`, a flag)?
3. Is a stored kind field present nearby, in the fragment or in the response
   schema?

**Dirty if:** 1 = yes and 2 = yes.

**Does not count:** the module where this prefix or label is **declared** (one
`parse_*` function); translating a label for display; a branch that chooses
only display text by unit or label; a comparison with a member of a declared
list (`value === "custom"` with `type Size = "small" | "custom"`); tests.

**Dirty:**
```ts
const isPallet = order.sizeUnit === "pallets";
```
**Clean:**
```ts
const isPallet = order.kind === "pallet";
```

## C8. A negative check of the kind

**Search:** `not is_<kind>`, `!is<Kind>`, `!= Kind.`, `!== "…"` in a condition
that chooses the processing.

**Questions:**
1. Does the branch choose the **processing** (what to do with the object next)
   by the kind of the object? A branch whose only action is a refusal (`raise`,
   returning an error) does not choose processing.
2. Is the condition "not such-and-such kind", rather than "such-and-such kind"
   or an entry from a table of kinds? A kind is the value of the object's kind
   field (`kind`, `type`, role). Validity, emptiness, whether a day is a
   holiday, a flag are not a kind: "no".

**Dirty if:** 1 = yes and 2 = yes.

**Does not count:** a branch whose only action is a refusal (`raise`, returning
an error with a code): "this kind is not accepted here"; a check of a sign that
is not a kind (whether an index is valid, whether it is a holiday).

**Dirty:**
```python
if not is_pallet(order):
    build_parcel_route(order)
```
**Clean:**
```python
PLANS[order.kind].build(order)
```

## C9. A set of values declared more than once

**Search:** the machine finds literal sets of three or more strings (`set`,
`frozenset`, `tuple`, `Literal[...]`, an array, a union type) and gives the
model pairs with the same or almost the same contents, and also a set next to
an API list (an `enum` in an OpenAPI schema, a generated type).

**Questions (about a pair):**
1. Do both sets list the same thing: state values, kinds, refusal codes, ids of
   the options of one question? Calendar and physical constants (days of the
   week, months, sizes) are "no".
2. Is at least one of them written as a literal rather than obtained from the
   other (import, generation, `Enum.__members__`, a generated type)?
3. Do the contents differ by at least one value?

**Dirty if:** 1 = yes and 2 = yes, whatever the answer to question 3: contents
that match today will diverge at the next edit of one of the places. Question
3 = yes means the divergence already exists.

**Does not count:** a subset declared by **name** next to the list
(`FINAL = {A.DONE, A.FAILED}`); fixtures and test parametrization; sizes,
colors and other presentation values (`"xs" | "sm" | "md"`).

**Dirty:**
```ts
type Status = "pending" | "approved" | "rejected";  // a copy of the API enum
```
**Clean:**
```ts
type Status = components["schemas"]["ExtensionStatus"];
```

## C10. All or nothing

**Search:** processing a list of parts (sections, steps, blocks, files) where
the failure of one part sets a failure of the whole: `raise` inside a loop over
parts, `status = "failed"` after the first error of a part, `Promise.all`
without examining the results.

**Questions:**
1. Name the object or field that receives an overall status or result from
   these parts (a report from sections, an application from files). If it
   cannot be named from the fragment, the answer is "no".
2. Does the failure of one part put the whole into failure or stop the
   processing of the rest?
3. Could the other parts have been accepted on their own?

**Dirty if:** 1, 2 and 3 = yes.

**Does not count:** parts that by type are all required together, and this is
declared in the plan or the type; `Promise.all` and a loop over independent
records (orders, table rows) that have no shared status.

**Dirty:**
```python
for section in sections:
    generate(section)   # the first exception fails the whole build
```
**Clean:**
```python
results = [generate_part(s) for s in sections]   # each part has its own outcome
```

## C11. A wait without a failure state

**Search:** a call to a model, network, queue, or background handler; writing
`pending`, `processing`, `generating`, `queued` before long work; `await` /
polling without a limit.

**Questions:**
1. Before or during an external call (model, network, queue, background
   handler), does the entity get a waiting state? If there is no external call
   (waiting for a human decision), the answer is "no".
2. Is there a path by which a refusal, a timeout, or the death of the process
   moves it to a final state (`failed`, `timeout`), in the fragment or in an
   explicitly named cleaner?

**Dirty if:** 1 = yes and 2 = no.

**Does not count:** a call with no waiting state on the entity (the error goes
straight to the caller).

**Dirty:**
```python
version.processing_status = "processing"; db.commit()
text = extract(document)   # the process died: the version stays "processing" forever
```
**Clean:**
```python
enqueue_extraction(version.id)   # a handler with a lease; the cleaner moves overdue work to failed
```

## C12. The screen assembles the state itself

**Search:** in the frontend, a `useState` named `status`, `state`, `phase`,
`stage`, `mode`, `ready`, `pending`, `step`, that is set in `useEffect`, by a
timer (`setTimeout`, `setInterval`), or from `localStorage`; a ladder of three
or more conditions that chooses a screen or a stage.

**Questions:**
1. Is the value the state or stage of an entity that is stored on the server
   (a draft, a build, an attempt, an answer, an assignment)?
2. Is it computed in the browser from other fields, flags, a timer, or browser
   storage, rather than taken from one field of the server response? The
   absence of `useState` and `useEffect` changes nothing: a pure function over
   three or more response fields, a ladder of conditions in the markup, and a
   polling loop that declares a failure by the browser clock are all "yes".

**Dirty if:** 1 = yes and 2 = yes.

**Does not count:** state of the interface itself that does not exist on the
server (whether a list is open, which tab, a draft of input, whether a request
is loading); a screen that picks a view by a mapping from one field of the
server response; a timer that only updates the displayed time and does not
declare a failure; tests.

**Dirty:**
```ts
useEffect(() => {
  if (job?.error || Date.now() - startedAt > 90_000) setPhase("failed");
}, [job, startedAt]);
```
**Clean:**
```ts
const phase = draft.stage;   // the server returns the stage, the screen draws by it
```

## C13. The outcome depends on what arrived first

**Search:** in the frontend, the response of an asynchronous request that
writes values into a form or into the user's choice (`prefill`, `seed`,
`apply*`, `onSuccess`, `.then(` with `set*`), while the user can change the
same fields before the response.

**Questions:**
1. Does the response of the request write values into fields that the user can
   also change (input, choice, switch)? A value that the screen only shows
   (`readOnly`, a link, a counter) is "no".
2. While the request is running, are these fields available to the user?
3. Is there no rule about who wins (the fields are blocked until the response,
   or the response does not touch what the user changed)?

**Dirty if:** 1, 2 and 3 = yes.

**Does not count:** the response writes only into its own result field
(`readOnly`, a link, a calculation, a counter, display text) and does not touch
the fields the user changes, even if those fields are available during the
request.

**Dirty:**
```tsx
<Wizard prefill={extract.lastResponse} />   // the wizard is available before the parse response
```
**Clean:**
```tsx
{extract.settled ? <Wizard prefill={extract.lastResponse} /> : <Loader />}
```

## C14. A declaration without a writer, or a read with a write

**Search:** the machine collects models, tables and lists and looks for who
creates them and who reads them; separately, `GET` handlers that contain
`commit`, `add`, `update`, `insert`.

**Questions:**
1. Is there in the list of places outside `tests/` at least one line that
   creates a record of this table or assigns this field (`Name(`,
   `insert(Name`, `.field =`)? An import, `__all__` and `relationship` are not
   a write.
2. Is there outside the declaring module at least one read of this list or
   constant?
3. Does the read handler (`GET`) write to the database?

**Dirty if:** 1 = no, or 2 = no, or 3 = yes. The search puts into the fragment
the declaration and the list of places of use by the name of the thing the
question is about (the field, not only the class).

**Does not count:** writing to an audit log or a view counter, if they are
declared as such; adding a row of a display event with an idempotency key
(`record_*_event`).

**Dirty:**
```python
@router.get("/drafts")
def list_drafts(db):
    for d in drafts: d.structure_json = engine.poll(d.run_id)
    db.commit()
```
**Clean:**
```python
@router.get("/drafts")
def list_drafts(db):
    return [DraftOut.from_orm(d) for d in drafts]   # the structure is written by a background sync
```

## C15. The reason for a refusal is lost on the way

**Search:** in the frontend, error handlers (`catch`, `onError`, `isError`,
`error &&`, `failed`) that show text to the user; in the frontend, "code →
text" tables declared as `Record<string, …>` or a list of strings; on the
server, `except Exception` / `except …:` with a refusal to the user
(`HTTPException`, a failure field), a string instead of an object in `detail`.

**Questions:**
1. Does the branch show the user the text of a refusal or hand the refusal to
   the user (a request response, a stored failure field)?
2. Does the refusal go out or get shown without a code from the list: a string
   instead of an object in `detail`, a code literal outside the list, or the
   code from the server response is not read?
3. Do several different causes get one code or one text: a catch of all
   exceptions sets a common code, several codes lead to one text?
4. Are the codes by which the text is chosen declared in the client code, as a
   list of strings or as keys of `Record<string, …>`, rather than taken as a
   type from the generated contract (`components["schemas"][…]`)?

**Dirty if:** 1 = yes and at least one of 2, 3, 4 = yes.

**Does not count:** writing to a log; a branch that shows its own text for the
single code chosen by a member of the list; a test.

**Dirty:**
```tsx
onError: () => notify(t("sources.readFailed"))   // the refusal code is not read
```
**Clean:**
```tsx
const text = {
  attachment_pdf_encrypted: "sources.pdfEncrypted",
  attachment_text_char_limit_exceeded: "sources.textTooLong",
} satisfies Record<SourceRefusalCode, string>;
onError: (e) => notify(t(text[e.code]))
```
