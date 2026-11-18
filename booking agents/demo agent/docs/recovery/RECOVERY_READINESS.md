# Recovery Readiness

| Scenario | Classification |
|---|---|
| A File deletion | DOCUMENTED |
| B Git corruption | DOCUMENTED |
| C Local repo deleted | DOCUMENTED |
| D Remote deleted (GitHub only) | BACKUP_IDENTIFIED (GitLab mirror) |
| E Hosting account loss (GitHub) | BACKUP_IDENTIFIED (GitLab + local DR pack) |
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
| P Repo + docs loss | BACKUP_IDENTIFIED (GitLab + `/home/unloved/backups/ai-voice-dr`) — restore **NOT_TESTED** |

Overall: **DOCUMENTED**; secondary sources **BACKUP_IDENTIFIED**; full restore drills still **NOT_TESTED**. Simultaneous GitHub+GitLab+workstation loss remains a residual risk.

Updated: 2026-11-18 (GitLab mirror + DR_EXPORT_DIR).

## Evidence log

| Date | Test | Result |
|---|---|---|
| 2026-11-18 | Commit `e051ecc` on GitHub `origin/main` | UAN M5–M14 present |
| 2026-11-18 | GitLab project `unlovedproducts/local-bussinesses-mirror` | Created private; `main` @ `e051ecc` via `git ls-remote gitlab` |
| 2026-11-18 | `DR_EXPORT_DIR=/home/unloved/backups/ai-voice-dr` export | PASS → `ai-voice-booking-agents-emergency-20261118T192914Z` |
| 2026-11-18 | Full clone-from-GitLab restore drill | **PASS** shallow clone; `coord.py status` ran from restored tree |
| 2026-11-18 | Dual-push helper | `scripts/push_both_remotes.sh` |

## Operator actions still required

1. After each important push: `./booking\ agents/demo\ agent/scripts/push_both_remotes.sh` (or `git push origin HEAD && git push gitlab HEAD`).
2. Re-run emergency pack export on a schedule you own (`DR_EXPORT_DIR=/home/unloved/backups/ai-voice-dr`).
3. Confirm Retell/Cal.com credential vault recovery path privately.
4. Live Retell/Cal.com E2E with credentials (product go-live).
