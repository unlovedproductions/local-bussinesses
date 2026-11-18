# Configuration Reference

| Field | Value |
|---|---|
| Owner | integrations + documentation |
| Classification | INTERNAL |
| Status | NEEDS_REVIEW |
| Last verified | 2026-11-18 |
| Authoritative template | `retell-pet-grooming-qa/.env.example` |

Names only. Never commit values.

## Retell

| Variable | Purpose |
|---|---|
| RETELL_API_KEY | Retell API auth |
| RETELL_API_BASE | API base URL |
| RECEPTIONIST_AGENT_ID | Target receptionist agent |
| RECEPTIONIST_PHONE_NUMBER | Optional PSTN |
| QA_CALLER_AGENT_ID | QA caller agent |
| QA_OUTBOUND_NUMBER | Outbound number for phone mode |
| RETELL_CALL_MODE | `web` (default) or `phone` |

## Judge

| Variable | Purpose |
|---|---|
| JUDGE_PROVIDER | `ollama` (default) or `openai` |
| OLLAMA_BASE_URL | Local OpenAI-compatible endpoint |
| JUDGE_MODEL | Model id |
| OPENAI_API_KEY | If provider=openai |

## Safety / budgets

| Variable | Purpose |
|---|---|
| MAX_CALLS | Cap calls per run |
| MAX_CALL_DURATION_SECONDS | Per-call duration cap |
| MAX_RUN_SPEND_USD | Spend cap |
| ALLOW_SANDBOX_WRITES | Must be YES + proof for sandbox writes |
| ACK_TARGET_NUMBER | Must acknowledge target number |
| SANDBOX_PROOF_PATH | Path to sandbox proof JSON |

## Adapters

| Variable | Purpose |
|---|---|
| QA_ASSERT_URL | Optional assert endpoint |
| TEST_ADAPTER_URL | Local stub harness (default `http://127.0.0.1:8787`) |

## Cal.com

| Variable | Purpose |
|---|---|
| CALCOM_API_KEY | API key |
| CALCOM_API_BASE | Default `https://api.cal.com/v2` |
| CALCOM_API_VERSION | API version header |
| CALCOM_EVENT_TYPE_ID | Event type |
| CALCOM_SANDBOX_CALENDAR_ID | Sandbox calendar |
| CALCOM_TIMEZONE | e.g. America/Los_Angeles |

## Paths

| Variable | Purpose |
|---|---|
| BUSINESS_CONFIG_PATH | Business JSON |
| QA_VARS_PATH | QA vars JSON |
| TEST_SETTINGS_PATH | Test settings |
| CASES_PATH | Scenario cases |
| QA_RUNS_DIR | Run evidence directory |

## Documentation / DR tooling

| Variable | Purpose |
|---|---|
| DR_EXPORT_DIR | Destination for emergency pack export (off-repo) |

## Config JSON examples

See `retell-pet-grooming-qa/config/*.example.json`.
