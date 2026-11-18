# Operations Runbook

Diagnostic commands assume workspace root or `retell-pet-grooming-qa/` as noted. Do not invent services.

## INC-STARTUP-FAIL — Application / QA startup failure

1. Symptoms: scripts exit non-zero; Streamlit won't start.
2. Impact: no QA runs / dashboard.
3. Severity: MEDIUM (demo) / HIGH if blocking go-live QA.
4. Access: local shell, `.env`.
5. Diagnostics:
   ```bash
   cd retell-pet-grooming-qa && source .venv/bin/activate
   python scripts/validate.py
   python scripts/preflight.py --mode readonly
   ```
6. Expected: validate lists missing config clearly.
7. Actions: fix paths/env; reinstall requirements.
8. Verify: validate + unit tests pass.
9. Escalation: testing agent → integrations if API auth fails.

## INC-RETELL-API — Retell failures / no inbound simulation

1. Symptoms: client errors, empty call results, smoke BLOCKED.
2. Diagnostics: `python scripts/inspect_retell.py` (with keys); check `RETELL_API_KEY`, agent IDs, `RETELL_CALL_MODE`.
3. Fallback: pause tests; do not bypass safety ACK gates.
4. Related: `src/retell_client.py`.

## INC-CALCOM — Scheduling / CRM calendar failures

1. Symptoms: availability empty, book fails.
2. Diagnostics: verify `CALCOM_*` env; event type id; timezone.
3. Related: `adapters/calcom_adapter.py`.

## INC-VOICE-QUALITY — Slow / wrong conversation behavior

1. Symptoms: latency, incorrect answers.
2. Actions: review Retell prompt vs `voice-agent/system-prompt.md` and business facts; check tool attachment.
3. Escalate: voice-development.

## INC-JUDGE — Judge / Ollama failures

1. Symptoms: judge errors, OOM.
2. Diagnostics: curl `OLLAMA_BASE_URL`; reduce model size per QA README notes.

## INC-SMOKE-BLOCKED — Smoke tests BLOCKED

1. Expected when credentials/ACK missing — not a silent pass.
2. Actions: supply authorized credentials or accept BLOCKED.

## INC-WEBHOOK — Webhook errors

No first-party webhook server in demo path. If Retell/Cal.com webhooks used later, document endpoints before adding runbook steps. Current status: N/A / UNKNOWN.

## INC-DEPLOY-ROLLBACK — Failed change

1. Restore prior Retell prompt from git (`voice-agent/system-prompt.md`).
2. Revert Cal.com event settings from documented tables.
3. Re-run acceptance tests.

More troubleshooting: [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
