# Troubleshooting

| Symptom | Likely cause | Action |
|---|---|---|
| All VOICE BLOCKED | Missing numbers / ACK / API key | Fill `.env`; set ACK only when authorized |
| Correlation BLOCKED | Inbound call not found / ambiguous | Widen window; confirm agent IDs and numbers |
| Calendar BLOCKED | Missing CALCOM_API_KEY or wrong event type | Configure Cal.com API key; verify event type ID |
| AUDIO/FAULT/DROP BLOCKED | No TEST_ADAPTER_URL | Start local stub: `python scripts/run_stub_adapter.py`, set `TEST_ADAPTER_URL=http://127.0.0.1:8787` (synthetic evidence only) |
| Judge INCONCLUSIVE | No OPENAI_API_KEY | Optional for conversational grading; backend asserts still run |
| Cal.com email 400 | Non-deliverable domain | Use a real inbox for sandbox attendees |
| False booking PASS | Not possible if verifier wired | Backend failure overrides spoken success |
