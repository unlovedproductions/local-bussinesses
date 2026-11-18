#!/usr/bin/env python3
"""UAN M5–M14 operations extensions for coord.py (stdlib only)."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

# Imported helpers are injected from coord.py to avoid circular imports at load time.
CoordAPI = dict[str, Any]


INTEGRATION_STATUSES = frozenset(
    {
        "DISCOVERED",
        "PROPOSED",
        "APPROVED_FOR_INSTALL",
        "INSTALLED",
        "AWAITING_AUTHORIZATION",
        "AUTHORIZED",
        "ENABLED",
        "DISABLED",
        "REJECTED",
    }
)
ENABLED_STATUSES = frozenset({"AUTHORIZED", "ENABLED"})
ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


def _now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def register(sub: Any, api: CoordAPI) -> None:
    """Attach new subcommands to coord argparse."""

    p = sub.add_parser("memory-status", help="Report semantic vs operational memory posture")
    p.set_defaults(func=lambda args: cmd_memory_status(args, api))

    p = sub.add_parser("memory-note", help="Publish shared-context note + Supermemory reminder")
    p.add_argument("--agent", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--body", required=True)
    p.add_argument("--id", default="")
    p.add_argument("--status", default="PROPOSED")
    p.add_argument("--evidence", default="")
    p.set_defaults(func=lambda args: cmd_memory_note(args, api))

    p = sub.add_parser("integrations", help="List integration registry")
    p.set_defaults(func=lambda args: cmd_integrations(args, api))

    p = sub.add_parser("integration-propose", help="Propose or upsert an integration record")
    p.add_argument("--file", required=True)
    p.set_defaults(func=lambda args: cmd_integration_propose(args, api))

    p = sub.add_parser("integration-set-status", help="Transition integration status with audit")
    p.add_argument("--id", required=True)
    p.add_argument("--status", required=True, choices=sorted(INTEGRATION_STATUSES))
    p.add_argument("--agent", required=True)
    p.add_argument("--note", default="")
    p.set_defaults(func=lambda args: cmd_integration_set_status(args, api))

    p = sub.add_parser("approvals", help="List approval audit records")
    p.set_defaults(func=lambda args: cmd_approvals(args, api))

    p = sub.add_parser("workflows", help="List VOICE-AIN workflows")
    p.set_defaults(func=lambda args: cmd_workflows(args, api))

    p = sub.add_parser("recovery-status", help="Summarize recovery readiness")
    p.set_defaults(func=lambda args: cmd_recovery_status(args, api))

    p = sub.add_parser("docs-health", help="Run documentation checks and summarize")
    p.set_defaults(func=lambda args: cmd_docs_health(args, api))

    p = sub.add_parser("ops", help="Operations dashboard snapshot (CLI)")
    p.set_defaults(func=lambda args: cmd_ops(args, api))

    p = sub.add_parser("report", help="Emit consolidated UAN ops report JSON")
    p.set_defaults(func=lambda args: cmd_report(args, api))


def integrations_path(api: CoordAPI) -> Path:
    return api["coord_root"]() / "config" / "integrations.json"


def approvals_dir(api: CoordAPI) -> Path:
    return api["coord_root"]() / "approvals" / "records"


def load_integrations(api: CoordAPI) -> dict[str, Any]:
    path = integrations_path(api)
    if not path.exists():
        return {"version": "1.0.0", "integrations": []}
    data = api["load_json"](path)
    if not isinstance(data, dict):
        api["die"](f"corrupt integrations registry: {path}")
    return data


def save_integrations(api: CoordAPI, data: dict[str, Any]) -> None:
    data["updated_at"] = _now()
    api["write_json"](integrations_path(api), data)


def write_approval(
    api: CoordAPI,
    *,
    integration_id: str,
    agent: str,
    action: str,
    status: str,
    note: str = "",
) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    rid = f"APR-{integration_id}-{stamp}"
    path = approvals_dir(api) / f"{rid}.json"
    api["write_json"](
        path,
        {
            "id": rid,
            "integration_id": integration_id,
            "agent": agent,
            "action": action,
            "status": status,
            "note": note,
            "at": _now(),
        },
    )
    return path


def cmd_memory_status(_: Any, api: CoordAPI) -> None:
    root = api["workspace_root"]()
    cfg = root / ".cursor" / ".supermemory" / "config.json"
    payload = {
        "semantic_memory": {
            "provider": "Supermemory Cursor MCP",
            "config_present": cfg.exists(),
            "config": api["load_json"](cfg) if cfg.exists() else None,
            "verified_write_retrieve": "2026-11-18 M5 harmless record (project container)",
            "authority": "lessons_only",
        },
        "operational_store": {
            "path": str(api["coord_root"]()),
            "authority": "tasks_messages_handoffs_approvals",
        },
        "shared_context": str(api["coord_root"]() / "shared-context"),
        "rule": "Do not use Supermemory as sole authority for transactional task state.",
    }
    print(json.dumps(payload, indent=2))


def cmd_memory_note(args: Any, api: CoordAPI) -> None:
    # Reuse publish-knowledge behavior via subprocess to keep one writer path
    cmd = [
        sys.executable,
        str(Path(__file__).resolve().parent / "coord.py"),
        "publish-knowledge",
        "--agent",
        args.agent,
        "--title",
        args.title,
        "--body",
        args.body,
        "--status",
        args.status,
    ]
    if args.id:
        cmd.extend(["--id", args.id])
    if args.evidence:
        cmd.extend(["--evidence", args.evidence])
    proc = subprocess.run(cmd, cwd=str(api["workspace_root"]()), capture_output=True, text=True)
    if proc.returncode != 0:
        api["die"](proc.stderr.strip() or "publish-knowledge failed")
    published = json.loads(proc.stdout)
    print(
        json.dumps(
            {
                "ok": True,
                "shared_context": published,
                "supermemory_reminder": {
                    "action": "Call Cursor MCP supermemory_add with the same durable lesson",
                    "do_not": "store credentials or task transactional state",
                },
            },
            indent=2,
        )
    )


def cmd_integrations(_: Any, api: CoordAPI) -> None:
    data = load_integrations(api)
    print(json.dumps(data, indent=2))


def cmd_integration_propose(args: Any, api: CoordAPI) -> None:
    item = api["load_json"](Path(args.file))
    if not isinstance(item, dict):
        api["die"]("integration file must be a JSON object")
    iid = item.get("id")
    if not isinstance(iid, str) or not ID_RE.match(iid):
        api["die"]("id must match [a-z0-9][a-z0-9._-]*")
    if item.get("status") not in INTEGRATION_STATUSES:
        item["status"] = "PROPOSED"
    for field in ("name", "provider", "purpose"):
        if not item.get(field):
            api["die"](f"missing required field: {field}")
    data = load_integrations(api)
    integrations = data.setdefault("integrations", [])
    if not isinstance(integrations, list):
        api["die"]("integrations must be a list")
    replaced = False
    for idx, existing in enumerate(integrations):
        if isinstance(existing, dict) and existing.get("id") == iid:
            integrations[idx] = item
            replaced = True
            break
    if not replaced:
        integrations.append(item)
    save_integrations(api, data)
    path = write_approval(
        api,
        integration_id=iid,
        agent=str(item.get("proposed_by") or "coordinator"),
        action="propose",
        status=str(item.get("status")),
        note="integration-propose",
    )
    print(json.dumps({"ok": True, "id": iid, "replaced": replaced, "approval": str(path)}, indent=2))


def cmd_integration_set_status(args: Any, api: CoordAPI) -> None:
    agent = api["resolve_agent"](args.agent)
    if args.status == "ENABLED" and agent != "coordinator":
        api["die"]("only coordinator may mark ENABLED")
    data = load_integrations(api)
    found = None
    for item in data.get("integrations") or []:
        if isinstance(item, dict) and item.get("id") == args.id:
            found = item
            break
    if found is None:
        api["die"](f"integration not found: {args.id}")
    previous = found.get("status")
    if args.status == "ENABLED" and previous not in {
        "AUTHORIZED",
        "ENABLED",
        "APPROVED_FOR_INSTALL",
        "INSTALLED",
        "AWAITING_AUTHORIZATION",
    }:
        api["die"](
            f"cannot ENABLE from {previous}; require authorization path first "
            "(managed workflow enforcement)"
        )
    if previous == "REJECTED" and args.status in ENABLED_STATUSES:
        api["die"]("rejected integrations cannot be enabled without a new proposal")
    found["status"] = args.status
    save_integrations(api, data)
    path = write_approval(
        api,
        integration_id=args.id,
        agent=agent,
        action="set_status",
        status=args.status,
        note=args.note or f"{previous} -> {args.status}",
    )
    print(
        json.dumps(
            {
                "ok": True,
                "id": args.id,
                "previous": previous,
                "status": args.status,
                "approval": str(path),
            },
            indent=2,
        )
    )


def cmd_approvals(_: Any, api: CoordAPI) -> None:
    rows = []
    folder = approvals_dir(api)
    if folder.exists():
        for path in sorted(folder.glob("APR-*.json")):
            rows.append(api["load_json"](path))
    print(json.dumps({"count": len(rows), "approvals": rows}, indent=2))


def cmd_workflows(_: Any, api: CoordAPI) -> None:
    root = api["workspace_root"]() / "domains" / "voice_agent_network" / "workflows"
    items = []
    if root.exists():
        for path in sorted(root.glob("*.yaml")):
            items.append({"id": path.stem, "path": str(path.relative_to(api["workspace_root"]()))})
    print(json.dumps({"count": len(items), "workflows": items}, indent=2))


def cmd_recovery_status(_: Any, api: CoordAPI) -> None:
    root = api["workspace_root"]()
    readiness = root / "docs" / "recovery" / "RECOVERY_READINESS.md"
    inventory = root / "docs" / "recovery" / "BACKUP_INVENTORY.md"
    export_dir = os.environ.get("DR_EXPORT_DIR", "").strip()
    payload = {
        "readiness_doc": str(readiness) if readiness.exists() else None,
        "inventory_doc": str(inventory) if inventory.exists() else None,
        "dr_export_dir_set": bool(export_dir),
        "dr_export_dir": export_dir or None,
        "secondary_mirror": "MISSING",
        "classification": "DOCUMENTED_BUT_UNTESTED"
        if not export_dir
        else "BACKUP_IDENTIFIED",
        "emergency_entry": "docs/recovery/EMERGENCY_RECOVERY_START_HERE.md",
        "note": "Documented procedures are not verified restores.",
    }
    print(json.dumps(payload, indent=2))


def cmd_docs_health(_: Any, api: CoordAPI) -> None:
    script = api["workspace_root"]() / "scripts" / "documentation" / "check_docs.py"
    proc = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(api["workspace_root"]()),
        capture_output=True,
        text=True,
    )
    print(
        json.dumps(
            {
                "ok": proc.returncode == 0,
                "returncode": proc.returncode,
                "stdout": proc.stdout.strip(),
                "stderr": proc.stderr.strip(),
            },
            indent=2,
        )
    )
    if proc.returncode != 0:
        raise SystemExit(proc.returncode)


def _snapshot(api: CoordAPI) -> dict[str, Any]:
    root = api["workspace_root"]()
    integ = load_integrations(api)
    tasks = list((api["coord_root"]() / "tasks" / "records").glob("TASK-*.json"))
    handoffs = list((api["coord_root"]() / "handoffs").glob("HANDOFF-*.json"))
    inbox = list((api["coord_root"]() / "messages" / "inbox").glob("MSG-*.json"))
    return {
        "workspace": str(root),
        "domain_id": "voice_agent_network",
        "agents": sorted(api["KNOWN_AGENTS"]),
        "inbox_open": len(inbox),
        "task_records": len(tasks),
        "handoff_json": len(handoffs),
        "integrations": [
            {"id": i.get("id"), "status": i.get("status")}
            for i in integ.get("integrations") or []
            if isinstance(i, dict)
        ],
        "max_concurrent_specialists": api["max_concurrent"](),
        "dr_export_dir_set": bool(os.environ.get("DR_EXPORT_DIR", "").strip()),
        "execution_model": "repo_bus_primary_cursor_task_secondary",
        "generated_at": _now(),
    }


def cmd_ops(_: Any, api: CoordAPI) -> None:
    print(json.dumps({"view": "Universal Command Center", **_snapshot(api)}, indent=2))


def cmd_report(_: Any, api: CoordAPI) -> None:
    snap = _snapshot(api)
    snap["views"] = [
        "command_center",
        "communication",
        "voice_projects",
        "testing",
        "memory",
        "integrations",
        "documentation_health",
        "disaster_recovery",
    ]
    snap["note"] = "Metrics are persisted counts only; no fictitious KPIs."
    print(json.dumps(snap, indent=2))
