# AGENTS.md — AI Voice Booking Agents Workspace

Multi-agent coordination for the AI voice booking demo and QA auditor.

**Delivery model:** persistent asynchronous handoffs via `coordination/` with explicit inbox polling. Not real-time messaging.

## Network (logical roles)

| ID | Role | Details |
|---|---|---|
| `coordinator` | Project Coordinator | [coordination/agents/coordinator.md](coordination/agents/coordinator.md) |
| `market-research` | Local Business Market Research | [coordination/agents/market-research.md](coordination/agents/market-research.md) |
| `voice-development` | AI Voice Development | [coordination/agents/voice-development.md](coordination/agents/voice-development.md) |
| `integrations` | Integrations (Cal.com/Retell/ERPNext staging) | [coordination/agents/integrations.md](coordination/agents/integrations.md) |
| `testing` | Testing & QA | [coordination/agents/testing.md](coordination/agents/testing.md) |
| `documentation` | Documentation, Knowledge Integrity & Recovery Assurance | [coordination/agents/documentation.md](coordination/agents/documentation.md) |

Registry: [coordination/agents/registry.md](coordination/agents/registry.md)

## Subprojects

- Voice demo assets: `voice-agent/`
- QA auditor (do not rebuild production receptionist): `retell-pet-grooming-qa/` — see its own `AGENTS.md` for QA safety
- Market intel: `research/local-market-intelligence/`
- ERPNext-ready CRM staging: `coordination/crm-staging/` (live sync **BLOCKED**)
- Workspace docs & recovery: `docs/` + `scripts/documentation/`

## Startup procedure (every session)

1. Read this file and your role card.
2. Identify your agent ID.
3. Inspect relevant `coordination/shared-context/`.
4. Discover work: `python3 coordination/scripts/coord.py inbox --agent <id>`
5. Check `coordination/tasks/active.md` and open blockers.
6. Confirm branch/worktree; commit coordination files before assuming other worktrees can see them.
7. Claim tasks before editing shared areas: `coord.py claim --task TASK-... --agent <id>`
8. Begin authorized work only.

## Completion procedure

1. Record completed work with evidence.
2. Update message/task state via CLI.
3. Document unresolved issues / blockers.
4. Submit handoffs under `coordination/handoffs/` when another agent must act.
5. Update verified shared knowledge when facts change.
6. For material code/config/infra/agent changes: file `docs/templates/DOCUMENTATION_IMPACT.md` and/or send `DOC_IMPACT` / `DOCUMENTATION_REQUEST` to `documentation`.
7. For prospects: `prepare-prospect` → `export-erpnext`; never claim ERPNext sync while blocked.
8. Identify next actions for the coordinator.

## Non-negotiables

- Do not disrupt live Retell/Cal.com production behavior without explicit approval.
- Do not fabricate agent acknowledgments or test passes.
- Do not store secrets or real customer PII in git.
- Distinguish VERIFIED / INFERRED / PROPOSED / BLOCKED.
- Registry entry ≠ running agent.
- Documentation ownership ≠ production decision authority.

## CLI

```bash
python3 coordination/scripts/coord.py status
python3 coordination/scripts/coord.py inbox --agent <id>
python3 coordination/scripts/coord.py send --file path/to/message.json
python3 scripts/documentation/check_docs.py
```

Operating guide: [coordination/README.md](coordination/README.md)  
Docs index: [docs/DOCUMENTATION_INDEX.md](docs/DOCUMENTATION_INDEX.md)  
Recovery: [docs/recovery/EMERGENCY_RECOVERY_START_HERE.md](docs/recovery/EMERGENCY_RECOVERY_START_HERE.md)
