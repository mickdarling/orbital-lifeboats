"""
Figure metadata — the single source of truth for the figure suite. Both the
gallery (generate_figures.py) and the integrated site (build_site.py) read this,
including which note each figure is placed beside.
"""

FIGURES = [
    {"file": "01_phasing_tradeoff.svg", "note": 9,
     "title": "Co-orbital phasing: Δv vs catch-up time",
     "caption": "Closing a co-orbital gap is cheap if you can wait — Δv falls "
                "with every extra orbit. The 6 h suit-clock and a 400 m/s "
                "budget bound the feasible corner (lower-left)."},
    {"file": "02_intercept_curve.svg", "note": 9,
     "title": "Cross-orbit intercept: the Δv floor & speed penalty",
     "caption": "A buoy on a different orbit (600 km higher) can't beat the "
                "Hohmann Δv floor, and arriving faster costs Δv steeply — a "
                "luxury rescue, hopeless on a short clock."},
    {"file": "03_reachability_heatmap.svg", "note": 9,
     "title": "Reachability map: cheapest rescue Δv",
     "caption": "The coverage map. For each phase gap (x) and life-support clock "
                "(y), the cheapest co-orbital rescue Δv. Grey = unreachable in "
                "time at any Δv. Coverage is cheap toward the top-left."},
    {"file": "04_period_floor.svg", "note": 9,
     "title": "The phasing time-floor scales with orbit",
     "caption": "Phasing can't beat one orbital period. Where the curve rises "
                "above the 6 h clock (past ~MEO), short-clock phasing rescue is "
                "impossible — at NRHO the period is ~6.5 days (off-chart)."},
    {"file": "05_boiloff.svg", "note": 3,
     "title": "Passive storage: what survives in a dormant cache",
     "caption": "Tank remaining over a year. Hydrogen is gone in ~100 days; "
                "storables, water, and gas are effectively permanent — which is "
                "why a fire-and-forget cache holds those."},
    {"file": "06_solar_power.svg", "note": 3,
     "title": "Solar power falls off as 1/r²",
     "caption": "Sunlight as a percent of Earth's. Past the asteroid belt, "
                "active cooling (and just staying alive) means nuclear, not "
                "solar."},
    {"file": "07_failure_modes.svg", "note": 6,
     "title": "Failure modes by life-support clock",
     "caption": "Each emergency's time-to-loss-of-crew, by category. The short-"
                "clock modes (fire, depress, radiation) drive the need for "
                "close/formation responders; long-clock ones tolerate slow "
                "recovery rigs."},
    {"file": "08_coverage_by_regime.svg", "note": 9,
     "title": "Where coverage is strong vs weak",
     "caption": "Reachable co-orbital arc vs clock, by orbit. LEO covers the "
                "whole ring in hours; GEO covers nothing until the clock exceeds "
                "~a day. The staircase is period-quantization."},
    {"file": "09_program_cost.svg", "note": 12,
     "title": "Phase-1 program cost (ISS + Tiangong)",
     "caption": "Order-of-magnitude cost for the two currently-crewed stations. "
                "Lean ≈ $1B (formation refuges only); Full ≈ $3B (echeloned "
                "network). Dominated by stage-1 units and development."},
    {"file": "10_lifeboats_per_launch.svg", "note": 14,
     "title": "Lifeboats per Starship launch",
     "caption": "Recovery vehicles per Starship (~100 t, ~1000 m³). Refuges and "
                "reentry vehicles are mass-limited. One Starship of reentry "
                "lifeboats (~24 seats) exceeds the entire current in-orbit "
                "population (10)."},
    {"file": "11_launch_cost_by_vehicle.svg", "note": 14,
     "title": "Launch cost of the fleet by vehicle",
     "caption": "Launch cost of the Phase-1 fleet (~81 t) by vehicle. Starship "
                "cuts the launch line to near-noise and carries the whole fleet "
                "in 1–2 flights vs ~5 on Falcon 9."},
]


def for_note(n):
    return [f for f in FIGURES if f["note"] == n]
