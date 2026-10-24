# Glossary

Every term from the notes, A to Z, in plain words. Each entry links to the lesson that first explains it. Numbers in brackets such as (3.2) point to other lessons.

[Numbers](#numbers) · [A](#a) · [B](#b) · [C](#c) · [D](#d) · [E](#e) · [F](#f) · [G](#g) · [H](#h) · [I](#i) · [J](#j) · [K](#k) · [L](#l) · [M](#m) · [N](#n) · [O](#o) · [P](#p) · [R](#r) · [S](#s) · [T](#t) · [U](#u) · [V](#v) · [W](#w)

## Numbers

**200k-token rule**  
If the knowledge base is under about 200,000 tokens (about 500 pages), skip retrieval and put the whole thing in the prompt with prompt caching (4.6). See [3.3](weeks/week-03-state-and-memory.md#33-retrieval-for-agents-rag-vs-agentic-search).


## A

**A/A test**  
Running the baseline against itself. The difference you see is the noise floor. See [6.5](weeks/week-06-evaluation-1.md#65-regression-testing-a-harness-change-ab-on-prompts-and-tools).

**ACI principles (SWE-agent)**  
Simple actions (understandable without demonstrations); efficient actions (navigation and editing combined into a few actions); feedback that is informative but short; guardrails that stop errors spreading and speed up recovery. See [4.4](weeks/week-04-prompt-and-tool-design.md#44-agent-computer-interface-aci).

**Adaptive attack**  
An attack tuned against one specific defence. *The Attacker Moves Second* (Oct 2025) got past 12 published defences at over 90% success for most of them, and human red-teamers succeeded 100% of the time — which is why detection alone is never the boundary. See [5.4](weeks/week-05-control-safety-reliability.md#54-prompt-injection-and-untrusted-content).

**Adaptive thinking**  
`thinking: {"type": "adaptive"}`: the model decides for each request whether to think and how much. It is the default on Opus 5+, Sonnet 5+ and Fable 5.1+. It replaces manual **extended thinking** (`type: "enabled"`, a fixed `budget_tokens` of at least 1,024 and below `max_tokens`, thinks on every request), which is kept for predictable latency and cost. See [2.2](weeks/week-02-core-mechanics.md#22-react-and-reasoning-then-acting-extended-thinking-in-the-loop).

**Agent**  
A system where the LLM directs its own process and decides which tools to use. Willison's short version: "an LLM agent runs tools in a loop to achieve a goal". It breaks down as *model(s) + harness*. See [1.1](weeks/week-01-what-an-agent-is.md#11-llm-call-vs-workflow-vs-agent).

**Agent loop**  
The harness cycle: call the model with tools, run any tools it asks for, append the results, and call again. It repeats until the model stops asking for tools. See [1.2](weeks/week-01-what-an-agent-is.md#12-the-agent-loop).

**Agent Skills open standard**  
The `SKILL.md` format published as an open specification (agentskills.io, Dec 2025). Required: `name` (at most 64 characters, lowercase letters, digits and hyphens, matching the folder name) and `description`. Optional: `license`, `compatibility`, `metadata`, and experimental `allowed-tools`. Adopted by Claude Code, Codex, Cursor, VS Code, GitHub, goose, Amp, OpenCode, Letta and others. See [4.5](weeks/week-04-prompt-and-tool-design.md#45-skills-procedural-knowledge-loaded-on-demand).

**Agent system prompt**  
The stable start of the assembled document the model reads on every turn, next to tool definitions, the transcript and injected context (memory index, triage table). It is written for a reader who will also see the tool results, so it says what the results cannot. It is kept byte-for-byte the same across turns so the cache prefix holds (4.6). See [4.1](weeks/week-04-prompt-and-tool-design.md#41-system-prompt-architecture-for-agents).

**Agent-computer interface (ACI)**  
"an abstraction layer between the LM agent and computer" (SWE-agent): the whole channel of observations and actions — which actions exist and how much each does, what each observation looks like, which state is visible, and which guardrails sit on actions. Tool design (4.2) is about one tool; the ACI is the interface as a whole. Anthropic: put as much effort into ACI as into HCI. See [4.4](weeks/week-04-prompt-and-tool-design.md#44-agent-computer-interface-aci).

**AgentErrorTaxonomy / AgentDebug**  
A taxonomy built from 500+ failed single-agent trajectories, grouping errors by module: memory, reflection, planning, action and system. Its AgentDebug method finds the earliest decisive error in 45% of cases (baselines 28%), and re-running from that step improved ALFWorld success by up to 26% relative. See [7.2](weeks/week-07-evaluation-2-and-iteration.md#72-error-taxonomies-and-common-failure-modes).

**Agentic search**  
Retrieval as a tool call inside the loop. The model sends a query (`grep`, `glob`, `read_file`, SQL, `search(q)`), reads the result, and searches again with what it learned, so it handles several hops by design. Claude Code's index-free ripgrep-plus-read is the standard example; Anthropic's just-in-time retrieval (2.1) is the same idea. See [3.3](weeks/week-03-state-and-memory.md#33-retrieval-for-agents-rag-vs-agentic-search).

**Agents Rule of Two**  
A session should have at most two of: (A) handles untrusted input, (B) can reach sensitive systems or data, (C) changes state or communicates outward. All three needs human oversight (Meta, Oct 2025). See [5.4](weeks/week-05-control-safety-reliability.md#54-prompt-injection-and-untrusted-content).

**AGENTS.md / CLAUDE.md**  
Instruction files kept in a repository that a coding-agent harness puts into the prompt. Best kept short (about 100–200 lines), as a map to fuller docs rather than a dump. Details in 3.4. See [1.4](weeks/week-01-what-an-agent-is.md#14-what-a-harness-is).

**Annotation queue**  
Where flagged production runs wait for a person to read them. Each gets an open code (7.1) and a category (7.2), and then becomes a new eval task (6.2). See [7.4](weeks/week-07-evaluation-2-and-iteration.md#74-online-evaluation-and-monitoring).

**Annotator agreement (κ)**  
κ (kappa) measures how often two labellers give the same label, beyond what chance would give. MAST's annotators started at κ = 0.24 and reached 0.88 only after several rounds of refining definitions; check it before you trust your own taxonomy. See [7.2](weeks/week-07-evaluation-2-and-iteration.md#72-error-taxonomies-and-common-failure-modes).

**APITimeoutError**  
Raised by the Python SDK when a request takes longer than the timeout (10 minutes by default; can be set per client or per request). Timed-out requests are retried by default. See [2.6](weeks/week-02-core-mechanics.md#26-error-handling-retries-backoff-and-feeding-tool-errors-back-to-the-model).

**Append-only context**  
The design rule that follows from caching: never edit earlier content. Send state changes as added messages (Claude Code's `<system-reminder>` in the next user message or tool result), keep the tool set fixed and turn modes into tools (EnterPlanMode/ExitPlanMode), and defer schemas (`defer_loading`) or mask tools (Manus) rather than removing them. See [4.6](weeks/week-04-prompt-and-tool-design.md#46-prompt-caching-and-cost).

**Approval fatigue**  
People asked too often approve by reflex, so the prompt stops being a real control. Sandboxing safely cut Claude Code's permission prompts by 84% (Anthropic, Oct 2025), which makes the remaining asks count. See [5.1](weeks/week-05-control-safety-reliability.md#51-permissions-and-sandboxing).

**Approval gate**  
A pause the harness triggers before a chosen tool call runs. The person approves, approves with edits, or rejects with a reason. Use it only on actions that cannot be undone or that others will see. See [5.2](weeks/week-05-control-safety-reliability.md#52-human-in-the-loop-approval-gates-interrupts-escalation).

**Assumption register**  
A table with one row per harness component: the model limitation it assumes, the ablation that would retire it, and whether it is a model-limit or a world-limit. See [7.6](weeks/week-07-evaluation-2-and-iteration.md#76-case-study-how-labs-iterate-on-coding-agent-harnesses).

**Attention budget**  
Anthropic's way of saying context is a limited resource with shrinking returns. Attention forms n² pairwise links between tokens and gets spread thinner as context grows, so every added token reduces the model's ability to use the rest. See [2.1](weeks/week-02-core-mechanics.md#21-context-window-as-working-memory).

**Augmented LLM**  
An LLM call plus tools, retrieval and memory that the model can ask for. Anthropic's term for the basic building block of agentic systems. See [1.1](weeks/week-01-what-an-agent-is.md#11-llm-call-vs-workflow-vs-agent).

**Auto memory (Claude Code)**  
Notes Claude writes for itself in `~/.claude/projects/<project>/memory/`: a `MEMORY.md` index (one line per memory) plus one topic file per memory. Kept per git repository, shared across worktrees, stored only on that machine, and not removed by transcript cleanup. On by default (`autoMemoryEnabled`, `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`, `autoMemoryDirectory`). Subagents do not inherit it (except forks); they can have their own through the `memory` field. See [3.4](weeks/week-03-state-and-memory.md#34-persistent-memory-files-and-memory-as-documents).

**Auto-compact (Claude Code)**  
The compaction Claude Code runs itself as the window nears its limit (threshold per model; `/autocompact <tokens>` sets it; `/compact <focus>` runs it now with instructions; `/rewind` → "Summarize from/up to here" compacts part of the history; `/clear` between unrelated tasks). What survives depends on where content lives: the system prompt, project CLAUDE.md, auto memory and the plan-mode plan are re-injected from disk; up to five recently changed files are read again (over 5,000 tokens → path reference only); bodies of skills already used are re-injected, capped at 5,000 tokens each and 25,000 in total, oldest dropped first; hook output, path-scoped rules and earlier tool results are summarised with the rest; `SessionStart` hooks matching the `compact` source add context back. See [3.2](weeks/week-03-state-and-memory.md#32-context-management-summarisation-compaction-truncation).

**Autonomy**  
How far an agent works without a human directing it. It is a spectrum, not yes-or-no. See [1.1](weeks/week-01-what-an-agent-is.md#11-llm-call-vs-workflow-vs-agent).

**Autonomy dial**  
The choice of how much control flow to hard-code and how much to hand to the model: no LLM → single call → workflow → hybrid → agent. This is the "layer-zero" harness decision, made before anything else. See [1.1](weeks/week-01-what-an-agent-is.md#11-llm-call-vs-workflow-vs-agent).

**Average tools per tool-calling message**  
The health metric for parallel calls: total `tool_use` blocks ÷ assistant messages that contain any. It should be above 1.0 if parallel calls are happening. See [5.6](weeks/week-05-control-safety-reliability.md#56-latency-and-cost-budgets-parallel-tool-calls-streaming).


**Axial coding**  
The step after open coding: grouping one-line failure notes into named categories, each with a definition and an include and exclude example. Hamel Husain calls it "the most important step". See [7.2](weeks/week-07-evaluation-2-and-iteration.md#72-error-taxonomies-and-common-failure-modes).

## B

**Back-pressure**  
Fixed, rule-based checks (tests, type checks, linters, builds) that push back on the model's output before it is accepted. This is the feedback layer. See [1.4](weeks/week-01-what-an-agent-is.md#14-what-a-harness-is).

**Balanced problem set**  
Tasks that cover both where a behaviour should happen and where it should not (should-file / should-not-file). "one-sided evals create one-sided optimization". See [6.2](weeks/week-06-evaluation-1.md#62-building-an-eval-set-from-real-failures-the-taskgraderenvironment-triad).

**Bare vs scoped deny**  
Denying a tool by name alone (`Bash`) removes it from the model's context completely (enforced at the schema). A scoped deny (`Bash(rm *)`) keeps the tool and blocks matching calls when they run. See [5.1](weeks/week-05-control-safety-reliability.md#51-permissions-and-sandboxing).

**Batch-level deadline**  
The wall-clock time by which a whole batch of runs (for example 40 sites) must finish. Divided by concurrency, it sets each run's time cap. See [5.6](weeks/week-05-control-safety-reliability.md#56-latency-and-cost-budgets-parallel-tool-calls-streaming).

**τ²-bench**  
The successor to τ-bench (adds a telecom domain): a simulated user + domain tools + a policy, graded on the final database state with pass^k. See [6.6](weeks/week-06-evaluation-1.md#66-public-benchmarks-swe-bench-τ-bench-gaia-terminal-bench-and-their-limits).

**Binary / weighted / hybrid scoring**  
Ways to combine graders: all must pass; a weighted sum must clear a threshold; or hard gates plus a weighted remainder. See [6.3](weeks/week-06-evaluation-1.md#63-graders-exact-match-rubric-llm-as-judge-outcome-checks).

**Budget-terminated run**  
A run that ended because a budget ran out, not because it finished. It gets its own status (`error_max_turns`, `error_max_budget_usd`, `budget`) plus cost and turn count, and either no result or a clearly labelled partial one. The graceful version: "Budget reached — answer now, say what is unverified" plus one last `tool_choice="none"` call. See [2.5](weeks/week-02-core-mechanics.md#25-stopping-conditions-step-budgets-and-loop-detection).


## C

**Cache accounting**  
With caching on, `usage.input_tokens` counts only the tokens after the last breakpoint. Total input = `cache_read_input_tokens + cache_creation_input_tokens + input_tokens`. Hit rate = read / total. See [4.6](weeks/week-04-prompt-and-tool-design.md#46-prompt-caching-and-cost).

**Cache boundary (prompt)**  
The marker between text that never changes (role, constraints, procedures, examples — the same in every run) and material that changes per run or per turn (site, window, memory index, budget left). The order reflects caching costs (4.6) and attention: rules come before facts that change. See [4.1](weeks/week-04-prompt-and-tool-design.md#41-system-prompt-architecture-for-agents).

**Cache break**  
Any change of even one byte before the breakpoint: timestamps or run ids in the system prompt, tools added or removed, a `tool_choice` change (messages level), images, thinking or effort changes (depends on the model), a model switch (caches are per model), JSON keys in a non-fixed order, edits to earlier messages (context clearing and compaction break it on purpose — `clear_at_least` makes each one worth it). The output is still correct; the cost is silent. See [4.6](weeks/week-04-prompt-and-tool-design.md#46-prompt-caching-and-cost).

**Cache pre-warming**  
Sending one request before a batch or fan-out so the shared prefix is written once. Needed because a cache entry is only available after the first response starts, so parallel cold requests each pay for the write. Goes with the TTL choice: sequential work refreshes a 5-minute entry on every read; a 1-hour TTL (2× write) only pays off when gaps are longer than 5 minutes. See [4.6](weeks/week-04-prompt-and-tool-design.md#46-prompt-caching-and-cost).

**Cache pricing and TTL**  
Compared with the base input price: reads cost 0.1× (less on some newer models), 5-minute writes 1.25×, 1-hour writes 2× (`"ttl":"1h"`). The lifetime counts from the start of the last request that wrote or read the entry. The minimum cacheable length depends on the model (512–4,096 tokens). See [4.6](weeks/week-04-prompt-and-tool-design.md#46-prompt-caching-and-cost).

**cache_control / breakpoint**  
`{"type":"ephemeral"}` on a content block marks the end of a cacheable prefix. At most 4 per request. Each breakpoint looks back at most 20 block positions for an earlier entry (a run of back-to-back tool_use/tool_result blocks counts as one). A single top-level `cache_control` turns on *automatic caching*: the breakpoint moves to the last cacheable block as the conversation grows. See [4.6](weeks/week-04-prompt-and-tool-design.md#46-prompt-caching-and-cost).

**canUseTool (Claude Agent SDK)**  
A callback asked only about calls that no rule or mode has already approved. It returns allow (optionally with `updatedInput`, applied silently — the model "isn't told you changed anything") or deny with a `message` the model sees. It can stay pending for as long as needed; a PreToolUse hook returning `defer` lets the process exit and resume later. See [5.2](weeks/week-05-control-safety-reliability.md#52-human-in-the-loop-approval-gates-interrupts-escalation).

**Capability eval**  
Tasks the agent mostly fails today (low pass rate, "a hill to climb"). See [6.2](weeks/week-06-evaluation-1.md#62-building-an-eval-set-from-real-failures-the-taskgraderenvironment-triad).

**Chain-of-thought (CoT)**  
Reasoning tokens written before an answer, with no tool use in between. Prone to making things up and to errors that carry forward, which ReAct's observations correct. See [2.2](weeks/week-02-core-mechanics.md#22-react-and-reasoning-then-acting-extended-thinking-in-the-loop).

**Checkpoint**  
A snapshot of everything the loop needs to carry on — transcript, plan object, turn counter, stuck-detector state, token totals, notes path, `done` set — saved to lasting storage under a run id at a clear boundary. It holds one run's state, not knowledge (compare 3.4). See [3.5](weeks/week-03-state-and-memory.md#35-checkpointing-and-resumability).

**Checkpoint boundary**  
The point in the loop where a checkpoint is consistent: after tool results are appended and before the next model call. Then every `tool_use` has its `tool_result` and nothing has been sent that is not recorded. Saving between the model call and running the tools means tools must run again on resume. See [3.5](weeks/week-03-state-and-memory.md#35-checkpointing-and-resumability).

**Checkpointer (LangGraph)**  
The plug-in storage layer (`InMemorySaver`, `SqliteSaver`, `PostgresSaver`, `MongoDBSaver`, …) that saves a `StateSnapshot` at every super-step when a graph is compiled with one. `thread_id` (in `config.configurable`) is the main key for saving and loading. See [3.5](weeks/week-03-state-and-memory.md#35-checkpointing-and-resumability).

**Clarification tool**  
A question tool the model triggers (Claude `AskUserQuestion`: 1–4 questions, 2–4 options each; answers come back as the tool result). Remove it, or answer it automatically, in unattended runs. See [5.2](weeks/week-05-control-safety-reliability.md#52-human-in-the-loop-approval-gates-interrupts-escalation).

**Claude Code subagent**  
An agent defined in Markdown (`.claude/agents/*.md`; frontmatter `name`, `description` used to decide when to delegate, a `tools` allow-list that inherits by default, `model`, a turn cap, a `memory` folder, worktree isolation, background mode). It runs in its own context window and returns a summary. Built-ins: Explore (Haiku, read-only), Plan (read-only) and general-purpose. Subagents cannot start subagents, and auto memory is not inherited. See [3.6](weeks/week-03-state-and-memory.md#36-sub-agents-and-context-isolation).

**CLAUDE.md**  
Claude Code's instruction file written by people: rules and conventions, scoped to the project (`./CLAUDE.md`, `.claude/CLAUDE.md`), the user (`~/.claude/CLAUDE.md`) or the organisation (managed policy path). Loaded every session; aim for under 200 lines (a file over 4 MiB is skipped). Files above the working directory load at launch; files in subfolders load when needed. `/init` creates one, `/memory` lists and opens them, `/context` shows what loaded. Claude also reads a repository's `AGENTS.md` directly. See [3.4](weeks/week-03-state-and-memory.md#34-persistent-memory-files-and-memory-as-documents).

**.claude/rules/**  
A folder of instruction files, one per topic. A `paths:` glob in the frontmatter makes a rule load only when Claude works on matching files (a path-scoped rule). Rules without `paths` load at launch like `.claude/CLAUDE.md`. `~/.claude/rules/` applies to every project, with lower priority than project rules. See [3.4](weeks/week-03-state-and-memory.md#34-persistent-memory-files-and-memory-as-documents).

**clear_thinking_20251015**  
The strategy for clearing thinking blocks: `keep: "all"` or `{"type":"thinking_turns","value":N}` (the last N assistant turns with thinking). It must be listed before `clear_tool_uses` when both are used. The default depends on the model (keep all on Opus 4.5+, Sonnet 4.6+, Fable/Mythos; last turn only on earlier models). Kept thinking preserves the cache; cleared thinking breaks it at the point of clearing. See [3.2](weeks/week-03-state-and-memory.md#32-context-management-summarisation-compaction-truncation).

**clear_tool_uses_20250919**  
The strategy for clearing tool results. When input goes over `trigger` (default `{"type":"input_tokens","value":100000}`; `tool_uses` also allowed), the oldest tool results are cleared, keeping the last `keep` pairs (default 3). Each cleared result is replaced with a placeholder so the model knows something was there. `clear_at_least` sets a minimum amount to free per pass (otherwise the pass is skipped, because breaking the cache must be worth it); `exclude_tools` names tools never cleared (the scratchpad tool belongs here); `clear_tool_inputs` (default false) also removes the call parameters. See [3.2](weeks/week-03-state-and-memory.md#32-context-management-summarisation-compaction-truncation).

**Clustered standard error**  
An SE computed with the task (not the trial) as the independent unit. Naive per-trial SEs understate the uncertainty. See [6.5](weeks/week-06-evaluation-1.md#65-regression-testing-a-harness-change-ab-on-prompts-and-tools).

**Code-based grader**  
A fixed, rule-based check: string match (exact / regex / fuzzy), pass/fail tests, static analysis, checking the outcome (query the end state), checking tool calls, transcript analysis (turns, tokens). Fast, cheap and repeatable, but brittle when there are valid variations. See [6.3](weeks/week-06-evaluation-1.md#63-graders-exact-match-rubric-llm-as-judge-outcome-checks).

**Code simulator**  
A stateful fake tool backend that computes answers from a fixture instead of replaying recorded ones, and can inject faults such as timeouts. Unlike a cassette, it can answer calls that were never recorded. See [7.3](weeks/week-07-evaluation-2-and-iteration.md#73-simulated-users-and-environments).

**compact_20260112**  
Anthropic's server-side compaction, beta `compact-2026-01-12` (Opus 4.6+, Sonnet 4.6+, Fable/Mythos 5+). When input goes over `trigger` (default 150,000 input tokens, minimum 50,000), the API runs a summary step and returns a `compaction` content block as the first block of the assistant message. The harness appends the response untouched, and the API drops every block before the compaction block on later requests. The same model writes the summary (no cheaper-model option). See [3.2](weeks/week-03-state-and-memory.md#32-context-management-summarisation-compaction-truncation).

**Compaction**  
The harness (or the API) swaps part of the transcript for a summary written by the model when the context gets close to its limit. Edd Mann's harness does this at 80% of the usable window; Anthropic offers it on the server side (`compact_20260112`). Covered fully in 3.2. See [1.2](weeks/week-01-what-an-agent-is.md#12-the-agent-loop).

**Compaction instructions**  
A string that *replaces* the default summariser prompt. Use it to say what must survive (ids, numbers cited as evidence, rejected hypotheses, next step) and to forbid tool use — with tools defined, the summariser sometimes calls one instead of writing (`content: null`). On Fable/Mythos 5.1 the summariser sees only the visible conversation, not earlier thinking. See [3.2](weeks/week-03-state-and-memory.md#32-context-management-summarisation-compaction-truncation).

**Compaction losses**  
Images, documents, `container_upload` blocks and fetched URLs inside the summarised stretch are removed. Earlier thinking is not carried forward (5.1 models). Anything a later turn still needs must be restated or uploaded again. See [3.2](weeks/week-03-state-and-memory.md#32-context-management-summarisation-compaction-truncation).

**Compounding error**  
If each turn succeeds with probability p, a task of n dependent turns naively succeeds about p^n of the time. Recovering by looking at results does better than that, but long tasks still fail sharply past a certain depth (HORIZON benchmark). This is the built-in cost of autonomy. See [1.6](weeks/week-01-what-an-agent-is.md#16-when-not-to-build-an-agent).

**Concurrent tool execution**  
The harness runs the several `tool_use` blocks of one assistant message at the same time (`asyncio.gather`). The API sets no order, so the harness runs read-only calls together and side-effect calls one at a time in message order. See [5.6](weeks/week-05-control-safety-reliability.md#56-latency-and-cost-budgets-parallel-tool-calls-streaming).

**Condensed summary (sub-agent return)**  
The 1,000–2,000-token digest a sub-agent hands back after "using tens of thousands of tokens or more". It is the only channel from child to parent, so the task text must set its format (verdict, deciding number, what was not checked). See [3.6](weeks/week-03-state-and-memory.md#36-sub-agents-and-context-isolation).

**Consolidation pass**  
A regular rewrite that keeps a memory core under its cap and free of duplicates and stale lines (Claude Code's index-rewrite reminder; Letta's sleep-time agent; this course's review-day pass). Without it, a memory file grows into a second transcript. See [3.4](weeks/week-03-state-and-memory.md#34-persistent-memory-files-and-memory-as-documents).

**Contamination**  
Benchmark tasks or solutions that are in the training data, so a model can remember rather than solve (gold patches reproduced word for word). See [6.6](weeks/week-06-evaluation-1.md#66-public-benchmarks-swe-bench-τ-bench-gaia-terminal-bench-and-their-limits).

**Context awareness**  
On Sonnet 4.5+ and Haiku 4.5, the API injects `<budget:token_budget>` and, after each tool call, `<system_warning>Token usage: N/M</system_warning>` tags so the model can track how much budget it has left. See [2.1](weeks/week-02-core-mechanics.md#21-context-window-as-working-memory).

**Context editing**  
API features for removing used-up context: clearing old tool results and clearing thinking blocks. Works alongside compaction. Settings are in 3.2. See [2.1](weeks/week-02-core-mechanics.md#21-context-window-as-working-memory).

**Context editing (API)**  
Server-side truncation by category: beta `context-management-2025-06-27`, `context_management.edits = [...]`. Applied to the prompt before the model sees it; the client keeps the full, unchanged history. The response's `context_management.applied_edits` reports what was cleared (`cleared_tool_uses`, `cleared_thinking_turns`, `cleared_input_tokens`). Available on all supported models. See [3.2](weeks/week-03-state-and-memory.md#32-context-management-summarisation-compaction-truncation).

**Context engineering**  
The wider job of deciding what goes into the model's context on each call: prompts, retrieved documents, tool results, summaries. HumanLayer treats harness engineering as part of it. Anthropic's definition: curating "the smallest possible set of high-signal tokens that maximize the likelihood of some desired outcome". Week 3 covers how it works. See [1.4](weeks/week-01-what-an-agent-is.md#14-what-a-harness-is).

**Context isolation**  
A sub-agent's tool results, dead ends and working-out never enter the parent's transcript. Anthropic: "the detailed search context remains isolated within sub-agents, while the lead agent focuses on synthesizing and analyzing the results". It is a context-management tool (alongside compaction and note-taking, 3.2/3.1) before it is a multi-agent pattern: it prevents bloat, where compaction repairs it. See [3.6](weeks/week-03-state-and-memory.md#36-sub-agents-and-context-isolation).

**Context rot**  
The finding (Chroma, Jul 2025; 18 models) that models do not use their context evenly. Accuracy on a fixed task drops as the input gets longer, even on trivial tasks. It is worse when the needed fact is far in meaning from the question and when similar-looking distractors are present. See [2.1](weeks/week-02-core-mechanics.md#21-context-window-as-working-memory).

**Context window**  
The total token budget of one model call, input and output together: system prompt, tool definitions, all messages (including tool results, images and documents), thinking blocks and the current output. 1M tokens on current Claude models, 200k on older ones. Not the same as `max_tokens`, which only caps the single response. See [2.1](weeks/week-02-core-mechanics.md#21-context-window-as-working-memory).

**"Context, not enforced configuration"**  
The docs' warning for both CLAUDE.md and auto memory: they change behaviour but do not block anything. An action that must never happen is blocked by a `PreToolUse` hook or `permissions.deny` (layer 5), never by a line in memory. See [3.4](weeks/week-03-state-and-memory.md#34-persistent-memory-files-and-memory-as-documents).

**Contextual retrieval**  
Anthropic's preparation step (Sep 2024): a model writes 50–100 tokens of context for each chunk ("situate this chunk within the overall document"), added to the chunk before embedding and BM25 indexing. 35% fewer retrieval failures alone, 49% with BM25, 67% with a reranker (top-20 failure rate 5.7% → 1.9%). See [3.3](weeks/week-03-state-and-memory.md#33-retrieval-for-agents-rag-vs-agentic-search).

**Cost / wall-clock budget**  
The same idea in dollars or seconds: Agent SDK `max_budget_usd` (covers subagents); mini-swe-agent `cost_limit` / `wall_time_limit_seconds` (raising `LimitsExceeded` / `TimeExceeded`, which the run loop turns into an exit message). See [2.5](weeks/week-02-core-mechanics.md#25-stopping-conditions-step-budgets-and-loop-detection).

**Cost per success**  
Total cost of all trials ÷ number of successful trials. The efficiency number that penalises cheap failures. See [6.4](weeks/week-06-evaluation-1.md#64-trajectory-level-metrics-passk-steps-cost-tool-call-accuracy).

**Credentials outside the box**  
Secrets never enter the environment where model-directed code runs. A proxy or the executor process adds scoped credentials after checking the operation (Claude Code on the web's git proxy). Goes with least-privilege service accounts (a read-only DB role) — 11.3. See [5.1](weeks/week-05-control-safety-reliability.md#51-permissions-and-sandboxing).

**Critique**  
The written reason attached to a pass/fail label. Detailed enough to serve as a few-shot example for a judge. See [6.3](weeks/week-06-evaluation-1.md#63-graders-exact-match-rubric-llm-as-judge-outcome-checks).


## D

**Deciding-number provenance check**  
A policy guardrail on the final output: any number a ticket cites as evidence must equal a value returned by one of this run's own tool calls (traceable by tool_use_id), never a figure taken from a document. This catches a well-typed lie that gets through the quarantine schema. See [5.4](weeks/week-05-control-safety-reliability.md#54-prompt-injection-and-untrusted-content).

**Decisive error step**  
The earliest step in a failed run where a correction would have turned the failure into a success (Who&When). It is rarely the last bad step, because errors compound. See [7.1](weeks/week-07-evaluation-2-and-iteration.md#71-reading-a-transcript).

**Degrees of freedom (skills)**  
Anthropic's writing rule for how strict a skill should be. Low freedom (exact steps, scripts) for fragile operations where order matters — a "narrow bridge with cliffs on both sides". High freedom (general direction) where many approaches work — an "open field". See [4.5](weeks/week-04-prompt-and-tool-design.md#45-skills-procedural-knowledge-loaded-on-demand).

**Delayed ground truth**  
Labels that arrive after a live run, such as a reviewer's approve/edit/reject (hours later) or a confirmed field outcome (days later), joined back to the run by its id. It is the only online layer that measures accuracy itself. See [7.4](weeks/week-07-evaluation-2-and-iteration.md#74-online-evaluation-and-monitoring).

**Delegation task text (the contract)**  
The written brief the parent gives the child: the goal, the site/window/baseline the parent already chose, the exact fields to return, tool guidance, limits, a cap on tool calls and a cap on words. Passing the parent's decisions down as constraints is what stops the child remaking them (the Cognition failure). A vague task ("check the weather") makes children duplicate work, leave gaps and return prose no one can check. See [3.6](weeks/week-03-state-and-memory.md#36-sub-agents-and-context-isolation).

**Delegation tool**  
The tool on the parent's side (`delegate(name, task)`, Claude Code's Agent/Task tool) whose executor is another harness: fresh `messages`, a bounded loop, limited tools, final text returned. A layer-2 tool built from its own layers 1–5. See [3.6](weeks/week-03-state-and-memory.md#36-sub-agents-and-context-isolation).

**Delivery path**  
How a search result reaches the model: inline in the transcript (shaped, 2.1) or written to a file the agent must open (restorable offload, 3.2). Sen et al. show it changes accuracy as much as the choice of searcher. A search tool that returns full text inline "to save a turn" gets the worst of both. See [3.3](weeks/week-03-state-and-memory.md#33-retrieval-for-agents-rag-vs-agentic-search).

**Detector (failure category)**  
A code check or calibrated judge that finds more cases of one failure category in traces automatically. Every category in your own taxonomy should have one. See [7.2](weeks/week-07-evaluation-2-and-iteration.md#72-error-taxonomies-and-common-failure-modes).

**disable_parallel_tool_use**  
A `tool_choice` flag. With `auto`, the model makes at most one tool call per response; with `any`/`tool`, exactly one (that combination is not supported on Opus 5.5, Sonnet 5.5, Fable 5.1, Mythos 5.1). See [5.6](weeks/week-05-control-safety-reliability.md#56-latency-and-cost-budgets-parallel-tool-calls-streaming).

**Distractor**  
Content in the context that looks like the needed fact but is wrong or irrelevant (for example, 143 near-identical weather rows around the one that matters). The main thing that makes context rot worse in agent transcripts. See [2.1](weeks/week-02-core-mechanics.md#21-context-window-as-working-memory).

**Done set (done: set[tool_use_id])**  
The "already done?" guard for tools with side effects. If a `tool_use_id` is already in the set, the executor returns the stored result, so replay after a crash cannot fire `draft_ticket` twice, wherever the save happens. It is keyed on the id (stable, from the model response, already in the checkpoint), never on tool name plus arguments (that would skip a legitimate repeat call). See [3.5](weeks/week-03-state-and-memory.md#35-checkpointing-and-resumability).

**Draft-then-file**  
The shape for a gated side effect in an unattended run: the agent's tool only writes a draft (always allowed), and filing is a separate step a person does. This takes the live "ask" out of the run completely. See [5.2](weeks/week-05-control-safety-reliability.md#52-human-in-the-loop-approval-gates-interrupts-escalation).

**Dual control**  
In τ²-bench's telecom domain, the simulated user also has tools that act on the shared state, so both agent and user can change the environment. See [Week 6 review](weeks/week-06-evaluation-1.md#week-6-review).

**Durability mode (LangGraph)**  
The safety-versus-speed setting on `invoke`. `"exit"` saves only when the graph finishes (nothing to resume mid-run); `"async"` saves in the background (fast, but the last step can be lost); `"sync"` waits for the write before each step (needed when a missed checkpoint would repeat a real-world side effect). The one tool with side effects decides which mode you need. See [3.5](weeks/week-03-state-and-memory.md#35-checkpointing-and-resumability).

**Durable execution**  
The stronger promise that a workflow will finish despite crashes: a runtime saves state automatically, notices failure, restarts, and resumes by replaying. Diagrid's contrast: checkpointing says "I saved your state; you take it from here", durable execution says "your agent workflows will run to completion". A checkpointer alone gives you no supervisor, watchdog or duplicate removal. See [3.5](weeks/week-03-state-and-memory.md#35-checkpointing-and-resumability).


## E

**Edit guardrail (linter)**  
SWE-agent runs flake8 on every edit and rejects edits that add syntax errors, showing the error and the unchanged file. Removing it cost 3 points (18.0% → 15.0%). This is how the line-range editor handles the failure that Anthropic's exact-string editor (1.5) removes in a different way. See [4.4](weeks/week-04-prompt-and-tool-design.md#44-agent-computer-interface-aci).

**edit_file (exact-match replace)**  
The standard edit tool for coding agents: `old_str` must match exactly once and `new_str` replaces it; an empty `old_str` creates the file. Refusing ambiguous matches is its main protection against silently losing code. See [1.5](weeks/week-01-what-an-agent-is.md#15-anatomy-of-a-real-agent).

**effort**  
`output_config.effort`, one of low / medium / high (default) / xhigh / max. It is soft guidance on how willing the model is to think and how deeply; at low, easy turns may get no thinking block. It is written into the prompt, so changing it breaks the cache prefix (4.6). See [2.2](weeks/week-02-core-mechanics.md#22-react-and-reasoning-then-acting-extended-thinking-in-the-loop).

**Effort scaling (sub-agents)**  
Anthropic's rule of thumb for how many to start: simple fact-finding, 1 agent and 3–10 tool calls; direct comparisons, 2–4 sub-agents with 10–15 calls each; complex research, more than 10. An early failure was fifty sub-agents for a simple query. See [3.6](weeks/week-03-state-and-memory.md#36-sub-agents-and-context-isolation).

**Empty-output confirmation**  
Replying "Your command ran successfully and did not produce any output." instead of an empty observation. Silence is ambiguous to a model (findings vs errors, 4.3). See [4.4](weeks/week-04-prompt-and-tool-design.md#44-agent-computer-interface-aci).

**Environment isolation**  
Every trial starts from a fresh copy of all state the agent can read or write (database, files, memory, checkpoints). Breaking this either inflates scores (leaked state) or links failures together (shared infrastructure faults). See [6.1](weeks/week-06-evaluation-1.md#61-why-agent-evals-differ-from-llm-evals).

**Error catalogue**  
One row per tool per failure mode, with the exact text returned. A reviewable artefact, like a prompt, and the layer-6 unit for errors-per-tool metrics. It should shrink over time: a recurring error is a description or parameter bug (4.2) or a schema gap (2.4) to close, not a message to polish. See [4.3](weeks/week-04-prompt-and-tool-design.md#43-tool-error-messages-as-instructions-designing-for-recovery).

**Error discovery**  
Reading production traces (at least 100, the first ~30 annotated by hand) and writing down each distinct way the system fails. This is the source list for new tasks. See [6.2](weeks/week-06-evaluation-1.md#62-building-an-eval-set-from-real-failures-the-taskgraderenvironment-triad).

**Error result as prompt**  
An `is_error` tool result is prompt text. It lands where a successful result would, is re-read on every later turn, and is the model's only clue to why the action failed. The design question: what must the model read to choose a *different* action in one turn? See [4.3](weeks/week-04-prompt-and-tool-design.md#43-tool-error-messages-as-instructions-designing-for-recovery).

**Error taxonomy**  
A counted list of named failure categories, built by open-coding failing traces and then grouping the codes. Count one root category per trace and rank by count × severity; it tells you what to fix first. See [7.2](weeks/week-07-evaluation-2-and-iteration.md#72-error-taxonomies-and-common-failure-modes).

**Error-exhausted run**  
When retries run out, the loop returns status `error` with the exception type and `request_id`, not a traceback. Partial findings and cost are kept, as for any other end state. See [2.6](weeks/week-02-core-mechanics.md#26-error-handling-retries-backoff-and-feeding-tool-errors-back-to-the-model).

**Escalation**  
The agent hands a decision to a person (stuck, out of budget, conflicting evidence, low confidence) through a tool such as `escalate(question, options)` rather than free text. See [5.2](weeks/week-05-control-safety-reliability.md#52-human-in-the-loop-approval-gates-interrupts-escalation).

**Eval saturation**  
A suite at about 100% gives a regression signal but no signal about improvement. See [6.2](weeks/week-06-evaluation-1.md#62-building-an-eval-set-from-real-failures-the-taskgraderenvironment-triad).

**Evaluation harness**  
The setup that runs trials (in parallel), gives the agent its tools and environment, records transcripts, grades and adds up results. Separate from the agent harness it drives. See [6.1](weeks/week-06-evaluation-1.md#61-why-agent-evals-differ-from-llm-evals).

**Evaluation suite**  
A collection of tasks that measure related abilities or behaviours. See [6.1](weeks/week-06-evaluation-1.md#61-why-agent-evals-differ-from-llm-evals).

**Exact replay**  
Running the harness again with the model and tools stubbed from the trajectory log. Repeatable and free; it tests harness code (guardrails, parsers, status logic). See [5.5](weeks/week-05-control-safety-reliability.md#55-observability-tracing-logging-trajectories-replaying-runs).

**Explicit completion signal / submission string**  
A `submit(result)` tool or a magic string (mini-swe-agent's `COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT`) that the harness treats as "done". Then an `end_turn` without it counts as a stall and gets the reply "not submitted — call submit or continue". From the other side, the Agent SDK `Stop` hook checks a result before accepting the stop. See [2.5](weeks/week-02-core-mechanics.md#25-stopping-conditions-step-budgets-and-loop-detection).

**Exponential backoff**  
Wait `base * 2**attempt` between retries. Used alone, it lines up competing clients so their retries spike together. See [2.6](weeks/week-02-core-mechanics.md#26-error-handling-retries-backoff-and-feeding-tool-errors-back-to-the-model).


## F

**Feature list**  
Anthropic's artefact for long-running agents. An initializer agent expands the requirements into a JSON list of features, all marked "failing" at first. Each later session picks one, builds it, checks it, marks it, and leaves things clean. Upfront breakdown that spans sessions. See [2.3](weeks/week-02-core-mechanics.md#23-planning-and-task-decomposition).

**Filter vs wall**  
A rule on command text (deny `curl`) is a filter the model can get around (`python -c "urllib…"`, a script that opens files itself). A sandbox or a missing credential is a wall that holds whatever the model decides, including under prompt injection. See [5.1](weeks/week-05-control-safety-reliability.md#51-permissions-and-sandboxing).

**Findings vs errors**  
Results that are answers, not failures: "no incidents match", "station 4 returned no data". Sent back as errors, they teach the model to retry a correct answer; sent back as empty lists, they teach it nothing was wrong (the Day 7 null-weather case). The executor sorts each outcome per tool: error (model must act differently), finding (model should reason about it), or invisible (retried inside the tool, 2.6). See [4.3](weeks/week-04-prompt-and-tool-design.md#43-tool-error-messages-as-instructions-designing-for-recovery).

**Fine-grained tool streaming (eager_input_streaming)**  
A per-tool flag that streams a tool's input as `input_json_delta` pieces without server-side buffering or JSON checks. Lower latency for large parameters, but the input may be partial or invalid JSON (return it as an `is_error` result wrapping `{"INVALID_JSON": …}`). Replaces the deprecated `fine-grained-tool-streaming-2025-05-14` beta header. See [5.6](weeks/week-05-control-safety-reliability.md#56-latency-and-cost-budgets-parallel-tool-calls-streaming).

**Five-question test**  
Five questions to answer before writing any prompt or tool: Can I draw the full graph? Is the "reasoning" really just rules? What is the worst silent wrong action? Can I eval it? Can one agent do it? See [1.6](weeks/week-01-what-an-agent-is.md#16-when-not-to-build-an-agent).

**Fixture**  
The frozen environment for a task (database snapshot, recorded tool responses / cassette, seeded memory). Built cheaply from the failing run's trajectory log, never from live vendor calls. See [6.2](weeks/week-06-evaluation-1.md#62-building-an-eval-set-from-real-failures-the-taskgraderenvironment-triad).

**Fork replay**  
Load the transcript up to turn k, change one thing (a prompt section, a tool description, a tool result), and let the live model carry on, with tools answered from a recorded cassette keyed by (name, sorted input). It tests whether a harness change fixes the behaviour. See [5.5](weeks/week-05-control-safety-reliability.md#55-observability-tracing-logging-trajectories-replaying-runs).

**Four recoverable-error shapes**  
*Bad argument*: the rule broken plus the corrected value when it can be computed ("date '03/09/2026' does not match YYYY-MM-DD; did you mean 2026-09-03?"). *Wrong state / wrong order*: the precondition and the tool that sets it up ("cannot terminate a running instance; call `stop_instance` first"). *Too-expensive request*: refuse or cut down, and name the cheaper way ("use `agg=daily`, or hourly for one station and ≤3 days"). *Unavailable*: what was obtained, what is pending, the options. All four are the 1.3 triad — problem, fix, data — in different amounts. See [4.3](weeks/week-04-prompt-and-tool-design.md#43-tool-error-messages-as-instructions-designing-for-recovery).

**Four-part description**  
The docs' minimum of 3–4 sentences, written for a new colleague rather than copied from the API docs: what the tool does; when to use it, and when to use the sibling tool instead; what each parameter means; what it returns, in what shape and size, and its limits (including what "no data" looks like). "Gets the stock price for a ticker" is the classic poor example. See [4.2](weeks/week-04-prompt-and-tool-design.md#42-tool-design-naming-descriptions-parameters).

**Full jitter**  
`sleep = random(0, min(cap, base * 2**attempt))` (AWS). Random backoff that spreads retries out into a nearly steady call rate. In AWS's simulation with 100 competing clients it cut total calls by more than half compared with plain exponential backoff. See [2.6](weeks/week-02-core-mechanics.md#26-error-handling-retries-backoff-and-feeding-tool-errors-back-to-the-model).


## G

**GAIA**  
General-assistant questions (browsing, files, several steps) graded by exact match on a short answer. See [6.6](weeks/week-06-evaluation-1.md#66-public-benchmarks-swe-bench-τ-bench-gaia-terminal-bench-and-their-limits).

**Garbage collection (harness)**  
A background job that scans for drift and proposes small fixes. In OpenAI's Codex team, background tasks open small refactor PRs; in the investigator's weekly version, it scans memory and skills (stale lines, duplicates, failing scripts, renamed tools) and makes only mechanical fixes without a person. See [7.6](weeks/week-07-evaluation-2-and-iteration.md#76-case-study-how-labs-iterate-on-coding-agent-harnesses).

**Grader**  
Logic that scores one aspect of a trial. A task may have several (outcome check, path constraint, rubric). See [6.1](weeks/week-06-evaluation-1.md#61-why-agent-evals-differ-from-llm-evals).

**Grammar scope**  
On Claude the grammar applies only to the model's direct output, "not to tool use calls, tool results, or thinking tags". Grammar state resets between sections, so the model can think freely and then write constrained JSON. See [2.4](weeks/week-02-core-mechanics.md#24-structured-outputs-and-schemas).

**Grammar-constrained sampling (constrained decoding)**  
How the guarantee works: the schema is turned into a grammar, and at each step tokens that could not continue a valid document are blocked. The model cannot produce output that does not fit. Compiled grammars are cached for about 24 h; the first request with a new schema pays extra latency to compile it. See [2.4](weeks/week-02-core-mechanics.md#24-structured-outputs-and-schemas).

**Guard metrics**  
Cost per success, p90 turns, status mix: these must not get worse beyond a margin, even when the pass rate goes up. See [6.5](weeks/week-06-evaluation-1.md#65-regression-testing-a-harness-change-ab-on-prompts-and-tools).

**Guardrail**  
A harness check on content at a boundary (input, tool input, tool output, final output). Permissions control actions; guardrails control content. See [5.3](weeks/week-05-control-safety-reliability.md#53-guardrails-inputoutput-validation-policy-checks-classifiers).

**Guardrail responses**  
Block, reject with a message, repair (redact or clip), or escalate. A classifier on its own should flag or escalate, not block. See [5.3](weeks/week-05-control-safety-reliability.md#53-guardrails-inputoutput-validation-policy-checks-classifiers).


## H

**Harmlessness screen**  
A light model that checks user input before the main model sees it (Anthropic docs). See [5.3](weeks/week-05-control-safety-reliability.md#53-guardrails-inputoutput-validation-policy-checks-classifiers).

**Harness**  
Everything around the model: prompts and injected context, tools and the executor, loop control, state, guardrails and permissions, feedback and evals. HumanLayer: "The agent's runtime, or its peripherals: what does the model use to interact with its environment?" See [1.4](weeks/week-01-what-an-agent-is.md#14-what-a-harness-is).

**Harness A/B test**  
Running the baseline and the candidate harness on the same frozen suite, with one change between them, and comparing task by task. See [6.5](weeks/week-06-evaluation-1.md#65-regression-testing-a-harness-change-ab-on-prompts-and-tools).

**Harness engineering**  
Improving an agent by changing the harness, not the model. When the agent makes a mistake, build a fix "such that the agent never makes that mistake again" (Hashimoto). OpenAI and others treat it as the next step after "prompt engineering". See [1.4](weeks/week-01-what-an-agent-is.md#14-what-a-harness-is).

**Harness version hash**  
A hash of the system prompt + tool definitions (+ skill listing) recorded on every run, so metrics and failures can be split by harness version. See [5.5](weeks/week-05-control-safety-reliability.md#55-observability-tracing-logging-trajectories-replaying-runs).

**Held-out split**  
Eval tasks kept aside while you tune a fix, used only to check it. A fix that wins on dev but drops on held-out is overfit to the examples that inspired it. See [7.5](weeks/week-07-evaluation-2-and-iteration.md#75-the-improvement-loop).

**Hot-path vs background memory writes**  
Writing memory during the run (available at once; each write costs a tool turn and latency) versus in a separate pass afterwards (no latency during the run; you must decide when it fires; the run cannot use what it learned). This course's daily task is a background writer. See [3.1](weeks/week-03-state-and-memory.md#31-short-term-vs-long-term-memory-scratchpads-conversation-state).

**Human grader**  
Expert review, spot-check sampling, crowdsourced or A/B judgement. The gold standard, but slow and costly; mainly used to make the labels that judges are calibrated on. See [6.3](weeks/week-06-evaluation-1.md#63-graders-exact-match-rubric-llm-as-judge-outcome-checks).

**Human-in-the-loop (HITL)**  
Any point where a run waits for a person. Three shapes: approval gate, clarification, interrupt or escalation. Mechanically it is always a lasting pause with a pending tool call plus a way to resume. See [5.2](weeks/week-05-control-safety-reliability.md#52-human-in-the-loop-approval-gates-interrupts-escalation).

**Hybrid architecture**  
A fixed outer workflow with one agentic step inside. Plain code computes and routes, an agent handles the open-ended part, and a human or a gate sits before any side effect. When an agent is needed at all, this is usually the right shape. See [1.1](weeks/week-01-what-an-agent-is.md#11-llm-call-vs-workflow-vs-agent).

**Hybrid search (BM25 + embeddings)**  
Combining exact-word search and meaning-based search, usually merging the rankings and then reranking. Each catches what the other misses (synonyms versus identifiers and error codes). See [3.3](weeks/week-03-state-and-memory.md#33-retrieval-for-agents-rag-vs-agentic-search).


## I

**Idempotent retry**  
Retrying a failed model call is safe because the failed call had no side effects. Retrying a tool that timed out is safe only if the tool is read-only or idempotent (safe to run twice) — and the error text should say which. See [2.6](weeks/week-02-core-mechanics.md#26-error-handling-retries-backoff-and-feeding-tool-errors-back-to-the-model).

**Idempotent step**  
A step that is safe to run twice. Anything after a checkpoint must be like this, because replay runs nodes again, LLM calls and API requests included. You get it by wrapping side effects in a task whose result is saved (LangGraph `@task`), by "already done?" guards keyed on a stable id (for example `tool_use_id`), and by avoiding reads that change each time (`now()`) inside a step. See [3.5](weeks/week-03-state-and-memory.md#35-checkpointing-and-resumability).

**Improvement ledger**  
The record of each iteration: hypothesis, change, harness hash, result and decision. Rejected hypotheses are kept too. See [7.5](weeks/week-07-evaluation-2-and-iteration.md#75-the-improvement-loop).

**Improvement loop**  
Eval → hypothesis → harness change → re-eval → ship: pick the top category by count × severity, write a falsifiable hypothesis, make one change as low in the harness as it will go, and re-check with fork replay, the paired suite and a held-out split. See [7.5](weeks/week-07-evaluation-2-and-iteration.md#75-the-improvement-loop).

**Incremental planning**  
No separate plan; each turn's thinking block (2.2) picks the next step. Cheapest and most flexible, but short-sighted: nothing forces a rethink when early results should change the whole approach. See [2.3](weeks/week-02-core-mechanics.md#23-planning-and-task-decomposition).

**Infrastructure error**  
A failure on the way to the model (HTTP 429/500/504/529, a dropped connection, a client timeout). The model never sees it, the transcript does not change, and the harness retries the call. Layer 3. The same split applies inside a tool that calls an outside API: the tool's own client retries quietly, and only when that runs out does it become a task error. See [2.6](weeks/week-02-core-mechanics.md#26-error-handling-retries-backoff-and-feeding-tool-errors-back-to-the-model).

**Infrastructure noise**  
Score changes caused by container resources, timeouts and tool versions rather than the agent (6 points on Terminal-Bench 2.0). See [6.5](weeks/week-06-evaluation-1.md#65-regression-testing-a-harness-change-ab-on-prompts-and-tools).

**Injection-resistant design patterns**  
Action-selector, plan-then-execute, LLM map-reduce, dual LLM, code-then-execute (CaMeL), and context minimisation (Beurer-Kellner et al., Jun 2025). Limits on control flow that make it impossible for untrusted input the agent reads to trigger actions that matter. See [5.4](weeks/week-05-control-safety-reliability.md#54-prompt-injection-and-untrusted-content).

**Instructive error message**  
The docs' rule for `is_error` content: say what went wrong and what to try next ("Rate limit exceeded. Retry after 60 seconds." not "Error"). The tools guide adds "specific and actionable improvements, rather than opaque error codes or tracebacks", and pointing toward cheaper strategies (filters, pagination) or a correctly formatted input. The rule is aimed at *opaque* codes and 40-line dumps, not at stderr as such — the last three lines of a traceback (file, line, caret) are exactly the data needed for the fix. Design details in 4.3. See [2.6](weeks/week-02-core-mechanics.md#26-error-handling-retries-backoff-and-feeding-tool-errors-back-to-the-model).

**Interleaved thinking**  
The model thinks between tool calls within one assistant turn, "reflecting on each tool result before deciding what to do next". It is automatic with adaptive thinking; on Claude 4.x, manual mode needed the `interleaved-thinking-2025-05-14` beta header. See [2.2](weeks/week-02-core-mechanics.md#22-react-and-reasoning-then-acting-extended-thinking-in-the-loop).

**Interrupt (LangGraph)**  
`interrupt(payload)` inside a node saves state through the checkpointer and shows the payload. It is resumed with `Command(resume=value)` on the same `thread_id`. The node runs again from its start, so earlier side effects must be idempotent. Never wrap it in try/except. See [5.2](weeks/week-05-control-safety-reliability.md#52-human-in-the-loop-approval-gates-interrupts-escalation).

**Interruptions / RunState (OpenAI Agents SDK)**  
Tools with `needs_approval` (true/false or a per-call function) end the run with `result.interruptions`. Then `state = result.to_state()`, `state.approve()/reject(rejection_message=…)`, and `Runner.run(agent, state)`. `always_approve/always_reject` make the decision stick for the run; `state.to_json()` handles long waits. See [5.2](weeks/week-05-control-safety-reliability.md#52-human-in-the-loop-approval-gates-interrupts-escalation).


## J

**JSON mode**  
OpenAI's older `response_format: {"type": "json_object"}`. It only guarantees valid JSON syntax, not any particular keys or types. See [2.4](weeks/week-02-core-mechanics.md#24-structured-outputs-and-schemas).

**JSON outputs**  
Claude's name for constraining the model's final text with `output_config.format`. Python SDK helper: `client.messages.parse(output_format=PydanticModel)` → `response.parsed_output` (None on refusal or `max_tokens`). See [2.4](weeks/week-02-core-mechanics.md#24-structured-outputs-and-schemas).

**Judge biases**  
Position bias (the order in a pairwise comparison changes the verdict), verbosity bias (longer wins), self-enhancement bias (favours its own model family) (MT-Bench). See [6.3](weeks/week-06-evaluation-1.md#63-graders-exact-match-rubric-llm-as-judge-outcome-checks).

**Judge TPR / TNR**  
The share of human-labelled passes the judge also passes (TPR) and of human-labelled fails the judge also fails (TNR). Reported separately because plain agreement hides a judge that always says pass when failures are rare. See [6.3](weeks/week-06-evaluation-1.md#63-graders-exact-match-rubric-llm-as-judge-outcome-checks).

**Just-in-time retrieval**  
Give the model light pointers (file paths, site codes, saved queries, links) and let it load the data when it needs it, instead of loading everything into context up front. The basis of agentic search (3.3). See [2.1](weeks/week-02-core-mechanics.md#21-context-window-as-working-memory).


## K

**Keep the wrong stuff in**  
Manus's warning against cleaning up transcripts: "leave failed actions in the context" because "without evidence, the model can't adapt". Compaction instructions should keep errors and rejected hypotheses, not only successes. See [3.2](weeks/week-03-state-and-memory.md#32-context-management-summarisation-compaction-truncation).


## L

**Leak rate**  
How often a simulated user or reviewer gives away a hidden fact before the agent has asked about it. A high leak rate means the simulator is doing part of the agent's work. See [7.3](weeks/week-07-evaluation-2-and-iteration.md#73-simulated-users-and-environments).

**Lethal trifecta**  
Private data + untrusted content + a way to communicate outward, all in one agent = a path for stealing data (Willison, Jun 2025). See [5.4](weeks/week-05-control-safety-reliability.md#54-prompt-injection-and-untrusted-content).

**Lexical vs semantic search**  
grep and BM25 match words: exact, no index or model needed, precise on identifiers, depend on the right vocabulary, and scan linearly (over 4 s across a million files). Dense embeddings match meaning: roughly constant query time using ANN indexes, need parsing for PDF and Office files, and are less precise on exact strings. See [3.3](weeks/week-03-state-and-memory.md#33-retrieval-for-agents-rag-vs-agentic-search).

**Linear history**  
An agent design where each step only adds to the message list and never rewrites it. It is the simplest to debug, replay and fine-tune on (mini-swe-agent). Compare compaction (3.2). See [1.5](weeks/week-01-what-an-agent-is.md#15-anatomy-of-a-real-agent).

**LLM call**  
One prompt in, one completion out, with no side effects. The code that makes the call owns all the control flow. See [1.1](weeks/week-01-what-an-agent-is.md#11-llm-call-vs-workflow-vs-agent).

**LLMCompiler**  
A variant that writes the plan as a task graph (DAG) and runs independent steps in parallel as soon as what they depend on is done (the paper claims a 3.6× speed-up). See [2.3](weeks/week-02-core-mechanics.md#23-planning-and-task-decomposition).

**LLM-simulated user**  
A language model that plays the user or reviewer in an eval, from a persona prompt with hidden facts and a goal, until a stop token or a turn cap. Useful for comparing harnesses, but biased, so not for absolute rates. See [7.3](weeks/week-07-evaluation-2-and-iteration.md#73-simulated-users-and-environments).

**LM-emulated tools (ToolEmu)**  
A language model that plays a tool's API from its spec. ToolEmu emulated 311 tools in 36 toolkits. Never use it to produce a deciding number. See [7.3](weeks/week-07-evaluation-2-and-iteration.md#73-simulated-users-and-environments).

**Long-term memory**  
"user-specific or application-level data across sessions", shared across threads. A store the harness owns, looked up by namespace and key rather than thread id. The model reaches it only through tools or harness injection. See [3.1](weeks/week-03-state-and-memory.md#31-short-term-vs-long-term-memory-scratchpads-conversation-state).


## M

**Macro average**  
Work out a metric for each task, then average across tasks, so tasks with more trials do not dominate. See [6.4](weeks/week-06-evaluation-1.md#64-trajectory-level-metrics-passk-steps-cost-tool-call-accuracy).

**MAST (Multi-Agent System Failure Taxonomy)**  
Cemri et al.'s taxonomy from 200+ traces across 7 multi-agent frameworks: 14 failure modes in 3 groups (specification issues 41.8%, inter-agent misalignment 36.9%, task verification 21.3%). Useful as a checklist, but its labels describe the agent, not where the harness fix lives. See [7.2](weeks/week-07-evaluation-2-and-iteration.md#72-error-taxonomies-and-common-failure-modes).

**max_retries**  
An SDK client setting. The official SDKs retry short-lived failures twice by default with a short exponential backoff (Python: connection errors, 408, 409, 429, ≥500). Set it on the client or per request with `with_options`. See [2.6](weeks/week-02-core-mechanics.md#26-error-handling-retries-backoff-and-feeding-tool-errors-back-to-the-model).

**Memory as documents**  
Long-term memory (3.1) kept as plain text files that the model reads and edits with normal file tools. People can audit them (diff and edit), they are addressed by path (a small index in context, bodies on demand), and they are injected at session start rather than searched. Claude Code's CLAUDE.md and auto memory, the Claude memory tool, Letta's memory blocks and this course's five docs are all examples. See [3.4](weeks/week-03-state-and-memory.md#34-persistent-memory-files-and-memory-as-documents).

**Memory block (Letta / MemGPT)**  
A labelled string with a character limit (originally `persona` and `human`), put into the prompt on every call and edited by the agent itself through tools (`core_memory_replace`, a `rethink_memory` that rewrites a block). Blocks are saved in a database, can be shared between agents, and a background "sleep-time" agent can tidy the main agent's blocks. Letta's case for blocks over RAG: models are sensitive to what is in context, so memory should be curated, not retrieved. See [3.4](weeks/week-03-state-and-memory.md#34-persistent-memory-files-and-memory-as-documents).

**Memory container**  
Course shorthand for the four places state is held, each with its own lifetime, owner and injection rule: transcript (one run), scratchpad (one task), long-term store (across runs), procedural memory (edited by humans). Most "memory failures" are facts kept in the wrong container. See [3.1](weeks/week-03-state-and-memory.md#31-short-term-vs-long-term-memory-scratchpads-conversation-state).

**Memory injection (via own memory)**  
A wrong or planted line in a memory file that the model obeys because the file is injected as trusted context (Day 19's "skip weather checks"). Nothing in the transcript shows whether a line was written by the model, a person or a bug. Defences are in layer 5: refuse procedural or command-like writes outside files people own, and present memory on read as evidence about the past, not as instructions (5.4). See [3.4](weeks/week-03-state-and-memory.md#34-persistent-memory-files-and-memory-as-documents).

**Memory tool**  
Claude API tool `type: "memory_20250818"` (Claude 4+): six file commands (`view`, `create`, `str_replace`, `insert`, `delete`, `rename`) over a virtual `/memories` folder. It runs client-side: the model asks for file operations, and the harness runs them and maps `/memories` to real storage. The handler must check every path to block path traversal. Turning it on injects a memory protocol (view memory first, record progress, "ASSUME INTERRUPTION"). See [3.1](weeks/week-03-state-and-memory.md#31-short-term-vs-long-term-memory-scratchpads-conversation-state).

**Memory types (user / feedback / project / reference)**  
The `type` frontmatter field on Claude Code auto-memory files: the user's role and preferences; corrections and approaches that were confirmed; ongoing work, deadlines and decisions you cannot work out from the code or git history; where to find things outside the project (issue tracker, dashboard). The write rule: skip anything you can get from the codebase and anything CLAUDE.md already says. `feedback` is really procedural memory — the type to put behind review. See [3.4](weeks/week-03-state-and-memory.md#34-persistent-memory-files-and-memory-as-documents).

**MEMORY.md read limit**  
Only the first 200 lines or 25 KB of the index load at session start. Near the limit, Claude Code reminds Claude to shorten it (one line per entry, details into topic files, merge or drop stale entries). Over the limit, the write succeeds but returns an error telling Claude to rewrite the index, because everything past the limit is dropped on the next load. The standard example of an always-loaded core with a hard cap. See [3.4](weeks/week-03-state-and-memory.md#34-persistent-memory-files-and-memory-as-documents).

**Message Batches API**  
Asynchronous bulk requests at 50% of the standard price. Most finish within an hour, all within 24 h (or they expire); up to 100,000 requests / 256 MB; caching is best-effort (30–98% hits); results kept 29 days. Suits single-call stages, not multi-turn loops. See [5.6](weeks/week-05-control-safety-reliability.md#56-latency-and-cost-budgets-parallel-tool-calls-streaming).

**Minimal coding agent**  
A loop plus three or four file and shell tools (`read_file`, `list_files`, `edit_file`, `bash`). It fits in about 40–200 lines and is the skeleton inside every production coding agent. See [1.5](weeks/week-01-what-an-agent-is.md#15-anatomy-of-a-real-agent).

**Minimal-prompt rule**  
Start with a minimal prompt on the best model, then add instructions and examples only for failures you have actually seen (the Day 4 discipline applied to text). Two deletion tests: move any line the executor could enforce into the executor, and cut any line whose removal changes no decision across ten transcripts. See [4.1](weeks/week-04-prompt-and-tool-design.md#41-system-prompt-architecture-for-agents).

**Minimum detectable effect (MDE)**  
The smallest true difference the suite can reliably detect: about 2.8 × SE_diff at 80% power, α = 0.05 two-sided. See [6.5](weeks/week-06-evaluation-1.md#65-regression-testing-a-harness-change-ab-on-prompts-and-tools).

**Model-based grader (LLM-as-judge)**  
A model that scores output against a rubric, a plain-language assertion, a reference, or another output (pairwise), alone or as several judges agreeing. It handles open-ended output, is not deterministic, and must be calibrated against people. See [6.3](weeks/week-06-evaluation-1.md#63-graders-exact-match-rubric-llm-as-judge-outcome-checks).

**Model-invoked vs user-invoked skill**  
Claude Code frontmatter sets who can start a skill; by default both can. `disable-model-invocation: true` removes the description from context so only a person can run it (use for side effects: deploy, send, commit). `user-invocable: false` hides it from the `/` menu, for background knowledge. `context: fork` runs the skill as a sub-agent (3.6); `allowed-tools` pre-approves tools while it is active. See [4.5](weeks/week-04-prompt-and-tool-design.md#45-skills-procedural-knowledge-loaded-on-demand).

**model_context_window_exceeded**  
The stop_reason returned (Claude 4.5+) when input plus `max_tokens` would overflow the window. If the input alone is bigger than the window, the call fails at once with a 400 error. See [2.1](weeks/week-02-core-mechanics.md#21-context-window-as-working-memory).

**Model-limit vs world-limit**  
Why a harness component exists. A model-limit (for example, attention degrading on long dumps) may go away with a better model; a world-limit (vendor outages, forged documents) holds whatever the model. See [7.6](weeks/week-07-evaluation-2-and-iteration.md#76-case-study-how-labs-iterate-on-coding-agent-harnesses).

**modified timestamp**  
An ISO 8601 field Claude Code writes into a memory file's frontmatter on every write (v2.1.214+), so both the user and Claude can see how fresh a fact is. The cheapest defence against stale memory. It shows age, not where a line came from, so it does not defend against a planted line. See [3.4](weeks/week-03-state-and-memory.md#34-persistent-memory-files-and-memory-as-documents).

**Multi-hop retrieval**  
Answering needs a second query whose words come from the first result. One-shot RAG cannot do it; an agent with a search tool can. See [3.3](weeks/week-03-state-and-memory.md#33-retrieval-for-agents-rag-vs-agentic-search).


## N

**Non-monotonic information**  
The ACI ablation finding that more observation is not always better: a 30-line window scored 14.3%, 100 lines 18.0%, the whole file 12.7% on SWE-bench Lite. Too little means blind scrolling turns; too much means context rot (2.1). See [4.4](weeks/week-04-prompt-and-tool-design.md#44-agent-computer-interface-aci).

**Nudge-then-stop**  
How to escalate a detected loop. First add a user message that names the repetition and asks for a different approach (this changes what the model sees, which a plain repeat never does). If the streak goes on, hard-stop with status `stuck`. See [2.5](weeks/week-02-core-mechanics.md#25-stopping-conditions-step-budgets-and-loop-detection).

**Null agent / shotgun agent**  
Sanity-check agents for an eval suite: one does nothing and claims success; the other submits every possible answer. Both should score 0 on should-file tasks. See [6.6](weeks/week-06-evaluation-1.md#66-public-benchmarks-swe-bench-τ-bench-gaia-terminal-bench-and-their-limits).


## O

**Offline vs online eval**  
An offline eval scores a frozen task with a known answer. An online eval scores live runs, where nobody knows the answer yet, using reference-free signals, late labels and rates over many runs. See [7.4](weeks/week-07-evaluation-2-and-iteration.md#74-online-evaluation-and-monitoring).

**Open code**  
A one-line diagnosis of a failed run, naming the first thing that went wrong, e.g. "T3: hourly pull → memory cleared → weather blamed". Open codes are later grouped into a taxonomy. See [7.1](weeks/week-07-evaluation-2-and-iteration.md#71-reading-a-transcript).

**Oracle check (simulator)**  
A scripted agent that asks exactly the right question must pass against the simulator, and a null agent must fail. If the oracle fails, the bug is in the simulator. See [7.3](weeks/week-07-evaluation-2-and-iteration.md#73-simulated-users-and-environments).

**Orchestrator–worker (lead agent + sub-agents)**  
Anthropic's Research architecture: a lead agent plans, starts sub-agents that "operate in parallel with their own context windows", and combines their short results. About 4× a chat's tokens for a single agent and about 15× for multi-agent; token usage explained 80% of the difference in performance; an Opus 4 lead with Sonnet 4 sub-agents beat a single Opus 4 by 90.2% on an internal breadth-first research eval. Covered fully in 8.1. See [3.6](weeks/week-03-state-and-memory.md#36-sub-agents-and-context-isolation).

**OTel GenAI semantic conventions**  
Vendor-neutral span names and attributes for LLM and agent telemetry: `create_agent`, `invoke_agent`, `execute_tool`, `gen_ai.agent.name`, `gen_ai.conversation.id`, `gen_ai.usage.input_tokens`, `gen_ai.tool.call.id`. Message content is opt-in. Status: Development. See [5.5](weeks/week-05-control-safety-reliability.md#55-observability-tracing-logging-trajectories-replaying-runs).

**Outcome**  
The final state of the environment after a trial (a row in the database, a ticket in the sink), as opposed to what the agent says it did. See [6.1](weeks/week-06-evaluation-1.md#61-why-agent-evals-differ-from-llm-evals).

**Outcome validity**  
Whether a benchmark's pass/fail really reflects task success (ABC). Broken by graders that accept empty answers or a scatter of every possible answer. See [6.6](weeks/week-06-evaluation-1.md#66-public-benchmarks-swe-bench-τ-bench-gaia-terminal-bench-and-their-limits).

**Overlap tool**  
Two tools that can answer the same request (`fetch_weather` next to `weather_get_history`). The model picks by name and argument count, so the shorter one wins some calls however good the descriptions are. Day 24's finding: which tools exist changes behaviour more than any wording — remove the coin flip before polishing text. See [4.2](weeks/week-04-prompt-and-tool-design.md#42-tool-design-naming-descriptions-parameters).


## P

**Paired difference**  
The per-task score of B minus A. Its mean and SE take differences in task difficulty out of the comparison. See [6.5](weeks/week-06-evaluation-1.md#65-regression-testing-a-harness-change-ab-on-prompts-and-tools).

**Parallel tool use**  
The model asks for several independent tool calls in one assistant message; results are matched back by id. You can turn it off when the order of calls matters because of side effects. See [1.3](weeks/week-01-what-an-agent-is.md#13-tool--function-calling).

**Parallel vs blocking guardrail**  
A parallel guardrail runs alongside the agent (lower latency, but the agent may act before it trips). A blocking one (`run_in_parallel=False`) runs first. Use blocking in front of tools with side effects. See [5.3](weeks/week-05-control-safety-reliability.md#53-guardrails-inputoutput-validation-policy-checks-classifiers).

**Parameter design**  
Clear names (`user_id` not `user`, `window_days` not `n`); enums and object structure so invalid states cannot be expressed; values that change the domain (site codes) as free strings plus an executor allow-list (2.4); every parameter described, with a default; and no parameter for a value the harness already knows (set it in code and remove it). See [4.2](weeks/week-04-prompt-and-tool-design.md#42-tool-design-naming-descriptions-parameters).

**Partial credit**  
A score that reflects how far a multi-step trial got (right cause with a vague ticket scores higher than no cause). See [6.3](weeks/week-06-evaluation-1.md#63-graders-exact-match-rubric-llm-as-judge-outcome-checks).

**pass@k**  
The chance that at least one of k trials succeeds. It goes up with k. Right when one success is enough (a person picks the best attempt). See [6.1](weeks/week-06-evaluation-1.md#61-why-agent-evals-differ-from-llm-evals).

**pass^k**  
The chance that all k trials succeed. It goes down with k (0.75 per trial → pass^3 ≈ 42%). Right for unattended or customer-facing agents. Estimated per task as C(c,k)/C(n,k) from n trials with c successes, then averaged over tasks (τ-bench). See [6.1](weeks/week-06-evaluation-1.md#61-why-agent-evals-differ-from-llm-evals).

**pass^k estimator**  
`C(c, k)/C(n, k)`: the chance that k trials drawn from the n all succeed. See [6.4](weeks/week-06-evaluation-1.md#64-trajectory-level-metrics-passk-steps-cost-tool-call-accuracy).

**@path import**  
CLAUDE.md syntax that pulls another file into context at launch (path relative to the importing file; up to four levels deep; ignored inside backticks or code fences). Imports from outside the working directory need a one-time approval. It helps organise a file but does not save context. See [3.4](weeks/week-03-state-and-memory.md#34-persistent-memory-files-and-memory-as-documents).

**pause_after_compaction**  
A true/false setting (default false). When true, the API returns `stop_reason: "compaction"` after writing only the compaction block, so the harness can re-inject state (plan object, scratchpad, files) before carrying on. See [3.2](weeks/week-03-state-and-memory.md#32-context-management-summarisation-compaction-truncation).

**pause_turn**  
The stop reason returned when server-side tools (web search and so on) reach their per-request iteration limit (default 10). The harness carries on by sending the response back as it is. See [2.5](weeks/week-02-core-mechanics.md#25-stopping-conditions-step-budgets-and-loop-detection).

**Pending side-effect group**  
When a gated call pauses the run, every later side-effect call in the same assistant message is held with it and settled together on resume. Each one still needs its tool_result before the next model call. See [5.2](weeks/week-05-control-safety-reliability.md#52-human-in-the-loop-approval-gates-interrupts-escalation).

**Pending writes**  
When one node in a super-step fails, LangGraph saves the outputs of the nodes that succeeded, so resuming from that super-step does not run them again. See [3.5](weeks/week-03-state-and-memory.md#35-checkpointing-and-resumability).

**Permission mode**  
The session-wide default for what needs a prompt. Claude Code: `default`/Manual, `acceptEdits`, `plan` (read-only exploring), `auto` (a background classifier reviews actions instead of a person), `dontAsk` (anything that would prompt is denied automatically; pre-approved tools still run), `bypassPermissions` (no prompts; "only use this mode in isolated environments"). Codex's equivalent is the approval policy (`on-request`, `never`, granular). See [5.1](weeks/week-05-control-safety-reliability.md#51-permissions-and-sandboxing).

**Permission rule (allow / ask / deny)**  
A policy for each tool call that the harness checks before running it: allow runs without approval, ask prompts a person, deny blocks it. Claude Code checks "deny, then ask, then allow. The first match in that order determines the outcome, and rule specificity doesn't change the order". A deny from any settings scope beats an allow from any other, and managed settings cannot be overridden. See [5.1](weeks/week-05-control-safety-reliability.md#51-permissions-and-sandboxing).

**Plan as state**  
Keeping the plan as a structured object outside the transcript (a Python variable, a `PLAN.md`, Anthropic's `feature-list.json` with a status per item). It survives compaction, can be re-injected briefly each turn, and stops the agent from quietly redefining "done". Layer 4. See [2.3](weeks/week-02-core-mechanics.md#23-planning-and-task-decomposition).

**Plan mode**  
Claude Code's permission phase (`Shift+Tab`, `--permission-mode plan`) in which the agent may read and answer but not write. The four-phase workflow is explore → plan → (a human approves or edits) → implement → commit. "If you could describe the diff in one sentence, skip the plan." See [2.3](weeks/week-02-core-mechanics.md#23-planning-and-task-decomposition).

**Plan-and-execute**  
A *planner* call writes a multi-step plan, an *executor* does one step at a time and calls tools, and a *replanner* reviews results and either finishes or revises the remaining steps (LangChain, Feb 2024). Reasons: speed (the big model is not asked after every action), cost (steps can go to smaller models), quality (the planner has to think the whole task through). See [2.3](weeks/week-02-core-mechanics.md#23-planning-and-task-decomposition).

**Planning / task decomposition**  
Writing out how a task breaks down — subgoals, their order, what depends on what — instead of choosing one step at a time from the transcript. The fix for drift on long tasks (planning failures dominate as tasks get longer, HORIZON). See [2.3](weeks/week-02-core-mechanics.md#23-planning-and-task-decomposition).

**Poka-yoke (tools)**  
Mistake-proofing the interface so the wrong call is hard to make (Anthropic). For example, requiring absolute paths after the model misused relative paths once it had changed folder. The ACI version of "make invalid states unrepresentable" (2.4, 4.2). See [4.4](weeks/week-04-prompt-and-tool-design.md#44-agent-computer-interface-aci).

**Pre-retrieval vs agentic retrieval**  
The "who decides" question. Code fetches before the call (pre-retrieval, classic RAG), or the model fetches through a search tool inside the loop (agentic search), or both (hybrid). Pre-retrieval is cheaper; agentic retrieval has a way to recover when the first fetch misses. See [3.3](weeks/week-03-state-and-memory.md#33-retrieval-for-agents-rag-vs-agentic-search).

**Privileged vs quarantined LLM (Dual LLM)**  
The privileged model has the tools and never reads untrusted text. The quarantined model reads it, has no tools, and returns typed fields or opaque references. See [5.4](weeks/week-05-control-safety-reliability.md#54-prompt-injection-and-untrusted-content).

**Progress file**  
A file the harness (or the agent, when told to) writes so the next session or context window can pick up where it left off; for example Anthropic's `claude-progress.txt`. Part of the state layer (3.1, 3.4, 10.3). See [1.4](weeks/week-01-what-an-agent-is.md#14-what-a-harness-is).

**Progressive disclosure (skills)**  
Loading in three levels. Metadata (about 100 tokens per skill, always in the system prompt) → the `SKILL.md` body (under 5k tokens recommended; read when the model decides the skill is relevant) → bundled resources (reference files read when needed; scripts run, and only their output enters context). It lets an agent carry many skills while paying only for the one in use. See [4.5](weeks/week-04-prompt-and-tool-design.md#45-skills-procedural-knowledge-loaded-on-demand).

**Prompt assembly**  
Production system prompts are not single strings; they are built from parts switched on by conditions. Claude Code's has about 25 parts (intro, system rules, doing tasks, executing actions with care, using your tools, tone and style, a cache boundary marker, session guidance, memory/output-style instructions, environment info, MCP server instructions recomputed each turn, scratchpad/budget/git status), switched by flags such as whether skills or the Agent tool are on. Piebald's extraction of v2.1.259 counts 500+ strings, 150+ sections, separate Explore/Plan subagent prompts and 27 tool descriptions. See [4.1](weeks/week-04-prompt-and-tool-design.md#41-system-prompt-architecture-for-agents).

**Prompt caching**  
The provider stores the model's computed state (the KV cache) for the start of a request. A later request that begins with byte-identical content reads it instead of computing it again. On Claude the prefix order is tools → system → messages, and a change at one level invalidates that level and every later one. Agents re-send the whole transcript every turn (input:output ≈ 100:1 at Manus), so the hit rate decides most of the bill and the time to first token. See [4.6](weeks/week-04-prompt-and-tool-design.md#46-prompt-caching-and-cost).

**Prompt injection (direct / indirect)**  
Text that steers the model against what the harness intends. Direct injection comes from the user; indirect injection is planted in content the agent reads (web page, email, document, a free-text API field, file, memory). It works because instructions and data travel in the same token stream. See [5.4](weeks/week-05-control-safety-reliability.md#54-prompt-injection-and-untrusted-content).

**Prompt sections (role / constraints / procedures / examples)**  
The four blocks found in every serious agent prompt, marked off with XML tags or Markdown headers: who the agent is and what "done" looks like; what it must never do (mirrors layer 5); how to work, including order and the completion rule (mirrors layer 3); and a few varied, typical examples that fix the format (mirror the layer-2 schema) — not a long list of edge cases. See [4.1](weeks/week-04-prompt-and-tool-design.md#41-system-prompt-architecture-for-agents).

**Prompted JSON**  
Asking for JSON in the prompt and parsing the text. It breaks on preamble, code fences, trailing commas, missing fields and wrong types, so the harness ends up full of regex and retries. See [2.4](weeks/week-02-core-mechanics.md#24-structured-outputs-and-schemas).

**Protocol error vs tool execution error (MCP)**  
The MCP spec's split. Protocol errors (unknown tool, invalid arguments, server errors) are JSON-RPC `error` responses that the client handles and usually throws away. Tool execution errors (API failures, invalid input data, business-logic errors) come back as a normal `result` with `isError: true`, so they stay in the model's context. The Claude API equivalent is `is_error: true` on a `tool_result` (1.3). See [4.3](weeks/week-04-prompt-and-tool-design.md#43-tool-error-messages-as-instructions-designing-for-recovery).

**Public agent benchmark**  
A published, frozen set of tasks, environments and graders (SWE-bench, Terminal-Bench, τ-bench, GAIA). A score on it belongs to model + harness + infrastructure + version, not to the model alone. See [6.6](weeks/week-06-evaluation-1.md#66-public-benchmarks-swe-bench-τ-bench-gaia-terminal-bench-and-their-limits).


## R

**ReAct**  
Yao et al. (2022): mix reasoning steps with actions — *Thought → Action → Observation*, repeated — instead of reasoning only at the start (chain-of-thought) or acting without reflecting. The reasoning tracks and updates the plan and handles surprises; the actions ground it in real information. It is the 1.2 loop with the Thought written out. See [2.2](weeks/week-02-core-mechanics.md#22-react-and-reasoning-then-acting-extended-thinking-in-the-loop).

**Read-heavy vs write-heavy delegation**  
Reading splits safely across sub-agents (each result stands alone). Writing conflicts, because "actions carry implicit decisions, and conflicting decisions carry bad results" (Cognition). Hand out investigation; keep combining results, memory writes and side effects in one agent. See [3.6](weeks/week-03-state-and-memory.md#36-sub-agents-and-context-isolation).

**Rebuilt context**  
The exact request the model received at a given turn, reconstructed after clearing, compaction and skill loading. It is what you diagnose from, because the trajectory log is not what the model saw. See [7.1](weeks/week-07-evaluation-2-and-iteration.md#71-reading-a-transcript).

**Recitation**  
Manus's attention trick: the agent rewrites a `todo.md` at the end of the context each step, "reciting its objectives into the end of the context" so the goals stay in the model's recent attention. A plan-as-state (2.3) that also works as an anchor compaction cannot remove. See [3.2](weeks/week-03-state-and-memory.md#32-context-management-summarisation-compaction-truncation).

**redacted_thinking**  
A thinking block hidden for safety reasons (it has only `data`). It must also be passed back unchanged. Filtering on `block.type == "thinking"` alone quietly drops it and breaks the tool-use protocol. See [2.2](weeks/week-02-core-mechanics.md#22-react-and-reasoning-then-acting-extended-thinking-in-the-loop).

**Reference solution**  
A known-good outcome that passes the task's grader in its environment. It proves the task can be solved and the grader is wired up correctly. See [6.2](weeks/week-06-evaluation-1.md#62-building-an-eval-set-from-real-failures-the-taskgraderenvironment-triad).

**Regression eval**  
Tasks the agent should pass about 100% of the time; it guards against sliding back. Capability tasks *graduate* into it once they are solved reliably. See [6.2](weeks/week-06-evaluation-1.md#62-building-an-eval-set-from-real-failures-the-taskgraderenvironment-triad).

**Regression gate**  
A per-task rule (for example, a regression-set task failing 2 or more of 10) that blocks a change whatever the average says. See [6.5](weeks/week-06-evaluation-1.md#65-regression-testing-a-harness-change-ab-on-prompts-and-tools).

**Removal ablation**  
Taking a harness component out and re-running the tasks it guards, to see if it still earns its place. Run it whenever the model changes. See [7.6](weeks/week-07-evaluation-2-and-iteration.md#76-case-study-how-labs-iterate-on-coding-agent-harnesses).

**Replanning**  
Revising the rest of the plan after a step's result. This is what lets a fixed upfront plan survive contact with real results. It needs a tool that edits the plan object *and* tool results that show the surprise (Day 11). See [2.3](weeks/week-02-core-mechanics.md#23-planning-and-task-decomposition).

**Replay / time travel**  
Calling a graph with an earlier `checkpoint_id` re-runs the nodes after that checkpoint from that state. `get_state_history` lists the thread's snapshots, newest first. `update_state` makes a new checkpoint with edited values rather than changing an old one (history is append-only). See [3.5](weeks/week-03-state-and-memory.md#35-checkpointing-and-resumability).

**request_id**  
The `request-id` header / `request_id` body field (`req_…`) on every response; `_request_id` on SDK response objects. Log it on every retry and failure — it is what support needs. See [2.6](weeks/week-02-core-mechanics.md#26-error-handling-retries-backoff-and-feeding-tool-errors-back-to-the-model).

**response_format knob**  
A `concise|detailed` (or `detail=true`) parameter that lets the model ask for the short version by default. Anthropic's example: 72 vs 206 tokens for the same result. Result shaping (2.1) offered as a choice. See [4.2](weeks/week-04-prompt-and-tool-design.md#42-tool-design-naming-descriptions-parameters).

**Restorable offload (restorable compression)**  
Manus's rule: only shrink context in ways the agent can undo — "the content of a web page can be dropped from the context as long as the URL is preserved, and a document's contents can be omitted if its path remains available in the sandbox". The file system is "the ultimate context: unlimited in size, persistent by nature, and directly operable by the agent". This is what makes truncation and compaction safe; the memory tool (3.1) is the API's version. See [3.2](weeks/week-03-state-and-memory.md#32-context-management-summarisation-compaction-truncation).

**Result shaping**  
The executor parses, cuts down or summarises a tool's raw output before it goes into the transcript (numbers not payloads; the last 10k characters of bash output; "…4,800 chars omitted, call with verbose=true"). It is done in code, never by asking the model to "be brief". The reason is recall (2.1) as much as cost. See [1.3](weeks/week-01-what-an-agent-is.md#13-tool--function-calling).

**Resumability**  
A fresh process, given only a run id, can load the latest checkpoint and carry on as if nothing happened, making exactly the remaining calls with no repeated side effects. See [3.5](weeks/week-03-state-and-memory.md#35-checkpointing-and-resumability).

**Retrieval-augmented generation (RAG)**  
Before the model runs, code finds passages related to the query (embeddings, BM25, or both) and puts them into the prompt. This is a workflow (1.1): one shot, code decides what is fetched, and the model's reading gives no feedback. See [3.3](weeks/week-03-state-and-memory.md#33-retrieval-for-agents-rag-vs-agentic-search).

**retry-after**  
A header on a 429 response that says how long to wait; the SDKs follow it. If a 429 has no such header, that signals a spend cap. See [2.6](weeks/week-02-core-mechanics.md#26-error-handling-retries-backoff-and-feeding-tool-errors-back-to-the-model).

**Retry-with-corrections**  
The model's documented behaviour when a parameter is missing or invalid: it "will retry 2-3 times with corrections before apologizing to the user". An error that includes the correction gets fixed on the first retry; a bare "invalid input" uses up all of them. See [2.6](weeks/week-02-core-mechanics.md#26-error-handling-retries-backoff-and-feeding-tool-errors-back-to-the-model).

**Retryable vs non-retryable status**  
Anthropic's groups. Retry: 429 (with `retry-after`), 500, 504, 529, 409 once resolved, connection and timeout errors. Never retry: 400 (bad request, including too-long context), 401, 403, 404, 413, or a 429 with no `retry-after` header (a spend cap; it keeps failing until access comes back). See [2.6](weeks/week-02-core-mechanics.md#26-error-handling-retries-backoff-and-feeding-tool-errors-back-to-the-model).

**Review card**  
What the approver sees: the action and its arguments, the evidence (deciding numbers, notes), whether it can be undone, and what happens on timeout — not the transcript. See [5.2](weeks/week-05-control-safety-reliability.md#52-human-in-the-loop-approval-gates-interrupts-escalation).

**ReWOO**  
A plan-and-execute variant where plan steps refer to earlier outputs by variable (`#E2`), so the whole plan can run without replanning. Steps still run one after another. See [2.3](weeks/week-02-core-mechanics.md#23-planning-and-task-decomposition).

**Right altitude**  
Anthropic's target for agent instructions: specific enough to guide behaviour, general enough to give the model strong rules of thumb rather than a script. The two ways to miss: *brittle hardcoded logic* (if-else chains written as prose, which break on the first unexpected case and are really a workflow, 1.6) and *vague high-level guidance* ("be thorough"), which gives no concrete signal. See [4.1](weeks/week-04-prompt-and-tool-design.md#41-system-prompt-architecture-for-agents).

**Rolling-window alert**  
An online alert computed over several nights (for example 7) rather than one, or on a count with a hard floor. With 40 runs a night, a 10% rate has a standard error of about 4.7 points, so single nights are mostly noise. See [7.4](weeks/week-07-evaluation-2-and-iteration.md#74-online-evaluation-and-monitoring).

**Rubric**  
Explicit criteria a judge applies. Works best as several pass/fail criteria, each graded by its own separate judge, rather than one 1–5 score. See [6.3](weeks/week-06-evaluation-1.md#63-graders-exact-match-rubric-llm-as-judge-outcome-checks).

**Run status**  
The final state the loop returns: success / budget / stuck / refusal / error. This is the unit layer 6 adds up; an eval that cannot tell these apart measures nothing. See [2.5](weeks/week-02-core-mechanics.md#25-stopping-conditions-step-budgets-and-loop-detection).

**Run statuses (Week 5 additions)**  
`awaiting_approval` (paused at a gate) and `expired` (not reviewed before the timeout; never filed, never auto-approved), added to 2.5's success / budget / stuck / refusal / error. See [5.2](weeks/week-05-control-safety-reliability.md#52-human-in-the-loop-approval-gates-interrupts-escalation).


## S

**Sandbox**  
Operating-system enforcement of file and network limits for everything a shell or code tool runs, child processes included (bubblewrap on Linux, Seatbelt on macOS; Codex adds seccomp). Both limits are needed: no network isolation → data can be sent out; no filesystem isolation → the agent can escape. Codex modes: `read-only`, `workspace-write` (default; `.git` and similar protected), `danger-full-access`. See [5.1](weeks/week-05-control-safety-reliability.md#51-permissions-and-sandboxing).

**Saturation**  
Scores near the ceiling, where the remaining gap is mostly broken tasks and noise. See [6.6](weeks/week-06-evaluation-1.md#66-public-benchmarks-swe-bench-τ-bench-gaia-terminal-bench-and-their-limits).

**Scratchpad / structured note-taking (agentic memory)**  
Working memory the model writes on purpose outside the transcript during a run (NOTES.md, a plan file, a progress file): "the agent regularly writes notes persisted to memory outside of the context window" (Anthropic). It is curated, does not add to the growing token bill or to context rot, and can be re-injected; it belongs to one task. A note must hold the deciding number, not just the verdict, or a resumed run has to work it out again. See [3.1](weeks/week-03-state-and-memory.md#31-short-term-vs-long-term-memory-scratchpads-conversation-state).

**Search–harness–delivery as one system**  
Sen et al. (May 2026): the same documents and model scored 93.1% under one harness and 76.7% under another. Retrieval, harness and delivery path must be "a single jointly evaluated system rather than independent design choices". See [3.3](weeks/week-03-state-and-memory.md#33-retrieval-for-agents-rag-vs-agentic-search).

**Section ablation**  
The eval move for a system prompt: run the same task with one section removed at a time and record which removal changes behaviour (turns, completion signal, deciding number present, ignored results). Sections whose removal changes nothing are cut or moved into code (6.5). Day 23's result: procedure moves decisions, examples move format, constraints move only the hard case — and one run of a random system proves nothing; use five. See [4.1](weeks/week-04-prompt-and-tool-design.md#41-system-prompt-architecture-for-agents).

**Semantic / episodic / procedural memory**  
LangChain's three kinds of long-term memory: facts ("SG-03 recabled 2026-08-12"); past events and actions ("last three SG-03 incidents were curtailment"); and rules for doing the job (system prompt, hypothesis checklist — memory that changes behaviour rather than facts). See [3.1](weeks/week-03-state-and-memory.md#31-short-term-vs-long-term-memory-scratchpads-conversation-state).

**Session (Claude Agent SDK)**  
The saved conversation history of a run, written automatically as `~/.claude/projects/<encoded-cwd>/<session-id>.jsonl`. `session_id` is on every result message; `resume=<id>` continues it (for example after `error_max_turns`, with a higher limit), `continue_conversation` picks the most recent one in the folder, and `fork_session=True` branches a copy with its own id. It saves the conversation, not the filesystem — pair it with file checkpointing or a `SessionStore` for other hosts. See [3.5](weeks/week-03-state-and-memory.md#35-checkpointing-and-resumability).

**Shape vs truth**  
Constrained decoding guarantees types, required keys and valid enum values. It says nothing about whether a value is *correct* (a site code that exists, a real date, an id that is in the plan). Syntax checks move to the API; meaning checks stay in the executor (allow-lists, ranges, existence checks → `is_error` with the fix). See [2.4](weeks/week-02-core-mechanics.md#24-structured-outputs-and-schemas).

**Short-term memory**  
The transcript: the message history for one thread, which "tracks the ongoing conversation by maintaining message history within a session" (LangChain). It lives in the harness's state object and dies or overflows with the run. Everything the model "remembers" mid-run is here, unless the harness copies it somewhere else. See [3.1](weeks/week-03-state-and-memory.md#31-short-term-vs-long-term-memory-scratchpads-conversation-state).

**Silent wrong action**  
A side effect taken on bad data or a wrong conclusion, with nothing to flag it (for example, forty tickets filed on a null weather feed, or made-up actuals written into the training set). This is what the side-effect question measures, and it is the case for a human gate. See [1.6](weeks/week-01-what-an-agent-is.md#16-when-not-to-build-an-agent).

**Six layers**  
The course's map of a harness: (1) prompts and injected context, (2) tools and executor, (3) loop control, (4) state, (5) guardrails and permissions, (6) feedback and evals. See [1.4](weeks/week-01-what-an-agent-is.md#14-what-a-harness-is).

**Skill (Agent Skill)**  
A folder with a `SKILL.md` (YAML frontmatter with `name` and `description`, then Markdown instructions) and optionally `scripts/`, `references/`, `assets/`. Packaged know-how that the agent loads only when it is relevant. "Like putting together an onboarding guide for a new hire" (Anthropic). See [4.5](weeks/week-04-prompt-and-tool-design.md#45-skills-procedural-knowledge-loaded-on-demand).

**Skill description (trigger)**  
The frontmatter `description` (at most 1,024 characters in the spec; Claude Code cuts description + `when_to_use` at 1,536 characters in its listing). It is the only text the model sees before deciding to load a skill, so it must say what the skill does *and* when to use it, in the third person, with the key terms. A skill that never fires, or always fires, has a description bug. See [4.5](weeks/week-04-prompt-and-tool-design.md#45-skills-procedural-knowledge-loaded-on-demand).

**Stall (empty end_turn)**  
An `end_turn` with nothing useful in it (Anthropic documents a 2–3-token empty response). It usually happens when the harness adds text after tool results, so the model expects the user to speak. `end_turn` is a sign the run may be done, not proof. See [2.5](weeks/week-02-core-mechanics.md#25-stopping-conditions-step-budgets-and-loop-detection).

**State footer**  
State the harness holds (open file, cursor, current folder, current site/window) repeated in every observation, so the agent never has to remember it or ask again. SWE-agent shows the open file and working directory every turn. See [4.4](weeks/week-04-prompt-and-tool-design.md#44-agent-computer-interface-aci).

**Stateless model**  
The API call remembers nothing between calls. All continuity comes from what the harness sends again. See [1.2](weeks/week-01-what-an-agent-is.md#12-the-agent-loop).

**StateSnapshot**  
LangGraph's checkpoint record: `values` (state channel values), `next` (nodes to run next; empty means the graph is finished), `config` (`thread_id`, `checkpoint_ns`, `checkpoint_id`), `metadata` (`source`: input/loop/update; `writes` per node; `step`), `created_at`, `parent_config`, `tasks` (with any error or interrupt). See [3.5](weeks/week-03-state-and-memory.md#35-checkpointing-and-resumability).

**Status mix**  
The share of runs that end in success / budget / stuck / refusal / error. It separates loop-control failures from wrong answers. See [6.4](weeks/week-06-evaluation-1.md#64-trajectory-level-metrics-passk-steps-cost-tool-call-accuracy).

**Step budget / max_turns**  
A cap on model calls (or tool-use turns) per run. Claude Agent SDK `max_turns` counts tool-use turns only and has no limit by default; OpenAI Agents SDK `max_turns` defaults to 10 (`MaxTurnsExceeded`); mini-swe-agent uses `step_limit`. Hitting it must be a handled path, not a crash. See [2.5](weeks/week-02-core-mechanics.md#25-stopping-conditions-step-budgets-and-loop-detection).

**stop_reason**  
Why the model stopped writing: `tool_use` (run a tool and carry on), `end_turn` (finished on its own), `max_tokens`, `stop_sequence`, `refusal`, `pause_turn`, `model_context_window_exceeded`, or `compaction` (3.2). How to handle each one is covered in 2.5. See [1.2](weeks/week-01-what-an-agent-is.md#12-the-agent-loop).

**Stopping condition**  
Any check the loop makes before the next model call that can end the run: stop-reason handling, a budget, a stuck detector, or an explicit "done" signal. The weakest one, `stop_reason != "tool_use"`, only means "no tool was asked for". See [2.5](weeks/week-02-core-mechanics.md#25-stopping-conditions-step-budgets-and-loop-detection).

**Streaming**  
Getting the response as server-sent events while it is being written. It cuts time to first token (how fast it feels), not total generation time. See [5.6](weeks/week-05-control-safety-reliability.md#56-latency-and-cost-budgets-parallel-tool-calls-streaming).

**Strict tool use**  
`strict: true` on a tool "guarantees Claude's tool inputs match your JSON Schema by constraining the model's token sampling to schema-valid outputs", and also guarantees the tool `name` is valid. Not accepted on the computer-use or browser-use toolsets. Limits per request: 20 strict tools, 24 optional parameters, 16 union-typed parameters (over that: "Schema is too complex for compilation", a 400 error). See [2.4](weeks/week-02-core-mechanics.md#24-structured-outputs-and-schemas).

**Structural vs content telemetry**  
Structural telemetry is durations, names and token counts (exported by default). Content telemetry is prompt text, tool arguments, tool outputs and raw API bodies (opt-in: Claude `OTEL_LOG_USER_PROMPTS` / `OTEL_LOG_TOOL_DETAILS` / `OTEL_LOG_TOOL_CONTENT` / `OTEL_LOG_RAW_API_BODIES`; OpenAI `trace_include_sensitive_data`, default true). See [5.5](weeks/week-05-control-safety-reliability.md#55-observability-tracing-logging-trajectories-replaying-runs).

**Structured outputs / schema-constrained output**  
The API guarantees the output fits a JSON Schema you supply. OpenAI: `strict: true` on a function or a `json_schema` response format. Claude: `output_config.format = {"type": "json_schema", "schema": …}` for the final response ("JSON outputs") and `"strict": true` on a tool definition ("strict tool use"); both can be used in one request. See [2.4](weeks/week-02-core-mechanics.md#24-structured-outputs-and-schemas).

**Structured-output escape hatches**  
Three cases where output may not match the schema: `stop_reason: "refusal"` (the refusal text wins), `stop_reason: "max_tokens"` (cut-off JSON), and enum or const values that differ only in capitalisation. The loop must check `stop_reason` before parsing. See [2.4](weeks/week-02-core-mechanics.md#24-structured-outputs-and-schemas).

**Stuck detector / loop detection**  
Harness code that compares recent (action, observation) pairs — by tool name, input and result content, ignoring ids — and steps in when they repeat. OpenHands' StuckDetector (on by default) flags: same action and same observation 4+ times; same action and an error 3+ times; 3+ assistant messages in a row with no tool call ("monologue"); A,B,A,B alternation for 6+ cycles; repeated context-window errors. See [2.5](weeks/week-02-core-mechanics.md#25-stopping-conditions-step-budgets-and-loop-detection).

**Sub-agent**  
A second agent loop (1.2) started by the main loop, with its own fresh transcript, its own system prompt and (usually) a smaller set of tools. It runs to the end and returns only its final message to the parent, as a tool result. Everything it read along the way is thrown away with its context window. See [3.6](weeks/week-03-state-and-memory.md#36-sub-agents-and-context-isolation).

**Summarisation / compaction**  
Replacing a stretch of the transcript with a summary the model writes. It loses information by judgement (what the summariser kept) rather than by position. The extra model call costs tokens and latency, and it is where domain-specific instructions belong. See [3.2](weeks/week-03-state-and-memory.md#32-context-management-summarisation-compaction-truncation).

**Summarised vs iterative search**  
Returning a capped list of all matches at once (SWE-agent: max 50, 18.0%) versus stepping through matches one at a time like an IDE (12.0%, below no search at all at 15.7%). What is friendly for people can be hostile for agents, because every step is another billed turn. See [4.4](weeks/week-04-prompt-and-tool-design.md#44-agent-computer-interface-aci).

**Super-step**  
One round of LangGraph execution in which all ready nodes run (in parallel if independent). A checkpoint is written once per super-step. See [3.5](weeks/week-03-state-and-memory.md#35-checkpointing-and-resumability).

**Supported schema subset**  
Supported: `type`, `properties`, `required`, `enum`, `const`, `additionalProperties: false`, `format: date` and similar. **Not** supported: `minimum`/`maximum`, `minLength`/`maxLength`, `pattern`. SDKs strip unsupported keywords and move them into the field description — that is, into prompt text, a hint and not a guarantee. Required properties are written first, then optional ones. See [2.4](weeks/week-02-core-mechanics.md#24-structured-outputs-and-schemas).

**SWE-bench Verified / Pro**  
Verified: 500 GitHub-issue repair tasks filtered by people and graded by hidden tests (retired by OpenAI in Feb 2026 over flawed tests and contamination). Pro: its harder, less contaminated successor. See [6.6](weeks/week-06-evaluation-1.md#66-public-benchmarks-swe-bench-τ-bench-gaia-terminal-bench-and-their-limits).

**Swiss-cheese model**  
Anthropic's name for stacking several imperfect evaluation layers, because no single layer catches everything. See [7.4](weeks/week-07-evaluation-2-and-iteration.md#74-online-evaluation-and-monitoring).


## T

**Task (eval)**  
One test with defined inputs and success criteria (also called a problem or test case). For the investigator: a fixture incident plus the expected root cause. See [6.1](weeks/week-06-evaluation-1.md#61-why-agent-evals-differ-from-llm-evals).

**Task error**  
A failure inside a tool the model asked for (bad argument, missing site, crashed script). It must go back to the model as an `is_error` tool_result, because only the model can choose a different action. Layer 2. See [2.6](weeks/week-02-core-mechanics.md#26-error-handling-retries-backoff-and-feeding-tool-errors-back-to-the-model).

**Task validation**  
The one-time check when a task is added: the empty, do-nothing outcome fails the grader and the reference solution passes it. See [6.2](weeks/week-06-evaluation-1.md#62-building-an-eval-set-from-real-failures-the-taskgraderenvironment-triad).

**Task validity**  
Whether a task can be solved only with the target ability, and can be solved at all (ABC). Broken by tests that are too narrow or too wide, and by live environments that decay. See [6.6](weeks/week-06-evaluation-1.md#66-public-benchmarks-swe-bench-τ-bench-gaia-terminal-bench-and-their-limits).

**Task/grader/environment triad**  
The three parts of an eval task that must agree: inputs plus clear success criteria; the frozen state the agent acts on (rebuilt for each trial); and the code that reads the end state. See [6.2](weeks/week-06-evaluation-1.md#62-building-an-eval-set-from-real-failures-the-taskgraderenvironment-triad).

**Terminal-Bench 2.0**  
89 checked command-line tasks run in containers through the Harbor harness and graded by a test script on the final state. See [6.6](weeks/week-06-evaluation-1.md#66-public-benchmarks-swe-bench-τ-bench-gaia-terminal-bench-and-their-limits).

**Theoretical saturation**  
The point in error discovery where new traces stop showing new failure modes or changing the ones you have. See [6.2](weeks/week-06-evaluation-1.md#62-building-an-eval-set-from-real-failures-the-taskgraderenvironment-triad).

**"think" tool**  
Anthropic's do-nothing tool ("It will not obtain new information or change the database, but just append the thought to the log") that gives the model a deliberate pause in the middle of a run, after a tool result. It differs from built-in thinking in when it happens. On τ-bench airline with a usage prompt: 0.584 pass^1, versus 0.332 baseline and 0.412 with extended thinking alone. See [2.2](weeks/week-02-core-mechanics.md#22-react-and-reasoning-then-acting-extended-thinking-in-the-loop).

**Thinking block**  
An assistant content block (`type: "thinking"`) that comes before text or `tool_use` blocks when thinking is on. It carries a `signature` (the full reasoning, encrypted) and, by default on newer models, an empty or summarised `thinking` text. It must be passed back unchanged within a tool-use turn. See [2.2](weeks/week-02-core-mechanics.md#22-react-and-reasoning-then-acting-extended-thinking-in-the-loop).

**thinking_tokens**  
`usage.output_tokens_details.thinking_tokens`: the raw reasoning tokens billed as output on this call. Thinking from earlier turns that stays in context is billed as input (keep-all models: Opus 4.5+, Sonnet 4.6+, 5-series; earlier models keep only the last turn's). See [2.2](weeks/week-02-core-mechanics.md#22-react-and-reasoning-then-acting-extended-thinking-in-the-loop).

**Thought / Action / Observation**  
ReAct's three text parts. In 2022 the harness pulled out the Action with a regex and stopped generation at "Observation:". Tool calling (1.3) replaced the parsing, and `thinking` blocks replaced the Thought text. See [2.2](weeks/week-02-core-mechanics.md#22-react-and-reasoning-then-acting-extended-thinking-in-the-loop).

**Thread**  
LangGraph's unit for one conversation or run: the sequence of checkpoints sharing a `thread_id`. The same id continues the run; a new id starts fresh. See [3.5](weeks/week-03-state-and-memory.md#35-checkpointing-and-resumability).

**Tolerance match**  
Comparing numbers within an allowed error instead of requiring the exact same string (the CORE-Bench "96.12" vs "96.124991…" lesson). See [6.3](weeks/week-06-evaluation-1.md#63-graders-exact-match-rubric-llm-as-judge-outcome-checks).

**Tool / function calling**  
The protocol a model uses to ask for an action. Tool definitions go in, a structured `tool_use` request comes out, and the harness runs the tool and returns a `tool_result`. The model never runs anything itself. See [1.3](weeks/week-01-what-an-agent-is.md#13-tool--function-calling).

**Tool consolidation**  
OpenAI's matching rule: merge functions that are always called one after another, and keep the active set small (their guidance: under about 20 tools at once), because the model picks less accurately as the menu grows. See [4.2](weeks/week-04-prompt-and-tool-design.md#42-tool-design-naming-descriptions-parameters).

**Tool definition**  
A tool's `name` (must match `^[a-zA-Z0-9_-]{1,64}$`), `description` (plain text), `input_schema` (JSON Schema), optional `input_examples` and optional `strict` (2.4). The API writes it into the system prompt, so it is prompt text that costs tokens on every call. See [1.3](weeks/week-01-what-an-agent-is.md#13-tool--function-calling).

**Tool guardrail**  
A check wrapped around one function tool's input or output. Outcomes: allow / reject_content (the model sees a message) / raise_exception. See [5.3](weeks/week-05-control-safety-reliability.md#53-guardrails-inputoutput-validation-policy-checks-classifiers).

**Tool namespacing**  
Prefixing names by service or resource (`weather_get_history`, `archive_search_incidents`, `asana_projects_search`) so the model can tell tool families apart before it reads descriptions. Names are verb_noun and state the effect. Two tools whose names differ only by one modifier are a coin flip. See [4.2](weeks/week-04-prompt-and-tool-design.md#42-tool-design-naming-descriptions-parameters).

**Tool registry / executor**  
Harness code that maps tool names to functions, checks inputs against the schema, runs the function, and formats the result for the model. See [1.3](weeks/week-01-what-an-agent-is.md#13-tool--function-calling).

**Tool-argument matching**  
A per-tool rule for when two calls count as the same: exact, ignore, chosen fields, or a custom comparison. See [6.4](weeks/week-06-evaluation-1.md#64-trajectory-level-metrics-passk-steps-cost-tool-call-accuracy).

**Tool-call precision / recall**  
Precision: the share of the agent's calls that are in the reference call set. Recall: the share of reference calls the agent made. See [6.4](weeks/week-06-evaluation-1.md#64-trajectory-level-metrics-passk-steps-cost-tool-call-accuracy).

**Tool-description eval loop**  
Anthropic's final step: run the tools on realistic tasks, read the transcripts for wrong-tool and wrong-argument calls, then let a model rewrite the descriptions against that eval. They report their own tools got better this way. Layer 6 applied to layer 2's text. See [4.2](weeks/week-04-prompt-and-tool-design.md#42-tool-design-naming-descriptions-parameters).

**tool_choice**  
A request setting for whether the model may call a tool (`auto`), must call one (`any`), must call a named one (`tool`), or may not call any (`none`). `any` and `tool` turn tool calling into a way to get structured output (guaranteed when combined with `strict`, 2.4). `none` forces a final text answer, which is useful when a budget runs out or for a planning call with no tools. See [1.3](weeks/week-01-what-an-agent-is.md#13-tool--function-calling).

**tool_result block**  
The content block in a user message that the harness sends back, matched by `tool_use_id`, carrying the tool's output. `is_error: true` marks a failed call. See [1.3](weeks/week-01-what-an-agent-is.md#13-tool--function-calling).

**tool_use block**  
The content block in an assistant message where the model asks for an action: `id`, `name`, `input` (the JSON arguments). It is a proposal, not an execution. OpenAI's version is a `function_call` item with `call_id`, `name`, `arguments`. See [1.3](weeks/week-01-what-an-agent-is.md#13-tool--function-calling).

**ToolError(problem, fix, data, retryable)**  
The course's exception type. Every tool raises it with the three fields plus a flag for whether the same retry could succeed. The executor writes out the text, sets `is_error`, and logs the tool and the error class. See [4.3](weeks/week-04-prompt-and-tool-design.md#43-tool-error-messages-as-instructions-designing-for-recovery).

**Tools as the agent's UI**  
The model sees only names, descriptions and parameter schemas, and chooses among them like buttons on an unfamiliar screen. A tool is "a contract between deterministic systems and non-deterministic agents" (Anthropic). Calls with the wrong tool or wrong arguments are mostly interface bugs, which you can fix without touching the model. See [4.2](weeks/week-04-prompt-and-tool-design.md#42-tool-design-naming-descriptions-parameters).

**Trace / span**  
A trace is one run from start to end. Spans are its nested, timed operations (run → turn/model call → tool call → sub-agent spans under the tool span that started them), each with attributes (tokens, latency, stop_reason, tool name, is_error, ids). See [5.5](weeks/week-05-control-safety-reliability.md#55-observability-tracing-logging-trajectories-replaying-runs).

**Trace context propagation**  
Passing W3C `TRACEPARENT`/`TRACESTATE` so the agent's spans (and the commands it runs) sit under the calling application's trace. See [5.5](weeks/week-05-control-safety-reliability.md#55-observability-tracing-logging-trajectories-replaying-runs).

**Trajectory log**  
The content record of a run (the exact request and response for each model call, every tool result, gate decisions), kept apart from spans. Spans say where time, tokens and errors went; the trajectory says what happened. See [5.5](weeks/week-05-control-safety-reliability.md#55-observability-tracing-logging-trajectories-replaying-runs).

**Trajectory match modes**  
Strict (same calls, same order), unordered (same calls, any order), subset (nothing beyond the reference), superset (all reference calls, extras allowed) (agentevals). See [6.4](weeks/week-06-evaluation-1.md#64-trajectory-level-metrics-passk-steps-cost-tool-call-accuracy).

**Transcript (eval)**  
The full record of a trial (outputs, tool calls, reasoning, intermediate results). The same thing as the trajectory log in 5.5. See [6.1](weeks/week-06-evaluation-1.md#61-why-agent-evals-differ-from-llm-evals).

**Transcript (message history)**  
The ordered list of user and assistant messages, including tool calls and tool results. It is re-sent in full on every model call and is the agent's only working memory. See [1.2](weeks/week-01-what-an-agent-is.md#12-the-agent-loop).

**Trial**  
One attempt at a task. Agents are not deterministic, so each task gets several trials. See [6.1](weeks/week-06-evaluation-1.md#61-why-agent-evals-differ-from-llm-evals).

**Tripwire (OpenAI Agents SDK)**  
A flag on a guardrail result (`tripwire_triggered`) that stops the run by raising `InputGuardrailTripwireTriggered` / `OutputGuardrailTripwireTriggered`. See [5.3](weeks/week-05-control-safety-reliability.md#53-guardrails-inputoutput-validation-policy-checks-classifiers).

**Truncation**  
Making the transcript smaller by position or category, with no model call: drop the oldest turns, or the oldest tool results. Predictable and cheap. It assumes older means less needed, which is false for the task and early decisions — so truncate a category that can be fetched again (tool results), not the whole history. See [3.2](weeks/week-03-state-and-memory.md#32-context-management-summarisation-compaction-truncation).

**Turn / step**  
One pass through the agent loop: one model call plus the tool runs it triggers. See [1.2](weeks/week-01-what-an-agent-is.md#12-the-agent-loop).

**Turn latency**  
Time to first token + output generation + tool running time for one loop pass. A run's wall-clock time is roughly the sum over turns, so the number of turns is the main driver of latency. See [5.6](weeks/week-05-control-safety-reliability.md#56-latency-and-cost-budgets-parallel-tool-calls-streaming).


## U

**Unbiased pass@k estimator**  
`1 − C(n−c, k)/C(n, k)` from n ≥ k trials with c successes (Chen et al. 2021). It varies less than checking "any pass" in exactly k runs. See [6.4](weeks/week-06-evaluation-1.md#64-trajectory-level-metrics-passk-steps-cost-tool-call-accuracy).

**Unfair failure**  
A failure caused by the grader, the task or the infrastructure rather than the agent. Rule these out first when reading a transcript, and count them in their own categories so they never count against the agent. See [7.1](weeks/week-07-evaluation-2-and-iteration.md#71-reading-a-transcript).

**Unknown option**  
An explicit "not enough information" verdict offered to a judge so it does not guess. See [6.3](weeks/week-06-evaluation-1.md#63-graders-exact-match-rubric-llm-as-judge-outcome-checks).

**Untrusted content / provenance**  
Any tool result whose text an outside party could have written. Tagging where it came from (`<untrusted source=…>`, "treat as data") lowers attack rates, but it is a filter, not a wall. See [5.4](weeks/week-05-control-safety-reliability.md#54-prompt-injection-and-untrusted-content).

**usage field**  
The token count on each response: `input_tokens`, `output_tokens`, plus `cache_read_input_tokens` and `cache_creation_input_tokens` with prompt caching, and `iterations` when compaction ran (3.2). All of these count toward the window. The harness uses it to watch the context grow. It does not include a sub-agent's tokens (3.6). See [2.1](weeks/week-02-core-mechanics.md#21-context-window-as-working-memory).

**usage.iterations**  
A per-response list of `{type: "compaction"|"message", input_tokens, output_tokens}`. The top-level `input_tokens`/`output_tokens` leave out the compaction pass, so total billed tokens = the sum over iterations. Counting compactions × trigger gives a cheap total-token budget (2.5). See [3.2](weeks/week-03-state-and-memory.md#32-context-management-summarisation-compaction-truncation).


## V

**Validator / policy check / classifier**  
The three kinds of guardrail: fixed checks on shape, range, regex or allow-list; business rules written as code; and a small model or LLM judge answering a narrow question (based on probability — a filter, not a wall). See [5.3](weeks/week-05-control-safety-reliability.md#53-guardrails-inputoutput-validation-policy-checks-classifiers).

**Verifier**  
Any independent check the agent can run on its own work, such as a `bash` tool that runs the tests or a check that the numbers in a draft match. Without one, a tool's false "ok" is never caught, because the transcript is the only memory. See [1.5](weeks/week-01-what-an-agent-is.md#15-anatomy-of-a-real-agent).


## W

**Who&When**  
Zhang et al.'s benchmark (ICML 2025) for finding which agent caused a failure and at which step. The best automated method found the agent 53.5% of the time but the decisive step only 14.2%. See [7.1](weeks/week-07-evaluation-2-and-iteration.md#71-reading-a-transcript).

**Windowed viewer**  
A viewer for a file (or a data series) that shows a fixed window with line numbers, the path, the total length and a count of what is hidden, plus scroll and goto commands. SWE-agent's default is 100 lines. The alternative to dumping whole files. See [4.4](weeks/week-04-prompt-and-tool-design.md#44-agent-computer-interface-aci).

**Workflow**  
A system where LLMs and tools run along code paths written in advance. The graph is fixed before any model runs. See [1.1](weeks/week-01-what-an-agent-is.md#11-llm-call-vs-workflow-vs-agent).

**Workflow-shaped tool**  
A tool that fits how the agent actually works instead of copying one API endpoint: `schedule_event` instead of `list_users` + `list_events` + `create_event`, with the joining done inside the tool. Each call removed takes one factor out of the compounding-error product (1.6). Keep these next to the basic tools, not in place of them (Day 3's `get_site_metrics`). See [4.2](weeks/week-04-prompt-and-tool-design.md#42-tool-design-naming-descriptions-parameters).
