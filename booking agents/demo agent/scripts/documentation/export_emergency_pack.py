#!/usr/bin/env python3
"""Export allowlisted recovery docs to DR_EXPORT_DIR (off-repo)."""

from __future__ import annotations

import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

ALLOWLIST = [
    "README.md",
    "AGENTS.md",
    "docs",
    "coordination/README.md",
    "coordination/architecture.md",
    "coordination/agents",
    "coordination/schemas",
    "coordination/templates",
    "coordination/decisions",
    "coordination/shared-context",
    "coordination/config",
    "coordination/memory",
    "coordination/schemas",
    "domains/voice_agent_network",
    "scripts/documentation",
    "scripts/uan",
    "voice-agent/README.md",
    "voice-agent/system-prompt.md",
    "voice-agent/business-facts.md",
    "retell-pet-grooming-qa/README.md",
    "retell-pet-grooming-qa/.env.example",
    "retell-pet-grooming-qa/docs",
]

DENY_NAME_PARTS = (".env", "qa_runs", "__pycache__", ".venv")


def denied(path: Path) -> bool:
    name = path.name
    if name == ".env" or name.endswith(".env"):
        return True
    parts = set(path.parts)
    if "qa_runs" in parts or ".venv" in parts or "__pycache__" in parts:
        return True
    return False


def copy_item(src: Path, dest_root: Path) -> None:
    if not src.exists():
        print(f"SKIP missing: {src.relative_to(ROOT)}")
        return
    rel = src.relative_to(ROOT)
    dest = dest_root / rel
    if src.is_dir():
        for path in src.rglob("*"):
            if path.is_dir() or denied(path):
                continue
            target = dest_root / path.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
    else:
        if denied(src):
            print(f"SKIP denied: {rel}")
            return
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)


def main() -> int:
    dest = os.environ.get("DR_EXPORT_DIR", "").strip()
    if not dest:
        print(
            "BLOCKED: set DR_EXPORT_DIR to an absolute path outside the repository",
            file=sys.stderr,
        )
        return 2
    dest_path = Path(dest).expanduser().resolve()
    if ROOT.resolve() in dest_path.parents or dest_path == ROOT.resolve():
        # also block exporting into the workspace itself
        try:
            dest_path.relative_to(ROOT.resolve())
            print("BLOCKED: DR_EXPORT_DIR must be outside the workspace", file=sys.stderr)
            return 2
        except ValueError:
            pass
    # stronger check: if dest is inside ROOT
    try:
        dest_path.relative_to(ROOT.resolve())
        print("BLOCKED: DR_EXPORT_DIR must be outside the workspace", file=sys.stderr)
        return 2
    except ValueError:
        pass

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    pack = dest_path / f"ai-voice-booking-agents-emergency-{stamp}"
    pack.mkdir(parents=True, exist_ok=False)
    for item in ALLOWLIST:
        copy_item(ROOT / item, pack)
    manifest = pack / "MANIFEST.txt"
    manifest.write_text(
        f"exported_at_utc={stamp}\nsource={ROOT}\nitems={len(ALLOWLIST)}\n",
        encoding="utf-8",
    )
    print(f"PASS: exported to {pack}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
