# Execution Architecture

## Verified mechanisms

| Mechanism | Cross-session? | Auto-starts agent? | Use |
|---|---|---|---|
| `coord.py` message/task/handoff files | Yes (after git sync) | **No** | Primary |
| Cursor Task / subagents | No (same chat) | Yes within session | Secondary |
| Supermemory | Yes (semantic) | No | Lessons, not task authority |

## Commander lifecycle (Agent 00)

1. Interpret objective → `coord.py plan --objective "..."`  
2. Select domain VOICE-AIN from config.  
3. Match capabilities → recommended agents.  
4. Optional `--dispatch` creates READY tasks + claims (respects max concurrent).  
5. Specialists poll inbox/tasks; acknowledge; transition RUNNING→COMPLETED with evidence.  
6. Documentation impact → include `documentation` when triggers match.  
7. Human approval still required for production Retell/Cal.com changes.

## Concurrency

- Default max concurrent specialist RUNNING tasks: **3**
- Override: env `UAN_MAX_CONCURRENT`
- `coordinator` tasks do not consume the specialist slot

## Failure / recovery of workflows

- Attempts logged under `coordination/tasks/attempts/`
- Interrupted RUNNING tasks remain in records for resume/fail/cancel
- Duplicate claims fail closed

## Forbidden claims

Do not state that `handoff-create` or `plan --dispatch` launched a Cursor agent. They only persist work for a human or same-session Task to pick up.
