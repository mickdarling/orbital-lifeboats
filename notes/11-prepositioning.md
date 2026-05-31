# 11 — Event-driven pre-positioning & expendable stage-1s

The reachability math (note 09) said rescue is hard because the cheap maneuvers
are slow, so the responder has to already be *close*. This note is the answer to
*"how do you arrange to already be close?"* — and the answer turns on a fact we
haven't used yet:

> **Emergencies are unpredictable in time and place — but most crewed activity is
> scheduled, and a risky maneuver fails into a *predictable* set of states.**

So you don't have to blanket space and hope. You **pre-position** responders at
the specific places a planned, known-risky event could strand someone. That
converts an unpredictable rescue into a *scheduled rendezvous* — and defeats the
clock in advance, because the responder is co-located with where the casualty
will actually be.

## Two deployment regimes

The fleet works in two modes, drawing from the same stable reserve (DRO, L4/5):

1. **Standing coverage** — persistent stage-1s on crewed orbits / formation-flying
   with stations, for the *always-there* population and truly unscheduled failures.
   Reusable, station-kept. (This is notes 08–10.)
2. **Event-driven surge** — for a *scheduled* risky event (launch, TLI, orbit
   insertion, descent, a crewed transit window), ion-ferry stage-1s out of the
   reserve *ahead of time* and park them at the event's failure geometry. The lead
   time is days-to-months, so **ion is fine for the pre-positioning move** — only
   the rescue burn itself needs to be chemical/fast (note 09's fleet split still
   holds, just across time).

This mirrors how terrestrial emergency services pre-stage ambulances at a stadium
on game day rather than blanketing the whole city, and how WWII air-sea rescue
launches loitered offshore *during* a raid. You surge coverage to the known risk.

## The failure geometry: fore, aft, sides — and a no-burn guardian

"Where would a failure leave them?" has structure. For a planned burn, the
dispersion of outcomes maps to physical directions, so you bracket it:

- **Fore / aft (along-track)** — *energy / burn-magnitude* errors. An under-burn
  leaves you short and low (aft); an over-burn long and high (fore). Pre-place
  stage-1s ahead of and behind the nominal post-burn state.
- **Sides (cross-track)** — *pointing / plane* errors. A mis-aimed burn throws you
  out of plane. Lateral stage-1s cover that.
- **The no-burn guardian** — the discontinuous case. A *total* engine failure
  doesn't disperse you a little; it leaves you on your **original pre-burn
  trajectory**, which is somewhere else entirely. That needs its own responder
  pre-staged on the original path. (This is the free-return station — note 04 §E
  made the trajectory itself a lifeboat; here we add a hardware guardian to it.)

`reachability.py` §6 shows why this is so cheap for the common (dispersed) cases:
a stage-1 sitting on the nominal trajectory sees a dispersed casualty depart at
only **~the burn error** (tens of m/s), so their separation grows slowly — a
30 m/s dispersion is ~100 km after an hour, ~650 km after six. A co-located
stage-1 with a few tens-to-hundreds of m/s catches that trivially, far inside any
clock. **The proximity problem evaporates because you pre-arranged the proximity.**

## The highest-value targets: irreversible maneuvers

Pre-positioning pays most where (a) failure is *catastrophic* and (b) the off-
nominal state is *predictable*. That's exactly the **orbit-insertion / injection
burns**: miss the Mars or lunar orbit insertion and you fly past with no second
chance; under-burn TLI and you're on a decaying or stranded arc. These are the
moments crews are most exposed and the geometry is most knowable — so they're
where a pre-staged guardian (or a ring of them) earns its keep.

## Expendable stage-1s: safety apparatus you use up

The reframing inside the reframing: a pre-positioned stage-1 doesn't have to come
back. It's **consumable safety apparatus** — you spend it simply to *be available*
during a risky window. If the event goes nominally, the stage-1 may end up on a
trajectory you can't cheaply recover, and **that's an acceptable loss.** It was
insurance; the premium is one cheap, mass-produced module.

Why this is sound:
- **The economics are lopsided.** A stage-1 is the cheapest echelon (note 10);
  a crew + ship is not. Throwing away even several stage-1s per high-risk event is
  trivial insurance against losing the mission.
- **It removes the recovery constraint** that would otherwise force every
  responder onto a stable, returnable orbit. An expendable guardian can sit on a
  trajectory that's *perfect for the rescue geometry* but *terrible for its own
  survival* — e.g. one that would itself decay or escape — because it only has to
  exist for the hours/days of the risky window.
- **Recover opportunistically, never count on it.** If a spent guardian happens
  to end up somewhere an ion tug can fetch it later, great; design as if it won't.

## What it changes in the numbers

- **Standing coverage can be thinner than feared.** If most high-risk exposure is
  during *scheduled* events you can pre-position for, the persistent network only
  has to cover the steady-state population (stations) and the genuinely
  unscheduled. The surge handles the rest, on demand.
- **Reserve size is driven by event tempo, not by blanketing space.** You need
  enough reserve stage-1s (plus ion ferries) to surge the busiest overlapping set
  of scheduled events, plus a margin of expendables per event. That's a
  *scheduling/throughput* number, not a coverage-geometry number — and it's much
  smaller.
- **Production rate matters more than fleet size.** Because stage-1s are
  expendable and event-driven, the conveyor belt (note 07) feeds consumption. The
  question becomes "how many do we burn per year of operations," which the flight
  schedule sets directly.

## Open questions this adds
- **Dispersion sizing → guardian count.** How many stage-1s, and at what spacing
  along the dispersion ellipse, to cover a given burn's 3σ failure set? The natural
  calc: propagate the maneuver's covariance, tile it with stage-1 reach volumes.
- **Expendable vs. recoverable accounting.** At what unit cost does "throwaway per
  event" beat "fewer reusable guardians ion-ferried in and out"? There's a
  crossover set by unit cost, ferry cost, and event tempo.
- **Multiplexing guardians across events.** Can one pre-positioned ring cover
  several sequential missions through the same corridor before it's spent or
  recovered? Cislunar traffic is bursty around launch windows — worth exploiting.
