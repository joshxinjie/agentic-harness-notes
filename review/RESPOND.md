# Author response procedure

You wrote the notes in this repository. A reviewer from a different model has reviewed them under
[REVIEW.md](../REVIEW.md); its findings are given to you below. Answer every finding, apply the fixes you accept, and
report each decision in the output schema. The owner makes the final call: your changes arrive as a pull request they
review, and your decisions count only once they merge it.

## For each finding, decide

| Decision | When | What you do |
|---|---|---|
| `accept` | The finding is right and the proposed change is sound | Make the change |
| `modify` | The problem is real but a different fix is better | Make your fix; say how it differs and why |
| `reject` | The finding is wrong, or the change would do harm | Change nothing; give the evidence (file, line, source, checker output) |
| `defer` | Valid but not worth doing in this pull request | Add a dated item to `BACKLOG.md` and say so |

Judge on the evidence, not on who raised it. Do not accept a finding just to be agreeable, and do not reject one to
defend your earlier work: check it against the lesson's sources and the text before the change (`git log -p`,
`git show <base>:<file>`). If a finding is unclear (`question`), answer it in `reason` and change text only if the
answer shows a problem.

## Rules for changes

1. Follow [STYLE.md](../STYLE.md) exactly. Nothing of substance is lost or invented: every number, identifier,
   caveat, code sketch and source stays (in prose, a table or code). Do not add facts, numbers or sources that are
   not in the lesson's sources.
2. The emails are the record. If a reviewer shows the email itself was wrong, do not silently rewrite the fact: keep
   it and add a short, dated note in the text saying what is wrong and citing the source.
3. Keep each change as small as the finding needs. No unrelated rewording or polish.
4. Never rename a `## ` heading unless every link to its anchor is updated in the same change.
5. Diagrams: edit the Mermaid source in `diagrams/src/`, re-render with `python tools/render_diagrams.py <name>`, and
   never hand-edit a generated `.svg`. After adding or renaming a heading in a week file, run
   `python tools/make_toc.py` to regenerate its contents list.
6. Run `python -m pytest -q` at the end (it includes the link checker, which must report `bad 0`, and the contents
   check), and report the result honestly in `tests`.
7. Add one line to `CHANGELOG.md`: the date, "Review response to <review file>", and the findings fixed.
8. You cannot change the review machinery (`REVIEW.md`, `review/`, `reviews/`, `.github/`) or commit or push; the
   workflow writes the decision log and opens the pull request from your edits.

## Output

Return one JSON object matching the schema: one entry per finding ID given (no more, no fewer), each with the
decision, a reason a reader can check, and what you changed (files, in one line); the test result; and a summary
that fits on a phone screen (counts per decision, then anything the owner should look at first).
