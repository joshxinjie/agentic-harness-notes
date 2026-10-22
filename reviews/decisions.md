# Review decisions

Every finding from a cross-model review ([REVIEW.md](../REVIEW.md)) gets one row here once it is decided. Reviewers
read this log before reviewing and do not re-raise a rejected finding without new evidence (they cite the decision
ID in `related_decision`).

**Decision:** `accept` (fix as proposed) · `modify` (fix differently, say how) · `reject` (no change, say why) ·
`defer` (valid, not now; add a dated item to [BACKLOG.md](../BACKLOG.md))

**Decided by:** the owner. `/respond` writes the author's proposed rows here in its pull request; they count as
decided once the owner merges it (or edits them first).

**IDs:** `PR<n>-F<k>` for finding F<k> of a PR's first review, `PR<n>-<round>-F<k>` for later rounds (PR5-2-F1 is
F1 of the second review of #5); project reviews use `PROJ-<date>[-<round>]-F<k>`. Reviewers cite these IDs in
`related_decision`.

Review files (`YYYY-MM-DD-<scope>-<reviewer>.json`, scope `project` or `pr<number>`) sit in this folder.
Add new rows at the top; never edit a decided row, add a new one that supersedes it. A row marked "(author; for the owner to confirm)" records the author's response and is provisional: when the owner confirms or reverses it, a new row
supersedes it.

| ID | Date | Review file | Finding | Reviewer | Severity | Decision | Reason | Fixed in |
|---|---|---|---|---|---|---|---|---|
| PR8-F6 | 2026-10-22 | [2026-10-22-pr8-fable.json](2026-10-22-pr8-fable.json) (copy of `reviewer/archive`) | F6: Could not run HEAD's test suite; 83 pass on the checkout available, 85 claimed | fable | question | accept | Answer: I ran `python -m pytest -q tests` on the PR head in this worktree and got 86 passed. That is the 85 claimed (83 plus 2 new) plus the F1 test added here. The link checker reports bad 0. No text change was needed for this finding. | #9 |
| PR8-F5 | 2026-10-22 | [2026-10-22-pr8-fable.json](2026-10-22-pr8-fable.json) (copy of `reviewer/archive`) | F5: No CHANGELOG line for this change | fable | nit | accept | REVIEW.md E asks for a CHANGELOG line per change, and the 2026-10-22 entry shows machinery and docs changes get one. I added a line describing the PR's /respond changes and this review response. | #9 |
| PR8-F4 | 2026-10-22 | [2026-10-22-pr8-fable.json](2026-10-22-pr8-fable.json) (copy of `reviewer/archive`) | F4: After a push-but-no-PR failure the decision rows still say "Fixed in: respond/..." and the summary is never shown | fable | minor | defer | Valid: `exit 1` runs before the sed that rewrites the Fixed-in cell, and the failure comment leaves out the summary. The fix is in respond.yml, which is off limits under rule 8. | BACKLOG.md: 2026-10-22 item 'failure comment, pushed-branch case: mention Fixed-in cell and response artifact' (PR8-F4) |
| PR8-F3 | 2026-10-22 | [2026-10-22-pr8-fable.json](2026-10-22-pr8-fable.json) (copy of `reviewer/archive`) | F3: Failure comment interpolates the head branch name into the shell script instead of via env | fable | minor | defer | Valid: the failure step interpolates `${{ steps.gate.outputs.head_ref }}` into the script, unlike the env HEAD_REF pattern used elsewhere in the file. The file is .github/workflows/respond.yml, and rule 8 puts .github/ off limits for me. | BACKLOG.md: 2026-10-22 item 'failure step: pass the head branch as env HEAD_REF' (PR8-F3) |
| PR8-F2 | 2026-10-22 | [2026-10-22-pr8-fable.json](2026-10-22-pr8-fable.json) (copy of `reviewer/archive`) | F2: MD_LINK wraps a link that is already inside a longer code span, breaking the cell's markdown | fable | minor | defer | Valid as traced: the lookbehind and lookahead only check the characters right next to the link, so a link inside a longer code span gets wrapped again. The fix belongs in scripts/review_harness/respond.py, which RESPOND.md rule 8 bars me from changing in a /respond run. | BACKLOG.md: 2026-10-22 item 'quote a markdown link as code only outside existing code spans' (PR8-F2) |
| PR8-F1 | 2026-10-22 | [2026-10-22-pr8-fable.json](2026-10-22-pr8-fable.json) (copy of `reviewer/archive`) | F1: Untracked .pyc files will come back: no .gitignore, and the respond workflow runs `git add -A` | fable | major | accept | Confirmed: the only .gitignore was .pytest_cache's own, and respond.yml runs `git add -A` after the tests, so the next /respond run would commit the .pyc files again. I added a top-level .gitignore (__pycache__/, *.pyc, .pytest_cache/) and a test that it lists them and that `git ls-files` tracks no .pyc. After pytest ran, `git status` showed no bytecode. I did not do the optional pathspec change in the workflow because rule 8 puts .github/ off limits. | #9 |
