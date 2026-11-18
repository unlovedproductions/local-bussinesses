# Backup Inventory

| Asset | Owner | Method | Destination | Encryption | Retention | Frequency | Last success | Integrity check | Last restore | Access | Limitations |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Source + history | human | git push | GitHub `local-bussinesses` | TLS in transit | per GitHub | on push | UNKNOWN (ongoing remote) | clone test | see verification report | GitHub auth | Account-wide delete risk |
| Emergency pack | documentation + human | export script | `$DR_EXPORT_DIR` | operator-managed | operator | manual | **NONE** | list files | **NOT TESTED** | filesystem ACL | **BLOCKED until configured** |
| Secondary mirror | — | — | — | — | — | — | — | — | — | — | **MISSING** |
| Cal.com data | human | provider | Cal.com | provider | provider | provider | UNKNOWN | provider UI | UNKNOWN | Cal.com login | External dependency |
| Retell agents | human | provider | Retell | provider | provider | provider | UNKNOWN | provider UI | UNKNOWN | Retell login | External dependency |
| `.env` secrets | human | vault | operator vault | required | operator | on change | UNKNOWN | — | — | vault ACL | Never in git |
| `qa_runs/` | testing | local disk | workstation | optional | local | per run | N/A | — | — | local | Not DR-grade |
| coordination/ | coordinator | git | same as source | — | — | on commit | with repo | — | — | git | Lost if remote lost without pack |
