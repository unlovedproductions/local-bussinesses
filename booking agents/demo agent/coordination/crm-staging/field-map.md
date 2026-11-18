# Internal Prospect → ERPNext Field Map

Owned by `integrations`. Based on ERPNext CRM Lead / Opportunity / Customer / Contact usage.

| Staging path | ERPNext doctype | ERPNext field (typical) |
|---|---|---|
| `lead.lead_name` | Lead | `lead_name` / person name |
| `lead.organization` | Lead | `company_name` |
| `lead.email` | Lead | `email_id` |
| `lead.phone` | Lead | `mobile_no` / `phone` |
| `lead.source` | Lead | `source` |
| `lead.territory` | Lead | `territory` |
| `lead.industry` | Lead | `industry` |
| `lead.notes` | Lead | `notes` / Communication |
| `opportunity.title` | Opportunity | `title` |
| `opportunity.opportunity_amount` | Opportunity | `opportunity_amount` |
| `opportunity.probability` | Opportunity | `probability` |
| `opportunity.sales_stage` | Opportunity | `sales_stage` |
| `opportunity.expected_closing` | Opportunity | `expected_closing` |
| `opportunity.next_action` | Opportunity / ToDo | next action / assignment note |
| `opportunity.items[]` | Opportunity Item | item / description rows |
| `party.customer_name` | Customer | `customer_name` |
| `party.contact_name` | Contact | `first_name` / full name |
| `party.address` | Address | address lines |
| `communications[]` | Communication | type, date, content |
| `verified_capabilities[]` | Opportunity notes | narrative only; not invent product SKUs |

## Export payload shape

`export-erpnext` emits:

```json
{
  "Lead": { "...": "mapped fields" },
  "Opportunity": { "...": "mapped fields" },
  "Customer": null,
  "Contact": null,
  "meta": { "prospect_id": "...", "generated_at": "..." }
}
```

Network push is out of scope until sync-status is CONFIGURED.
