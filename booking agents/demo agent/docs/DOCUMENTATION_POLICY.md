# Documentation Source-of-Truth Policy

| Field | Value |
|---|---|
| Owner | documentation |
| Classification | INTERNAL |
| Status | VERIFIED (policy text); compliance continuous |
| Last verified | 2026-11-18 |

## Principles

1. **One authoritative source per subject.** Other docs link; they do not fork procedures.
2. **Documentation must reflect reality.** Label VERIFIED / IMPLEMENTED BUT UNTESTED / PROPOSED / BLOCKED / OUTDATED.
3. **Evidence before VERIFIED.** Existence ≠ accuracy ≠ operational readiness.
4. **No secrets** in git documentation (API keys, tokens, customer PII, recordings).
5. **Documentation Agent** maintains integrity; it does not approve production architecture or release alone.

## Authoritative locations

| Subject | Authoritative source |
|---|---|
| Workspace introduction | Root `README.md` |
| Agent coordination | `AGENTS.md` + `coordination/` |
| Demo voice booking | `voice-agent/README.md` |
| QA auditor | `retell-pet-grooming-qa/README.md` + `retell-pet-grooming-qa/docs/` |
| Architecture (workspace) | `docs/SYSTEM_ARCHITECTURE.md` |
| Configuration names | `docs/CONFIGURATION_REFERENCE.md` (+ `.env.example`) |
| Client onboarding | `docs/clients/` |
| Operations | `docs/operations/` |
| Disaster recovery | `docs/recovery/` |
| ADRs | `coordination/decisions/` |
| Verified product features | `coordination/shared-context/verified-features.md` |

## Change rule

Material changes to code, prompts, integrations, env vars, deployment, or agent roles require a [DOCUMENTATION_IMPACT](templates/DOCUMENTATION_IMPACT.md) assessment and, when needed, a `DOCUMENTATION_REQUEST` / `DOC_IMPACT` message to `documentation`.
