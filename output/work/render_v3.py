#!/usr/bin/env python3
"""Build VO + bed + frame-accurate MP4 for Video 3 (Local SEO)."""
from __future__ import annotations

import asyncio
import json
import subprocess
from pathlib import Path

from render_frames import capture_frames, duration_of, encode

ROOT = Path(__file__).resolve().parent
SCENES = ROOT / "scenes"
VIDEOS = ROOT.parent / "videos"


def run(cmd: list[str], **kw) -> None:
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
        tmp = parts_dir / f"{i:02d}-raw.wav"
        run(
            ["ffmpeg", "-y", "-i", str(src), "-ar", "48000", "-ac", "1", str(tmp)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if pad > 0.05:
            run(
                [
                    "ffmpeg", "-y", "-i", str(tmp),
                    "-af", f"apad=pad_dur={pad:.3f}",
                    "-t", f"{hold:.3f}",
                    str(part),
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        else:
            run(
                ["ffmpeg", "-y", "-i", str(tmp), "-t", f"{hold:.3f}", str(part)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        lines.append(f"file '{part.name}'")

    list_file.write_text("\n".join(lines) + "\n")
    run(
        [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", str(list_file), "-c:a", "pcm_s16le", str(out),
        ],
        cwd=str(parts_dir),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
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
    run(
        [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"sine=frequency=220:sample_rate=48000:duration={duration:.3f}",
            "-f", "lavfi",
            "-i", f"sine=frequency=330:sample_rate=48000:duration={duration:.3f}",
            "-filter_complex",
            "[0][1]amix=inputs=2:duration=longest,volume=0.035,"
            f"afade=t=in:st=0:d=2,afade=t=out:st={max(0.1, duration - 2)}:d=2",
            "-ar", "48000", "-ac", "2",
            str(out),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return out


async def main() -> None:
    key = "v3"
    html = SCENES / "video3.html"
    mp4 = VIDEOS / "03-local-seo.mp4"
    VIDEOS.mkdir(parents=True, exist_ok=True)

    print("=== Building VO ===")
    vo = build_voiceover(key)
    manifest = json.loads((ROOT / f"timeline-{key}.json").read_text())
    total = manifest["total_s"]
    print(f"VO {duration_of(vo):.2f}s / timeline {total:.2f}s")
    bed = make_bed(total + 0.5, ROOT / "audio" / f"{key}-bed.wav")

    print("=== Capturing frames ===")
    frame_dir = ROOT / "frames" / f"{key}-seq"
    await capture_frames(html, total, frame_dir)
    encode(frame_dir, vo, bed, mp4, total)
    print(f"Wrote {mp4} ({duration_of(mp4):.2f}s)")


if __name__ == "__main__":
    asyncio.run(main())
