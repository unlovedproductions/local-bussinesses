# Retell Setup

## Existing receptionist
Do not rebuild it. Record `RECEPTIONIST_AGENT_ID` from the Retell dashboard.

Known demo agent: `agent_7fd690435a3abdb17cbc4d38c9` (Taft Grooming Demo).

## Create QA caller
1. Create a new Retell voice agent named `QA Caller — Pet Grooming Test Agent`.
2. Paste `prompts/RETELL_QA_CALLER.md` as the system prompt.
3. Ensure dynamic variable `{{qa_case}}` is referenced.
4. Assign an authorized outbound number → `QA_OUTBOUND_NUMBER`.
5. Set `QA_CALLER_AGENT_ID`.
6. Configure receptionist inbound number → `RECEPTIONIST_PHONE_NUMBER`.
7. Set `ACK_TARGET_NUMBER=YES` only after confirming the destination is authorized.

## Inspect
```bash
python scripts/inspect_retell.py
```

## Call API
Uses official `POST /v2/create-phone-call`, `GET /v2/get-call/{call_id}`, `POST /v2/list-calls`.

## Web mode (no phone numbers)
Set `RETELL_CALL_MODE=web`. VOICE scenarios run via Retell LLM simulation (`create-test-case-definition` + `create-batch-test`). Retell labels these `call_type=web_call`. This does not exercise PSTN audio or the QA caller phone agent.
Dynamic variables must be strings (`retell_llm_dynamic_variables.qa_case`).
