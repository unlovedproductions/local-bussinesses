# Incident Response

1. Detect via failed QA, client report, or provider outage.
2. Triage severity; protect calendars (keep sandbox writes gated).
3. Use runbook incident IDs.
4. Coordinate via `coord.py` messages (`BLOCKER` / `STATUS_UPDATE`).
5. Rotate credentials if compromise suspected.
6. Post-incident: update docs + shared-context; file DOC_IMPACT if procedures changed.
