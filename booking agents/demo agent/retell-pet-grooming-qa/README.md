# Retell Pet Grooming — Autonomous Voice QA Auditor

Independent AI test caller + orchestrator + judge + Cal.com verifier + Streamlit dashboard for an **existing** Retell pet grooming receptionist.

## What this is
- 108 structured voice/audio/fault/drop scenarios (`tests/cases.json`)
- Separate QA caller agent prompt (`prompts/RETELL_QA_CALLER.md`)
- Independent judge (`prompts/INDEPENDENT_JUDGE.md`)
- Fail-closed safety gates (`src/safety.py`)
- Cal.com verification adapter (discovered provider for the Taft demo)
- Streamlit dashboard over **saved** `qa_runs/` only

## What this is not
- A rebuild of your production receptionist
- A license to write to your live customer calendar
- A claim that live Retell/Cal.com calls already passed without credentials

## Discovered target (this workspace)
| Item | Value |
|---|---|
| Business | Taft Grooming Demo |
| Retell agent | `agent_7fd690435a3abdb17cbc4d38c9` |
| Calendar | Cal.com event type `1cFQUeczd2cF5ByMEs8E5i` |
| Phone | Demo uses `RETELL_CALL_MODE=web` (Retell LLM simulation / web_call). PSTN phone path optional |

## Quick start
```bash
cd retell-pet-grooming-qa
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/setup.py
# edit .env with RETELL_API_KEY, agent IDs, numbers, CALCOM_API_KEY
# Judge defaults to local Ollama (JUDGE_PROVIDER=ollama, JUDGE_MODEL=qwen2.5:14b-instruct-q5_K_M)
# Larger models (qwen3.6 / 27b / llama3:70b) are stronger but currently OOM on this host
python scripts/validate.py
python -m unittest discover -s tests -p "test_*.py"
python scripts/preflight.py --mode readonly
python scripts/run_smoke.py
streamlit run dashboard/app.py
python scripts/create_zip.py
```

## Smoke tests
`run_smoke.py` executes **A01, A02, A05** with `MAX_CALLS=3` and readonly gates.  
If phone/QA caller/ACK are missing, results are honestly **BLOCKED** — not fabricated PASS.

## Sandbox booking tests
Only after `config/sandbox_proof.json` is fully approved and `ALLOW_SANDBOX_WRITES=YES`:
```bash
python scripts/run_qa.py --ids D01 --max-calls 1 --mode sandbox
python scripts/run_qa.py --ids D06 --max-calls 1 --mode sandbox
python scripts/run_qa.py --ids D02 --max-calls 1 --mode sandbox
```

## Safety defaults
`ACK_TARGET_NUMBER=NO`, `ALLOW_SANDBOX_WRITES=NO`, `MAX_CALLS=3`.

## Package
```bash
python scripts/create_zip.py
```
Produces `retell-pet-grooming-qa.zip` (also copied next to this folder).

See `docs/` for Retell setup, Cal.com sandbox, playbook, troubleshooting, and security.
