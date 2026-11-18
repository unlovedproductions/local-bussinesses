#!/usr/bin/env python3
"""Repository coordination CLI — stdlib only."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

KNOWN_AGENTS = frozenset(
    {
        "coordinator",
        "market-research",
        "voice-development",
        "integrations",
        "testing",
        "documentation",
    }
)
RECIPIENTS = KNOWN_AGENTS | {"all"}
MESSAGE_TYPES = frozenset(
    {
        "DISCOVERY",
        "FEATURE_REQUEST",
        "TECHNICAL_REVIEW",
        "TASK_ASSIGNMENT",
        "STATUS_UPDATE",
        "BLOCKER",
        "TEST_RESULT",
        "DECISION",
        "QUESTION",
        "RESPONSE",
        "PROSPECT_READY",
        "CRM_SYNC_REQUEST",
        "DOCUMENTATION_REQUEST",
        "DOC_IMPACT",
    }
)
PRIORITIES = frozenset({"P0", "P1", "P2", "P3"})
STATUSES = frozenset(
    {
        "PROPOSED",
        "ACKNOWLEDGED",
        "IN_PROGRESS",
        "COMPLETED",
        "BLOCKED",
        "REJECTED",
        "CANCELLED",
    }
)
TRANSITIONS: dict[str, frozenset[str]] = {
    "PROPOSED": frozenset({"ACKNOWLEDGED", "REJECTED", "CANCELLED"}),
    "ACKNOWLEDGED": frozenset({"IN_PROGRESS", "BLOCKED", "REJECTED", "CANCELLED"}),
    "IN_PROGRESS": frozenset({"COMPLETED", "BLOCKED", "CANCELLED"}),
    "BLOCKED": frozenset({"IN_PROGRESS", "CANCELLED", "REJECTED"}),
    "COMPLETED": frozenset(),
    "REJECTED": frozenset(),
    "CANCELLED": frozenset(),
}
SALES_STAGES = frozenset(
    {
        "Lead",
        "Qualified",
        "Discovery",
        "Demo",
        "Proposal",
        "Negotiation",
        "Won",
        "Lost",
    }
)
MSG_ID_RE = re.compile(r"^MSG-[A-Za-z0-9._-]+$")
PROSPECT_ID_RE = re.compile(r"^PROSPECT-[A-Za-z0-9._-]+$")
TERMINAL = frozenset({"COMPLETED", "REJECTED", "CANCELLED"})


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def coord_root() -> Path:
    return workspace_root() / "coordination"


def inbox_dir() -> Path:
    return coord_root() / "messages" / "inbox"


def archive_dir() -> Path:
    return coord_root() / "messages" / "archive"


def claims_dir() -> Path:
    return coord_root() / "tasks" / "claims"


def prospects_dir() -> Path:
    return coord_root() / "crm-staging" / "prospects"


def exports_dir() -> Path:
    return coord_root() / "crm-staging" / "exports"


def knowledge_dir() -> Path:
    return coord_root() / "shared-context"


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def die(msg: str, code: int = 1) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(code)


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        die(f"file not found: {path}")
    except json.JSONDecodeError as exc:
        die(f"invalid JSON in {path}: {exc}")


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def find_message(msg_id: str) -> tuple[Path, dict[str, Any]]:
    for folder in (inbox_dir(), archive_dir()):
        path = folder / f"{msg_id}.json"
        if path.exists():
            data = load_json(path)
            if not isinstance(data, dict):
                die(f"message is not an object: {path}")
            return path, data
    die(f"message not found: {msg_id}")


def validate_message(data: dict[str, Any], *, require_new_id: bool = True) -> list[str]:
    errors: list[str] = []
    msg_id = data.get("id")
    if not isinstance(msg_id, str) or not MSG_ID_RE.match(msg_id):
        errors.append("id must match MSG-[A-Za-z0-9._-]+")
    elif require_new_id:
        if (inbox_dir() / f"{msg_id}.json").exists() or (
            archive_dir() / f"{msg_id}.json"
        ).exists():
            errors.append(f"duplicate message id: {msg_id}")

    sender = data.get("sender")
    if sender not in KNOWN_AGENTS:
        errors.append(f"unknown sender: {sender}")

    recipient = data.get("recipient")
    if recipient not in RECIPIENTS:
        errors.append(f"unknown recipient: {recipient}")

    if data.get("type") not in MESSAGE_TYPES:
        errors.append(f"invalid type: {data.get('type')}")

    if data.get("priority") not in PRIORITIES:
        errors.append(f"invalid priority: {data.get('priority')}")

    if data.get("status") not in STATUSES:
        errors.append(f"invalid status: {data.get('status')}")

    for field in ("subject", "requested_action", "created_at"):
        if not isinstance(data.get(field), str) or not data.get(field):
            errors.append(f"missing or empty required field: {field}")

    return errors


def validate_prospect(data: dict[str, Any], *, require_new_id: bool = True) -> list[str]:
    errors: list[str] = []
    pid = data.get("id")
    if not isinstance(pid, str) or not PROSPECT_ID_RE.match(pid):
        errors.append("id must match PROSPECT-[A-Za-z0-9._-]+")
    elif require_new_id and (prospects_dir() / f"{pid}.json").exists():
        errors.append(f"duplicate prospect id: {pid}")

    if data.get("created_by") not in KNOWN_AGENTS:
        errors.append(f"unknown created_by: {data.get('created_by')}")

    if data.get("sales_stage") not in SALES_STAGES:
        errors.append(f"invalid sales_stage: {data.get('sales_stage')}")

    lead = data.get("lead")
    if not isinstance(lead, dict):
        errors.append("lead object required")
    else:
        for field in ("lead_name", "organization", "source"):
            if not lead.get(field):
                errors.append(f"lead.{field} required")

    opp = data.get("opportunity")
    if not isinstance(opp, dict):
        errors.append("opportunity object required")
    else:
        if not opp.get("title"):
            errors.append("opportunity.title required")
        if not opp.get("sales_stage"):
            errors.append("opportunity.sales_stage required")

    if data.get("verification_status") not in {
        "PROPOSED",
        "INFERRED",
        "VERIFIED",
        "STALE",
        "BLOCKED",
    }:
        errors.append(f"invalid verification_status: {data.get('verification_status')}")

    return errors


def transition(data: dict[str, Any], new_status: str) -> None:
    current = data.get("status")
    if current not in STATUSES:
        die(f"corrupt status: {current}")
    allowed = TRANSITIONS.get(current, frozenset())
    if new_status not in allowed:
        die(f"invalid transition {current} → {new_status}")
    data["status"] = new_status


def maybe_archive(path: Path, data: dict[str, Any]) -> Path:
    if data.get("status") not in TERMINAL:
        return path
    dest = archive_dir() / path.name
    write_json(dest, data)
    if path.resolve() != dest.resolve() and path.exists():
        path.unlink()
    return dest


def cmd_register(_: argparse.Namespace) -> None:
    registry = coord_root() / "agents" / "registry.md"
    if not registry.exists():
        die("registry.md missing")
    print("KNOWN_AGENTS:")
    for agent in sorted(KNOWN_AGENTS):
        print(f"  - {agent}")
    print(f"registry: {registry}")


def cmd_inbox(args: argparse.Namespace) -> None:
    agent = args.agent
    if agent not in KNOWN_AGENTS:
        die(f"unknown agent: {agent}")
    matches: list[dict[str, Any]] = []
    for path in sorted(inbox_dir().glob("MSG-*.json")):
        data = load_json(path)
        if not isinstance(data, dict):
            continue
        recipient = data.get("recipient")
        if recipient in {agent, "all"} and data.get("status") not in TERMINAL:
            matches.append(data)
    print(json.dumps({"agent": agent, "count": len(matches), "messages": matches}, indent=2))


def cmd_send(args: argparse.Namespace) -> None:
    data = load_json(Path(args.file))
    if not isinstance(data, dict):
        die("message file must be a JSON object")
    if "status" not in data:
        data["status"] = "PROPOSED"
    if "created_at" not in data:
        data["created_at"] = now_iso()
    errors = validate_message(data, require_new_id=True)
    if errors:
        die("; ".join(errors))
    path = inbox_dir() / f"{data['id']}.json"
    write_json(path, data)
    print(json.dumps({"ok": True, "path": str(path), "id": data["id"]}, indent=2))


def cmd_ack(args: argparse.Namespace) -> None:
    path, data = find_message(args.id)
    if path.parent.name == "archive":
        die("cannot ack archived message")
    if args.agent not in KNOWN_AGENTS:
        die(f"unknown agent: {args.agent}")
    recipient = data.get("recipient")
    if recipient not in {args.agent, "all"}:
        die(f"agent {args.agent} is not recipient ({recipient})")
    transition(data, "ACKNOWLEDGED")
    data["ack"] = {
        "agent": args.agent,
        "at": now_iso(),
        "note": args.note or "",
    }
    write_json(path, data)
    print(json.dumps({"ok": True, "id": data["id"], "status": data["status"]}, indent=2))


def cmd_start(args: argparse.Namespace) -> None:
    path, data = find_message(args.id)
    if args.agent not in KNOWN_AGENTS:
        die(f"unknown agent: {args.agent}")
    if data.get("status") == "PROPOSED":
        transition(data, "ACKNOWLEDGED")
        data["ack"] = {
            "agent": args.agent,
            "at": now_iso(),
            "note": "auto-ack on start",
        }
    transition(data, "IN_PROGRESS")
    write_json(path, data)
    print(json.dumps({"ok": True, "id": data["id"], "status": data["status"]}, indent=2))


def cmd_complete(args: argparse.Namespace) -> None:
    path, data = find_message(args.id)
    if not args.summary:
        die("--summary is required for COMPLETED")
    transition(data, "COMPLETED")
    data["resolution"] = {
        "summary": args.summary,
        "at": now_iso(),
        "evidence": args.evidence or [],
    }
    path = maybe_archive(path, data)
    write_json(path, data)
    print(json.dumps({"ok": True, "id": data["id"], "status": data["status"], "path": str(path)}, indent=2))


def cmd_block(args: argparse.Namespace) -> None:
    path, data = find_message(args.id)
    if not args.reason:
        die("--reason is required for BLOCKED")
    transition(data, "BLOCKED")
    data["resolution"] = {
        "summary": args.summary or "blocked",
        "at": now_iso(),
        "blocker": args.reason,
        "evidence": args.evidence or [],
    }
    write_json(path, data)
    print(json.dumps({"ok": True, "id": data["id"], "status": data["status"]}, indent=2))


def cmd_reject(args: argparse.Namespace) -> None:
    path, data = find_message(args.id)
    transition(data, "REJECTED")
    data["resolution"] = {
        "summary": args.summary or "rejected",
        "at": now_iso(),
        "evidence": args.evidence or [],
    }
    path = maybe_archive(path, data)
    write_json(path, data)
    print(json.dumps({"ok": True, "id": data["id"], "status": data["status"], "path": str(path)}, indent=2))


def cmd_claim(args: argparse.Namespace) -> None:
    if args.agent not in KNOWN_AGENTS:
        die(f"unknown agent: {args.agent}")
    if not args.task:
        die("--task is required")
    claim_path = claims_dir() / f"{args.task}.json"
    if claim_path.exists():
        existing = load_json(claim_path)
        if isinstance(existing, dict) and existing.get("agent") != args.agent:
            die(
                f"conflicting task ownership: {args.task} owned by {existing.get('agent')}; escalate to coordinator"
            )
    claim = {
        "task_id": args.task,
        "agent": args.agent,
        "claimed_at": now_iso(),
        "note": args.note or "",
    }
    write_json(claim_path, claim)
    print(json.dumps({"ok": True, "claim": claim}, indent=2))


def cmd_publish_knowledge(args: argparse.Namespace) -> None:
    title = args.title
    body = args.body
    kid = args.id or f"KNOW-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    agent = args.agent
    if agent not in KNOWN_AGENTS:
        die(f"unknown agent: {agent}")
    status = args.status or "PROPOSED"
    path = knowledge_dir() / f"{kid.lower().replace('_', '-')}.md"
    content = (
        f"# Knowledge: {title}\n\n"
        f"| Field | Value |\n"
        f"|---|---|\n"
        f"| ID | {kid} |\n"
        f"| Description | {body} |\n"
        f"| Source / evidence | {args.evidence or 'n/a'} |\n"
        f"| Responsible agent | {agent} |\n"
        f"| Date recorded | {now_iso()} |\n"
        f"| Verification status | {status} |\n"
        f"| Related files or tasks | {args.related or 'n/a'} |\n"
        f"| Last reviewed | {now_iso()} |\n"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not args.force:
        die(f"knowledge file exists (use --force): {path}")
    path.write_text(content, encoding="utf-8")
    print(json.dumps({"ok": True, "path": str(path), "id": kid}, indent=2))


def cmd_prepare_prospect(args: argparse.Namespace) -> None:
    data = load_json(Path(args.file))
    if not isinstance(data, dict):
        die("prospect file must be a JSON object")
    if "created_at" not in data:
        data["created_at"] = now_iso()
    data["updated_at"] = now_iso()
    if "erpnext_sync" not in data:
        data["erpnext_sync"] = {
            "status": "NOT_SYNCED",
            "last_export_at": None,
            "blocker": "ERPNext site not configured",
        }
    errors = validate_prospect(data, require_new_id=not args.update)
    if errors:
        die("; ".join(errors))
    path = prospects_dir() / f"{data['id']}.json"
    write_json(path, data)
    print(json.dumps({"ok": True, "path": str(path), "id": data["id"]}, indent=2))


def map_export(prospect: dict[str, Any]) -> dict[str, Any]:
    lead = prospect.get("lead") or {}
    opp = prospect.get("opportunity") or {}
    party = prospect.get("party") or {}
    return {
        "meta": {
            "prospect_id": prospect.get("id"),
            "generated_at": now_iso(),
            "sales_stage": prospect.get("sales_stage"),
            "verification_status": prospect.get("verification_status"),
            "note": "Local export only — not pushed to ERPNext",
        },
        "Lead": {
            "lead_name": lead.get("lead_name"),
            "company_name": lead.get("organization"),
            "email_id": lead.get("email"),
            "mobile_no": lead.get("phone"),
            "source": lead.get("source"),
            "territory": lead.get("territory"),
            "industry": lead.get("industry"),
            "notes": lead.get("notes"),
        },
        "Opportunity": {
            "title": opp.get("title"),
            "opportunity_amount": opp.get("opportunity_amount"),
            "probability": opp.get("probability"),
            "sales_stage": opp.get("sales_stage"),
            "expected_closing": opp.get("expected_closing"),
            "next_action": opp.get("next_action"),
            "items": opp.get("items") or [],
            "verified_capabilities": prospect.get("verified_capabilities") or [],
        },
        "Customer": (
            {"customer_name": party.get("customer_name")}
            if party.get("customer_name")
            else None
        ),
        "Contact": (
            {
                "first_name": party.get("contact_name"),
                "address": party.get("address"),
            }
            if party.get("contact_name")
            else None
        ),
    }


def cmd_export_erpnext(args: argparse.Namespace) -> None:
    path = prospects_dir() / f"{args.id}.json"
    if not path.exists():
        die(f"prospect not found: {args.id}")
    prospect = load_json(path)
    if not isinstance(prospect, dict):
        die("corrupt prospect")
    errors = validate_prospect(prospect, require_new_id=False)
    if errors:
        die("; ".join(errors))
    payload = map_export(prospect)
    out = exports_dir() / f"{args.id}.json"
    write_json(out, payload)
    sync = prospect.setdefault("erpnext_sync", {})
    sync["status"] = "EXPORTED"
    sync["last_export_at"] = now_iso()
    sync["blocker"] = "ERPNext site not configured — export local only"
    prospect["updated_at"] = now_iso()
    write_json(path, prospect)
    print(json.dumps({"ok": True, "export": str(out), "sync_status": sync["status"]}, indent=2))


def cmd_sync_erpnext(args: argparse.Namespace) -> None:
    url = os.environ.get("ERPNEXT_URL", "").strip()
    key = os.environ.get("ERPNEXT_API_KEY", "").strip()
    secret = os.environ.get("ERPNEXT_API_SECRET", "").strip()
    status_file = coord_root() / "crm-staging" / "sync-status.md"
    if not (url and key and secret):
        die(
            "BLOCKED: ERPNext sync unavailable. Set ERPNEXT_URL, ERPNEXT_API_KEY, "
            f"ERPNEXT_API_SECRET and complete {status_file}. No network write performed."
        )
    # Credentials present still require explicit status flip after dry-run.
    text = status_file.read_text(encoding="utf-8") if status_file.exists() else ""
    if "**BLOCKED**" in text or "Status | **BLOCKED**" in text or "| **BLOCKED** |" in text:
        die(
            "BLOCKED: credentials present but sync-status.md is still BLOCKED. "
            "Complete dry-run Lead create and update sync-status before enabling live sync."
        )
    die(
        "BLOCKED: live sync implementation not enabled in this pass "
        f"(prospect={args.id}). Export locally with export-erpnext."
    )


def cmd_status(_: argparse.Namespace) -> None:
    inbox = list(inbox_dir().glob("MSG-*.json"))
    archive = list(archive_dir().glob("MSG-*.json"))
    prospects = list(prospects_dir().glob("PROSPECT-*.json"))
    claims = list(claims_dir().glob("*.json"))
    print(
        json.dumps(
            {
                "workspace": str(workspace_root()),
                "inbox_count": len(inbox),
                "archive_count": len(archive),
                "prospect_count": len(prospects),
                "claim_count": len(claims),
                "agents": sorted(KNOWN_AGENTS),
                "erpnext_sync": "BLOCKED",
            },
            indent=2,
        )
    )


def cmd_verify_schema(args: argparse.Namespace) -> None:
    path = Path(args.file)
    data = load_json(path)
    if not isinstance(data, dict):
        die("file must be a JSON object")
    kind = args.kind
    if kind == "message":
        errors = validate_message(data, require_new_id=False)
    elif kind == "prospect":
        errors = validate_prospect(data, require_new_id=False)
    else:
        die(f"unknown kind: {kind}")
    if errors:
        die("; ".join(errors))
    print(json.dumps({"ok": True, "kind": kind, "file": str(path)}, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Multi-agent coordination CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("register", help="List registered agents")
    p.set_defaults(func=cmd_register)

    p = sub.add_parser("inbox", help="List open messages for an agent")
    p.add_argument("--agent", required=True)
    p.set_defaults(func=cmd_inbox)

    p = sub.add_parser("send", help="Validate and store a message")
    p.add_argument("--file", required=True)
    p.set_defaults(func=cmd_send)

    p = sub.add_parser("ack", help="Acknowledge a message")
    p.add_argument("--id", required=True)
    p.add_argument("--agent", required=True)
    p.add_argument("--note", default="")
    p.set_defaults(func=cmd_ack)

    p = sub.add_parser("start", help="Mark message IN_PROGRESS")
    p.add_argument("--id", required=True)
    p.add_argument("--agent", required=True)
    p.set_defaults(func=cmd_start)

    p = sub.add_parser("complete", help="Complete a message")
    p.add_argument("--id", required=True)
    p.add_argument("--summary", required=True)
    p.add_argument("--evidence", action="append", default=[])
    p.set_defaults(func=cmd_complete)

    p = sub.add_parser("block", help="Block a message")
    p.add_argument("--id", required=True)
    p.add_argument("--reason", required=True)
    p.add_argument("--summary", default="")
    p.add_argument("--evidence", action="append", default=[])
    p.set_defaults(func=cmd_block)

    p = sub.add_parser("reject", help="Reject a message")
    p.add_argument("--id", required=True)
    p.add_argument("--summary", default="rejected")
    p.add_argument("--evidence", action="append", default=[])
    p.set_defaults(func=cmd_reject)

    p = sub.add_parser("claim", help="Claim a task")
    p.add_argument("--task", required=True)
    p.add_argument("--agent", required=True)
    p.add_argument("--note", default="")
    p.set_defaults(func=cmd_claim)

    p = sub.add_parser("publish-knowledge", help="Publish a knowledge markdown entry")
    p.add_argument("--agent", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--body", required=True)
    p.add_argument("--id", default="")
    p.add_argument("--status", default="PROPOSED")
    p.add_argument("--evidence", default="")
    p.add_argument("--related", default="")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_publish_knowledge)

    p = sub.add_parser("prepare-prospect", help="Validate and store a prospect package")
    p.add_argument("--file", required=True)
    p.add_argument("--update", action="store_true")
    p.set_defaults(func=cmd_prepare_prospect)

    p = sub.add_parser("export-erpnext", help="Export local ERPNext-shaped payload")
    p.add_argument("--id", required=True)
    p.set_defaults(func=cmd_export_erpnext)

    p = sub.add_parser("sync-erpnext", help="Blocked live sync stub")
    p.add_argument("--id", required=True)
    p.set_defaults(func=cmd_sync_erpnext)

    p = sub.add_parser("status", help="Show coordination status")
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("verify-schema", help="Validate a message or prospect file")
    p.add_argument("--file", required=True)
    p.add_argument("--kind", choices=["message", "prospect"], required=True)
    p.set_defaults(func=cmd_verify_schema)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
