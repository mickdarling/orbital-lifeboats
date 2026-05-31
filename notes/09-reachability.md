# 09 — Time-vs-Δv reachability (and how it rewrites everything)

Backed by `reachability.py` (run it). This is the note that changes the rest of
the design, because it adds the axis the first eight notes were missing: **time.**

## The core finding: rescue has two budgets, and the clock binds first

A rescue only happens if it satisfies **both**:
1. **Δv** — can the mover afford the velocity change?
2. **Time** — does it finish before the life-support clock runs out?

And the cruel coupling: **the cheap maneuvers are the slow ones.** Drifting and
phasing cost almost nothing but take many orbits; arriving fast means a high-
energy transfer whose Δv explodes. So a buoy can be comfortably within Δv reach
and still be **useless to a crew on a short clock.** Δv alone — the metric the
whole repo used through note 08 — is the wrong question. The right question is
*"reachable before the air runs out?"*

## What the model shows (LEO, validated against Hohmann)

**Co-orbital phasing** (a buoy sharing the victim's orbit — the safe-haven /
breadcrumb case). The Δv to close a phase gap drops the more orbits you allow:

| Gap | rescue in 6 h (suit clock) | rescue in 48 h |
|-----|----------------------------|----------------|
| 15° | yes, 72–222 m/s | trivially |
| 40° | yes, 146–301 m/s | yes, down to ~50 m/s |
| 120° | **NO** — in-time options all exceed 400 m/s | yes |
| 180° | NO | yes, ~220–390 m/s |

Time literally buys angular reach. With a 400 m/s chemical responder, a 6-hour
clock covers ~100° of co-orbital arc; a 48-hour clock covers the whole orbit.

**Cross-orbit transfer** (buoy on a *different* orbit). There's a Δv floor (the
min-energy Hohmann, ~318 m/s for a 600 km gap) and arriving faster than its
~0.8 h transfer time costs Δv steeply — **6× the floor to halve the time, 40× to
quarter it.** A different-orbit buoy is a luxury rescue: fine on a long clock,
hopeless on a short one. *Co-orbital is the only thing that works under pressure.*

## The two findings that reshape the architecture

### 1. The phasing time floor is one orbital period — and it explodes with altitude

You cannot phase faster than ~1 revolution. So the **orbital period is a hard
floor** on co-orbital rescue time, and it scales viciously:

| Orbit | Period | Short clock (~6 h) co-orbital rescue? |
|-------|--------|---------------------------------------|
| LEO | ~1.5 h | yes — a few revs fit |
| GEO | ~24 h | **no** — <1 rev fits |
| NRHO | ~6.5 days | **no** — one rev dwarfs any short clock |

**Consequence:** in deep cislunar space (NRHO) and at GEO, a buoy merely "nearby
in the orbit" cannot phase in time for a short-clock emergency. Short-clock
survival there requires a lifeboat **docked to or formation-flying with the
crewed asset** — zero initial separation, zero phasing. The standing network can
only cover the *long-clock* failure modes that far out; the *fast* failure modes
must be handled by a lifeboat that's already right there. (This pulls the concept
back toward "every station/ship carries or is shadowed by its own lifeboat" — see
the failure-mode mapping below.)

### 2. Ion cannot first-respond — the fleet splits in two

An electric tug delivers Δv far too slowly for an emergency: even a generous
0.5 mm/s² gives **~2.3 days to produce 100 m/s, ~23 days for 1 km/s.** Useless
against an hours-to-days clock. So propulsion bifurcates the fleet by role:

| Role | Propulsion | Where it sits | Job |
|------|-----------|---------------|-----|
| **First responder** | **chemical** (fast, impulsive) | pre-staged *close* to crewed traffic, co-orbital | make the actual rescue burn within the clock |
| **Reserve / repositioner** | **ion** (slow, efficient) | stable parking (DRO, L4/5) | refill responders, redistribute the fleet *between* emergencies |

Ion never makes the rescue burn. It moves the chess pieces while no one's dying.

## How this revises notes 06–08

- **Note 06 (failure modes) gains a clock column.** What matters now is each
  mode's *time budget*, because that decides whether any buoy is reachable:

  | Failure mode | Clock | Implication |
  |--------------|-------|-------------|
  | Hull breach (suits), fire, contamination → must evacuate | **hours** | Hardest. Needs a chemical responder co-orbital and *close*, or a docked lifeboat. Drives the whole density requirement. |
  | Acute medical, CO₂/thermal/power degradation | hours–~day | Moderate proximity; chemical. |
  | Consumables overrun, missed window, off-nominal trajectory | days–weeks | Easy. Cross-orbit OK, ion OK, sparse network fine. |
  | Stuck, no way down | days–weeks (consumables-limited) | Long clock, but needs the *reentry-capable* variant (`07`). |

  The **shortest clock you choose to insure against sets the entire network
  density.** Insure against suit-breach (hours) and you need dense, chemical,
  co-orbital responders; insure only against consumables overrun (weeks) and a
  sparse ion-served network suffices. That's the master design dial.

- **Note 08 (placement) gets tighter and cheaper-than-feared at LEO.** Coverage
  isn't "which orbits" — it's *phase spacing on each crewed orbit.* The good
  news: at LEO the count per orbit is small (≈2 co-orbital responders with a
  400 m/s budget cover a 6 h clock across the whole ring; see `reachability.py`
  §4). The cost driver is **replication per crewed plane** (plane changes remain
  unaffordable, note 02) plus the high-orbit formation-flying requirement — not a
  dense grid. So: a couple of chemical responders co-orbital on each *crewed*
  plane (ISS/Tiangong/commercial-station inclinations, the active lunar corridor),
  docked/formation lifeboats at NRHO and GEO, and an ion-served DRO reserve behind
  it all.

- **Note 07 (the unit) keeps both engines, with clarified roles.** Chemical for
  the rescue burn, ion for self-repositioning — and the reachability math is *why*
  it needs both, not just nice-to-have. It also strengthens the "dormant, pre-
  staged" logic: responders must already be on station, close, and awake enough to
  move within minutes, because there's no time to ferry one in.

## The one-sentence rewrite

> The design is no longer "scatter caches where the Δv is cheap"; it's **"pre-
> stage fast (chemical) responders within one-or-two orbital periods of where
> crews actually are, sized by the shortest life-support clock you're insuring
> against, and use slow (ion) reserve buoys to keep them topped up and
> redistributed."**

## Model limits (honesty)
- Two-body, planar, impulsive, Earth-centric. LEO/MEO/GEO geometries are sound;
  **NRHO and EM-Lagrange cases are three-body** and only reasoned about
  qualitatively (the period-floor argument carries, the exact Δv numbers don't).
- Single-revolution Lambert for cross-orbit; multi-rev solutions exist but don't
  change the conclusion (cross-orbit is the luxury case).
- No plane-change cost included in the rescue itself (we assume co-planar). Out-
  of-plane victims are simply unreachable on a short clock — which only reinforces
  "one responder set *per crewed plane*."
- Phasing model assumes rendezvous back at the maneuver point; real ops would
  optimize further, making it somewhat *cheaper* than shown. The conclusions are
  conservative.

## Next builds this points to
- A 3-body reachability pass for NRHO/EML using a CR3BP propagator (to put real
  numbers on the "formation-fly your lifeboat" claim).
- A Monte-Carlo: traffic model × failure-mode/clock distribution → P(rescued)
  vs. fleet size and placement. That's the number that sizes the program.
