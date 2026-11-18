# Secrets Management

- Template names only in git (`.env.example`).
- Real secrets: operator vault + local `.env` (gitignored).
- Rotate on compromise or personnel change.
- `check_docs.py` scans docs for high-entropy secret patterns (heuristic).
- See also `retell-pet-grooming-qa/docs/SECURITY.md`.
