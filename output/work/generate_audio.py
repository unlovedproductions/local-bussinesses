#!/usr/bin/env python3
"""Generate per-scene narration with edge-tts and write timing manifests."""
from __future__ import annotations

import asyncio
import json
import subprocess
from pathlib import Path

import edge_tts

ROOT = Path(__file__).resolve().parent
VOICE = "en-US-AndrewNeural"
RATE = "-5%"

V1 = [
    ("title", "Here's an example of how online ordering, your POS, and inventory could work together."),
    ("s1", "A customer visits the Smoke and Supply website, finds a product, and places an order for in-store pickup."),
    ("s2", "That order can then move from the website into the store's connected systems, so it doesn't have to remain separate from the rest of the store's sales."),
    ("s3", "The order can appear for store staff, showing what was ordered and that it's ready to be prepared for pickup."),
    ("s4", "Now let's follow that same product. We start with 25 units. After the online purchase, the connected inventory could reflect 24."),
    ("s5", "Later, two more units are sold at the counter. The POS records the sale, and the inventory could change from 24 to 22."),
    ("s6", "That updated quantity can then be synchronized back to the website, so the online availability reflects the connected inventory."),
    ("s7", "As that inventory continues to fall, the system can flag a product when it reaches the store's minimum stock level."),
    ("s8", "For example, this product has eight units available, a minimum of ten, and average daily sales of four. Based on the store's own rules and supplier information, the system could suggest a reorder quantity."),
    ("s9", "The goal is to connect the pieces: online orders, in-store sales, and inventory information. That gives the owner a clearer view of what's selling, what's running low, and what may need attention—without treating each part as a completely separate process."),
    ("end", "This is a simulated concept. The actual setup would depend on the store's POS, inventory system, and available integrations."),
]

V2 = [
    ("title", "Once your sales and inventory are connected, here's the kind of information you could have available from the owner's dashboard."),
    ("s1", "Instead of starting with individual transactions, the owner can start with a quick overview of what's happening across the store."),
    ("s2", "Sales can be separated into online and in-store activity, making it easier to see where today's transactions are coming from."),
    ("s3", "The owner can also see online orders and their status, giving them a quick way to monitor the pickup side of the business."),
    ("s4", "A top-sellers view can show which products are moving, giving the owner another piece of information to consider when managing inventory and placing orders."),
    ("s5", "The inventory view brings attention to products that may need attention, rather than making the owner search through every item manually."),
    ("s6", "When supported by the selected system, low-stock alerts could notify the owner when an item reaches a defined threshold."),
    ("s7", "Now the owner can look at sales activity alongside inventory information and see how products are moving through the store."),
    ("s8", "Instead of digging through different systems to figure out what needs attention, the dashboard can bring those items into one place."),
    ("s9", "The goal isn't simply to give the owner another dashboard. It's to make the information from the store's different sales channels easier to understand and act on. This is what a connected setup could look like."),
    ("end", "This is a simulated concept. Actual dashboard features and integrations depend on the systems selected for the store."),
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


async def synth(video: str, scenes: list[tuple[str, str]]) -> list[dict]:
    out_dir = ROOT / "audio" / video
    out_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    t = 0.0
    pad = 0.45  # pause after each scene
    for key, text in scenes:
        mp3 = out_dir / f"{key}.mp3"
        communicate = edge_tts.Communicate(text, VOICE, rate=RATE)
        await communicate.save(str(mp3))
        d = duration(mp3)
        # Hold a bit longer than speech so visuals can land
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
    manifest = {
        "voice": VOICE,
        "rate": RATE,
        "total_s": round(t, 3),
        "scenes": rows,
    }
    (ROOT / f"timeline-{video}.json").write_text(json.dumps(manifest, indent=2))
    print(f"{video}: {t:.1f}s across {len(rows)} scenes")
    return rows


async def main() -> None:
    await synth("v1", V1)
    await synth("v2", V2)


if __name__ == "__main__":
    asyncio.run(main())
