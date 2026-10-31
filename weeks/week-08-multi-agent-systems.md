# Week 8 — Multi-agent systems

<!-- toc -->
## Contents

- **[8.1 Orchestrator–worker pattern](#81-orchestratorworker-pattern)**  
  [Idea](#the-idea) · [When to add an agent](#when-to-add-an-agent) · [Example](#an-example) · [Mistakes](#common-mistakes) · [Try it](#try-it) · [Answer](#worked-answer) · [Sources](#sources)
- **[8.2 Handoffs, routing and specialist agents](#82-handoffs-routing-and-specialist-agents)**  
  [Idea](#the-idea-1) · [In the harness](#where-it-lives-in-the-harness) · [Mistakes](#common-mistakes-1) · [Try it](#try-it-1) · [Answer](#worked-answer-1) · [Sources](#sources-1)
- **[8.3 Parallel agents, fan-out and fan-in](#83-parallel-agents-fan-out-and-fan-in)**  
  [Idea](#the-idea-2) · [Example](#an-example-1) · [Mistakes](#common-mistakes-2) · [Try it](#try-it-2) · [Answer](#worked-answer-2) · [Sources](#sources-2)
- **[8.4 Shared state vs message passing](#84-shared-state-vs-message-passing)**  
  [Idea](#the-idea-3) · [In the harness](#where-it-lives-in-the-harness-1) · [Mistakes](#common-mistakes-3) · [Try it](#try-it-3) · [Answer](#worked-answer-3) · [Sources](#sources-3)
- **[8.5 Failure modes of multi-agent systems](#85-failure-modes-of-multi-agent-systems)**  
  [Idea](#the-idea-4) · [Example](#an-example-2) · [Mistakes](#common-mistakes-4) · [Try it](#try-it-4) · [Answer](#worked-answer-4) · [Sources](#sources-4)

<!-- /toc -->

[Week 7](week-07-evaluation-2-and-iteration.md) finished the work on a single agent: weeks 1–7 built it, controlled it and measured it. Sub-agents appeared in [3.6](week-03-state-and-memory.md#36-sub-agents-and-context-isolation), but only as a way to keep a context window clean. This week asks the architecture question: when should work be split across several agent loops, and how do those loops coordinate?

![The six layers of a harness, stacked below the stateless model they wrap: prompts, tools and the executor, loop control, state, guardrails and permissions, feedback and evals.](../diagrams/harness-layers.svg)

*Figure: the six harness layers from [1.4](week-01-what-an-agent-is.md#14-what-a-harness-is). A second agent adds no new layer: a worker is a tool (layer 2) whose executor is a whole loop (layer 3).*

We start with the most common shape, an orchestrator that hands pieces of a task to workers (8.1). Then control moving from one agent to another (8.2), running workers at once and merging what they return (8.3), and how agents share information (8.4). The last lesson puts the week's failure modes into one map (8.5).

The running example is still the nightly investigator for a portfolio of solar sites. This week, six sites get flagged on the same morning.

---

## 8.1 Orchestrator–worker pattern

*Day 51 · 2026-10-26*

> **In short**
> - In the orchestrator–worker pattern, a central model splits a task after it has seen the input, hands the pieces to worker loops, and combines what they return.
> - A second agent earns its keep only for breadth, context pressure or separation. In one large study, every multi-agent variant did worse on the sequential PlanCraft tasks.
> - The orchestrator's harness owns the task spec, the fan-out cap, a budget per worker, aggregation, verification, and a single writer for side effects.

### The idea

Anthropic's [*Building effective agents*](https://www.anthropic.com/engineering/building-effective-agents) defines **orchestrator–workers** as a central LLM that breaks a task down dynamically, delegates the pieces to worker LLMs and synthesises (combines) their results. It was one of the shapes listed in [1.1](week-01-what-an-agent-is.md#11-llm-call-vs-workflow-vs-agent).

The key word is *dynamically*. In the **parallelisation** workflow (also from 1.1), code fixes the subtasks in advance. Here, the orchestrator decides how many workers to start, and what each one does, after it has seen the input.

Mechanically, nothing is new. The orchestrator is the usual agent loop from [1.2](week-01-what-an-agent-is.md#12-the-agent-loop), and one of its tools is `spawn_workers`. Each worker is another loop with:

- its own transcript;
- a restricted set of tools;
- a turn cap;
- an output schema ([2.4](week-02-core-mechanics.md#24-structured-outputs-and-schemas)).

Only the worker's final structured result comes back, as a tool result. In harness terms, a worker is a layer 2 (tools and the executor) tool whose executor is a layer 3 (loop control) loop: the sub-agent of [3.6](week-03-state-and-memory.md#36-sub-agents-and-context-isolation).

What is new is the list of things the orchestrator's harness must own:

- the task spec each worker gets;
- a fan-out limit (how many workers at once);
- a budget per worker;
- aggregation of the results;
- verification of the results;
- a single writer for side effects, so only one agent files tickets or writes memory.

### When to add an agent

A second agent earns its keep when at least one of these holds:

- **Breadth.** The subtasks are independent and can run in parallel. Google Research (Jan 2026) tested 180 configurations: five architectures across three model families. Centralised coordination improved Finance-Agent results by 80.9% over a single agent.
- **Context pressure.** A worker reads far more than it returns: tens of thousands of tokens in, 1–2k out ([3.6](week-03-state-and-memory.md#36-sub-agents-and-context-isolation)).
- **Separation.** The pieces need different tools, permissions or team owners (LangChain).

The evidence against is just as concrete. In the same Google study:

- every multi-agent variant made the sequential PlanCraft tasks worse, by 39–70%;
- coordination overhead grew with the number of tools;
- independent agents amplified errors 17.2×, and centralised ones 4.4×. The orchestrator checking its workers' output is what keeps that number down.

Multi-agent runs also cost about 15× the tokens of a chat (Anthropic). LangChain's rule of thumb: "Add tools before adding agents."

### An example

One morning, six sites are flagged at once. Here is the spec each worker gets, and the orchestrator's tool that starts them:

```python
WORKER_SPEC = """Objective: test {hypotheses} for {scope}.
Window {start}..{end}; baseline {baseline} (do not change).
Tools: metrics, weather(agg=daily), pipeline. Max 6 turns.
Return SiteFinding JSON: scope, hypothesis, verdict,
deciding_value, tool_use_id. Do not file tickets or write memory."""

def spawn_workers(tasks):            # the orchestrator's tool
    assert len(tasks) <= 4           # fan-out cap
    return gather(run_loop(WORKER_ROLE, WORKER_SPEC.format(**t),
                           tools=READ_ONLY, max_turns=6,
                           output_format=SiteFinding)
                  for t in tasks)
```

`spawn_workers` refuses more than four workers. Every worker gets read-only tools, at most six turns, and must return a `SiteFinding`. The spec says what to test, over which window, against which baseline, and what it may not do.

The orchestrator's trace:

- **T1:** pulls aggregate metrics for all six sites, and sees that five of them share weather-station cluster W2.
- **T2:** spawns two workers. One checks the fleet-level W2 weather feed. The other checks PVA-03 alone, since it is not on W2.
- **T3:** checks each returned `deciding_value` against the tool result named by its `tool_use_id` (the provenance check from [5.3](week-05-control-safety-reliability.md#53-guardrails-inputoutput-validation-policy-checks-classifiers)).
- **T4:** files one fleet ticket (feed outage, 5 sites) and one PVA-03 meter ticket.

![A flowchart: six sites flagged; the orchestrator reads aggregate metrics and spawns two read-only workers with six turns each, one for the W2 feed and one for PVA-03 alone; both return a SiteFinding; the orchestrator checks provenance, then files the tickets as the only writer.](../diagrams/orchestrator-workers.svg)

*Figure: the orchestrator chose two workers after seeing the input; workers only read and return typed findings, and only the orchestrator writes.*

The split depended on the input, and that is what an orchestrator buys. If every morning were simply "one worker per site", code could do the fan-out: a parallelisation workflow with no orchestrator model call at all.

### Common mistakes

Anthropic's early lead agents "spawned 50 subagents for simple queries" and duplicated each other's work ([3.6](week-03-state-and-memory.md#36-sub-agents-and-context-isolation)). Both fixes were harness changes:

- Every worker task carries an objective, an output format, guidance on tools and sources, and clear boundaries.
- The prompt states effort-scaling rules: 1 agent with 3–10 tool calls for simple fact-finding, 2–4 subagents for comparisons, and more than 10 only for complex research.

Other common mistakes:

- letting workers write;
- trusting worker summaries without checking them;
- running workers synchronously, so the whole run waits on the slowest one.

### Try it

*10–15 min.* Fake fixture: 6 sites flagged. PVA-01, -02, -04, -05 and -06 share a W2 weather-feed outage; PVA-03 has a meter fault. The expected output is one fleet feed ticket plus one PVA-03 meter ticket.

1. Write `WORKER_SPEC` and a `SiteFinding` Pydantic model.
2. Run three variants. For each, record the total tokens (orchestrator plus workers), the wall-clock time, and whether the tickets are correct:
   - **A:** a single agent with a 20-turn cap;
   - **B:** the orchestrator with `spawn_workers`;
   - **C:** B with the spec cut to "investigate site X", forced to one worker per site.
3. In C, count how many workers re-check the W2 feed independently, and how many tickets it files.
4. One paragraph: is the nightly queue from the [5.6](week-05-control-safety-reliability.md#56-latency-and-cost-budgets-parallel-tool-calls-streaming) worked answer (8 workers over 40 sites) an orchestrator–worker system or a parallelisation workflow? And what single input would make a real orchestrator earn its keep there?

### Worked answer

**(1) The spec and the schema.** `WORKER_SPEC` holds:

- the objective ("test hypothesis H for scope S");
- a fixed window and baseline;
- the allowed read-only tools;
- `max_turns` 6;
- "do not file tickets or write memory; return only a `SiteFinding`".

```python
SiteFinding(scope: Literal["site", "cluster"], hypothesis: Enum,
            verdict: confirmed | rejected | untested,
            deciding_value: float | None, tool_use_id: str)
```

**(2) The three variants** (illustrative results).

- **A, a single agent.** Works through the sites one by one, and usually spots the shared W2 feed after 3–4 of them. It uses 14–18 turns, about 200k input tokens and the longest wall-clock time. On runs where it misses the pattern, it files five separate weather tickets.
- **B, the orchestrator.** T1 pulls aggregates for all six sites and sees the W2 cluster. It then spawns two workers: the W2 feed check and PVA-03 alone. It uses about 120–150k tokens across orchestrator and workers, the workers run in parallel, and it files the right tickets: 1 feed ticket and 1 meter ticket.

**(3) C, one worker per site with a cut spec.** All five W2 workers re-check the same feed. That costs the most tokens (250k+), and the orchestrator files five duplicate feed tickets unless it dedupes by scope.

**(4) The nightly queue** is a parallelisation workflow, because code fixes the split at one worker per site. A real orchestrator earns its keep when the input reveals cross-site structure: a fleet-level view (station clusters, shared feeds) that changes how the work should be split.

Typical slips: counting only the orchestrator's token usage, and giving workers `ticket_draft`.

### Sources

- [Google Research — Towards a science of scaling agent systems (Jan 2026)](https://research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work/)
- [LangChain — Choosing the right multi-agent architecture (Jan 2026)](https://www.langchain.com/blog/choosing-the-right-multi-agent-architecture)
- [Anthropic — How we built our multi-agent research system (Jun 2025)](https://www.anthropic.com/engineering/multi-agent-research-system)

---

In 8.1 the orchestrator kept control and got results back. The next lesson lets control itself move between agents.

[↑ Contents](#contents)

## 8.2 Handoffs, routing and specialist agents

*Day 52 · 2026-10-27*

> **In short**
> - There are three ways to bring in a specialist, and they differ in who holds control afterwards: an agent called as a tool (control comes back), routing (one choice, made up front) and a handoff (control moves on).
> - A handoff is a tool that does no work: it only changes which prompt and tools the loop uses next, so "which agent is active" is state you must checkpoint.
> - Hand off a typed payload with the evidence, plus filtered history. Cap handoffs, and gate handoffs to agents that can write.

### The idea

There are three ways to bring in a specialist agent. They differ in who holds control afterwards.

- **Agent as tool** (8.1). The parent calls the child, the child returns, and the parent carries on. Control comes back.
- **Routing.** A classification step runs before any agent and sends the request to one or more specialists. The classifier can be code, one structured-output call that returns an enum ([2.4](week-02-core-mechanics.md#24-structured-outputs-and-schemas)), or an embedding match. Routing is a workflow ([1.1](week-01-what-an-agent-is.md#11-llm-call-vs-workflow-vs-agent)): the graph is drawn in advance, and only the choice of branch is learned. LangChain's router is usually stateless per request: classify, call zero or more specialists in parallel, then synthesise.
- **Handoff.** The active agent decides partway through the run that another agent should take over. The run continues under the new agent's system prompt and tools. Control does not come back unless someone hands it back. The OpenAI Agents SDK shows each handoff to the model as a tool named after the target agent. In LangGraph, a tool returns a command that jumps to another agent in the parent graph.

![Three small flows. Agent as tool: parent calls child, child returns a result, parent continues. Routing: request goes to a classifier, then to one or more specialists, then to a synthesis step. Handoff: the active agent transfers, and the new agent takes over the conversation.](../diagrams/specialist-control.svg)

*Figure: control comes back (agent as tool), is decided once up front (routing), or moves on (handoff).*

Mechanically, a handoff is a tool whose executor does no work. It only changes which configuration the loop uses on the next call:

```python
while turn < cap:
    a = AGENTS[st.active]                 # prompt + tools for this turn
    resp = call(a.system, a.tools, history_for(st.active, st.messages))
    for b in tool_uses(resp):
        if b.name.startswith("transfer_to_"):
            p = HandoffInput(**b.input)   # site, window, reason, evidence
            results.append(tool_result(b.id, f"Handed to {b.name[12:]}"))
            st.active = b.name[12:]
            st.handoffs += 1
        else:
            results.append(execute(b))
    save(st)                              # the active agent is state
```

Each turn, the loop looks up the active agent's prompt and tools. A `transfer_to_…` call gets a short tool result, and the next turn runs as the named agent (`b.name[12:]` drops the 12-character `transfer_to_` prefix). Every other call runs as usual.

**API details**

| What | Value |
|---|---|
| Handoff tool name (OpenAI Agents SDK) | `transfer_to_<agent_name>` |
| Handoff from a tool (LangGraph) | the tool returns `Command(goto=agent, update=…, graph=Command.PARENT)` |

### Where it lives in the harness

- **Layer 3 (loop control):** the active agent decides the prompt and tools on every call.
- **Layer 4 (state):** the active agent and the history policy must be checkpointed ([3.5](week-03-state-and-memory.md#35-checkpointing-and-resumability)). LangGraph's swarm remembers the last active agent, so the next turn resumes with it.
- **Layer 2 (tools and the executor):** the handoff tools' descriptions are your routing policy.
- **Layer 5 (guardrails and permissions):** a handoff can be a privilege change, if the receiving agent holds write tools.

**The history decision.** By default, both the OpenAI SDK and LangGraph give the receiving agent the full shared history. There are three alternatives:

- **Filtered:** a filter strips the tool calls and tool results.
- **Collapsed:** an option (in beta, off by default) summarises earlier turns into one history block.
- **Task-only:** the receiver gets just a task message.

Full history means the receiver sees calls to tools it doesn't have, plus a predecessor's reasoning it may anchor on. Task-only history loses facts unless the payload carries them.

The practical rule: send a **typed payload** plus filtered history. The payload holds the site, the window, the deciding numbers with their `tool_use_id`s, and the hypotheses already rejected. It is 8.1's "the spec is the interface" again, because the receiver cannot ask the sender anything.

**Cost.** LangChain counted model calls per scenario for both patterns:

| Scenario | Handoffs | Router |
|---|---|---|
| One-shot request | 3 calls | 3 calls |
| Repeat turn | 2 calls (the specialist is still active) | 3 calls |
| Multi-domain question | 7+ calls, ~14k tokens (handoffs run one after another) | 5 calls, ~9k tokens (run in parallel) |

So handoffs fit staged, multi-turn conversations, and routers fit independent questions across several domains. Every handoff also swaps the system prompt and tools, which breaks the prompt cache ([4.6](week-04-prompt-and-tool-design.md#46-prompt-caching-and-cost)).

**API details**

| What | Value |
|---|---|
| Filtered history (OpenAI Agents SDK) | `handoff_filters.remove_all_tools` |
| Collapsed history (OpenAI Agents SDK) | `nest_handoff_history` (beta, off by default); earlier turns go into a `<CONVERSATION HISTORY>` block |
| Task-only handoff (LangGraph) | `Send` with just a task message |

### Common mistakes

- **Ping-pong** (A→B→A). Cap handoffs per run, and feed them to the stuck detector ([2.5](week-02-core-mechanics.md#25-stopping-conditions-step-budgets-and-loop-detection)).
- **Handing off without the evidence.** The receiver redoes the work.
- **A router with no "unknown" class.** It is forced to misroute. Log the misroute rate as an eval metric.
- **Relying on the SDK's enable check alone.** The OpenAI SDK evaluates it *before* the model fills in the handoff's arguments, so validate the payload in the executor.
- **Ungated handoffs to write-capable agents.** Treat them as permission escalations, and gate them like any side effect ([5.2](week-05-control-safety-reliability.md#52-human-in-the-loop-approval-gates-interrupts-escalation)).

**API details**

| What | Value |
|---|---|
| Per-handoff enable check (OpenAI Agents SDK) | `is_enabled` |

### Try it

Build a three-agent "morning ops" front end:

- `triage`: read-only metrics, plus the tools `transfer_to_feed_specialist` and `transfer_to_site_specialist`;
- `feed_specialist`: the weather and pipeline tools, plus `ticket_draft`;
- `site_specialist`: the series viewer, the curtailment tool and `ticket_draft`.

The payload is `HandoffInput(site, window, reason, evidence: list[{metric, value, tool_use_id}])`. Then:

1. Implement the active-agent loop with a handoff cap of 3, and store the active agent in the checkpoint.
2. Run the six-site fixture from [8.1](#81-orchestratorworker-pattern) and a PVA-03 curtailment case under three history policies: full, remove-tools, and payload-only. Record:
   - turns per agent;
   - total input tokens;
   - whether the specialist re-pulls metrics that triage already had;
   - whether the tickets are correct.
3. Plant an ambiguous case: PVA-04 with both a W2 null burst and a 40% curtailment cap. Count the handoffs and check for ping-pong.
4. One paragraph: should the nightly batch use a router (code or LLM) or handoffs? And what single change would you make to the 8.1 orchestrator instead?

### Worked answer

**(1) The loop.** Each turn loads `AGENTS[st.active]` (system prompt and tools). A `transfer_to_X` call is validated in the executor:

- Is the site on the allow-list?
- Do the evidence `tool_use_id`s exist in this run?

If so, the executor appends the tool result "Transferred to X", sets `st.active = X`, increments `st.handoffs`, applies the history policy and saves the checkpoint. A fourth handoff ends the run with status `stuck`.

**(2) History policies** (illustrative).

- **Full history.** Specialists rarely re-pull metrics. But each handoff re-sends the whole transcript under a new system prompt, which breaks the cache and makes this the most expensive policy.
- **Remove-tools filter.** The metrics results disappear. Without evidence in the payload, the specialist re-pulls them on most runs.
- **Payload-only, with typed evidence.** The cheapest policy, and re-pulls are rare.

All three file the PVA-03 curtailment ticket correctly. Handoffs fit the six-site fixture badly: control moves one agent at a time, so the five W2 sites are investigated one after another, and duplicate feed tickets are likely.

**(3) The ambiguous PVA-04.** The feed specialist sees the 40% cap and hands back. Triage then hands off to the site specialist, and the run ping-pongs for 2–3 handoffs, hitting the cap on some runs.

**(4) The nightly batch.** Use a *code* router: feed and curtailment flags are rules. The single change to the 8.1 orchestrator is a specialist enum on `spawn_workers`. Each worker then gets a specialist's prompt and tools, while the orchestrator stays the only writer.

Typical slip: using handoffs for work that is really parallel. That is the next lesson.

### Sources

- [OpenAI Agents SDK — Handoffs](https://openai.github.io/openai-agents-python/handoffs/)
- [LangChain docs — Custom multi-agent (handoffs with Command, Send)](https://docs.langchain.com/oss/python/multi-agent-custom)
- [LangChain — Choosing the right multi-agent architecture (Jan 2026)](https://www.langchain.com/blog/choosing-the-right-multi-agent-architecture)

---

8.1 gave the orchestrator a `spawn_workers` tool, and 8.2 moved control between agents. Next is the step after `spawn_workers`: running the workers at once and merging what comes back. Most multi-agent bugs this week live in that merge step.

[↑ Contents](#contents)

## 8.3 Parallel agents, fan-out and fan-in

*Day 53 · 2026-10-28*

> **In short**
> - Fan-out starts several independent branches from one state; fan-in waits for them and merges their outputs into one state.
> - Parallelism buys wall-clock time, not accuracy. Accuracy is decided at fan-in.
> - Merge typed findings in code: a deadline per branch, a provenance check, a stable sort, a quorum where it applies, and escalation for real conflicts.

### The idea

**Fan-out** creates N independent branches from one state. **Fan-in** is a barrier: it waits for the branches and merges their outputs into one state. Either code or the model can decide the split.

- **Code fan-out** (a parallelisation workflow). Run a fixed set of agents concurrently, or have a LangGraph conditional edge return one task message per item. OpenAI's cookbook contrasts this with agents called as tools. Code fan-out gives lower latency and a deterministic order. A planner agent picks the branches dynamically, but adds a planning call and a longer context.
- **Model fan-out.** The orchestrator emits several worker tool calls in one message, and the `run_tools` executor from [5.6](week-05-control-safety-reliability.md#56-latency-and-cost-budgets-parallel-tool-calls-streaming) runs them concurrently. Anthropic's lead agent starts 3–5 subagents in parallel. This kind of parallelism cut research time "by up to 90%" on complex queries.

**API details**

| What | Value |
|---|---|
| Fixed fan-out in Python | `asyncio.gather` over the agents |
| Fan-out from a conditional edge (LangGraph) | return `[Send("worker", {...}) for x in items]` |

Fan-out is the easy half. Fan-in forces four decisions, and they live in layers 3 (loop control) and 4 (state).

**1. A merge rule for shared keys.** When parallel branches write the same key, you need a **reducer**: a function that says how two writes combine (for example, append both to a list). Without one, the last write wins. LangGraph's docs warn that updates from a parallel step "may not be ordered consistently", so sort by a stable key before merging. Reproducibility depends on it, and so does your prompt cache ([4.6](week-04-prompt-and-tool-design.md#46-prompt-caching-and-cost)).

**2. Partial failure.** A LangGraph superstep (one round of parallel branches) is transactional: if one branch fails, "none of the updates are applied". With a checkpointer, the successful branches are saved and are not re-run on resume. That suits correctness. For an investigation, though, a missing branch usually means "untested", not "abort". So choose a policy for each task: all-or-nothing, a quorum, or partial results with flags.

**3. Barrier and deadline.** A synchronous join waits for the slowest worker. Anthropic notes the whole system "can be blocked while waiting for a single subagent". Give each branch a deadline, and turn a timeout into a typed `untested` result. Cap concurrency too, on top of the 8.1 fan-out cap.

**4. Conflict resolution.** Workers will duplicate and contradict each other. Merge typed findings in code:

- group them by (scope, hypothesis);
- drop claims that fail provenance ([5.3](week-05-control-safety-reliability.md#53-guardrails-inputoutput-validation-policy-checks-classifiers));
- take a quorum (a minimum number of agreeing workers) where it applies;
- escalate real contradictions, rather than letting a model pick the more fluent one.

For large outputs, Anthropic's artifact pattern applies: workers write to storage and return references. That avoids the "game of telephone", where each retelling loses detail.

**API details**

| What | Value |
|---|---|
| Reducer for a list key (LangGraph) | `Annotated[list, operator.add]` |
| Concurrency cap (LangGraph) | `max_concurrency` |

### An example

Here is a fan-in for the six-site fixture from 8.1:

```python
done, late = await asyncio.wait(tasks, timeout=deadline)
results = [t.result() for t in done] + [Untested(t.spec, "timeout") for t in late]
ok = [f for f in results if isinstance(f, SiteFinding) and provenance_ok(f)]
groups = group_by(sorted(ok, key=key), key=lambda f: (f.scope_id, f.hypothesis))
for g, fs in groups:
    verdicts = {f.verdict for f in fs}
    if len(verdicts) > 1:
        escalate(g, fs)              # conflict: never resolved by prose
w2 = [f for f in ok if f.cluster == "W2" and f.verdict == "confirmed"]
fleet_ticket = len(w2) >= 3          # quorum: 3 of 5 W2 sites
```

Late branches become `Untested` results, never verdicts. Findings that fail provenance are dropped. The rest are sorted, grouped and checked for conflicts, and the fleet ticket needs 3 of the 5 W2 sites to confirm.

One timed-out W2 worker leaves 4 of 5 confirmations. So the quorum still files a single fleet ticket, and the review card lists the missing site as untested.

![A flowchart: workers fan out under a concurrency cap. A branch not done by its deadline becomes untested; a claim whose value is not in its own tool results is dropped; the rest are sorted and grouped by scope and hypothesis. Disagreeing verdicts are escalated, agreeing ones go to a quorum per scope. All four outcomes land in one MergeResult.](../diagrams/fan-in-merge.svg)

*Figure: every branch ends up in the merge result, as a verdict, an untested scope, a dropped claim or an escalated conflict.*

### Common mistakes

Parallelism buys wall-clock time, not accuracy. Accuracy is decided at fan-in. Typical mistakes:

- concatenating worker prose and asking a model to "summarise", which loses provenance and lets one confident hallucination dominate;
- no reducer, so findings silently overwrite each other;
- treating a timeout as a negative verdict. That is category A from [7.2](week-07-evaluation-2-and-iteration.md#72-error-taxonomies-and-common-failure-modes), "tool failure absorbed silently", in a new place;
- merge output that depends on the order in which workers finish.

### Try it

*10–15 min.* Write `fan_out(specs, deadline)` and `fan_in(results) -> MergeResult`, with fake workers.

Fixture:

- Five W2 site workers. Four return feed *confirmed*, with null rates of 28, 31, 33 and 34% (each value present in that worker's tool results). The fifth sleeps past the deadline.
- A PVA-03 worker returns meter *confirmed*.
- A duplicate PVA-03 worker returns weather *confirmed*, with a deciding value of 38 that none of its tools returned.

Tasks:

1. Implement the per-branch timeout. Make `MergeResult` report tickets, untested scopes, conflicts and dropped claims.
2. Run it 5 times with a randomised completion order, and assert that the `MergeResult` JSON is byte-identical.
3. Change the quorum to 4 of 5 and to 5 of 5, and note what gets filed.
4. One paragraph: should the 40-site nightly batch use LangGraph-style transactional fan-in or partial-with-flags? What goes on the review card for a site whose worker died?

### Worked answer

**`fan_out`.** Use `asyncio.wait(tasks, timeout=deadline)`. Any task still pending is cancelled and becomes `Untested(spec, "timeout")`. A late branch is never a verdict.

**`fan_in`** runs in a fixed order:

1. **Provenance.** Drop any claim whose deciding value is not in that worker's own tool results. The duplicate PVA-03 "weather 38" goes into `dropped`.
2. **Group** by (scope, hypothesis).
3. **Quorum**, applied per scope.
4. **Conflicts.** One scope with two surviving, conflicting hypotheses goes into `conflicts` and is escalated.

Sort every list by (scope, hypothesis, site), and serialise with `sort_keys=True`. After that, five randomised completion orders give byte-identical JSON. Without the sort, they don't.

**Quorum.**

- **3 of 5 or 4 of 5:** four confirmations (28–34% nulls) give one fleet W2 feed ticket, with the fifth site listed as untested.
- **5 of 5:** the quorum is missed. No fleet ticket; the scope is "untested (1 timeout)" and is escalated. A single dead worker blocks the whole fleet finding, so pick the quorum from what the domain needs, not from caution.

The PVA-03 meter ticket is filed in every variant.

**The nightly batch:** partial-with-flags. Transactional fan-in would throw away 39 good sites because one died. The review card for the dead site shows:

- status untested (timeout at 15 min);
- which hypotheses were tested before it died;
- the trace link;
- "re-queued for second pass".

Common slips: sorting after the merge instead of before it, and counting the timed-out site as a "no".

### Sources

- [LangGraph docs — Graph API (parallel branches, reducers, transactional supersteps, defer, Send, max_concurrency)](https://docs.langchain.com/oss/python/langgraph/use-graph-api)
- [OpenAI Cookbook — Running specialized agents in parallel with the Agents SDK (May 2025, archived)](https://developers.openai.com/cookbook/examples/agents_sdk/parallel_agents)
- [Anthropic Engineering — How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)

---

The fan-in in 8.3 merged worker outputs that arrived as messages (tool results). The next lesson asks the question underneath: should agents talk only through messages, or read and write a common store?

[↑ Contents](#contents)

## 8.4 Shared state vs message passing

*Day 54 · 2026-10-29*

> **In short**
> - Agents share information either by message passing (private state, explicit messages) or through shared state (one store that every agent reads and writes).
> - Shared state avoids the "game of telephone" but costs context, risks write conflicts and makes agents' errors correlated; messages keep agents isolated but lose detail.
> - Production systems mix the two. Share facts, not reasoning; share by reference, not by copying; give every key one writer or a reducer.

### The idea

Agents can share information in two ways.

**Message passing.** Each agent keeps private state: its own transcript and notes. Information moves only in explicit, addressed messages. AutoGen Core makes this the whole design: "messages are the only means through which agents can communicate with each other". It offers two kinds:

- direct request and response, which works like a function call;
- one-way publish and subscribe, on topics.

You already know a version of this. An orchestrator's worker spec going down, and a typed `SiteFinding` coming back as a tool result (8.1), is message passing.

**Shared state.** Agents read and write one common store. In LangGraph's simplest multi-agent graph, all agents append to one list of messages. LangChain calls this a "shared scratchpad": "other agents can see all the individual steps", but it is "sometimes overly verbose".

The classic AI version is the **blackboard**. In Google's 2025 blackboard system, a main agent posts requests to a board without naming who should answer, and helper agents volunteer. Across three data-discovery benchmarks, it beat a master–slave (direct-assignment) baseline: 28.5% vs 24.0% macro with Gemini 2.5 Pro, at about 1.8× the cost.

One detail matters. Helpers write their answers to a separate response board that only the main agent reads, "so helpers do not influence each other". The design shares requests, but deliberately keeps answers private.

**API details**

| What | Value |
|---|---|
| Direct request/response (AutoGen Core) | `send_message` |

That detail is the main trade-off. Shared state avoids the "game of telephone", where each hand-off summarises the facts away, and it lets agents see work that is already done. It costs three things:

- **Context bloat.** Every agent pays for everyone's steps.
- **Write conflicts.** Two agents update one key (the reducers from [8.3](#83-parallel-agents-fan-out-and-fan-in)).
- **Lost independence.** Agents read each other's guesses, so their errors become correlated. And an injected instruction in one place ([5.4](week-05-control-safety-reliability.md#54-prompt-injection-and-untrusted-content)) reaches every reader.

Message passing gives isolation, a typed contract and a clean trace. In exchange it is lossy, and the sender has to predict what the receiver needs.

### Where it lives in the harness

This is layer 4 (state): where state lives and who sees it. Layer 5 (guardrails and permissions) decides who may write.

Production systems mix the two. Anthropic's research system has subagents write large outputs to a filesystem and pass back "lightweight references". So you get private transcripts, typed messages, and a shared store for artifacts. Three rules make the mix safe:

```python
board = AppendOnlyStore("runs/2026-10-29/board.jsonl")

# workers: append facts only, each with provenance
board.append(Finding(scope="W2", hyp="feed", verdict="confirmed",
                     value=0.31, author="w-PVA04", tool_use_id="tu_17"))

# workers may READ facts in their scope, never others' reasoning
peers = board.query(scope="W2", fields=FACT_FIELDS)

# single writer: only the orchestrator writes verdicts and tickets
assert caller == "orchestrator" or key not in {"verdicts", "tickets"}
```

Workers can only append facts, each tied to the tool call that produced it. They can read facts in their own scope, but not each other's reasoning. Only the orchestrator writes verdicts and tickets.

![A flowchart: worker A appends a fact with its tool_use_id to an append-only board of facts and references; worker B reads facts in its scope from the board; both workers send typed findings to the orchestrator, the only writer, which produces the verdicts and tickets.](../diagrams/shared-board.svg)

*Figure: a mixed design. Workers share facts on an append-only board and keep their reasoning private; only the orchestrator writes verdicts and tickets.*

The rules in one line: share facts, not reasoning. Share by reference, not by copying. Give every key exactly one writer, or a reducer.

### Common mistakes

Most multi-agent "coordination" bugs come down to a state decision nobody made. The usual mistakes:

- one shared message list by default: bloat, and children anchor on the parent's hunches;
- a shared store with several writers per key and no reducer: the last write wins, silently;
- typed messages so thin that the receiver re-pulls the data (the handoff problem from [8.2](#82-handoffs-routing-and-specialist-agents));
- treating anything on a shared board as trusted. A worker that read a forged document can post it to every reader.

### Try it

*10–15 min.* Use the six-site fixture from 8.1, and add one planted fault: the PVA-01 worker finishes first and wrongly posts "W2 feed OK, nulls 2%".

1. **Message passing:** workers return `SiteFinding` only to the orchestrator.
2. **Blackboard:** workers append to `board.jsonl`, and may read W2 rows before they finish. Run each variant 5× and record:
   - total tokens;
   - how many W2 workers stop early because the board already has a cluster finding;
   - how many copy the false "OK".
3. Add a provenance rule for reads: a peer row counts only if its value matches the cited `tool_use_id`. Re-run.
4. One paragraph: in the nightly batch state (findings, verdicts, notes, memory, tickets, the done set), which keys need a single writer, and which can take an append-only reducer?

### Worked answer

**(1) Message passing.** Every W2 worker returns its `SiteFinding` only to the orchestrator. The false PVA-01 "W2 OK, nulls 2%" is one finding out of five. The other four still report nulls of 28–34%. So a 3-of-5 quorum files the fleet feed ticket, and the card lists PVA-01 as a dissent. No worker stops early, which makes this the most expensive variant (five full feed checks).

**(2) Blackboard with no read checks** (illustrative). PVA-01 posts first. On a typical run, 2–4 of the other four workers read "W2 OK" and skip the feed check. Tokens fall by roughly 30–40%, the quorum fails, and no fleet ticket is filed. The run is cheaper and wrong: one error copied into several workers.

**(3) Read provenance** stops a forged or hallucinated 2%. It does not stop a 2% that PVA-01's tool really returned from a faulty station. Provenance proves where a value came from, not that it is true. So add a **quorum on read**: a worker may skip its own check only after at least 2 independent authors agree.

**(4) Writers.**

- **Single writer (the orchestrator only):** verdicts, tickets, the done set, memory, the checkpoint.
- **Append-only reducer:** board findings keyed by (author, `tool_use_id`), and trace events.

Slip: treating the first row on the board as a verdict.

### Sources

- [Salemi et al. (Google) — LLM-Based Multi-Agent Blackboard System for Information Discovery in Data Science (Oct 2025)](https://arxiv.org/abs/2510.01285)
- [AutoGen Core — Message and Communication](https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/framework/message-and-communication.html)
- [LangChain — LangGraph: Multi-Agent Workflows (Jan 2024)](https://www.langchain.com/blog/langgraph-multi-agent-workflows)

---

Week 8 has now built the parts: orchestrators (8.1), handoffs (8.2), fan-in (8.3) and the state channel between agents (8.4). Each lesson listed its own common mistakes. The last lesson puts them into one map, so you can read a multi-agent trace ([7.1](week-07-evaluation-2-and-iteration.md#71-reading-a-transcript)) with the right categories in hand.

[↑ Contents](#contents)

## 8.5 Failure modes of multi-agent systems

*Day 55 · 2026-10-30*

> **In short**
> - A multi-agent system fails in every way a single agent does, and also along its edges: the messages between agents.
> - Edge failures fall into four families: specification and communication, coordination, cost, and error cascades.
> - Log lineage (author, parent message, `tool_use_id`) for every claim, or you will blame the worker model for failures that come from the spec or the merge.

### The idea

A multi-agent system fails in every way a single agent fails. It also fails along its edges, and each edge is a message between agents. There are four families of edge failure.

**1. Specification and communication** (layers 1 prompts, 2 tools and the executor, and 4 state). MAST coded 200+ traces from 7 frameworks: specification issues were 41.8% and inter-agent misalignment 36.9% ([7.2](week-07-evaluation-2-and-iteration.md#72-error-taxonomies-and-common-failure-modes)). Cognition reached the same conclusion in production (Apr 2026): "The open problems are all communication problems." Their examples:

- managers that are too prescriptive, because they lack the codebase context;
- "agents assume they share state with their children when they don't";
- children that never report discoveries that should change a sibling's work.

Fix: a typed spec going down, a typed finding coming back, and an explicit discoveries field.

**2. Coordination** (layers 3 loop control and 4 state). This family covers:

- duplicated work (variant C in [8.1](#81-orchestratorworker-pattern));
- conflicting writes (Cognition: parallel writers make "conflicting implicit choices");
- handoff ping-pong ([8.2](#82-handoffs-routing-and-specialist-agents));
- a fan-in stalled by one slow worker ([8.3](#83-parallel-agents-fan-out-and-fan-in));
- premature or missing verification (MAST: 21.3%).

Fixes from this week: one writer per key or a reducer, handoff caps, per-branch deadlines, and verification in code.

**3. Cost** (layer 3, loop control). A multi-agent run costs about 15× a chat in tokens (Anthropic). Coordination overhead grows with the number of tools. On sequential tasks, every multi-agent variant lost 39–70% (Google, Jan 2026). And the gains shrink as the single-agent baseline gets stronger. A stuck worker burns its whole budget, and so does each of the N copies you fanned out. Fix: a run-level budget that counts children, not only per-worker caps.

**4. Error compounding and cascades** (layer 5, guardrails and permissions). Independent agents amplified errors 17.2×; a central orchestrator that checks worker output cut this to 4.4× (Google).

Xie et al. ("From Spark to Fire", 2026) model a collaboration as a directed graph of who depends on whom. Across six frameworks they found three weaknesses: cascade amplification, topological sensitivity (results depend on how the agents are connected) and consensus inertia (a false agreement, once formed, is hard to undo). A single injected "atomic error seed" could spread into a system-wide false consensus.

Their fix is a plugin at the message layer that keeps a **genealogy graph**: a record of which messages each claim came from. It prevented final infection in at least 89% of runs. In this course's terms, that is the provenance of [5.3](week-05-control-safety-reliability.md#53-guardrails-inputoutput-validation-policy-checks-classifiers), extended from "which tool produced this number" to "which chain of messages carried it here".

![Four rows, one per failure family. Specification and communication: a spec or report misses what the other agent needs; fix with a typed spec, a typed finding and a discoveries field. Coordination: duplicates, clashes, stalls and ping-pong; fix with one writer per key, caps and deadlines. Cost: tokens multiply across children; fix with a run budget that counts children. Error cascades: one error spreads to a false consensus; fix with lineage for every claim.](../diagrams/multi-agent-failure-families.svg)

*Figure: the four families of edge failure, each with the harness fix from this week.*

### An example

The nightly fleet run files five weather tickets and nothing for PVA-03. Reading the trace, each symptom maps to a family and a detector (a check you can run over the trace):

| Detector | What it counts | Family |
|---|---|---|
| `duplicate_scope` | More than one finding or ticket with the same (scope, hypothesis) from different workers | 1: the decomposition never assigned the W2 cluster as one scope |
| `orphan_claim` | A cited value with no tool-result ancestor in its lineage | 4: an error seed |
| `copy_rate` | The share of findings whose only evidence is another agent's finding | 4: consensus inertia |
| `child_cost_share` | Child tokens ÷ total tokens | 3 |
| `untested_rate` | The share of branches that timed out | 3 |

In this run, PVA-03's worker hit its deadline (untested), and five W2 workers each filed a ticket because nothing deduplicated by scope. Two harness bugs, no model bug.

### Common mistakes

In multi-agent traces, blame is hard to place. On Who&When, the best automated method finds the responsible agent 53.5% of the time, and the decisive step only 14.2% ([7.1](week-07-evaluation-2-and-iteration.md#71-reading-a-transcript)). Unless the harness logs lineage (author, parent message, `tool_use_id`), you will blame "the worker model" for failures that come from the spec or the merge.

Two more mistakes:

- judging only accuracy while cost multiplies;
- patching a cascade by adding a verifier agent that reads prose. That verifier is just one more node the error can reach.

### Try it

Take the six-site fixture from 8.1 and plant one error seed: the PVA-01 worker reports "W2 nulls 2%". Run three topologies 5× each:

- **(A)** independent workers whose findings are concatenated with no check;
- **(B)** an orchestrator with provenance and a 3-of-5 quorum at fan-in;
- **(C)** the blackboard from [8.4](#84-shared-state-vs-message-passing), with no read checks.

Give every finding a `parents` list (`tool_use_id`s or finding ids). For each topology, report:

- the **infection rate**: the share of final verdicts whose lineage reaches the seed;
- total tokens;
- the detector values from the table above.

Then answer in one paragraph: which single detector would you add to `monitor()` ([7.4](week-07-evaluation-2-and-iteration.md#74-online-evaluation-and-monitoring)) first, and what alert threshold would you set?

### Worked answer

*Answer coming in the next brief.*

### Sources

- [Cemri et al. — Why Do Multi-Agent LLM Systems Fail? (MAST, NeurIPS 2025)](https://arxiv.org/abs/2503.13657)
- [Xie et al. — From Spark to Fire: Modeling and Mitigating Error Cascades in LLM-Based Multi-Agent Collaboration (2026)](https://arxiv.org/abs/2603.04474)
- [Cognition — Multi-Agents: What's Actually Working (Apr 2026)](https://cognition.com/blog/multi-agents-working)

---

*Week 8 review coming soon.*
