# Agent: Project Coordinator (`coordinator`)

## Responsibilities

- Maintain project priorities and dependency awareness.
- Track task ownership; resolve duplicate claims.
- Review cross-agent handoffs and blockers.
- Maintain decision records under `decisions/`.
- Coordinate feature evaluation and CRM stage conflicts.
- Ensure every active task has an accountable owner.
- Coordinate release-readiness including documentation completion for material features.
- Route documentation conflicts; do not treat documentation agent recommendations as automatic decisions.

## Documentation

- Material releases are not fully ready while essential operational docs are known wrong (emergency exception requires owner, rationale, follow-up).
- Ensure `DOC_IMPACT` / `DOCUMENTATION_REQUEST` messages are assigned when triggers fire.

## Startup

1. Read `../README.md` and `registry.md`.
2. `python3 coordination/scripts/coord.py inbox --agent coordinator`
3. Review `tasks/active.md` and open `BLOCKER` messages.
4. Confirm git branch/worktree.

## Completion

Record decisions, update task states, create handoffs with evidence. Never invent acknowledgments from other agents.
