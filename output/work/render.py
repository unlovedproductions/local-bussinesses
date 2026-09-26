#!/usr/bin/env python3
"""Concatenate VO, record HTML timelines, mux final MP4s."""
from __future__ import annotations

import asyncio
import json
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCENES = ROOT / "scenes"
FRAMES = ROOT / "frames"
VIDEOS = ROOT.parent / "videos"
CHROME = Path("/home/unloved/.local/bin/chromium")


def run(cmd: list[str], **kw) -> None:
    print("+", " ".join(cmd[:8]), "..." if len(cmd) > 8 else "")
    subprocess.check_call(cmd, **kw)


def build_voiceover(video: str) -> Path:
    manifest = json.loads((ROOT / f"timeline-{video}.json").read_text())
    out = ROOT / "audio" / f"{video}-full.wav"
    parts_dir = ROOT / "audio" / f"{video}-parts"
    parts_dir.mkdir(parents=True, exist_ok=True)
    list_file = parts_dir / "concat.txt"
    lines: list[str] = []

    for i, scene in enumerate(manifest["scenes"]):
        src = ROOT / scene["audio"]
        speech = scene["speech_s"]
        hold = scene["duration_s"]
        pad = max(0.0, hold - speech)
        part = parts_dir / f"{i:02d}-{scene['id']}.wav"
        # Decode mp3 → wav at exact speech length, then pad silence
        tmp = parts_dir / f"{i:02d}-raw.wav"
        run(
            [
                "ffmpeg", "-y", "-i", str(src),
                "-ar", "48000", "-ac", "1",
                str(tmp),
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if pad > 0.05:
            run(
                [
                    "ffmpeg", "-y",
                    "-i", str(tmp),
                    "-af", f"apad=pad_dur={pad:.3f}",
                    "-t", f"{hold:.3f}",
                    str(part),
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        else:
            run(
                [
                    "ffmpeg", "-y", "-i", str(tmp),
                    "-t", f"{hold:.3f}",
                    str(part),
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        lines.append(f"file '{part.name}'")

    list_file.write_text("\n".join(lines) + "\n")
    run(
        [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", str(list_file),
            "-c:a", "pcm_s16le",
            str(out),
        ],
        cwd=str(parts_dir),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    # Loudnorm for clear narration
    norm = ROOT / "audio" / f"{video}-vo.wav"
    run(
        [
            "ffmpeg", "-y", "-i", str(out),
            "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
            str(norm),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return norm


def make_bed(duration: float, out: Path) -> Path:
    """Quiet warm pad under VO — sine chords, very low volume."""
    # Two soft tones, amplitude low enough not to compete
    run(
        [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"sine=frequency=220:sample_rate=48000:duration={duration:.3f}",
            "-f", "lavfi",
            "-i", f"sine=frequency=330:sample_rate=48000:duration={duration:.3f}",
            "-filter_complex",
            "[0][1]amix=inputs=2:duration=longest,volume=0.035,afade=t=in:st=0:d=2,afade=t=out:st={0}:d=2".format(
                max(0.1, duration - 2)
            ),
            "-ar", "48000", "-ac", "2",
            str(out),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return out


async def record_html(html: Path, duration: float, out_webm: Path) -> None:
    from playwright.async_api import async_playwright

    FRAMES.mkdir(parents=True, exist_ok=True)
    out_webm.parent.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path=str(CHROME),
            headless=True,
            args=["--disable-dev-shm-usage", "--no-sandbox"],
        )
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=1,
            record_video_dir=str(out_webm.parent),
            record_video_size={"width": 1920, "height": 1080},
        )
        page = await context.new_page()
        await page.goto(html.as_uri(), wait_until="networkidle")
        await page.wait_for_function("() => window.__demo && window.__demo.total")
        total = await page.evaluate("() => window.__demo.total")
        await page.evaluate("() => window.__demo.start()")
        # Record slightly past end
        await page.wait_for_timeout(int((total + 0.8) * 1000))
        video = page.video
        await page.close()
        await context.close()
        await browser.close()
        if video:
            path = await video.path()
            Path(path).replace(out_webm)
            print(f"recorded {out_webm} ({total:.1f}s timeline)")


def mux(video_in: Path, vo: Path, bed: Path, out_mp4: Path, duration: float) -> None:
    # Mix VO + bed, encode H.264
    run(
        [
            "ffmpeg", "-y",
            "-i", str(video_in),
            "-i", str(vo),
            "-i", str(bed),
            "-filter_complex",
            "[1:a]aformat=sample_rates=48000:channel_layouts=mono[vo];"
            "[2:a]aformat=sample_rates=48000:channel_layouts=stereo[bed];"
            "[vo][bed]amix=inputs=2:duration=first:dropout_transition=0,volume=1.1[a]",
            "-map", "0:v",
            "-map", "[a]",
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            "-r", "30",
            "-c:a", "aac",
            "-b:a", "192k",
            "-t", f"{duration:.3f}",
            "-movflags", "+faststart",
            str(out_mp4),
        ],
    )


def duration_of(path: Path) -> float:
    out = subprocess.check_output(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        text=True,
    ).strip()
    return float(out)


async def main() -> None:
    VIDEOS.mkdir(parents=True, exist_ok=True)

    jobs = [
        ("v1", SCENES / "video1.html", VIDEOS / "01-pos-inventory-integration.mp4"),
        ("v2", SCENES / "video2.html", VIDEOS / "02-owner-dashboard.mp4"),
    ]

    for key, html, mp4 in jobs:
        print(f"\n=== Building {key} ===")
        vo = build_voiceover(key)
        vo_dur = duration_of(vo)
        manifest = json.loads((ROOT / f"timeline-{key}.json").read_text())
        target = manifest["total_s"]
        print(f"VO duration {vo_dur:.2f}s, timeline {target:.2f}s")

        bed = make_bed(max(vo_dur, target) + 0.5, ROOT / "audio" / f"{key}-bed.wav")
        webm = ROOT / "frames" / f"{key}.webm"
        await record_html(html, target, webm)

        # Trim/pad video to match audio
        dur = max(vo_dur, target)
        mux(webm, vo, bed, mp4, dur)
        print(f"Wrote {mp4} ({duration_of(mp4):.2f}s)")


if __name__ == "__main__":
    asyncio.run(main())
