# Agent Registry

Logical roles for this workspace. **A registry row is not proof a process is running.**

UAN numeric IDs are aliases only; string IDs are authoritative in schemas/CLI. Config: [`../config/uan.json`](../config/uan.json).

| Agent ID | UAN | Role | Status | Handoff / inbox | Owned components | Last verified activity |
|---|---|---|---|---|---|---|
| `coordinator` | 00 | Universal Commander / Project Coordinator | Logical | `messages/inbox/` recipient=`coordinator` | `coordination/`, Commander plan/dispatch | 2026-11-18 — UAN M1–M4 |
| `market-research` | 11 | Local Business Market Research | Logical | recipient=`market-research` | `research/local-market-intelligence/`, prospect authorship | 2026-11-15 — system bootstrap |
| `voice-development` | 10/20 | AI Voice Development | Logical | recipient=`voice-development` | `voice-agent/` | 2026-11-15 — system bootstrap |
| `integrations` | 40 | Integration Agent | Logical | recipient=`integrations` | Cal.com/Retell docs, `crm-staging/` field map + sync | 2026-11-15 — system bootstrap |
| `testing` | 50 | Testing & QA | Logical | recipient=`testing` | `retell-pet-grooming-qa/` | 2026-11-15 — system bootstrap |
| `documentation` | 70 | Documentation, Knowledge Integrity & Recovery Assurance | Logical | recipient=`documentation` | `docs/`, `scripts/documentation/`, root README | 2026-11-18 — docs + UAN audit |

## Capabilities (declared)

| Agent ID | Supported capabilities |
|---|---|
| `coordinator` | Plan/dispatch, priorities, ownership, blockers, ADRs, CRM stage conflicts, release-readiness coordination |
| `market-research` | Local prospect research, commercial discovery, `prepare-prospect`, sales positioning from verified intel |
| `voice-development` | Conversational flows, feasibility reviews, verified feature descriptions |
| `integrations` | Telephony/calendar/CRM/API review, ERPNext export mapping, blocked sync gate |
| `testing` | Scenario validation, defect investigation, reproducible test evidence, independent review posture |
| `documentation` | Doc integrity, registry, drift checks, impact assessments, recovery knowledge assurance |

## How to join

1. Add a role card under `coordination/agents/`.
2. Add the ID to schemas + `coord.py` `KNOWN_AGENTS` + `config/uan.json` aliases if needed.
3. Update this registry table and `docs/uan/agent-registry.md`.
4. Do not claim the agent is active until a session records inbox/task evidence.
