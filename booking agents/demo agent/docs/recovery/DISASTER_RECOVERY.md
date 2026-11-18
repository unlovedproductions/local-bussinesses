# Disaster Recovery

| Status | DOCUMENTED; operational readiness partial |
| Last verified | 2026-11-18 |
| RPO / RTO | **Unset** — operator must approve business targets |

## Scenarios

| ID | Scenario | Primary source | Independent source | Readiness |
|---|---|---|---|---|
| A | Accidental file deletion | `git checkout` / `git restore` | Off-repo pack if exported | DOCUMENTED |
| B | Git repo corruption | Re-clone remote | Off-repo pack | DOCUMENTED |
| C | Local repo deleted | Re-clone remote | Off-repo pack | DOCUMENTED |
| D | Remote deleted | — | **MISSING secondary** | BLOCKED |
| E | GitHub account unavailable | — | **MISSING secondary** | BLOCKED |
| F | Workstation failure | Re-clone + vault secrets | Off-repo pack | DOCUMENTED |
| G | Dev environment loss | Recreate venv from manifests | — | DOCUMENTED |
| H | Production infra failure | Retell/Cal.com SaaS status | Provider support | DOCUMENTED (SaaS) |
| I | Database corruption | N/A demo path; Cal.com provider | Provider | N/A / DOCUMENTED |
| J | External config loss | Provider dashboards + `voice-agent/` files | Emergency pack | DOCUMENTED |
| K | Credential loss | Provider reset + vault | — | DOCUMENTED |
| L | Unauthorized repo mods | `git` history / revert; rotate secrets | — | DOCUMENTED |
| M | Bad deploy / upgrade | Retell prompt rollback; Cal.com settings | Pack + git history | DOCUMENTED |
| N | Agent coordination loss | Restore `coordination/` from git | Emergency pack | DOCUMENTED |
| O | Original developer unavailable | This docs system + AGENTS.md | Pack | DOCUMENTED |
| P | Repo + docs simultaneous loss | — | **Requires off-repo pack** | BLOCKED until export activated |

## Reconstruction stages

Follow stages 1–12 in the master recovery protocol summary under `REPOSITORY_RESTORATION.md` and `EMERGENCY_RECOVERY_START_HERE.md`.
