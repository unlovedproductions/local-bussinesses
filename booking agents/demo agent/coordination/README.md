# Coordination Operating Guide

Persistent multi-agent handoffs for the AI Voice Agent workspace.

**Delivery model:** asynchronous repo bus with explicit inbox polling. Not real-time messaging.

## Quick start

From workspace root (`demo agent/`):

```bash
python3 coordination/scripts/coord.py status
python3 coordination/scripts/coord.py inbox --agent voice-development
python3 coordination/scripts/coord.py send --file path/to/message.json
python3 coordination/scripts/coord.py ack --id MSG-... --agent voice-development
```

## Session startup (every agent)

1. Read root `AGENTS.md` and your role card under `coordination/agents/`.
2. Run `coord.py inbox --agent <your-id>`.
3. Check `tasks/active.md` and unresolved `BLOCKER` messages.
4. Confirm branch/worktree; do not edit another agent's uncommitted work.
5. Claim ownership before modifying shared files.

## Session completion

1. Update message/task status with evidence.
2. Publish verified knowledge to `shared-context/` when facts change.
3. Create handoffs for other agents (do not rely on passive docs alone).
4. For sales prospects: `prepare-prospect` then optionally `export-erpnext`.
5. Never claim ERPNext sync succeeded while `crm-staging/sync-status.md` is BLOCKED.

## Layout

| Path | Purpose |
|---|---|
| `agents/` | Registry + role cards |
| `messages/inbox/` | Open messages (JSON) |
| `messages/archive/` | Terminal messages |
| `handoffs/` | Narrative handoff notes |
| `tasks/` | Backlog, active, claims |
| `decisions/` | ADRs |
| `shared-context/` | Verified project intelligence |
| `crm-staging/` | ERPNext-ready prospect packages |
| `scripts/coord.py` | Lifecycle CLI |

## Safety

- No secrets, API keys, or real customer PII in git.
- Distinguishing VERIFIED / INFERRED / PROPOSED / BLOCKED is mandatory.
- Registry entries ≠ running agents.
