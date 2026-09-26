# Smoke & Supply — Demo Prototype

Fictional neighborhood smoke shop demo for presenting a storefront + simulated POS/inventory integration to a real store owner.

**Not a real business. No real payments. No real POS connection.**

This app lives in `smoke-supply/` so it does not replace the church proposal site in the repo root.

## Run locally

```bash
cd smoke-supply
pnpm install
pnpm dev
```

Open the URL printed by Astro (usually `http://localhost:4321`).

## Demonstrate to a store owner

1. Open `/tour` and walk the guided steps, **or**
2. Homepage → Shop → add to cart → Checkout (demo) → confirmation
3. `/admin/orders` — show the new order
4. `/admin/pos` — click **Simulate: customer buys 2 in store → Sync**
5. `/admin/inventory` and `/admin/reorder` — low stock + suggestions
6. `/how-it-works` — 9-scene integration story
7. `/connect` — discovery conversation (no secrets)

## What is simulated

- Product catalog, prices, inventory, customers, sales, analytics
- Checkout and pay-at-pickup (no payment processor)
- POS adapter + inventory sync (`DemoPosAdapter`)
- Reorder math (demo assumptions, labeled on page)

## Phase 2 — ask the owner

- POS name / version
- Inventory software (if separate)
- Receipt photo (no card data) or blurred screenshot
- Vendor/reseller contact
- Existing online ordering tools
- Payment processor preference
- Jurisdiction / age-verification requirements

**Never collect passwords or API keys through the demo.**

## Deploy

Deploy `smoke-supply` as its **own** project. Do not publish it on the church domain. Root `.vercelignore` excludes `smoke-supply` from the church static deploy.
