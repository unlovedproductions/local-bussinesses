# Security & Approvals (M6)

Registry: `coordination/config/integrations.json`  
Policy: `domains/voice_agent_network/policies/approvals.md`  
Audit records: `coordination/approvals/records/`

CLI:

```bash
python3 coordination/scripts/coord.py integrations
python3 coordination/scripts/coord.py integration-propose --file path.json
python3 coordination/scripts/coord.py integration-set-status --id <id> --status PROPOSED --agent coordinator
python3 coordination/scripts/coord.py approvals
```

Credential rule: never commit secrets; reference vault/process only.
