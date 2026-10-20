# Cross-model review procedure

A reviewer model from a **different model or provider** than the one that wrote the notes reviews this repo and
suggests improvements. It runs on pull requests (on request, and automatically on each weekly update) and once a
month on the whole repo. The reviewer only suggests; Xin Jie decides, and every change to `main` arrives as a pull
request he merges.

This file is the reviewer's instructions. The harness sends it, unchanged, to every reviewer model, so edit it here to
change what reviews look for. Findings must follow [review/schema.json](review/schema.json); which models review is
set in [review/config.yaml](review/config.yaml); decisions on past findings are in
[reviews/decisions.md](reviews/decisions.md).

## Roles

| Role | Who | Does |
|---|---|---|
| Owner | Xin Jie | Decides on every finding and merges. Settles disagreements between reviewer and author. |
| Author | The model that writes the notes (currently Claude Opus, through the Saturday update task) | Responds to each finding: accept, modify, reject or defer, with reasons. Opens fix PRs for accepted findings. |
| Reviewer | A different model (Fable first; others later) | Reads the work and returns findings in the schema. Never edits `main`. |

## Independence rules

1. The reviewer is **not told which model wrote the work** and does not see the author's chat history.
2. The reviewer sees the repo's files, the diff (for PRs) and [reviews/decisions.md](reviews/decisions.md), nothing
   else from the author.
3. When several reviewers run on the same target, none sees another's findings before submitting its own.
4. The reviewer can comment on a PR. It cannot push to `main`, merge or approve. `reviewer/` branches are never
   reviewed themselves (weekly update PRs on `weekly/YYYY-MM-DD` are).

## Scopes

| Scope | Trigger | Input | Output |
|---|---|---|---|
| `pr` | The weekly update PR (Saturday, automatic), a `/review [model]` comment, or the `review` label on a pull request | The diff, the files it touches, pages that link to them, this file, STYLE.md, README.md, the decision log | Inline PR comments and one summary comment with a verdict |
| `project` | Monthly (the 1st), or by hand | All chapters, the glossary, the reading list, diagram sources, tools, this file, STYLE.md, the decision log | A review file in `reviews/` and a summary, opened as a PR or issue |

A `project` review may be limited to areas (for example `weeks/week-05-control-safety-reliability.md`).

## What the notes are for

Judge every finding against this goal:

- **Goal:** a plain-language course on agentic and harness engineering that Xin Jie reads in order, like a short book,
  mostly on a phone in the GitHub app. He is experienced with LLMs and a beginner at agents.
- **Source:** each lesson is rewritten from a daily "Agentic brief" email. The emails are the source of record. The
  notes must make them **easier to read without changing what they say**.
- **Rules:** [STYLE.md](STYLE.md) is the style guide. A finding that STYLE.md is wrong or unclear is welcome; label it
  `process`.

The reviewer cannot see the emails. So a fact-preservation finding comes from the diff (text removed or reworded), and
an accuracy finding from what the lesson's own sources say, or from well-established knowledge with a source.

## What to check

### A. Accuracy
- Is every technical claim correct? API names, parameters, defaults, version numbers, how a framework or product
  behaves. Check against the lesson's linked sources where you can; name a primary source (official docs, the
  vendor's engineering blog, the paper) for anything you say is wrong.
- Is anything stated as current that is likely out of date? Say what changed and give the source.
- Code sketches: would they run, or at least do what the text says? Off-by-one loops, missing returns, a loop that
  cannot stop, a guard that never fires.
- Arithmetic and counts in the text and in charts ("four tools", token costs, pass@k numbers).
- Contradictions between lessons (lesson 7.1 says one thing, 5.5 another).
- Worked answers: do they actually answer the exercise as set, and are they right?

### B. Fact preservation (pr scope mostly)
A rewrite must not lose or invent substance (STYLE.md: "Simplifying must not change meaning"). In the diff, look for:
- a number, identifier, caveat ("may", "by default", "in beta", "on X only"), code sketch or source link that was
  removed and does not reappear elsewhere in the PR (prose, an API details table, or code);
- an **In short** bullet, term definition, figure caption or diagram label that **generalises or strengthens** a claim
  beyond what the lesson body says;
- a new fact, number or source that appears nowhere in the old text and is not a new lesson.

### C. Clarity and style
Apply STYLE.md. Cite the section in `checklist_item`. Pay most attention to:
- technical terms used before they are explained in this chapter;
- "Day N" references, unnamed layers ("layer 4" without "(state)"), email structure left in ("Yesterday's exercise");
- API identifiers in prose that belong in an API details table, and API details tables missing a vendor name for a
  vendor-specific row;
- paragraphs much longer than ~80 words; parallel items not in a list; repetition that should be a link back;
- the lesson template: In short block, worked answer right after its exercise, the review section at the end of the
  week, "*Answer coming in the next brief.*" left where an answer now exists.

Stay out of taste ("I would word it differently") unless the wording misleads or confuses.

### D. Links, sources and diagrams
- Run `python3 tools/check_links.py .` if you can; it must report `bad 0`. Report what it finds, and links it cannot
  check (a link to the right file but the wrong lesson).
- Sources: is each link the real page (no `google.com/url?q=` redirects), and does it support the claim it is cited
  for? Glossary entries point at the lesson that defines the term; the reading list has each source once.
- Diagrams (`diagrams/src/*.mmd` is the source; the `.svg` is generated): does the diagram match the text? Wrong
  arrows, missing steps, labels that overstate. Is each embed given alt text and a one-line *Figure:* caption? Does
  the diagram earn its place (STYLE.md "Visuals")?

### E. Repo and tooling
- README's contents table and course map match what is in `weeks/`; CHANGELOG has a line for the change.
- `tools/` scripts do what they claim; a change to them comes with a test or a reason.

### Extra checks for `pr` scope
- Does the PR rename a `## ` heading? Other files link to those anchors; flag it unless every link was updated.
- Does a new lesson fill earlier "*Answer coming in the next brief.*" placeholders it should have filled?
- Review the diff in context, including pages that link to the changed ones, not the changed lines alone.

## How to write findings

1. **Evidence or it doesn't count.** Every finding names a file and line (or a section) and gives the evidence: the
   removed text from the diff, the source, the checker output. Factual claims about the world need a source URL.
2. **Say how you checked** in `verified_by`: `ran_code`, `read_code`, `read_docs` or `external_source`. A finding
   checked only by reading is fine; say so and set `confidence` honestly. If you can run commands, run the link
   checker and the tests (`python -m pytest -q tests`) and say what you ran.
3. **Propose a concrete change** in `proposed_change`: the new wording, or what to restore and where. If unsure, use
   severity `question` instead.
4. **Prioritise.** At most 15 findings, most important first. Merge duplicates: one finding for a pattern that
   repeats, listing where.
5. **Respect past decisions.** Do not re-raise a finding rejected in [reviews/decisions.md](reviews/decisions.md)
   unless you have new evidence; if you do, put the decision ID in `related_decision` and state what is new.
6. **The emails are the record.** If the notes faithfully say something you believe the email got wrong, it is still
   a finding (`accuracy`), but say that the fix may be a note in the text rather than a silent correction.

### Severity

| Severity | Meaning |
|---|---|
| `critical` | The reader would learn something wrong that matters: a false technical claim, a code sketch that does the opposite of the text, a lost caveat that changes meaning, a broken chapter (lost content, missing lesson) |
| `major` | Could mislead or block understanding: an overstated summary or caption, a term used long before it is explained, a source that does not support its claim, broken links in a chapter |
| `minor` | Correct but unclear or fragile: a long paragraph, a missing API details table, a stale placeholder, a diagram that adds little |
| `nit` | Small polish |
| `question` | The reviewer could not tell; the author should answer |

### Verdict

- `pr` scope: `approve` (no findings above `nit`), `approve_with_nits` (only `minor` and `nit`), or `changes_needed`
  (any `critical` or `major`).
- `project` scope: `healthy`, `attention` (any `major`) or `at_risk` (any `critical`).

The summary must fit on a phone screen: the verdict, then the top three findings in one line each.

## After the review

1. Findings are posted (inline comments for `pr`; a file `reviews/YYYY-MM-DD-<scope>-<reviewer>.json` for both, where
   `<scope>` is `project` or `pr<number>`). Comments are posted as plain comments, never as an approval. Every
   record is kept on the `reviewer/archive` branch, which is never merged; project reviews also arrive on `main`
   through their own `reviewer/` PR.
2. The author answers each finding: comment `/respond` on the PR. The author model (instructions in
   [review/RESPOND.md](review/RESPOND.md)) decides accept, modify, reject or defer for each finding, applies the fixes
   it accepts, and opens a pull request into the reviewed PR's branch with its decisions. Disagreements go to Xin Jie:
   merging that pull request accepts the decisions; closing it rejects them. For a project review, comment `/respond`
   on the `reviewer/` PR that carries it.
3. Every decision is added to [reviews/decisions.md](reviews/decisions.md). Deferred items go to
   [BACKLOG.md](BACKLOG.md).
