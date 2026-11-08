# Defect Repair Guidance

Do not alter the production receptionist without operator approval.

Preferred order:
1. Reproduce on staging with the failing scenario ID.
2. Confirm authoritative backend evidence (Cal.com booking state, tool results).
3. Apply the smallest staging prompt/tool/knowledge change that addresses the root cause.
4. Re-run the failed test plus the generated regression selection.
5. Compare before/after results.
6. Only then propose production promotion.

Write recommended fixes that name the component:
- Retell system prompt section
- Knowledge base / business facts
- Cal.com tool configuration
- Transfer / CRM / notification wiring
- Authorization / identity checks

Avoid generic advice such as "improve the prompt."
