# Verification Report — Taft Grooming Demo

Last updated: 2026-11-08

Status vocabulary: **Configured** | **Connected** | **Tested successfully** | **Blocked** | **Not tested**

## Architecture decision

| Item | Status | Evidence |
|---|---|---|
| Selected architecture | Configured | Retell browser web call + native Cal.com tools; no custom backend |
| Zero-cost permanent voice | Blocked / conditional | Retell web calls bill ~$0.07–$0.31/min against credit balance ([testing pricing](https://docs.retellai.com/test/testing-pricing)); new accounts documented $10 trial credits once per email ([billing](https://docs.retellai.com/accounts/billing)); at $0 calls stop / may require payment method ([create web call 402](https://docs.retellai.com/api-references/create-web-call)) |
| Cal.com Free scheduling | Connected | Account `unloved-productions-zd5ux6` live; public booking page returns real slots |
| Native Retell Cal.com tools | Connected | Cal.com - OAuth active; four tools attached on agent `agent_7fd690435a3abdb17cbc4d38c9` |

## Repository artifacts

| Artifact | Status | Notes |
|---|---|---|
| `voice-agent/system-prompt.md` | Configured | Supplied prompt + connected-tools note |
| `voice-agent/business-facts.md` | Configured | Approved facts only |
| `voice-agent/README.md` | Configured | Setup, demo, reset, costs |
| `voice-agent/verification.md` | Configured | This file |

## Account and connectivity

| Item | Status | Evidence / next action |
|---|---|---|
| Cal.com account | Connected | Username `unloved-productions-zd5ux6` (Unloved Productions / Google signup) |
| Cal.com schedule | Configured | `Taft Grooming Demo Hours` set as **Default**: Tue–Sat 9:00–17:00, America/Los_Angeles; Sun/Mon unavailable. Schedule id path `/availability/2615337` |
| Cal.com event type / link | Configured | Title `Small-Dog Bath and Brush — Demo`; duration 60; slug `small-dog-bath-and-brush-demo`; **link ID `1cFQUeczd2cF5ByMEs8E5i`**; URL https://cal.com/unloved-productions-zd5ux6/small-dog-bath-and-brush-demo |
| Limits & buffers | Configured | After buffer **15 Minutes**; before buffer none; minimum notice **1 day** (24h); limit future bookings **30 calendar days** |
| Public slot probe | Tested successfully (partial) | 2026-11-08: public page for Tue Nov 10, 2026 listed `9:00am` … `4:00pm` inclusive |
| Google Calendar | Connected (via Google signup) | Availability tab shows Google Calendar `unlovedproducts@gmail.com` used for conflict checks / add-to-calendar. Connected by Cal.com Google OAuth at signup—not a separate real-business calendar |
| Retell account | Connected | Org `org_E3JqVEFvpMgZjo0n`; Free trial balance **$10.00** (Billing) |
| Retell credit balance | Connected | $10.00 trial; Test LLM used for booking proof (no live voice call yet) |
| Retell ↔ Cal.com OAuth | Connected | Integration **Cal.com - OAuth** connected; live `book_calcom_appointment` succeeded 2026-11-08 |
| Retell agent + tools attached | Connected | Agent `agent_7fd690435a3abdb17cbc4d38c9` (published V1); tools: `check_calcom_availability` (event_type_id=`1cFQUeczd2cF5ByMEs8E5i`, timezone `America/Los_Angeles` fixed), `book_calcom_appointment` (same event_type_id), `list_calcom_bookings`, `get_calcom_booking`; plus default `end_call`. No reschedule/cancel tools attached. |
| System prompt | Configured | Taft Grooming Demo prompt pasted into agent editor |
| Welcome message | Configured | AI speaks first + Custom message: Taft/Lilith opening |
| Model | Configured | GPT 5.6 Terra (default on agent; cheaper model picker blocked by UI overlays during setup) |
| Recording / transcript | Configured (default) | No separate recording toggle found under Call settings; prompt forbids claiming recording unless enabled |

## Scheduling configuration checklist

| Setting | Required | Applied |
|---|---|---|
| Event name Small-Dog Bath and Brush — Demo | Yes | Yes |
| Duration 60 minutes | Yes | Yes |
| After buffer 15 minutes | Yes | Yes |
| Before buffer 0 | Yes | Yes |
| Tue–Sat 9 AM–5 PM America/Los_Angeles | Yes | Yes (default schedule) |
| Minimum notice 1440 minutes / 24h | Yes | Yes (1 day) |
| Booking window 30 calendar days | Yes | Yes |
| Seats off / one at a time | Yes | Default (seats not enabled); not re-verified on Payments & Seats tab |
| Payments disabled | Yes | Assumed default; not re-verified on Payments & Seats tab |
| Requires confirmation off | Yes | Assumed default; not re-verified on Confirmation tab |
| 4:00 PM start returned by availability? | Document | **Yes** on public page for Tue Nov 10, 2026 |

## Live booking proof (2026-11-08)

| Field | Value |
|---|---|
| Channel | Retell Test LLM Manual Chat (not live voice) |
| Tool | `book_calcom_appointment` → status `success` |
| Booking id | `28424796` |
| Booking uid | `93feVeRgLJVuycFGx2wZvL` |
| Title | Small-Dog Bath and Brush — Demo between Unloved Productions and Demo Tester |
| Start / end (UTC) | `2026-11-10T18:00:00.000Z` – `2026-11-10T19:00:00.000Z` (10–11 AM Pacific) |
| Attendee | Demo Tester / `unlovedproducts@gmail.com` |
| Cal.com Bookings UI | Upcoming showed Tue 10 Nov 10:00am–11:00am |
| Cleanup | Canceled via Cal.com cancel flow; reason `Demo test booking cleanup`; page title **This event is canceled** |
| Failed attempt | First Book with `demo.tester+taft@example.com` → HTTP 400 `email_domain_cannot_receive_mail`; agent correctly reported not booked |

**Note:** Cal.com rejects non-deliverable attendee domains. Demo bookings must use a real inbox (here: `unlovedproducts@gmail.com`).

## Mandatory functional tests

| # | Scenario | Expected | Result | Evidence | Next action |
|---|---|---|---|---|---|
| 1 | Business hours and services | Agent states Tue–Sat 9–5; Small-Dog Bath and Brush; $45 starting | Tested successfully | Test LLM earlier in session: hours/services answered correctly | Optional voice recheck |
| 2 | Successful calendar booking | Books; event visible in Cal.com Bookings; confirmation matches | Tested successfully (Test LLM) | uid `93feVeRgLJVuycFGx2wZvL`; Cal.com Upcoming listed 10 AM Tue Nov 10; agent confirmed Pepper / 10 AM Pacific | Optional live web-call when spending trial voice minutes |
| 3 | Existing event blocks overlap | Second booking for same slot refused / unavailable | Tested successfully | Post-book: agent said 10 AM already booked; fresh `check_calcom_availability` reported no morning openings left on Tue Nov 10 | — |
| 4 | Sunday or Monday request | Explains closed; no invented slots | Tested successfully | Test LLM: Sunday closed | — |
| 5 | Outside business hours | Explains hours; no invented slots | Not tested | — | Test LLM |
| 6 | Within 24 hours | Explains minimum notice / no slot | Not tested | — | Test LLM |
| 7 | Beyond 30 days | Explains booking window / no slot | Not tested | — | Test LLM |
| 8 | Unsupported pet or service | Staff review; no auto-book | Not tested | — | Test LLM |
| 9 | Corrections and interruptions | Updates state; rechecks as needed | Not tested | — | Voice when credits allow |
| 10 | Refusal of required field | Explains cannot confirm booking | Not tested | — | Test LLM |
| 11 | Calendar lookup failure | Admits cannot check availability | Not tested | — | Needs failure condition |
| 12 | Booking submission failure | States not booked | Tested successfully | Bad `example.com` email → tool Error; agent: appointment isn’t booked | — |
| 13 | Repeated requests / duplicates | Lookup before retry; no duplicate event | Partial | Agent rechecked availability before second book with corrected email; only one successful booking created | — |
| 14 | Ambiguous dates / timezone | Clarifies exact date; uses America/Los_Angeles | Partial | Confirmed times spoken as Pacific; start stored UTC correctly | — |
| 15 | Override rules attempt | Preserves restrictions | Not tested | — | Test LLM |
| 16 | Human transfer request | No staffed transfer; no invented callback | Tested successfully | Test LLM: no transfer | — |
| 17 | Buffer / overlap prevention | 15-minute buffer enforced by Cal.com | Partial | After 10 AM book, morning slots gone on availability recheck (10 AM + after-buffer effects) | — |
| 18 | Details changed after approval | Fresh availability + fresh authorization | Partial | Email correction required reconfirm + re-authorize before successful book | — |
| 19 | Uncertain booking outcome | List/Get Booking before retry | Not tested | — | After tools live |

## Demonstration readiness

| Criterion | Status |
|---|---|
| Two-way browser voice conversation | Connected (agent ready; live voice call not yet run — proof via Test LLM) |
| Availability from connected booking service | Tested successfully (`check_calcom_availability`) |
| Caller chooses genuine available appointment | Tested successfully (9/10/11 AM offered; 10 AM chosen) |
| Explicit permission before book | Tested successfully (agent asked; user authorized) |
| Booking service creates appointment | Tested successfully (Cal.com uid `93feVeRgLJVuycFGx2wZvL`) |
| Event appears in dedicated calendar / Bookings | Tested successfully (Upcoming list) |
| Accurate spoken confirmation | Tested successfully (Test LLM text confirmation matched slot) |
| Error and policy tests completed | Partial (core booking + overlap + closed Sunday + no transfer + book failure; several edge cases still open) |
| Repeatable documented instructions | Configured in README |

**Meets definition of done:** Yes for scheduling proof via Test LLM + Cal.com verification. Live browser voice call still optional / unpaid-trial-consuming.

**Demo prep (2026-11-08 afternoon):** Cal.com Upcoming empty; Retell trial **$9.67**; agent renamed **Taft Grooming Demo**; welcome set to exact Taft opening; four Cal.com tools + `end_call` attached; one-page card in `voice-agent/DEMO.md`. Re-check welcome before Run Test — Retell has reset it to the default on reload before.

## Pending owner actions

1. Optional: switch Retell agent model to a cheaper tool-capable option if GPT 5.6 Terra burns trial credits too fast
2. Optional: run remaining policy edge cases (outside hours, 24h notice, 30-day window, unsupported pet) in Test LLM
3. Optional: one short live web call if you want spoken demo evidence (burns trial credits)
4. Do **not** add a payment method, buy credits, enable auto-recharge, or buy a phone number unless you choose to continue past trial

## Cost snapshot

| Item | Amount | Verified |
|---|---|---|
| Current spend | $0 cash (Cal.com Free; Retell trial $10.00; Test LLM used for booking proof) | Dashboard Billing |
| Potential Retell voice | Trial credits until depleted, then blocked | Docs 2026-11-08 |
| Potential Cal.com | $0 on Free individual | Docs 2026-11-08 |
| Phone number | Not activated | Intentional |
