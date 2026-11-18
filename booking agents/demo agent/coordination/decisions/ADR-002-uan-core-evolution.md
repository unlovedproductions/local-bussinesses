# ADR-002 — Evolve Repo Bus into UAN-CORE (No Parallel Orchestrator)

| Field | Value |
|---|---|
| Status | Accepted |
| Date | 2026-11-18 |
| Owner | coordinator (Agent 00) |

## Context

Master directive requires UAN-CORE + VOICE-AIN while forbidding duplicate agent coordination infrastructure and unnecessary reinstalls.

## Decision

1. Keep `coordination/` + `coord.py` as the authoritative control/execution store.
2. Add UAN config, task records, attempts, JSON handoffs, and Commander `plan`/`dispatch`.
3. Map UAN numeric IDs as aliases; keep string IDs in schemas.
4. Defer SQLite and separate audio/red-team agent processes.
5. Register VOICE-AIN via `domains/voice_agent_network/domain.yaml` metadata only for M1–M4.

## Alternatives rejected

- Greenfield `src/uan/` orchestrator — duplicates bus; violates preserve/strengthen.
- Claiming Cursor Task as cross-session A2A — false.
- Auto-marking handoffs acknowledged — forges evidence.

## Consequences

- Operators must still poll inboxes / open sessions as specialists.
- Concurrency limits apply to structured task RUNNING state, not Cursor processes.
- Later milestones extend domain pack evaluation without replacing the bus.
