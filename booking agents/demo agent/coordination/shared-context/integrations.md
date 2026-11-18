# Shared Context — Integrations

| Field | Value |
|---|---|
| ID | KNOW-INT-001 |
| Verification status | VERIFIED (discovered providers) |
| Responsible agent | integrations |
| Date recorded | 2026-11-15 |

## Providers

| Integration | Status | Notes |
|---|---|---|
| Retell AI | Connected in demo docs | Agent IDs recorded in QA AGENTS.md |
| Cal.com | Connected in demo docs | Native Retell tools |
| ERPNext | BLOCKED | No site; staging only under `crm-staging/` |
| Generic CRM writes on receptionist | NOT_APPLICABLE / unconfigured in QA | Fault scenarios exist |

## Auth / data-flow notes

- Never commit API keys.
- ERPNext sync requires `ERPNEXT_URL`, `ERPNEXT_API_KEY`, `ERPNEXT_API_SECRET` (future).
