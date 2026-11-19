# Sales assets — voice agent (no live demo)

| Asset | Path | Use |
|---|---|---|
| **One-pager** | `one-pager.html` | Print Letter / PDF; leave on counter |
| **90s clip** | `videos/voice-agent-90s.mp4` | Text/MMS/email after the call |
| Rebuild video | `video/build_90s.py` | Uses gTTS (edge-tts fallback if available) + Playwright + ffmpeg |

## How to use

1. Print `one-pager.html` (browser → Print → Letter, no margins extras).
2. After the conversation, text or AirDrop `voice-agent-90s.mp4`.
3. Close on a **20-minute setup visit** — not a live Retell session.

## Claims on the clip

- On-screen: `Demo · Simulated salon`
- VO: fictional Taft Grooming Demo; booking tools are real
- End card: not ads, not customer forecasts, not emergency dispatch

## Rebuild

```bash
cd "booking agents/demo agent/research/local-market-intelligence/sales-assets/video"
# Prefer the existing work venv that has playwright + gTTS
/home/unloved/local-bussinesses/output/work/.venv/bin/python build_90s.py
```

Work intermediates stay in `video/work/` (gitignored).
