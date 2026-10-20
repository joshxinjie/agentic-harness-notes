"""Cross-model review harness (scripts/review_harness): offline tests, no API calls."""

import copy
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from review_harness import context as C  # noqa: E402
from review_harness import post as P  # noqa: E402
from review_harness import run as R  # noqa: E402
from review_harness.config import get_reviewer, load_config  # noqa: E402
from review_harness.diff import parse_unified_diff  # noqa: E402
from review_harness.providers.anthropic import AnthropicProvider  # noqa: E402
from review_harness.providers.base import Completion, Provider  # noqa: E402
from review_harness.validate import (derive_verdict, extract_json, schema_errors,  # noqa: E402
                                     semantic_errors)

CFG = load_config(ROOT)
SCHEMA = json.loads((ROOT / "review" / "schema.json").read_text())


def finding(**kw):
    f = {"id": "F1", "severity": "minor", "area": "tooling", "title": "t", "file": "README.md", "line_start": 3,
         "claim": "c", "evidence": "e", "proposed_change": "p", "verified_by": "read_code", "confidence": 0.7}
    f.update(kw)
    return f


def review(scope="pr", verdict="approve_with_nits", findings=None):
    return {"schema_version": 1, "scope": scope, "verdict": verdict, "summary": "s",
            "findings": [finding()] if findings is None else findings}


# ---- diff -----------------------------------------------------------------------------------------------------------

def test_diff_lines_and_header_lookalikes():
    d = ("diff --git a/x.py b/x.py\n--- a/x.py\n+++ b/x.py\n@@ -1,3 +1,4 @@\n a\n-b\n+++ c\n+d\n e\n"
         "diff --git a/new.md b/new.md\nnew file mode 100644\n--- /dev/null\n+++ b/new.md\n@@ -0,0 +1,2 @@\n+one\n+two\n"
         "\\ No newline at end of file\n"
         "diff --git a/gone.py b/gone.py\n--- a/gone.py\n+++ /dev/null\n@@ -1 +0,0 @@\n-x\n")
    m = parse_unified_diff(d)
    assert m["x.py"] == {"added": {2, 3}, "commentable": {1, 2, 3, 4}}
    assert m["new.md"]["added"] == {1, 2}
    assert "gone.py" not in m and "+++ c" not in str(m.keys())


# ---- validation -----------------------------------------------------------------------------------------------------

def test_valid_review_passes():
    assert schema_errors(review(), SCHEMA) == []
    assert semantic_errors(review(), "pr", ROOT) == []


@pytest.mark.parametrize("mutate, expect", [
    (lambda r: r.pop("summary"), "missing required field 'summary'"),
    (lambda r: r["findings"][0].update(severity="huge"), "not one of"),
    (lambda r: r.update(extra=1), "unexpected field 'extra'"),
    (lambda r: r["findings"][0].update(confidence=1.5), "above 1"),
    (lambda r: r["findings"][0].update(id="X1"), "does not match"),
    (lambda r: r.update(findings=[finding(id=f"F{k}") for k in range(16)]), "more than 15 items"),
    (lambda r: r["findings"][0].update(line_start="3"), "expected integer"),
])
def test_schema_rejects(mutate, expect):
    r = review()
    mutate(r)
    assert any(expect in e for e in schema_errors(r, SCHEMA))


def test_semantic_errors():
    r = review(verdict="healthy", findings=[finding(), finding(file="nope/missing.py#x"),
                                            finding(id="F2", line_start=9, line_end=4)])
    errs = " ".join(semantic_errors(r, "pr", ROOT))
    assert "not a pr-scope verdict" in errs and "unique" in errs
    assert "does not exist" in errs and "line_end before line_start" in errs
    assert semantic_errors(review(findings=[finding(file="STYLE.md#visuals section")]), "pr", ROOT) == []


@pytest.mark.parametrize("scope, sevs, verdict", [
    ("pr", [], "approve"), ("pr", ["nit", "question"], "approve"), ("pr", ["minor"], "approve_with_nits"),
    ("pr", ["minor", "major"], "changes_needed"), ("project", ["minor"], "healthy"),
    ("project", ["major"], "attention"), ("project", ["critical", "nit"], "at_risk"),
])
def test_derive_verdict(scope, sevs, verdict):
    assert derive_verdict(scope, [{"severity": s} for s in sevs]) == verdict


def test_extract_json():
    assert extract_json('Sure:\n```json\n{"a": {"b": 1}}\n```\nDone')["a"]["b"] == 1
    assert extract_json('{"a": 1}')["a"] == 1
    with pytest.raises(ValueError):
        extract_json("no json here")


# ---- run loop -------------------------------------------------------------------------------------------------------

class FakeProvider(Provider):
    model = "fake"

    def __init__(self, replies):
        self.replies, self.calls = list(replies), []

    def complete(self, system, messages, max_output_tokens):
        self.calls.append(copy.deepcopy(messages))
        return Completion(self.replies.pop(0), 100, 10)


PACK = {"scope": "pr", "text": "===== DIFF =====\n", "files": ["DIFF"], "dropped": [], "tokens": 5,
        "diff": "", "changed": [], "dependents": []}
REVIEWER = {"name": "fable", "provider": "anthropic", "model": "claude-fable-5-1"}


def test_run_retries_then_corrects_verdict_and_sorts():
    good = review(verdict="approve", findings=[finding(id="F1", severity="nit"), finding(id="F2", severity="major")])
    fake = FakeProvider(["not json", json.dumps(good)])
    env = R.run_review(ROOT, CFG, REVIEWER, fake, PACK)
    assert env["meta"]["attempts"] == 2 and "invalid" not in env["meta"]
    assert env["review"]["verdict"] == "changes_needed" and env["meta"]["verdict_adjusted_from"] == "approve"
    assert [f["id"] for f in env["review"]["findings"]] == ["F2", "F1"]
    assert env["meta"]["input_tokens"] == 200
    retry = fake.calls[1]
    assert retry[1]["role"] == "assistant" and "did not pass validation" in retry[2]["content"]


def test_run_gives_up_after_one_retry():
    env = R.run_review(ROOT, CFG, REVIEWER, FakeProvider(["{}", "{}"]), PACK)
    assert env["meta"]["attempts"] == 2 and env["meta"]["invalid"]


def test_prompt_is_blind_and_carries_instructions():
    from review_harness.prompt import build_prompt
    system, user = build_prompt(ROOT, CFG, PACK)
    assert "Cross-model review procedure" in system and '"schema_version"' in system
    assert "claude-opus" not in system + user


def test_output_path_never_overwrites(tmp_path):
    (tmp_path / "reviews").mkdir()
    first = R.output_path(tmp_path, "2026-10-14", "pr25", "fable")
    first.write_text("{}")
    assert R.output_path(tmp_path, "2026-10-14", "pr25", "fable").name == "2026-10-14-pr25-fable-2.json"


# ---- context --------------------------------------------------------------------------------------------------------

def test_sanitize_strips_attribution():
    text = "Fix bug\n\nCo-Authored-By: Claude Opus <x>\nClaude-Session: https://claude.ai/code/session_1\nkeep\n"
    assert C.sanitize(text) == "Fix bug\n\nkeep\n"


def test_fit_to_budget_drops_low_priority_first_and_never_drops_priority_zero():
    items = [C.Item("diff", "x" * 4000, 0), C.Item("dep", "y" * 8000, 2), C.Item("changed", "z" * 4000, 1)]
    kept, dropped = C.fit_to_budget(items, 2100)
    assert dropped == ["dep"] and [i.label for i in kept] == ["diff", "changed"]
    kept, dropped = C.fit_to_budget([C.Item("diff", "x" * 40000, 0)], 1000)
    assert kept[0].label == "diff" and "truncated" in dropped[0] and kept[0].tokens < 10000


def test_build_pr_pack_finds_changes_and_dependents(tmp_path):
    def sh(*a):
        subprocess.run(["git", "-C", str(tmp_path), *a], check=True, capture_output=True)
    sh("init", "-q", "-b", "main")
    sh("config", "user.email", "t@t")
    sh("config", "user.name", "t")
    (tmp_path / "models").mkdir()
    (tmp_path / "REVIEW.md").write_text("instructions")
    (tmp_path / "STYLE.md").write_text("style")
    (tmp_path / "models" / "signal.py").write_text("def f():\n    return 1\n")
    (tmp_path / "models" / "user.py").write_text("from signal import f\n")
    (tmp_path / "models" / "other.py").write_text("x = 1\n")
    sh("add", "-A")
    sh("commit", "-qm", "base")
    sh("checkout", "-qb", "feature")
    (tmp_path / "models" / "signal.py").write_text("def f():\n    return 2\n")
    sh("commit", "-qam", "change")
    pack = C.build_pr_pack(tmp_path, CFG, "main", "feature", "Title",
                           "Body\nCo-Authored-By: Claude <noreply@anthropic.com>")
    assert pack["changed"] == ["models/signal.py"] and pack["dependents"] == ["models/user.py"]
    assert "REVIEW.md" not in pack["files"] and "STYLE.md" in pack["files"]
    assert "+    return 2" in pack["text"] and "Co-Authored-By" not in pack["text"]


def test_project_pack_respects_excludes():
    pack = C.build_project_pack(ROOT, CFG, ["weeks/", "diagrams/"])
    assert pack["files"][0] in CFG["context"]["project"]["always"]
    assert any(f.startswith("weeks/") for f in pack["files"])
    assert any(f.startswith("diagrams/src/") and f.endswith(".mmd") for f in pack["files"])
    assert not any(f.endswith(".svg") for f in pack["files"]) and "REVIEW.md" not in pack["files"]


def test_markdown_dependents_are_pages_that_link_or_embed(tmp_path):
    (tmp_path / "weeks").mkdir()
    (tmp_path / "diagrams" / "src").mkdir(parents=True)
    (tmp_path / "weeks" / "week-01-a.md").write_text("## 1.1 Idea\n")
    (tmp_path / "weeks" / "week-02-b.md").write_text("See [1.1](week-01-a.md#11-idea).\n![x](../diagrams/loop.svg)\n")
    (tmp_path / "glossary.md").write_text("- **Loop**. See [1.1](weeks/week-01-a.md#11-idea).\n")
    (tmp_path / "reading-list.md").write_text("Nothing about week 1 here: week-01-a.md mentioned bare.\n")
    assert C.find_dependents(tmp_path, ["weeks/week-01-a.md"]) == ["glossary.md", "weeks/week-02-b.md"]
    assert C.find_dependents(tmp_path, ["diagrams/src/loop.mmd"]) == ["weeks/week-02-b.md"]


# ---- posting --------------------------------------------------------------------------------------------------------

def envelope(findings):
    return {"meta": {"reviewer": "fable", "model": "claude-fable-5-1", "input_tokens": 1000, "output_tokens": 100,
                     "context_dropped": []},
            "review": review(verdict=derive_verdict("pr", findings), findings=findings)}


def test_plan_comments_and_summary():
    diff_map = {"models/a.py": {"added": {10, 11}, "commentable": {8, 9, 10, 11, 12}}}
    fs = [finding(id="F1", severity="major", file="models/a.py", line_start=10, line_end=12),
          finding(id="F2", file="models/a.py", line_start=40), finding(id="F3", file="README.md")]
    inline, rest = P.plan_comments(fs, diff_map)
    assert len(inline) == 1 and inline[0]["line"] == 12 and inline[0]["start_line"] == 10
    assert [f["id"] for f in rest] == ["F2", "F3"]
    text = P.render_summary(envelope(fs), rest)
    assert "changes_needed" in text and "F2" in text
    assert text.index("F1") < text.index("<details>")      # top findings come before the details


def test_post_falls_back_when_inline_positions_rejected():
    class Resp:
        def __init__(self, code):
            self.status_code = code

        def raise_for_status(self):
            if self.status_code >= 400:
                raise RuntimeError(self.status_code)

        def json(self):
            return {"html_url": "u"}

    class Session:
        def __init__(self):
            self.payloads = []

        def post(self, url, json, headers, timeout):
            self.payloads.append(json)
            return Resp(422 if len(self.payloads) == 1 else 200)

    s = Session()
    out = P.post_pr_review("o/r", 1, "abc", "body", [{"path": "a", "line": 1, "body": "b"}], "tok", s)
    assert out["html_url"] == "u" and s.payloads[0]["event"] == "COMMENT"
    assert "comments" not in s.payloads[1] and "GitHub rejected" in s.payloads[1]["body"]


# ---- config and provider --------------------------------------------------------------------------------------------

def test_get_reviewer_guards():
    assert get_reviewer(CFG)["model"] == "claude-fable-5-1"
    with pytest.raises(ValueError, match="disabled"):
        get_reviewer(CFG, "gpt")
    bad = copy.deepcopy(CFG)
    bad["reviewers"]["fable"]["model"] = bad["author"]["model"]
    with pytest.raises(ValueError, match="author model"):
        get_reviewer(bad)


def test_anthropic_adapter_parses_and_retries(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "k")
    monkeypatch.setattr("review_harness.providers.anthropic.time.sleep", lambda s: None)

    class Resp:
        def __init__(self, code, data=None):
            self.status_code, self._data, self.headers, self.text = code, data, {}, ""

        def json(self):
            return self._data

    class Session:
        def __init__(self):
            self.n, self.payload = 0, None

        def post(self, url, json, headers, timeout):
            self.n += 1
            self.payload = json
            if self.n == 1:
                return Resp(529)
            return Resp(200, {"content": [{"type": "text", "text": "{}"}], "stop_reason": "end_turn",
                              "usage": {"input_tokens": 7, "output_tokens": 3}})

    s = Session()
    c = AnthropicProvider({"model": "claude-fable-5-1", "secret": "ANTHROPIC_API_KEY"}, s) \
        .complete("sys", [{"role": "user", "content": "u"}], 100)
    assert (c.text, c.input_tokens, c.output_tokens, s.n) == ("{}", 7, 3, 2)
    assert s.payload["model"] == "claude-fable-5-1" and s.payload["system"] == "sys"


# ---- workflow gate --------------------------------------------------------------------------------------------------

from review_harness import gate as G  # noqa: E402

TODAY = "2026-11-06"


def pr_json(number=7, ref="feature/x", state="open", fork=False):
    base_repo = {"full_name": "joshxinjie/dalio-debt-cycle"}
    head_repo = {"full_name": "someone/fork"} if fork else base_repo
    return {"number": number, "state": state, "title": "T\nitle", "body": "B",
            "head": {"ref": ref, "sha": "abc123", "repo": head_repo}, "base": {"ref": "main", "repo": base_repo}}


def comment_event(body, assoc="OWNER", number=7):
    return {"issue": {"number": number, "pull_request": {}}, "comment": {"body": body, "author_association": assoc}}


@pytest.mark.parametrize("body, expect", [
    ("/review", (True, None)), ("/review fable", (True, "fable")), ("/review  GPT \nplease", (True, "gpt")),
    ("/reviewer", (False, None)), ("please /review", (False, None)), ("/review a b", (False, None)), ("", (False, None)),
])
def test_parse_command(body, expect):
    assert G.parse_command(body) == expect


def test_gate_comment_runs_and_rejects():
    get = lambda path: pr_json()  # noqa: E731
    out = G.resolve("issue_comment", comment_event("/review"), {}, CFG, get, [], TODAY)
    assert out["run"] == "true" and out["scope"] == "pr" and out["reviewer"] == "fable"
    assert out["head_sha"] == "abc123" and out["base"] == "main"
    assert G.resolve("issue_comment", comment_event("/review", "NONE"), {}, CFG, get, [], TODAY)["run"] == "false"
    msg = G.resolve("issue_comment", comment_event("/review gpt"), {}, CFG, get, [], TODAY)["message"]
    assert "disabled" in msg
    assert G.resolve("issue_comment", comment_event("thanks!"), {}, CFG, get, [], TODAY) == G.skip()


@pytest.mark.parametrize("pr, why", [
    (pr_json(state="closed"), "not open"), (pr_json(fork=True), "forks"), (pr_json(ref="reviewer/project-x"), ""),
])
def test_gate_skips(pr, why):
    out = G.resolve("issue_comment", comment_event("/review"), {}, CFG, lambda p: pr, [], TODAY)
    assert out["run"] == "false" and why in out["message"]


def test_gate_daily_limit_counts_only_this_pr_today():
    limit = CFG["limits"]["max_runs_per_pr_per_day"]
    files = [f"reviews/{TODAY}-pr7-fable{'' if k == 0 else f'-{k + 1}'}.json" for k in range(limit)]
    files += [f"reviews/{TODAY}-pr70-fable.json", "reviews/2026-11-05-pr7-fable.json"]
    assert G.runs_today(files, TODAY, 7) == limit
    out = G.resolve("issue_comment", comment_event("/review"), {}, CFG, lambda p: pr_json(), files, TODAY)
    assert out["run"] == "false" and "already had" in out["message"]


def test_gate_label_dispatch_and_schedule():
    label = {"label": {"name": "review"}, "pull_request": {"number": 7}}
    assert G.resolve("pull_request", label, {}, CFG, lambda p: pr_json(), [], TODAY)["run"] == "true"
    other = {"label": {"name": "bug"}, "pull_request": {"number": 7}}
    assert G.resolve("pull_request", other, {}, CFG, lambda p: pr_json(), [], TODAY)["run"] == "false"
    proj = G.resolve("workflow_dispatch", {}, {"scope": "project", "areas": "weeks/"}, CFG, None, [], TODAY)
    assert proj["scope"] == "project" and proj["areas"] == "weeks/"
    assert "PR number" in G.resolve("workflow_dispatch", {}, {"scope": "pr", "pr": ""}, CFG, None, [], TODAY)["message"]
    pulls = [pr_json(3, "feature/y"), pr_json(8, "weekly/2026-10-24"), pr_json(9, "weekly/2026-10-31")]
    weekly = G.resolve("schedule", {"schedule": G.WEEKLY_CRON}, {}, CFG, lambda p: pulls, [], TODAY)
    assert weekly["run"] == "true" and weekly["pr"] == "9"               # the newest weekly PR
    none = G.resolve("schedule", {"schedule": G.WEEKLY_CRON}, {}, CFG, lambda p: pulls[:1], [], TODAY)
    assert none["run"] == "false" and "weekly/" in none["message"]
    assert G.resolve("schedule", {"schedule": G.PROJECT_CRON}, {}, CFG, None, [], TODAY)["scope"] == "project"


def test_gate_outputs_are_single_line(tmp_path):
    out, body = tmp_path / "out", tmp_path / "body.md"
    G.write_outputs(G.pr_target(CFG, pr_json(), None, [], TODAY), str(out), str(body))
    lines = out.read_text().splitlines()
    assert "title=T itle" in lines and body.read_text() == "B" and not any(ln.startswith("body=") for ln in lines)


def test_workflow_matches_gate_and_never_approves():
    wf = yaml.safe_load((ROOT / ".github" / "workflows" / "review.yml").read_text())
    on = wf.get("on", wf.get(True))            # PyYAML reads the key "on" as True
    assert {c["cron"] for c in on["schedule"]} == {G.WEEKLY_CRON, G.PROJECT_CRON}
    text = (ROOT / ".github" / "workflows" / "review.yml").read_text()
    assert "review_harness.gate" in text and "APPROVE" not in text and "--force" not in text
    assert "git checkout -q origin/main -- REVIEW.md review scripts/review_harness" in text
    assert CFG["triggers"]["pr_label"] in text and CFG["triggers"]["pr_comment_command"] in text


def test_failures_write_a_short_redacted_reason(tmp_path, monkeypatch):
    err = tmp_path / "err.txt"
    R.report_error(str(err), "RuntimeError: Anthropic API 401 for key sk-ant-abcdefghijklmnop " + "x" * 2000)
    text = err.read_text()
    assert "401" in text and "sk-ant" not in text and "[redacted]" in text and len(text) <= 801
    monkeypatch.delenv("CLAUDE_CODE_OAUTH_TOKEN", raising=False)
    err2 = tmp_path / "err2.txt"
    with pytest.raises(RuntimeError):
        R.main(["--scope", "project", "--areas", "README.md", "--error-file", str(err2)])
    assert "CLAUDE_CODE_OAUTH_TOKEN is not set" in err2.read_text()


# ---- Claude Code (subscription) reviewer ----------------------------------------------------------------------------

from review_harness.providers import claude_code as CCP  # noqa: E402


def test_claude_code_command_is_read_only_and_schema_bound():
    cmd = CCP.build_command("claude-fable-5-1", "/tmp/sys.md", SCHEMA, 40)
    joined = " ".join(cmd)
    assert cmd[:2] == ["claude", "-p"] and "--json-schema" in cmd and "--no-session-persistence" in cmd
    schema_arg = json.loads(cmd[cmd.index("--json-schema") + 1])
    assert "$schema" not in schema_arg and schema_arg["required"] == SCHEMA["required"]
    assert cmd[cmd.index("--permission-prompts") + 1] == "none"
    allowed = cmd[cmd.index("--allowedTools") + 1: cmd.index("--disallowedTools")]
    assert "Edit" not in allowed and "Bash" not in allowed            # bash only through the listed patterns
    assert all(a in CCP.READ_TOOLS or a.startswith("Bash(") for a in allowed)
    assert "Edit Write" in joined and "--dangerously-skip-permissions" not in joined


def test_claude_code_env_drops_github_token_and_api_keys():
    environ = {"PATH": "/bin", "HOME": "/h", "CLAUDE_CODE_OAUTH_TOKEN": "t", "GITHUB_TOKEN": "g",
               "GH_TOKEN": "g", "ANTHROPIC_API_KEY": "k", "OPENAI_API_KEY": "o"}
    assert CCP.agent_env("CLAUDE_CODE_OAUTH_TOKEN", environ) == {"PATH": "/bin", "HOME": "/h",
                                                                 "CLAUDE_CODE_OAUTH_TOKEN": "t"}


def test_claude_code_provider_runs_cli_and_parses(monkeypatch):
    monkeypatch.setenv("CLAUDE_CODE_OAUTH_TOKEN", "tok")
    seen = {}

    class Proc:
        returncode = 0
        stderr = ""
        stdout = json.dumps({"is_error": False, "subtype": "success", "result": "ignored",
                             "structured_output": review(), "usage": {"input_tokens": 5, "cache_read_input_tokens": 95,
                                                                      "output_tokens": 7}})

    def fake_run(cmd, **kw):
        seen.update(cmd=cmd, **kw)
        assert open(cmd[cmd.index("--append-system-prompt-file") + 1]).read() == "SYS"
        return Proc()

    p = CCP.ClaudeCodeProvider({"model": "claude-fable-5-1", "secret": "CLAUDE_CODE_OAUTH_TOKEN"}, run=fake_run)
    msgs = [{"role": "user", "content": "U"}, {"role": "assistant", "content": "A"}, {"role": "user", "content": "F"}]
    c = p.complete("SYS", msgs, 100)
    assert json.loads(c.text)["verdict"] == "approve_with_nits" and (c.input_tokens, c.output_tokens) == (100, 7)
    assert seen["input"].startswith("U") and "Your previous reply" in seen["input"] and "Feedback" in seen["input"]
    assert seen["env"]["CLAUDE_CODE_OAUTH_TOKEN"] == "tok" and "GITHUB_TOKEN" not in seen["env"]
    assert seen["cwd"] == ROOT and seen["timeout"] == 60 * CFG["limits"]["agent_timeout_minutes"]


def test_claude_code_token_line_breaks_are_removed():
    env = CCP.agent_env("CLAUDE_CODE_OAUTH_TOKEN", {"PATH": "/bin", "CLAUDE_CODE_OAUTH_TOKEN": " sk-ant-oat01-abc\ndef \n"})
    assert env["CLAUDE_CODE_OAUTH_TOKEN"] == "sk-ant-oat01-abcdef"


def test_claude_code_errors_are_reported(monkeypatch):
    with pytest.raises(RuntimeError, match="error_max_turns"):
        CCP.parse_output(json.dumps({"is_error": True, "subtype": "error_max_turns", "result": ""}))
    monkeypatch.delenv("CLAUDE_CODE_OAUTH_TOKEN", raising=False)
    with pytest.raises(RuntimeError, match="CLAUDE_CODE_OAUTH_TOKEN is not set"):
        CCP.ClaudeCodeProvider({"model": "m", "secret": "CLAUDE_CODE_OAUTH_TOKEN"}, run=lambda *a, **k: None)


def test_default_reviewer_uses_the_subscription_and_gate_reports_provider():
    r = get_reviewer(CFG)
    assert r["provider"] == "claude-code" and r["secret"] == "CLAUDE_CODE_OAUTH_TOKEN"
    out = G.pr_target(CFG, pr_json(), None, [], TODAY)
    assert out["provider"] == "claude-code"


# ---- /respond (author response, M5) ---------------------------------------------------------------------------------

from review_harness import respond as RS  # noqa: E402

# A real decision log with history (copied from joshxinjie/dalio-debt-cycle, where this harness was built), so the
# row-numbering and "already decided" logic is tested against rows /respond actually wrote. This repo's own log
# must keep the same table format: test_live_log_has_the_same_format.
LOG = (ROOT / "tests" / "fixtures" / "decisions_sample.md").read_text()


def test_live_log_has_the_same_format():
    live = (ROOT / "reviews" / "decisions.md").read_text()
    header = lambda text: next(ln for ln in text.splitlines() if ln.startswith("| ID |"))
    assert header(live) == header(LOG)
RESP_SCHEMA = json.loads((ROOT / "review" / "respond_schema.json").read_text())


def env_with(findings):
    return {"meta": {"reviewer": "fable", "model": "claude-fable-5-1"},
            "review": review(verdict=derive_verdict("pr", findings), findings=findings)}


def answer(fid, decision="accept", reason="right", changes="x.py"):
    return {"finding_id": fid, "decision": decision, "reason": reason, "changes": changes}


def resp_json(answers, passed=True):
    return {"schema_version": 1, "summary": "2 accepted", "responses": answers,
            "tests": {"ran": True, "passed": passed, "detail": "300 passed"}}


def test_decision_log_rows_follow_the_log_convention():
    env = env_with([finding(id="F1", severity="major", title="first"), finding(id="F2", severity="nit")])
    name = "2026-10-20-pr40-fable.json"
    assert RS.row_prefix(LOG, name) == "PR40"                     # no earlier review of #40 in the log
    rows = RS.decision_rows([answer("F2", "reject", "wrong | see line 3\nok", "none"), answer("F1")], env,
                            name, "PR40", "2026-10-20", "respond/pr40-2026-10-20")
    assert rows[0].startswith(f"| PR40-F2 | 2026-10-20 | [{name}]({name}) (copy of `reviewer/archive`) | F2: t | "
                              "fable | nit | reject |")
    assert "wrong / see line 3 ok" in rows[0] and rows[0].endswith("| — |")
    assert rows[1].startswith("| PR40-F1 |") and rows[1].endswith("| respond/pr40-2026-10-20 |")
    log = RS.insert_rows(LOG, rows)
    assert log.index("PR40-F2") > log.index("|---|") and RS.decided(log, name) == {"F1", "F2"}
    assert RS.row_prefix(log, name) == "PR40"                     # reused for a partial second answer
    assert RS.row_prefix(log, "2026-10-21-pr40-fable.json") == "PR40-2"
    assert RS.row_prefix(LOG, "2026-10-21-project-fable.json") == "PROJ-2026-10-21"
    assert RS.decided(log, "2026-10-20-pr40-fable-2.json") == set()   # no prefix collision between files
    assert schema_errors(resp_json([answer("F1")]), RESP_SCHEMA) == []


def test_existing_log_rows_are_recognised():
    """The log on main uses linked review cells and 'F1: title' findings; /respond must see them as decided."""
    assert RS.decided(LOG, "2026-10-13-pr31-fable.json") >= {"F1", "F11"}
    assert RS.decided(LOG, "2026-10-13-pr31-fable-2.json") >= {"F1", "F5"}
    assert "F6" not in RS.decided(LOG, "2026-10-13-pr31-fable-2.json")
    assert RS.row_prefix(LOG, "2026-10-14-pr31-fable.json") == "PR31-4"
    assert RS.row_prefix(LOG, "2026-10-20-pr31-fable.json") == "PR31-5"
    pattern = SCHEMA["$defs"]["finding"]["properties"]["related_decision"]["pattern"]
    ids = [c[0] for c in RS.table_rows(LOG)]
    assert ids and all(re.match(pattern, i) for i in ids)


def test_response_must_answer_each_pending_finding_once():
    errs = RS.response_errors(resp_json([answer("F1"), answer("F1"), answer("F9")]), RESP_SCHEMA, ["F1", "F2"])
    joined = " ".join(errs)
    assert "no answer for: F2" in joined and "not asked about: F9" in joined and "more than one answer for: F1" in joined
    assert RS.response_errors(resp_json([answer("F1", "maybe")]), RESP_SCHEMA, ["F1"])


def scratch_repo(tmp_path):
    def sh(*a):
        subprocess.run(["git", "-C", str(tmp_path), *a], check=True, capture_output=True)
    sh("init", "-q", "-b", "main")
    sh("config", "user.email", "t@t")
    sh("config", "user.name", "t")
    (tmp_path / "reviews").mkdir()
    (tmp_path / "reviews" / "decisions.md").write_text(LOG)
    (tmp_path / "REVIEW.md").write_text("rules\n")
    (tmp_path / "x.py").write_text("x = 1\n")
    sh("add", "-A")
    sh("commit", "-qm", "base")
    return tmp_path


class EditingAuthor(Provider):
    """Fake author: edits x.py, tries to edit REVIEW.md and add a review file, then answers."""
    model = "fake-author"

    def __init__(self, work, replies):
        self.work, self.replies, self.calls = work, list(replies), 0

    def complete(self, system, messages, max_output_tokens):
        self.calls += 1
        (self.work / "x.py").write_text("x = 2\n")
        (self.work / "REVIEW.md").write_text("weakened rules\n")
        (self.work / "reviews" / "fake.json").write_text("{}")
        return Completion(self.replies.pop(0), 1, 1)


def test_respond_applies_logs_and_undoes_protected_edits(tmp_path):
    work = scratch_repo(tmp_path)
    env = env_with([finding(id="F1", severity="major"), finding(id="F2", severity="minor")])
    good = json.dumps(resp_json([answer("F1"), answer("F2", "defer", "later", "research/backlog.md item")]))
    author = EditingAuthor(work, ["{not json", good])
    out = RS.respond(ROOT, CFG, author, work, env, "2026-10-14-pr7-fable.json", 7, "main", "respond/pr7-x",
                     date="2026-10-14")
    assert out["status"] == "done" and author.calls == 2
    assert (work / "x.py").read_text() == "x = 2\n"                      # the fix stays
    assert (work / "REVIEW.md").read_text() == "rules\n"                  # protected edit undone
    assert not (work / "reviews" / "fake.json").exists()
    assert set(out["reverted"]) == {"REVIEW.md", "reviews/fake.json"}
    log = (work / "reviews" / "decisions.md").read_text()
    assert ("| PR7-F1 | 2026-10-14 | [2026-10-14-pr7-fable.json](2026-10-14-pr7-fable.json) (copy of `reviewer/archive`) "
            "| F1: t | fable | major | accept |") in log
    assert "| F2: t | fable | minor | defer | later | research/backlog.md item |" in log
    assert json.loads((work / "reviews" / "2026-10-14-pr7-fable.json").read_text()) == env
    s = out["summary"]
    assert "✅ 1 accept" in s and "⏳ 1 defer" in s and "tests pass" in s and "undone: " in s
    assert "Merging this pull request accepts" in s
    again = RS.respond(ROOT, CFG, EditingAuthor(work, []), work, env, "2026-10-14-pr7-fable.json", 7, "main", "b")
    assert again == {"status": "nothing", "already": ["F1", "F2"]}


def test_respond_invalid_answer_leaves_log_unchanged(tmp_path):
    work = scratch_repo(tmp_path)
    env = env_with([finding(id="F1")])
    out = RS.respond(ROOT, CFG, EditingAuthor(work, ["{}", "{}"]), work, env, "r.json", 7, "main", "b")
    assert out["status"] == "invalid" and (work / "reviews" / "decisions.md").read_text() == LOG
    with pytest.raises(ValueError, match="failed validation"):
        RS.respond(ROOT, CFG, EditingAuthor(work, []), work, {"meta": {"invalid": ["x"]}, "review": None},
                   "r.json", 7, "main", "b")


def test_respond_prompt_lists_only_pending_findings():
    env = env_with([finding(id="F1"), finding(id="F2", title="second")])
    system, user = RS.build_prompt(ROOT, CFG, env, ["F2"], 7, "main")
    assert "Author response procedure" in system and "exactly these finding IDs: F2." in system
    assert '"F2"' in user and '"F1"' not in user and "git diff origin/main...HEAD" in user


def test_respond_mode_can_edit_but_not_the_review_machinery_or_git_history():
    cmd = CCP.build_command("claude-opus-5-5", "/tmp/s.md", RESP_SCHEMA, 100, mode="respond")
    allowed = cmd[cmd.index("--allowedTools") + 1: cmd.index("--disallowedTools")]
    denied = cmd[cmd.index("--disallowedTools") + 1: cmd.index("--permission-prompts")]
    assert {"Edit", "Write", "Bash(python *)"} <= set(allowed)
    assert {"Bash(git push *)", "Bash(git commit *)", "Edit(./REVIEW.md)", "Write(./.github/**)",
            "Edit(./scripts/review_harness/**)", "Edit(./reviews/**)", "WebFetch"} <= set(denied)
    with pytest.raises(ValueError):
        CCP.build_command("m", "s", RESP_SCHEMA, 1, mode="anything")


def github(pr=None, open_pulls=()):
    """Stub for gate's get_json: one PR, plus the open-PR list."""
    pr = pr or pr_json()
    return lambda path: list(open_pulls) if path.startswith("pulls?") else pr


def test_gate_respond():
    assert G.parse_respond("/respond") == (True, None)
    assert G.parse_respond("/respond 2026-10-13-pr31-fable.json\nthanks") == (True, "2026-10-13-pr31-fable.json")
    assert G.parse_respond("/respond now") == (False, None) and G.parse_respond("/review") == (False, None)
    newest_first = ["reviews/2026-10-14-pr7-fable-response-020000.json", "reviews/2026-10-14-pr7-fable-response.json",
                    "reviews/2026-10-14-pr7-fable.json", "reviews/2026-10-13-pr7-fable.json",
                    "reviews/2026-10-14-pr70-fable.json"]
    assert G.latest_review(newest_first, 7) == "2026-10-14-pr7-fable.json" and G.latest_review(newest_first, 8) is None
    good = env_with([finding()])
    good["meta"]["commit"] = "abc123"
    read = {"2026-10-14-pr7-fable.json": good, "empty.json": env_with([]),
            "bad.json": {"meta": {"invalid": ["x"]}, "review": None}}.get
    ev = comment_event("/respond")
    out = G.resolve_respond("issue_comment", ev, {}, CFG, github(), newest_first, read)
    assert out["run"] == "true" and out["review"] == "2026-10-14-pr7-fable.json" and out["head_ref"] == "feature/x"
    assert G.resolve_respond("issue_comment", comment_event("/respond", "NONE"), {}, CFG, github(),
                             newest_first, read)["run"] == "false"
    assert "comment /review first" in G.resolve_respond("issue_comment", ev, {}, CFG, github(), [], read)["message"]
    for name, why in (("bad.json", "failed validation"), ("empty.json", "no findings"), ("gone.json", "not found")):
        out = G.resolve_respond("issue_comment", comment_event(f"/respond {name}"), {}, CFG, github(),
                                newest_first, read)
        assert out["run"] == "false" and why in out["message"]
    assert G.resolve_respond("workflow_dispatch", {}, {"pr": "7", "review": ""}, CFG, github(),
                             newest_first, read)["run"] == "true"


def test_respond_waits_for_the_pending_fix_pr_and_for_a_fresh_review():
    newest_first = ["reviews/2026-10-14-pr7-fable.json"]
    env = env_with([finding()])
    env["meta"]["commit"] = "abc123"
    read = {"2026-10-14-pr7-fable.json": env}.get
    pending = [pr_json(38, "respond/pr7-2026-10-14"), pr_json(39, "respond/pr70-2026-10-14")]
    out = G.resolve_respond("issue_comment", comment_event("/respond"), {}, CFG, github(open_pulls=pending),
                            newest_first, read)
    assert out["run"] == "false" and "#38" in out["message"] and "#39" not in out["message"]
    moved = pr_json()
    moved["head"]["sha"] = "def456"
    out = G.resolve_respond("issue_comment", comment_event("/respond"), {}, CFG, github(moved), newest_first, read)
    assert out["run"] == "false" and "new commits since" in out["message"] and "abc123" in out["message"]


def test_review_skips_a_commit_already_reviewed_unless_forced():
    assert G.parse_command("/review force") == (True, None) and G.wants_force("/review force")
    assert G.parse_command("/review fable force") == (True, "fable") and G.wants_force("/review fable force")
    assert not G.wants_force("/review fable") and G.parse_command("/review force now") == (False, None)
    last = lambda n: ("2026-11-06-pr7-fable.json", "abc123")  # noqa: E731
    out = G.resolve("issue_comment", comment_event("/review"), {}, CFG, github(), [], TODAY, last)
    assert out["run"] == "false" and "already reviewed" in out["message"] and "/review force" in out["message"]
    assert G.resolve("issue_comment", comment_event("/review force"), {}, CFG, github(), [], TODAY, last)["run"] == "true"
    moved = pr_json()
    moved["head"]["sha"] = "def456"
    assert G.resolve("issue_comment", comment_event("/review"), {}, CFG, github(moved), [], TODAY, last)["run"] == "true"
    label = {"label": {"name": "review"}, "pull_request": {"number": 7}}
    assert G.resolve("pull_request", label, {}, CFG, github(), [], TODAY, last)["run"] == "false"
    manual = G.resolve("workflow_dispatch", {}, {"scope": "pr", "pr": "7"}, CFG, github(), [], TODAY, last)
    assert manual["run"] == "true"                                  # a manual run is deliberate


def test_review_records_never_overwrite_the_archive(tmp_path):
    (tmp_path / "reviews").mkdir()
    taken = {"2026-10-14-pr37-fable.json", "2026-10-14-pr37-fable-2.json", "2026-10-14-pr37-fable-response.json"}
    assert R.output_path(tmp_path, "2026-10-14", "pr37", "fable", taken).name == "2026-10-14-pr37-fable-3.json"
    files = [f"reviews/{n}" for n in taken] + ["reviews/2026-10-14-pr37-fable-response-020000.json"]
    assert G.runs_today(files, "2026-10-14", 37) == 2               # responses are not reviews


def test_respond_workflow_runs_harness_from_main_and_targets_the_pr_branch():
    text = (ROOT / ".github" / "workflows" / "respond.yml").read_text()
    assert "review_harness.gate --respond" in text and "PYTHONPATH: ${{ github.workspace }}/scripts" in text
    assert '-f base="$HEAD_REF"' in text and "-f base=main" not in text
    assert "APPROVE" not in text and "--force" not in text and "git worktree add -q -b" in text
    assert text.count("secrets.CLAUDE_CODE_OAUTH_TOKEN") == 1 and CFG["triggers"]["respond_command"] in text


# ---- live progress (stream-json + progress comment) -----------------------------------------------------------------

from review_harness import progress as PG  # noqa: E402


def test_describe_tool_calls(tmp_path):
    assert CCP.describe("Read", {"file_path": str(tmp_path / "plans" / "x.md")}, tmp_path) == "Read `plans/x.md`"
    assert CCP.describe("Bash", {"command": "python  -m pytest\n -q"}, tmp_path) == "Run `python -m pytest -q`"
    assert CCP.describe("Grep", {"pattern": "H23p"}, tmp_path) == "Search for `H23p`"
    assert CCP.describe("StructuredOutput", {}, tmp_path) == "Write the final answer"


def test_stream_reports_steps_and_returns_the_result(tmp_path):
    events = [{"type": "system", "subtype": "init"},
              {"type": "assistant", "message": {"content": [
                  {"type": "text", "text": "hi"},
                  {"type": "tool_use", "name": "Read", "input": {"file_path": str(tmp_path / "README.md")}}]}},
              {"type": "assistant", "message": {"content": [
                  {"type": "tool_use", "name": "Bash", "input": {"command": "python -m pytest -q"}}]}},
              {"type": "result", "is_error": False, "subtype": "success", "structured_output": {"ok": 1},
               "usage": {"input_tokens": 3, "output_tokens": 2}}]
    fake = tmp_path / "fake_cli.py"
    fake.write_text("import sys, json\nsys.stdin.read()\n"
                    + "".join(f"print(json.dumps({e!r}))\n" for e in events))
    steps = []
    out = CCP.stream([sys.executable, str(fake)], "prompt", tmp_path, {"PATH": "/usr/bin:/bin"}, 30, steps.append)
    assert steps == ["Read `README.md`", "Run `python -m pytest -q`"] and out["structured_output"] == {"ok": 1}
    assert CCP.parse_output(json.dumps(out)).text == '{"ok": 1}'
    bad = tmp_path / "bad_cli.py"
    bad.write_text("import sys\nsys.stdin.read()\nprint('not json')\nsys.exit(1)\n")
    with pytest.raises(RuntimeError, match="without a result"):
        CCP.stream([sys.executable, str(bad)], "p", tmp_path, {"PATH": "/usr/bin:/bin"}, 30)


def test_progress_comment_throttles_and_folds_on_finish():
    calls = []

    class Resp:
        status_code = 201

        def json(self):
            return {"id": 99}

    class Session:
        def request(self, method, url, json, timeout, headers):
            calls.append((method, url, json["body"]))
            return Resp()

    now = [0.0]
    env = {"GITHUB_TOKEN": "t", "GITHUB_REPOSITORY": "o/r", "PROGRESS_PR": "37", "RUN_URL": "https://run"}
    p = PG.Progress("Author response", env, Session(), clock=lambda: now[0])
    p.start()
    assert calls[0][0] == "POST" and calls[0][1].endswith("/issues/37/comments") and "⏳" in calls[0][2]
    for k in range(20):
        now[0] += 1
        p.step(f"Read `f{k}.md`")
    assert len(calls) == 2 and calls[1][0] == "PATCH" and calls[1][1].endswith("/issues/comments/99")
    assert "_… " in calls[1][2] and "Read `f14.md`" in calls[1][2]          # only the last steps are shown
    p.finish(True, "decisions ready")
    last = calls[-1][2]
    assert last.startswith("✅ **Author response** — decisions ready") and "<details>" in last and "20. Read" in last
    assert PG.Progress("x", {}).enabled is False                          # no env: does nothing


def test_failing_progress_never_breaks_the_run():
    class Boom:
        def request(self, *a, **k):
            raise ConnectionError("down")

    p = PG.Progress("x", {"GITHUB_TOKEN": "t", "GITHUB_REPOSITORY": "o/r", "PROGRESS_PR": "1"}, Boom())
    p.start()
    p.step("Read `a`")
    p.finish(False, "err")
    assert p.steps == ["Read `a`"]


# ---- /respond on a project-review PR --------------------------------------------------------------------------------

def test_respond_on_a_project_review_pr():
    name = "2026-10-14-project-fable.json"
    assert G.project_review_name("reviewer/2026-10-14-project-fable") == name
    assert G.project_review_name("reviewer/2026-10-14-project-fable-2") == "2026-10-14-project-fable-2.json"
    assert G.project_review_name("feature/project-x") is None and G.project_review_name("reviewer/other") is None
    env = env_with([finding()])
    env["review"]["scope"], env["review"]["verdict"] = "project", "attention"
    env["meta"]["commit"] = "main000"                     # main as reviewed; the PR head (main + record) differs
    pr = pr_json(49, "reviewer/2026-10-14-project-fable")
    out = G.resolve_respond("issue_comment", comment_event("/respond", number=49), {}, CFG, github(pr),
                            [], {name: env}.get)
    assert out["run"] == "true" and out["review"] == name and out["head_ref"] == "reviewer/2026-10-14-project-fable"
    pending = [pr_json(50, "respond/pr49-2026-10-14")]
    out = G.resolve_respond("issue_comment", comment_event("/respond", number=49), {}, CFG,
                            github(pr, pending), [], {name: env}.get)
    assert out["run"] == "false" and "#50" in out["message"]
    other = pr_json(51, "reviewer/archive-cleanup")       # other reviewer/ branches are still ignored
    assert G.resolve_respond("issue_comment", comment_event("/respond", number=51), {}, CFG, github(other),
                             [], {name: env}.get) == G.skip("", pr="51")


def test_project_response_prompt_and_ids():
    env = env_with([finding(id="F1"), finding(id="F2")])
    env["review"]["scope"] = "project"
    system, user = RS.build_prompt(ROOT, CFG, env, ["F1", "F2"], 49, "main")
    assert "reviewed the project (not a single pull request)" in user and "git diff" not in user
    assert RS.row_prefix(LOG, "2026-10-14-project-fable.json") == "PROJ-2026-10-14"


# ---- review of project-review PRs; full decision-log text; diff without data files ----------------------------------

def test_decision_rows_keep_the_full_reason():
    env = env_with([finding(id="F1", title="x" * 120)])
    reason = ("A long reason. " * 40)[:600]                        # the schema's maximum
    row = RS.decision_rows([answer("F1", reason=reason, changes="y" * 300)], env, "r.json", "PR1", "d", "b")[0]
    assert "…" not in row and reason.strip() in row and "x" * 120 in row


def test_project_review_prs_can_be_reviewed_and_answered():
    pr = pr_json(49, "reviewer/2026-10-14-project-fable")
    out = G.resolve("issue_comment", comment_event("/review", number=49), {}, CFG, github(pr), [], TODAY)
    assert out["run"] == "true" and out["scope"] == "pr"           # reviews the fixes merged into it
    own = G.resolve("issue_comment", comment_event("/review", number=52), {}, CFG,
                    github(pr_json(52, "reviewer/archive-x")), [], TODAY)
    assert own["run"] == "false" and "reviewer's own output" in own["message"]   # no longer silent
    proj, later = env_with([finding()]), env_with([finding()])
    proj["review"]["scope"] = "project"
    later["meta"]["commit"] = pr["head"]["sha"]
    read = {"2026-10-14-project-fable.json": proj, "2026-10-14-pr49-fable.json": later}.get
    out = G.resolve_respond("issue_comment", comment_event("/respond", number=49), {}, CFG, github(pr),
                            ["reviews/2026-10-14-pr49-fable.json"], read)
    assert out["run"] == "true" and out["review"] == "2026-10-14-pr49-fable.json"   # the newer PR review wins


def test_reviewed_diff_leaves_out_data_files(tmp_path):
    assert C.pathspec_excludes(["data/raw/", "**/*.csv"]) == [":(exclude,glob)data/raw/**", ":(exclude,glob)**/*.csv"]

    def sh(*a):
        subprocess.run(["git", "-C", str(tmp_path), *a], check=True, capture_output=True)
    sh("init", "-q", "-b", "main")
    sh("config", "user.email", "t@t")
    sh("config", "user.name", "t")
    (tmp_path / "m.py").write_text("x = 1\n")
    sh("add", "-A")
    sh("commit", "-qm", "base")
    sh("checkout", "-qb", "f")
    (tmp_path / "m.py").write_text("x = 2\n")
    (tmp_path / "diagrams").mkdir()
    (tmp_path / "diagrams" / "big.svg").write_text("<svg>a,b</svg>\n" * 5000)
    sh("add", "-A")
    sh("commit", "-qm", "change")
    pack = C.build_pr_pack(tmp_path, CFG, "main", "f")
    assert "+x = 2" in pack["diff"] and "a,b" not in pack["diff"]
    assert "left out of this diff: diagrams/big.svg" in pack["diff"]


def test_respond_workflow_records_the_fix_pr_number(tmp_path):
    """Runs the workflow's own sed line: 'Fixed in' must change from the branch name to the PR number."""
    text = (ROOT / ".github" / "workflows" / "respond.yml").read_text()
    line = next(ln.strip() for ln in text.splitlines() if ln.strip().startswith("sed -i") and "decisions.md" in ln)
    command = line.split("   #")[0]                              # drop the trailing comment
    log = tmp_path / "reviews" / "decisions.md"
    log.parent.mkdir()
    log.write_text("| PR57-F1 | d | r | F1: t | fable | major | accept | why | respond/pr57-2026-10-15 |\n"
                   "| PR57-F2 | d | r | F2: t | fable | minor | reject | why | — |\n")
    subprocess.run(["bash", "-c", command], check=True, cwd=tmp_path,
                   env={"PATH": "/usr/bin:/bin", "BRANCH": "respond/pr57-2026-10-15", "num": "58"})
    out = log.read_text()
    assert "| #58 |" in out and "respond/pr57" not in out and "| — |" in out


def test_workflows_install_from_main_not_the_pr():
    """A PR branched before the review setup has no requirements.txt; installing only the PR's copy failed (PR #2)."""
    review = (ROOT / ".github" / "workflows" / "review.yml").read_text()
    respond = (ROOT / ".github" / "workflows" / "respond.yml").read_text()
    assert "git show origin/main:requirements.txt" in review
    assert "\n          pip install -r requirements.txt\n" not in review
    assert 'if [ -f "$RUNNER_TEMP/work/requirements.txt" ]' in respond
