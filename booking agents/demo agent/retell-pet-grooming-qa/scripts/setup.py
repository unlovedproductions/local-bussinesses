#!/usr/bin/env python3
"""Copy example configs if missing. Never overwrite local secrets."""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAIRS = [
    ("config/business.example.json", "config/business.json"),
    ("config/qa_vars.example.json", "config/qa_vars.json"),
    ("config/sandbox_proof.example.json", "config/sandbox_proof.json"),
    ("config/test_settings.example.json", "config/test_settings.json"),
    (".env.example", ".env"),
]


def main() -> int:
    for src_rel, dst_rel in PAIRS:
        src = ROOT / src_rel
        dst = ROOT / dst_rel
        if not src.exists():
            print("Missing", src)
            return 1
        if dst.exists():
            print("exists:", dst_rel)
            continue
        shutil.copyfile(src, dst)
        print("created:", dst_rel)
    print("Setup complete. Fill .env with local credentials; do not commit it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
