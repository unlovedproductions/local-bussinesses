#!/usr/bin/env python3
"""Verification harness for coordination CLI (stdlib unittest)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COORD = ROOT / "coordination"
SCRIPT = COORD / "scripts" / "coord.py"


def run_coord(args: list[str], env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    full_env = os.environ.copy()
    if env:
        full_env.update(env)
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        env=full_env,
    )


class CoordTests(unittest.TestCase):
    def test_a_register_discoverable(self) -> None:
        proc = run_coord(["register"])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("market-research", proc.stdout)
        self.assertIn("voice-development", proc.stdout)
        self.assertTrue((COORD / "agents" / "registry.md").exists())

    def test_b_message_create(self) -> None:
        msg_id = "MSG-TEST-CREATE-001"
        for folder in (COORD / "messages" / "inbox", COORD / "messages" / "archive"):
            p = folder / f"{msg_id}.json"
            if p.exists():
                p.unlink()
        payload = {
            "id": msg_id,
            "sender": "market-research",
            "recipient": "voice-development",
            "created_at": "2026-11-15T16:00:00-08:00",
            "type": "FEATURE_REQUEST",
            "subject": "test create",
            "priority": "P2",
            "task_id": "TASK-TEST-001",
            "background": "harness",
            "evidence": ["coordination/scripts/test_coord.py"],
            "requested_action": "ack",
            "dependencies": [],
            "related_files": [],
            "status": "PROPOSED",
            "ack": None,
            "resolution": None,
        }
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as tmp:
            json.dump(payload, tmp)
            tmp_path = tmp.name
        try:
            proc = run_coord(["send", "--file", tmp_path])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertTrue((COORD / "messages" / "inbox" / f"{msg_id}.json").exists())
        finally:
            Path(tmp_path).unlink(missing_ok=True)
            # cleanup message for isolation of later runs
            for folder in (COORD / "messages" / "inbox", COORD / "messages" / "archive"):
                p = folder / f"{msg_id}.json"
                if p.exists():
                    p.unlink()

    def test_c_recipient_discovery(self) -> None:
        proc = run_coord(["inbox", "--agent", "voice-development"])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = json.loads(proc.stdout)
        self.assertEqual(data["agent"], "voice-development")
        self.assertIn("messages", data)

    def test_d_ack_and_invalid_transition(self) -> None:
        msg_id = "MSG-TEST-ACK-001"
        for folder in (COORD / "messages" / "inbox", COORD / "messages" / "archive"):
            p = folder / f"{msg_id}.json"
            if p.exists():
                p.unlink()
        payload = {
            "id": msg_id,
            "sender": "market-research",
            "recipient": "voice-development",
            "created_at": "2026-11-15T16:00:00-08:00",
            "type": "QUESTION",
            "subject": "ack test",
            "priority": "P3",
            "task_id": None,
            "background": "harness",
            "evidence": [],
            "requested_action": "ack",
            "dependencies": [],
            "related_files": [],
            "status": "PROPOSED",
            "ack": None,
            "resolution": None,
        }
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as tmp:
            json.dump(payload, tmp)
            tmp_path = tmp.name
        try:
            self.assertEqual(run_coord(["send", "--file", tmp_path]).returncode, 0)
            ack = run_coord(["ack", "--id", msg_id, "--agent", "voice-development"])
            self.assertEqual(ack.returncode, 0, ack.stderr)
            bad = run_coord(["ack", "--id", msg_id, "--agent", "voice-development"])
            self.assertNotEqual(bad.returncode, 0)
            self.assertIn("invalid transition", bad.stderr)
        finally:
            Path(tmp_path).unlink(missing_ok=True)
            for folder in (COORD / "messages" / "inbox", COORD / "messages" / "archive"):
                p = folder / f"{msg_id}.json"
                if p.exists():
                    p.unlink()

    def test_e_task_ownership_and_conflict(self) -> None:
        task = "TASK-TEST-CLAIM-001"
        claim = COORD / "tasks" / "claims" / f"{task}.json"
        if claim.exists():
            claim.unlink()
        first = run_coord(["claim", "--task", task, "--agent", "voice-development"])
        self.assertEqual(first.returncode, 0, first.stderr)
        conflict = run_coord(["claim", "--task", task, "--agent", "testing"])
        self.assertNotEqual(conflict.returncode, 0)
        self.assertIn("conflicting task ownership", conflict.stderr)
        if claim.exists():
            claim.unlink()

    def test_f_shared_knowledge(self) -> None:
        kid = "KNOW-TEST-001"
        path = COORD / "shared-context" / "know-test-001.md"
        if path.exists():
            path.unlink()
        proc = run_coord(
            [
                "publish-knowledge",
                "--agent",
                "voice-development",
                "--id",
                kid,
                "--title",
                "Harness knowledge",
                "--body",
                "Temporary verification entry",
                "--status",
                "VERIFIED",
                "--evidence",
                "coordination/scripts/test_coord.py",
            ]
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue(path.exists())
        text = path.read_text(encoding="utf-8")
        self.assertIn("VERIFIED", text)
        path.unlink()

    def test_g_session_persistence(self) -> None:
        # Re-read status in a fresh process — proves file persistence across invocations.
        proc1 = run_coord(["status"])
        self.assertEqual(proc1.returncode, 0, proc1.stderr)
        proc2 = run_coord(["status"])
        self.assertEqual(proc2.returncode, 0, proc2.stderr)
        self.assertEqual(json.loads(proc1.stdout)["workspace"], json.loads(proc2.stdout)["workspace"])

    def test_h_error_handling(self) -> None:
        missing = run_coord(["ack", "--id", "MSG-DOES-NOT-EXIST", "--agent", "testing"])
        self.assertNotEqual(missing.returncode, 0)
        dup_id = "MSG-TEST-DUP-001"
        for folder in (COORD / "messages" / "inbox", COORD / "messages" / "archive"):
            p = folder / f"{dup_id}.json"
            if p.exists():
                p.unlink()
        payload = {
            "id": dup_id,
            "sender": "coordinator",
            "recipient": "testing",
            "created_at": "2026-11-15T16:00:00-08:00",
            "type": "STATUS_UPDATE",
            "subject": "dup",
            "priority": "P3",
            "requested_action": "none",
            "status": "PROPOSED",
        }
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as tmp:
            json.dump(payload, tmp)
            tmp_path = tmp.name
        try:
            self.assertEqual(run_coord(["send", "--file", tmp_path]).returncode, 0)
            dup = run_coord(["send", "--file", tmp_path])
            self.assertNotEqual(dup.returncode, 0)
            self.assertIn("duplicate message id", dup.stderr)
            bad_recipient = dict(payload)
            bad_recipient["id"] = "MSG-TEST-BAD-RECIPIENT"
            bad_recipient["recipient"] = "not-an-agent"
            with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as tmp2:
                json.dump(bad_recipient, tmp2)
                tmp2_path = tmp2.name
            try:
                bad = run_coord(["send", "--file", tmp2_path])
                self.assertNotEqual(bad.returncode, 0)
                self.assertIn("unknown recipient", bad.stderr)
            finally:
                Path(tmp2_path).unlink(missing_ok=True)
        finally:
            Path(tmp_path).unlink(missing_ok=True)
            for folder in (COORD / "messages" / "inbox", COORD / "messages" / "archive"):
                p = folder / f"{dup_id}.json"
                if p.exists():
                    p.unlink()

    def test_j_prepare_prospect(self) -> None:
        pid = "PROSPECT-TEST-001"
        path = COORD / "crm-staging" / "prospects" / f"{pid}.json"
        if path.exists():
            path.unlink()
        payload = {
            "id": pid,
            "created_by": "market-research",
            "verification_status": "PROPOSED",
            "sales_stage": "Lead",
            "lead": {
                "lead_name": "Test Owner",
                "organization": "Test HVAC LLC",
                "email": None,
                "phone": None,
                "source": "harness",
                "territory": "Taft",
                "industry": "HVAC",
                "notes": "synthetic",
            },
            "opportunity": {
                "title": "AI voice intake",
                "opportunity_amount": 1000,
                "probability": 10,
                "sales_stage": "Lead",
                "expected_closing": None,
                "next_action": "Qualify",
                "items": ["voice agent"],
            },
        }
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as tmp:
            json.dump(payload, tmp)
            tmp_path = tmp.name
        try:
            proc = run_coord(["prepare-prospect", "--file", tmp_path])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertTrue(path.exists())
        finally:
            Path(tmp_path).unlink(missing_ok=True)
            if path.exists():
                path.unlink()

    def test_k_export_erpnext(self) -> None:
        pid = "PROSPECT-TEST-EXPORT-001"
        path = COORD / "crm-staging" / "prospects" / f"{pid}.json"
        export = COORD / "crm-staging" / "exports" / f"{pid}.json"
        for p in (path, export):
            if p.exists():
                p.unlink()
        payload = {
            "id": pid,
            "created_by": "market-research",
            "verification_status": "INFERRED",
            "sales_stage": "Qualified",
            "lead": {
                "lead_name": "Export Owner",
                "organization": "Export HVAC",
                "source": "harness",
                "notes": "synthetic",
            },
            "opportunity": {
                "title": "Export test",
                "sales_stage": "Qualified",
                "items": ["voice"],
            },
        }
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as tmp:
            json.dump(payload, tmp)
            tmp_path = tmp.name
        try:
            self.assertEqual(run_coord(["prepare-prospect", "--file", tmp_path]).returncode, 0)
            proc = run_coord(["export-erpnext", "--id", pid])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertTrue(export.exists())
            data = json.loads(export.read_text(encoding="utf-8"))
            self.assertIn("Lead", data)
            self.assertEqual(data["Lead"]["company_name"], "Export HVAC")
        finally:
            Path(tmp_path).unlink(missing_ok=True)
            for p in (path, export):
                if p.exists():
                    p.unlink()

    def test_l_sync_blocked(self) -> None:
        env = {
            "ERPNEXT_URL": "",
            "ERPNEXT_API_KEY": "",
            "ERPNEXT_API_SECRET": "",
        }
        proc = run_coord(["sync-erpnext", "--id", "PROSPECT-ANY"], env=env)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("BLOCKED", proc.stderr)

    def test_m_uan_register_aliases(self) -> None:
        proc = run_coord(["register"])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("documentation", proc.stdout)
        self.assertIn("70", proc.stdout)
        self.assertIn("max_concurrent_specialists", proc.stdout)

    def test_n_plan_and_task_lifecycle(self) -> None:
        records = COORD / "tasks" / "records"
        attempts = COORD / "tasks" / "attempts"
        created: list[Path] = []
        claim_paths: list[Path] = []
        try:
            plan = run_coord(
                [
                    "plan",
                    "--objective",
                    "documentation recovery release readiness",
                    "--dispatch",
                    "--priority",
                    "P2",
                ]
            )
            self.assertEqual(plan.returncode, 0, plan.stderr)
            payload = json.loads(plan.stdout)
            self.assertIn("documentation", payload["recommended_agents"])
            self.assertTrue(payload["documentation_impact"])
            self.assertGreaterEqual(len(payload["created_tasks"]), 1)
            for tid in payload["created_tasks"]:
                path = records / f"{tid}.json"
                created.append(path)
                claim_paths.append(COORD / "tasks" / "claims" / f"{tid}.json")
                self.assertTrue(path.exists())
            tid = payload["created_tasks"][0]
            path = records / f"{tid}.json"
            owner = json.loads(path.read_text(encoding="utf-8"))["owner"]
            start = run_coord(
                ["task-transition", "--id", tid, "--agent", owner, "--status", "RUNNING"]
            )
            self.assertEqual(start.returncode, 0, start.stderr)
            done = run_coord(
                [
                    "task-transition",
                    "--id",
                    tid,
                    "--agent",
                    owner,
                    "--status",
                    "COMPLETED",
                    "--summary",
                    "harness completion",
                    "--evidence",
                    "coordination/scripts/test_coord.py",
                    "--confidence",
                    "VERIFIED",
                ]
            )
            self.assertEqual(done.returncode, 0, done.stderr)
            task = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(task["status"], "COMPLETED")
            att = run_coord(["attempts", "--task", tid])
            self.assertEqual(att.returncode, 0, att.stderr)
            self.assertGreaterEqual(json.loads(att.stdout)["count"], 1)
        finally:
            task_ids = {p.stem for p in created}
            for p in created + claim_paths:
                if p.exists():
                    p.unlink()
            for path in attempts.glob("ATT-*.json"):
                try:
                    data = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                if data.get("task_id") in task_ids:
                    path.unlink(missing_ok=True)

    def test_o_handoff_lifecycle(self) -> None:
        hid = "HANDOFF-TEST-001"
        path = COORD / "handoffs" / f"{hid}.json"
        if path.exists():
            path.unlink()
        try:
            create = run_coord(
                [
                    "handoff-create",
                    "--id",
                    hid,
                    "--sender",
                    "coordinator",
                    "--recipient",
                    "documentation",
                    "--subject",
                    "test handoff",
                    "--requested-action",
                    "ack and close",
                    "--background",
                    "harness",
                    "--priority",
                    "P3",
                ]
            )
            self.assertEqual(create.returncode, 0, create.stderr)
            ack = run_coord(
                [
                    "handoff-transition",
                    "--id",
                    hid,
                    "--agent",
                    "documentation",
                    "--status",
                    "ACKNOWLEDGED",
                    "--note",
                    "harness ack",
                ]
            )
            self.assertEqual(ack.returncode, 0, ack.stderr)
            complete = run_coord(
                [
                    "handoff-transition",
                    "--id",
                    hid,
                    "--agent",
                    "documentation",
                    "--status",
                    "IN_PROGRESS",
                ]
            )
            self.assertEqual(complete.returncode, 0, complete.stderr)
            done = run_coord(
                [
                    "handoff-transition",
                    "--id",
                    hid,
                    "--agent",
                    "documentation",
                    "--status",
                    "COMPLETED",
                    "--summary",
                    "done",
                    "--evidence",
                    "coordination/scripts/test_coord.py",
                ]
            )
            self.assertEqual(done.returncode, 0, done.stderr)
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(data["status"], "COMPLETED")
            self.assertEqual(data["ack"]["agent"], "documentation")
        finally:
            if path.exists():
                path.unlink()

    def test_p_concurrency_limit(self) -> None:
        records = COORD / "tasks" / "records"
        claims = COORD / "tasks" / "claims"
        created: list[str] = []
        env = {"UAN_MAX_CONCURRENT": "1"}
        try:
            for i, agent in enumerate(("voice-development", "testing")):
                tid = f"TASK-TEST-CONC-{i}"
                created.append(tid)
                proc = run_coord(
                    [
                        "task-create",
                        "--id",
                        tid,
                        "--objective",
                        f"concurrency {i}",
                        "--created-by",
                        "coordinator",
                        "--owner",
                        agent,
                        "--status",
                        "READY",
                        "--priority",
                        "P3",
                    ],
                    env=env,
                )
                self.assertEqual(proc.returncode, 0, proc.stderr)
            first = run_coord(
                [
                    "task-transition",
                    "--id",
                    created[0],
                    "--agent",
                    "voice-development",
                    "--status",
                    "RUNNING",
                ],
                env=env,
            )
            self.assertEqual(first.returncode, 0, first.stderr)
            second = run_coord(
                [
                    "task-transition",
                    "--id",
                    created[1],
                    "--agent",
                    "testing",
                    "--status",
                    "RUNNING",
                ],
                env=env,
            )
            self.assertNotEqual(second.returncode, 0)
            self.assertIn("concurrency limit", second.stderr)
        finally:
            for tid in created:
                for folder in (records, claims):
                    p = folder / f"{tid}.json"
                    if p.exists():
                        p.unlink()
                for path in (COORD / "tasks" / "attempts").glob(f"ATT-{tid}-*.json"):
                    path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
