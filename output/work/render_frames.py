#!/usr/bin/env python3
"""Re-render both videos with frame-accurate HTML seeks (A/V sync fix)."""
from __future__ import annotations

import asyncio
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCENES = ROOT / "scenes"
VIDEOS = ROOT.parent / "videos"
CHROME = Path("/home/unloved/.local/bin/chromium")
FPS = 15  # motion-graphics pace; keeps A/V sync and readable UI


def run(cmd: list[str], **kw) -> None:
    subprocess.check_call(cmd, **kw)


def duration_of(path: Path) -> float:
    return float(
        subprocess.check_output(
            [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(path),
            ],
            text=True,
        ).strip()
    )


async def capture_frames(html: Path, total: float, frame_dir: Path) -> None:
    from playwright.async_api import async_playwright

    if frame_dir.exists():
        shutil.rmtree(frame_dir)
    frame_dir.mkdir(parents=True)

    n = int(total * FPS) + 1
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path=str(CHROME),
            headless=True,
            args=["--disable-dev-shm-usage", "--no-sandbox"],
        )
        page = await browser.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=1)
        await page.goto(html.as_uri(), wait_until="domcontentloaded")
        await page.wait_for_function("() => window.__demo && window.__demo.seek")

        for i in range(n):
            t = i / FPS
            await page.evaluate("(t) => window.__demo.seek(t)", t)
            path = frame_dir / f"f{i:05d}.png"
            await page.screenshot(path=str(path), type="png", animations="disabled")
            if i % 90 == 0:
                print(f"  frame {i}/{n} t={t:.1f}s")

        await browser.close()
    print(f"captured {n} frames -> {frame_dir}")


def encode(frame_dir: Path, vo: Path, bed: Path, out_mp4: Path, duration: float) -> None:
    run(
        [
            "ffmpeg", "-y",
            "-framerate", str(FPS),
            "-i", str(frame_dir / "f%05d.png"),
            "-i", str(vo),
            "-i", str(bed),
            "-filter_complex",
            "[1:a]aformat=sample_rates=48000:channel_layouts=mono[vo];"
            "[2:a]aformat=sample_rates=48000:channel_layouts=stereo[bed];"
            "[vo][bed]amix=inputs=2:duration=first:dropout_transition=0,volume=1.05[a]",
            "-map", "0:v",
            "-map", "[a]",
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-t", f"{duration:.3f}",
            "-movflags", "+faststart",
            str(out_mp4),
        ]
    )


async def main() -> None:
    jobs = [
        ("v1", SCENES / "video1.html", VIDEOS / "01-pos-inventory-integration.mp4"),
        ("v2", SCENES / "video2.html", VIDEOS / "02-owner-dashboard.mp4"),
    ]
    for key, html, mp4 in jobs:
        print(f"\n=== Frame-accurate render {key} ===")
        manifest = json.loads((ROOT / f"timeline-{key}.json").read_text())
        total = manifest["total_s"]
        vo = ROOT / "audio" / f"{key}-vo.wav"
        bed = ROOT / "audio" / f"{key}-bed.wav"
        if not vo.exists():
            raise SystemExit(f"missing {vo}")
        frame_dir = ROOT / "frames" / f"{key}-seq"
        await capture_frames(html, total, frame_dir)
        encode(frame_dir, vo, bed, mp4, total)
        print(f"Wrote {mp4} ({duration_of(mp4):.2f}s)")


if __name__ == "__main__":
    asyncio.run(main())
