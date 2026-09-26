# Smoke & Supply — Demo Prototype

Fictional neighborhood smoke shop demo for presenting a storefront + simulated POS/inventory integration to a real store owner.

**Not a real business. No real payments. No real POS connection.**

## Live URLs

| What | URL |
|------|-----|
| Demo storefront | [https://smoke.unlovedproductions.com](https://smoke.unlovedproductions.com) |
| Sales videos | [https://smoke.unlovedproductions.com/videos](https://smoke.unlovedproductions.com/videos) |
| Vercel alias (works now) | [https://smoke-supply-demo.vercel.app](https://smoke-supply-demo.vercel.app) |

Easy paths: `/` · `/videos` · `/how-it-works` · `/admin` · `/local-seo`

### DNS (registrar)

Nameservers are `dns1.registrar-servers.com` (not Vercel). Add:

```
Type:  A
Host:  smoke
Value: 76.76.21.21
```

The domain is already attached and verified on Vercel project `smoke-supply-demo`. SSL follows after the A record propagates.

This app lives in `smoke-supply/` so it does not replace the church proposal site in the repo root.

## Run locally

```bash
cd smoke-supply
pnpm install
pnpm dev
```

Open the URL printed by Astro (usually `http://localhost:4321`).

## Demonstrate to a store owner

1. Open `/videos` — three sales demos (POS/inventory, owner dashboard, local SEO), **or**
2. Open `/tour` and walk the guided steps, **or**
3. Homepage → Shop → add to cart → Checkout (demo) → confirmation
4. `/admin/orders` — show the new order
5. `/admin/pos` — click **Simulate: customer buys 2 in store → Sync**
6. `/admin/inventory` and `/admin/reorder` — low stock + suggestions
7. `/how-it-works` — 9-scene integration story
8. `/connect` — discovery conversation (no secrets)

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

```bash
cd smoke-supply
pnpm dlx vercel --prod --yes
```

Own Vercel project: `smoke-supply-demo`. Root `.vercelignore` excludes `smoke-supply` from the church static deploy.
