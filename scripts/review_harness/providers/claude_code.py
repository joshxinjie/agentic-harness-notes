"""Claude Code CLI in print mode, authenticated with a Claude subscription token (CLAUDE_CODE_OAUTH_TOKEN).

Uses subscription usage instead of API credits. Two modes:
- "review": the reviewer can look things up and run the tests; read-only tools plus a short list of safe commands.
- "respond": the author can also edit files and run Python to apply fixes, but never the review machinery itself
  (PROTECTED), and never commit or push: the workflow does that, as a pull request.
Neither mode gets the GitHub token or web tools.
"""

import json
import os
import shutil
import subprocess
import tempfile
import threading
from pathlib import Path

from ..config import ROOT, load_config
from .base import Completion, Provider

READ_TOOLS = ["Read", "Grep", "Glob"]
SAFE_COMMANDS = ["Bash(git diff *)", "Bash(git log *)", "Bash(git show *)",
                 "Bash(python -m pytest *)", "Bash(python3 -m pytest *)",
                 "Bash(python3 tools/check_links.py *)", "Bash(python tools/check_links.py *)", "Bash(ls *)"]
EDIT_TOOLS = ["Edit", "Write"]
RESPOND_COMMANDS = ["Bash(git status *)", "Bash(python *)", "Bash(python3 *)", "Bash(mmdc *)"]
# The author may not change how reviews work or what the reviewer decided; respond.py also reverts any such change.
PROTECTED = [".github/", "REVIEW.md", "review/", "reviews/", "scripts/review_harness/"]


PASS_ENV = ("PATH", "HOME", "LANG", "LC_ALL", "TMPDIR", "CI")


def agent_env(secret: str, environ=os.environ) -> dict:
    """Only what the CLI needs, plus the subscription token. Never the GitHub token or an API key: an API key would
    switch Claude Code to API billing, and the agent has no business with GitHub write access."""
    env = {k: environ[k] for k in PASS_ENV if k in environ}
    # A token copied from a terminal can pick up a line break where the terminal wrapped it; tokens never contain
    # whitespace, so drop any.
    env[secret] = "".join(environ[secret].split())
    return env


def cli_schema(schema: dict) -> dict:
    """The CLI's validator rejects meta-schema URLs; the schema itself is unchanged."""
    return {k: v for k, v in schema.items() if k not in ("$schema", "$id")}


def protected_rules() -> list[str]:
    rules = []
    for path in PROTECTED:
        target = f"./{path}**" if path.endswith("/") else f"./{path}"
        rules += [f"Edit({target})", f"Write({target})"]
    return rules


def build_command(model: str, system_file: str, schema: dict, max_turns: int, mode: str = "review") -> list[str]:
    if mode == "review":
        tools, allowed = READ_TOOLS + ["Bash"], READ_TOOLS + SAFE_COMMANDS
        denied = ["Edit", "Write", "NotebookEdit"]
    elif mode == "respond":
        tools, allowed = READ_TOOLS + EDIT_TOOLS + ["Bash"], READ_TOOLS + EDIT_TOOLS + SAFE_COMMANDS + RESPOND_COMMANDS
        denied = ["NotebookEdit", "Bash(git commit *)", "Bash(git push *)", "Bash(git reset *)",
                  "Bash(git checkout *)", "Bash(rm *)", *protected_rules()]
    else:
        raise ValueError(f"unknown mode {mode!r}")
    return ["claude", "-p",
            "--model", model,
            "--output-format", "json",
            "--append-system-prompt-file", system_file,
            "--json-schema", json.dumps(cli_schema(schema)),
            "--tools", ",".join(tools),
            "--allowedTools", *allowed,
            "--disallowedTools", *denied, "WebFetch", "WebSearch", "mcp__*",
            "--permission-prompts", "none",       # anything not allowed above is denied, never waited on
            "--max-turns", str(max_turns),
            "--no-session-persistence"]


def flatten(messages: list[dict]) -> str:
    """The CLI takes one prompt; fold a retry conversation into it."""
    if len(messages) == 1:
        return messages[0]["content"]
    parts = [messages[0]["content"]]
    for m in messages[1:]:
        label = "Your previous reply" if m["role"] == "assistant" else "Feedback"
        parts.append(f"\n\n===== {label} =====\n{m['content']}")
    return "".join(parts)


def parse_output(stdout: str) -> Completion:
    """Read the CLI's JSON result; prefer the schema-validated object when present."""
    data = json.loads(stdout)
    if data.get("is_error"):
        raise RuntimeError(f"Claude Code reported an error ({data.get('subtype', 'unknown')}): "
                           f"{str(data.get('result', ''))[:400]}")
    structured = data.get("structured_output")
    text = json.dumps(structured) if isinstance(structured, dict) else str(data.get("result", ""))
    usage = data.get("usage") or {}
    tokens_in = sum(int(usage.get(k, 0) or 0) for k in
                    ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"))
    return Completion(text, tokens_in, int(usage.get("output_tokens", 0) or 0))


def describe(name: str, args: dict, work_dir: Path) -> str | None:
    """One line for the live progress comment, e.g. 'Read plans/live-test.md'. None for steps not worth showing."""
    def rel(path: str) -> str:
        try:
            return str(Path(path).resolve().relative_to(work_dir.resolve()))
        except (ValueError, OSError):
            return path
    if name in ("Read", "Edit", "Write"):
        return f"{name} `{rel(args.get('file_path', '?'))}`"
    if name == "Grep":
        return f"Search for `{str(args.get('pattern', ''))[:60]}`"
    if name == "Glob":
        return f"List `{str(args.get('pattern', ''))[:60]}`"
    if name == "Bash":
        return f"Run `{' '.join(str(args.get('command', '')).split())[:100]}`"
    if name == "StructuredOutput":
        return "Write the final answer"
    return f"{name}"


def stream(cmd: list[str], prompt: str, cwd: Path, env: dict, timeout: float, on_step=None) -> dict:
    """Run the CLI with stream-json output; report each tool call to on_step; return the final result event."""
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                            cwd=cwd, env=env)
    timer = threading.Timer(timeout, proc.kill)
    timer.start()
    result, stderr = None, []
    reader = threading.Thread(target=lambda: stderr.append(proc.stderr.read()), daemon=True)
    reader.start()
    try:
        proc.stdin.write(prompt)
        proc.stdin.close()
        for line in proc.stdout:
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            if ev.get("type") == "assistant" and on_step:
                for block in ev.get("message", {}).get("content", []):
                    if block.get("type") == "tool_use":
                        text = describe(block.get("name", ""), block.get("input") or {}, cwd)
                        if text:
                            try:
                                on_step(text)
                            except Exception:  # noqa: BLE001 - progress is cosmetic; never break the run
                                pass
            elif ev.get("type") == "result":
                result = ev
        proc.wait()
    finally:
        timer.cancel()
    if result is None:
        why = "timed out" if proc.returncode in (-9, 137) else f"exited with {proc.returncode}"
        raise RuntimeError(f"Claude Code {why} without a result: {''.join(stderr)[-400:]}")
    return result


class ClaudeCodeProvider(Provider):
    """config is read from the harness root (main); the agent works in work_dir (the PR checkout, by default the same)."""

    def __init__(self, reviewer: dict, run=subprocess.run, cwd: Path = ROOT, mode: str = "review",
                 work_dir: Path | None = None, schema: dict | None = None):
        self.model = reviewer["model"]
        if not os.environ.get(reviewer["secret"]):
            raise RuntimeError(f"environment variable {reviewer['secret']} is not set")
        if run is subprocess.run and not shutil.which("claude"):
            raise RuntimeError("the Claude Code CLI ('claude') is not installed")
        cfg = load_config(cwd)
        limits = cfg["limits"]
        prefix = "respond_" if mode == "respond" else ""
        self.max_turns = limits.get(f"{prefix}max_agent_turns", limits.get("max_agent_turns", 40))
        self.timeout = 60 * limits.get(f"{prefix}agent_timeout_minutes", limits.get("agent_timeout_minutes", 25))
        self.schema = schema or json.loads((cwd / cfg["output_schema"]).read_text())
        self.run, self.cwd, self.secret, self.mode = run, Path(work_dir or cwd), reviewer["secret"], mode
        self.on_step = None          # set to a callable to receive one line per tool call (live progress)

    def complete(self, system: str, messages: list[dict], max_output_tokens: int) -> Completion:
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as fh:
            fh.write(system)
            system_file = fh.name
        cmd = build_command(self.model, system_file, self.schema, self.max_turns, self.mode)
        try:
            if self.run is subprocess.run:          # the real CLI: stream, so progress can be shown live
                i = cmd.index("--output-format")
                cmd[i + 1: i + 2] = ["stream-json", "--verbose"]
                return parse_output(json.dumps(stream(cmd, flatten(messages), self.cwd, agent_env(self.secret),
                                                      self.timeout, self.on_step)))
            proc = self.run(cmd, input=flatten(messages), capture_output=True, text=True, cwd=self.cwd,
                            timeout=self.timeout, env=agent_env(self.secret))
        finally:
            os.unlink(system_file)
        if proc.returncode != 0 and not proc.stdout.strip().startswith("{"):
            raise RuntimeError(f"Claude Code exited with {proc.returncode}: {(proc.stderr or proc.stdout)[-400:]}")
        return parse_output(proc.stdout)
