# Taft Grooming Demo — AI Voice Booking

Browser voice booking demonstration for **Unloved Productions**.

Architecture: **Retell AI** (browser web call) + **Cal.com** (real availability and booking). No custom backend, no phone number, no paid subscriptions.

Status words used in this project:

- **Configured** — settings or files applied; end-to-end not verified
- **Connected** — account or integration authenticated and connectivity check succeeded
- **Tested successfully** — functional test passed with evidence
- **Blocked** — concrete dependency prevents progress

See [verification.md](verification.md) for current evidence. This README is not proof that the live demo works.

## Architecture

```text
Browser caller
  → Retell dashboard web call (single-prompt agent)
    → Check Availability (Cal.com)
    → Book Appointment (Cal.com)
    → List Bookings / Get Booking (reconcile uncertain results)
      → Cal.com event type + demo bookings / calendar
```

Tools intentionally **not** attached: Reschedule Booking, Cancel Booking.

Reset path: cancel fictional test bookings manually in Cal.com → Bookings.

## Repository files

| File | Purpose |
|---|---|
| [system-prompt.md](system-prompt.md) | Paste into the Retell agent prompt |
| [business-facts.md](business-facts.md) | Approved business facts and policies |
| [verification.md](verification.md) | Test evidence and blockers |
| [DEMO.md](DEMO.md) | One-page live demo card (talk track + links) |
| [README.md](README.md) | Setup and demo instructions |

No application source code is required for the native Retell + Cal.com path.

## Cal.com event configuration

Create these settings on a free `cal.com` account (not `cal.eu`).

### Schedule

| Setting | Value |
|---|---|
| Name | Taft Grooming Demo Hours |
| Timezone | America/Los_Angeles |
| Availability | Tuesday–Saturday, 09:00–17:00 |
| Closed | Sunday, Monday |

### Event type / link

| Setting | Value |
|---|---|
| Title | Small-Dog Bath and Brush — Demo |
| Duration | 60 minutes |
| After-event buffer | 15 minutes |
| Before-event buffer | 0 minutes |
| Schedule | Taft Grooming Demo Hours |
| Minimum notice | 1440 minutes (24 hours) |
| Booking window | 30 calendar days |
| Seats | Off (one booking occupies the slot) |
| Payments / deposits | Disabled |
| Requires confirmation | Off |
| Price in Cal.com | $0 (spoken demo price remains $45; staff confirms final price) |

### Buffer vs end of day

A 4:00 PM start ends at 5:00 PM; the 15-minute buffer runs to 5:15 PM. Only advertise times that **Check Availability** actually returns. Record whether 4:00 PM appears in [verification.md](verification.md).

### Calendar destination

Use the dedicated Cal.com demo bookings for this event type. Do not connect a personal or real-business calendar unless a later conflict test proves Cal.com alone cannot block overlapping bookings, and you approve that connection.

### Attendee email

Cal.com booking requires attendee email. Collect a real inbox you control during tests. Never invent an address.

## Retell agent configuration

1. Create a **Single prompt** agent.
2. Paste the full contents of [system-prompt.md](system-prompt.md).
3. Voice: Retell platform voice (avoid ElevenLabs while on trial credits).
4. LLM: cheapest model that reliably calls tools.
5. Recording / transcript retention: leave off until privacy settings are reviewed and approved.
6. Connect Cal.com under **Integrations** (prefer OAuth, domain `Cal.com`).
7. Attach these tools with timezone `America/Los_Angeles` and the event link ID / event type ID:

| Tool | Purpose |
|---|---|
| Check Availability | Live open slots |
| Book Appointment | Create booking after explicit approval |
| List Bookings | Reconcile by attendee email |
| Get Booking | Reconcile by booking UID |

Configure tool inputs with **Description** (filled from conversation), not fixed Values, for caller name, email, phone, time, and notes.

### Duplicate prevention

Cal.com create-booking has no idempotency key. Safeguard:

1. Do not retry Book Appointment while waiting.
2. On uncertain result, List Bookings / Get Booking first.
3. On HTTP 409, run Check Availability again and offer a new slot.

## Account setup (one step at a time)

### 1. Cal.com account

1. Open https://cal.com/signup
2. Create a free individual account on `cal.com`
3. Report only your public username (no passwords or API keys in chat)

### 2. Schedule and event type — DONE (2026-11-08)

Configured on account `unloved-productions-zd5ux6`:

| Item | Value |
|---|---|
| Schedule | Taft Grooming Demo Hours (Default), Tue–Sat 9:00–17:00 America/Los_Angeles |
| Event | Small-Dog Bath and Brush — Demo |
| Link ID | `1cFQUeczd2cF5ByMEs8E5i` |
| Public URL | https://cal.com/unloved-productions-zd5ux6/small-dog-bath-and-brush-demo |
| After buffer | 15 minutes |
| Minimum notice | 1 day |
| Booking window | 30 calendar days |

Paste link ID `1cFQUeczd2cF5ByMEs8E5i` into Retell Cal.com tools.

### 3. Retell account

1. Open https://dashboard.retellai.com
2. Sign up
3. Do **not** add a payment method, buy credits, enable auto-recharge, or buy a phone number
4. Open Billing and report whether a credit balance is visible (amount if shown)

### 4. Connect Cal.com to Retell

1. Retell → Integrations → Cal.com → Connect
2. Prefer OAuth with domain `Cal.com`
3. If OAuth cannot book and Settings → Developer → API keys exists on Cal.com, create a key, paste it only into Retell’s connection dialog, then continue
4. Never paste secrets into Cursor chat

### 5. Create the agent

1. Agents → Create → Single prompt
2. Paste [system-prompt.md](system-prompt.md)
3. Attach the four tools with the event type ID and `America/Los_Angeles`
4. Save

## Launch the browser demo

Use the one-page card: [DEMO.md](DEMO.md).

1. Open the Retell agent (link in DEMO.md)
2. Confirm Billing still has credits
3. Click **Test** / **Run Test** for a web call
4. Allow microphone access
5. Speak with the agent
6. Verify the booking on Cal.com → Bookings

## Successful booking demonstration (~90 seconds target)

Use fictional details and an inbox you control.

1. Agent opens with the exact Taft Grooming Demo greeting
2. Caller asks for a small-dog bath and brush
3. Caller gives pet under 25 lb, no special handling / severe matting
4. Caller provides name, callback number, email, pet details, preferred day
5. Agent checks live availability and offers real slots
6. Caller chooses a slot
7. Agent reads back details and asks for booking permission
8. Caller says yes
9. Agent books and confirms only after tool success
10. Verify the appointment on Cal.com → Bookings

Do not hardcode successful dates.

## Unavailable appointment demonstration

1. Book or occupy a known slot first (or request a closed day / too-soon time)
2. Ask the agent for that unavailable time
3. Confirm the agent refuses invented slots and offers real alternatives or explains policy

## Reset

1. Cal.com → Bookings
2. Cancel only fictional test appointments created for this demo
3. Do not delete unrelated calendar entries
4. Confirm Check Availability returns the freed slot before the next demo

## Costs (verified 2026-11-08)

| Item | Cost | Notes |
|---|---|---|
| Cal.com Free | $0 | Individual scheduling |
| Retell signup trial credits | $10 once per email (documented) | Not guaranteed if email already used |
| Retell web call | ~$0.07–$0.31 / minute against credits | No telephony on web calls |
| Retell phone number | $2 / month + card required | Out of scope |
| Custom backend / hosting | $0 | Not used |

When credits hit $0, calls stop. Do not add a card without explicit approval.

Sources:

- https://docs.retellai.com/test/testing-pricing
- https://docs.retellai.com/accounts/billing
- https://cal.com/pricing

## Known limitations

- Voice testing spends Retell credits; permanently free unlimited voice is not verified
- Hosted Cal.com API entitlement for free accounts may differ from OAuth; OAuth is preferred
- No phone inbound/outbound in version one
- No agent-side reschedule/cancel
- Duplicate prevention is lookup-before-retry, not provider idempotency keys
- Recording/transcript settings must stay off until approved
- Google Calendar is not connected by default

## Definition of done

The demonstration is ready only when a live browser conversation checks real availability, receives explicit approval, creates a Cal.com booking, and the spoken confirmation matches that booking. File presence alone is not completion.
