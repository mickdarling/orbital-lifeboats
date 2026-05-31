# 13 — The toolkit & figures

The first twelve notes were backed by three standalone scripts (`napkin.py`,
`reachability.py`, `phase1.py`). Those still run and still match the notes, but
the calculations now also live in a proper, reusable package so you can **plug in
values and regenerate everything** — numbers *and* graphs.

## The package: `orbital_lifeboats/`

Pure standard library (no numpy / matplotlib / anything to install). Modules:

| Module | What it gives you |
|--------|-------------------|
| `constants` | Bodies (Sun, Earth, Moon, Mars, …) with μ, radius, orbit; AU, G0 |
| `astro` | Two-body mechanics: circular states, Hohmann, plane change, reachable apoapsis, and a **validated universal-variable Lambert solver** (`test_astro()` round-trips a circular orbit to <0.01 m/s) |
| `reachability` | The two-budget model: `phasing_options`, `phasing_best`, `max_reach_angle`, `responders_for_ring`, `intercept_curve`, `hohmann_floor`, `ion_time`/`ion_deliverable` |
| `boiloff` | Storage timelines (`fraction_remaining`, `days_to_lose`) and `solar_fraction` |
| `failures` | The failure-mode taxonomy as data (id, category, **clock_h**, needs, echelon) |
| `fleet` | Program sizing: `plan_station`, `size_lean`, `size_full` → counts, mass, cost |
| `presets` | **The "plug in the values" surface**: `STATIONS`, `DesignParams`, unit mass/cost |
| `svgplot` | Dependency-free SVG charts: `line_chart`, `heatmap`, `barh`, `stacked_bar` |

Quick use:

```python
from orbital_lifeboats import reachability as R, presets, fleet
R.max_reach_angle(6, 400, presets.STATIONS[0].radius)   # reachable arc, deg
fleet.size_full(presets.STATIONS).cost_total_b           # program $B
```

## Plugging in values

Everything funnels through `presets.py`. Edit and re-run `generate_figures.py`:
- **Add a station** (e.g. Haven-1 when it's crewed): append a `Station(...)` to
  `STATIONS`. The fleet re-sizes and the per-plane coverage recomputes.
- **Change the design clock** (insure against minutes-not-hours): set
  `DesignParams.design_clock_h`. Watch the responder count and cost move.
- **Change unit mass/cost or launch price**: the cost figures track it
  (Starship-class launch ≈ set `launch_cost_b_per_t` to noise).

Because the figures are generated *from* these inputs, the graphs are never stale
relative to the assumptions — they're one `python3 generate_figures.py` away.

## The figures (`figures/`)

`python3 generate_figures.py` writes nine SVGs + an `index.html` gallery (open it
in any browser). The "fire-station staging" picture, in charts:

1. **Phasing tradeoff** — Δv vs catch-up time per phase gap; the feasible corner.
2. **Cross-orbit intercept** — the Δv floor and the speed penalty.
3. **Reachability map** — *the coverage map*: phase gap × clock → cheapest rescue
   Δv (grey = unreachable in time). Where coverage is cheap vs costly vs impossible.
4. **Period time-floor** — period vs orbit; where phasing rescue dies.
5. **Boiloff** — what survives in a dormant cache over a year.
6. **Solar power** — 1/r² falloff vs distance.
7. **Failure modes by clock** — what we're rescuing, sorted by the time we have.
8. **Coverage by regime** — reachable arc vs clock for LEO/MEO/GEO (strong vs weak).
9. **Program cost** — Phase-1 lean (~$1B) vs full (~$3B) breakdown.

## Relationship to the original scripts

`napkin.py`, `reachability.py`, `phase1.py` remain as the **narrative/CLI**
versions (they print the annotated walkthroughs the notes cite). The package is
the **library** version of the same math, plus the plotting and the figure suite.
When they disagree on a fringe number it's because the package applies design
rules (e.g. spares margin) uniformly; both are order-of-magnitude.

## What's still missing (honest)
- Three-body (CR3BP) dynamics for NRHO/EML — the package is two-body, so cislunar
  figures would be qualitative until that's added.
- A Monte-Carlo coverage simulator (traffic × failure-clock distribution →
  P(rescued) vs fleet size) — the natural next module, `montecarlo.py`.
- Burn-dispersion → guardian-count tiling for the pre-positioning model (note 11).
