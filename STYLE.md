# How these notes are written

These notes are rewritten from the daily "Agentic brief" emails. The emails were written fast, one day at a time. The notes are meant to be read in order, like a short book, often on a phone in the GitHub app. This file is the style guide for anyone (human or Claude) who adds to them.

## Plain language

- Short sentences. One idea per sentence where you can.
- Prefer everyday words. "Use" not "leverage". "Check" not "validate" unless the technical word matters.
- Keep technical terms, but explain each one in plain words the first time it appears in a **chapter**, even if an earlier chapter explained it. A short clause is enough: "the executor (the code that runs tool calls)". Link to the lesson that introduced it.
- Lead with what the idea is and why it matters. Then the detail.
- Say things directly. No hype, no filler, no "it's important to note that".
- Simplifying must not change meaning. Keep every number, caveat and source. If a sentence cannot get simpler without losing a caveat, keep the caveat.
- Code stays as code. Add one or two sentences that say what the code does before or after it.
- Paragraphs of at most about 80 words. A list of three or more parallel items becomes a bulleted list.

## Keep the main text about ideas

The main text explains how something works and why. Exact API identifiers get in the way of that, so they go in an **API details** table at the end of the section where they come up:

- Beta header strings, versioned type names (`clear_tool_uses_20250919`), parameter names, default and minimum values, model availability, product version numbers, billing fields.
- In the text, describe the thing in words ("the API can clear old tool results once the input passes a threshold") and leave the names and numbers to the table.
- Numbers that carry the argument (a cost ratio, a benchmark score, "keeps the last 3") stay in the text.
- Nothing is deleted. Every identifier and number from the original goes somewhere.

```
**API details**

| What | Value |
|---|---|
| Beta header | `context-management-2025-06-27` |
| Default trigger | 100k input tokens |
```

Code examples keep their identifiers. The table is for prose only.

## Keep it anonymous

The notes name no real employer, client, person or site. The emails sometimes do, because they tie exercises to the owner's day job; the notes do not.

- Write "a solar forecasting team", "a portfolio of solar sites", "the owner" or "you" instead of a company or a person's name.
- Use the made-up example site codes with neutral prefixes (PVA-03, PVB-01 and so on). If an email uses other prefixes, map them to these; never use a prefix that hints at a country or place. Never swap in real site, plant or asset names, project codes, or customer names.
- Nothing that locates the sites or the owner: no countries, cities, regions, or a time zone that gives one away. Do not attach a time zone to clock times; where one is needed, write "local time". Technical references such as "the site's time zone" or UTC as a standard are fine.
- No email addresses or other personal contact details. The GitHub username in repo URLs is fine; it is the repo's address.
- Names of public companies, products, papers and authors that are *sources* (Anthropic, OpenAI, LangGraph, a paper's authors) stay: they are what the lesson cites.

## Flow

- Each week is one file in `weeks/`. Lessons follow each other in order.
- Open each week with a short paragraph: what the week covers and how it follows from the last one.
- Join lessons with a sentence or two, so it reads as a story, not a pile of emails.
- Do not keep the email structure ("Yesterday's exercise", "Tomorrow"). Put each exercise's worked answer directly after the exercise, inside the same lesson.
- Remove repetition between lessons. If an idea was explained earlier, link back instead of explaining again.
- Never refer to "Day N". Refer to the lesson by number, with a link: `the allow-list from [1.4](week-01-what-an-agent-is.md#14-what-a-harness-is)`.
- When a lesson says "layer N", name it too: "layer 4 (state)". The six layers are pictured in `diagrams/harness-layers.svg`.
- Aim for a lesson (idea to common mistakes) that reads in 5–7 minutes. The exercise and worked answer are extra.

## Contents list

Every week file has a generated contents list right under its title (between `<!-- toc -->` and `<!-- /toc -->`) and has a "↑ Contents" link before each lesson. Do not edit them by hand: after adding or renaming any heading, run `python3 tools/make_toc.py`. `python3 tools/make_toc.py --check` fails if a list is out of date.

## Lesson template

```
## N.M Lesson title

*Day X · YYYY-MM-DD*

> **In short**
> - The main idea, in one line.
> - Why it matters, in one line.
> - The one thing to remember or do, in one line.

### The idea
### An example
### Where it lives in the harness
### Common mistakes
### Try it
(the exercise, as set)
### Worked answer
(the model answer from the next day's email, rewritten plainly)
### Sources
```

Drop any heading that has nothing under it. Review days become a "Week N review" section at the end of the week file: a short recap, the self-quiz with its answers, and the integrative exercise with its answer.

If an answer has not been published yet, write: *Answer coming in the next brief.* The weekly update fills it in later.

## Visuals

Add a picture only where it explains something faster than text: a flow, a cycle, a structure, a trade-off, a comparison. Most lessons get one; some get none; few need two. Never decorate.

How they are made, so they display in the GitHub mobile app and in dark mode:

1. Write the diagram as Mermaid in `diagrams/src/<name>.mmd`. Name it after the idea, not the lesson (`compaction-survival`, not `lesson-3-2`). Use `flowchart`, `sequenceDiagram` or `stateDiagram-v2`. Do not set colours or themes in the file; the shared config handles them. You may use `classDef` for at most two highlight styles.
2. Render with `python3 tools/render_diagrams.py <name>`. This writes `diagrams/<name>.svg` with plain text labels and a white background card. Commit both the `.mmd` and the `.svg`.
3. For a data chart (numbers plotted on axes), write a small matplotlib script in `diagrams/src/<name>.py` that saves `diagrams/<name>.svg` with a white background, using only numbers from the lesson. Commit both.
4. Check legibility: `python3 tools/preview_diagrams.py /tmp/out.png diagrams/<name>.svg` shows it at phone width on a dark page. Text must be readable at that size. Keep it to roughly 12 boxes or fewer, labels of 1–5 words, and prefer top-to-bottom (`TD`) layouts, which fit a phone better than wide left-to-right ones.
5. Embed it right after the paragraph it explains:

```
![Alt text that says what the picture shows, in one sentence.](../diagrams/<name>.svg)

*Figure: one line on what to notice.*
```

Shared diagrams (for example `harness-layers`) are reused by linking the same file; do not copy them.

## Files

- `README.md` — what this is, how to read it, table of contents.
- `weeks/week-NN-<slug>.md` — the lessons.
- `diagrams/` — rendered SVGs; `diagrams/src/` — their Mermaid or Python sources.
- `glossary.md` — terms, alphabetical, plain definitions, each pointing to the lesson that introduces it.
- `reading-list.md` — sources, grouped by week.
- `CHANGELOG.md` — one line per update.
- `tools/` — `check_links.py`, `make_toc.py`, `render_diagrams.py`, `preview_diagrams.py` and the Mermaid config.
