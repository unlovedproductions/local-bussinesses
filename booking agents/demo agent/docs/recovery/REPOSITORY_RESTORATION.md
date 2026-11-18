# Repository Restoration

## Stage checklist

1. **Assess** — what was lost; compromise? preserve evidence if security incident.
2. **Clean environment** — Linux + git + Python 3.10+.
3. **Restore repo** — clone `unlovedproductions/local-bussinesses`; verify path `booking agents/demo agent/`.
4. **Dependencies** — QA `pip install -r requirements.txt`.
5. **Configuration** — recreate `.env` from vault using `.env.example` names only.
6. **Infrastructure** — Retell/Cal.com SaaS (no local K8s in this project).
7. **Data** — Cal.com bookings via provider; local `qa_runs/` optional.
8. **Integrations** — API keys, agent IDs, event type IDs.
9. **Agent system** — `AGENTS.md`, `coordination/`, `.cursor/rules/coordination.mdc`.
10. **Tests** — coordination tests, doc checks, QA validate/unittest/preflight.
11. **Return to service** — human authorization for any live calendar/phone.
12. **Post-review** — record incident, source, outcome, gaps.

## Integrity

Compare commit SHA to a known good value when available. Tags/releases: use whatever exists on remote (do not invent).
