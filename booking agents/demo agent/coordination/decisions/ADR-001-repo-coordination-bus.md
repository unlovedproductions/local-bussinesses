# ADR-001: Repository-based coordination bus

| Field | Value |
|---|---|
| ID | ADR-001 |
| Date | 2026-11-15 |
| Status | Accepted |
| Deciders | coordinator (bootstrap) |

## Context

Multiple logical agents need cross-session communication. Native Cursor messaging across chats is unavailable. MCP memory services are unauthenticated. ERPNext is not installed.

## Decision

Use version-controlled JSON/Markdown under `coordination/` as the primary bus, with a stdlib CLI for lifecycle transitions. Stage ERPNext-ready prospects locally; keep live sync BLOCKED.

## Alternatives rejected

- Native-only messaging (no cross-session delivery)
- MCP-primary bus (auth blocked)
- External orchestrator (unnecessary overhead)
- Installing ERPNext in this pass (unauthorized / unavailable)

## Consequences

- Agents must poll inbox at session start.
- Strong concurrency locks are not guaranteed.
- CRM packages can accumulate without inventing sync success.
