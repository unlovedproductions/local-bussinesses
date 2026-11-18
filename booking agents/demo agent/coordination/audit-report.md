# Coordination Environment Audit Report

**Date recorded:** 2026-11-15  
**Workspace:** `/home/unloved/local-bussinesses/booking agents/demo agent`  
**Status labels:** VERIFIED | INFERRED | UNAVAILABLE | BLOCKED

## Project inspection (VERIFIED)

| Item | Finding |
|---|---|
| Structure | `voice-agent/` (Retell + Cal.com demo markdown) and `retell-pet-grooming-qa/` (Python QA auditor) |
| Existing AGENTS.md | `retell-pet-grooming-qa/AGENTS.md` — QA mission/safety only; not a multi-agent bus |
| Cursor rules | `retell-pet-grooming-qa/.cursor/rules/` (`qa-development`, `qa-safety`); no prior workspace-level `.cursor/` |
| Prior coordination tree | Absent before this implementation |
| Git | Parent repo `/home/unloved/local-bussinesses`; single worktree on `main` |
| Research | Parent `research/local-owner-objections/` exists; not previously wired to voice product loop |
| Testing | `retell-pet-grooming-qa/tests/` unittest suite; voice-agent has `verification.md` evidence notes |
| ERPNext / Frappe / `bench` | Not installed; no site URL or API credentials in workspace |
| Live CRM on voice agent | QA treats CRM as unconfigured / fault-injected |

## Capability matrix

| Capability | Current status | Evidence | Recommendation |
|---|---|---|---|
| Native agent messaging | Unavailable | No A2A message bus in Cursor MCP/tooling for cross-chat delivery | Use repo inbox + explicit polling |
| Parallel execution | Verified | Cursor `Task` subagent tool available in-session | Optional same-session only; not primary bus |
| Persistent shared context | Verified (via files) | Git-tracked markdown/JSON under `coordination/` | Repo files are source of truth |
| Agent task discovery | Unavailable natively | No automatic task push to other chats | CLI `inbox` + startup Cursor rule |
| MCP communication | Partial / blocked | Supermemory not authenticated; Adapter `needsAuth` | Optional later; not required for Done |
| Git worktree isolation | Verified | `git worktree list` shows single worktree | Commit coordination changes to share across machines/worktrees |
| ERPNext CRM sync | Unavailable | `bench` not found; no ERPNext site | Stage ERPNext-ready packages now; sync later |

## Delivery model (VERIFIED conclusion)

This environment supports **persistent asynchronous handoffs with explicit recipient polling or coordinator intervention**. It does **not** provide real-time agent-to-agent messaging across independent Cursor chats.

## Evidence integrity rules

- Do not claim an agent received, acknowledged, or completed work without file evidence (message status + timestamps).
- Creating a registry entry does not mean an agent process is running.
- Creating a prospect package does not mean ERPNext contains the record.
