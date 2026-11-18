# Master System Specification — UAN-CORE + VOICE-AIN

| Field | Value |
|---|---|
| Version | 0.2.0 |
| Date | 2026-11-18 |
| Status | PARTIALLY_OPERATIONAL |

## Architecture

Reusable core = evolved `coordination/` repo bus (ADR-001, ADR-002).  
Domain pack = `domains/voice_agent_network/` (VOICE-AIN).  
Commander = `coordinator` (UAN 00).  
Docs/recovery = `documentation` (UAN 70).

## Execution truth

| Capability | Mechanism | Auto-starts agents? |
|---|---|---|
| Cross-session A2A | messages/tasks/handoffs JSON | No |
| Same-session specialists | Cursor Task | Yes (session only) |
| Semantic memory | Supermemory MCP | No |
| Voice QA execution | `retell-pet-grooming-qa` | N/A |

## Milestone map

| Milestone | Status |
|---|---|
| M1 Audit | Done |
| M2 Contracts | Done |
| M3 Commander | Done |
| M4 Communication | Done |
| M5 Memory | Done (MCP verified; Python reminder adapter) |
| M6 Approvals | Done (registry + enforcement in managed CLI) |
| M7 Voice domain pack | Done (workflows/gates; adapters = existing QA) |
| M8 Doc agent | Done (strengthened; existed) |
| M9 Doc/recovery foundations | Done (existed + DR allowlist/ops status) |
| M10 Voice testing/optimization | Partial — contracts + QA suite; live optimize deferred |
| M11 Client/ops | Done (existing docs; version note) |
| M12 Drift automation | Done (extended check_docs + CI workflow) |
| M13 Ops interface | Done (CLI ops/report; no fake KPI dashboard) |
| M14 E2E acceptance | Done (harness; no live telephony) |

## Non-goals completed as rejections

- Parallel `src/uan/` orchestrator
- Silent MCP installs
- Supermemory reinstall
- Claiming DR verified without restore tests
