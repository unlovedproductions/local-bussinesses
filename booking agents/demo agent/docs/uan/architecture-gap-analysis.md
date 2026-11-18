# Architecture Gap Analysis — UAN-CORE + VOICE-AIN

| Field | Value |
|---|---|
| Report ID | UAN-GAP-20261118 |
| Date | 2026-11-18 |
| Baseline | Inventory UAN-INV-20261118 |
| Scope | M1–M4 target vs existing workspace |

## Priority legend

- **P0** Critical foundations
- **P1** Required core capabilities
- **P2** Valuable enhancements
- **P3** Future extensions

## Gaps

| ID | Gap | Severity | Pre-pass status | M1–M4 disposition |
|---|---|---|---|---|
| G01 | No `docs/uan/` inventory/gap artifacts | P0 | MISSING | ADD |
| G02 | No UAN agent alias map / domain pack metadata | P0 | MISSING | ADD (`uan.json`, `domain.yaml`) |
| G03 | No structured task lifecycle store | P0 | PARTIAL (markdown) | ADD JSON records + transitions |
| G04 | No execution attempt log | P0 | MISSING | ADD `tasks/attempts/` |
| G05 | Commander cannot plan/dispatch with concurrency limit | P0 | MISSING | ADD `coord.py plan` |
| G06 | Handoff contract not machine-validated | P1 | PARTIAL (MD) | ADD JSON schema + CLI |
| G07 | Docs claim remote missing docs (stale) | P1 | OUTDATED | FIX readiness docs |
| G08 | No secondary backup / durable DR export | P0 ops | BLOCKED | Document; human activation |
| G09 | SQLite operational DB | P2 | MISSING | DEFER — file bus OK |
| G10 | Separate audio/red-team/perf agents (30/31/51/60/61) | P2 | MISSING | DEFER — map into existing roles |
| G11 | Full VOICE-AIN eval framework | P1 product | PARTIAL (QA suite) | DEFER to M7/M10 |
| G12 | Slash-command registration in Cursor | P3 | MISSING | Map to `coord.py` equivalents |
| G13 | Graphical ops dashboard | P3 | PARTIAL (QA Streamlit) | DEFER |
| G14 | Parallel orchestrator under `src/uan/` | — | — | REJECT (duplicate) |

## Layer readiness (six UAN layers)

| Layer | Readiness | Notes |
|---|---|---|
| Control plane | PARTIAL → M3 strengthens | `coordinator` + `plan` |
| Execution plane | PARTIAL | Repo bus + Cursor Task secondary; no auto-session spawn |
| Memory & knowledge | PARTIAL | shared-context + Supermemory tags; no reset |
| Domain intelligence | PARTIAL | VOICE-AIN metadata only in M1–M4 |
| Security & governance | PARTIAL | Approval gates documented; ERPNext blocked |
| Operations & interface | PARTIAL | `coord.py status/plan/task/handoff` |

## Honest execution limits

1. File creation ≠ agent activation.
2. Cursor Task works only in the same chat session that invokes it.
3. Cross-worktree visibility requires commit/pull of coordination files.
4. Max concurrent specialists default **3** (`UAN_MAX_CONCURRENT` overrides).

## Acceptance for this gap pass

- Inventory + this gap file exist with evidence.
- Agent 70 remains `documentation` (no duplicate).
- Commander helpers land on `coord.py` without a second bus.
