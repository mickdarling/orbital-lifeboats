# 14 — Launch vehicle sensitivity (Falcon vs Starship)

Backed by `orbital_lifeboats/astro.py` (Tsiolkovsky helpers) and the `LAUNCHERS`
preset. The short version: **Starship changes the constraint regime, not the
physics.** Module masses go *up* by design, the launch cost line *shrinks*, and
the orbital mechanics don't move at all.

## Mass doesn't come from the rocket — it comes from what the module must do

A module's mass is dry structure + payload + propellant. The propellant share is
set by the Δv budget via the rocket equation, *independent of launch vehicle*:

| Module / budget | propellant (% of wet mass) | wet/dry |
|-----------------|----------------------------|---------|
| Stage-1, 400 m/s, storable | 12% | ×1.14 |
| Stage-1, 1200 m/s (rendezvous + margin), storable | 32% | ×1.47 |
| Stage-3 tug, 2500 m/s, **storable** | 55% | ×2.22 |
| Stage-3 tug, 2500 m/s, **ion** | 8% | ×1.09 |

(That last row is why a recovery tug uses ion: 2.5 km/s costs it 8% of its mass
instead of 55%.) None of this depends on whether you launched on a Falcon or a
Starship — it depends on the job.

## What Starship actually changes

**1. It removes the "lightweighting tax," so modules get heavier by choice.**
On Falcon you squeeze every kg (mass optimization is expensive engineering and
launch is dear). On Starship you don't bother — heavier, simpler, more-margin,
more-consumables modules are fine. Realistically that's a ~2× growth in design
mass (stage-1 ~3 t → ~6–15 t; stage-2 ~6 → ~15–30 t; stage-3 ~10 → ~20–40 t).

**2. The launch line collapses even as mass doubles.** Approximate $/kg: Falcon 9
~$3.0k, Falcon Heavy ~$1.5k, Starship ~$0.5k credible-early, ~$0.15k aspirational.
For the Phase-1 full fleet (see `phase1.py` / `fleet.py`):

| Module masses | Deployed mass | Falcon 9 | Falcon Heavy | Starship | Starship (goal) |
|---------------|---------------|----------|--------------|----------|-----------------|
| constrained (3/6/10 t) | 81 t | $0.24B / 5 flights | $0.12B / 3 | $0.04B / **1** | $0.01B / 1 |
| relaxed (6/12/20 t) | 162 t | $0.49B / 10 | $0.24B / 6 | $0.08B / **2** | $0.02B / 2 |

So doubling module mass and switching to Starship still **cuts** the launch line
(from ~$0.24B to ~$0.08B) — and the *whole Phase-1 fleet fits in 1–2 Starship
flights* instead of 5–10 Falcon 9s. Launch goes from ~6–8% of the program to
~1–2%.

**3. Volume unlocks capability.** Starship's ~8 m bay / ~1000 m³ means a stage-1
"Connect" can be a real shirt-sleeve refuge for a crew for days, not a phone-booth
capsule jammed into a 5 m fairing. The dormant-cache concept (note 07) gets
roomier consumables and shielding for free.

## What it does NOT change

- **The reachability math.** Δv budgets, the phasing time-floor, the coverage map,
  the fleet *counts* and placement (notes 08–11) are all **mass-invariant** — a
  3 t or 15 t responder both need the same 400 m/s; the heavier one just carries
  proportionally more propellant (rows above). So the coverage figures and the
  number of modules per plane don't move.
- **The dominant program costs.** Development + unit production are mass-
  insensitive (they're avionics, life support, heat shield, software). Launch was
  always the small line. So the program total stays ~$1–3B order-of-magnitude;
  Starship mostly buys *more capable hardware and far simpler logistics* for the
  same money, not a cheaper bill.

## How many lifeboats per Starship launch?

Packing is the binding question, and it's **mass OR volume, whichever runs out
first** (`fleet.lifeboats_per_launch`). Starship ≈ 100 t (credible early) to LEO
and ~1000 m³ usable bay. Three representative recovery-vehicle designs:

| Lifeboat | mass / volume | per Starship (early, 100 t) | per Starship (goal, 150 t) | binds on |
|----------|---------------|------------------------------|-----------------------------|----------|
| Compact refuge pod (squeezed) | 3 t / 25 m³ | **33** (99 seats) | 40 (120 seats) | mass→volume |
| Standard refuge (relaxed) | 8 t / 50 m³ | **12** (48 seats) | 18 (72 seats) | mass |
| Reentry lifeboat (brings crew home) | 25 t / 80 m³ | **4** (24 seats) | 6 (36 seats) | mass |

So a **single Starship** lofts ~12 standing refuges, or ~4 full bring-them-home
reentry vehicles, or ~33 compact pods. Refuges and reentry vehicles are **mass-
limited** (dense — heat shield, tanks); only the lightest compact pod ever becomes
volume-limited.

**The headline:** the entire current human population in orbit is **10** (ISS 7 +
Tiangong 3). **One Starship of reentry lifeboats = ~24 seats home — 2.4× the
people currently in space.** Everyone in orbit could be given a dedicated ride
home, with margin, in a single launch. The whole Phase-1 *network* (notes 12) is
1–2 Starship flights.

## Bottom line

> Starship doesn't make the lifeboats lighter — it makes them **heavier on
> purpose, cheaper to loft, roomier, and deliverable in one or two flights.** The
> mass goes up, the launch cost goes down, the orbital mechanics stay put. And one
> Starship can carry more lifeboat seats than there are people in orbit. Plug a
> different `LAUNCHERS[...]` / `LIFEBOATS[...]` entry into the model and watch the
> counts move.
