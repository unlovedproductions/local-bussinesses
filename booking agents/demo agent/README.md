# AI Voice Booking Agents

Workspace for Unloved Productions local-business **AI voice booking** demos, QA auditing, multi-agent coordination, and client implementation knowledge.

> This folder is **not** its own git root. It lives in the parent repository `local-bussinesses` (GitHub: `unlovedproductions/local-bussinesses`).

## Purpose

Help authorized operators and AI agents:

1. Understand the Retell + Cal.com booking demo and QA auditor.
2. Reconstruct a development environment.
3. Coordinate work across logical agent roles.
4. Onboard supported clients using verified capabilities only.
5. Operate, troubleshoot, and recover using documented procedures.

## Verified capabilities

| Capability | Status | Source of truth |
|---|---|---|
| Browser Retell web call → Cal.com availability/book/list/get | Configured (live E2E needs credentials) | [`voice-agent/README.md`](voice-agent/README.md) |
| Autonomous voice QA auditor + Streamlit dashboard | Implemented | [`retell-pet-grooming-qa/README.md`](retell-pet-grooming-qa/README.md) |
| Repo-bus multi-agent coordination | Implemented | [`coordination/README.md`](coordination/README.md) |
| ERPNext CRM live sync | BLOCKED | [`coordination/crm-staging/`](coordination/crm-staging/) |
| Reschedule / cancel booking tools | Not attached | `voice-agent/README.md` |

Do not market PROPOSED features (e.g. HVAC emergency intake) as shipped.

## Subprojects

| Path | Role |
|---|---|
| `voice-agent/` | Taft Grooming demo artifacts (prompt, facts, verification) |
| `retell-pet-grooming-qa/` | Independent QA caller/judge/orchestrator |
| `coordination/` | Multi-agent inbox, tasks, shared context, CRM staging |
| `research/local-market-intelligence/` | Market research outputs |
| `docs/` | Workspace documentation system (this pass) |

## Architecture (overview)

```text
Browser caller → Retell AI (web call) → Cal.com tools → demo calendar
Independent QA suite exercises the receptionist; does not rebuild it.
Agents coordinate via git-backed coordination/ (poll inbox; not real-time).
```

Details: [`docs/SYSTEM_ARCHITECTURE.md`](docs/SYSTEM_ARCHITECTURE.md).

## Prerequisites

- Git access to parent remote `unlovedproductions/local-bussinesses`
- Python 3.10+ (QA suite; coordination CLI is stdlib)
- Retell + Cal.com accounts/API keys for live tests (never commit secrets)
- Optional: Ollama for local QA judge

## Quick start

```bash
# From parent clone, enter this workspace:
cd "booking agents/demo agent"

# Coordination
python3 coordination/scripts/coord.py status
python3 coordination/scripts/coord.py inbox --agent documentation

# Voice demo — follow voice-agent/README.md (Retell dashboard + Cal.com)

# QA auditor
cd retell-pet-grooming-qa
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/setup.py
# edit .env from .env.example — do not commit
python scripts/validate.py
python -m unittest discover -s tests -p "test_*.py"
python scripts/preflight.py --mode readonly
python scripts/run_smoke.py
```

## Documentation

- Index: [`docs/DOCUMENTATION_INDEX.md`](docs/DOCUMENTATION_INDEX.md)
- Registry: [`docs/DOCUMENTATION_REGISTRY.md`](docs/DOCUMENTATION_REGISTRY.md)
- Developer setup: [`docs/development/DEVELOPER_SETUP.md`](docs/development/DEVELOPER_SETUP.md)
- Recovery start: [`docs/recovery/EMERGENCY_RECOVERY_START_HERE.md`](docs/recovery/EMERGENCY_RECOVERY_START_HERE.md)
- Agents: [`AGENTS.md`](AGENTS.md)

## Documentation checks

```bash
python3 scripts/documentation/check_docs.py
python3 scripts/documentation/test_check_docs.py
```

## Contribution / coordination

Follow [`AGENTS.md`](AGENTS.md). Material code/config changes require a documentation impact assessment ([`docs/templates/DOCUMENTATION_IMPACT.md`](docs/templates/DOCUMENTATION_IMPACT.md)).

## Recovery

Primary recoverable source today: parent GitHub remote. **Independent off-repo backup is not yet activated.** See recovery docs. Export pack:

```bash
export DR_EXPORT_DIR=/path/outside/this/repo
python3 scripts/documentation/export_emergency_pack.py
```

Last foundation review: 2026-11-18.
