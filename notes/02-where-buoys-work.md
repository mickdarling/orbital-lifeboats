# 02 — Where buoys actually work: a node-by-node tour

Ordered by how soon humans will be there. For each: is a *passive* cache viable,
what should it hold, and what's the catch.

---

## Earth orbit (now → always)

**LEO.** Paradoxically the *worst* place for a rescue-buoy network and the place
that needs it least. The plane-change tax (§2) means you'd need hundreds to
thousands of buoys to cover all planes (§6), and a stranded LEO craft has a
built-in lifeboat anyway: **atmospheric decay brings it home.** A dead ship in
LEO reenters in days to months. The danger in LEO is loss of life support before
decay, not loss of a way home — so the useful LEO cache is a **co-orbital
shelter on a specific high-traffic plane** (ISS/Tiangong at 51.6°, sun-synch ~98°,
maybe a couple of popular smallsat shells), not a blanket network.
- Hold: O2/N2, water, food, CO2 scrubber media, a pressurized refuge, comms.
- Catch: must share the user's plane. One per popular plane, phasing covers the
  rest.

**GEO belt.** A genuine node: everything is in (nearly) one plane at one radius,
all moving at the same 3.07 km/s, drifting only slowly in longitude. A dead GEO
sat is stuck forever (no decay). A few caches spaced around the belt could be
reached by slow longitude drift — almost pure phasing. Good candidate for
**propellant + a robotic refuel/reboost tug** (this is basically what MEV/mission-
extension vehicles already do commercially).

**MEO / transfer ellipses (GTO).** Awkward middle ground — high relative
velocities, eccentric orbits, the Van Allen belts. Skip for caches; cover with
tugs.

---

## Cislunar (this decade → next)

The sweet spot for the whole concept, because it's full of natural low-energy
nodes and the distances are still small enough that solar power works for active
cooling.

- **EML1** — gateway between Earth and Moon, low station-keeping. A propellant +
  consumables depot here serves both lunar-bound and Earth-return traffic.
- **EML2 / NRHO** — where Gateway orbits; the staging point for lunar surface
  ops. Cache here backstops surface sorties.
- **Low Lunar Orbit (LLO)** — last stop before descent; cache supports aborts to
  orbit.
- **Lunar surface depots** — at the poles (ice → water → O2/H2). Less "buoy,"
  more "base annex," but part of the same survival web.

Cislunar caches can run **active cryo-cooling on solar power** (100% sunlight),
so they can hold methalox/hydrolox, not just storables. Free-return trajectory
design (see `04`) means some lunar aborts need *no* hardware at all — the
trajectory itself is the lifeboat.

---

## Earth–Mars (next → 2 decades)

Here the corridor problem bites. Hohmann Earth→Mars is ~5–6 km/s of heliocentric
Δv split across two burns (§1), and the transfer takes ~6–9 months. A crippled
ship mid-transfer cannot reach an off-trajectory cache.

Viable patterns:
- **Breadcrumb convoy:** pre-stage caches on the *same* transfer in the same
  window. Reachable by phasing. (See `04`.)
- **Mars-system nodes:** once you arrive, Mars has its own L-points, Phobos/
  Deimos (Phobos as a propellant/ice depot is a recurring proposal), and low Mars
  orbit. These behave like the cislunar nodes — passive caches work again.
- **Aldrin cycler:** a buoy on a permanent Earth↔Mars cycling orbit (see `04`)
  passes both planets forever, but *boarding* it costs the V∞ match (km/s) at
  each flyby. It's a habitat/way-station you rendezvous with on schedule, not an
  emergency float you stumble onto.

Sunlight at Mars is ~43% of Earth's — active cooling still works, but tanks and
arrays grow.

---

## Outer system (multi-decade, speculative)

Jupiter, Saturn, the asteroids. Hohmann to Jupiter is ~14 km/s and years of
flight (§1). Two regime changes dominate:

1. **Sunlight collapses.** ~3.7% at Jupiter, ~1.1% at Saturn (§5). Solar cryo-
   cooling is dead. A cache out here must hold **storables, water, and gas**
   (zero-boiloff for free) or carry a **nuclear** power source (RTG/fission) for
   active cooling. Water doubles as radiation shielding, drinking supply, and —
   with power — splittable propellant.
2. **Nodes are the moons and the L-points.** The natural caches are the icy
   moons (Europa, Enceladus, Titan, Ceres) and Jovian/Saturnian Lagrange points.
   Free-floating heliocentric buoys in the outer system are nearly useless;
   everything worth caching clusters around the giant planets' gravity wells.

The asteroid belt is the interesting wildcard: lots of bodies, but vast spacing
and a spread of orbits — a buoy network there only makes sense *along
established mining/transit routes*, the breadcrumb model again, not a grid.

---

## The pattern across all of it

Passive caches earn their mass at **gravitationally distinguished nodes**
(L-points, parking orbits, moons, the GEO belt) and along **pre-flown
trajectories** (convoys). Everywhere else — open corridors, blanket shells — you
need active hardware (tugs) or you're spending more Δv to reach the lifeboat than
you had to begin with.

→ next: `03-what-you-can-keep.md`
