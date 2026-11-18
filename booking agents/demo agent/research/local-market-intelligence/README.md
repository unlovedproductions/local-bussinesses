# Local Market Intelligence

Working area for the `market-research` agent.

## Pointers

- Parent research (existing): `../../../research/local-owner-objections/` (sales objections playbook; not voice-specific).
- CRM staging for ERPNext-ready packages: `../../coordination/crm-staging/`
- Verified product capabilities: `../../coordination/shared-context/verified-features.md`

## Layout

| Path | Purpose |
|---|---|
| `findings/` | Industry / problem discoveries |
| `prospects/` | Research notes that feed `prepare-prospect` |

## Rules

- Synthetic or operator-approved contacts only in committed samples.
- Product claims must cite verified capabilities from coordination shared-context.
- Create explicit `FEATURE_REQUEST` / `PROSPECT_READY` messages when engineering or CRM action is needed.
