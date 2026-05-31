#!/usr/bin/env python3
"""
Orbital Lifeboats — napkin math.

Order-of-magnitude calculations for a network of emergency resource caches.
No external dependencies; just the standard library and high-school orbital
mechanics. Run it:  python3 napkin.py

Everything here is deliberately simple (patched-conic, circular orbits,
impulsive burns, linear boiloff). The point is to get the *shape* of the
problem right, not to plan a mission.
"""

import math

# ---------------------------------------------------------------------------
# Constants  (km, s)
# ---------------------------------------------------------------------------
MU_EARTH = 398_600.0        # km^3/s^2
MU_SUN   = 1.327_124e11
MU_MOON  = 4_902.8

R_EARTH  = 6_378.0          # km, equatorial
LEO_ALT  = 400.0
R_LEO    = R_EARTH + LEO_ALT
R_GEO    = 42_164.0         # km, geostationary radius
R_MOON_ORBIT = 384_400.0    # Earth-Moon distance

AU = 1.495_979e8            # km
R_MARS_ORBIT = 1.524 * AU
R_JUP_ORBIT  = 5.203 * AU
R_SAT_ORBIT  = 9.537 * AU


def hr(title):
    line = "=" * 74
    print(f"\n{line}\n{title}\n{line}")


# ---------------------------------------------------------------------------
# Core maneuvers
# ---------------------------------------------------------------------------
def v_circ(mu, r):
    """Circular orbital speed."""
    return math.sqrt(mu / r)


def hohmann(mu, r1, r2):
    """
    Two-burn Hohmann transfer between coplanar circular orbits.
    Returns (dv1, dv2, total) in km/s.
    """
    a_t = (r1 + r2) / 2.0
    v1 = v_circ(mu, r1)
    v2 = v_circ(mu, r2)
    v_peri = math.sqrt(mu * (2.0 / r1 - 1.0 / a_t))
    v_apo = math.sqrt(mu * (2.0 / r2 - 1.0 / a_t))
    dv1 = abs(v_peri - v1)
    dv2 = abs(v2 - v_apo)
    return dv1, dv2, dv1 + dv2


def plane_change(v, deg):
    """Δv to rotate a velocity vector of magnitude v by `deg` degrees."""
    return 2.0 * v * math.sin(math.radians(deg) / 2.0)


def reachable_apoapsis(mu, r, dv):
    """
    If you're on a circular orbit at radius r and you have a budget dv to spend
    as a single prograde burn, how high an apoapsis can you raise to?
    Useful for "how far can a half-dead ship even get?"
    """
    v = v_circ(mu, r) + dv
    energy = v * v / 2.0 - mu / r          # specific orbital energy
    if energy >= 0:
        return float("inf")                # escaped
    a = -mu / (2.0 * energy)
    return 2.0 * a - r                     # r_apo = 2a - r_peri


# ---------------------------------------------------------------------------
# 1. The Δv map — the "distances" between caches
# ---------------------------------------------------------------------------
def deltav_map():
    hr("1.  Δv MAP — what 'distance' actually costs (km/s)")
    print("Circular orbital speeds:")
    print(f"  LEO (400 km)        v = {v_circ(MU_EARTH, R_LEO):6.3f} km/s")
    print(f"  GEO                 v = {v_circ(MU_EARTH, R_GEO):6.3f} km/s")
    print(f"  Earth around Sun    v = {v_circ(MU_SUN, AU):6.3f} km/s")
    print(f"  Mars around Sun     v = {v_circ(MU_SUN, R_MARS_ORBIT):6.3f} km/s")

    print("\nHohmann transfers (coplanar, ideal):")
    for label, mu, r1, r2 in [
        ("LEO -> GEO",            MU_EARTH, R_LEO, R_GEO),
        ("LEO -> lunar distance", MU_EARTH, R_LEO, R_MOON_ORBIT),
        ("Earth -> Mars (helio)", MU_SUN,   AU,    R_MARS_ORBIT),
        ("Earth -> Jupiter",      MU_SUN,   AU,    R_JUP_ORBIT),
    ]:
        dv1, dv2, tot = hohmann(mu, r1, r2)
        print(f"  {label:22s} dv1={dv1:5.2f}  dv2={dv2:5.2f}  total={tot:5.2f}")

    print("\n  NOTE: heliocentric 'totals' above are burns *relative to the")
    print("  planet's orbital motion' — the injection from LEO is cheaper than")
    print("  it looks (you start with Earth's 29.8 km/s for free), but the")
    print("  point stands: these are the gaps a stranded ship must cross.")


# ---------------------------------------------------------------------------
# 2. The plane-change tax — why scatter-shot buoys fail
# ---------------------------------------------------------------------------
def plane_change_tax():
    hr("2.  THE PLANE-CHANGE TAX — the real reason 'swim to it' breaks")
    v = v_circ(MU_EARTH, R_LEO)
    print(f"At LEO (v = {v:.2f} km/s), Δv to change orbital plane by:")
    for deg in (1, 5, 10, 28.5, 51.6, 90):
        print(f"   {deg:5.1f} deg  ->  {plane_change(v, deg):5.2f} km/s")
    _, _, to_moon = hohmann(MU_EARTH, R_LEO, R_MOON_ORBIT)
    print(f"\nFor scale, raising LEO to lunar distance costs ~{to_moon:.2f} km/s.")
    print("So a ~30 deg plane change costs MORE than heading to the Moon.")
    print("\nConsequence: two ships in LEO in different planes are 'far apart'")
    print("even if they pass within meters. A buoy only helps craft that share")
    print("its plane. To blanket all planes you need a LOT of buoys (see #5).")


# ---------------------------------------------------------------------------
# 3. Phasing is nearly free — why nodes & convoys DO work
# ---------------------------------------------------------------------------
def phasing_is_cheap():
    hr("3.  PHASING IS (NEARLY) FREE — the loophole that saves the idea")
    r = R_LEO
    v = v_circ(MU_EARTH, r)
    T = 2 * math.pi * math.sqrt(r**3 / MU_EARTH)
    print(f"LEO period ~ {T/60:.1f} min.  To catch a buoy that's AHEAD of you on")
    print("your own orbit, drop to a slightly lower (faster) orbit, lap it, and")
    print("come back up. Cost depends only on how *fast* you want to catch up:\n")
    print("   catch-up time      approx round-trip Δv")
    # Drop apoapsis stays at r; lower periapsis so period shrinks enough to gain
    # the phase angle over N revs. Crude: dv to shift period by dT each way.
    for revs, desc in [(50, "~2.5 days (lazy)"),
                       (10, "~15 hours"),
                       (3,  "~4.5 hours (hurried)")]:
        # period of phasing orbit must be T*(1 - 1/revs) to gain one full lap
        # over `revs` revolutions; approximate single-rev catch handled similarly.
        T_phase = T * (1 - 1.0 / revs)
        a_phase = (MU_EARTH * (T_phase / (2 * math.pi))**2) ** (1.0 / 3.0)
        # vis-viva at r on the phasing ellipse (apoapsis = r):
        v_phase = math.sqrt(MU_EARTH * (2.0 / r - 1.0 / a_phase))
        dv = 2 * abs(v - v_phase)   # enter and exit the phasing orbit
        print(f"   {desc:18s}  {dv*1000:6.1f} m/s")
    print("\nCompare to km/s for plane changes. Staying on ONE orbit and just")
    print("waiting is the cheapest maneuver in spaceflight. THIS is why caches")
    print("belong at congregation points and on shared trajectories — places")
    print("where rescue collapses to a phasing problem, not a plane change.")


# ---------------------------------------------------------------------------
# 4. How far can a crippled ship even get?
# ---------------------------------------------------------------------------
def crippled_reach():
    hr("4.  REACHABLE SET — how far a half-dead ship can limp")
    r = R_LEO
    print(f"Starting circular at LEO ({LEO_ALT:.0f} km). With a one-shot prograde")
    print("budget left in the tank, the highest apoapsis you can coast to:\n")
    for dv in (0.05, 0.1, 0.2, 0.5, 1.0, 2.0):
        ra = reachable_apoapsis(MU_EARTH, r, dv)
        if math.isinf(ra):
            print(f"   {dv*1000:5.0f} m/s  ->  ESCAPE (you're leaving)")
        else:
            print(f"   {dv*1000:5.0f} m/s  ->  apoapsis {ra - R_EARTH:8.0f} km altitude")
    print("\nThe lesson: a near-dry ship can barely change its orbit. A useful")
    print("buoy is one already within a few hundred m/s of where you'll be —")
    print("which again means: on your trajectory, or at the node you're near.")


# ---------------------------------------------------------------------------
# 5. Boiloff — what you can actually keep in the cache
# ---------------------------------------------------------------------------
def boiloff():
    hr("5.  BOILOFF — what survives in a passive cache, and for how long")
    # Representative *passive* (MLI only, no cryocooler) boiloff rates, %/day.
    # Order-of-magnitude; real rates depend hugely on tank size & sun exposure.
    propellants = [
        ("Liquid hydrogen (LH2, 20 K)",  1.0,  "brutal: large surface heat leak"),
        ("Liquid methane (LCH4, 112 K)", 0.10, "manageable with good MLI"),
        ("Liquid oxygen (LOX, 90 K)",    0.10, "manageable"),
        ("Storables (N2H4, NTO/MMH)",    0.0,  "years-to-decades, no cooling"),
        ("Water / O2 & N2 gas / food",   0.0,  "indefinite if sealed"),
    ]
    print("Days to lose 10% / 50% of a passively-stored tank:\n")
    print(f"   {'commodity':32s} {'%/day':>6s}  {'-10%':>8s} {'-50%':>8s}")
    for name, rate, note in propellants:
        if rate == 0.0:
            d10 = d50 = "  stable"
        else:
            d10 = f"{10.0/rate:6.0f} d"
            d50 = f"{50.0/rate:6.0f} d"
        print(f"   {name:32s} {rate:5.2f}  {d10:>8s} {d50:>8s}   {note}")
    print("\nZero-boiloff (ZBO) cryocoolers can hold cryogens indefinitely, but")
    print("they need continuous POWER. Solar power scales as 1/r^2:")
    for label, r in [("Earth/Moon", AU), ("Mars", R_MARS_ORBIT),
                     ("Jupiter", R_JUP_ORBIT), ("Saturn", R_SAT_ORBIT)]:
        frac = (AU / r) ** 2
        print(f"   sunlight at {label:10s} = {frac*100:5.1f}% of Earth's")
    print("\nSo: cryogenic emergency caches are plausible in cislunar space with")
    print("big solar arrays, but past the asteroid belt a passive cache should")
    print("hold storables/water/gas, or carry a nuclear (RTG/fission) source.")


# ---------------------------------------------------------------------------
# 6. Coverage counting — how many buoys?
# ---------------------------------------------------------------------------
def coverage():
    hr("6.  COVERAGE — blanket the sky (hopeless) vs. cover the nodes (cheap)")
    print("To put a buoy within reach of ANY craft in LEO, you must sample the")
    print("space of orbital PLANES (inclination x RAAN), because plane changes")
    print("are unaffordable. In-plane phasing is free, so a few buoys per plane.\n")
    print(f"   {'plane resolution':18s} {'planes':>8s} {'x3 phased':>10s}")
    for res in (30, 20, 10, 5):
        n_incl = 180 // res          # inclination 0..180
        n_raan = 360 // res          # RAAN 0..360
        planes = n_incl * n_raan // 2  # symmetry: a plane is defined mod 180 RAAN
        print(f"   every {res:3d} deg       {planes:8d} {planes*3:10d}")
    print("\n...hundreds to thousands of buoys just for LEO. Now instead cover")
    print("only the places people actually are:\n")
    nodes = ["ISS / Tiangong plane (51.6 deg)", "Sun-synchronous (~98 deg)",
             "GEO belt", "EML1 depot", "EML2 / Gateway NRHO", "Low Lunar Orbit"]
    for n in nodes:
        print(f"   - {n}")
    print(f"\n   => ~{len(nodes)} nodes, a few caches each = a few dozen buoys total.")
    print("   The network is affordable ONLY if it follows traffic, not geometry.")


# ---------------------------------------------------------------------------
def main():
    print(__doc__)
    deltav_map()
    plane_change_tax()
    phasing_is_cheap()
    crippled_reach()
    boiloff()
    coverage()
    hr("BOTTOM LINE")
    print("""
  * Δv, not distance, is the metric. A crippled ship's reachable set is tiny.
  * Plane changes are unaffordable; phasing is nearly free. So caches must sit
    where rescue is a phasing problem: nodes (Lagrange pts, NRHO, parking
    orbits, GEO) and shared trajectories (breadcrumb convoys on the exact
    transfer a crew will fly).
  * On an open transfer corridor, the lifeboat must come to you — that's a
    rescue tug with its own propulsion, not a passive buoy.
  * Store storables, water, and gas for free; cryogens need power, and power
    in the outer system means nuclear.
  * Follow the traffic, not the geometry, and the buoy network costs dozens of
    units, not thousands.
    """)


if __name__ == "__main__":
    main()
