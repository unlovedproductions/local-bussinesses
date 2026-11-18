# Client Implementation Guide (Retell + Cal.com)

## Prerequisites

- Retell account
- Cal.com account (`.com` vs `.eu` per voice-agent docs)
- Approved business facts
- Human owner for go-live

## Steps

1. Create Cal.com schedule + event type using the pattern in `voice-agent/README.md` (adapt hours/services; do not copy Taft demo prices blindly).
2. Create Retell single-prompt agent; paste adapted system prompt.
3. Connect Cal.com tools: Check Availability, Book Appointment, List/Get Booking.
4. Test web call end-to-end; record evidence.
5. Optional PSTN: configure numbers; treat as separate verification.
6. QA: point auditor at agent IDs with fail-closed gates.
7. Acceptance + handoff.

## Failure handling

- Tool misconfig → fix in Retell dashboard; retest.
- Calendar conflicts → verify buffers/timezone.
- Blocked QA → do not fabricate PASS.
