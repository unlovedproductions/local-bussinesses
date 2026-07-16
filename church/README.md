# Church Websites

Two bilingual (English / Spanish) church website variants for Grace Community Church.

## Sites

| Folder | Style |
|--------|-------|
| `traditional/` | Classic — serif typography, burgundy/cream/gold palette, stained-glass motifs |
| `ultra-modern/` | Contemporary — dark theme, gradient accents, glassmorphism, bold typography |

## Preview Locally

Open either site directly in your browser — no build step or server required:

```bash
xdg-open traditional/index.html
xdg-open ultra-modern/index.html
```

Or from the repo root:

```bash
xdg-open church/traditional/index.html
xdg-open church/ultra-modern/index.html
```

## Language Behavior

Both sites automatically detect the visitor's browser language:

- **Spanish** (`es`, `es-MX`, etc.) → all content in Spanish
- **English** or any other language → English (default)

Detection reads `navigator.languages` first, then falls back to `navigator.language`.

### Manual Override

Each site has an **EN | ES** toggle in the header. Selecting a language:

1. Immediately switches all page text
2. Saves the choice to `localStorage` (key: `church-lang`)
3. Overrides browser detection on future visits

To reset to browser detection, clear site data or run in the browser console:

```js
localStorage.removeItem('church-lang');
location.reload();
```

## Editing Copy

Translations live in the `TRANSLATIONS` object at the bottom of each site's `index.html`:

- `church/traditional/index.html`
- `church/ultra-modern/index.html`

Each key maps to English (`en`) and Spanish (`es`) strings. Elements with `data-i18n="key.name"` are updated automatically.

To change the church name, search for `Grace Community Church` / `Iglesia Comunidad de Gracia` in both files.

## File Structure

```
church/
├── shared/
│   └── i18n.js          # Language detection and DOM translation
├── traditional/
│   ├── index.html
│   └── styles.css
├── ultra-modern/
│   ├── index.html
│   └── styles.css
└── README.md
```

## Sections (both sites)

- Hero / welcome
- About
- Worship service times
- Ministries
- Contact info
- Footer
