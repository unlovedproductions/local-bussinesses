# Handoff: Synthetic prospect export

| Field | Value |
|---|---|
| ID | HANDOFF-20261115-prospect-to-integrations |
| From | `market-research` |
| To | `integrations` |
| Related message | `MSG-20261115-prospect-ready` |
| Related task | `TASK-CRM-001` |
| Created | 2026-11-15T16:26:00-08:00 |
| Status | PROPOSED |

## Background

ERPNext-ready package for Valley Air Demo HVAC (synthetic).

## Evidence

- `coordination/crm-staging/prospects/PROSPECT-20261115-valley-hvac.json`

## Requested action

`export-erpnext`; keep `sync-erpnext` blocked.

## Acceptance criteria

Export JSON under `crm-staging/exports/`; sync attempt fails closed with BLOCKED evidence.
