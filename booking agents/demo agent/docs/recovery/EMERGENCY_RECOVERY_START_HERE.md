# EMERGENCY RECOVERY — START HERE

| Classification | INTERNAL (keep a copy **outside** the primary GitHub account) |
| Owner | Human recovery operator + documentation agent (knowledge) |
| Last updated | 2026-11-18 |
| Off-repo copy status | GitLab secondary mirror + local emergency pack **BACKUP_IDENTIFIED**; full restore drills still **NOT_TESTED** |

## If the primary repository is unavailable

1. **Do not** invent credentials. Use the operator password manager / provider dashboards.
2. Prefer independent sources in order: (a) GitLab mirror, (b) local emergency pack under `/home/unloved/backups/ai-voice-dr`, (c) any other known clone.
3. Identify the latest trusted recovery point (git commit SHA or export timestamp).

## Primary recovery source

| Item | Value |
|---|---|
| Git host | GitHub |
| Repository | `unlovedproductions/local-bussinesses` |
| Remote name | `origin` |
| Workspace path inside repo | `booking agents/demo agent/` |
| Default branch | `main` |

```bash
git clone git@github.com-unloved:unlovedproductions/local-bussinesses.git /tmp/local-bussinesses-recover
cd /tmp/local-bussinesses-recover/"booking agents/demo agent"
ls AGENTS.md voice-agent retell-pet-grooming-qa coordination docs
```

## Secondary recovery source (GitLab mirror)

| Item | Value |
|---|---|
| Git host | GitLab.com |
| Repository | `unlovedproducts/local-bussinesses-mirror` |
| URL | https://gitlab.com/unlovedproducts/local-bussinesses-mirror |
| Remote name (local) | `gitlab` |
| Visibility | Private |

```bash
git clone git@gitlab.com:unlovedproducts/local-bussinesses-mirror.git /tmp/local-bussinesses-from-gitlab
cd /tmp/local-bussinesses-from-gitlab/"booking agents/demo agent"
```

Do **not** use GitLab project `unlovedproducts/local-bussinesses` — that is a different (church) project.

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
| Source + git history | GitHub `origin` | BACKUP_IDENTIFIED |
| Secondary mirror | GitLab `gitlab` remote | BACKUP_IDENTIFIED (manual push) |
| Off-repo emergency pack | `/home/unloved/backups/ai-voice-dr` (`DR_EXPORT_DIR`) | BACKUP_IDENTIFIED |
| Application database | N/A (demo uses Cal.com) | N/A |
| QA run evidence | Local `qa_runs/` only | Not durable backup |
| Secrets | Operator vault + Retell/Cal.com dashboards | Process only |

## Keep the mirror current

```bash
git push origin HEAD
git push gitlab HEAD
```

## Full runbook

See `DISASTER_RECOVERY.md`, `REPOSITORY_RESTORATION.md`, `BACKUP_INVENTORY.md`, `RECOVERY_READINESS.md`.
