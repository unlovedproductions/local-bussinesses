# Existing System Inventory — UAN Audit

| Field | Value |
|---|---|
| Report ID | UAN-INV-20261118 |
| Project | AI Voice Booking Agents (`booking agents/demo agent`) |
| Version | workspace @ parent `local-bussinesses` |
| Date | 2026-11-18 |
| Responsible agents | coordinator (00), documentation (70) |
| Classification | INTERNAL |
| Confidence | HIGH for structure; MEDIUM for live provider E2E |

## Method

Read-only inspection of workspace tree, git status/history, `AGENTS.md`, `coordination/`, `voice-agent/`, `retell-pet-grooming-qa/`, `docs/`, `research/`, `.cursor/.supermemory/`, and CLI behavior. Status taxonomy per master directive.

## Parent git / recovery

| Component | Status | Action | Evidence |
|---|---|---|---|
| Nested workspace (no local `.git`) | VERIFIED_IMPLEMENTED | PRESERVE | Parent `/home/unloved/local-bussinesses` |
| Remote `unlovedproductions/local-bussinesses` | VERIFIED_IMPLEMENTED | PRESERVE | `git remote -v` |
| Docs/coordination committed on `main` | VERIFIED_IMPLEMENTED | PRESERVE | Commit `9d1e207`; `main...origin/main` |
| Secondary mirror | MISSING | ADD (approval) | `BACKUP_INVENTORY.md` |
| Durable `DR_EXPORT_DIR` | USER_REPORTED_UNVERIFIED / BLOCKED | STRENGTHEN | Export script exists; operator path unset |
| Supermemory config tags | VERIFIED_PARTIAL | PRESERVE | `.cursor/.supermemory/config.json` |

## Voice product

| Component | Status | Action | Evidence |
|---|---|---|---|
| Retell web-call demo assets | VERIFIED_PARTIAL | PRESERVE | `voice-agent/README.md` |
| Cal.com availability/book/list/get | VERIFIED_PARTIAL | PRESERVE | Configured; live E2E needs credentials |
| Reschedule/cancel tools | MISSING (intentional) | PRESERVE | Demo README |
| Custom app backend / DB | MISSING (N/A) | PRESERVE | No server in `voice-agent/` |
| PSTN path | CONFIGURED_BUT_INACTIVE | PRESERVE | Optional; default web |
| HVAC emergency intake | DESIGNED_NOT_IMPLEMENTED | PRESERVE as PROPOSED | Sample coordination messages |

## QA / evaluation

| Component | Status | Action | Evidence |
|---|---|---|---|
| Autonomous QA auditor | VERIFIED_IMPLEMENTED | PRESERVE | `retell-pet-grooming-qa/` |
| Streamlit dashboard | VERIFIED_IMPLEMENTED | PRESERVE | `dashboard/app.py` |
| Stub harness / additional scripts | VERIFIED_PARTIAL | STRENGTHEN | Some files still untracked |
| Audio WER / live latency metrics | MISSING | ADD later (M10) | No verified traces in-repo |

## Multi-agent coordination (pre-UAN evolution)

| Component | Status | Action | Evidence |
|---|---|---|---|
| Repo-bus messages + lifecycle CLI | VERIFIED_IMPLEMENTED | STRENGTHEN → UAN | `coord.py`, schemas |
| Logical agent registry (6 roles) | VERIFIED_IMPLEMENTED | STRENGTHEN | `coordination/agents/registry.md` |
| Documentation agent (70) | VERIFIED_IMPLEMENTED | PRESERVE | `documentation` role |
| Continuous autonomous agents | MISSING | PRESERVE honesty | Polling model |
| Cross-session real-time A2A | MISSING (by design) | PRESERVE | ADR-001 |
| Universal Commander runtime | DESIGNED_NOT_IMPLEMENTED → this pass | ADD on bus | Was coordinator role only |
| Structured task records + attempts | MISSING → this pass | ADD | Markdown tasks only previously |
| JSON handoff contract CLI | MISSING → this pass | ADD | Markdown handoffs existed |
| SQLite operational DB | MISSING | DEFER | File bus sufficient for M1–M4 |
| Parallel `src/uan/` orchestrator | MISSING | DO NOT ADD | Would duplicate bus |

## Documentation & DR

| Component | Status | Action | Evidence |
|---|---|---|---|
| `docs/` ecosystem | VERIFIED_PARTIAL | STRENGTHEN | Registry statuses mostly NEEDS_REVIEW/DRAFT |
| `check_docs.py` | VERIFIED_IMPLEMENTED | PRESERVE | Prior PASS |
| `docs/uan/` | MISSING → this pass | ADD | Required audit artifacts |
| Recovery docs | DOCUMENTED / NOT_TESTED | STRENGTHEN | `RECOVERY_READINESS.md` |
| Client impl templates | VERIFIED_PARTIAL | PRESERVE | `docs/clients/` |

## Market research

| Component | Status | Action | Evidence |
|---|---|---|---|
| Research folder + sample HVAC loop | VERIFIED_PARTIAL | EXPAND later | `research/local-market-intelligence/` |
| ERPNext live sync | BLOCKED | PRESERVE gate | `crm-staging/sync-status.md` |

## Limitations

- Live Retell/Cal.com calls not re-executed in this audit.
- Adapter MCP unauthenticated in prior sessions; not required for M1–M4.
- Inventory does not claim production telephony readiness.

## Recommended next steps

1. Complete M1–M4 UAN contracts on existing bus (this pass).
2. Operator: durable DR export + optional secondary mirror.
3. Later milestones: VOICE-AIN eval workflows, drift CI, dashboard.
