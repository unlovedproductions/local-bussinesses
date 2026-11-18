# AGENTS.md — AI Voice Booking Agents Workspace

Multi-agent coordination for the AI voice booking demo and QA auditor.

**Delivery model:** persistent asynchronous handoffs via `coordination/` with explicit inbox polling. Not real-time messaging.

**UAN-CORE:** repo-bus evolution (ADR-002). Domain pack: **VOICE-AIN**. Commander: `coordinator` (alias **00**). Docs/recovery: `documentation` (alias **70**).

## Network (logical roles)

| ID | UAN | Role | Details |
|---|---|---|---|
| `coordinator` | 00 | Universal Commander / Project Coordinator | [coordination/agents/coordinator.md](coordination/agents/coordinator.md) |
| `market-research` | 11 | Local Business Market Research | [coordination/agents/market-research.md](coordination/agents/market-research.md) |
| `voice-development` | 10/20 | AI Voice Development | [coordination/agents/voice-development.md](coordination/agents/voice-development.md) |
| `integrations` | 40 | Integrations (Cal.com/Retell/ERPNext staging) | [coordination/agents/integrations.md](coordination/agents/integrations.md) |
| `testing` | 50 | Testing & QA | [coordination/agents/testing.md](coordination/agents/testing.md) |
| `documentation` | 70 | Documentation, Knowledge Integrity & Recovery Assurance | [coordination/agents/documentation.md](coordination/agents/documentation.md) |

Registry: [coordination/agents/registry.md](coordination/agents/registry.md)  
UAN mapping: [docs/uan/agent-registry.md](docs/uan/agent-registry.md)

## Subprojects

- Voice demo assets: `voice-agent/`
- QA auditor (do not rebuild production receptionist): `retell-pet-grooming-qa/` — see its own `AGENTS.md` for QA safety
- Market intel: `research/local-market-intelligence/`
- ERPNext-ready CRM staging: `coordination/crm-staging/` (live sync **BLOCKED**)
- Workspace docs & recovery: `docs/` + `scripts/documentation/`
- VOICE-AIN metadata: `domains/voice_agent_network/domain.yaml`

## Startup procedure (every session)

1. Read this file and your role card.
2. Identify your agent ID (string ID or UAN alias such as `70`).
3. Inspect relevant `coordination/shared-context/`.
4. Discover work: `python3 coordination/scripts/coord.py inbox --agent <id>`
5. Check tasks: `python3 coordination/scripts/coord.py task-list --owner <id>` and `handoff-list --recipient <id> --open-only`
6. Confirm branch/worktree; commit coordination files before assuming other worktrees can see them.
7. Claim / transition tasks before editing shared areas.
8. Begin authorized work only.

## Completion procedure

1. Record completed work with evidence (`task-transition` / message `complete`).
2. Update message/task/handoff state via CLI.
3. Document unresolved issues / blockers.
4. Submit JSON handoffs when another agent must act (`handoff-create`).
5. Update verified shared knowledge when facts change.
6. For material code/config/infra/agent changes: file `docs/templates/DOCUMENTATION_IMPACT.md` and/or send `DOC_IMPACT` / `DOCUMENTATION_REQUEST` to `documentation`.
7. For prospects: `prepare-prospect` → `export-erpnext`; never claim ERPNext sync while blocked.
8. Identify next actions for the coordinator.

## Non-negotiables

- Do not disrupt live Retell/Cal.com production behavior without explicit approval.
- Do not fabricate agent acknowledgments or test passes.
- Do not store secrets or real customer PII in git.
- Distinguish VERIFIED / INFERRED / PROPOSED / BLOCKED.
- Registry entry ≠ running agent; file write ≠ session start.
- Documentation ownership ≠ production decision authority.
- Do not install MCP/plugins without approval; do not reinstall Supermemory.

## CLI

```bash
python3 coordination/scripts/coord.py status
python3 coordination/scripts/coord.py register
python3 coordination/scripts/coord.py plan --objective "review documentation recovery readiness"
python3 coordination/scripts/coord.py plan --objective "test integration calendar" --dispatch
python3 coordination/scripts/coord.py inbox --agent documentation
python3 coordination/scripts/coord.py task-list --status READY
python3 coordination/scripts/coord.py handoff-list --open-only
python3 coordination/scripts/coord.py memory-status
python3 coordination/scripts/coord.py integrations
python3 coordination/scripts/coord.py workflows
python3 coordination/scripts/coord.py ops
python3 coordination/scripts/coord.py recovery-status
python3 scripts/documentation/check_docs.py
python3 scripts/uan/run_m5_m14_acceptance.py
```

Operating guide: [coordination/README.md](coordination/README.md)  
UAN docs: [docs/uan/core-architecture.md](docs/uan/core-architecture.md)  
Docs index: [docs/DOCUMENTATION_INDEX.md](docs/DOCUMENTATION_INDEX.md)  
Recovery: [docs/recovery/EMERGENCY_RECOVERY_START_HERE.md](docs/recovery/EMERGENCY_RECOVERY_START_HERE.md)
