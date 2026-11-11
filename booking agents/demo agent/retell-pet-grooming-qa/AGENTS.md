# AGENTS.md — Retell Pet Grooming Voice QA

## Mission
Independent Retell-to-Retell QA caller + orchestrator + judge + calendar verifier + Streamlit dashboard for an **existing** pet grooming receptionist.

## Non-negotiables
- Do not rebuild or silently modify the production receptionist.
- Do not disconnect or rewrite the live calendar.
- Stateful tests are BLOCKED until sandbox proof is complete.
- Defaults: `ACK_TARGET_NUMBER=NO`, `ALLOW_SANDBOX_WRITES=NO`, `MAX_CALLS=3`.
- Never fabricate transcripts, bookings, recordings, or passes.
- Never put secrets in prompts, logs, or git.

## Discovered integration (this workspace)
- Receptionist: Taft Grooming Demo `agent_7fd690435a3abdb17cbc4d38c9`
- Calendar: **Cal.com** via Retell native tools (`check_calcom_availability`, `book_calcom_appointment`, `list_calcom_bookings`, `get_calcom_booking`)
- Cancel/reschedule tools: **not attached** — related scenarios must test honest fallback or stay blocked/N/A until staging tools exist
- Default demo path: `RETELL_CALL_MODE=web` — VOICE runs Retell LLM simulation (no phone numbers). Phone Retell-to-Retell still needs numbers + `ACK_TARGET_NUMBER=YES` (QA caller exists: `agent_2c4935e05f846fecd384ad78d1`)
- Sandbox calendar proof approved; `ALLOW_SANDBOX_WRITES=YES`; Cal.com verifier uses bookings API with User-Agent
- Local stub harness (`scripts/run_stub_adapter.py` → `TEST_ADAPTER_URL=http://127.0.0.1:8787`) unblocks AUDIO/FAULT/DROP for **demo only** (synthetic evidence, `stub: true`)

## Specialist roles
1. Retell connectivity — inspect, QA caller, calls, correlation, budgets
2. Calendar — Cal.com sandbox verification, snapshots, assertions
3. QA evaluation — judge, scoring, defects, dashboard
4. Independent verification — safety tests, zip, secret scan

## Execution order
1. `python scripts/setup.py`
2. Fill `.env` locally
3. `python scripts/validate.py`
4. `python -m unittest discover -s tests -p "test_*.py"`
5. `python scripts/preflight.py --mode readonly`
6. `python scripts/run_smoke.py` (A01,A02,A05)
7. Only after sandbox proof: booking tests D01 → D06 → D02
8. `streamlit run dashboard/app.py`
9. `python scripts/create_zip.py`
