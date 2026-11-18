#!/usr/bin/env python3
"""Repository coordination CLI — UAN-CORE adapter (stdlib only).

Primary execution: persistent repo bus (messages/tasks/handoffs).
Secondary: same-session Cursor Task (documented; not invoked by this CLI).
Writing a file does not start another agent session.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import ops_ext

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
TASK_STATUSES = frozenset(
    {
        "PENDING",
        "READY",
        "RUNNING",
        "WAITING_APPROVAL",
        "BLOCKED",
        "COMPLETED",
        "FAILED",
        "CANCELLED",
    }
)
TASK_TRANSITIONS: dict[str, frozenset[str]] = {
    "PENDING": frozenset({"READY", "CANCELLED", "BLOCKED"}),
    "READY": frozenset({"RUNNING", "CANCELLED", "BLOCKED", "WAITING_APPROVAL"}),
    "RUNNING": frozenset(
        {"COMPLETED", "FAILED", "BLOCKED", "WAITING_APPROVAL", "CANCELLED"}
    ),
    "WAITING_APPROVAL": frozenset({"READY", "RUNNING", "CANCELLED", "BLOCKED"}),
    "BLOCKED": frozenset({"READY", "CANCELLED", "FAILED"}),
    "COMPLETED": frozenset(),
    "FAILED": frozenset({"READY", "CANCELLED"}),
    "CANCELLED": frozenset(),
}
HANDOFF_TRANSITIONS = TRANSITIONS
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
TASK_ID_RE = re.compile(r"^TASK-[A-Za-z0-9._-]+$")
HANDOFF_ID_RE = re.compile(r"^HANDOFF-[A-Za-z0-9._-]+$")
PROSPECT_ID_RE = re.compile(r"^PROSPECT-[A-Za-z0-9._-]+$")
TERMINAL = frozenset({"COMPLETED", "REJECTED", "CANCELLED"})
TASK_TERMINAL = frozenset({"COMPLETED", "FAILED", "CANCELLED"})
DEFAULT_PROJECT_ID = "ai-voice-booking-agents"
DEFAULT_DOMAIN_ID = "voice_agent_network"


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


def task_records_dir() -> Path:
    return coord_root() / "tasks" / "records"


def attempts_dir() -> Path:
    return coord_root() / "tasks" / "attempts"


def handoffs_dir() -> Path:
    return coord_root() / "handoffs"


def prospects_dir() -> Path:
    return coord_root() / "crm-staging" / "prospects"


def exports_dir() -> Path:
    return coord_root() / "crm-staging" / "exports"


def knowledge_dir() -> Path:
    return coord_root() / "shared-context"


def uan_config_path() -> Path:
    return coord_root() / "config" / "uan.json"


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


def load_uan_config() -> dict[str, Any]:
    path = uan_config_path()
    if not path.exists():
        return {
            "max_concurrent_specialists": 3,
            "aliases": {},
            "capability_routes": {},
            "domain_id": DEFAULT_DOMAIN_ID,
        }
    data = load_json(path)
    if not isinstance(data, dict):
        die(f"corrupt UAN config: {path}")
    return data


def max_concurrent() -> int:
    env = os.environ.get("UAN_MAX_CONCURRENT", "").strip()
    if env:
        try:
            return max(1, int(env))
        except ValueError:
            die(f"invalid UAN_MAX_CONCURRENT: {env}")
    cfg = load_uan_config()
    raw = cfg.get("max_concurrent_specialists", 3)
    try:
        return max(1, int(raw))
    except (TypeError, ValueError):
        return 3


def resolve_agent(raw: str) -> str:
    if raw in KNOWN_AGENTS:
        return raw
    aliases = load_uan_config().get("aliases") or {}
    if isinstance(aliases, dict):
        mapped = aliases.get(raw) or aliases.get(raw.lower())
        if mapped in KNOWN_AGENTS:
            return mapped
    die(f"unknown agent or alias: {raw}")


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


def validate_task(data: dict[str, Any], *, require_new_id: bool = True) -> list[str]:
    errors: list[str] = []
    tid = data.get("id")
    if not isinstance(tid, str) or not TASK_ID_RE.match(tid):
        errors.append("id must match TASK-[A-Za-z0-9._-]+")
    elif require_new_id and (task_records_dir() / f"{tid}.json").exists():
        errors.append(f"duplicate task id: {tid}")

    if data.get("created_by") not in KNOWN_AGENTS:
        errors.append(f"unknown created_by: {data.get('created_by')}")

    owner = data.get("owner")
    if owner is not None and owner not in KNOWN_AGENTS:
        errors.append(f"unknown owner: {owner}")

    if data.get("priority") not in PRIORITIES:
        errors.append(f"invalid priority: {data.get('priority')}")

    if data.get("status") not in TASK_STATUSES:
        errors.append(f"invalid status: {data.get('status')}")

    if not isinstance(data.get("objective"), str) or not data.get("objective"):
        errors.append("objective required")

    if not isinstance(data.get("domain_id"), str) or not data.get("domain_id"):
        errors.append("domain_id required")

    if not isinstance(data.get("created_at"), str) or not data.get("created_at"):
        errors.append("created_at required")

    return errors


def validate_handoff(data: dict[str, Any], *, require_new_id: bool = True) -> list[str]:
    errors: list[str] = []
    hid = data.get("id")
    if not isinstance(hid, str) or not HANDOFF_ID_RE.match(hid):
        errors.append("id must match HANDOFF-[A-Za-z0-9._-]+")
    elif require_new_id and (handoffs_dir() / f"{hid}.json").exists():
        errors.append(f"duplicate handoff id: {hid}")

    if data.get("sender") not in KNOWN_AGENTS:
        errors.append(f"unknown sender: {data.get('sender')}")
    if data.get("recipient") not in KNOWN_AGENTS:
        errors.append(f"unknown recipient: {data.get('recipient')}")
    if data.get("priority") not in PRIORITIES:
        errors.append(f"invalid priority: {data.get('priority')}")
    if data.get("status") not in STATUSES:
        errors.append(f"invalid status: {data.get('status')}")

    for field in (
        "project_id",
        "domain_id",
        "created_at",
        "subject",
        "background",
        "requested_action",
    ):
        if not isinstance(data.get(field), str) or not data.get(field):
            errors.append(f"missing or empty required field: {field}")

    return errors


def transition(data: dict[str, Any], new_status: str) -> None:
    current = data.get("status")
    if current not in STATUSES:
        die(f"corrupt status: {current}")
    allowed = TRANSITIONS.get(current, frozenset())
    if new_status not in allowed:
        die(f"invalid transition {current} → {new_status}")
    data["status"] = new_status


def transition_task(data: dict[str, Any], new_status: str) -> None:
    current = data.get("status")
    if current not in TASK_STATUSES:
        die(f"corrupt task status: {current}")
    allowed = TASK_TRANSITIONS.get(current, frozenset())
    if new_status not in allowed:
        die(f"invalid task transition {current} → {new_status}")
    data["status"] = new_status
    data["updated_at"] = now_iso()


def maybe_archive(path: Path, data: dict[str, Any]) -> Path:
    if data.get("status") not in TERMINAL:
        return path
    dest = archive_dir() / path.name
    write_json(dest, data)
    if path.resolve() != dest.resolve() and path.exists():
        path.unlink()
    return dest


def list_task_records() -> list[dict[str, Any]]:
    tasks: list[dict[str, Any]] = []
    for path in sorted(task_records_dir().glob("TASK-*.json")):
        data = load_json(path)
        if isinstance(data, dict):
            tasks.append(data)
    return tasks


def running_specialist_count() -> int:
    count = 0
    for task in list_task_records():
        if task.get("status") == "RUNNING" and task.get("owner") != "coordinator":
            count += 1
    return count


def find_task(task_id: str) -> tuple[Path, dict[str, Any]]:
    path = task_records_dir() / f"{task_id}.json"
    if not path.exists():
        die(f"task not found: {task_id}")
    data = load_json(path)
    if not isinstance(data, dict):
        die(f"corrupt task: {path}")
    return path, data


def find_handoff(handoff_id: str) -> tuple[Path, dict[str, Any]]:
    path = handoffs_dir() / f"{handoff_id}.json"
    if not path.exists():
        die(f"handoff not found: {handoff_id}")
    data = load_json(path)
    if not isinstance(data, dict):
        die(f"corrupt handoff: {path}")
    return path, data


def record_attempt(
    *,
    task_id: str,
    agent: str,
    action: str,
    outcome: str,
    note: str = "",
) -> dict[str, Any]:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    attempt_id = f"ATT-{task_id}-{stamp}"
    attempt = {
        "id": attempt_id,
        "task_id": task_id,
        "agent": agent,
        "action": action,
        "outcome": outcome,
        "note": note,
        "at": now_iso(),
    }
    write_json(attempts_dir() / f"{attempt_id}.json", attempt)
    return attempt


def cmd_register(_: argparse.Namespace) -> None:
    registry = coord_root() / "agents" / "registry.md"
    if not registry.exists():
        die("registry.md missing")
    cfg = load_uan_config()
    aliases = cfg.get("aliases") or {}
    reverse: dict[str, list[str]] = {a: [] for a in sorted(KNOWN_AGENTS)}
    if isinstance(aliases, dict):
        for alias, agent in aliases.items():
            if agent in reverse:
                reverse[agent].append(str(alias))
    print("KNOWN_AGENTS:")
    for agent in sorted(KNOWN_AGENTS):
        alias_list = ", ".join(sorted(reverse[agent])) or "(none)"
        print(f"  - {agent}  [UAN aliases: {alias_list}]")
    print(f"registry: {registry}")
    print(f"uan_config: {uan_config_path()}")
    print(f"max_concurrent_specialists: {max_concurrent()}")
    print(f"domain_id: {cfg.get('domain_id', DEFAULT_DOMAIN_ID)}")
    print(
        "execution_note: repo-bus is authoritative; Cursor Task is same-session only; "
        "files do not auto-start agents."
    )


def cmd_inbox(args: argparse.Namespace) -> None:
    agent = resolve_agent(args.agent)
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
    agent = resolve_agent(args.agent)
    recipient = data.get("recipient")
    if recipient not in {agent, "all"}:
        die(f"agent {agent} is not recipient ({recipient})")
    transition(data, "ACKNOWLEDGED")
    data["ack"] = {
        "agent": agent,
        "at": now_iso(),
        "note": args.note or "",
    }
    write_json(path, data)
    print(json.dumps({"ok": True, "id": data["id"], "status": data["status"]}, indent=2))


def cmd_start(args: argparse.Namespace) -> None:
    path, data = find_message(args.id)
    agent = resolve_agent(args.agent)
    if data.get("status") == "PROPOSED":
        transition(data, "ACKNOWLEDGED")
        data["ack"] = {
            "agent": agent,
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
    agent = resolve_agent(args.agent)
    if not args.task:
        die("--task is required")
    claim_path = claims_dir() / f"{args.task}.json"
    if claim_path.exists():
        existing = load_json(claim_path)
        if isinstance(existing, dict) and existing.get("agent") != agent:
            die(
                f"conflicting task ownership: {args.task} owned by {existing.get('agent')}; escalate to coordinator"
            )
    claim = {
        "task_id": args.task,
        "agent": agent,
        "claimed_at": now_iso(),
        "note": args.note or "",
    }
    write_json(claim_path, claim)
    print(json.dumps({"ok": True, "claim": claim}, indent=2))


def cmd_publish_knowledge(args: argparse.Namespace) -> None:
    title = args.title
    body = args.body
    kid = args.id or f"KNOW-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    agent = resolve_agent(args.agent)
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
    tasks = list_task_records()
    handoffs = list(handoffs_dir().glob("HANDOFF-*.json"))
    by_status: dict[str, int] = {}
    for task in tasks:
        st = str(task.get("status"))
        by_status[st] = by_status.get(st, 0) + 1
    print(
        json.dumps(
            {
                "workspace": str(workspace_root()),
                "inbox_count": len(inbox),
                "archive_count": len(archive),
                "prospect_count": len(prospects),
                "claim_count": len(claims),
                "task_record_count": len(tasks),
                "task_status_counts": by_status,
                "running_specialists": running_specialist_count(),
                "max_concurrent_specialists": max_concurrent(),
                "handoff_json_count": len(handoffs),
                "agents": sorted(KNOWN_AGENTS),
                "domain_id": load_uan_config().get("domain_id", DEFAULT_DOMAIN_ID),
                "erpnext_sync": "BLOCKED",
                "execution_model": "repo_bus_primary_cursor_task_secondary",
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
    elif kind == "task":
        errors = validate_task(data, require_new_id=False)
    elif kind == "handoff":
        errors = validate_handoff(data, require_new_id=False)
    else:
        die(f"unknown kind: {kind}")
    if errors:
        die("; ".join(errors))
    print(json.dumps({"ok": True, "kind": kind, "file": str(path)}, indent=2))


def cmd_plan(args: argparse.Namespace) -> None:
    """Agent 00 planning — deterministic capability routing. Does not execute agents."""
    objective = args.objective.strip()
    if not objective:
        die("objective required")
    cfg = load_uan_config()
    routes = cfg.get("capability_routes") or {}
    text = objective.lower()
    selected: list[str] = []
    matched_caps: list[str] = []
    if isinstance(routes, dict):
        for cap, agents in routes.items():
            if str(cap).lower() in text:
                matched_caps.append(str(cap))
                if isinstance(agents, list):
                    for agent in agents:
                        if agent in KNOWN_AGENTS and agent not in selected:
                            selected.append(agent)
    if not selected:
        selected = ["voice-development", "testing"]
        matched_caps = ["default_voice_quality"]
    # Documentation impact when triggers appear in objective
    triggers = cfg.get("documentation_impact_triggers") or []
    doc_impact = False
    if isinstance(triggers, list):
        for trigger in triggers:
            token = str(trigger).replace("_", " ")
            if token in text or str(trigger) in text:
                doc_impact = True
                break
    if any(k in text for k in ("doc", "recover", "deploy", "release", "runbook")):
        doc_impact = True
    if doc_impact and "documentation" not in selected:
        selected.append("documentation")
    # Always keep commander ownership of plan
    plan = {
        "commander": "coordinator",
        "uan_alias": "00",
        "objective": objective,
        "domain_id": cfg.get("domain_id", DEFAULT_DOMAIN_ID),
        "matched_capabilities": matched_caps,
        "recommended_agents": selected,
        "documentation_impact": doc_impact,
        "max_concurrent_specialists": max_concurrent(),
        "execution_semantics": {
            "creates_tasks": False if not args.dispatch else True,
            "auto_starts_sessions": False,
            "cursor_task": "same-session secondary only — human/orchestrator must invoke",
            "repo_bus": "authoritative persistent coordination",
        },
        "created_at": now_iso(),
    }
    created_tasks: list[str] = []
    if args.dispatch:
        limit = max_concurrent()
        running = running_specialist_count()
        for agent in selected:
            if agent == "coordinator":
                continue
            if running >= limit:
                plan["blocked_by_concurrency"] = {
                    "running": running,
                    "limit": limit,
                    "skipped_from": agent,
                }
                break
            stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
            tid = f"TASK-PLAN-{stamp}-{agent[:4].upper()}"
            # avoid collisions in same second
            while (task_records_dir() / f"{tid}.json").exists():
                tid = f"{tid}-X"
            task = {
                "id": tid,
                "objective": f"[{agent}] {objective}",
                "owner": agent,
                "created_by": "coordinator",
                "created_at": now_iso(),
                "updated_at": now_iso(),
                "priority": args.priority,
                "status": "READY",
                "domain_id": cfg.get("domain_id", DEFAULT_DOMAIN_ID),
                "capabilities": matched_caps,
                "dependencies": [],
                "related_files": [],
                "acceptance": "Structured result with evidence; update message/handoff as needed",
                "verification": "coord.py task-get + evidence paths",
                "documentation_impact": doc_impact if agent == "documentation" else None,
                "idempotency_key": f"plan:{stamp}:{agent}",
                "result": None,
            }
            errors = validate_task(task, require_new_id=True)
            if errors:
                die("; ".join(errors))
            write_json(task_records_dir() / f"{tid}.json", task)
            write_json(
                claims_dir() / f"{tid}.json",
                {
                    "task_id": tid,
                    "agent": agent,
                    "claimed_at": now_iso(),
                    "note": "auto-claim from commander plan --dispatch",
                },
            )
            record_attempt(
                task_id=tid,
                agent="coordinator",
                action="dispatch",
                outcome="READY",
                note="Commander dispatch; recipient must poll and run manually or via Cursor Task",
            )
            created_tasks.append(tid)
            running += 1
    plan["created_tasks"] = created_tasks
    print(json.dumps(plan, indent=2))


def cmd_task_create(args: argparse.Namespace) -> None:
    created_by = resolve_agent(args.created_by)
    owner = resolve_agent(args.owner) if args.owner else None
    tid = args.id or f"TASK-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    cfg = load_uan_config()
    task = {
        "id": tid,
        "objective": args.objective,
        "owner": owner,
        "created_by": created_by,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "priority": args.priority,
        "status": args.status,
        "domain_id": args.domain_id or cfg.get("domain_id", DEFAULT_DOMAIN_ID),
        "capabilities": args.capability or [],
        "dependencies": args.dependency or [],
        "related_files": args.related_file or [],
        "acceptance": args.acceptance or "",
        "verification": args.verification or "",
        "documentation_impact": args.documentation_impact,
        "idempotency_key": args.idempotency_key or None,
        "result": None,
    }
    errors = validate_task(task, require_new_id=True)
    if errors:
        die("; ".join(errors))
    path = task_records_dir() / f"{tid}.json"
    write_json(path, task)
    record_attempt(
        task_id=tid,
        agent=created_by,
        action="create",
        outcome=task["status"],
        note=args.note or "",
    )
    print(json.dumps({"ok": True, "path": str(path), "task": task}, indent=2))


def cmd_task_list(args: argparse.Namespace) -> None:
    tasks = list_task_records()
    if args.status:
        tasks = [t for t in tasks if t.get("status") == args.status]
    if args.owner:
        owner = resolve_agent(args.owner)
        tasks = [t for t in tasks if t.get("owner") == owner]
    print(json.dumps({"count": len(tasks), "tasks": tasks}, indent=2))


def cmd_task_get(args: argparse.Namespace) -> None:
    _, task = find_task(args.id)
    print(json.dumps(task, indent=2))


def cmd_task_transition(args: argparse.Namespace) -> None:
    path, task = find_task(args.id)
    agent = resolve_agent(args.agent)
    new_status = args.status
    if new_status == "RUNNING":
        owner = task.get("owner")
        if owner and owner != agent and agent != "coordinator":
            die(f"only owner ({owner}) or coordinator may start RUNNING")
        if owner != "coordinator" and owner is not None:
            # concurrency gate for specialists
            if task.get("status") != "RUNNING":
                running = running_specialist_count()
                if running >= max_concurrent():
                    die(
                        f"concurrency limit reached ({running}/{max_concurrent()}). "
                        "Complete or cancel a RUNNING specialist task first."
                    )
        if owner is None:
            task["owner"] = agent
        claim_path = claims_dir() / f"{task['id']}.json"
        if claim_path.exists():
            existing = load_json(claim_path)
            if isinstance(existing, dict) and existing.get("agent") not in {agent, owner}:
                die(
                    f"conflicting task ownership: {task['id']} owned by {existing.get('agent')}"
                )
        else:
            write_json(
                claim_path,
                {
                    "task_id": task["id"],
                    "agent": agent,
                    "claimed_at": now_iso(),
                    "note": "claim on RUNNING",
                },
            )
    transition_task(task, new_status)
    if new_status in {"COMPLETED", "FAILED"}:
        if not args.summary:
            die("--summary required for COMPLETED/FAILED")
        task["result"] = {
            "summary": args.summary,
            "at": now_iso(),
            "evidence": args.evidence or [],
            "confidence": args.confidence or "UNVERIFIED",
            "risks": args.risk or [],
            "next_actions": args.next_action or [],
        }
    elif new_status == "BLOCKED":
        if not args.summary:
            die("--summary required for BLOCKED")
        task["result"] = {
            "summary": args.summary,
            "at": now_iso(),
            "evidence": args.evidence or [],
            "confidence": args.confidence or "UNVERIFIED",
            "risks": args.risk or [args.summary],
            "next_actions": args.next_action or [],
        }
    write_json(path, task)
    record_attempt(
        task_id=task["id"],
        agent=agent,
        action="transition",
        outcome=new_status,
        note=args.summary or args.note or "",
    )
    print(json.dumps({"ok": True, "task": task}, indent=2))


def cmd_handoff_create(args: argparse.Namespace) -> None:
    data = load_json(Path(args.file)) if args.file else None
    if data is None:
        data = {
            "id": args.id
            or f"HANDOFF-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            "sender": resolve_agent(args.sender),
            "recipient": resolve_agent(args.recipient),
            "project_id": args.project_id or DEFAULT_PROJECT_ID,
            "domain_id": args.domain_id
            or load_uan_config().get("domain_id", DEFAULT_DOMAIN_ID),
            "related_task": args.related_task,
            "related_message": args.related_message,
            "created_at": now_iso(),
            "subject": args.subject,
            "background": args.background or "",
            "evidence": args.evidence or [],
            "requested_action": args.requested_action,
            "priority": args.priority,
            "dependencies": args.dependency or [],
            "required_permissions": args.permission or [],
            "affected_files": args.affected_file or [],
            "artifact_refs": args.artifact or [],
            "status": "PROPOSED",
            "ack": None,
            "resolution": None,
        }
    if not isinstance(data, dict):
        die("handoff must be a JSON object")
    if "created_at" not in data:
        data["created_at"] = now_iso()
    if "status" not in data:
        data["status"] = "PROPOSED"
    errors = validate_handoff(data, require_new_id=True)
    if errors:
        die("; ".join(errors))
    path = handoffs_dir() / f"{data['id']}.json"
    write_json(path, data)
    print(
        json.dumps(
            {
                "ok": True,
                "path": str(path),
                "id": data["id"],
                "note": "Handoff persisted. Recipient must poll; file write does not start an agent.",
            },
            indent=2,
        )
    )


def cmd_handoff_transition(args: argparse.Namespace) -> None:
    path, data = find_handoff(args.id)
    agent = resolve_agent(args.agent)
    new_status = args.status
    if new_status == "ACKNOWLEDGED":
        if data.get("recipient") != agent and agent != "coordinator":
            die("only recipient or coordinator may acknowledge")
        transition(data, "ACKNOWLEDGED")
        data["ack"] = {"agent": agent, "at": now_iso(), "note": args.note or ""}
    elif new_status == "IN_PROGRESS":
        if data.get("status") == "PROPOSED":
            transition(data, "ACKNOWLEDGED")
            data["ack"] = {
                "agent": agent,
                "at": now_iso(),
                "note": args.note or "auto-ack on start",
            }
        transition(data, "IN_PROGRESS")
    elif new_status == "COMPLETED":
        if not args.summary:
            die("--summary required for COMPLETED")
        transition(data, "COMPLETED")
        data["resolution"] = {
            "summary": args.summary,
            "at": now_iso(),
            "evidence": args.evidence or [],
        }
    elif new_status == "BLOCKED":
        if not args.summary:
            die("--summary/--reason required for BLOCKED")
        transition(data, "BLOCKED")
        data["resolution"] = {
            "summary": args.summary,
            "at": now_iso(),
            "blocker": args.summary,
            "evidence": args.evidence or [],
        }
    elif new_status in {"REJECTED", "CANCELLED"}:
        transition(data, new_status)
        data["resolution"] = {
            "summary": args.summary or new_status.lower(),
            "at": now_iso(),
            "evidence": args.evidence or [],
        }
    else:
        die(f"unsupported handoff status: {new_status}")
    write_json(path, data)
    print(json.dumps({"ok": True, "handoff": data}, indent=2))


def cmd_handoff_list(args: argparse.Namespace) -> None:
    items: list[dict[str, Any]] = []
    for path in sorted(handoffs_dir().glob("HANDOFF-*.json")):
        data = load_json(path)
        if not isinstance(data, dict):
            continue
        if args.recipient:
            if data.get("recipient") != resolve_agent(args.recipient):
                continue
        if args.status and data.get("status") != args.status:
            continue
        if args.open_only and data.get("status") in TERMINAL:
            continue
        items.append(data)
    print(json.dumps({"count": len(items), "handoffs": items}, indent=2))


def cmd_attempts(args: argparse.Namespace) -> None:
    rows: list[dict[str, Any]] = []
    for path in sorted(attempts_dir().glob("ATT-*.json")):
        data = load_json(path)
        if not isinstance(data, dict):
            continue
        if args.task and data.get("task_id") != args.task:
            continue
        rows.append(data)
    print(json.dumps({"count": len(rows), "attempts": rows}, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="UAN-CORE coordination CLI (repo bus + commander helpers)"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("register", help="List registered agents and UAN aliases")
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

    p = sub.add_parser("verify-schema", help="Validate a message, prospect, task, or handoff")
    p.add_argument("--file", required=True)
    p.add_argument(
        "--kind",
        choices=["message", "prospect", "task", "handoff"],
        required=True,
    )
    p.set_defaults(func=cmd_verify_schema)

    p = sub.add_parser(
        "plan",
        help="Agent 00 plan: recommend specialists; optional --dispatch creates READY tasks",
    )
    p.add_argument("--objective", required=True)
    p.add_argument("--dispatch", action="store_true")
    p.add_argument("--priority", default="P2", choices=sorted(PRIORITIES))
    p.set_defaults(func=cmd_plan)

    p = sub.add_parser("task-create", help="Create a structured task record")
    p.add_argument("--objective", required=True)
    p.add_argument("--created-by", required=True)
    p.add_argument("--owner", default="")
    p.add_argument("--id", default="")
    p.add_argument("--priority", default="P2", choices=sorted(PRIORITIES))
    p.add_argument(
        "--status",
        default="PENDING",
        choices=sorted(TASK_STATUSES),
    )
    p.add_argument("--domain-id", default="")
    p.add_argument("--capability", action="append", default=[])
    p.add_argument("--dependency", action="append", default=[])
    p.add_argument("--related-file", action="append", default=[])
    p.add_argument("--acceptance", default="")
    p.add_argument("--verification", default="")
    p.add_argument("--documentation-impact", action="store_true")
    p.add_argument("--idempotency-key", default="")
    p.add_argument("--note", default="")
    p.set_defaults(func=cmd_task_create)

    p = sub.add_parser("task-list", help="List task records")
    p.add_argument("--status", default="")
    p.add_argument("--owner", default="")
    p.set_defaults(func=cmd_task_list)

    p = sub.add_parser("task-get", help="Get one task record")
    p.add_argument("--id", required=True)
    p.set_defaults(func=cmd_task_get)

    p = sub.add_parser("task-transition", help="Transition task status with attempt log")
    p.add_argument("--id", required=True)
    p.add_argument("--agent", required=True)
    p.add_argument("--status", required=True, choices=sorted(TASK_STATUSES))
    p.add_argument("--summary", default="")
    p.add_argument("--note", default="")
    p.add_argument("--evidence", action="append", default=[])
    p.add_argument("--confidence", default="")
    p.add_argument("--risk", action="append", default=[])
    p.add_argument("--next-action", action="append", default=[])
    p.set_defaults(func=cmd_task_transition)

    p = sub.add_parser("handoff-create", help="Create structured JSON handoff")
    p.add_argument("--file", default="")
    p.add_argument("--id", default="")
    p.add_argument("--sender", default="")
    p.add_argument("--recipient", default="")
    p.add_argument("--subject", default="")
    p.add_argument("--requested-action", default="")
    p.add_argument("--background", default="")
    p.add_argument("--priority", default="P2", choices=sorted(PRIORITIES))
    p.add_argument("--project-id", default="")
    p.add_argument("--domain-id", default="")
    p.add_argument("--related-task", default=None)
    p.add_argument("--related-message", default=None)
    p.add_argument("--evidence", action="append", default=[])
    p.add_argument("--dependency", action="append", default=[])
    p.add_argument("--permission", action="append", default=[])
    p.add_argument("--affected-file", action="append", default=[])
    p.add_argument("--artifact", action="append", default=[])
    p.set_defaults(func=cmd_handoff_create)

    p = sub.add_parser("handoff-transition", help="Acknowledge/start/complete handoffs")
    p.add_argument("--id", required=True)
    p.add_argument("--agent", required=True)
    p.add_argument("--status", required=True, choices=sorted(STATUSES))
    p.add_argument("--summary", default="")
    p.add_argument("--note", default="")
    p.add_argument("--evidence", action="append", default=[])
    p.set_defaults(func=cmd_handoff_transition)

    p = sub.add_parser("handoff-list", help="List JSON handoffs")
    p.add_argument("--recipient", default="")
    p.add_argument("--status", default="")
    p.add_argument("--open-only", action="store_true")
    p.set_defaults(func=cmd_handoff_list)

    p = sub.add_parser("attempts", help="List execution attempt records")
    p.add_argument("--task", default="")
    p.set_defaults(func=cmd_attempts)

    ops_ext.register(
        sub,
        {
            "workspace_root": workspace_root,
            "coord_root": coord_root,
            "load_json": load_json,
            "write_json": write_json,
            "die": die,
            "resolve_agent": resolve_agent,
            "max_concurrent": max_concurrent,
            "KNOWN_AGENTS": KNOWN_AGENTS,
        },
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    # Normalize optional empty strings for handoff-create file mode
    if getattr(args, "command", None) == "handoff-create" and not args.file:
        if not (args.sender and args.recipient and args.subject and args.requested_action):
            die(
                "handoff-create requires --file or --sender --recipient --subject --requested-action"
            )
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
