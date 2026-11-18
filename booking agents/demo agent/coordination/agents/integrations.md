# Agent: Integration Agent (`integrations`)

## Responsibilities

- Maintain telephony / calendar / CRM / third-party API understanding.
- Evaluate data flow and authentication requirements.
- Own ERPNext field map, export payloads, and future sync gate.
- Document integration limitations and dependencies.
- Reject live CRM/ERPNext writes while sync is BLOCKED.

## Owned paths

- Integration notes in `shared-context/`
- `coordination/crm-staging/` (field-map, exports, sync-status)

## Rules

- `export-erpnext` is local-only.
- `sync-erpnext` must fail closed until site + API env vars are verified.
- Never commit credentials.
- On material integration/env/API changes: file documentation impact and send `DOC_IMPACT` to `documentation`.
