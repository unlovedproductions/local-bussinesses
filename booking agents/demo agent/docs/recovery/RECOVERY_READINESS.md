# Recovery Readiness

| Scenario | Classification |
|---|---|
| A File deletion | DOCUMENTED |
| B Git corruption | DOCUMENTED |
| C Local repo deleted | DOCUMENTED |
| D Remote deleted | BLOCKED (no secondary) |
| E Hosting account loss | BLOCKED (no secondary) |
| F Workstation failure | DOCUMENTED |
| G Dev env loss | DOCUMENTED |
| H Prod infra (SaaS) | DOCUMENTED |
| I Database | N/A / DOCUMENTED |
| J External config | DOCUMENTED |
| K Credentials | DOCUMENTED |
| L Unauthorized mods | DOCUMENTED |
| M Bad deploy | DOCUMENTED |
| N Agent coordination | DOCUMENTED |
| O Developer unavailable | DOCUMENTED |
| P Repo + docs loss | BLOCKED until off-repo pack verified |

Overall: **DOCUMENTED BUT UNTESTED** for most paths; **BLOCKED** for account-wide GitHub loss without secondary copy / durable emergency pack.

Updated: 2026-11-18 (UAN M1–M4 refresh).

## Evidence log

| Date | Test | Result |
|---|---|---|
| 2026-11-18 | Commit `9d1e207` on `main` tracking origin | `docs/`, `coordination/`, root `AGENTS.md`, `scripts/` present on remote (prior "uncommitted" note obsolete) |
| 2026-11-18 | Emergency pack export to `/tmp/ai-voice-dr-export-test` | PASS script; durable `DR_EXPORT_DIR` still operator-owned / not activated |
| 2026-11-18 | `check_docs.py` | PASS historically; re-run after UAN docs |
| 2026-11-18 | `test_coord.py` | Extended for UAN task/handoff/plan |

## Operator actions still required

1. Set durable `DR_EXPORT_DIR` and schedule exports.
2. Optional secondary git remote/mirror.
3. Confirm Retell/Cal.com credential vault recovery path privately.
