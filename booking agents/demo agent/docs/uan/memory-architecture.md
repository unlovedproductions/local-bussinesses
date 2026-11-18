# Memory Architecture (M5)

| Field | Value |
|---|---|
| Status | VERIFIED_PARTIAL |
| Date | 2026-11-18 |

## Verified

- Supermemory MCP available in Cursor
- Project container write + retrieve succeeded (harmless M5 test record)
- Operational bus remains `coordination/` JSON/Markdown

## Adapter

No Python SDK reinstall. Cursor MCP is the adapter. Workspace notes: `coordination/memory/README.md`.

## Scopes

- Universal / VOICE-AIN / project: use project container
- Client-specific confidential: do not put in git or Supermemory without policy review

## Contradiction rule

If memory conflicts with verified implementation (`voice-agent/`, QA evidence), investigate; documentation agent + technical owner decide; do not silently overwrite SoT docs.
