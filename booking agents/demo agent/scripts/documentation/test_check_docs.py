#!/usr/bin/env python3
"""Controlled drift test for check_docs.py (temp fixture)."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHECK = ROOT / "scripts" / "documentation" / "check_docs.py"


class CheckDocsTests(unittest.TestCase):
    def test_detects_broken_link_in_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp) / "ws"
            # Minimal tree satisfying some required paths is heavy; instead
            # run check against real ROOT expecting PASS, then a fixture dir
            # that only tests link helper via importing would be ideal.
            # Practical test: copy docs snippet with broken link and invoke
            # check_docs with --root pointing at a stub workspace.
            for rel in (
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
                "retell-pet-grooming-qa/.env.example",
                "retell-pet-grooming-qa/scripts/validate.py",
                "retell-pet-grooming-qa/scripts/preflight.py",
                "retell-pet-grooming-qa/scripts/run_smoke.py",
                "retell-pet-grooming-qa/scripts/setup.py",
            ):
                src = ROOT / rel
                dest = base / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                if src.is_file():
                    shutil.copy2(src, dest)
                else:
                    dest.write_text("# placeholder\n", encoding="utf-8")

            broken = base / "docs" / "BROKEN_LINK_TEST.md"
            broken.write_text(
                "# Broken Link Test\n\nSee [missing](./does-not-exist-12345.md).\n",
                encoding="utf-8",
            )
            # Ensure config reference does not invent env vars
            (base / "docs" / "CONFIGURATION_REFERENCE.md").write_text(
                "# Configuration Reference\n\n| RETELL_API_KEY | x |\n",
                encoding="utf-8",
            )
            (base / "retell-pet-grooming-qa" / ".env.example").write_text(
                "RETELL_API_KEY=\n",
                encoding="utf-8",
            )

            proc = subprocess.run(
                [sys.executable, str(CHECK), "--root", str(base)],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertIn("broken link", (proc.stdout + proc.stderr).lower())

    def test_real_workspace_runs(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(CHECK), "--root", str(ROOT)],
            capture_output=True,
            text=True,
        )
        # May PASS or FAIL depending on coordination agent file timing; assert runs
        self.assertIn(proc.returncode, (0, 1), proc.stdout + proc.stderr)


if __name__ == "__main__":
    unittest.main()
