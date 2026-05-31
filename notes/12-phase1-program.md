# 12 — Phase 1: sizing a program for what's crewed today

Backed by `phase1.py` (which reuses the validated `reachability.py` engine).
Order-of-magnitude, assumptions stated in the script.

## The roster (verified May 2026)

Exactly **two** orbital assets are in continuous human habitation right now:

| Station | Inclination | Altitude | Period | Crew | Notes |
|---------|-------------|----------|--------|------|-------|
| **ISS** | 51.6° | ~417 km | ~92.9 min | 7 | Continuously crewed since Nov 2000; retire ~2030 |
| **Tiangong** | 41.5° | ~389 km | ~92.3 min | 3 | Crews of 3 (6 at handover) via Shenzhou |

Commercial free-flyers are **next window, not yet inhabited**: Vast Haven-1 is now
NET Q1 2027; Axiom's free-flyer ~2028. Each is **Phase 1.5** — and because each is
its own orbital plane, each simply *adds a plane* to the model (one line in
`phase1.py`). (Sources at bottom.)

## What the sizing says

**Standing coverage is cheap per plane, and the cost is replication across planes.**
The two stations are in **different planes** (different inclination *and*
precessing RAAN), and plane changes are unaffordable (note 02), so coverage can't
be shared — you build it twice.

For the design clock (a catastrophic depress with the crew in suits, ~6 h of O2)
and a 400 m/s stage-1 budget, the reachability model says a co-orbital responder
reaches ~104° of the ring — so **just 2 ring responders per plane** cover it
(LEO's ~93-min period means phasing fits inside the clock). Add **2 formation
lifeboats** per station (zero-phasing, to cover sub-period failures and to survive
a station-wide event that might also disable the docked return craft).

| Echelon | Per station | Both planes | Role |
|---------|-------------|-------------|------|
| Stage-1 "Connect" | 4 (2 ring + 2 formation) | 8 | stem the bleeding, buy time |
| Stage-2 "Sustain" | 1 | 2 | diagnosis-driven resupply |
| Stage-3 "Recover" | 1 | 2 | independent reentry-capable return |
| **+30% spares** | | **17 total** | reserve |

**Program cost, order of magnitude:**
- **Lean** (just the free-flying formation refuges that add robustness beyond the
  docked craft; rely on decay + ground launch-on-need for the rest): ~5 units,
  ~15 t, **~$1B**.
- **Full** (the echeloned network on both planes): ~17 units, ~80 t, **~$3B**.

For comparison: that's about *one commercial-crew development program*, set against
two stations worth well over $150B and crews that are irreplaceable.

## Why Phase 1 is so small — and honest about marginal value

LEO is the *forgiving* regime, which is exactly why the number is modest:
- **Short period (~93 min)** → phasing rescue fits inside an hours-long clock, so
  you don't need many co-orbital responders.
- **Atmospheric decay is a free lifeboat** → "get home" is partly solved by physics.
- **Stations already dock return craft** (Soyuz / Shenzhou / Crew Dragon) → the
  return function is largely covered already.

So the network's **honest marginal value** in Phase 1 isn't "a way home" — it's:
1. a refuge that survives the *same* event that might have compromised the docked
   craft (fire, depress, collision, toxic release — common-cause failures),
2. coverage of a casualty that has *separated* from the station (a departing or
   arriving vehicle that fails, an EVA emergency, a debris strike during approach),
3. autonomy / response time independent of a ground launch-on-need.

That framing keeps Phase 1 lean and defensible: don't rebuild what Dragon/Soyuz
already provide; add the robustness they can't.

## What would change the number
- **A tighter clock** (fire or toxic release with minutes, not hours) pushes the
  whole posture toward *formation-only* (you can't phase in minutes) — fewer ring
  responders, more co-located refuges.
- **More crewed stations** (Haven-1, Axiom, Orbital Reef, Starlab, Bharatiya
  Antariksh, future Tiangong expansion) each add a plane → roughly linear growth
  in the standing fleet. Five commercial stations would ~triple Phase 1.
- **Unit cost / launch cost** are the big cost levers; Starship-class launch would
  drop the launch line to noise and make the *full* posture the obvious choice.

## Roadmap (where the hard physics starts)

- **Phase 1 (now):** ISS + Tiangong. ~$1–3B. *This note.*
- **Phase 1.5:** commercial LEO stations as they're crewed — add planes.
- **Phase 2 (Artemis / cislunar):** the physics turns hostile. NRHO's **~6.5-day
  period breaks phasing entirely** (note 09) → formation-flying lifeboats become
  mandatory, not optional; **no atmospheric decay** to bring anyone home; deep
  gravity wells. **Pre-positioning at the insertion/injection burns** (note 11)
  becomes the central tool, because that's where Artemis crews are most exposed
  and the geometry is knowable. Expect this phase to be far costlier per crew
  protected than Phase 1.
- **Phase 3 (lunar base + mass driver):** once there's a lunar surface base (even
  automated), a **mass driver** changes the delivery game — see below.

### The mass-driver delivery concept (Phase 3 hook)

A lunar mass driver (electromagnetic launcher) could fling specially-prepared
emergency modules off the Moon at high velocity, reaching a cislunar casualty
**very fast** — directly attacking the *time* budget by brute launch speed instead
of pre-positioning. Two attractive twists:
- **Spend the boiloff.** Propellant that would evaporate anyway (note 03) can be
  pre-packaged and launched as the emergency payload — turning a loss into a
  delivered resource.
- **A fast projectile still has to match velocity** at the target, or it's just a
  high-speed flyby. So the launched module needs onboard Δv (or a catch mechanism)
  to circularize/rendezvous — the mass driver provides the *speed*, the module
  provides the *match*. Worth modeling: lunar-launch geometry only serves
  trajectories reachable from the Moon's position, so it complements (doesn't
  replace) the pre-positioned network.

This is the natural Phase-2/3 calculation set, for the next sessions.

---

## Sources (station roster, May 2026)
- [Tiangong space station — Wikipedia](https://en.wikipedia.org/wiki/Tiangong_space_station)
- [International Space Station — Wikipedia](https://en.wikipedia.org/wiki/International_Space_Station)
- [The Era of Private Space Stations Launches in 2026 — SingularityHub](https://singularityhub.com/2025/12/26/the-era-of-private-space-stations-launches-in-2026/)
- [NASA releases details on revised next phase of commercial space station development — SpaceNews](https://spacenews.com/nasa-releases-details-on-revised-next-phase-of-commercial-space-station-development/)
