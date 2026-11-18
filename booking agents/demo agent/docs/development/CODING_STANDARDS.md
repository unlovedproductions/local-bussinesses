# Coding Standards

- Prefer smallest surgical change; do not rebuild the receptionist inside the QA package.
- Fail closed on safety gates (`src/safety.py`).
- Distinguish VERIFIED / PROPOSED / BLOCKED in agent communications.
- No secrets or real customer PII in git.
- Coordination messages must follow schema + lifecycle transitions via CLI.
- Documentation updates accompany material behavior changes.
