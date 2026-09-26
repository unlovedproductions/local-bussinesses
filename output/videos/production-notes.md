# Production notes — Smoke & Supply sales demos

## Deliverables

| File | Duration | Spec |
|------|----------|------|
| `output/videos/01-pos-inventory-integration.mp4` | **103.2s** | 1920×1080, H.264, AAC, 15 fps |
| `output/videos/02-owner-dashboard.mp4` | **94.6s** | 1920×1080, H.264, AAC, 15 fps |
| `output/videos/03-local-seo.mp4` | **95.4s** | 1920×1080, H.264, AAC, 15 fps |

Work files (HTML timelines, VO stems, frame sequences) live under `output/work/`. Source package under `smoke-supply/video-package/` was not modified.

## Authoritative sources used

- Video 1 VO: `01-NARRATION-SCRIPT.md` (revised)
- Video 1 storyboard: `02-STORYBOARD.md`
- Video 2 VO + storyboard: `Sales Dashboard & Owner View-script.md`
- Video 3: Original Local SEO script (not in package) — claim-safe explanation for a local store owner, same visual system as V1/V2
- End card: `08-END-CARD.md` + task qualifier on system dependency (V3 adapted for search/listings)
- Brand: `05-VISUAL-STYLE.md` / site tokens

Ignored as outdated: `src/lib/narration.ts`, `SOURCE-narration.ts`, `06-ARCHITECTURE.txt` qty:5 diagram, `04-CAPTIONS.md` as speech captions (used as scene-label reference only).

## Narration

- Voice: edge-tts `en-US-AndrewNeural`, rate `-5%`
- Videos 1–2: script text unchanged from revised packages
- Video 3: original practical Local SEO VO; no guaranteed rankings/traffic/sales language
- “Smoke & Supply” spoken as “Smoke and Supply” in TTS for pronunciation only; on-screen copy keeps “Smoke & Supply”
- Scene holds follow measured speech + ~0.45s pause (end card +1.2s), not the shorter table in `03-TIMING.md`

## Deviations from storyboard / timing docs

1. **Duration longer than ~90s** — Full scripts at a clear pace land at ~103s / ~95s / ~95s. Timing adjusted; narration not cut.
2. **Frame rate 15 fps** — Frame-accurate HTML capture for A/V sync; motion is discrete UI state changes. Resolution remains 1080p.
3. **Video 2 Scene 7 inventory** — Storyboard “Current: 8 / Minimum: 10” used (not the earlier narration note `22 → 8`).
4. **Background audio** — No approved music in package; very quiet dual-sine pad under VO.
5. **Captions** — Burned speech-aligned lower-thirds from final VO.
6. **Architecture diagram qty:5** — Not used; Scene 6 shows **22** on POS/inventory and website.
7. **Video 3** — No storyboard in package; matched V1/V2 brand, tone, DEMO labeling, and end-card pattern. Local pack placement is explicitly example-only.

## Inventory consistency (Video 1)

Product X: **25 → 24** (online ×1) → **24 → 22** (in-store ×2) → website sync **22** → visible **Later** jump → **8** available / min **10** → reorder suggestion **30**.

## Video 3 scene flow (Local SEO)

1. What local SEO is (Search / Maps / store)
2. Google Business Profile (simulated)
3. Local pack / Maps example (illustrative ranking)
4. Website support for location clarity (no ranking promises)
5. Reviews & trust
6. NAP consistency across profile / website / directories
7. Owner benefit: be seen / be clear / build trust
8. Takeaway + end card (rankings/traffic not guaranteed)

## Claim / demo qualification on screen

- Persistent `DEMO · SIMULATED` on UI scenes
- End-card language: simulated data; real setup depends on the store’s systems/listings
- Video 3: simulated search/listings; rankings and traffic not guaranteed
- Fictional products only; no real POS or tobacco brand marks

## Technical limitations

- No pre-existing logos, fonts packs, music, or video assets in the package — all UI drawn for these renders
- Astro demo site was not screen-recorded
- Final encodes use seek-driven PNG sequences muxed to the VO timeline

## QC checks performed

- Pulled frames at inventory beats, Later/low-stock, reorder, owner dashboard, end cards (V1/V2)
- Pulled frames at GBP, local pack, NAP, end card (V3)
- Confirmed 1920×1080 h264 + aac via ffprobe
- Confirmed disclaimer end cards present on all three videos
