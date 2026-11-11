# Calendar Sandbox (Cal.com)

Discovered provider: **Cal.com** (not Google Calendar directly).

Event type (demo): numeric `7825232` / slug id `1cFQUeczd2cF5ByMEs8E5i` / slug `small-dog-bath-and-brush-demo`  
Account: `unloved-productions-zd5ux6`

## Isolation requirements
1. Confirm bookings land only on the demo event type / sandbox calendar.
2. Set `CALCOM_API_KEY`, `CALCOM_EVENT_TYPE_ID=7825232`, `CALCOM_SANDBOX_CALENDAR_ID`.
3. Complete `config/sandbox_proof.json` with all `proof_checks=true` and `approved=true`.
4. Set `ALLOW_SANDBOX_WRITES=YES` only after proof.

## Verification
Before/after snapshots via Cal.com `GET /v2/bookings` and `GET /v2/bookings/{uid}`.

Use `cal-api-version: 2024-08-13` for bookings. Event-type GETs need `2024-06-14` or `2026-06-12`. Clients need a non-empty `User-Agent` (Cloudflare 1010 otherwise).

Spoken confirmation is insufficient.

## Notes
- Cal.com rejects non-deliverable attendee emails (e.g. example.com).
- Demo receptionist has no cancel/reschedule Retell tools attached; D05/D06/J07 should expect honest limitation unless staging tools are added.
