#!/usr/bin/env python3
"""Package retell-pet-grooming-qa.zip with validation."""
from __future__ import annotations

import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.scenario_loader import load_cases, validate_cases

REQUIRED = [
    "README.md",
    "AGENTS.md",
    "requirements.txt",
    "pyproject.toml",
    ".env.example",
    ".gitignore",
    "tests/cases.json",
    "src/qa_orchestrator.py",
    "src/safety.py",
    "src/retell_client.py",
    "src/qa_judge.py",
    "adapters/integration_verifier.py",
    "adapters/VERIFICATION_CONTRACT.md",
    "dashboard/app.py",
    "prompts/RETELL_QA_CALLER.md",
    "prompts/INDEPENDENT_JUDGE.md",
    "scripts/validate.py",
    "scripts/create_zip.py",
]

EXCLUDE_DIRS = {".venv", "venv", "__pycache__", ".git", ".mypy_cache", ".pytest_cache", "qa_runs"}
EXCLUDE_FILES = {".env", "retell-pet-grooming-qa.zip"}
EXCLUDE_SUFFIXES = {".pyc", ".wav", ".mp3"}


def should_include(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    parts = set(rel.parts)
    if parts & EXCLUDE_DIRS:
        return False
    if path.name in EXCLUDE_FILES:
        return False
    if path.suffix in EXCLUDE_SUFFIXES:
        return False
    if path.name.endswith(".json") and path.parent.name == "qa_runs":
        return False
    # Exclude local filled configs that may contain operational details beyond examples
    if rel.as_posix() in {
        "config/business.json",
        "config/qa_vars.json",
        "config/sandbox_proof.json",
        "config/test_settings.json",
    }:
        return False
    return True


def main() -> int:
    # Validate structure
    missing = [r for r in REQUIRED if not (ROOT / r).exists()]
    if missing:
        print("Missing required files:")
        for m in missing:
            print(" -", m)
        return 1
    cases = load_cases()
    errors = validate_cases(cases)
    print(f"Manifest scenarios: {len(cases)} unique={len({c['id'] for c in cases})}")
    if errors:
        print("Manifest validation failed:")
        for e in errors:
            print(" -", e)
        return 1

    # Unit tests
    proc = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    print(proc.stdout)
    print(proc.stderr)
    if proc.returncode != 0:
        print("Unit tests failed — ZIP not created")
        return 1

    zip_path = ROOT / "retell-pet-grooming-qa.zip"
    # Prefer writing to parent if project root IS the package folder — user asked project root.
    # Also place a copy at workspace parent of this package.
    out_paths = [zip_path, ROOT.parent / "retell-pet-grooming-qa.zip"]

    files = [p for p in ROOT.rglob("*") if p.is_file() and should_include(p)]
    for out in out_paths:
        with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for path in files:
                arc = Path("retell-pet-grooming-qa") / path.relative_to(ROOT)
                zf.write(path, arcname=str(arc))
        # Verify
        with zipfile.ZipFile(out, "r") as zf:
            names = set(zf.namelist())
            for req in REQUIRED:
                key = f"retell-pet-grooming-qa/{req}"
                if key not in names:
                    print("ZIP missing", key)
                    return 1
            # verify cases inside zip
            raw = zf.read("retell-pet-grooming-qa/tests/cases.json")
            import json
            zcases = json.loads(raw)
            assert len(zcases) == 108
            assert len({c["id"] for c in zcases}) == 108
        size = out.stat().st_size
        print(f"ZIP OK: {out.resolve()}")
        print(f"Files packaged: {len(files)}")
        print(f"Size bytes: {size}")
    print("Validation: manifest 108 OK; unit tests OK; zip verified OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
