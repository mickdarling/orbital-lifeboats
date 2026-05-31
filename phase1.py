#!/usr/bin/env python3
"""
Orbital Lifeboats — PHASE 1 program sizing.

Scope: what is *presently* in continuous human habitation in orbit (verified
May 2026): the ISS and Tiangong. Nothing else is permanently crewed yet
(Vast Haven-1 is NET Q1 2027; Axiom's free-flyer ~2028 — those are Phase 1.5,
add them as stations below when they're crewed).

This sizes a near-term rescue network for those two stations using the
echeloned triage model (notes 09-11) and the validated reachability engine
(reachability.py). Order-of-magnitude; assumptions are stated inline so you can
push them around. Run:  python3 phase1.py
"""

import math
from reachability import phasing_options, max_reach_angle, MU_EARTH, R_EARTH


def hr(t):
    print("\n" + "=" * 74 + f"\n{t}\n" + "=" * 74)


# ---------------------------------------------------------------------------
# What's actually up there and crewed (May 2026)
# ---------------------------------------------------------------------------
STATIONS = [
    # name, inclination (deg), altitude (km), nominal crew
    ("ISS",      51.6, 417.0, 7),
    ("Tiangong", 41.5, 389.0, 3),
]

# Design clock: the shortest life-support emergency we insure against.
# A catastrophic depressurization with the crew in suits gives ~hours of O2.
DESIGN_CLOCK_H = 6.0
# A first-responder (stage-1) chemical Δv budget:
STAGE1_BUDGET_MS = 400.0

# Per-unit mass (tonnes) and early-production unit cost ($B), order-of-magnitude.
UNIT_MASS = {1: 3.0, 2: 6.0, 3: 10.0}     # Connect / Sustain / Recover
UNIT_COST = {1: 0.08, 2: 0.12, 3: 0.25}   # $B each, early production
LAUNCH_PER_T = 0.0025                      # $B per tonne to LEO (~$2.5k/kg)
DEV_COST_FULL = 1.0                        # $B shared platform development
DEV_COST_LEAN = 0.6
SPARES_MARGIN = 0.30


def period_min(alt_km):
    r = R_EARTH + alt_km
    return 2 * math.pi * math.sqrt(r ** 3 / MU_EARTH) / 60.0


# ---------------------------------------------------------------------------
def coverage_per_station():
    hr("1.  STANDING COVERAGE — how many stage-1s per station (from the model)")
    print(f"Design clock {DESIGN_CLOCK_H:.0f} h (suit O2 after a bad depress); "
          f"stage-1 budget {STAGE1_BUDGET_MS:.0f} m/s.\n")
    print("Each station is its own orbital PLANE; plane changes are unaffordable")
    print("(note 02), so coverage does NOT share between stations.\n")
    results = {}
    for name, inc, alt, crew in STATIONS:
        r = R_EARTH + alt
        T = period_min(alt)
        reach = max_reach_angle(DESIGN_CLOCK_H, STAGE1_BUDGET_MS, r)
        ring = math.ceil(360 / (2 * reach)) if reach else 99
        # Posture: formation lifeboats (zero-phasing, survive station-wide events)
        # + co-orbital ring responders (catch separated casualties around the plane)
        formation = 2
        s1 = formation + ring
        results[name] = dict(inc=inc, alt=alt, crew=crew, period=T,
                             reach=reach, ring=ring, formation=formation, s1=s1)
        print(f"  {name:9s} i={inc:4.1f}°  alt {alt:.0f} km  period {T:.1f} min  crew {crew}")
        print(f"    co-orbital reach within {DESIGN_CLOCK_H:.0f} h: ~{reach}°  "
              f"-> {ring} ring responder(s) cover the plane")
        print(f"    + {formation} formation lifeboats (zero-phasing, robust to a "
              f"station-wide event)")
        print(f"    => {s1} stage-1 'Connect' units for {name}\n")
    return results


def sustain_recover(results):
    hr("2.  SUSTAIN (stage-2) and RECOVER (stage-3)")
    print("LEO has a built-in lifeboat — orbital decay brings a dead ship home —")
    print("and stations already dock Soyuz/Shenzhou/Crew Dragon as return craft.")
    print("So Phase-1 stage-2/3 are LEAN: they add robustness those don't give")
    print("(a refuge that survives the SAME event that disabled the docked craft,")
    print("and an independent deorbit-capable return).\n")
    for name in results:
        results[name]["s2"] = 1   # one modular resupply per plane
        results[name]["s3"] = 1   # one independent reentry-capable refuge per plane
        print(f"  {name:9s}: 1 stage-2 (Sustain, co-orbital, modular resupply) "
              f"+ 1 stage-3 (Recover, reentry-capable)")
    print("\n  (Ground launch-on-need also backstops stage-2; we still field one")
    print("  per plane for autonomy and response time.)")
    return results


def roll_up(results):
    hr("3.  FLEET TOTALS")
    tot = {1: 0, 2: 0, 3: 0}
    for name, d in results.items():
        tot[1] += d["s1"]; tot[2] += d["s2"]; tot[3] += d["s3"]
    print(f"  deployed:  stage-1 {tot[1]}   stage-2 {tot[2]}   stage-3 {tot[3]}   "
          f"= {sum(tot.values())} units")
    # add spares
    spar = {k: math.ceil(v * (1 + SPARES_MARGIN)) for k, v in tot.items()}
    print(f"  +{int(SPARES_MARGIN*100)}% spares/reserve:  "
          f"stage-1 {spar[1]}   stage-2 {spar[2]}   stage-3 {spar[3]}   "
          f"= {sum(spar.values())} units")
    return spar


def mass_cost(counts, dev_cost, label):
    mass = sum(counts[k] * UNIT_MASS[k] for k in counts)
    units = sum(counts[k] * UNIT_COST[k] for k in counts)
    launch = mass * LAUNCH_PER_T
    total = units + launch + dev_cost
    print(f"\n  --- {label} ---")
    print(f"    units: " + "  ".join(f"s{k}x{counts[k]}" for k in counts))
    print(f"    deployed mass     : {mass:5.0f} t")
    print(f"    unit production   : ${units:4.2f} B")
    print(f"    launch (@~$2.5k/kg): ${launch:4.2f} B")
    print(f"    development       : ${dev_cost:4.2f} B")
    print(f"    PROGRAM TOTAL     : ${total:4.1f} B")
    return total


def main():
    print(__doc__)
    results = coverage_per_station()
    results = sustain_recover(results)
    full = roll_up(results)

    hr("4.  PROGRAM COST — two postures, order of magnitude")
    print("All figures order-of-magnitude (see UNIT_* assumptions at top of file).")
    # Lean: just the free-flying formation refuges that add robustness beyond the
    # docked return craft. 2 per station + 1 spare = 5 stage-1 only.
    lean = {1: 2 * len(STATIONS) + 1, 2: 0, 3: 0}
    mass_cost(lean, DEV_COST_LEAN,
              "LEAN: formation refuges only (rely on decay + docked craft + ground)")
    mass_cost(full, DEV_COST_FULL,
              "FULL: echeloned network (Connect + Sustain + Recover, both planes)")

    hr("5.  PHASE-1 BOTTOM LINE")
    print(f"""
  * Presently crewed in orbit: ISS + Tiangong — TWO planes, no sharing.
  * Shortest clock (suit depress, ~{DESIGN_CLOCK_H:.0f} h) needs only ~2 co-orbital
    responders per plane (LEO period ~93 min, so phasing fits) — plus formation
    lifeboats for the sub-period failures. Coverage is cheap PER plane; the cost
    is replicating it across planes.
  * Total fleet: a couple dozen modules at most. Dominated by stage-1 (the cheap
    echelon); stage-2/3 stay lean because LEO decay + existing docked return craft
    already cover 'get home'.
  * Order-of-magnitude program: ~$1B lean / ~$3B full — one commercial-crew
    development, against two stations worth >$150B and irreplaceable crews.
  * Phase 1 is small because LEO is forgiving. The expensive physics (long
    periods, no decay, deep gravity wells) starts at Phase 2 (Artemis / cislunar)
    and Phase 3 (lunar base + mass-driver delivery). See notes/12.
    """)


if __name__ == "__main__":
    main()
