# 04 — Candidate architectures

Five ways to actually build survival redundancy into a spacefaring solar system,
roughly from "most like a Channel buoy" to "least." Most real systems would mix
them.

---

## A. Node depot (the true passive buoy)

**What:** A cache parked at a gravitationally distinguished, low-station-keeping
node — EML1, EML2/NRHO, GEO belt, low Mars orbit, Phobos.

**Why it works:** Traffic passes nearby at low relative velocity; reaching it is
a phasing/small-burn problem, not a plane change. Can be serviced and refilled on
a schedule.

**Holds:** Tier 1 survival kit always; storables for everyone; ZBO methalox where
solar power is strong (cislunar, Mars).

**Best for:** Cislunar (this decade) and planetary systems on arrival/departure.
**Weakness:** Only helps craft that are *near the node*. Useless mid-corridor.

---

## B. Breadcrumb convoy (the corridor solution)

**What:** For a planned crewed transfer, launch one or more **uncrewed cargo/
cache vehicles on the identical trajectory** in the same window — leading and/or
trailing the crew by hours-to-days of phase.

**Why it works:** The cache and the crew share a heliocentric orbit, so the
relative velocity is tiny and rendezvous is a cheap phasing maneuver (§3) even
for a half-dead ship. You turn the open-corridor problem into the node problem by
*co-flying* the lifeboat.

**Holds:** Whatever the mission's failure modes demand — propellant for an abort
burn, consumables to extend life support until the next window, spares.

**Best for:** Earth↔Mars crewed flights, any high-stakes single transfer.
**Weakness:** Per-mission cost; the convoy only protects *that* trajectory in
*that* window. It's insurance bought per-trip, not a standing network.

*This is probably the single most realistic near-term version of the idea:
"every crewed Mars ship flies with a dumb cargo twin a few hours behind it."*

---

## C. Cycler way-station

**What:** A large habitat/cache placed on a permanent cycling orbit that repeats
encounters with two bodies — the **Aldrin cycler** (Earth↔Mars) being the classic.

**Why it's seductive:** Built once, it passes Earth and Mars forever with no
propellant for the transfer itself. A standing waypoint with shelter and supplies.

**The catch:** It flies past each planet at a hyperbolic excess velocity of
**several km/s**. To board it you must *match that V∞* — a big burn, planned in
advance. So it is **not** an emergency float you drift onto; it's a scheduled
ferry you rendezvous with deliberately. Great as routine infrastructure, weak as
a contingency lifeboat (you can't catch the bus if you've already missed it).

**Best for:** Routine, high-cadence Earth–Mars traffic once it exists.
**Weakness:** Unforgiving boarding Δv; fixed schedule; no help to an off-nominal
ship that can't make the intercept.

---

## D. Rescue tug (the buoy that swims to you)

**What:** A fueled, powered, fast-reaction vehicle stationed at a node, that
*maneuvers out to intercept* a stricken ship and either tows it, refuels it, or
takes the crew aboard.

**Why it's the honest generalization:** It accepts that in open space the
immobile party is the *victim*, so the rescuer must be the mobile one — exactly
inverting the Channel picture. This is the orbital coast guard.

**Holds:** Lots of propellant (it must afford the intercept *and* the return),
grapple/docking gear, a crew transfer tunnel, medical.

**The Δv lives in the right place.** The crucial reason the active asset matters
isn't just mobility — it's that **the buoy is the thing that has the Δv, and the
crippled capsule is the thing that doesn't.** A bare-bones survival capsule, a
holed habitat, or a tank-dry transfer stage may have *zero* maneuvering
capability left. So you can't put the propulsion burden on the victim. The
network's job is to concentrate Δv (and the power, antennas, and brains to use
it) in the *rescuer*, precisely because the survivor has none. The capsule's only
job is to stay alive and be findable; everything that requires moving is the
buoy's job.

**It also has to be the one that calls for help.** Same logic applies to comms:
the stricken capsule may have lost its high-gain antenna, its power, or its
pointing. A standing buoy with a powered, always-on relay can (a) detect/receive
a weak distress squawk, (b) relay it across the network to wherever the rescue
Δv actually is, and (c) act as a navigation beacon the incoming rescuer homes on.
So the active "buoy" is really three things the victim can't be: the **mover**,
the **radio**, and the **beacon**. (This is why a passive-only network is
incomplete — see the layering note below.)

**Best for:** GEO belt (commercially real today — mission-extension vehicles),
cislunar space, anywhere with enough traffic to justify a standing asset.
**Weakness:** Expensive, must be kept fueled and ready, range-limited by its own
Δv budget. Can't save a ship it can't reach in time.

---

## E. Trajectory-as-lifeboat (zero hardware)

**What:** Design the *mission trajectory itself* so that a propulsion failure is
survivable with no intervention. The canonical example: a **free-return**
lunar trajectory — if the engine dies after trans-lunar injection, the ship loops
around the Moon and comes back to Earth on its own (this is literally what saved
Apollo 13). Analogous free-return and abort-to-Earth windows exist for Mars.

**Why it's the cheapest lifeboat of all:** it weighs nothing. The safety is in
the geometry.

**Best for:** Always worth layering in, especially early lunar and Mars missions.
**Weakness:** Constrains the trajectory (often costs Δv or time vs. the optimal
path), and only covers the failure modes the geometry happens to address — it
gets you *home*, not necessarily *alive* if life support is the thing that failed.

---

## How they layer

A mature architecture isn't one of these — it's all of them, matched to regime:

```
LEO            : co-orbital shelters on busy planes + decay-is-your-lifeboat
GEO            : node depots + rescue tugs (already commercial)
Cislunar       : node depots (EML1/EML2/NRHO/LLO) + free-return trajectories
Earth->Mars    : breadcrumb convoys per crewed flight + abort-to-Earth windows
Mars system    : node depots (Phobos, low Mars orbit, Mars L-points)
Outer system   : node depots at moons, storables/nuclear only, mining-route convoys
```

The thread: **passive caches at nodes, co-flown caches on corridors, active tugs
where traffic pays for them, and free trajectory safety everywhere it's available.**

→ next: `05-open-questions.md`
