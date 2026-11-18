# Debugging Guide

| Symptom | First checks |
|---|---|
| `coord.py` rejects agent | Agent ID not in `KNOWN_AGENTS` / registry |
| Inbox empty | Wrong `--agent`; messages archived; uncommitted bus on other machine |
| QA validate fails | Missing config JSON / cases path |
| Smoke BLOCKED | Missing API keys, agent IDs, or ACK gates |
| Judge errors | Ollama down / wrong `OLLAMA_BASE_URL` / model OOM |
| Cal.com adapter errors | Key, event type id, timezone, API version |
| Streamlit empty | No files under `qa_runs/` |

Logs/evidence: `retell-pet-grooming-qa/qa_runs/`. Do not commit secrets from debug dumps.
