"""Load review/config.yaml and pick a reviewer."""

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def load_config(root: Path = ROOT) -> dict:
    return yaml.safe_load((root / "review" / "config.yaml").read_text())


def get_reviewer(cfg: dict, name: str | None = None) -> dict:
    """Return the named reviewer (default if None) with its name added; refuse disabled, unpinned or author models."""
    name = name or cfg["default_reviewer"]
    reviewers = cfg["reviewers"]
    if name not in reviewers:
        raise ValueError(f"unknown reviewer {name!r}; known: {', '.join(reviewers)}")
    r = dict(reviewers[name], name=name)
    if not r.get("enabled"):
        raise ValueError(f"reviewer {name!r} is disabled in review/config.yaml")
    if not r.get("model"):
        raise ValueError(f"reviewer {name!r} has no pinned model")
    if r["model"] == cfg["author"]["model"]:
        raise ValueError(f"reviewer {name!r} uses the author model; reviews must come from a different model")
    return r


def today_sgt() -> str:
    """Review dates are Singapore dates, so file names and the daily limit match the owner's day."""
    import datetime as dt
    return dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).date().isoformat()
