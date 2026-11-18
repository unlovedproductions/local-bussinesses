# Active Tasks

Every active task must have: Task ID, description, responsible agent, priority, dependencies, status, files, acceptance criteria, verification requirements.

| Task ID | Description | Owner | Priority | Status | Dependencies | Files | Acceptance | Verification |
|---|---|---|---|---|---|---|---|---|
| TASK-HVAC-001 | Evaluate after-hours HVAC emergency call intake feasibility | voice-development | P1 | IN_PROGRESS | none | voice-agent/, coordination/shared-context/ | Feasibility note with VERIFIED/PROPOSED/BLOCKED | TECHNICAL_REVIEW message completed with evidence |

## Ownership rules

- Claim via `coord.py claim --task TASK-... --agent <id>` before editing shared areas.
- Duplicate claims fail; escalate to `coordinator`.
- Shared files requiring review: root `AGENTS.md`, `coordination/shared-context/*`, `crm-staging/field-map.md`.
