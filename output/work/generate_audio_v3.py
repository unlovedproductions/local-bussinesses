#!/usr/bin/env python3
"""Generate Local SEO demo narration (Video 3)."""
from __future__ import annotations

import asyncio
import json
import subprocess
from pathlib import Path

import edge_tts

ROOT = Path(__file__).resolve().parent
VOICE = "en-US-AndrewNeural"
RATE = "-5%"

# Practical, claim-safe local SEO VO for a local independent store owner.
# Same fictional brand context as the other demos. No guaranteed rankings/traffic.
V3 = [
    (
        "title",
        "Here's a simple look at how local SEO could help a store like Smoke and Supply show up when nearby customers are searching.",
    ),
    (
        "s1",
        "Local SEO is about being findable when someone nearby searches for what you sell — on Google Search, Maps, and related results.",
    ),
    (
        "s2",
        "A strong Google Business Profile can be a starting point: your name, address, hours, categories, photos, and how customers can contact you.",
    ),
    (
        "s3",
        "When someone searches for a product or service near them, your store could appear in the local pack or on the map — alongside other nearby options.",
    ),
    (
        "s4",
        "Your website can support that by making it clear where you are, what you offer, and which areas you serve — without promising a specific ranking.",
    ),
    (
        "s5",
        "Reviews and ratings matter to many shoppers. Encouraging honest customer feedback, when appropriate, can help build trust over time.",
    ),
    (
        "s6",
        "Consistent business information — the same name, address, and phone number across your profile, website, and directories — helps search systems understand your store.",
    ),
    (
        "s7",
        "For the owner, the practical benefit is visibility: more chances to be seen by people already looking for a local option.",
    ),
    (
        "s8",
        "Local SEO doesn't replace good service or a clear offer. It can make it easier for the right nearby customers to find you in the first place.",
    ),
    (
        "end",
        "This is a simulated concept. Actual local search results depend on competition, Google's systems, your category, and how the store's listings and website are set up.",
    ),
]


def duration(path: Path) -> float:
    out = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        text=True,
    ).strip()
    return float(out)


async def main() -> None:
    out_dir = ROOT / "audio" / "v3"
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    t = 0.0
    pad = 0.45
    for key, text in V3:
        mp3 = out_dir / f"{key}.mp3"
        await edge_tts.Communicate(text, VOICE, rate=RATE).save(str(mp3))
        d = duration(mp3)
        hold = max(d + pad, 3.2 if key == "title" else (d + pad))
        if key == "end":
            hold = max(d + 1.2, 5.5)
        rows.append(
            {
                "id": key,
                "text": text,
                "audio": str(mp3.relative_to(ROOT)),
                "speech_s": round(d, 3),
                "start_s": round(t, 3),
                "duration_s": round(hold, 3),
            }
        )
        t += hold
    manifest = {"voice": VOICE, "rate": RATE, "total_s": round(t, 3), "scenes": rows}
    (ROOT / "timeline-v3.json").write_text(json.dumps(manifest, indent=2))
    print(f"v3: {t:.1f}s across {len(rows)} scenes")


if __name__ == "__main__":
    asyncio.run(main())
