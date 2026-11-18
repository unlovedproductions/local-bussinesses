# Development Workflow

1. Identify agent role (`AGENTS.md`).
2. Poll inbox: `python3 coordination/scripts/coord.py inbox --agent <id>`.
3. Claim tasks before editing shared areas.
4. Make smallest safe change; preserve QA fail-closed defaults and live Retell behavior unless approved.
5. File [`DOCUMENTATION_IMPACT`](../templates/DOCUMENTATION_IMPACT.md) for material changes; message `documentation` when docs must update.
6. Complete messages with evidence; update `shared-context/` when verified facts change.
7. Commit coordination/docs so other worktrees can see them (parent repo).

Branching: follow parent repo practice on `main`. No separate worktree convention enforced beyond coordination README warnings.
