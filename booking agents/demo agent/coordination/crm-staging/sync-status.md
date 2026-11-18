# ERPNext Sync Status

| Field | Value |
|---|---|
| Status | **BLOCKED** |
| Reason | No ERPNext/Frappe site or `bench` install detected in this environment (audit 2026-11-15) |
| Staging authoritative | YES |
| Live writes allowed | NO |

## Activation checklist (manual)

1. Provision ERPNext (self-host or Frappe Cloud).
2. Create API key/secret for a least-privilege CRM user.
3. Set env vars (never commit): `ERPNEXT_URL`, `ERPNEXT_API_KEY`, `ERPNEXT_API_SECRET`.
4. Dry-run create one synthetic Lead; record evidence path here.
5. Change status to `CONFIGURED` only after verified dry-run.
6. Then implement/enable real network sync in `coord.py sync-erpnext`.

Until then, `coord.py sync-erpnext` must fail closed.
