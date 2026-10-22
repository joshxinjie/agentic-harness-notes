# Backlog

Valid improvements that were deferred, usually from a cross-model review ([REVIEW.md](REVIEW.md)). Newest first.
Each item: date, what to do, where it came from (a decision ID from [reviews/decisions.md](reviews/decisions.md)).

- 2026-10-22 — Normalise the review-section headings across weeks (answer: "Worked answer" in weeks 1, 3, 4, "Integrative answer" in 5, 6, "Integrative exercise — worked answer" in 2; recap: "The week in six paragraphs" in 1, 5, 6, "Recap" in 2, 3, 4), or only their labels in `SHORT` in tools/make_toc.py. Renaming headings means updating every link to `#worked-answer-6` and the like first. From PR #6 review, F8.
- 2026-10-22 — Rule 6 in review/RESPOND.md should say to run `python3 tools/make_toc.py` after adding or renaming a heading. The author can't edit review/; the owner should make this change. (CI catches a stale list anyway, through tests/test_make_toc.py.) From PR #6 review, F7.
- 2026-10-22 — Untrack compiled bytecode: `git rm -r --cached tools/__pycache__ tests/__pycache__ scripts/review_harness/__pycache__ scripts/review_harness/providers/__pycache__`. .gitignore now ignores them, but files that are already tracked keep showing up in diffs. The author session wasn't allowed to run `git rm`, and scripts/review_harness/ is off-limits to it. From PR #6 review, F4.
