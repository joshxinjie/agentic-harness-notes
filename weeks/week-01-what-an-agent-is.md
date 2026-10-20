# Week 1 — What an agent is

This first week pins down what an "agent" actually is, so that "harness engineering" has a clear object for the rest of the course. (The harness is all the ordinary code and text around the model; [1.4](#14-what-a-harness-is) defines it properly.)

- We start by treating "agent" as a setting on a dial rather than a marketing word (1.1).
- Then we open up the loop that makes an agent run (1.2) and the tool-calling handshake inside it (1.3).
- Next we name everything around the model — the harness — and split it into six layers (1.4).
- We read one complete, working agent line by line (1.5).
- We finish by asking when you should not build an agent at all (1.6).

The week ends with a review, a self-quiz and an exercise that becomes the seed of the capstone.

---

## 1.1 LLM call vs workflow vs agent

*Day 1 · 2026-09-03*

> **In short**
> - A single model call, a workflow and an agent sit on one dial: "agentic" is a matter of degree.
> - The dial is set by how much of the control flow your code decides and how much it hands to the model.
> - Autonomy is a cost, not a feature: add agent behaviour only when you cannot predict the steps up front.

### The idea

Start with what you know: a **single LLM call**. Prompt in, text out, no side effects (no changes to anything outside the call). You control everything: what the model sees, how many times it runs, what happens to the answer. The model has no say over control flow (the order in which steps happen).

Now add three things to that call:

- tools it can ask for, through a function-calling API (an API that lets the model request a named function with arguments);
- retrieval it can trigger (fetching documents into the prompt);
- some memory it can read and write.

Anthropic calls this the **augmented LLM**. It is the basic building block for everything that follows. Note that control flow has not changed yet. The model can *ask* for a web search; your code decides whether to run it.

From here you can go two ways. Anthropic's "Building effective agents" post draws the line:

> Workflows are systems where LLMs and tools are orchestrated through predefined code paths. Agents are systems where LLMs dynamically direct their own processes and tool usage.

In a **workflow**, your code owns the graph of steps. The classic shapes are:

- **Prompt chaining** — the output of call A feeds call B.
- **Routing** — a classifier call picks which branch runs.
- **Parallelisation** — several calls run at once, then you merge the results or take a vote.
- **Orchestrator–workers** — one call splits the task, other calls do the pieces.
- **Evaluator–optimiser** — one call produces, another critiques, and you loop until it is good.

Each shape is still fixed in structure. You can draw the boxes and arrows before any model runs. The model only fills in the boxes.

In an **agent**, the model owns the graph. Simon Willison's one-liner, which the field has largely settled on, is: "An LLM agent runs tools in a loop to achieve a goal."

Running the loop is the harness's job: call the model; if it asked for a tool, run the tool and add the result; repeat until the model stops asking. Which tools, in what order, and how many rounds are decided at run time by the model, based on what it currently sees in its context (everything it is sent on that call).

![A vertical dial: a single LLM call, then the augmented LLM with tools, retrieval and memory, then a workflow where code owns the path, then an agent where the model owns the path; the agent gains steps you cannot predict and costs tokens, latency and predictability.](../diagrams/autonomy-dial.svg)

*Figure: moving down the dial hands more of the control flow to the model. Adding tools alone does not move it.*

### An example

The same task at three points on the dial. Task: "Is our day-ahead solar forecast for site X still trustworthy?"

```python
# Level 0: single call
answer = llm(f"Here is the last 7 days of forecast vs actual: {table}. Is it drifting?")

# Level 1: workflow — your code fixes the path
stats   = compute_error_metrics(site)          # plain code
verdict = llm(f"MAE={stats.mae}, bias={stats.bias}. Drift or not?")
if "drift" in verdict.lower():
    report = llm(f"Draft an alert: {stats}")

# Level 2: agent — the model picks the path
tools = [query_forecast_db, query_weather_api, compute_metrics, send_alert]
msgs  = [user("Is the forecast for site X still trustworthy? Investigate and act.")]
while True:
    resp = llm(msgs, tools=tools)
    if not resp.tool_calls:
        break                                   # model decided it is done
    for call in resp.tool_calls:
        msgs.append(tool_result(call, run(call)))  # harness runs the tool, feeds the result back
```

Level 2 might query the database, notice a gap in the data, decide to check the weather API for a cloud event, and only then compute metrics. Or it might do something dumb. That variability is what you buy with autonomy.

### Where it lives in the harness

The [harness](#14-what-a-harness-is) is everything around the model: the loop, the tool executor (the code that runs tool calls), the prompts, the state, the guardrails. The **autonomy dial** is set by how much of the control flow the harness hard-codes versus hands to the model.

- A workflow is a harness with a fixed graph and model-filled nodes.
- An agent is a harness with a generic loop and model-chosen edges.
- Most real systems sit in between — for example, a fixed outer workflow with an agent loop inside one step.

Anthropic's February 2026 autonomy research makes "a matter of degree" concrete. It defines autonomy as "the degree to which an agent operates independently of human direction" and scores it per tool call on a 1–10 scale.

It finds that the same product (Claude Code) runs at very different autonomy levels depending on the user. New users auto-approve roughly 20% of the time; experienced users over 40% — yet experienced users also interrupt more. Same model, same code; the human's oversight settings move it along the dial.

### Common mistakes

Autonomy is a cost, not a feature. Every decision you hand to the model costs tokens, latency and predictability, and errors compound across steps. Anthropic's advice is to find the simplest solution possible and add agent behaviour only when you cannot predict the task's steps up front.

- Building an agent for a problem whose steps you could have drawn on a whiteboard.
- Calling a chained prompt "an agent", then being surprised it cannot recover from anything unexpected.

One more caveat from Willison: an agent has no agency in the human sense. It cannot take responsibility, so the harness and the human still own the outcome.

### Try it

Take one real process from your forecasting work — for example, the morning check of yesterday's forecast error, or onboarding a new site. Sketch it three ways, like the code above: single call, workflow, agent. For each, answer:

1. Could I draw the full graph before running it?
2. What is the worst thing that happens if the model chooses wrong?

Where the answer to (1) is "yes", you probably want a workflow. Keep the sketch; lessons [1.5](#15-anatomy-of-a-real-agent) and [1.6](#16-when-not-to-build-an-agent) build on it.

### Worked answer

Take "morning check of yesterday's day-ahead forecast for every site".

- **Single call.** Put the site table (forecast, actual, MAE, weather flags) into one prompt and ask for a summary. MAE is mean absolute error, the average size of the forecast miss. This is fine while the question is "describe", not "investigate".
- **Workflow.** Code computes per-site error metrics. A routing step sorts sites into fine / degraded / broken. One call writes the digest. A second call runs only for broken sites, to draft a ticket. You can draw every box and arrow before any model runs.
- **Agent.** Give the model `query_metrics`, `get_weather_history`, `get_site_config`, `open_ticket` and a loop, and ask why site X degraded. You cannot draw this graph in advance, because the cause — curtailment, sensor drift, a bad weather feed, a stuck ETL job — decides what to look at next.

Two things beginners get wrong:

1. They answer "can I draw the graph?" for the happy path only. The real test is whether the branches you *cannot* list are the ones that matter. The digest can be listed; the root-cause hunt cannot.
2. The worst wrong choice is usually not too little autonomy, but too much where a bug is silent. An agent that opens tickets on its own judgement will one day open forty on a Sunday because a weather API returned nulls.

The pattern: workflow for the fixed part, agent for the open-ended investigation, and a human gate before any side effect.

### Sources

- Anthropic — [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) (Dec 2024)
- Simon Willison — ["An LLM agent runs tools in a loop to achieve a goal"](https://simonwillison.net/2025/Sep/18/agents/) (Sep 2025)
- Anthropic — [Measuring AI agent autonomy in practice](https://www.anthropic.com/research/measuring-agent-autonomy) (Feb 2026)

---

If an agent is "a model running tools in a loop", the next question is what actually happens on each pass of that loop — and what the model sees.

## 1.2 The agent loop

*Day 2 · 2026-09-04*

> **In short**
> - The model remembers nothing between calls; an agent is a harness that calls it again and again, running tools in between.
> - Each call re-sends the whole conversation, so the transcript is the agent's only memory.
> - The decision to keep going is harness code, and most hard agent problems are loop problems.

### The idea

The model is **stateless**. Each API call is a pure function: messages in, one assistant message out, nothing remembered afterwards. So "an agent that works for twenty minutes" is really a harness that calls the model fifty or two hundred times. On every call it re-sends the entire transcript so far (the running list of messages and tool results).

In the Anthropic API's own terms, the loop is:

1. Send a request with the tool definitions and the messages.
2. The model replies with a stop reason (the field that says why it stopped) of "tool use", and one or more tool-use blocks. Each block has an id, the tool's name and an input object.
3. You run each tool. You wrap each output as a tool-result block tagged with the matching tool-use id, and append them as a new user message.
4. Call again. Repeat while the stop reason is "tool use". Stop when it is "end turn" — or anything else (hitting the output limit, a refusal, a stop sequence).

![A cycle: the task starts the transcript; the harness calls the model with the whole transcript, appends its reply, and checks whether it asked for a tool. If not, stop. If yes, the harness runs each tool, appends the results as a user message, and calls the model again.](../diagrams/agent-loop-cycle.svg)

*Figure: the model only produces the reply. Every other box, including the decision to go round again, is harness code.*

You will often see this described as **perceive → reason → act → observe**. Mapped onto the loop:

- **Perceive** — the model reads the transcript.
- **Reason** — the tokens it generates before or alongside a tool call (extended thinking, which is reasoning text the model writes before answering, or plain text).
- **Act** — the harness runs the tool the model named.
- **Observe** — the tool result lands in the transcript. It is only "observed" when the next call re-reads it.

The model never observes anything itself. The harness observes, then narrates back.

In code, the whole thing is small. Thorsten Ball's write-up builds a working file-editing agent in about 190 lines of Go with three tools (`read_file`, `list_files`, `edit_file`), and the loop is the boring part:

```python
messages = [user(task)]
while True:
    resp = client.messages.create(model, tools=TOOLS, messages=messages)
    messages.append(assistant(resp.content))
    if resp.stop_reason != "tool_use":
        return resp
    results = [tool_result(b.id, run(b.name, b.input))
               for b in resp.content if b.type == "tool_use"]
    messages.append(user(results))
```

Each pass adds the model's reply to the transcript, stops if no tool was asked for, and otherwise runs every requested tool and adds the results as the next user message.

**API details**

| What | Value |
|---|---|
| Tool definitions in the request | `tools` array |
| Stop reason when a tool is requested | `stop_reason: "tool_use"` |
| Tool request block | `tool_use`, with `id`, `name`, `input` |
| Tool result block | `tool_result`, tagged with `tool_use_id` |
| Normal finish | `"end_turn"` |
| Other stop reasons | `max_tokens`, `refusal`, `stop_sequence` |

### An example

What does the model see on turn 7? Not "the latest tool result". It sees, in order:

- the system prompt and the tool definitions;
- the original task;
- every assistant message and every tool result from turns 1 to 6;
- then the newest result.

There is no hidden memory; the transcript *is* the memory. Three things follow:

1. **Context only grows.** A tool that dumps 40 KB of logs on turn 2 makes every later turn more expensive. ([Week 2](week-02-core-mechanics.md) and [Week 3](week-03-state-and-memory.md) deal with this.)
2. **If it is not in the transcript, it does not exist for the model.** If the harness silently retried or cut something short, the model does not know unless you tell it.
3. **The tool result is the only channel through which the world talks back.** That is why later weeks treat error messages and result formatting as prompt engineering.

### Where it lives in the harness

Loop control (when to call, when to stop), the tool executor and the transcript builder are all harness code. The model contributes exactly one thing per turn: the next message. The decision to keep going is yours. That is why step budgets and stop conditions ([2.5](week-02-core-mechanics.md#25-stopping-conditions-step-budgets-and-loop-detection)) are harness features, not model features.

### Common mistakes

Most hard agent problems are loop problems in disguise:

- Runaway cost is a loop with no budget.
- "The agent forgot" is a trimmed transcript.
- "It keeps calling the same tool" is a result that failed to change what the model sees.

The most common beginner mistake is appending the tool result without the assistant's tool-use message before it. The API rejects this, and it erases the model's record of what it tried.

The second is treating an "end turn" stop as "task complete". It only means the model chose not to call a tool, which may be a stall.

### Try it

Write the loop above in Python against the Anthropic SDK (or any provider with function calling), with two fake tools: `get_forecast(site, date)` and `get_actual(site, date)`, each returning a hard-coded dict. Ask the model for the day-ahead error of site "SG-01" on 2026-09-03. On each pass, log the message count and the total characters in `messages`.

Run it again with `get_actual` returning 5,000 characters of noise around the numbers. Report: turns per run, how the transcript size grew, and one change that would make the noisy result cheaper on later turns.

No API key? Trace it by hand and write out the exact `messages` array at the end of turn 2.

### Worked answer

A clean run takes **three model calls**:

1. Call 1 returns `tool_use` for `get_forecast`. (A model that runs tools in parallel may ask for both `get_forecast` and `get_actual` in one assistant message — then the whole run is two calls.)
2. Call 2 asks for `get_actual`.
3. Call 3 computes the error in text and returns `end_turn`.

At the end of turn 2, the `messages` array has five entries:

```
user      task
assistant [tool_use get_forecast]
user      [tool_result]
assistant [tool_use get_actual]
user      [tool_result]
```

The message count grows by two per tool turn. Characters grow by roughly the size of each result.

With the noisy `get_actual`, the message count is the same, but the transcript jumps by about 5,000 characters at turn 2 — and **every later call re-sends them**. That is roughly 1,300 extra input tokens per turn for no information, paid on every turn of a long investigation.

The cheapest fix is in the harness. Have the executor return only what the model needs before wrapping it in the `tool_result`: parse out the numbers, or truncate with a note like `"…4,800 chars omitted; call with verbose=true if needed"`.

Beginner mistakes:

- Appending the `tool_result` without the preceding assistant `tool_use` message (the API rejects it).
- Asking the model to "be brief". That trims the model's *output*, not the tool result — and the tool result is where the cost is.

### Sources

- Anthropic — [How tool use works](https://platform.claude.com/docs/en/agents-and-tools/tool-use/how-tool-use-works)
- Anthropic — [Stop reasons and fallback](https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons)
- Thorsten Ball — [How to Build an Agent](https://ampcode.com/notes/how-to-build-an-agent) (Apr 2025)

---

Inside that loop, the single most important exchange is the moment the model asks for an action and your code answers. That handshake is next.

## 1.3 Tool / function calling

*Day 3 · 2026-09-05*

> **In short**
> - A model cannot call anything: tool calling is a protocol where you describe actions, the model sends back a structured request, and your code does the work and reports back.
> - Only the request comes from the model; everything else is harness, so the harness defends the contract before and after running.
> - Tool descriptions are prompt text, and the highest-leverage prompt text you will write.

### The idea

Three pieces make up the contract.

**1. The tool definition.** A name, a plain-text description, and a JSON Schema for the arguments (JSON Schema is a standard way to describe the shape of JSON data). Anthropic's minimal example:

```json
{
  "name": "get_weather",
  "description": "Get the current weather in a given location",
  "input_schema": {
    "type": "object",
    "properties": {
      "location": {"type": "string", "description": "The city and state, e.g. San Francisco, CA"},
      "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
    },
    "required": ["location"]
  }
}
```

Nothing here is magic. The API turns your definitions into text in the system prompt ("In this environment you have access to a set of tools… Here are the functions available in JSONSchema format: …"). The model has been trained to emit a special content block instead of prose when it decides to act. So tool definitions are **prompt text**: they cost tokens on every call, and their wording steers behaviour.

**2. The request.** An assistant message whose stop reason is "tool use", containing one or more tool-use blocks. Each block holds an id, a tool name and an input. The input is a JSON object the model generated to match your schema.

OpenAI's equivalent is a function-call item with a call id, a name and arguments; the shapes differ, the idea is the same. The request is a **proposal**. The model has done nothing yet.

**3. The execution and result.** Your harness:

- looks up the name in a registry (a table from tool name to function);
- checks the input against the schema;
- runs the function;
- returns a user message with a tool-result block: the matching id, the content, and an optional error flag.

Setting the error flag tells the model the call failed, so it can adapt instead of trusting garbage. The result must be matched by id, because the model may have asked for several tools in one turn (**parallel tool use**) and needs to know which answer belongs to which question.

![A sequence between harness and model: the harness sends tool definitions and messages; the model returns a tool-use request with id, name and input; the harness looks it up, validates, runs and shapes the result; it sends back a tool result matched by id, with an error flag if it failed; the model sends its next request or final answer.](../diagrams/tool-call-handshake.svg)

*Figure: the model's only move is the request. Validation, running and shaping all happen on the harness side.*

The executor in Python is about as small as it sounds:

```python
REGISTRY = {"get_forecast": get_forecast, "get_actual": get_actual}

def execute(block):  # block is a tool_use block
    fn = REGISTRY.get(block.name)
    if fn is None:
        return tool_result(block.id, f"Unknown tool {block.name}", is_error=True)
    try:
        validate(block.input, SCHEMAS[block.name])   # jsonschema
        out = fn(**block.input)
        return tool_result(block.id, render(out))     # shape it for the model
    except Exception as e:
        return tool_result(block.id, f"{type(e).__name__}: {e}", is_error=True)
```

It looks the tool up, checks the arguments, runs it, shapes the output for the model, and turns any failure into an error result rather than crashing or hiding it.

Two control knobs sit on the request side:

- **Tool choice** decides whether the model *may* call a tool (the default), *must* call some tool, must call one specific tool, or may not call any. The two "must" settings are how you use tool calling purely to get structured output.
- **Parallel tool use** lets the model ask for several independent actions in one turn. You can turn it off when the order of calls matters because of side effects.

**API details**

| What | Value |
|---|---|
| Request (Anthropic) | `stop_reason: "tool_use"`; `tool_use` blocks `{id, name, input}` |
| Request (OpenAI) | `function_call` item with `call_id`, `name`, `arguments` |
| Result (Anthropic) | `tool_result` block `{tool_use_id, content, is_error?}` |
| Error flag | `is_error: true` |
| Tool choice setting | `tool_choice` |
| Tool choice values | `auto` (may; the default), `any` (must call some tool), `tool` (must call one named tool), `none` (may not) |

### Where it lives in the harness

Everything except the request is your code: registry, validation, dispatch, permissions around the function, and how results are rendered.

Anthropic calls a tool "a contract between deterministic systems and non-deterministic agents". The caller may misread the purpose, invent arguments, or pick a strange strategy. So the harness defends the contract at both edges:

- **before** running: validate and authorise;
- **after** running: shape the result so the next call sees what it needs and nothing more.

### Common mistakes

Tool descriptions are the highest-leverage prompt text you will write. Anthropic asks for at least 3–4 sentences per tool, covering what it does, when to use it and when not to, what each parameter means, and caveats. It reports that "even small refinements to tool descriptions can yield dramatic improvements".

- One tool per API endpoint instead of a few workflow-shaped tools (`schedule_event`, not `list_users` + `list_events` + `create_event`).
- Returning raw UUIDs and full payloads where names and a filtered view would do.
- Swallowing exceptions, so the model sees an empty result and assumes success.
- Trusting the model's input because "the schema was in the prompt". The schema constrains; it does not guarantee.

### Try it

Take the `get_forecast` / `get_actual` tools from [1.2](#12-the-agent-loop) and:

- **(a)** Write full definitions with 3–4-sentence descriptions and per-parameter descriptions. Include what is returned and what happens when a site or date has no data.
- **(b)** Add a registry-and-validate executor like the one above.
- **(c)** Feed it three bad requests — an unknown tool name, a date in the wrong format, a site that does not exist — and write the exact `tool_result` content for each. Does each message tell the model what to do next?

Bonus: sketch a `get_site_metrics(site, date)` tool that does both lookups and the error calculation inside it. Argue in two sentences whether it should replace the other two.

### Worked answer

**(a) Definitions.** A good `get_forecast` description says:

> Returns the day-ahead solar generation forecast for one site on one date, in MWh per hour (24 values, local time). Use it when you need the predicted output; use get_actual for what was produced. site is the ENGIE site code, e.g. SG-01; date is ISO YYYY-MM-DD. If no forecast exists for that site/date the result is {"status":"no_data","reason":...}, not an error.

The per-parameter descriptions repeat the format and give one example each.

**(b) Executor.** Registry lookup → `jsonschema.validate(input, schema)` → run → render → wrap. Any exception becomes `is_error: true`. The render step is where the 1.2 lesson lands: return the numbers, not the raw payload.

**(c) The three results.**

- Unknown tool: `Unknown tool 'get_forcast'. Available tools: get_forecast, get_actual.`
- Bad date: `Validation error: date '03/09/2026' does not match YYYY-MM-DD. Retry with date='2026-09-03'.`
- Unknown site: `No site with code 'SG-99'. Known sites: SG-01, SG-02, MY-01. Check the code or ask the user.`

Each one names the problem, names the fix, and gives the model the data it needs to fix it without another round trip.

**Bonus.** `get_site_metrics(site, date)` should *join* the other two, not replace them. It turns a three-turn exchange into one call for the common question (Anthropic's advice to consolidate tools). But keep the basic tools for when the model needs forecast-only or actual-only detail.

Beginner mistakes:

- Error text that says only "invalid input" — the model then guesses.
- Validation errors that leak Python tracebacks instead of a sentence about what to do next.

### Sources

- Anthropic — [Define tools](https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools) (schema, description guidance, `tool_choice`, system-prompt injection)
- Anthropic — [How tool use works](https://platform.claude.com/docs/en/agents-and-tools/tool-use/how-tool-use-works)
- Anthropic Engineering — [Writing effective tools for AI agents](https://www.anthropic.com/engineering/writing-tools-for-agents) (Sep 2025)

---

So far we have the autonomy dial, the loop and the tool contract. It is time to name the whole thing they belong to.

## 1.4 What a "harness" is

*Day 4 · 2026-09-06*

> **In short**
> - An agent is a model plus a harness: all the ordinary code and text around a stateless model that turns it into something that can do a job.
> - The harness has six layers, and it — not the model — is the part you can engineer.
> - Fix agent mistakes with deterministic changes to a layer (a validator, a budget, a linter), not by asking the model harder.

### The idea

Strip an agent down and you find two parts: a model, and everything else. The **harness** is the everything else. HumanLayer's definition is the tidiest: a coding agent is "AI model(s) + harness", where the harness is "the agent's runtime, or its peripherals: what does the model use to interact with its environment?"

It helps to see the harness as six layers. You have already met a piece of each:

1. **Prompts.** The system prompt, tool descriptions ([1.3](#13-tool--function-calling)), and any files injected into context (everything the model is sent on a call) — CLAUDE.md / AGENTS.md-style repo instructions, skills loaded on demand. This layer sets the model's job, limits and procedures.
2. **Tools and the executor.** The registry, schema validation, dispatch and result shaping ([1.3](#13-tool--function-calling)). This is the model's only hands and eyes.
3. **Loop control.** The while-loop, stop-reason handling, step and token budgets, loop detection ([1.2](#12-the-agent-loop); [Week 2](week-02-core-mechanics.md) covers budgets).
4. **State.** The transcript, plus whatever survives outside it: progress files, scratchpads, checkpoints, memory documents ([Week 3](week-03-state-and-memory.md)).
5. **Guardrails and permissions.** What the model may do, with whose credentials, what needs a human's approval, what gets filtered ([Week 5](week-05-control-safety-reliability.md)).
6. **Feedback and evals.** Tests, linters, type checks, tracing, and the eval suite (a set of test tasks with graders) that tells you whether a change to layers 1–5 helped ([Weeks 6](week-06-evaluation-1.md)–[7](week-07-evaluation-2-and-iteration.md)).

![The six layers of a harness, stacked below the stateless model they wrap: prompts, tools and the executor, loop control, state, guardrails and permissions, feedback and evals.](../diagrams/harness-layers.svg)

*Figure: the six harness layers. This week introduces all six; each later week thickens one.*

### An example

Two engineering blogs from 2026 and late 2025 show why "harness engineering" has become a job description.

**OpenAI's Codex team (Feb 2026)** described a three-person team merging roughly 1,500 PRs and about a million lines of code in five months, with "humans steer, agents execute". Almost none of the post is about prompting. It is about the harness:

- a ~100-line AGENTS.md pointing into a `docs/` directory that is the system of record (layer 1, prompts);
- custom linters (automatic code checkers) enforcing naming, file size and dependency direction, so the agent cannot drift (layers 5 and 6, guardrails and feedback);
- local environments and observability the agent can query to check its own work (layers 2 and 6, tools and feedback).

**Anthropic's post on long-running agents (Nov 2025)** attacks layer 4 (state). Agents "must work in discrete sessions, and each new session begins with no memory of what came before." Their answer:

- an initializer agent that sets up a feature list (200+ items, all marked failing);
- a `claude-progress.txt` file;
- descriptive git commits;
- a rule that every session ends in a mergeable "clean state".

The common thread: when the agent makes a mistake, the fix is rarely "ask the model harder". Mitchell Hashimoto's framing (via HumanLayer) is that harness engineering means engineering a solution "such that the agent never makes that mistake again" — a lint rule, a validation step, a better tool result, a progress file. The model is the one part you mostly cannot change; the harness is the part you can.

Your 1.2/1.3 loop was already a harness, just a thin one:

| Layer | In your loop |
|---|---|
| 1 Prompts | a system prompt |
| 2 Tools/executor | two tools and an executor |
| 3 Loop control | a bare while-loop |
| 4 State | the transcript only |
| 5 Guardrails | none |
| 6 Evals | none |

Each week of this course thickens one layer.

### Common mistakes

Two teams with the same model get wildly different results; the difference is almost entirely harness.

- Treating the harness as glue code to write once. It is the product, and it deserves tests, versioning and design review.
- Fixing a failure with prompt wording when a deterministic check (validation, a linter, a budget) would remove that whole class of failure.
- Forgetting layer 6 (feedback and evals). Without evals, every harness change is a guess.

### Try it

Take your 1.3 code and write a one-page **harness inventory**: a table with the six layers as rows. For each layer write (i) what exists today, and (ii) what is missing that bit you yesterday or could bite in production. Be specific: "no budget — a stuck tool loops forever", not "needs guardrails".

Then pick *one* cheap addition for each of layers 3, 5 and 6 (loop control, guardrails, feedback), and implement or sketch it:

- a step budget (e.g. exit after 8 model calls with a message telling the model to summarise);
- a site allow-list checked in the executor before any lookup;
- a logger that appends every model call and tool result to a JSONL file.

Finally, in two sentences: which of the three bad requests from 1.3 would each addition have caught or made cheaper? Keep the code — [1.5](#15-anatomy-of-a-real-agent) walks through a complete minimal agent and you will compare.

### Worked answer

The inventory for the 1.3 code, one line per layer (what exists → the gap):

| Layer | Exists | Gap |
|---|---|---|
| 1 Prompts | system prompt + two tool descriptions | no statement of when to stop, no output format, so answers vary run to run |
| 2 Tools/executor | registry, schema validation, `is_error` | results not truncated; a 30-day query would dump thousands of rows |
| 3 Loop control | `while stop_reason == "tool_use"` | no budget; a tool that keeps returning `"no_data"` loops until the wallet or the context runs out |
| 4 State | transcript only | nothing survives a crash or a context overflow |
| 5 Guardrails/permissions | none | any site code, any date, any tool, no human gate |
| 6 Feedback/evals | none | no way to know if a description tweak helped |

The three cheap additions:

- **(a) Step budget.** Count model calls. At 8, append a user message: `"Budget reached. Answer now from what you have and say what is unverified."` Then allow one final call with `tool_choice="none"`.
- **(b) Allow-list.** `if site not in KNOWN_SITES:` return an error that lists `KNOWN_SITES`. Check it in the executor before dispatch, not in the prompt.
- **(c) Logger.** One JSON line per model call and per tool result: turn, `stop_reason`, input/output tokens, tool name, `is_error`.

Which catches what:

- The **allow-list** makes the SG-99 request cheaper: it is rejected before dispatch, with the fix attached, and this is now guaranteed rather than dependent on each tool.
- The **budget** catches the model retrying the bad date format forever.
- The **logger** catches nothing at run time, but it is the only thing that tells you the unknown-tool typo happened three times last week.

Common mistake: putting the allow-list in the system prompt. That only shifts probability; the executor check removes the whole class of error.

### Sources

- OpenAI — [Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/) (Feb 2026)
- Anthropic — [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) (Nov 2025)
- HumanLayer — [Skill Issue: Harness Engineering for Coding Agents](https://www.humanlayer.dev/blog/skill-issue-harness-engineering-for-coding-agents) (Mar 2026)

---

The six-layer map is still abstract. The fastest way to make it concrete is to read one complete, working agent and label every line with its layer.

## 1.5 Anatomy of a real agent

*Day 5 · 2026-09-07*

> **In short**
> - Every production coding agent — Claude Code, Codex, mini-swe-agent — is a small loop wearing a large coat.
> - Take the coat off and the skeleton fits on one screen, with each line belonging to one of the six layers.
> - Three choices carry most of the weight: exact-match edits, truncation inside the tools, and a way for the model to check its own work.

### The idea

Here is a minimal coding agent in Python against the Anthropic SDK. The bracketed numbers are the harness layers from [1.4](#14-what-a-harness-is): [1] prompts, [2] tools and the executor, [3] loop control, [4] state, [5] guardrails and permissions, [6] feedback and evals. It is a sketch: `MODEL`, `confirm`, `err` and `log` are left for you to fill in, and the tool schemas are elided.

```python
import os, subprocess, json, anthropic
client = anthropic.Anthropic()

SYSTEM = ("You are a coding agent in a repo. Use tools to inspect and edit. "
          "Stop when the task is done and summarise what changed.")          # [1]

def read_file(path):
    return open(path).read()[:20_000]                                         # [2] result shaping

def list_files(path="."):
    out = subprocess.run(["ls", "-R", path], capture_output=True, text=True).stdout
    return "\n".join(out.splitlines()[:300])

def edit_file(path, old_str, new_str):
    src = open(path).read() if os.path.exists(path) else ""
    if old_str and src.count(old_str) != 1:
        raise ValueError(f"old_str must match exactly once; matched {src.count(old_str)} times")
    open(path, "w").write(src.replace(old_str, new_str) if old_str else new_str)
    return "ok"

def bash(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
    return (r.stdout + r.stderr)[-10_000:]

TOOLS = [{"name": "read_file",
          "description": "Read a file's contents (first 20k chars). Use before editing.",
          "input_schema": {...}},
         ...]                                                                 # [1]+[2]
REGISTRY = {"read_file": read_file, "list_files": list_files,
            "edit_file": edit_file, "bash": bash}

def execute(block):                                                           # [2] executor
    if block.name == "bash" and not confirm(block.input["cmd"]):
        return err(block, "User declined.")                                   # [5]
    try:
        return {"type": "tool_result", "tool_use_id": block.id,
                "content": REGISTRY[block.name](**block.input)}
    except Exception as e:
        return err(block, f"{type(e).__name__}: {e}")                         # [2]/[6] error fed back

def run(task, max_turns=30):                                                  # [3]
    messages = [{"role": "user", "content": task}]                            # [4] the only state
    for turn in range(max_turns):
        resp = client.messages.create(model=MODEL, max_tokens=8000, system=SYSTEM,
                                      tools=TOOLS, messages=messages)
        messages.append({"role": "assistant", "content": resp.content})
        log(turn, resp)                                                       # [6]
        if resp.stop_reason != "tool_use":
            return resp
        messages.append({"role": "user",
                         "content": [execute(b) for b in resp.content if b.type == "tool_use"]})
    return "Budget exhausted"                                                 # [3]
```

Four tools that cap their own output, an executor that asks a human before running shell commands and feeds every error back, a loop with a turn limit, and a log.

![The minimal coding agent as a flow: the transcript starts with the task; each turn calls the model with the system prompt and tools, logs the turn, and stops if no tool was requested. Otherwise the executor asks the human before bash, runs read, list, edit or bash with capped output, and sends results and errors back as the next message, until 30 turns are used.](../diagrams/minimal-coding-agent.svg)

*Figure: the same code as a flow. The bracketed numbers are the layers, so every box belongs to one of the six.*

### An example

Walk through a run. Task: "make pytest pass".

1. **Turn 1.** The model has only the task and the tool descriptions. It cannot see the repo, so it must ask: it calls `list_files`.
2. **Turn 2.** It reads the failing test and the module.
3. **Turn 3.** It calls `edit_file` with an `old_str` / `new_str` pair.
4. **Turn 4.** It calls `bash("pytest -q")`.
5. **Turn 5.** The output is green. The model writes a summary and returns `end_turn`.

Five calls, four tool runs, one transcript that grew at every step.

Other small agents have the same shape:

- Thorsten Ball's Go version (three tools, no bash) is about 190 lines.
- nanoAgent is ~100 lines of Python with the same three-tool shape.
- mini-swe-agent drops even the tool-calling API. It has bash only, parses actions from a code block in the model's text, runs every command as an independent subprocess, and keeps "a completely linear history". It scores over 74% on SWE-bench Verified (a public coding benchmark; see [6.6](week-06-evaluation-1.md#66-public-benchmarks-swe-bench-τ-bench-gaia-terminal-bench-and-their-limits)).

Three design choices carry most of the weight:

1. **`edit_file` uses exact-match replacement and refuses ambiguous matches.** That one `ValueError`, fed back word for word, is the most important guardrail in the file. Whole-file rewrites by the model are where code silently disappears.
2. **Results are truncated in the tool**, not by asking the model to be brief (see [1.2](#12-the-agent-loop)).
3. **`bash` gives the model its own feedback loop.** It can run the tests. That is layer 6 (feedback and evals) handed to the agent instead of kept by you.

**API details**

| What | Value |
|---|---|
| mini-swe-agent: how each command runs | an independent `subprocess.run` |

### Where it lives in the harness

Where the coat goes on. mini-swe-agent's default agent wraps the same loop with a step limit, a cost limit and a wall-clock limit, all checked before each model call. It treats "task complete" as the model echoing a magic string that the environment intercepts.

Edd Mann's April 2026 write-up of building a harness ends up with:

- seven shaped tools instead of one bash hammer;
- Pydantic schemas (Pydantic is a Python data-validation library) that both generate the tool definition and validate arguments;
- authorisation hooks for permissions;
- compaction (replacing older transcript with a summary, [3.2](week-03-state-and-memory.md#32-context-management-summarisation-compaction-truncation)) when context passes 80% of the window.

Same skeleton, thicker layers 2, 3, 4 and 5 (tools, loop control, state, guardrails).

**API details**

| What | Value |
|---|---|
| mini-swe-agent: limits checked before each model call | `step_limit`, `cost_limit`, a wall-clock limit |
| Edd Mann's harness: permission hook | `authorize_tool_call` |

### Common mistakes

Once you have read one of these, "agent", "tool", "memory" and "guardrail" each map to a specific line, and frameworks become choices rather than magic. The beginner mistakes are predictable:

- No turn budget. An agent that cannot fix the test will run pytest forty times.
- A `write_file` tool instead of an `edit_file` tool. The model rewrites 400 lines to change one.
- Catching exceptions in the executor but returning an empty string, so the model believes the edit succeeded.

### Try it

Build the agent above (or adapt your 1.4 code) with the four tools. Create a folder with `forecast.csv` and `actual.csv` (24 hourly rows each, site SG-01). Give it the task: "Write mae.py that prints the MAE between the two files, run it, and report the number." Record the turns used, the tool sequence, and the final transcript size in characters.

Then inject one failure: change `edit_file` to return `"ok"` even when `old_str` does not match. Run the same task and note whether — and how many turns later — the model notices.

Finally, write two sentences: which of your 1.4 inventory gaps did the failure exercise, and what single executor change would have caught it?

### Worked answer

**Clean run.**

1. Turn 1: `list_files`.
2. Turn 2: `read_file` on both CSVs (often in parallel).
3. Turn 3: `edit_file` with an empty `old_str`, to create `mae.py`.
4. Turn 4: `bash("python mae.py")`.
5. Turn 5: the number, and `end_turn`.

Five model calls. The transcript is roughly 6–9k characters, most of it the two CSV dumps — so capping `read_file` matters even on toy data.

**Sabotaged run.** Creating a file uses the empty-`old_str` path, so the fake `"ok"` only bites when editing an *existing* file. Seed a buggy `mae.py` first. Then the run goes: `read_file` → `edit_file` (fake `"ok"`) → `bash` runs the *old* code → wrong output or a traceback is the first real signal.

A capable model usually notices on the next turn, because the bash output contradicts the edit it believes it made. It re-reads the file and retries, costing two to three extra turns. Without a bash verifier it never notices: the transcript says "ok", and the transcript is the only memory.

**Gaps exercised:** layer 2 (the executor swallowing a failure) and layer 6 (no independent check). **The single executor change:** raise on zero or multiple matches, and return that as `is_error: true`.

Beginner mistake: blaming the model for "not checking its work". The harness lied to it.

### Sources

- SWE-agent team — [mini-swe-agent: the 100-line agent](https://github.com/SWE-agent/mini-swe-agent)
- mini-swe-agent docs — [Control flow of the default agent](https://mini-swe-agent.com/latest/advanced/control_flow/)
- Edd Mann — [Around the Loop: Building a Coding Agent Harness in Python](https://eddmann.com/posts/around-the-loop-building-a-coding-agent-harness-in-python/) (Apr 2026)
- nanoAgent — ["If you can read ~100 lines of Python, you understand agents"](https://github.com/sanbuphy/nanoAgent)

---

You can now build an agent. The last lesson of the week asks the question you should ask before building one.

## 1.6 When NOT to build an agent

*Day 6 · 2026-09-08*

> **In short**
> - An agent buys one thing: the ability to handle steps you could not list in advance.
> - It pays with tokens, latency, unpredictability and errors that pile up over turns — and that cost is built in, not a tuning problem.
> - Default to the simplest structure that works.

### The idea

Anthropic's guidance is blunt. Find "the simplest solution possible, and only increase complexity when needed". For many applications, "optimizing single LLM calls with retrieval and in-context examples is usually enough". Agents are for open-ended problems where "it's difficult or impossible to predict the required number of steps", and only when "you must have some level of trust in its decision-making".

**Why the cost is built in, not a tuning problem.** If each turn succeeds with probability *p* and the task needs *n* turns that depend on each other, naive success is about *p<sup>n</sup>*. At *p* = 0.95, ten turns gives roughly 60%; twenty turns roughly 36%. Real agents do better, because they can observe and recover (the observe step from [1.2](#12-the-agent-loop)), but the shape holds.

The HORIZON benchmark paper (Wang et al., Apr 2026) studied 3,100+ trajectories (recorded agent runs) across web, OS, embodied and database tasks with GPT-5 and Claude-4-class models. It found success "relatively stable at small levels, then exhibiting sharp performance drop beyond" a depth threshold, with planning and memory failures taking over as the task gets longer. Every turn you take off the model's plate deletes a term from that product.

### A decision procedure

1. **Can I draw the full graph in advance?** If yes, write a workflow ([1.1](#11-llm-call-vs-workflow-vs-agent)). The model fills in nodes; your code owns the edges. You get repeatable behaviour, steps you can unit-test, and a fixed cost.
2. **Is the "reasoning" really just rules?** OpenAI's practitioner guide lists three signs that an agent earns its keep:
   - nuanced, context-sensitive judgement with exceptions;
   - rule sets that have become "costly or error-prone" to maintain;
   - heavy reliance on unstructured data.

   Its advice: "validate that your use case can meet these criteria clearly. Otherwise, a deterministic solution may suffice."
3. **What does a silent wrong action cost?** Agents take actions; workflows mostly transform data. If the worst case is "the digest reads oddly", autonomy is cheap. If it is "forty tickets opened on null weather data" (from [1.1](#11-llm-call-vs-workflow-vs-agent)), either put a human gate on the side effect (layer 5, guardrails and permissions) or remove the autonomy.
4. **Can I test it?** Anthropic's precondition for agents is "extensive testing in sandboxed environments, along with the appropriate guardrails". If you cannot build an eval (layer 6, feedback and evals), you cannot tell whether the agent is working — so you should not ship one.
5. **Start with one agent.** OpenAI: "maximize a single agent's capabilities first". Adding agents "can introduce additional complexity and overhead". (Week 8 covers when it is worth it.)

![A decision flow: if you can draw the full graph in advance, build a workflow. If not, and the reasoning is really just rules, deterministic code may suffice. Otherwise, if a silent wrong action is costly, add a human gate on the side effect or reduce autonomy. Then, if you cannot eval it, do not ship an agent; if you can, start with one agent.](../diagrams/agent-or-not.svg)

*Figure: the five questions as a flow. An agent is what is left after every simpler answer has been ruled out.*

### An example

Three jobs from a solar-forecasting morning routine:

- **"Compute yesterday's MAE (mean absolute error) per site and flag anything above threshold."** Every step is known. No LLM calls needed — a cron job (a scheduled script) and pandas. An agent here adds cost and a failure mode to something that already worked.
- **"Write a plain-English morning digest of those flags."** One call over a table. The prompt is the whole harness.
- **"Site SG-03 has degraded for three days; find out why."** The cause is unknown, and the next step depends on the last answer (curtailment? sensor drift? stale weather feed? stuck ETL?). This is the agent-shaped job.

Even so, the right build for SG-03 is a hybrid: a deterministic pipeline computes and routes, the agent investigates read-only, and a human approves the ticket.

### Where it lives in the harness

This is the layer-zero decision: how much control flow to hard-code (layers 1–3: prompts, tools, loop control) and how much to hand over. Every later week assumes you have made it on purpose.

### Common mistakes

- **An agent where a workflow would do.** This is the most common expensive mistake: slower, pricier, harder to test, and failing in ways a cron job never did. The tell: you are prompting the model to "always do X first, then Y". That is a graph — write it as code.
- **The mirror image: a rigid pipeline for a job whose branches you keep discovering in production**, patched with if-statements until the rule set is itself "costly or error-prone". That is the moment to move up the dial. The tell: your routing code has a growing `else` branch labelled "escalate".

### Try it

Take five tasks from the ENGIE forecasting stack — for example: nightly retrain check, weather-feed data-quality validation, "why is site X off?", drafting the weekly performance note, backfilling missing actuals. For each, write one line answering: Can I draw the graph? What is the worst silent wrong action? Can I eval it? Then place it on the dial: no LLM / single call / workflow / agent / hybrid.

Pick the one that lands at "agent" and write two sentences on what you would hard-code to pull it toward "workflow" without losing what needed the agent. Keep the table — the week review and the capstone reuse it.

### Worked answer

| Task | Graph drawable? | Worst silent wrong action | Eval? | Dial |
|---|---|---|---|---|
| Nightly retrain check | Yes: job ran? loss converged? holdout metrics beat the champion? promote or hold | Promoting a worse model | Fully | **No LLM** — metrics and a threshold; at most one call to write the human summary |
| Weather-feed data-quality validation | Yes: schema, null rate, physical ranges, stale timestamps, station dropouts — all rules | Passing a corrupt feed downstream | Yes | **No LLM** |
| "Why is site X off?" | No — the cause (curtailment, sensor drift, stale weather feed, stuck ETL) decides the next step | A confident wrong root cause turned into a wrong ticket | Only against labelled past incidents | **Agent**, built as a hybrid |
| Weekly performance note | Yes: compute metrics in code, one call drafts, a check compares every number in the draft to the source table | A hallucinated figure | Yes | **Workflow** |
| Backfilling missing actuals | Yes: detect gaps, pull the secondary meter, interpolate only under stated rules | Made-up ground truth silently entering the training and eval sets — the most dangerous of the five | Yes | **No LLM**, human gate on any imputation |

**Pulling the agent toward workflow.** Run a deterministic triage first (curtailment flag, weather-feed staleness, ETL job status, inverter alarms), and only call the agent when triage finds nothing. Give it read-only tools and a fixed hypothesis checklist in the prompt. Its output is a ticket draft that a human approves.

The open-ended part — choosing which evidence to pull next — stays with the model. Everything that can be listed leaves the loop.

Two common mistakes:

- Placing the weekly note at "agent" because writing feels open-ended. The writing is one call; only the investigation is open-ended.
- Underrating backfill's worst case. Bad actuals poison every future eval, so backfill deserves the strictest gate — even though it needs no model at all.

### Sources

- Anthropic — [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
- OpenAI — [A practical guide to building agents](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf) (PDF)
- Wang et al. — [The Long-Horizon Task Mirage? Diagnosing Where and Why Agentic Systems Break](https://arxiv.org/html/2604.11978v1) (Apr 2026)

---

## Week 1 review

*Day 7 · 2026-09-09*

Week 1 asked one question from six angles: what is an agent, mechanically, and what around the model makes it work? Week 2 opens the hood on the mechanics, starting with the context window as working memory ([2.1](week-02-core-mechanics.md#21-context-window-as-working-memory)).

### The week in six paragraphs

**1.1 LLM call vs workflow vs agent.** One dial, set by how much control flow the harness hard-codes versus hands over.

- A single call owns everything.
- A workflow is a graph you can draw before running, with the model filling the nodes.
- An agent is a generic loop where the model chooses the edges.

The test is "can I draw the full graph in advance?" — asked about the branches you cannot list, not the happy path. Most real systems are hybrids.

**1.2 The agent loop.** The model is stateless. The harness re-sends the entire transcript on every call and runs tools between calls. Perceive is reading the transcript; act is the harness running a named tool; observe is a tool result appended and seen only on the next call. Context only grows, the transcript is the only memory, and the decision to keep going is harness code. Most hard agent problems are loop problems.

**1.3 Tool calling.** Three pieces:

- the definition (name, description, JSON schema — injected as prompt text);
- the request (a `tool_use` block: a proposal, nothing run yet);
- the execution plus result (registry → validate → run → `tool_result` matched by id, `is_error` on failure).

Only the request is the model's; the rest is harness. Descriptions are the highest-leverage prompt text. Error text should name the problem, the fix, and the data needed to fix it.

**1.4 What a harness is.** Agent = model + harness. The harness has six layers: prompts and injected context, tools and executor, loop control, state, guardrails and permissions, feedback and evals. Harness engineering means fixing agent mistakes with deterministic changes to those layers — a validator, a budget, a linter — so the mistake cannot happen again. Prompt wording only shifts probability. The model is the one part you cannot change.

**1.5 Anatomy of a real agent.** A complete coding agent is about forty lines:

- a system prompt;
- read/list/edit/bash tools that truncate their own output;
- a registry-executor that feeds every exception back as `is_error`;
- a bounded loop;
- a log.

mini-swe-agent and Edd Mann's harness are the same skeleton with thicker layers (limits, submission strings, permission hooks, compaction). The three load-bearing choices: exact-match `edit_file`, truncation inside tools, and giving the model a way to check its own work.

**1.6 When not to build an agent.** An agent buys the ability to handle steps you cannot list, and pays in tokens, latency, unpredictability and compounding error — roughly *p<sup>n</sup>*, with a sharp cliff beyond a depth threshold (HORIZON). Five questions: Can I draw the graph? Is the reasoning really rules? What is the worst silent wrong action? Can I eval it? Can one agent do it? Default to the simplest structure. When an agent is needed, wrap it in a deterministic pipeline with a human gate on side effects.

### Self-quiz

Try each question before reading the answer.

**1.** A colleague says: "Our pipeline calls a model to classify each alert, routes by class in code, then a second call drafts the message — that's our agent." Is it? Name the single property that decides, and what you would have to change for it to become one.

> **Answer.** Not an agent. Code owns every edge, so it is a workflow (the routing pattern). It becomes an agent only when the model chooses the next step — give it the tools and a loop.

**2.** On turn 5 of the loop, list exactly what the model sees, and say where the tool result from turn 2 lives. Then explain why "the agent forgot what it read earlier" is a harness bug rather than a model bug — and name the one case where it is not.

> **Answer.** Turn 5 sees the system prompt, the tool definitions, the task, and every assistant message and `tool_result` from turns 1–4. The turn-2 result is a content block inside a user message. "Forgot" means the harness trimmed it, compacted it, or never narrated it. The exception: the fact was in context and the model still missed it. That is a model limit (the topic of [2.1](week-02-core-mechanics.md#21-context-window-as-working-memory)).

**3.** Name the three pieces of the tool-calling protocol and say which one the model produces. Where does `is_error: true` go, and what three things should the text with it contain?

> **Answer.** Definition, request, execution + result. Only the request (the `tool_use` block) is the model's. `is_error: true` goes on the `tool_result`. The text names the problem, the fix, and the data needed to fix it.

**4.** List the six harness layers and, for each, one specific failure that lives there — concrete enough that you could point at the line of code.

> **Answer.** Prompts: no stop criterion. Tools: an unshaped 5k-character result. Loop: no budget. State: nothing survives a crash. Guardrails: no site allow-list. Feedback: no log or eval.

**5.** Your `edit_file` returns `"ok"` when `old_str` matches twice. Which layer is broken, how (and when) does the model find out, and what is the one-line fix? Then: why is this fix better than adding "always re-read the file after editing" to the system prompt?

> **Answer.** Layer 2 (tools and the executor). The model finds out only when a verifier (`bash`) contradicts it, turns later. Fix: raise on 0 or more than 1 matches, and return `is_error`. This beats a prompt line because it removes the whole class of failure and costs no turn.

### Integrative exercise

Take the one task that landed at "agent" in [1.6](#16-when-not-to-build-an-agent) — "why is site X off?" — and write a one-page harness design for it, one short block per layer:

- **Layer 0 (the agent-or-not decision):** what runs deterministically before the loop, and what the agent is actually asked.
- **Layer 1 (prompts):** the system prompt's role, the hypothesis checklist, the stop instruction.
- **Layer 2 (tools and the executor):** three to five tools, with one written out in full (description, per-parameter descriptions, what "no data" returns). Reuse your 1.3 definitions.
- **Layer 3 (loop control):** the step budget and the completion signal.
- **Layer 4 (state):** what survives across turns beyond the transcript, if anything.
- **Layer 5 (guardrails and permissions):** which tools are read-only, which side effect is gated, and by whom.
- **Layer 6 (feedback and evals):** how you would know it worked on ten past incidents you already have the answer to.

Then inject one failure — the weather API starts returning nulls for every station — and trace which layer notices, on which turn, and what the model sees. Keep this page: it is the seed of the capstone, and Week 2 will thicken layers 1, 3 and 6 (prompts, loop control, feedback and evals).

### Worked answer

- **Layer 0.** A cron job computes 3-day MAE per site and runs deterministic triage (curtailment flag, feed staleness, ETL status, inverter alarms). Only sites that fail triage with no rule-based cause reach the agent, and the triage table is already in the prompt.
- **Layer 1 (prompts).** Role: "forecasting-ops investigator, read-only". A hypothesis checklist: weather feed, sensor/meter drift, curtailment, capacity change, model staleness. Stop instruction: "emit a ticket draft with evidence and confidence; say what is unverified".
- **Layer 2 (tools and the executor).** `get_site_metrics`, `get_weather_history`, `get_site_config`, `get_pipeline_status`, `draft_ticket`. The 1.3 definitions apply, with `{"status":"no_data"}` treated as a normal result.
- **Layer 3 (loop control).** 12 model calls, then a forced final answer with `tool_choice="none"`. Completion = `draft_ticket` called.
- **Layer 4 (state).** Transcript only, plus the JSONL log.
- **Layer 5 (guardrails and permissions).** Everything read-only except `draft_ticket`, which creates a draft that a human approves.
- **Layer 6 (feedback and evals).** Ten labelled past incidents; score root-cause match and steps used.

**Failure trace: null weather for every station.** The executor (layer 2) notices on the first weather call. It returns an `is_error` that names the problem, e.g. `"all 6 stations returned null for 2026-09-07..09; likely feed outage — check pipeline status"`. The model sees this on the next turn and switches to the feed hypothesis.

Common mistake: returning an empty array instead. The model then concludes "no weather anomaly" and moves on.

### Sources (the week's core reading)

- Anthropic — [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
- Anthropic — [How tool use works](https://platform.claude.com/docs/en/agents-and-tools/tool-use/how-tool-use-works)
- OpenAI — [Harness engineering](https://openai.com/index/harness-engineering/)
- SWE-agent team — [mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent)
