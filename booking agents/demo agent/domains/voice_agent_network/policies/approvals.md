# Integration & Production Approval Policy (M6)

## Installation vs authorization

Approving installation of a tool ≠ authorizing OAuth/API usage, paid spend, outbound calls, or production deploy.

## Required proposal fields

Tool name, provider, official source, purpose, agents, benefits, essential/optional, alternatives, permissions, data accessed, auth, costs, security, install/remove steps.

## Decisions

`APPROVE_INSTALLATION` | `MORE_INFORMATION` | `SKIP_FOR_NOW` | `REJECT`

## Managed workflow enforcement

Within `coord.py` integration commands, unapproved/rejected integrations cannot be marked `ENABLED` without an approval record. This does not constrain arbitrary terminal use outside the managed workflow.
