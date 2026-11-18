# ERPNext CRM Staging

Stage prospect and sales-path data here before any live ERPNext write.

**Current sync status:** see [sync-status.md](sync-status.md) — **BLOCKED** until an ERPNext site exists.

## Flow

1. Market Research authors a package → `prospects/<id>.json` via `coord.py prepare-prospect`.
2. Voice/Testing attach only verified capabilities.
3. Integrations runs `export-erpnext` → `exports/<id>.json` (REST-shaped, local).
4. `sync-erpnext` remains blocked until site URL + API credentials are configured and a dry-run Lead create is verified.

## Official ERPNext path (docs)

Lead → Opportunity → Quotation → Customer → Sales Order.

## Safety

- Synthetic or operator-approved contacts only in git samples.
- No API keys in this directory.
- Staging files are authoritative until sync is CONFIGURED + TESTED.
