# Monitoring

| Signal | How |
|---|---|
| QA run outcomes | `qa_runs/` + Streamlit dashboard |
| Retell | Provider dashboard |
| Cal.com | Provider dashboard / booking list |
| Coordination bus health | `coord.py status` + test_coord.py |
| Doc drift | `scripts/documentation/check_docs.py` |

No dedicated APM in this workspace. Do not invent metrics endpoints.
