"""
Program sizing: stations + design params -> fleet counts -> mass -> cost.
Generalizes phase1.py. Everything flows from the reachability engine, so changing
the design clock or budget in presets re-sizes the whole program.
"""

import math
from dataclasses import dataclass
from .presets import DEFAULT
from .astro import period
from .reachability import max_reach_angle, responders_for_ring


@dataclass
class StationPlan:
    station: object
    period_min: float
    reach_deg: int
    ring: int
    formation: int
    stage1: int
    stage2: int
    stage3: int


@dataclass
class Program:
    plans: list
    deployed: dict       # {echelon: count}
    with_spares: dict
    mass_t: float
    cost_units_b: float
    cost_launch_b: float
    cost_dev_b: float
    cost_total_b: float
    label: str


def plan_station(station, p=DEFAULT):
    T = period(station.radius) / 60.0
    reach = max_reach_angle(p.design_clock_h, p.stage1_budget_ms, station.radius)
    ring = responders_for_ring(p.design_clock_h, p.stage1_budget_ms, station.radius)
    ring = int(ring) if ring != math.inf else 99
    s1 = p.formation_per_station + ring
    return StationPlan(station, T, reach, ring, p.formation_per_station,
                       s1, p.sustain_per_plane, p.recover_per_plane)


def _rollup(counts, p, dev_b, label):
    spar = {k: math.ceil(v * (1 + p.spares_margin)) for k, v in counts.items()}
    mass = sum(spar[k] * p.unit_mass_t[k] for k in spar)
    units = sum(spar[k] * p.unit_cost_b[k] for k in spar)
    launch = mass * p.launch_cost_b_per_t
    return Program([], counts, spar, mass, units, launch, dev_b,
                   units + launch + dev_b, label)


def size_full(stations, p=DEFAULT):
    plans = [plan_station(s, p) for s in stations]
    counts = {1: sum(pl.stage1 for pl in plans),
              2: sum(pl.stage2 for pl in plans),
              3: sum(pl.stage3 for pl in plans)}
    prog = _rollup(counts, p, p.dev_cost_full_b,
                   "FULL: echeloned network (Connect+Sustain+Recover)")
    prog.plans = plans
    return prog


def lifeboats_per_launch(launcher, lifeboat):
    """How many lifeboat units fit in one launch — the binding constraint is
    whichever of mass / volume runs out first. Returns a dict with the count,
    which limit binds, and the crew seats delivered."""
    by_mass = int(launcher.leo_capacity_t // lifeboat.mass_t)
    by_vol = (int(launcher.bay_volume_m3 // lifeboat.volume_m3)
              if launcher.bay_volume_m3 else by_mass)
    n = min(by_mass, by_vol)
    return {"n": n, "by_mass": by_mass, "by_volume": by_vol,
            "limit": "mass" if by_mass <= by_vol else "volume",
            "seats": n * lifeboat.crew}


def size_lean(stations, p=DEFAULT):
    """Just the free-flying formation refuges that add robustness beyond the
    docked craft; rely on decay + ground + existing return capsules."""
    counts = {1: p.formation_per_station * len(stations) + 1, 2: 0, 3: 0}
    prog = _rollup(counts, p, p.dev_cost_lean_b,
                   "LEAN: formation refuges only")
    prog.plans = [plan_station(s, p) for s in stations]
    return prog
