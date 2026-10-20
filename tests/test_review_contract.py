"""Cross-model review contract (REVIEW.md): schema, config and docs must stay consistent."""

import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "review" / "schema.json").read_text())
CONFIG = yaml.safe_load((ROOT / "review" / "config.yaml").read_text())
REVIEW_MD = (ROOT / "REVIEW.md").read_text()
FINDING = SCHEMA["$defs"]["finding"]["properties"]


def test_config_points_at_existing_files():
    for key in ("instructions", "output_schema", "decision_log"):
        assert (ROOT / CONFIG[key]).exists(), f"config {key} -> {CONFIG[key]} missing"
    for scope in ("pr", "project"):
        for path in CONFIG["context"][scope]["always"]:
            assert (ROOT / path).exists(), f"context.{scope}.always -> {path} missing"


def test_default_reviewer_enabled_pinned_and_not_the_author():
    reviewers = CONFIG["reviewers"]
    default = reviewers[CONFIG["default_reviewer"]]
    assert default["enabled"]
    for name, r in reviewers.items():
        if r["enabled"]:
            assert r["model"], f"enabled reviewer {name} has no pinned model"
            assert r["model"] != CONFIG["author"]["model"], f"reviewer {name} is the author model"
            assert re.fullmatch(r"[A-Z][A-Z0-9_]*", r["secret"]), "secret must be a name, not a key"


def test_every_schema_enum_is_documented_in_review_md():
    enums = (SCHEMA["properties"]["verdict"]["enum"] + FINDING["severity"]["enum"]
             + FINDING["verified_by"]["enum"])
    missing = [v for v in enums if f"`{v}`" not in REVIEW_MD]
    assert not missing, f"REVIEW.md does not define: {missing}"


def test_limits_agree_between_schema_config_and_docs():
    assert SCHEMA["properties"]["findings"]["maxItems"] == CONFIG["limits"]["max_findings"]
    assert f"At most {CONFIG['limits']['max_findings']} findings" in REVIEW_MD


def test_reviewer_branches_are_skipped_but_weekly_updates_are_not():
    skip = CONFIG["triggers"]["skip_branches"]
    assert "reviewer/" in skip
    assert not any("weekly/2026-10-24".startswith(p) for p in skip)


def test_decision_log_has_expected_columns():
    header = next(line for line in (ROOT / CONFIG["decision_log"]).read_text().splitlines()
                  if line.startswith("| ID |"))
    cols = [c.strip() for c in header.strip("|").split("|")]
    assert cols == ["ID", "Date", "Review file", "Finding", "Reviewer", "Severity", "Decision", "Reason", "Fixed in"]
