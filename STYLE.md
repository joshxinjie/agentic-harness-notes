# How these notes are written

These notes are rewritten from the daily "Agentic brief" emails. The emails were written fast, one day at a time. The notes are meant to be read in order, like a short book. This file is the style guide for anyone (human or Claude) who adds to them.

## Plain language

- Short sentences. One idea per sentence where you can.
- Prefer everyday words. "Use" not "leverage". "Check" not "validate" unless the technical word matters.
- Keep technical terms, but explain each one in plain words the first time it appears in a lesson. Link to `glossary.md` when it helps.
- Lead with what the idea is and why it matters. Then the detail.
- Say things directly. No hype, no filler, no "it's important to note that".
- Simplifying must not change meaning. Keep every number, caveat and source. If a sentence cannot get simpler without losing a caveat, keep the caveat.
- Code stays as code. Add one or two sentences that say what the code does before or after it.

## Flow

- Each week is one file in `weeks/`. Lessons follow each other in order.
- Open each week with a short paragraph: what the week covers and how it follows from the last one.
- Join lessons with a sentence or two, so it reads as a story, not a pile of emails.
- Do not keep the email structure ("Yesterday's exercise", "Tomorrow"). Put each exercise's worked answer directly after the exercise, inside the same lesson.
- Remove repetition between lessons. If an idea was explained earlier, link back instead of explaining again.

## Lesson template

```
## N.M Lesson title

*Day X · YYYY-MM-DD*

One- or two-sentence summary in bold or as the first paragraph.

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

## Files

- `README.md` — what this is, how to read it, table of contents.
- `weeks/week-NN-<slug>.md` — the lessons.
- `glossary.md` — terms, alphabetical, plain definitions, each pointing to the lesson that introduces it.
- `reading-list.md` — sources, grouped by week.
- `CHANGELOG.md` — one line per update.
