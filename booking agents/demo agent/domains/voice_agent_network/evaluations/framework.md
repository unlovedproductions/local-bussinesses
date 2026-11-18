# VOICE-AIN Evaluation Framework (M10)

Evidence labels: `SYNTHETIC` | `SIMULATED` | `INTEGRATION_TEST` | `RECORDED_CALL` | `HUMAN_EVALUATED` | `PRODUCTION_OBSERVED`

Never present simulations as production results.

## Dimensions

| Dimension | Primary owner | Measurement source |
|---|---|---|
| Task success | testing | QA cases / live evidence |
| Conversation quality | voice-development + testing | Judge + human notes |
| Prompt compliance | voice-development | Prompt review workflow |
| Tool accuracy | integrations + testing | Cal.com adapters / stub harness |
| Latency / audio | testing | Only with real traces |
| Security / privacy | testing | Redteam workflow |
| Documentation integrity | documentation | check_docs.py |

## Separate scores

- Performance Score
- Evidence Confidence
- Operational Risk
- Release Readiness

Critical failures must not be hidden by averages.

## Existing harness

Authoritative executable tests live in `retell-pet-grooming-qa/`. This framework contracts routing and labeling; it does not replace the QA suite.
