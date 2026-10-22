# Backlog

Valid improvements that were deferred, usually from a cross-model review ([REVIEW.md](REVIEW.md)). Newest first.
Each item: date, what to do, where it came from (a decision ID from [reviews/decisions.md](reviews/decisions.md)).

- 2026-10-22 — `scripts/review_harness/respond.py`: quote a markdown link as code only outside existing code spans,
  so a link inside a longer span is not wrapped again; add a test for that case. (PR8-F2)
- 2026-10-22 — `.github/workflows/respond.yml` failure step: pass the head branch as `env: HEAD_REF` and use
  `$HEAD_REF` in the compare URL instead of interpolating `steps.gate.outputs.head_ref` into the script. (PR8-F3)
- 2026-10-22 — `.github/workflows/respond.yml` failure comment, pushed-branch case: say the decision rows' Fixed-in
  cell still holds the branch name and the author's summary is in the `response-<pr>` artifact. (PR8-F4)
