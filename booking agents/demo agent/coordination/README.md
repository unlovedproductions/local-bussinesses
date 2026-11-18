# Coordination Operating Guide

Persistent multi-agent handoffs for the AI Voice Agent workspace.

**Delivery model:** asynchronous repo bus with explicit inbox polling. Not real-time messaging.

**UAN-CORE:** this bus is the Universal Multi-Agent Network core (ADR-002). Commander = `coordinator` (00). Domain pack = VOICE-AIN.

## Quick start

From workspace root (`demo agent/`):

```bash
python3 coordination/scripts/coord.py status
python3 coordination/scripts/coord.py register
python3 coordination/scripts/coord.py plan --objective "documentation recovery audit"
python3 coordination/scripts/coord.py inbox --agent voice-development
python3 coordination/scripts/coord.py send --file path/to/message.json
python3 coordination/scripts/coord.py ack --id MSG-... --agent voice-development
python3 coordination/scripts/coord.py task-list --status READY
python3 coordination/scripts/coord.py handoff-list --open-only
```

## Session startup (every agent)

1. Read root `AGENTS.md` and your role card under `coordination/agents/`.
2. Run `coord.py inbox --agent <your-id>` (UAN aliases like `70` accepted).
3. Check `task-list --owner <id>`, `handoff-list --recipient <id> --open-only`, and `tasks/active.md`.
4. Confirm branch/worktree; do not edit another agent's uncommitted work.
5. Claim / transition tasks before modifying shared files.

## Session completion

1. Update message/task/handoff status with evidence.
2. Publish verified knowledge to `shared-context/` when facts change.
3. Create JSON handoffs for other agents (`handoff-create`) — file write does not start them.
4. For sales prospects: `prepare-prospect` then optionally `export-erpnext`.
5. Never claim ERPNext sync succeeded while `crm-staging/sync-status.md` is BLOCKED.

## Layout

| Path | Purpose |
|---|---|
| `config/uan.json` | Aliases, capability routes, concurrency |
| `agents/` | Registry + role cards |
| `messages/inbox/` | Open messages (JSON) |
| `messages/archive/` | Terminal messages |
| `handoffs/` | JSON handoffs (+ optional MD notes) |
| `tasks/records/` | Structured task lifecycle |
| `tasks/attempts/` | Execution attempt log |
| `tasks/claims/` | Ownership claims |
| `decisions/` | ADRs |
| `shared-context/` | Verified project intelligence |
| `crm-staging/` | ERPNext-ready prospect packages |
| `scripts/coord.py` | Lifecycle + Commander CLI |

## Safety

- No secrets, API keys, or real customer PII in git.
- Distinguishing VERIFIED / INFERRED / PROPOSED / BLOCKED is mandatory.
- Registry entries ≠ running agents.
- Max concurrent specialist RUNNING tasks: 3 (override `UAN_MAX_CONCURRENT`).
