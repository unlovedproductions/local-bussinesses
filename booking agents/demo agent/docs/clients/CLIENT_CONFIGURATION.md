# Client Configuration Guide

| Area | Where configured | Notes |
|---|---|---|
| Prompt / persona | Retell dashboard + versioned markdown in repo when approved | No secrets |
| Business facts | Markdown/JSON artifacts | Client-specific → careful git hygiene |
| Calendar | Cal.com event + API keys in `.env` locally | |
| QA targets | `.env` + `config/*.json` | |
| CRM | `coordination/crm-staging/` | Sync BLOCKED |

Never commit `.env` or real customer PII.
