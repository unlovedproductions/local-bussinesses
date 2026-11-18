# Sales Stages (Staging Defaults)

Aligned to ERPNext Opportunity sales-stage usage. Adjust only via coordinator ADR.

| Stage | Meaning | Typical next action |
|---|---|---|
| `Lead` | Unqualified interest captured | Assign owner; gather contact/org facts |
| `Qualified` | Requirement/budget/timing checked | Schedule discovery |
| `Discovery` | Needs analysis in progress | Confirm product fit with verified capabilities |
| `Demo` | Product demonstration planned/done | Collect objections; attach demo evidence |
| `Proposal` | Commercial proposal prepared | Send quote; track response |
| `Negotiation` | Terms under discussion | Update amount/probability |
| `Won` | Closed won | Ensure Customer/Contact party fields filled |
| `Lost` | Closed lost | Record loss reason in notes |

## Rules

- Do not jump to `Won` without party fields and verified commercial acceptance evidence.
- Market Research may set stages through `Qualified`; later stages need coordinator or explicit sales evidence.
- Product claims in notes must cite `verified_capabilities` with status VERIFIED.
