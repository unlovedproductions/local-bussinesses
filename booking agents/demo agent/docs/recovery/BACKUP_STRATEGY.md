# Backup Strategy

## Principles

- Primary: GitHub remote for source.
- Need: secondary copy outside the same account blast radius.
- Secrets: never in git; vault + provider dashboards.
- QA artifacts: not treated as canonical backups.

## Activation (manual)

1. Set `DR_EXPORT_DIR` to encrypted/offsite path.
2. Run `python3 scripts/documentation/export_emergency_pack.py` on a schedule you own.
3. Optionally add a second git remote/mirror (human setup).
4. Record last successful export + restore test in `BACKUP_INVENTORY.md`.

RPO/RTO: unset until business owner approves.
