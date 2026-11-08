# Security

- Secrets only in local `.env` (gitignored).
- Suite H adversarial tests must target staging.
- No credential disclosure expected from receptionist.
- Do not export real customer data into `qa_runs`.
- Zip packaging excludes `.env`, live configs with secrets, and qa evidence.
- Recording/consent: use authorized numbers and comply with local recording laws.
