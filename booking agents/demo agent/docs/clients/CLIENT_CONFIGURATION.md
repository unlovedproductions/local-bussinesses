# Client Configuration Guide

| Area | Where configured | Notes |
|---|---|---|
| Prompt / persona | Retell dashboard + versioned markdown in repo when approved | Candidates under `domains/voice_agent_network/prompts/versions/` |
| Business facts | Markdown/JSON artifacts | Client-specific → careful git hygiene |
| Calendar | Cal.com event + API keys in `.env` locally | |
| QA targets | `.env` + `config/*.json` | |
| CRM | `coordination/crm-staging/` | Sync BLOCKED |

## Version compatibility

| Product surface | Instructions apply to | Upgrade / rollback |
|---|---|---|
| Taft Grooming Retell+Cal.com demo | `voice-agent/` artifacts as of parent git `main` | Revert prompt paste in Retell; restore prior markdown from git |
| QA auditor | `retell-pet-grooming-qa/` at same commit | Reinstall venv from lock/requirements; do not reuse stale `.env` blindly |
| UAN coordination | `coordination/` + `docs/uan/` | Bus is file-based; restore from git; unfinished claims may need manual cleanup |

Do not present older procedures as current after material Retell tool or Cal.com event changes.

Never commit `.env` or real customer PII.
