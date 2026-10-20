"""Decide what a workflow event should review (or why it should not), for .github/workflows/review.yml.

Writes key=value lines to $GITHUB_OUTPUT:
  run      "true" or "false"
  message  why not (posted on the PR when there is one), or empty
  scope    pr | project
  pr       pull request number (pr scope)
  reviewer reviewer name from review/config.yaml
  provider that reviewer's provider (the workflow installs Claude Code for claude-code)
  base     base branch (pr scope)
  head_sha PR head commit (pr scope)
  title    PR title (pr scope); the description is written to $RUNNER_TEMP/pr_body.md
  areas    space-separated areas (project scope), or empty for the defaults
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import requests

from .config import ROOT, get_reviewer, load_config, today_sgt

COMMAND = re.compile(r"^/review(?:[ \t]+(?!force\b)([A-Za-z0-9_-]+))?([ \t]+force)?[ \t]*$")
TRUSTED = {"OWNER", "MEMBER", "COLLABORATOR"}
WEEKLY_CRON = "23 3 * * 6"
PROJECT_CRON = "23 5 1 * *"
WEEKLY_PREFIX = "weekly/"


def parse_command(body: str) -> tuple[bool, str | None]:
    """'/review', '/review fable', '/review force' or '/review fable force' on the first line -> (True, name or None)."""
    first = (body or "").strip().splitlines()[0] if (body or "").strip() else ""
    m = COMMAND.match(first)
    return (True, m.group(1).lower() if m and m.group(1) else None) if m else (False, None)


def wants_force(body: str) -> bool:
    first = (body or "").strip().splitlines()[0] if (body or "").strip() else ""
    m = COMMAND.match(first)
    return bool(m and m.group(2))


def skip(message: str = "", **extra) -> dict:
    return {"run": "false", "message": message, **extra}


def runs_today(archive_files: list[str], date: str, pr: int) -> int:
    """Reviews of this PR today (author responses don't count)."""
    return sum(1 for f in archive_files
               if Path(f).name.startswith(f"{date}-pr{pr}-") and "-response" not in Path(f).name)


def pr_target(cfg: dict, pr: dict, reviewer_name: str | None, archive_files: list[str], today: str,
              last_review=None, force: bool = False) -> dict:
    """Common checks for any pr-scope run. last_review(pr_number) -> (review file, reviewed commit) or None."""
    number = pr["number"]
    if pr.get("state") != "open":
        return skip(f"PR #{number} is not open.", pr=str(number))
    head_repo = (pr.get("head") or {}).get("repo") or {}
    if head_repo.get("full_name") != (pr.get("base") or {}).get("repo", {}).get("full_name"):
        return skip("Pull requests from forks are not reviewed.", pr=str(number))
    branch = pr["head"]["ref"]
    # A project-review PR collects the author's fixes (merged /respond PRs), so it can be reviewed like any PR.
    if project_review_name(branch) is None and any(branch.startswith(p) for p in cfg["triggers"]["skip_branches"]):
        return skip(f"Not reviewed: `{branch}` holds the reviewer's own output.", pr=str(number))
    try:
        reviewer = get_reviewer(cfg, reviewer_name)
    except ValueError as e:
        return skip(f"Not reviewed: {e}.", pr=str(number))
    limit = cfg["limits"]["max_runs_per_pr_per_day"]
    if runs_today(archive_files, today, number) >= limit:
        return skip(f"Not reviewed: PR #{number} already had {limit} reviews today (limit in review/config.yaml).",
                    pr=str(number))
    if last_review and not force:
        last = last_review(number)
        if last and last[1] and last[1] == pr["head"]["sha"]:
            return skip(f"Not reviewed: commit {last[1][:7]} was already reviewed (`{last[0]}`). Apply the fixes "
                        "first (merge the author's fix PR, or push changes), then `/review` again; comment "
                        "`/review force` to review the same commit anyway.", pr=str(number))
    return {"run": "true", "message": "", "scope": "pr", "pr": str(number), "reviewer": reviewer["name"],
            "provider": reviewer["provider"],
            "base": pr["base"]["ref"], "head_sha": pr["head"]["sha"], "title": pr.get("title", ""),
            "body": pr.get("body") or "", "areas": ""}


def resolve(event_name: str, event: dict, inputs: dict, cfg: dict, get_json, archive_files: list[str],
            today: str, last_review=None) -> dict:
    """get_json(path) -> parsed GitHub REST response for /repos/{repo}/<path>."""
    if event_name == "issue_comment":
        if "pull_request" not in event.get("issue", {}):
            return skip()
        ok, name = parse_command(event["comment"]["body"])
        if not ok:
            return skip()
        if event["comment"].get("author_association") not in TRUSTED:
            return skip("Only the repo owner or collaborators can start a review.")
        return pr_target(cfg, get_json(f"pulls/{event['issue']['number']}"), name, archive_files, today,
                         last_review, wants_force(event["comment"]["body"]))

    if event_name == "pull_request":
        if event.get("label", {}).get("name") != cfg["triggers"]["pr_label"]:
            return skip()
        return pr_target(cfg, get_json(f"pulls/{event['pull_request']['number']}"), None, archive_files, today,
                         last_review)

    if event_name == "workflow_dispatch":
        name = (inputs.get("reviewer") or "").strip() or None
        if inputs.get("scope", "pr") == "pr":
            if not str(inputs.get("pr", "")).strip().isdigit():
                return skip("A PR number is needed for a pr-scope run.")
            # A manual run from the Actions tab is deliberate, so it skips the same-commit check.
            return pr_target(cfg, get_json(f"pulls/{int(inputs['pr'])}"), name, archive_files, today)
        try:
            reviewer = get_reviewer(cfg, name)
        except ValueError as e:
            return skip(f"Not reviewed: {e}.")
        return {"run": "true", "message": "", "scope": "project", "reviewer": reviewer["name"],
                "provider": reviewer["provider"],
                "areas": (inputs.get("areas") or "").strip()}

    if event_name == "schedule":
        if event.get("schedule") == PROJECT_CRON:
            reviewer = get_reviewer(cfg)
            return {"run": "true", "message": "", "scope": "project", "reviewer": reviewer["name"],
                    "provider": reviewer["provider"], "areas": ""}
        # Review the newest open weekly update PR (branch weekly/YYYY-MM-DD, opened by the Saturday task). The
        # same-commit check stops a PR that was already reviewed, and not changed since, from being reviewed again.
        pulls = get_json("pulls?state=open&per_page=100")
        match = sorted((p for p in pulls if p["head"]["ref"].startswith(WEEKLY_PREFIX)),
                       key=lambda p: p["head"]["ref"], reverse=True)
        if not match:
            return skip(f"No open weekly update PR ({WEEKLY_PREFIX}YYYY-MM-DD) to review.")
        return pr_target(cfg, match[0], None, archive_files, today, last_review)

    return skip(f"Unhandled event {event_name}.")


RESPOND = re.compile(r"^/respond(?:[ \t]+([\w.-]+\.json))?[ \t]*$")


def parse_respond(body: str) -> tuple[bool, str | None]:
    """'/respond' or '/respond <review file name>' on the first line."""
    first = (body or "").strip().splitlines()[0] if (body or "").strip() else ""
    m = RESPOND.match(first)
    return (True, m.group(1)) if m else (False, None)


def latest_review(archive_newest_first: list[str], pr: int) -> str | None:
    """Newest review record of this PR (response records excluded)."""
    for path in archive_newest_first:
        name = Path(path).name
        if f"-pr{pr}-" in name and name.endswith(".json") and "-response" not in name:
            return name
    return None


def project_review_name(head_ref: str) -> str | None:
    """'reviewer/2026-10-14-project-fable' (the PR a project review opens) -> its review file name."""
    if head_ref.startswith("reviewer/") and "-project-" in head_ref:
        return head_ref[len("reviewer/"):] + ".json"
    return None


def resolve_respond(event_name: str, event: dict, inputs: dict, cfg: dict, get_json,
                    archive_newest_first: list[str], read_archive) -> dict:
    """read_archive(name) -> the parsed review envelope from the archive branch, or None."""
    if event_name == "issue_comment":
        if "pull_request" not in event.get("issue", {}):
            return skip()
        ok, name = parse_respond(event["comment"]["body"])
        if not ok:
            return skip()
        if event["comment"].get("author_association") not in TRUSTED:
            return skip("Only the repo owner or collaborators can ask for a response.")
        number = int(event["issue"]["number"])
    elif event_name == "workflow_dispatch":
        if not str(inputs.get("pr", "")).strip().isdigit():
            return skip("A PR number is needed.")
        number, name = int(inputs["pr"]), (inputs.get("review") or "").strip() or None
    else:
        return skip(f"Unhandled event {event_name}.")
    pr = get_json(f"pulls/{number}")
    if pr.get("state") != "open":
        return skip(f"PR #{number} is not open.", pr=str(number))
    head_repo = (pr.get("head") or {}).get("repo") or {}
    if head_repo.get("full_name") != (pr.get("base") or {}).get("repo", {}).get("full_name"):
        return skip("Pull requests from forks are not answered.", pr=str(number))
    project = project_review_name(pr["head"]["ref"])
    if project is None and any(pr["head"]["ref"].startswith(p) for p in cfg["triggers"]["skip_branches"]):
        return skip("", pr=str(number))
    pending = [p for p in get_json("pulls?state=open&per_page=100")
               if p["head"]["ref"].startswith(f"respond/pr{number}-")]
    if pending:
        links = ", ".join(f"#{p['number']}" for p in pending)
        return skip(f"The author's fix PR for #{number} ({links}) is still open: merge or close it first, then "
                    "`/review` the result before asking for another response.", pr=str(number))
    # On a project-review PR, a later /review of the PR itself (its fixes) takes precedence over the project review.
    name = name or latest_review(archive_newest_first, number) or project
    if not name:
        return skip(f"No cross-model review of PR #{number} to answer yet; comment /review first.", pr=str(number))
    envelope = read_archive(name)
    if envelope is None:
        return skip(f"Review record {name} not found in the archive.", pr=str(number))
    if "invalid" in envelope.get("meta", {}) or not envelope.get("review"):
        return skip(f"Review {name} failed validation; there are no findings to answer.", pr=str(number))
    if not envelope["review"]["findings"]:
        return skip(f"Review {name} has no findings to answer.", pr=str(number))
    reviewed = envelope.get("meta", {}).get("commit")
    # A project review reads main as it was; its PR only adds the record, so there is no head to compare with.
    if envelope["review"].get("scope") != "project" and reviewed and reviewed != pr["head"]["sha"]:
        return skip(f"PR #{number} has new commits since `{name}` (reviewed {reviewed[:7]}, now "
                    f"{pr['head']['sha'][:7]}); comment `/review` first.", pr=str(number))
    return {"run": "true", "message": "", "pr": str(number), "review": name, "head_ref": pr["head"]["ref"],
            "head_sha": pr["head"]["sha"], "base": pr["base"]["ref"]}


def archive_newest_first(root: Path) -> list[str]:
    out = subprocess.run(["git", "-C", str(root), "log", "--format=", "--name-only", "--diff-filter=A",
                          "origin/reviewer/archive", "--", "reviews/"], capture_output=True, text=True)
    return [line for line in out.stdout.splitlines() if line.strip()] if out.returncode == 0 else []


def read_archive_file(root: Path, name: str):
    out = subprocess.run(["git", "-C", str(root), "show", f"origin/reviewer/archive:reviews/{name}"],
                         capture_output=True, text=True)
    return json.loads(out.stdout) if out.returncode == 0 else None


def archive_listing(root: Path) -> list[str]:
    out = subprocess.run(["git", "-C", str(root), "ls-tree", "--name-only", "origin/reviewer/archive", "reviews/"],
                         capture_output=True, text=True)
    return out.stdout.split() if out.returncode == 0 else []


def write_outputs(result: dict, output_file: str, body_file: str) -> None:
    body = result.pop("body", None)
    if body is not None:
        Path(body_file).write_text(body)
    with open(output_file, "a") as fh:
        for key, value in result.items():
            value = str(value).replace("\r", " ").replace("\n", " ")   # one line per output
            fh.write(f"{key}={value}\n")


def main() -> int:
    repo = os.environ["GITHUB_REPOSITORY"]
    token = os.environ["GITHUB_TOKEN"]
    event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text())
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}

    def get_json(path: str):
        r = requests.get(f"https://api.github.com/repos/{repo}/{path}", headers=headers, timeout=30)
        r.raise_for_status()
        return r.json()

    inputs = event.get("inputs") or {}
    if "--respond" in sys.argv:
        result = resolve_respond(os.environ["GITHUB_EVENT_NAME"], event, inputs, load_config(ROOT), get_json,
                                 archive_newest_first(ROOT), lambda name: read_archive_file(ROOT, name))
    else:
        newest = archive_newest_first(ROOT)

        def last_review(number: int):
            name = latest_review(newest, number)
            env = read_archive_file(ROOT, name) if name else None
            return (name, (env or {}).get("meta", {}).get("commit")) if env else None

        result = resolve(os.environ["GITHUB_EVENT_NAME"], event, inputs, load_config(ROOT), get_json,
                         archive_listing(ROOT), today_sgt(), last_review)
    write_outputs(result, os.environ["GITHUB_OUTPUT"], str(Path(os.environ.get("RUNNER_TEMP", ".")) / "pr_body.md"))
    print(json.dumps({k: v for k, v in result.items() if k != "body"}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
