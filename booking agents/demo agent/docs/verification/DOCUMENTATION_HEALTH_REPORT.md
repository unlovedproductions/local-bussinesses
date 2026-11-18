# Documentation Health Report

| Field | Value |
|---|---|
| Date | 2026-11-18 |
| Producer | documentation bootstrap |
| Overall system status | **IMPLEMENTED BUT REQUIRES ACTIVATION** |

## CRITICAL

1. **Uncommitted documentation & coordination** — `docs/`, `coordination/`, root `AGENTS.md`, `scripts/` not on GitHub remote. Remote clone cannot restore the new system.
2. **No secondary mirror** — Scenario D/E/P blocked for account-wide GitHub loss.
3. **Off-repo emergency pack not operator-activated** — `$DR_EXPORT_DIR` must be set to durable storage outside repo; /tmp export is not a backup.

## HIGH

1. Many docs still NEEDS_REVIEW/DRAFT pending human technical review.
2. Live Retell/Cal.com operational procedures untested without credentials.
3. ERPNext sync remains BLOCKED (pre-existing).

## MEDIUM

1. Registry path string matching produces warnings for globbed entries (cosmetic).
2. No CI workflow wired for check_docs (local-first by design).

## LOW

1. Thin pointers in some architecture subdocs by design (avoid duplication).

## Fixed this pass

- Missing workspace docs foundation
- Missing documentation agent on bus
- Missing drift checks / impact workflow / recovery runbooks (documented)

## Not fixed / requires human

- Commit + push workspace docs/coordination
- Configure durable DR_EXPORT_DIR / secondary remote
- Approve RPO/RTO
- Auth Adapter/Supermemory if desired (optional)

## check_docs

Re-run after publishing this file; expect PASS with warnings acceptable.
