#!/usr/bin/env python3
"""Build the 90s voice-agent sales clip: edge-tts + HTML timeline + ffmpeg."""
from __future__ import annotations

import asyncio
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT.parent
OUT_VIDEOS = ASSETS / "videos"
WORK = ROOT / "work"
AUDIO = WORK / "audio"
VOICE = "en-US-AndrewNeural"
RATE = "-5%"

# Keep total near 90s; holds include short pause after speech.
# Spoken VO only. Avoid ambiguous TTS words: "lead" (metal) and mangled "Jeremy".
SCENES = [
    ("s0", "Your phone can book while you work. An AI receptionist answers, checks real availability, and books the appointment — or takes their info for a call back when you're full."),
    ("s1", "Those calls die when you're mid-service, after hours, or booked out. Voicemail doesn't put them on the calendar."),
    ("s2", "The agent answers with your approved greeting. This clip uses a fictional demo salon from Unloved Productions."),
    ("s3", "It asks only the intake questions you approve — pet details, contact info, and the service they want."),
    ("s4", "Then it checks real calendar availability and offers open times. It does not invent slots."),
    ("s5", "When the caller confirms, it books the appointment. They hear the confirmation. You see it on the calendar."),
    ("s6", "If you're full, it captures their contact for a call back instead of inventing an opening."),
    ("s7", "Next step: a twenty-minute setup visit. We map your phone flow and calendar, then run a paid pilot. Call Unloved Productions at six six one, seven six eight, eight five four five."),
]

# Target ~90s; holds expand automatically to speech + 0.45s.
HOLD = {
    "s0": 11.5,
    "s1": 10.0,
    "s2": 11.0,
    "s3": 11.0,
    "s4": 11.5,
    "s5": 12.0,
    "s6": 9.5,
    "s7": 14.5,
}


def run(cmd: list[str], **kw) -> None:
    print("+", " ".join(str(c) for c in cmd[:10]), "..." if len(cmd) > 10 else "")
    subprocess.check_call(cmd, **kw)


def duration(path: Path) -> float:
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


async def _synth_edge(text: str, mp3: Path) -> None:
    import edge_tts

    communicate = edge_tts.Communicate(text, VOICE, rate=RATE)
    await communicate.save(str(mp3))


def _synth_gtts(text: str, mp3: Path) -> None:
    from gtts import gTTS

    gTTS(text, lang="en").save(str(mp3))


async def synth() -> list[dict]:
    AUDIO.mkdir(parents=True, exist_ok=True)
    manifest = []
    engine = "edge-tts"
    for sid, text in SCENES:
        mp3 = AUDIO / f"{sid}.mp3"
        wav = AUDIO / f"{sid}.wav"
        try:
            if engine == "edge-tts":
                await _synth_edge(text, mp3)
            else:
                _synth_gtts(text, mp3)
        except Exception as exc:
            print(f"edge-tts failed ({exc}); falling back to gTTS")
            engine = "gtts"
            _synth_gtts(text, mp3)
        run(
            ["ffmpeg", "-y", "-i", str(mp3), "-ar", "48000", "-ac", "1", str(wav)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        speech = duration(wav)
        hold = max(HOLD[sid], speech + 0.45)
        manifest.append(
            {
                "id": sid,
                "audio": str(wav),
                "speech_s": speech,
                "duration_s": hold,
                "text": text,
                "engine": engine,
            }
        )
        print(f"{sid}: speech={speech:.2f}s hold={hold:.2f}s ({engine})")
    (WORK / "timeline.json").write_text(json.dumps({"scenes": manifest}, indent=2))
    return manifest


def build_vo(manifest: list[dict]) -> tuple[Path, float]:
    parts = AUDIO / "parts"
    parts.mkdir(parents=True, exist_ok=True)
    lines = []
    total = 0.0
    for i, scene in enumerate(manifest):
        src = Path(scene["audio"])
        hold = scene["duration_s"]
        speech = scene["speech_s"]
        pad = max(0.0, hold - speech)
        part = parts / f"{i:02d}.wav"
        if pad > 0.05:
            run(
                [
                    "ffmpeg", "-y", "-i", str(src),
                    "-af", f"apad=pad_dur={pad:.3f}",
                    "-t", f"{hold:.3f}",
                    str(part),
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        else:
            run(
                ["ffmpeg", "-y", "-i", str(src), "-t", f"{hold:.3f}", str(part)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        lines.append(f"file '{part.name}'")
        total += hold
    concat = parts / "concat.txt"
    concat.write_text("\n".join(lines) + "\n")
    raw = AUDIO / "vo-raw.wav"
    vo = AUDIO / "vo.wav"
    run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat), "-c:a", "pcm_s16le", str(raw)],
        cwd=str(parts),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    run(
        ["ffmpeg", "-y", "-i", str(raw), "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", str(vo)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return vo, total


def make_bed(dur: float, out: Path) -> Path:
    run(
        [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", f"sine=frequency=220:sample_rate=48000:duration={dur:.3f}",
            "-f", "lavfi", "-i", f"sine=frequency=330:sample_rate=48000:duration={dur:.3f}",
            "-filter_complex",
            f"[0][1]amix=inputs=2:duration=longest,volume=0.03,afade=t=in:st=0:d=1.5,afade=t=out:st={max(0.1, dur - 1.5):.3f}:d=1.5",
            "-ar", "48000", "-ac", "2",
            str(out),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return out


def patch_html_durations(manifest: list[dict]) -> Path:
    import re

    html = (ROOT / "voice-agent-90s.html").read_text()
    caps = {
        "s0": "Your phone can book while you work.",
        "s1": "Busy, closed, or booked out — those calls often hit voicemail.",
        "s2": "The AI receptionist answers with your approved greeting.",
        "s3": "It asks only the intake questions you approve.",
        "s4": "It checks real calendar availability — not invented times.",
        "s5": "With approval, it books the appointment on your calendar.",
        "s6": "If you’re full, it captures a lead for callback.",
        "s7": "Watch the clip. Then book a 20-minute setup visit.",
    }
    lines = ["  const scenes = ["]
    for scene in manifest:
        sid = scene["id"]
        lines.append(
            f'    {{ id: "{sid}", dur: {scene["duration_s"]:.3f}, cap: "{caps[sid]}" }},'
        )
    lines.append("  ];")
    block = "\n".join(lines)
    html2 = re.sub(r"  const scenes = \[[\s\S]*?\];", block, html, count=1)
    out = WORK / "voice-agent-90s.timed.html"
    out.write_text(html2)
    return out


async def record(html: Path, total: float, webm: Path) -> None:
    from playwright.async_api import async_playwright

    chrome = Path("/home/unloved/.local/bin/chromium")
    webm.parent.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path=str(chrome) if chrome.exists() else None,
            headless=True,
            args=["--disable-dev-shm-usage", "--no-sandbox"],
        )
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            record_video_dir=str(webm.parent),
            record_video_size={"width": 1920, "height": 1080},
        )
        page = await context.new_page()
        await page.goto(html.as_uri(), wait_until="networkidle")
        await page.wait_for_function("() => window.__demo && window.__demo.total")
        await page.evaluate("() => window.__demo.start()")
        await page.wait_for_timeout(int((total + 1.0) * 1000))
        video = page.video
        await page.close()
        await context.close()
        await browser.close()
        if not video:
            raise RuntimeError("No playwright video recorded")
        path = await video.path()
        Path(path).replace(webm)
        print(f"recorded {webm}")


def mux(webm: Path, vo: Path, bed: Path, mp4: Path, total: float) -> None:
    OUT_VIDEOS.mkdir(parents=True, exist_ok=True)
    run(
        [
            "ffmpeg", "-y",
            "-i", str(webm),
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
            "-t", f"{total:.3f}",
            "-movflags", "+faststart",
            str(mp4),
        ],
    )


async def main() -> None:
    WORK.mkdir(parents=True, exist_ok=True)
    manifest = await synth()
    vo, total = build_vo(manifest)
    print(f"total timeline {total:.2f}s")
    bed = make_bed(total, AUDIO / "bed.wav")
    html = patch_html_durations(manifest)
    webm = WORK / "capture.webm"
    await record(html, total, webm)
    mp4 = OUT_VIDEOS / "voice-agent-90s.mp4"
    mux(webm, vo, bed, mp4, total)
    print(f"DONE {mp4} ({duration(mp4):.2f}s)")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as exc:
        print(f"FAILED: {exc}", file=sys.stderr)
        raise
