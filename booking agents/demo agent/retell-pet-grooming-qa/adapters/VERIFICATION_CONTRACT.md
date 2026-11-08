# Provider Evidence Contract

## Input
- run_id
- test_id
- receptionist_call_id
- expected_outcome
- required_oracles
- sandbox_calendar_id

## Output
- verified
- status (`PASS` | `FAIL` | `BLOCKED` | `INCONCLUSIVE` | `NOT_APPLICABLE`)
- assertions
- before_snapshot
- after_snapshot
- tool_events
- event_ids
- evidence_references
- verification_errors

## Rules
- Evidence must come from trusted backend sources (Cal.com API for this project).
- Spoken confirmation is not evidence.
- LLM output is not evidence of backend state.
- If provider connectivity is unavailable, return BLOCKED.
