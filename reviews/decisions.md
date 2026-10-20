# Review decisions

Every finding from a cross-model review ([REVIEW.md](../REVIEW.md)) gets one row here once it is decided. Reviewers
read this log before reviewing and do not re-raise a rejected finding without new evidence (they cite the decision
ID in `related_decision`).

**Decision:** `accept` (fix as proposed) · `modify` (fix differently, say how) · `reject` (no change, say why) ·
`defer` (valid, not now; add a dated item to [BACKLOG.md](../BACKLOG.md))

**Decided by:** Xin Jie. `/respond` writes the author's proposed rows here in its pull request; they count as
decided once Xin Jie merges it (or edits them first).

**IDs:** `PR<n>-F<k>` for finding F<k> of a PR's first review, `PR<n>-<round>-F<k>` for later rounds (PR5-2-F1 is
F1 of the second review of #5); project reviews use `PROJ-<date>[-<round>]-F<k>`. Reviewers cite these IDs in
`related_decision`.

Review files (`YYYY-MM-DD-<scope>-<reviewer>.json`, scope `project` or `pr<number>`) sit in this folder.
Add new rows at the top; never edit a decided row, add a new one that supersedes it. A row marked "(author; for Xin
Jie to confirm)" records the author's response and is provisional: when Xin Jie confirms or reverses it, a new row
supersedes it.

| ID | Date | Review file | Finding | Reviewer | Severity | Decision | Reason | Fixed in |
|---|---|---|---|---|---|---|---|---|
