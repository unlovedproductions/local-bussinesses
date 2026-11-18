# Dependency Management

| Area | Manifest | Install |
|---|---|---|
| QA | `retell-pet-grooming-qa/requirements.txt`, `pyproject.toml` | `pip install -r requirements.txt` |
| Coordination | none (stdlib) | — |
| Docs scripts | none (stdlib) | — |

Pin/upgrade QA deps deliberately; run unit tests + `validate.py` after changes. Record doc impact if install/run commands change.
