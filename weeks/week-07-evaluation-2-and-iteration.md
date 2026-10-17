# Week 7 — Evaluation II and iteration

[Week 6](week-06-evaluation-1.md) turned runs into numbers you can trust: tasks, graders, metrics, and a paired comparison that says ship, hold or block. This week is about what you do when one of those numbers is bad.

Step one is always reading the run that produced it. A score tells you *that* something failed. The transcript tells you *where* and *why*. We start with how to read one failed transcript properly (7.1), then group many diagnoses into a counted list of failure types that tells you what to fix first (7.2).

The running example is still the nightly investigator for Xin Jie's solar sites.

---

## 7.1 Reading a transcript

*Day 44 · 2026-10-15*

**Reading a failed transcript is a procedure, not skimming. Check the failure is fair, walk back to the earliest step that decided it, rebuild what the model actually saw at that step, and confirm the fix with a fork replay.**

### The idea

Anthropic's eval guide ends with three words: "Read the transcripts!" Reading one well takes four steps.

**1. Check the failure is fair.** Before blaming the agent, rule out the grader, the task and the infrastructure. Does the reference solution pass? Is the expected answer right? Did a tool time out because of the environment? In Anthropic's words: "Failures should seem fair: it's clear what the agent got wrong and why."

**2. Walk backwards to the decisive error.** The wrong ticket is the *symptom*. What you want is the **decisive error step**: the earliest step where a correction would have turned the failure into a success. That definition comes from the Who&When paper (Zhang et al., ICML 2025). Errors compound (the p<sup>n</sup> of [lesson 1.6](week-01-what-an-agent-is.md#16-when-not-to-build-an-agent)), so the last bad step is rarely the cause.

**3. Rebuild what the model saw at that step, then name the layer.** Your trajectory log is not the model's context. Clearing, compaction and skill loading all change what was actually sent. So rebuild the exact request at turn k and ask three questions:

- Was the needed fact present, or buried among distractors? (Layers 2 and 4.)
- Did the tool menu, the tool description or the error text point the right way? (Layer 2.)
- Did the prompt or the loop control allow the right action? (Layers 1, 3 and 5.)

Only when the information was present, clear and allowed is it a model reasoning error.

**4. Confirm with a fork replay.** Patch the suspected cause at turn k. Re-run five times, with tools served from the recorded cassette, and see whether the outcome flips. If it does not flip, you have a story, not a diagnosis.

### An example

SG-03 was expected to be a meter fault. The run filed `root_cause=weather`, with status `success`. Render the run as a turn table:

| Turn | Call | Result |
|---|---|---|
| T1 | `read_memory sites/SG-03.md` | "meter under-reads <200 W/m² since 08-14" |
| T2 | `metrics_get_site` | MAE 3× from the 7th, worst at low irradiance |
| T3 | `weather_get_history(agg=hourly, 6 stations)` | about 38k tokens |
| T4 | *thinking* | "station 4 cloud variability high…" |
| T5 | `ticket_draft(weather, 22%)` | |

Read forwards, T4 looks like a reasoning failure: the model "ignored the memory".

Rebuilding the T4 request shows something else. T3 pushed the context past 30k tokens, and `clear_tool_uses` ([lesson 3.2](week-03-state-and-memory.md#32-context-management-summarisation-compaction-truncation)) wiped the T1 result. Only `note` was excluded from clearing. The model never saw the meter fact.

So the decisive step is T3: an hourly pull that both buried the evidence and triggered the clear. The fixes are in the harness, not the prompt:

- make `agg=daily` the default;
- exclude `read_memory` from clearing.

Fork at T3 with `agg=daily`: 5 of 5 runs file meter. Confirmed.

### Where it lives in the harness

Layer 6. It uses the layer-5 observability from [lesson 5.5](week-05-control-safety-reliability.md#55-observability-tracing-logging-trajectories-replaying-runs): traces joined to trajectories by `tool_use_id`, plus fork replay.

Write each diagnosis as one line, called an **open code**. For example: "T3: hourly pull → memory cleared → weather blamed". In 7.2 those lines get grouped into a taxonomy.

### Common mistakes

Finding the error is hard even for models. On Who&When, the best automated method found the responsible agent 53.5% of the time, but the decisive step only 14.2% of the time. So people read first, and LLM tools (for example Transluce's Docent) help search and cluster many runs. Typical mistakes:

- fixing the last bad step;
- reading the log instead of the rebuilt context;
- diagnosing from one run;
- reaching for a new prompt line when the cause sits in a tool or in what got cleared.

### Try it

*10 min.* MY-01 was expected to be `pipeline_stale`: the ETL was stuck and the actuals were forward-filled. The run filed `meter_drift`.

| Turn | Call | Result |
|---|---|---|
| T1 | `read_memory MEMORY.md` | "MY-01: no notes" |
| T2 | `metrics_get_site(3d)` | MAE 2.4×; actual flat at 4.1 MW from 10-12 14:00 to 10-14 02:00 |
| T3 | *thinking* "flat actuals = stuck sensor" · `pipeline_get_status` | `is_error`: "Error: timeout" |
| T4 | `weather_get_history(daily)` | normal, max delta 3% |
| T5 | `note` | "pipeline: n/a; weather 3% rejected; meter: flat 4.1 MW 36 h, likely stuck" |
| T6 | `ticket_draft(meter_drift, 4.1)` | no "unverified" line |

1. Write the one-line open code.
2. Name the decisive step and its layer, and say why it is not T6.
3. List every harness fix you can see, ranked by how many future failures each removes.
4. Write the fork replay that would confirm your top fix.
5. Name one thing this transcript cannot tell you, and where you would look for it.

### Worked answer

**1. Open code:** "T3: `pipeline_get_status` timed out with a bare 'Error: timeout'; the agent dropped the pipeline hypothesis as n/a and read 36 h of flat actuals (forward-fill) as a stuck meter."

**2. The decisive step is T3**, in layer 2 (the executor and its error text). The tool failed with no retry and no information. Fix T3 and the run flips. The fix could be a retry that returns "stale since 10-12 13:55", or an error that says "status UNKNOWN, do not rule pipeline out; flat actuals are also what forward-fill looks like".

T6 is only the symptom. By T6 the notes already said "pipeline: n/a". So even a perfect T6 could at best have produced an honest "unverified" meter ticket, never `pipeline_stale`. The thinking at T3 ("flat = stuck sensor") is anchoring, but the model only had one candidate explanation in front of it.

**3. Fixes, ranked by reach:**

1. **Executor-wide:** retry infrastructure errors in the tool client, then return problem/fix/data with "status unknown, not ruled out" ([lesson 4.3](week-04-prompt-and-tool-design.md#43-tool-error-messages-as-instructions-designing-for-recovery)). This covers every tool, every night.
2. **`guard_ticket`** rejects a ticket when any checklist hypothesis is untested but missing from an "unverified" section, and caps confidence at low.
3. **`metrics_get_site`** flags runs of identical consecutive actuals as "possible forward-fill / stuck sensor" (both, not one).
4. **The note format** bans "n/a" and requires "untested (reason)".

**4. Fork replay.** Take the messages up to T3 and replace the pipeline `tool_result` with the new error text. Run 5 times on the live model, with other tools served from the cassette. Decide up front what happens if the agent retries `pipeline_get_status`: serve a "stale" fixture, and mark the fork as partly synthetic. Run 5 unpatched forks as a control. Pass: at least 4 of 5 end in `pipeline_stale` or an escalation, not `meter_drift`.

**5. What the transcript can't tell you:** whether the timeout was a real API outage or a harness timeout set too short. Look at the span latency in the trace and at the pipeline service's own logs.

Common slips: calling T6 decisive, and fixing it with a prompt line ("always check the pipeline").

### Sources

- [Anthropic — Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- [Zhang et al. — Which Agent Causes Task Failures and When? (Who&When, ICML 2025)](https://arxiv.org/abs/2505.00212)
- [Langfuse — Error analysis to evaluate LLM applications](https://langfuse.com/blog/2025-08-29-error-analysis-to-evaluate-llm-applications)

---

## 7.2 Error taxonomies and common failure modes

*Day 45 · 2026-10-16*

**7.1 turned one failed run into one open code. This lesson turns a hundred open codes into a taxonomy: a counted list of failure categories that tells the rest of Week 7's improvement loop what to fix first.**

### The idea

An open code is one anecdote. A **taxonomy** is the same anecdotes grouped into named categories and counted. Hamel Husain calls the grouping step, **axial coding**, "the most important step". The procedure:

1. **Open-code** about 30 failing traces yourself: one line each about the *first* thing that went wrong.
2. **Cluster** the lines into categories. An LLM can propose the clusters, but you decide them.
3. **Write definitions:** one sentence per category, plus one example that belongs and one that doesn't.
4. **Re-code and count.** Keep adding traces until new ones stop producing new categories (saturation; a working pool of about 100 traces, as in [lesson 6.2](week-06-evaluation-1.md#62-building-an-eval-set-from-real-failures-the-taskgraderenvironment-triad)).

You don't have to start from a blank page. Two published agent taxonomies work as checklists.

**MAST** (Cemri et al., NeurIPS 2025) comes from 200+ traces across 7 multi-agent frameworks. It has 14 failure modes in 3 groups:

- **Specification issues**, 41.8% of failures. Includes step repetition (17.1%) and being unaware of stopping conditions (9.8%).
- **Inter-agent misalignment**, 36.9%. Includes reasoning–action mismatch (14.0%) and failing to ask for clarification (11.7%).
- **Task verification**, 21.3%. Includes premature termination, missing verification and incorrect verification.

The method matters as much as the list. Agreement between annotators (measured as κ, kappa) started at 0.24 and reached 0.88 only after several rounds of refining the definitions. An o1 judge given few-shot examples reached κ = 0.77 against the experts.

**AgentErrorTaxonomy** (Zhu et al., 2025) is built from 500+ failed single-agent trajectories. It groups errors by module:

| Module | Error types |
|---|---|
| Memory | hallucination, retrieval failure |
| Reflection | progress misjudgement, outcome misinterpretation, causal misattribution |
| Planning | impossible action, constraint ignorance |
| Action | format or parameter error, action–plan mismatch |
| System | tool execution error, step limit, environment error |

Even with step-level labels, its annotators only reached κ = 0.55. Its **AgentDebug** method finds the critical (earliest decisive) error in 45% of cases, against 28% for baselines. Re-running from that step improved ALFWorld success by up to 26% relative.

Both papers make the same point as 7.1: early errors cascade, so you label the root, not the wreckage.

**The harness twist.** Published labels describe what the *agent* did ("outcome misinterpretation"). Your own taxonomy should also say *where the fix lives*. The MY-01 failure from 7.1 is "causal misattribution" in the paper's terms, but the cause was an opaque tool error. So every category needs three things:

- a **definition**;
- a **harness layer and owner**;
- a **detector**: a code check or a calibrated judge that can find more cases in traces automatically.

Keep separate "unfair" categories (grader bug, task bug, infrastructure), so they never count against the agent.

### An example

A worked fragment from 40 nightly failures:

| Category | n | Layer | Detector |
|---|---|---|---|
| Tool failure absorbed silently | 11 | 2 | `is_error`/timeout followed by a verdict of "n/a" or "normal" in the notes |
| Context flooded or cleared | 9 | 2/4 | tool result > 10k tokens, or memory cleared before the verdict |
| Untested hypothesis filed | 7 | 5 | ticket lacks "unverified" while the notes show an untested item |
| No completion signal | 5 | 3 | status ≠ success, no ticket |
| Vague ticket | 4 | 1 | actionability judge (TPR/TNR) |
| Unfair: grader, fixture or infra | 4 | 6 | reference fails, or config diff |

Count by root category, one per trace. Then rank by **count × severity**, not count alone. One silent wrong ticket outweighs three budget stops that produced no ticket.

### Where it lives in the harness

Layer 6. The taxonomy becomes:

- a field in your trace store;
- the source of new eval tasks (6.2);
- the set of detectors that 7.4 runs over production.

### Common mistakes

Without counts, you fix whichever failure you saw last. With them, the top two categories usually cover most failures. Typical mistakes:

- adopting MAST wholesale, so the labels describe the model and not your harness;
- tagging every downstream symptom, which double-counts;
- categories so broad ("reasoning error") that they point at no fix;
- never checking that two people label the same trace the same way.

### Try it

*10–15 min.* Here are twelve open codes from the nightly batch:

1. SG-03 T3: hourly weather pull → memory cleared → weather blamed.
2. MY-01 T3: pipeline timeout, "Error: timeout" → pipeline n/a → meter filed.
3. SG-05 T2: hourly pull, 40k tokens → budget, no ticket.
4. SG-02 T4: cited `cloud_delta` 38% from an archive doc → provenance trip.
5. SG-01 T7: ticket "multiple factors, monitor" (no action).
6. SG-04 T5: vendor 429 after 2 stations → note "weather normal".
7. MY-02 T6: `metrics_get_site` with identical args 4× → stuck.
8. SG-03: grader expects `curtail_pct` 40; fixture stores 0.4 → unfair.
9. SG-06 T8: meter confirmed, text-only `end_turn`, no `ticket_submit`.
10. MY-01 T4: thinking says "check curtailment next", calls weather.
11. SG-02 quiet day T5: filed `meter_drift` on 1.3× MAE, below threshold.
12. SG-05 T3: pipeline timeout at 30 s in container → status error.

Your tasks:

1. Axial-code them into at most 6 categories, each with a one-sentence definition, a harness layer and a fix owner.
2. Count and rank them by count × severity.
3. Give each code its nearest MAST or AgentErrorTaxonomy label, and name one code where that label hides the harness cause.
4. Write a detector for your top two categories.
5. Which code fits nowhere, and what should you do with it?

### Worked answer

*Answer coming in the next brief.*

### Sources

- [Cemri et al. — Why Do Multi-Agent LLM Systems Fail? (MAST, NeurIPS 2025)](https://arxiv.org/abs/2503.13657)
- [Zhu et al. — Where LLM Agents Fail and How They Can Learn from Failures (AgentErrorTaxonomy / AgentDebug, 2025)](https://arxiv.org/abs/2509.25370)
- [Hamel Husain — Why is error analysis so important, and how is it performed?](https://hamel.dev/blog/posts/evals-faq/why-is-error-analysis-so-important-in-llm-evals-and-how-is-it-performed.html)

---

*Week 7 review coming soon.*
