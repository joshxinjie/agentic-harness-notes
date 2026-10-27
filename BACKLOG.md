# Backlog

Valid improvements that were deferred, usually from a cross-model review ([REVIEW.md](REVIEW.md)). Newest first.
Each item: date, what to do, where it came from (a decision ID from [reviews/decisions.md](reviews/decisions.md)).

- 2026-10-24 — `diagrams/src/online-eval-layers.mmd` and `diagrams/src/world-stand-ins.mmd`: draw the ordering
  edges between sibling options (L1→L2→L3→L4, W1→W2→W3→W4) dotted (`-.->`), keep the layer → queue arrows solid, then
  re-render both with `python3 tools/render_diagrams.py` and check at phone width. Not done in the response because
  `mmdc` could not launch Chrome in that session. (PR #12 review, F5.)
- 2026-10-24 — Week 7 (7.4, 7.6): with network access, confirm against the linked pages (a) LangSmith's weekly spend
  cap per evaluator that pauses it (online-evaluations docs), (b) "Context resets had already gone with Opus 4.5"
  (Anthropic, Mar 2026), (c) "three (later seven)" and "single Codex runs of up to six hours" (OpenAI, Feb 2026); if
  any differs, add a dated note as STYLE.md and RESPOND.md require. (PR #12 review, F7.)
- 2026-10-22 — Normalise the review-section headings across weeks (answer: "Worked answer" in weeks 1, 3, 4, "Integrative answer" in 5, 6, "Integrative exercise — worked answer" in 2; recap: "The week in six paragraphs" in 1, 5, 6, "Recap" in 2, 3, 4), or only their labels in `SHORT` in tools/make_toc.py. Renaming headings means updating every link to `#worked-answer-6` and the like first. From PR #6 review, F8.
