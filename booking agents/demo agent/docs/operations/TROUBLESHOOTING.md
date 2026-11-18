# Troubleshooting

Workspace-level pointer. QA-specific: `retell-pet-grooming-qa/docs/TROUBLESHOOTING.md`.

| Issue | Check |
|---|---|
| Import / module errors | venv activated; `pip install -r requirements.txt` |
| Wrong agent called | `RECEPTIONIST_AGENT_ID` / QA caller IDs |
| Calendar mismatch | event type id + timezone |
| Coordination schema errors | message enums / agent IDs |
| Docs check fail | run `check_docs.py` and fix links/registry |
