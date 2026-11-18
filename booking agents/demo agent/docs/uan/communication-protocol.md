# Agent Communication Protocol

## Flow

**Sender → Validated JSON → Store → Recipient poll → Ack → Execute → Result → Close**

## Message lifecycle

`PROPOSED → ACKNOWLEDGED → IN_PROGRESS → COMPLETED`  
Also: `BLOCKED`, `REJECTED`, `CANCELLED`

CLI: `send`, `ack`, `start`, `complete`, `block`, `reject`

## Handoff lifecycle (JSON)

Same status set as messages.  
CLI: `handoff-create`, `handoff-transition`, `handoff-list`  
Markdown handoffs under `coordination/handoffs/*.md` remain human notes; **JSON is authoritative** for machine lifecycle when both exist.

Required fields: id, sender, recipient, project_id, domain_id, created_at, subject, background, requested_action, priority, status.

## Task lifecycle

`PENDING → READY → RUNNING → COMPLETED|FAILED`  
Also: `WAITING_APPROVAL`, `BLOCKED`, `CANCELLED`

CLI: `task-create`, `task-list`, `task-get`, `task-transition`

## Worktree sync

Uncommitted coordination files are invisible to other worktrees. Commit/pull before assuming delivery. Do not auto-merge.

## Decision records

Consequential decisions stay in `coordination/decisions/` (ADR format).
