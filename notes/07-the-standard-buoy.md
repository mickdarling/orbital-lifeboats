# 07 — The Standard Buoy: a reference design

Pulling the threads together (`04` primitives + `06` failure modes + `03`
storage) into one coherent unit. The design goal that makes it work:

> **Put it up, and never think about it again.** It sits dormant for years to
> decades, costs nothing to keep, and wakes only when someone needs it. You don't
> maintain the network — you *manufacture* it. A production line keeps stamping
> out identical units and dropping them into more orbits and trajectories.

This is fire-and-forget infrastructure, not a fleet of tended outposts. Five
design choices make that possible.

---

## 1. Power: solar by default, nuclear for the deep ones

Tier the power source by *where the buoy lives*, rather than going nuclear across
the board:

- **Inner system (LEO, cislunar, Mars) → solar.** Sunlight is plentiful (100% at
  Earth/Moon, still 43% at Mars), panels are cheap and mass-produced, and there's
  no scarce-isotope supply chain throttling how many you can build. For the bulk
  of the network — which lives where the people are, this decade and next — solar
  is the right default.
- **Outer system (belt and beyond) → RTG / small fission.** Past Jupiter sunlight
  collapses to a few percent (`napkin.py` §5), so the deep buoys carry their own
  nuclear source. These are the minority, which is good, because nuclear is the
  production bottleneck (see below).

**The radiator argument is a wash.** An RTG has to dump its waste heat through a
radiator — but a solar bus has to radiate its electronics and battery heat too, so
both designs carry radiators regardless. Thermal management isn't a reason to
prefer one over the other.

**Battery aging — the solar buoy's real long-duration risk — is now largely
tractable.** Two developments and one architecture trick:

- **Sodium-ion cells.** They tolerate much wider temperature swings and take
  *one to two orders of magnitude* more charge/discharge cycles than lithium-ion.
  For a buoy cycling through eclipses for a decade-plus, that roughly removes
  cycle-life as the binding constraint (calendar aging remains, but it's far less
  punishing, and the wide temp tolerance eases thermal design too).
- **Capacitor-buffered power pipeline: solar → capacitors → batteries.** Run the
  always-on dormant loads off **capacitors**, not the battery. Supercaps have
  effectively unlimited cycle life and shrug off temperature, so the core stays
  lit (station-keeping nudges, distress receiver, beacon, health telemetry) on a
  component that never wears out. Solar trickles into the caps; the caps top up
  the **batteries** slowly over time; the batteries sit in reserve and are only
  drawn down on a *call to duty* — waking life support, an ion burn, a tug op.
  This keeps the high-energy chemistry mostly *at rest* (good for calendar life)
  and pushes all the relentless cycling onto the part that doesn't mind. The
  catch is energy density: caps store little for their mass, so they keep the
  low-power electronics alive but can't run life support alone — hence the
  battery for surge. That division of labor (**caps = keep-alive, battery =
  surge**) is exactly right for an asset that's 99% dormant.
- **Fuel cells** could do the store/release job, but they're still cycling
  chemical reactions back and forth, so it's not clear they age better than a
  good battery chemistry over decades — probably not worth the plumbing here.

Net: with sodium-ion + a capacitor-buffered pipeline, a **solar** buoy can
plausibly sit untended for the timescales we care about, and **RTG drops back to
being a deep-outer-system option** rather than a necessity.

**And near-term is what matters.** The honest scope of this exercise is the next
~10-20 years — Earth-Moon space, plus the first crewed Mars trajectories. The
outer system with actual people in it is a later era that will have its own
resources (in-situ propellant, local manufacturing, established nuclear infra) and
its own answers; we don't have to solve Saturn today. So design for **solar +
sodium-ion + capacitors in cislunar space first**, and let the deep variants wait
until there's anyone out there to rescue.

## 2. Dormant life support: consumables stowed, not running

The insight that defeats the boiloff/shelf-life problem: **life support doesn't
run until there's someone aboard.** While dormant, the cache is essentially a
sealed warehouse:
- O2, N2, water, food, medical, scrubber media — all **sealed and inert**, not
  cycling. Nothing is being consumed, nothing is wearing out.
- Shelf life becomes **sealed-storage physics** (slow material/radiation aging),
  not **active-system reliability** (a cooler or scrubber that must run flawlessly
  unattended for a decade). The hardest reliability problem just evaporates
  because the hard systems are *off*.
- On **detection of an incoming/arriving crew** (or a received distress call),
  the buoy boots: spins up life support, pressurizes the refuge, brings the
  cabin to temperature, opens comms. Consumables start being spent only at the
  moment of actual use.

So you can pre-position the survival kit years in advance and it's all still
there, full, the day it's needed. This is the single biggest reason the concept
is even affordable: **you're not paying to keep empty lifeboats running.**

## 3. Slow-push propulsion: ion drive + storable RCS

Two propulsion systems for two jobs:
- **Solar-electric / ion** for the patient work: slowly repositioning itself to
  follow predicted traffic, drifting toward a developing emergency, or acting as
  a **gentle tug** to move a stranded capsule from one orbit to a better one — the
  "small push" that a crippled but occupied capsule can't give itself. Ion is
  high-Δv-per-mass given *time*, which a fire-and-forget asset has plenty of.
  (RTG/fission can even power the thrusters — radioisotope-electric propulsion.)
- **Storable chemical RCS** (hydrazine, years of shelf life) for the things ion
  can't do fast enough: final docking, detumble, a quick nudge, attitude control.

The Δv lives in the buoy, not the victim (the point from note 04 §D): the capsule
just has to survive and be findable; the buoy does the moving.

## 4. It can become the reentry/landing vehicle

This is what covers failure modes A3, C1, I1 — *"fuel-rich but can't get down,"*
and *"the hab is gone, we have to abandon ship entirely."* The crew climbs into
the buoy and **the buoy takes them down.**

So the buoy is built with a heat shield (or aerocapture capability) and enough
control authority to **place itself on a reentry/landing trajectory on demand.**

Crucially — and this is your call-out — you do **not** park them on free-return
trajectories that naturally intersect a planet. A buoy that deorbits itself is a
buoy you've lost. Instead you park them on stable, non-impacting paths, but design
them so it's **cheap and easy to *change* their path** into a reentry/landing one
*when they're carrying people.* Easy-to-retarget, not pre-aimed-at-the-ground.

## 5. A bus you plug modules into — not one rigid design

Don't stamp out a single fixed unit; stamp out a **common bus** and configure it.
This is how real spacecraft are already built (a standard satellite bus + mission-
specific payloads), and it resolves the tension between "mass-produce one thing"
and "the buoy near Jupiter needs to be different from the one in the ISS plane."

**The common bus (stamped out at volume, identical):** structure, power
(solar *or* RTG slot — same mounting), propulsion (ion + storable RCS),
avionics/autonomy, the distress receiver + beacon + relay, station-keeping, and a
standardized docking port. This is the part the conveyor belt produces. You stop
reasoning about each buoy and start reasoning about *production rate* and
*placement strategy.*

**Plug-in payload modules (matched to where it'll live and what it must do):**
- consumables pack (air / water / food, sized to the regime),
- medical bay,
- propellant-transfer kit,
- storm-shelter shielding (water/regolith) for radiation modes,
- extra comms/nav relay capacity,
- reentry/landing kit (heat shield) for "carry them down" duty.

**A few standardized variants, all from the same bus + module kit:**

| Variant | Where | Power | Key modules |
|---------|-------|-------|-------------|
| Refuge buoy | cislunar nodes (EML1/2, NRHO, LLO) | solar | big consumables, medical, refuge |
| Corridor shelter | Earth↔Mars breadcrumb convoy | solar | storm shielding, consumables, relay |
| Reentry lifeboat | low planetary orbit (LEO, LMO) | solar | heat-shield kit, refuge |
| Deep-space tug | belt and beyond | RTG | ion-heavy, propellant transfer, minimal consumables |

**Standardized interfaces, two layers:** internal (bus↔module) so the factory can
mix and match, and external (one docking standard, one comms protocol, water as
the universal consumable) so *any* ship in trouble can use *any* buoy. The
standardization problem from `05` is a precondition, not an afterthought.

**Then scatter and grow.** Following `02`: dense at nodes, seeded along corridors,
self-repositioning via ion to fill gaps — and **self-reporting health** so the
network always knows which buoys are good, full, and reachable. The network grows
by you just building more buses and bolting on whichever modules that orbit needs.

---

## The unit, in one breath

> A mass-produced pod — solar-powered near the sun, RTG-powered out deep — that
> parks itself on a stable non-impacting orbit and sleeps for years — listening,
> beaconing, holding station — with its
> survival supplies sealed and its life support *off*. When it detects a crew in
> trouble it wakes, ion-drifts (or tugs the capsule) into rendezvous, opens up a
> pressurized refuge with air, water, power, and medical, relays the distress
> call, and — if there's no other way home — retargets itself onto a reentry path
> and carries the survivors down.

It is, at once, the **float** (refuge + supplies), the **coast-guard cutter**
(Δv + tug), the **radio** (relay + beacon), and the **lifeboat** (reentry
vehicle) — which is exactly what `06` says you need, because the failure that
strands a crew is rarely the failure you designed the buoy around.

## Where this still hurts (carried to `05`)
- RTGs need fuel (Pu-238) that is scarce and export-controlled; fission units are
  heavier and politically fraught. Going solar-default confines this to the
  outer-system minority — but the deep variants are exactly the ones you can't
  build at volume, so the network thins out precisely where rescue is hardest.
- The quiet long-duration risk on the *solar* majority is **battery aging**, not
  the panels — a decade of untended charge/discharge cycling is its own reliability
  problem (see §1). "Fire and forget" leans on solving it.
- Heat shield + reentry capability is mass the buoy carries for years against a
  rare event. Worth it for the modes only it covers, but it's not free.
- "Detect a crew in trouble" is a hard autonomy + sensing + comms problem,
  especially for a silent capsule (failure mode F1/E1).
- A maneuverable, nuclear-powered, autonomous object you scatter everywhere is
  also a dual-use concern (it's a satellite that can change orbits and carry
  things). Governance, not physics, but real.
