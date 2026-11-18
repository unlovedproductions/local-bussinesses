# Agent Registry

Logical roles for this workspace. **A registry row is not proof a process is running.**

| Agent ID | Role | Status | Handoff / inbox | Owned components | Last verified activity |
|---|---|---|---|---|---|
| `coordinator` | Project Coordinator | Logical | `messages/inbox/` recipient=`coordinator` | `coordination/` | 2026-11-15 — system bootstrap |
| `market-research` | Local Business Market Research | Logical | recipient=`market-research` | `research/local-market-intelligence/`, prospect authorship | 2026-11-15 — system bootstrap |
| `voice-development` | AI Voice Development | Logical | recipient=`voice-development` | `voice-agent/` | 2026-11-15 — system bootstrap |
| `integrations` | Integration Agent | Logical | recipient=`integrations` | Cal.com/Retell docs, `crm-staging/` field map + sync | 2026-11-15 — system bootstrap |
| `testing` | Testing & QA | Logical | recipient=`testing` | `retell-pet-grooming-qa/` | 2026-11-15 — system bootstrap |
| `documentation` | Documentation, Knowledge Integrity & Recovery Assurance | Logical | recipient=`documentation` | `docs/`, `scripts/documentation/`, root README | 2026-11-18 — docs system bootstrap |

## Capabilities (declared)

| Agent ID | Supported capabilities |
|---|---|
| `coordinator` | Priorities, ownership, blockers, ADRs, CRM stage conflict resolution, release-readiness coordination |
| `market-research` | Local prospect research, commercial discovery, `prepare-prospect`, sales positioning from verified intel |
| `voice-development` | Conversational flows, feasibility reviews, verified feature descriptions |
| `integrations` | Telephony/calendar/CRM/API review, ERPNext export mapping, blocked sync gate |
| `testing` | Scenario validation, defect investigation, reproducible test evidence |
| `documentation` | Doc integrity, registry, drift checks, impact assessments, recovery knowledge assurance |

## How to join

1. Add a role card under `coordination/agents/`.
2. Add the ID to schemas + `coord.py` `KNOWN_AGENTS`.
3. Update this registry table.
4. Do not claim the agent is active until a session records inbox/task evidence.
