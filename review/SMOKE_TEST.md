# GPT reviewer subscription smoke test

PR #40 round-2 finding PR40-2-F1 remains gated on the intended repository subscription.

## Current result (2026-11-18)

- Installed binary: `codex-cli 0.164.0`, checked with `--version`.
- The repository's `CODEX_AUTH_JSON` login was unavailable in this workspace.
  A local runtime login labelled ChatGPT was present, but its identity as this
  repository's subscription was not verified. It was not substituted.
- No live smoke command or model request ran. There is no model response, exit
  status, structured-output result, token usage or proof of subscription access.
- [Official OpenAI model documentation](https://developers.openai.com/api/docs/models/gpt-6.2-sol)
  lists the exact model ID and structured outputs. API documentation alone does
  not prove access through this CLI version and this subscription.
- `reviewers.gpt.model` therefore remains `gpt-6.1-sol`. Astra is unconfigured;
  no numerical claim about its context capacity is relied on.

## Bounded test to run when access is available

Use exactly the existing intended repository ChatGPT subscription authentication,
CLI 0.164.0 and a disposable clean Git checkout. Do not print credentials, log in
again, replace or share a login, refresh repository secrets, change CLI version,
use API keys, change providers or enable paid fallback. Stop on authentication,
access or usage limits; do not retry with another model or effort. The repository's
normal trusted-main review workflow still selects Sol 6.1 and cannot validate this
candidate. No workflow or subscription credential is added by this document.

The following is the planned command, **not an executed test**. Paths are explicit
placeholders for a trusted installed binary, disposable checkout and private
temporary files. Supply the existing intended authentication through the normal
secure runtime; exclude API-key and provider override settings.

Create `<private-schema.json>` with this small strict response schema:

```json
{"type":"object","properties":{"ok":{"type":"boolean"}},"required":["ok"],"additionalProperties":false}
```

After confirming the binary's `--version` is 0.164.0, run once with a 120-second
external timeout and the pinned harness's structured-output and sandbox flags:

```sh
timeout 120s <codex-0.164.0> exec --json --ephemeral \
  -m gpt-6.2-sol -s workspace-write \
  -c sandbox_workspace_write.network_access=false \
  -C <disposable-clean-checkout> \
  --output-schema <private-schema.json> -o <private-last-message.json> \
  -c 'approval_policy="never"' \
  -c 'cli_auth_credentials_store="file"' \
  -c project_doc_max_bytes=0 \
  -c 'web_search="cached"' \
  -c 'model_reasoning_effort="high"' - <<'PROMPT'
Return exactly {"ok":true}. Do not use tools, inspect files or perform a review.
PROMPT
```

The tiny schema probes the structured-output flags; it does not validate a full
review response. Check a successful exit and a final JSON object exactly equal to
`{"ok":true}`, with no substituted model, lower effort or fallback. Record only a
sanitized outcome, version, model, effort and authentication route. Do not publish
raw events or account identifiers. A successful tiny response would establish
basic request compatibility for that login at that time, not the project's
150,000/400,000-token context packs, full review schema, tool use, future access
or CI secret identity unless that intended CI login was actually used.

Until that check passes, defer the upgrade. If a later upgrade fails, rollback is
to restore `reviewers.gpt.model: gpt-6.1-sol`; leave the author model, auth, limits
and both harness pins unchanged.
