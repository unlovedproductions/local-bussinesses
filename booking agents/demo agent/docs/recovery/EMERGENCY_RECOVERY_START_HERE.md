# EMERGENCY RECOVERY — START HERE

| Classification | INTERNAL (keep a copy **outside** the primary GitHub account) |
| Owner | Human recovery operator + documentation agent (knowledge) |
| Last updated | 2026-11-18 |
| Off-repo copy status | **NOT YET PROTECTED** against total repository loss until `DR_EXPORT_DIR` export is activated |

## If the primary repository is unavailable

1. **Do not** invent credentials. Use the operator password manager / provider dashboards.
2. Locate an independent copy of this document (exported emergency pack). If none exists, recovery depends on GitHub or other backups only.
3. Identify the latest trusted recovery point (git tag/commit SHA or export timestamp).

## Primary recovery source (VERIFIED remote exists)

| Item | Value |
|---|---|
| Git host | GitHub |
| Repository | `unlovedproductions/local-bussinesses` |
| Workspace path inside repo | `booking agents/demo agent/` |
| Default branch | `main` |

Clone (example):

```bash
git clone <authorized-URL-to-local-bussinesses> /tmp/local-bussinesses-recover
cd /tmp/local-bussinesses-recover/"booking agents/demo agent"
ls AGENTS.md voice-agent retell-pet-grooming-qa coordination docs
```

## Who is responsible

| Role | Responsibility |
|---|---|
| Human owner / admin | Authorize recovery, provider account access, secrets |
| Recovery operator | Execute clone/restore steps |
| documentation agent | Keep this runbook accurate when invoked; escalate gaps |
| coordinator | Sequence multi-agent recovery work |

## Where backups live (current evidence)

| Asset | Location | Status |
|---|---|---|
| Source + git history | GitHub remote above | BACKUP IDENTIFIED (remote); restore test separately |
| Secondary mirror | — | **MISSING** |
| Off-repo emergency pack | `$DR_EXPORT_DIR` after export | **BLOCKED until configured** |
| Application database | N/A (demo uses Cal.com) | N/A |
| QA run evidence | Local `qa_runs/` only | Not durable backup |
| Secrets | Operator vault + Retell/Cal.com dashboards | Process only |

## How to retrieve the full DR runbook

From a restored tree or emergency pack:

- `docs/recovery/DISASTER_RECOVERY.md`
- `docs/recovery/REPOSITORY_RESTORATION.md`
- `docs/recovery/BACKUP_INVENTORY.md`
- `docs/recovery/CREDENTIAL_RECOVERY.md`
- `docs/recovery/AGENT_SYSTEM_RECOVERY.md`

## Begin reconstruction

1. Assess what was lost (Scenario letter in DISASTER_RECOVERY.md).
2. Establish clean OS + Python 3.10+.
3. Restore repository from trusted remote or pack.
4. Restore dependencies (`retell-pet-grooming-qa` venv).
5. Restore configuration from vault (not from git).
6. Reconnect Retell/Cal.com.
7. Restore agent coordination files if missing.
8. Run `validate.py`, unit tests, `preflight.py --mode readonly`.
9. Record post-recovery review.

## Verification

A documented plan ≠ tested recovery. Prefer isolated clone tests. Never destructive-test against production calendars.
