# Documentation Registry

| Path | Purpose | Owner | Audience | Class | Status | Last verified | Review triggers | Related |
|---|---|---|---|---|---|---|---|---|
| README.md | Workspace entry | documentation | all | PUBLIC | DRAFT→NEEDS_REVIEW | 2026-11-18 | structure, capabilities | docs/INDEX |
| AGENTS.md | Agent network | coordinator | agents | INTERNAL | VERIFIED | 2026-11-18 | agent roles | coordination/ |
| docs/DOCUMENTATION_POLICY.md | SoT policy | documentation | agents | INTERNAL | VERIFIED | 2026-11-18 | policy changes | registry |
| docs/DOCUMENTATION_REGISTRY.md | Doc metadata | documentation | documentation | INTERNAL | NEEDS_REVIEW | 2026-11-18 | any doc add/remove | index |
| docs/DOCUMENTATION_INDEX.md | Navigation | documentation | all | INTERNAL | NEEDS_REVIEW | 2026-11-18 | new docs | registry |
| docs/PROJECT_OVERVIEW.md | Scope | documentation | all | INTERNAL | NEEDS_REVIEW | 2026-11-18 | product scope | overview |
| docs/SYSTEM_ARCHITECTURE.md | Architecture | voice-development + documentation | eng | INTERNAL | NEEDS_REVIEW | 2026-11-18 | integrations | voice-agent |
| docs/TECHNOLOGY_STACK.md | Stack | documentation | eng | INTERNAL | NEEDS_REVIEW | 2026-11-18 | deps | pyproject |
| docs/DIRECTORY_STRUCTURE.md | Tree | documentation | eng | INTERNAL | NEEDS_REVIEW | 2026-11-18 | moves | — |
| docs/CONFIGURATION_REFERENCE.md | Env names | integrations + documentation | eng | INTERNAL | NEEDS_REVIEW | 2026-11-18 | .env.example | QA |
| docs/development/* | Dev guides | documentation | eng | INTERNAL | NEEDS_REVIEW | 2026-11-18 | scripts | QA README |
| docs/clients/* | Client impl | documentation + integrations | implementers | INTERNAL | DRAFT | 2026-11-18 | features | voice-agent |
| docs/operations/* | Runbooks | documentation + testing | ops | INTERNAL | DRAFT | 2026-11-18 | failures | QA docs |
| docs/recovery/* | DR | documentation | recovery | CONFIDENTIAL paths INTERNAL | DRAFT | 2026-11-18 | remotes/backups | emergency |
| docs/agents/* | Docs agent | documentation | agents | INTERNAL | NEEDS_REVIEW | 2026-11-18 | authority | coordination |
| docs/verification/* | Audit/tests | documentation | agents | INTERNAL | NEEDS_REVIEW | 2026-11-18 | each release | checks |
| voice-agent/README.md | Demo SoT | voice-development | eng | INTERNAL | VERIFIED (prior) | 2026-11-08 | Retell/Cal.com | verification.md |
| retell-pet-grooming-qa/README.md | QA SoT | testing | eng | INTERNAL | VERIFIED (prior) | 2026-11-11 | QA scripts | docs/ |
| coordination/README.md | Bus SoT | coordinator | agents | INTERNAL | VERIFIED | 2026-11-15 | bus changes | ADR-001 |
| docs/uan/* | UAN-CORE specs | coordinator + documentation | agents | INTERNAL | NEEDS_REVIEW | 2026-11-18 | bus/commander changes | ADR-002 |
| coordination/config/uan.json | UAN runtime config | coordinator | agents | INTERNAL | VERIFIED | 2026-11-18 | aliases/routes | coord.py |
| domains/voice_agent_network/domain.yaml | VOICE-AIN metadata | coordinator | agents | INTERNAL | NEEDS_REVIEW | 2026-11-18 | domain pack | docs/uan |
| coordination/config/integrations.json | Integration registry | coordinator | agents | INTERNAL | VERIFIED | 2026-11-18 | approvals | security-approvals |
| docs/uan/master-system-specification.md | Master UAN spec | coordinator + documentation | agents | INTERNAL | NEEDS_REVIEW | 2026-11-18 | milestones | acceptance |
| docs/uan/memory-architecture.md | Memory plane | documentation | agents | INTERNAL | VERIFIED | 2026-11-18 | supermemory | memory README |

Statuses: VERIFIED | NEEDS_REVIEW | DRAFT | OUTDATED | BLOCKED. Do not mark VERIFIED without evidence.

## Required-path checklist (for check_docs)

| Path | Listed |
|---|---|
| docs/development/DEVELOPER_SETUP.md | yes — development/* |
| docs/recovery/EMERGENCY_RECOVERY_START_HERE.md | yes — recovery/* |
| docs/recovery/DISASTER_RECOVERY.md | yes — recovery/* |
| docs/recovery/BACKUP_INVENTORY.md | yes — recovery/* |
| docs/agents/DOCUMENTATION_AGENT.md | yes — docs/agents/* |
| docs/templates/DOCUMENTATION_IMPACT.md | yes — templates |
| docs/verification/INITIAL_DOCUMENTATION_AUDIT.md | yes — verification/* |

Updated: 2026-11-18.

## Path index (machine-readable)

- `docs/development/DEVELOPER_SETUP.md`
- `docs/recovery/EMERGENCY_RECOVERY_START_HERE.md`
- `docs/recovery/DISASTER_RECOVERY.md`
- `docs/recovery/BACKUP_INVENTORY.md`
- `docs/agents/DOCUMENTATION_AGENT.md`
- `docs/templates/DOCUMENTATION_IMPACT.md`
- `docs/verification/INITIAL_DOCUMENTATION_AUDIT.md`
- `docs/verification/DOCUMENTATION_TEST_REPORT.md`
- `docs/verification/DOCUMENTATION_HEALTH_REPORT.md`
- `docs/uan/existing-system-inventory.md`
- `docs/uan/architecture-gap-analysis.md`
- `docs/uan/core-architecture.md`
- `coordination/config/uan.json`
- `coordination/config/integrations.json`
- `docs/uan/memory-architecture.md`
- `docs/uan/master-system-specification.md`
- `docs/uan/security-approvals.md`
- `docs/uan/voice-evaluation-framework.md`
