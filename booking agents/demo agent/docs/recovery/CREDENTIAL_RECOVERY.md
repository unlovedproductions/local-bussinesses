# Credential Recovery

**Never store secret values in this document.**

| Secret class | Recovery path |
|---|---|
| Retell API key | Retell dashboard → regenerate; update local `.env` |
| Cal.com API key | Cal.com settings → regenerate |
| OpenAI (optional judge) | OpenAI dashboard |
| GitHub SSH/HTTPS | Account recovery / new keys; rotate if compromise |
| ERPNext | N/A while sync BLOCKED |

After compromise: rotate all provider keys, revoke sessions, audit Retell agent tools and Cal.com webhooks, record incident.
