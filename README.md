# Orbital Lifeboats

*Napkin math for a network of emergency resource caches across the solar system —
the WWII English Channel rescue buoy, reimagined for spaceflight.*

---

## The seed idea

During WWII, both the Luftwaffe (the *Rettungsboje*) and the RAF anchored
**rescue buoys / air-sea-rescue floats** in the English Channel. A downed pilot
or a crew off a sinking boat could swim to one: shelter, bunk, food, water,
flares, a radio, dry blankets. You didn't have to make it all the way home —
you had to make it to the *nearest float*, and then wait.

The premise here: as humans push out into the solar system over the next
decades, we'll be running missions that are one failure away from being
unrecoverable. Out of propellant. Out of oxygen. Out of options. There is no
port to limp into and no chandlery to resupply at.

So — what if we pre-positioned caches? Passive (or lightly active) depots
holding propellant, water, oxygen, food, comms relay, and shelter, parked in
**known, published orbits and trajectories**, chosen so a ship in trouble can
reach one *cheaply* (low Δv), drift to it, dock, and survive until rescue.

This repo is a place to play with that — mostly **big-number napkin math**, not
a mission proposal.

---

## The one insight that reframes everything

**In the Channel, the buoy is stationary and you swim to it. In orbit, nothing
is stationary and "distance" is measured in Δv, not meters.**

A swimmer in the water can move in any direction for the cost of effort. A
stranded spacecraft that is "out of fuel" cannot move at all — it is a ballistic
object coasting on a conic section, and it will keep coasting on that exact
conic forever. Two objects can be 10 km apart and need **kilometers per second**
of Δv to actually rendezvous, because they're on different orbits moving at
different velocities.

That single fact splits the whole concept into two regimes:

1. **Nodes** — places where things naturally congregate at *low relative
   velocity*: Lagrange points (EML1/EML2), halo/NRHO orbits, planetary parking
   orbits, the GEO belt. Here a passive buoy genuinely works like the Channel
   float: a nearby ship needs only a small Δv to close in. **Park caches here.**

2. **Corridors** — interplanetary transfer trajectories, where everything is
   screaming past everything else at multiple km/s. Here a randomly-placed
   passive buoy is useless: matching its orbit costs more Δv than a healthy ship
   carries, let alone a crippled one. The buoy can only help if it is on the
   **exact same trajectory** as the ship it's meant to save (the "breadcrumb /
   convoy" model — launch caches ahead of crews on the identical transfer), or
   if it has its **own propulsion** and comes to *you* (which makes it a rescue
   tug, not a buoy).

So the honest version of the idea inverts the Channel picture: **on a transfer,
the lifeboat usually has to come to the swimmer.** The passive "swim-to-it"
buoy only survives at the nodes. A lot of this repo is mapping which is which.

### And it's not a fuel depot

The second reframing (see `notes/06`): the emergency is **rarely "out of fuel."**
A ship can be fuel-rich and still dying — an O2 leak, a holed hab with the crew in
suits on a countdown, a medical crisis, or simply stuck in an orbit with no way to
reenter. Most failure modes are solved by **refuge + air + water + power + medical
+ comms + a ride home**, not propellant. So the buoy's most broadly useful payload
is the *stay-alive kit*; propellant only helps the minority of failures that are
actually about Δv. A network optimized as a fuel-depot grid would miss most of the
ways people die out there.

### The unit that makes it affordable

The reference design (`notes/07`) is **dormant and fire-and-forget**: you put it
up and never think about it again. Its life support stays *off* — supplies sealed
and inert — until a crew is detected, so shelf life is just sealed-storage physics,
not decades of unattended machinery running flawlessly. It's **solar-powered near
the sun, RTG-powered out deep** (the radiator's needed either way; the real catch
for solar is decade-long *battery* aging). Slow ion propulsion lets it reposition,
tug a stranded capsule, or — since you deliberately *don't* park it on a planet-
impacting trajectory — **retarget itself into a reentry vehicle and carry the
survivors down.**

And it isn't one rigid unit: you stamp out a **common bus** (power, propulsion,
comms/beacon, autonomy, docking) and **plug in modules** (consumables, medical,
shielding, propellant transfer, reentry kit) to make a few standardized variants —
a cislunar refuge, a corridor storm-shelter, a planetary reentry lifeboat, a deep-
space tug — all off the same production line. The network grows by just building
more.

---

## What's here

| File | What it is |
|------|------------|
| `napkin.py` | Runnable calculations: Δv maps, plane-change & phasing costs, boiloff timelines, coverage counting. Run it: `python3 napkin.py` |
| `reachability.py` | The time-vs-Δv model: phasing & Lambert engines, the period time-floor, why ion can't first-respond. Run it: `python3 reachability.py` |
| `phase1.py` | Program sizing for what's crewed *today* (ISS + Tiangong): fleet count, mass, cost. Run it: `python3 phase1.py` |
| `orbital_lifeboats/` | The reusable toolkit (pure stdlib): physics, reachability, boiloff, failure taxonomy, fleet sizing, SVG plotting. Edit `presets.py` to plug in values. |
| `generate_figures.py` | Generates the 11-figure SVG suite, the `figures/index.html` gallery, and the integrated `index.html`. Run it: `python3 generate_figures.py` |
| `build_site.py` | Builds the integrated single-page site (`index.html`) — docs + diagrams woven together, self-contained (stdlib Markdown→HTML in `orbital_lifeboats/mdsite.py`). |
| `solar-wind-turbine/` | A *separate* side-concept (own folder): a magnetic-sail "windmill" that harvests the solar wind for power that stays flat with distance from the Sun. Could power a deep-system cache. See its [README](solar-wind-turbine/README.md). |
| `notes/01-the-core-inversion.md` | Why "swim to the buoy" mostly fails in space, and the two regimes |
| `notes/02-where-buoys-work.md` | The node-by-node tour: LEO → cislunar → Mars → outer system |
| `notes/03-what-you-can-keep.md` | The storage problem: boiloff, what survives passively vs. needs power |
| `notes/04-architectures.md` | Candidate designs: node depots, breadcrumb convoys, cyclers, rescue tugs |
| `notes/05-open-questions.md` | The hard parts and the fun rabbit holes |
| `notes/06-failure-modes.md` | What we're *actually* rescuing — a taxonomy. It's rarely "out of fuel" |
| `notes/07-the-standard-buoy.md` | The reference unit: dormant, fire-and-forget, a bus you plug modules into |
| `notes/08-near-term-placement.md` | The concrete cislunar map — which orbits, ranked by how hard they are to hold |
| `notes/09-reachability.md` | Time + Δv together — the result that rewrites the architecture (fleet splits, clock sets the count) |
| `notes/10-triage-swarm.md` | Not one buoy — an echeloned response (Connect → Sustain → Recover). Stage 1's product is *time* |
| `notes/11-prepositioning.md` | Surge responders to scheduled risky burns (fore/aft/sides + a no-burn guardian); expendable safety apparatus |
| `notes/12-phase1-program.md` | Phase 1 sized: ISS + Tiangong, ~$1–3B, why LEO is the cheap regime + the roadmap to cislunar |
| `notes/13-toolkit.md` | The reusable package + figure suite: what's in it, how to plug in values, what's still missing |
| `notes/14-launch-vehicle-sensitivity.md` | Falcon vs Starship: mass goes up, launch cost down, mechanics unchanged; lifeboats-per-launch |
| `notes/15-phase2-artemis.md` | Phase 2 — Artemis & cislunar (2026 architecture, Gateway shelved): event-driven, pre-position the burns |

## Running it

Everything is pure standard library — **nothing to install**, just Python 3.

```sh
python3 napkin.py            # Δv maps, plane-change/phasing, boiloff, coverage
python3 reachability.py      # the two-budget (Δv + time) model, validated
python3 phase1.py            # program size for what's crewed today
python3 generate_figures.py  # writes figures/*.svg + figures/index.html
```

To **plug in your own values**, edit `orbital_lifeboats/presets.py` (stations,
design clock, responder budget, unit mass/cost) and re-run `generate_figures.py` —
the fleet, coverage, and cost figures all re-derive from those inputs. The toolkit
is importable too:

```python
from orbital_lifeboats import reachability as R, fleet, presets
R.max_reach_angle(6, 400, presets.STATIONS[0].radius)   # reachable arc (deg)
fleet.size_full(presets.STATIONS).cost_total_b          # program cost ($B)
```

For the **integrated page** — all the documentation and every diagram woven into
one self-contained, offline file — open **`index.html`** (built by
`generate_figures.py`, or `python3 build_site.py` on its own). For the figures-only
gallery, open `figures/index.html`. The canonical figures are the SVGs in
`figures/`; PNG renders sit in `figures/png/` (regenerate with
`figures/render_png.sh`).

---

## Running totals (the headline napkin numbers)

Run `python3 napkin.py` for the live version. The punchlines it produces:

- **Δv is the currency.** A crippled ship's reachable set is tiny. Plane changes
  are the killer (a 30° plane change in LEO costs ~4 km/s — more than going to
  the Moon).
- **Phasing is nearly free.** Catching up to something on *your own orbit* costs
  almost nothing but time. This is the entire reason node depots and breadcrumb
  convoys are viable and scatter-shot buoys are not.
- **Hydrogen betrays you.** Passive liquid hydrogen boils off in days to weeks.
  An emergency cache that must sit for years should hold **storables**
  (hydrazine, NTO/MMH), **water**, and **gases** — or carry active cooling and a
  power source, which deep in the outer system means nuclear, not solar.
- **Blanket coverage is hopeless; node coverage is cheap.** Covering all of LEO
  to within reach takes *hundreds to thousands* of buoys (you must sample every
  orbital plane). Covering the ~handful of places people actually go —
  EML1, EML2, NRHO, the ISS plane, sun-synch, GEO — takes a *handful*.
- **The emergency is rarely "out of fuel."** Air leaks, medical, breached habs,
  and "stuck with no way down" dominate the failure modes (`notes/06`). The
  stay-alive kit matters more than the propellant tank.
- **Dormant beats stored.** Keep life support *off* until a crew arrives and the
  shelf-life problem nearly vanishes (`notes/07`). Power it with solar near the
  sun, RTG out deep — the sneaky long-duration risk on a solar buoy is *battery*
  aging, not the panels.
- **Build a bus, not a buoy.** A common mass-produced bus + plug-in modules yields
  a few standardized variants per regime, instead of one rigid design that fits
  nowhere well (`notes/07`).
- **Stability picks the address.** A buoy that burns fuel to hold station eats its
  own rescue reserve, so the near-term map ranks cislunar slots by how little they
  drift: stage the reserve in stable orbits (DRO, EML4/5), work the busy-but-leaky
  ones (NRHO, EML1, crewed LEO planes), and let ion propulsion redistribute
  (`notes/08`).
- **Rescue has two budgets — and the clock wins.** Δv isn't enough; the rescue
  must finish before the air runs out, and the cheap maneuvers are the slow ones
  (`notes/09`). This splits the fleet (**chemical** first-responders pre-staged
  *close*; **ion** reserve that only repositions between calls), and the
  *shortest life-support clock you insure against sets the network density*. The
  phasing time-floor is one orbital period — so at GEO/NRHO the lifeboat must
  fly in formation with the crew, not merely share the orbit.
- **It's a triage swarm, not a buoy.** An echeloned response — **Connect** (stem
  the bleeding, buy time) → **Sustain** (diagnosis-driven resupply) → **Recover**
  (repair/tug/return) — dissolves the single-buoy contradiction, because stage 1's
  real product is *time*, and buying time makes the slow heavy echelons reachable
  (`notes/10`). You replicate the cheap medic everywhere and keep the heavy
  recovery rigs rare.
- **Pre-position for the schedule; spend the cheap ones.** Emergencies are
  unpredictable, but crewed activity is *scheduled* and risky burns fail into
  *predictable* states — so surge stage-1s out of the reserve to a planned event's
  failure geometry (fore/aft = energy errors, sides = pointing, plus a no-burn
  guardian on the original trajectory). Co-locating with where the casualty will
  be defeats the clock *in advance*, and since stage-1s are cheap they can be
  **expendable** — safety apparatus you spend just to be available (`notes/11`).

---

## License

Copyright © 2026 Mick Darling. Dual-licensed:

- **Code** — the Python toolkit and build scripts — under the **MIT License**
  ([`LICENSE`](LICENSE)).
- **Writing & figures** — the notes, README prose, and diagrams — under
  **Creative Commons Attribution 4.0 (CC BY 4.0)**
  ([`LICENSE-CONTENT.md`](LICENSE-CONTENT.md)). Reuse freely with attribution:
  *"Orbital Lifeboats" by Mick Darling, CC BY 4.0.*

---

*Status: sketchpad. Everything here is order-of-magnitude. Correct me, break the
assumptions, push the numbers around.*
