# Backlog

Valid improvements that were deferred, usually from a cross-model review ([REVIEW.md](REVIEW.md)). Newest first.
Each item: date, what to do, where it came from (a decision ID from [reviews/decisions.md](reviews/decisions.md)).

- 2026-10-22 — `scripts/review_harness/respond.py` `cell()`: cut to `limit` before quoting links as code (or skip a
  link that straddles the cut), so a cut reason cannot end in an unmatched backtick; add a case with `limit=20` and a
  link crossing the cut to `test_cells_quote_markdown_links_as_code`, asserting an even number of backticks. (Third
  PR #8 review, F4.)
- 2026-10-22 — `tests/test_review_harness.py`: once the PR8-F3 item below is done, run the failure step's
  `reason=`…`fi` block with `bash -c` and `RUNNER_TEMP` set to a temp dir holding only `pushed_branch`; assert the
  outcome names the branch and the compare URL ends in `<head_ref>...<branch>`, and that with `fix_pr_url` present the
  "later step failed" text wins. (Third PR #8 review, F3.)
- 2026-10-22 — `.github/workflows/review.yml`: after checking out main's harness, tests and decision log over the PR
  head, also run `python -m pytest -q tests` and `python3 tools/check_links.py .` on an untouched checkout of the PR
  head (for example `git worktree add $RUNNER_TEMP/pr pr-head`) and put both results in the material, or at least
  list the replaced files there. (Second PR #8 review, F2; same gap as PR8-F6.)
- 2026-10-22 — `.github/workflows/respond.yml`: guard the archive and artifact steps with
  `!cancelled() && steps.respond.outputs.code == '0'` instead of `always() && ...`, and update the string asserted in
  `test_respond_workflow_reports_a_pushed_branch_without_a_pr`. (Second PR #8 review, F3.)
- 2026-10-22 — `scripts/review_harness/respond.py` `MD_LINK`: consume an optional leading `!` so `![alt](src)` does not
  keep a stray `!`, and reword the docstring to say every quoted link is shown as code; add `![a](b)` and
  `[BACKLOG.md](../BACKLOG.md)` to `test_cells_quote_markdown_links_as_code`. (Second PR #8 review, F4.)
- 2026-10-22 — `scripts/review_harness/respond.py`: quote a markdown link as code only outside existing code spans,
  so a link inside a longer span is not wrapped again; add a test for that case. (PR8-F2)
- 2026-10-22 — `.github/workflows/respond.yml` failure step: pass the head branch as `env: HEAD_REF` and use
  `$HEAD_REF` in the compare URL instead of interpolating `steps.gate.outputs.head_ref` into the script. (PR8-F3)
- 2026-10-22 — `.github/workflows/respond.yml` failure comment, pushed-branch case: say the decision rows' Fixed-in
  cell still holds the branch name and the author's summary is in the `response-<pr>` artifact. (PR8-F4)
- 2026-10-22 — Normalise the review-section headings across weeks (answer: "Worked answer" in weeks 1, 3, 4, "Integrative answer" in 5, 6, "Integrative exercise — worked answer" in 2; recap: "The week in six paragraphs" in 1, 5, 6, "Recap" in 2, 3, 4), or only their labels in `SHORT` in tools/make_toc.py. Renaming headings means updating every link to `#worked-answer-6` and the like first. From PR #6 review, F8.
- 2026-10-22 — Rule 6 in review/RESPOND.md should say to run `python3 tools/make_toc.py` after adding or renaming a heading. The author can't edit review/; the owner should make this change. (CI catches a stale list anyway, through tests/test_make_toc.py.) From PR #6 review, F7.
