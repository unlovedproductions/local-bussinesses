#!/usr/bin/env python3
"""Documentation integrity checks — stdlib only."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

REQUIRED = [
    "README.md",
    "AGENTS.md",
    "docs/README.md",
    "docs/DOCUMENTATION_INDEX.md",
    "docs/DOCUMENTATION_REGISTRY.md",
    "docs/DOCUMENTATION_POLICY.md",
    "docs/PROJECT_OVERVIEW.md",
    "docs/SYSTEM_ARCHITECTURE.md",
    "docs/TECHNOLOGY_STACK.md",
    "docs/DIRECTORY_STRUCTURE.md",
    "docs/CONFIGURATION_REFERENCE.md",
    "docs/development/DEVELOPER_SETUP.md",
    "docs/recovery/EMERGENCY_RECOVERY_START_HERE.md",
    "docs/recovery/DISASTER_RECOVERY.md",
    "docs/recovery/BACKUP_INVENTORY.md",
    "docs/agents/DOCUMENTATION_AGENT.md",
    "docs/templates/DOCUMENTATION_IMPACT.md",
    "docs/verification/INITIAL_DOCUMENTATION_AUDIT.md",
    "coordination/agents/documentation.md",
]

LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
ENV_NAME_RE = re.compile(r"\b([A-Z][A-Z0-9_]{2,})\b")
SECRET_RE = re.compile(
    r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{20,}"
)
SKIP_LINK_PREFIXES = ("http://", "https://", "mailto:", "#")

ENV_PREFIXES = (
    "ALLOW_",
    "ACK_",
    "MAX_",
    "CALCOM_",
    "RETELL_",
    "QA_",
    "TEST_",
    "JUDGE_",
    "OLLAMA_",
    "OPENAI_",
    "BUSINESS_",
    "CASES_",
    "SANDBOX_",
)
ENV_SUFFIXES = (
    "_DIR",
    "_PATH",
    "_KEY",
    "_URL",
    "_ID",
    "_BASE",
    "_VERSION",
    "_NUMBER",
    "_MODE",
    "_PROVIDER",
    "_MODEL",
    "_SECONDS",
    "_USD",
)
ENV_IGNORE = {
    "INTERNAL",
    "VERIFIED",
    "NEEDS_REVIEW",
    "DRAFT",
    "BLOCKED",
    "API",
    "URL",
    "JSON",
    "TLS",
    "SSH",
    "HTTPS",
    "HTTP",
    "PSTN",
    "LLM",
    "STT",
    "TTS",
    "CRM",
    "QA",
    "DR",
    "RPO",
    "RTO",
    "CLI",
    "OS",
    "UI",
    "ID",
    "YES",
    "NO",
}


def looks_like_env(name: str) -> bool:
    return name.startswith(ENV_PREFIXES) or name.endswith(ENV_SUFFIXES)


def run_checks(root: Path) -> tuple[list[str], list[str]]:
    root = root.resolve()
    docs = root / "docs"
    env_example = root / "retell-pet-grooming-qa" / ".env.example"
    qa_scripts = root / "retell-pet-grooming-qa" / "scripts"
    errors: list[str] = []
    warnings: list[str] = []

    for item in REQUIRED:
        if not (root / item).is_file():
            errors.append(f"missing required file: {item}")

    registry = docs / "DOCUMENTATION_REGISTRY.md"
    if registry.is_file():
        text = registry.read_text(encoding="utf-8", errors="replace")
        for item in REQUIRED:
            if item.startswith("docs/") or item in {"README.md", "AGENTS.md"}:
                if item not in text and Path(item).name not in text:
                    warnings.append(f"registry may omit: {item}")

    md_files: list[Path] = list(docs.rglob("*.md")) if docs.exists() else []
    for extra in (root / "README.md", root / "AGENTS.md"):
        if extra.is_file():
            md_files.append(extra)

    for md in md_files:
        text = md.read_text(encoding="utf-8", errors="replace")
        for _label, target in LINK_RE.findall(text):
            target = target.strip()
            if not target or target.startswith(SKIP_LINK_PREFIXES) or "://" in target:
                continue
            path_part = target.split("#", 1)[0]
            if not path_part:
                continue
            resolved = (md.parent / path_part).resolve()
            try:
                resolved.relative_to(root)
            except ValueError:
                errors.append(f"link escapes workspace in {md.relative_to(root)}: {target}")
                continue
            if not resolved.exists():
                errors.append(f"broken link in {md.relative_to(root)}: {target}")

    cfg = docs / "CONFIGURATION_REFERENCE.md"
    if cfg.is_file() and env_example.is_file():
        example_names: set[str] = set()
        for line in env_example.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            example_names.add(line.split("=", 1)[0].strip())
        documented = set(ENV_NAME_RE.findall(cfg.read_text(encoding="utf-8", errors="replace")))
        documented_env = {n for n in documented if n not in ENV_IGNORE and "_" in n}
        for name in sorted(documented_env - example_names - {"DR_EXPORT_DIR"}):
            if looks_like_env(name):
                errors.append(f"CONFIGURATION_REFERENCE env not in .env.example: {name}")
    else:
        warnings.append("skip env compare (missing files)")

    readme = root / "README.md"
    if readme.is_file():
        text = readme.read_text(encoding="utf-8", errors="replace")
        for name in ("validate.py", "preflight.py", "run_smoke.py", "setup.py"):
            if name in text and not (qa_scripts / name).is_file():
                warnings.append(f"README mentions missing script: {name}")

    for base in (docs, root / "coordination"):
        if not base.exists():
            continue
        for path in base.rglob("*.md"):
            if SECRET_RE.search(path.read_text(encoding="utf-8", errors="replace")):
                errors.append(f"possible secret material in {path.relative_to(root)}")

    titles: dict[str, list[str]] = {}
    if docs.exists():
        for md in docs.rglob("*.md"):
            for line in md.read_text(encoding="utf-8", errors="replace").splitlines()[:5]:
                if line.startswith("# "):
                    titles.setdefault(line[2:].strip().lower(), []).append(
                        str(md.relative_to(root))
                    )
                    break
    for title, paths in titles.items():
        if len(paths) > 1:
            warnings.append(f"duplicate title '{title}': {', '.join(paths)}")

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    errors, warnings = run_checks(args.root.resolve())

    for warning in warnings:
        print(f"WARN: {warning}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"FAIL: {len(errors)} error(s), {len(warnings)} warning(s)")
        return 1
    print(f"PASS: 0 errors, {len(warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
