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

Overall: **DOCUMENTED BUT UNTESTED** for most paths; **BLOCKED** for account-wide GitHub loss without secondary copy.

Updated: 2026-11-18.

## Evidence log

| Date | Test | Result |
|---|---|---|
| 2026-11-18 | Isolated shallow clone of GitHub remote | Committed subtrees `voice-agent/`, `retell-pet-grooming-qa/` present; root AGENTS/docs/coordination/scripts **absent on remote** (uncommitted) |
| 2026-11-18 | Emergency pack export to `/tmp/ai-voice-dr-export-test` | PASS script; not durable operator backup |
| 2026-11-18 | `check_docs.py` | PASS 0 errors |
| 2026-11-18 | `test_coord.py` | PASS 11/11 |
