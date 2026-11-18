# UAN Agent Registry Mapping

String IDs remain authoritative for CLI and JSON schemas. UAN numbers are aliases.

| UAN ID | String ID | Squad | Mission (summary) | Activation |
|---|---|---|---|---|
| 00 | `coordinator` | Control | Universal Commander — plan, dispatch, conflicts, approvals | Always for multi-agent objectives |
| 10 / 20 | `voice-development` | A/B | Architecture + prompt/conversation engineering | Voice/prompt/architecture work |
| 11 | `market-research` | A | Local business opportunity intelligence | Research / prospects |
| 40 | `integrations` | D | Retell/Cal.com/ERPNext staging | Integration changes |
| 50 | `testing` | E | QA, regression, independent verification (covers 51 scope lightly) | Tests / red-team style reviews |
| 70 | `documentation` | G | Docs integrity + recovery assurance | Doc impact / recovery knowledge |

## Not separately registered (deferred)

| UAN ID | Reason |
|---|---|
| 30 / 31 | Audio specialists — fold into `voice-development` + `testing` until evidence workflows exist |
| 51 | Red-team — `testing` owns independent review posture for now |
| 60 / 61 | Perf/release — coordinator + testing until dedicated need |

## Registration contract fields

See role cards under `coordination/agents/` plus machine config `coordination/config/uan.json`.

## Result contract (tasks)

Task `result` objects should include: summary, evidence, confidence, risks, next_actions. Enforced on COMPLETED/FAILED via `task-transition`.
