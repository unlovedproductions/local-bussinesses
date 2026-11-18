# Technology Stack

| Layer | Technology | Evidence |
|---|---|---|
| Voice AI | Retell AI | voice-agent, retell_client.py |
| Calendar | Cal.com API v2 | calcom_adapter.py, .env.example |
| Demo assets | Markdown / JSON | voice-agent/ |
| QA runtime | Python 3 | retell-pet-grooming-qa/pyproject.toml, requirements.txt |
| QA UI | Streamlit | dashboard/app.py |
| Judge LLM | Ollama (default) or OpenAI | JUDGE_PROVIDER |
| Coordination | Python stdlib CLI | coordination/scripts/coord.py |
| Docs checks | Python stdlib | scripts/documentation/ |
| Hosting of demo | Retell + Cal.com SaaS | no app server in voice-agent |
| Parent VCS | Git / GitHub | local-bussinesses remote |

Package manager for QA: `pip` + `requirements.txt` / `pyproject.toml`. Coordination has no third-party deps.
