# Church Website Proposal

Bilingual (English / Spanish) proposal site for Grace Community Church with two design mockups.

**Live site:** [church.unlovedproductions.com](https://church.unlovedproductions.com)

**Smoke & Supply demo:** [smoke.unlovedproductions.com](https://smoke.unlovedproductions.com) · [videos](https://smoke.unlovedproductions.com/videos) · (alias: [smoke-supply-demo.vercel.app](https://smoke-supply-demo.vercel.app))

## Routes

| Path | Content |
|------|---------|
| `/` | Client proposal page |
| `/traditional` | Traditional design mockup |
| `/modern` | Modern design mockup |

Smoke & Supply (separate Vercel project under `smoke-supply/`): `/`, `/videos`, `/how-it-works`, `/admin`, `/local-seo`.


## Preview Locally

Static files — no build step required:

```bash
# From repo root, serve locally
python3 -m http.server 8080
# Then open http://localhost:8080/
```

Or open files directly:

```bash
xdg-open index.html
xdg-open traditional/index.html
xdg-open modern/index.html
```

## Language Behavior

All three pages auto-detect browser language (Spanish → `es`, else English). Each page has an EN/ES toggle; the choice is stored in `localStorage` under `preferredLang` and persists across routes.

## File Structure

```
/
├── index.html              # Proposal homepage
├── traditional/
│   ├── index.html
│   └── styles.css
├── modern/
│   ├── index.html
│   └── styles.css
└── shared/
    └── i18n.js             # i18n for mockup pages
```

## Deploy (Vercel)

Static site — no build command. Framework preset: **Other**.

```bash
vercel link          # link or create project
vercel --prod        # deploy to production
```

Custom domain: `church.unlovedproductions.com`

1. Add the domain in Vercel project settings (or `vercel domains add church.unlovedproductions.com church-site`)
2. At your **registrar** (nameservers are `dns1.registrar-servers.com`, not Vercel), add:

```
Type:  A
Name:  church
Value: 76.76.21.21
```

Vercel also accepts pointing nameservers to `ns1.vercel-dns.com` / `ns2.vercel-dns.com` if you prefer centralized DNS.

3. Wait for DNS + SSL, then verify `/`, `/traditional`, and `/modern`.
