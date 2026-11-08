"""Persist QA run artifacts under qa_runs/."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from src.config import Settings, load_settings


def new_run_id() -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"run_{ts}_{uuid4().hex[:8]}"


def run_dir(settings: Settings, run_id: str) -> Path:
    path = settings.qa_runs_dir / run_id
    path.mkdir(parents=True, exist_ok=True)
    (path / "results").mkdir(exist_ok=True)
    (path / "evidence").mkdir(exist_ok=True)
    (path / "reports").mkdir(exist_ok=True)
    return path


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, default=str) + "\n")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text())


def save_result(settings: Settings, run_id: str, result: dict[str, Any]) -> Path:
    d = run_dir(settings, run_id)
    test_id = result.get("test_id", "unknown")
    path = d / "results" / f"{test_id}.json"
    write_json(path, result)
    # Update index
    index_path = d / "index.json"
    index = read_json(index_path) if index_path.exists() else {"run_id": run_id, "results": []}
    index["results"] = [r for r in index.get("results", []) if r.get("test_id") != test_id]
    index["results"].append(
        {
            "test_id": test_id,
            "status": result.get("status"),
            "severity": result.get("severity"),
            "path": str(path.relative_to(settings.qa_runs_dir)),
        }
    )
    index["updated_at"] = datetime.now(timezone.utc).isoformat()
    write_json(index_path, index)
    return path


def list_runs(settings: Settings | None = None) -> list[Path]:
    settings = settings or load_settings()
    if not settings.qa_runs_dir.exists():
        return []
    return sorted([p for p in settings.qa_runs_dir.iterdir() if p.is_dir()], reverse=True)


def load_run_results(settings: Settings, run_id: str) -> list[dict[str, Any]]:
    d = settings.qa_runs_dir / run_id / "results"
    if not d.exists():
        return []
    out = []
    for path in sorted(d.glob("*.json")):
        out.append(read_json(path))
    return out


def latest_run_id(settings: Settings | None = None) -> str | None:
    runs = list_runs(settings)
    return runs[0].name if runs else None
