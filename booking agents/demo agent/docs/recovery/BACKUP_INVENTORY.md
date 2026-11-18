# Backup Inventory

| Asset | Owner | Method | Destination | Encryption | Retention | Frequency | Last success | Integrity check | Last restore | Access | Limitations |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Source + history | human | git push | GitHub `unlovedproductions/local-bussinesses` (`origin`) | TLS in transit | per GitHub | on push | 2026-11-18 `e051ecc` | clone / ls-remote | see verification | GitHub auth | Account-wide delete risk |
| Secondary mirror | human | git push `gitlab` | GitLab `unlovedproducts/local-bussinesses-mirror` | TLS in transit | per GitLab | manual after push (or script) | 2026-11-18 `e051ecc` on `main` | `git ls-remote gitlab` | **NOT TESTED** full restore | GitLab auth (`glab` / SSH) | Not auto-synced; push both remotes |
| Emergency pack | documentation + human | export script | `$DR_EXPORT_DIR` → `/home/unloved/backups/ai-voice-dr` | operator-managed | operator | manual | 2026-11-18 export | list files | **NOT TESTED** | filesystem ACL | Local disk only; schedule yourself |
| Cal.com data | human | provider | Cal.com | provider | provider | provider | UNKNOWN | provider UI | UNKNOWN | Cal.com login | External dependency |
| Retell agents | human | provider | Retell | provider | provider | provider | UNKNOWN | provider UI | UNKNOWN | Retell login | External dependency |
| `.env` secrets | human | vault | operator vault | required | operator | on change | UNKNOWN | — | — | vault ACL | Never in git |
| `qa_runs/` | testing | local disk | workstation | optional | local | per run | N/A | — | — | local | Not DR-grade |
| coordination/ | coordinator | git | same as source + mirror | — | — | on commit/push | with remotes | — | — | git | Push to `gitlab` after GitHub |

## Remotes (parent repo)

```text
origin  git@github.com-unloved:unlovedproductions/local-bussinesses.git
gitlab  git@gitlab.com:unlovedproducts/local-bussinesses-mirror.git
```

Mirror URL: https://gitlab.com/unlovedproducts/local-bussinesses-mirror

Sync after meaningful pushes:

```bash
git push origin HEAD
git push gitlab HEAD
# or: git push gitlab --all && git push gitlab --tags
```

Do **not** confuse with existing GitLab project `unlovedproducts/local-bussinesses` (unrelated church site).
