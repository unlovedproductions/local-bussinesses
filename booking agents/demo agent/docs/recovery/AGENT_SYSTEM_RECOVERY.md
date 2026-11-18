# Agent System Recovery

Restore from git (or emergency pack):

- `AGENTS.md`
- `.cursor/rules/coordination.mdc`
- `coordination/agents/`
- `coordination/schemas/`
- `coordination/scripts/coord.py`
- `coordination/shared-context/`
- `docs/agents/`

Then:

```bash
python3 coordination/scripts/coord.py register
python3 coordination/scripts/test_coord.py
```

Uncommitted worktree files do not survive deletion. Registry entry ≠ running agent — reopen Cursor sessions and poll inboxes.
