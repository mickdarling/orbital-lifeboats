#!/usr/bin/env python3
"""
Orbital Lifeboats — time-vs-Δv reachability.

The other scripts treat Δv as the only budget. It isn't. A rescue has to satisfy
TWO budgets at once:

  1. Δv     — can whoever is doing the moving afford the velocity change?
  2. TIME   — does the rendezvous finish before the life-support clock runs out?

The cruel part: in orbit the *cheap* maneuvers are the *slow* ones (drift and
phase), and the *fast* maneuvers are *expensive* (high-energy transfers). So a
buoy can be well within Δv reach and still be useless to a crew on a 36-hour
oxygen clock. This script maps that tradeoff.

Two engines, picked by geometry:
  * phasing_options()  — co-orbital rescue (buoy & victim share an orbit). The
                         dominant near-term case: safe-havens, breadcrumb caches.
  * lambert_*()        — cross-orbit transfer (buoy & victim on different orbits).

Two-body, planar, impulsive. Earth-centric (so LEO / MEO geometries are honest;
NRHO / EM-Lagrange cases are 3-body and only discussed, not computed — see notes).
Run:  python3 reachability.py
"""

import math

MU_EARTH = 398_600.0          # km^3/s^2
R_EARTH  = 6_378.0
R_LEO    = R_EARTH + 400.0     # 6778 km


def hr(t):
    print("\n" + "=" * 74 + f"\n{t}\n" + "=" * 74)


# ---------------------------------------------------------------------------
# tiny 2-D vector helpers (no numpy; stdlib only)
# ---------------------------------------------------------------------------
def vadd(a, b): return (a[0] + b[0], a[1] + b[1])
def vsub(a, b): return (a[0] - b[0], a[1] - b[1])
def vscale(a, s): return (a[0] * s, a[1] * s)
def vdot(a, b): return a[0] * b[0] + a[1] * b[1]
def vnorm(a): return math.hypot(a[0], a[1])


def circ_pos(r, theta):
    return (r * math.cos(theta), r * math.sin(theta))


def circ_vel(mu, r, theta):
    """Prograde (counter-clockwise) circular velocity at angle theta."""
    vc = math.sqrt(mu / r)
    return (-vc * math.sin(theta), vc * math.cos(theta))


# ---------------------------------------------------------------------------
# Engine 1 — co-orbital phasing (same circular orbit, different phase)
# ---------------------------------------------------------------------------
def phasing_options(mu, r, dphi_rad, n_max=12):
    """
    Buoy and victim share a circular orbit of radius r; the victim leads/lags the
    buoy by phase dphi_rad. The buoy drops into a phasing orbit, completes N revs,
    and re-meets the victim at the maneuver point (where velocities match, so
    docking is automatic).

    Returns a list of (time_s, dv_ms) options for N = 1..n_max. More revs => less
    Δv but more time: the whole tradeoff in one table.
    """
    T = 2 * math.pi * math.sqrt(r**3 / mu)
    vc = math.sqrt(mu / r)
    out = []
    frac = (dphi_rad / (2 * math.pi))          # fraction of a lap to make up
    for n in range(1, n_max + 1):
        # catch up: phasing period shorter by frac/n of an orbit
        t_phase = T * (1 - frac / n)
        if t_phase <= 0:
            continue
        a_phase = (mu * (t_phase / (2 * math.pi)) ** 2) ** (1.0 / 3.0)
        # r is the apoapsis of the (lower) phasing ellipse:
        under = 2.0 / r - 1.0 / a_phase
        if under <= 0:
            continue
        v_phase = math.sqrt(mu * under)
        dv = 2.0 * abs(vc - v_phase)           # enter + exit the phasing orbit
        out.append((n * t_phase, dv * 1000.0)) # seconds, m/s
    return out


# ---------------------------------------------------------------------------
# Engine 2 — universal-variable Lambert (cross-orbit transfer)
# ---------------------------------------------------------------------------
def _stumpff(psi):
    if psi > 1e-6:
        sp = math.sqrt(psi)
        c2 = (1 - math.cos(sp)) / psi
        c3 = (sp - math.sin(sp)) / (sp ** 3)
    elif psi < -1e-6:
        sp = math.sqrt(-psi)
        c2 = (1 - math.cosh(sp)) / psi
        c3 = (math.sinh(sp) - sp) / (sp ** 3)
    else:
        c2, c3 = 0.5, 1.0 / 6.0
    return c2, c3


def lambert(r1v, r2v, tof, mu, prograde=True):
    """
    Vallado universal-variable Lambert. Solves the transfer from r1v to r2v in
    time tof. Returns (v1v, v2v) or None if it doesn't converge. Singular at a
    transfer angle of exactly 180 deg (avoid it).
    """
    r1, r2 = vnorm(r1v), vnorm(r2v)
    cos_dnu = vdot(r1v, r2v) / (r1 * r2)
    cos_dnu = max(-1.0, min(1.0, cos_dnu))
    # 2-D "cross product" z-component picks the direction
    cross_z = r1v[0] * r2v[1] - r1v[1] * r2v[0]
    dnu = math.acos(cos_dnu)
    if (cross_z < 0 and prograde) or (cross_z > 0 and not prograde):
        dnu = 2 * math.pi - dnu
    tm = 1.0 if dnu < math.pi else -1.0
    A = tm * math.sqrt(r1 * r2 * (1 + cos_dnu))
    if abs(A) < 1e-9:
        return None

    psi, c2, c3 = 0.0, 0.5, 1.0 / 6.0
    psi_up, psi_lo = 4 * math.pi ** 2, -4 * math.pi
    for _ in range(200):
        y = r1 + r2 + A * (psi * c3 - 1) / math.sqrt(c2)
        if A > 0 and y < 0:
            # raise lower bound until y is positive
            while y < 0:
                psi += 0.1
                c2, c3 = _stumpff(psi)
                y = r1 + r2 + A * (psi * c3 - 1) / math.sqrt(c2)
        if y < 0:
            return None
        chi = math.sqrt(y / c2)
        tof_calc = (chi ** 3 * c3 + A * math.sqrt(y)) / math.sqrt(mu)
        if abs(tof_calc - tof) < 1e-4 * tof:
            f = 1 - y / r1
            g = A * math.sqrt(y / mu)
            gdot = 1 - y / r2
            if abs(g) < 1e-12:
                return None
            v1 = vscale(vsub(r2v, vscale(r1v, f)), 1.0 / g)
            v2 = vscale(vsub(vscale(r2v, gdot), r1v), 1.0 / g)
            return v1, v2
        if tof_calc <= tof:
            psi_lo = psi
        else:
            psi_up = psi
        psi = (psi_up + psi_lo) / 2.0
        c2, c3 = _stumpff(psi)
    return None


def cross_orbit_curve(mu, r_buoy, r_vic, lead_deg, tof_list):
    """
    Buoy on circular orbit r_buoy, victim on circular orbit r_vic leading the buoy
    by lead_deg at t=0. For each time-of-flight the buoy flies a Lambert transfer
    to where the victim WILL be, then matches the victim's velocity to dock.
    Returns list of (tof_s, dv_total_ms). The buoy carries all the Δv.
    """
    th_b = 0.0
    w_vic = math.sqrt(mu / r_vic ** 3)               # victim's angular rate
    pos_b = circ_pos(r_buoy, th_b)
    vel_b = circ_vel(mu, r_buoy, th_b)
    out = []
    for tof in tof_list:
        th_v = math.radians(lead_deg) + w_vic * tof  # victim's angle at arrival
        pos_v = circ_pos(r_vic, th_v)
        vel_v = circ_vel(mu, r_vic, th_v)
        best = None
        for pro in (True, False):
            sol = lambert(pos_b, pos_v, tof, mu, prograde=pro)
            if not sol:
                continue
            v1, v2 = sol
            dv = vnorm(vsub(v1, vel_b)) + vnorm(vsub(vel_v, v2))
            if best is None or dv < best:
                best = dv
        if best is not None:
            out.append((tof, best * 1000.0))
    return out


# ---------------------------------------------------------------------------
# Low-thrust (ion) feasibility — can a slow-push tug deliver Δv in time?
# ---------------------------------------------------------------------------
def ion_time(dv_ms, accel):
    """Crude lower bound on time for an electric tug of acceleration `accel`
    (m/s^2) to deliver dv_ms (m/s):  t = dv / a."""
    return dv_ms / accel


def max_reach_angle(clock_h, budget_ms, r, dmax=179):
    """Largest co-orbital phase angle (deg) a buoy with `budget_ms` of Δv can
    rescue within `clock_h` hours, via phasing on a circular orbit of radius r."""
    clock_s = clock_h * 3600
    best = 0
    for d in range(1, dmax + 1):
        opts = phasing_options(MU_EARTH, r, math.radians(d))
        if any(t <= clock_s and dv <= budget_ms for t, dv in opts):
            best = d
    return best


# ---------------------------------------------------------------------------
# self-test: Lambert must recover a known circular orbit (round trip)
# ---------------------------------------------------------------------------
def self_test():
    hr("0.  SELF-TEST — Lambert recovers a known circular orbit")
    # Two points 90 deg apart on a LEO circle, with the true quarter-period TOF.
    # Lambert should hand back the circular velocities at both ends.
    r = R_LEO
    T = 2 * math.pi * math.sqrt(r ** 3 / MU_EARTH)
    p1, p2 = circ_pos(r, 0.0), circ_pos(r, math.pi / 2)
    sol = lambert(p1, p2, T / 4, MU_EARTH, prograde=True)
    vc = math.sqrt(MU_EARTH / r)
    if sol:
        v1, v2 = sol
        print(f"  true circular speed     : {vc*1000:6.1f} m/s")
        print(f"  Lambert |v1|, |v2|      : {vnorm(v1)*1000:6.1f}, {vnorm(v2)*1000:6.1f} m/s")
        err = (abs(vnorm(v1) - vc) + abs(vnorm(v2) - vc)) / 2
        print(f"  mean error              : {err*1000:.2f} m/s  "
              f"({'OK — solver trusted' if err*1000 < 1 else 'CHECK SOLVER'})")
    else:
        print("  Lambert failed (check solver)")


# ---------------------------------------------------------------------------
# scenarios
# ---------------------------------------------------------------------------
def fmt_h(s): return f"{s/3600:5.2f} h"


def reach_phasing(title, clock_h, budget_ms, dphi_deg, r=R_LEO):
    """Print the phasing tradeoff table and the reachability verdict."""
    print(f"\n  {title}")
    print(f"    victim leads/lags buoy by {dphi_deg} deg on the same orbit; "
          f"clock {clock_h} h, buoy budget {budget_ms} m/s")
    opts = phasing_options(MU_EARTH, r, math.radians(dphi_deg))
    print(f"    {'revs':>4s} {'time':>8s} {'Δv (m/s)':>10s}   feasible?")
    clock_s = clock_h * 3600
    reachable = False
    for n, (t, dv) in enumerate(opts, start=1):
        ok = (t <= clock_s) and (dv <= budget_ms)
        if ok:
            reachable = True
        intime = "t ok" if t <= clock_s else "TOO SLOW"
        infuel = "Δv ok" if dv <= budget_ms else "TOO COSTLY"
        flag = "  <== RESCUE" if ok else ""
        print(f"    {n:>4d} {fmt_h(t):>8s} {dv:>10.0f}   {intime:>8s}/{infuel}{flag}")
    print(f"    VERDICT: {'REACHABLE' if reachable else 'NO RESCUE — victim is out of reach in time'}")
    return reachable


def main():
    print(__doc__)
    self_test()

    hr("1.  CO-ORBITAL RESCUE — the safe-haven / breadcrumb case (phasing)")
    print("A buoy sharing the victim's orbit. The buoy carries the Δv; docking")
    print("velocities match automatically. We sweep how far ahead/behind (deg) the")
    print("victim is, against different life-support clocks.\n")
    print("  --- short clock: HULL BREACH, crew in suits (~6 h of air) ---")
    reach_phasing("close buoy", 6, 400, 15)
    reach_phasing("medium gap", 6, 400, 40)
    reach_phasing("far gap",    6, 400, 120)

    print("\n  --- long clock: SLOW CONSUMABLES PROBLEM (~48 h) ---")
    reach_phasing("medium gap", 48, 400, 40)
    reach_phasing("far gap",    48, 400, 120)
    reach_phasing("half-orbit away", 48, 400, 180)

    hr("2.  CROSS-ORBIT RESCUE — buoy on a different orbit (Lambert)")
    print("Victim in LEO (400 km); buoy parked 600 km higher (1000 km alt). The")
    print("buoy descends to intercept a victim near opposition. Two lessons: there")
    print("is a Δv FLOOR (the min-energy / Hohmann transfer), and arriving FASTER")
    print("than that costs Δv steeply — exactly where a short clock hurts you.\n")
    r_v = R_LEO
    r_b = R_EARTH + 1000.0
    a_t = (r_b + r_v) / 2
    v_b, v_v = math.sqrt(MU_EARTH / r_b), math.sqrt(MU_EARTH / r_v)
    v_ap = math.sqrt(MU_EARTH * (2 / r_b - 1 / a_t))
    v_pe = math.sqrt(MU_EARTH * (2 / r_v - 1 / a_t))
    dv_floor = abs(v_b - v_ap) + abs(v_v - v_pe)
    t_hoh = math.pi * math.sqrt(a_t ** 3 / MU_EARTH)
    print(f"    min-energy (Hohmann) floor : {dv_floor*1000:5.0f} m/s "
          f"at {t_hoh/3600:.2f} h\n")
    # victim sits near opposition (178 deg), moving at circular velocity:
    pos_b, vel_b = circ_pos(r_b, 0.0), circ_vel(MU_EARTH, r_b, 0.0)
    th_v = math.radians(178.0)
    pos_v, vel_v = circ_pos(r_v, th_v), circ_vel(MU_EARTH, r_v, th_v)
    print(f"    {'time':>8s} {'Δv (m/s)':>10s}   {'vs floor':>9s}")
    for frac in (0.45, 0.55, 0.65, 0.75, 0.85, 1.0):
        tof = frac * t_hoh
        best = None
        for pro in (True, False):
            sol = lambert(pos_b, pos_v, tof, MU_EARTH, prograde=pro)
            if sol:
                v1, v2 = sol
                dv = vnorm(vsub(v1, vel_b)) + vnorm(vsub(vel_v, v2))
                best = dv if best is None else min(best, dv)
        if best is not None:
            mult = best / dv_floor
            print(f"    {fmt_h(tof):>8s} {best*1000:>10.0f}   {mult:>7.1f}x")
    print("\n    Halving the transfer time multiplies the Δv several-fold. A buoy")
    print("    on a *different* orbit is a luxury rescue — fine for a long clock,")
    print("    out of reach for a short one. Co-orbital (section 1) is the way.")

    hr("3.  WHY ION CAN'T FIRST-RESPOND")
    print("Electric/ion propulsion is the buoy's repositioning engine (notes 07/08).")
    print("But its acceleration is tiny, so delivering rescue Δv takes a long time:\n")
    a_ion = 5e-4   # m/s^2 — a fairly muscular electric tug
    print(f"    (assuming a = {a_ion} m/s^2, a generous electric tug)")
    print(f"    {'Δv needed':>10s} {'ion time':>12s}")
    for dv in (100, 300, 1000):
        t = ion_time(dv, a_ion)
        print(f"    {dv:>8d} m/s {t/3600:>9.1f} h  ({t/86400:.1f} days)")
    print("\n    A 100 m/s nudge takes ion ~2.3 DAYS. Against a 6-hour suit clock")
    print("    that's hopeless. Ion repositions the reserve BETWEEN emergencies;")
    print("    the emergency itself needs CHEMICAL Δv, pre-staged CLOSE. See notes/09.")

    hr("4.  THE TIME FLOOR SCALES WITH ORBIT — and it sets the buoy count")
    print("Phasing can't beat ~1 revolution, so the orbital PERIOD is a hard floor")
    print("on how fast a co-orbital rescue can happen. That floor explodes with")
    print("altitude:\n")
    periods = [("LEO (400 km)", R_LEO), ("orbit @ 1000 km", R_EARTH + 1000),
               ("GEO", 42164.0)]
    print(f"    {'orbit':18s} {'period':>10s}   short-clock (6 h) phasing rescue?")
    for label, r in periods:
        T = 2 * math.pi * math.sqrt(r ** 3 / MU_EARTH) / 3600
        verdict = "yes (~%.1f revs fit)" % (6 / T) if T < 6 else "NO — <1 rev fits"
        print(f"    {label:18s} {T:>8.2f} h   {verdict}")
    print(f"    {'NRHO (3-body)':18s} {'~6.5 days':>10s}   NO — 1 rev >> any short clock")
    print("\n  => At GEO and NRHO a co-orbital buoy can't phase in time for a short")
    print("  clock. Short-clock survival there means a buoy DOCKED/formation-flying")
    print("  with the crewed asset (zero phasing), not 'nearby in the orbit.'\n")

    print("  How many co-orbital buoys to keep any point within reach (LEO):")
    print(f"    {'clock':>7s} {'budget':>8s} {'max reach':>10s} {'buoys/orbit':>12s}")
    for clock_h, budget in [(6, 400), (24, 400), (48, 400)]:
        ang = max_reach_angle(clock_h, budget, R_LEO)
        n = math.ceil(360 / (2 * ang)) if ang > 0 else float("inf")
        print(f"    {clock_h:>5d} h {budget:>6d} m/s {ang:>8d} deg {n:>12}")
    print("\n  The SHORTEST clock you insure against sets the spacing -> the count.")

    hr("5.  ECHELONED RESPONSE — stage 1 buys TIME, which unlocks everyone else")
    print("The single-buoy bind: it had to be close+fast+light AND heavy+complete.")
    print("A staged 'triage swarm' breaks it. Stage 1's product isn't supplies —")
    print("it's TIME. Watch what extending the clock does to reachability.\n")
    a6 = max_reach_angle(6, 400, R_LEO)
    print(f"  STAGE 1 ('Connect') must arrive on the RAW clock.")
    print(f"    LEO, 6 h, 400 m/s: reaches a co-orbital victim within ~{a6} deg")
    print(f"    (or it's a formation lifeboat already alongside). It delivers")
    print(f"    emergency O2/power/pressure and buys, say, +5 days of life support.\n")
    ext_h = 120
    print(f"  AFTER STABILIZATION the clock is now ~{ext_h} h. Suddenly:")
    full = max_reach_angle(ext_h, 400, R_LEO)
    print(f"    - co-orbital phasing covers the FULL ring (~{full} deg) at low Δv")
    for a in (5e-4, 1e-3):
        dv = a * ext_h * 3600
        print(f"    - an ion tug (a={a} m/s^2) can now deliver ~{dv:.0f} m/s "
              f"-> it can reposition from a node")
    print(f"    - cross-orbit Hohmann transfers (hours, ~hundreds of m/s) now fit")
    print("\n  So stage 1 converts an unsolvable 6-hour problem into a solvable")
    print("  multi-day one. Stages 2 (resupply) and 3 (recovery/return) ride the")
    print("  extended clock in from farther away. Triage, then stabilize, then")
    print("  recover. See notes/10-triage-swarm.md.")

    hr("6.  PRE-POSITIONING AT A PLANNED BURN — defeating the clock in advance")
    print("Most crewed activity is SCHEDULED, and a risky burn (TLI, orbit")
    print("insertion) fails into a PREDICTABLE set of states. So pre-place a stage-1")
    print("at the nominal post-burn trajectory: a dispersed casualty departs at only")
    print("~the burn error (delta), and their separation grows ~delta * t.\n")
    print(f"    {'burn error':>11s} {'sep @1h':>9s} {'sep @6h':>9s}   rescue character")
    for dv_err in (10, 30, 100):
        s1 = dv_err * 3600 / 1000.0
        s6 = dv_err * 6 * 3600 / 1000.0
        print(f"    {dv_err:>8d} m/s {s1:>7.0f} km {s6:>7.0f} km   "
              "stays close for hours -> easy catch")
    print("\n  So for a PARTIAL/dispersed failure, a co-located stage-1 with a few")
    print("  tens-to-hundreds of m/s catches the casualty trivially, well inside any")
    print("  clock. Pre-positioning converts an unpredictable rescue into a planned")
    print("  rendezvous.\n")
    print("  The exception is TOTAL engine failure: the ship stays on its ORIGINAL")
    print("  pre-burn trajectory, far from the nominal one. That needs a SEPARATE")
    print("  'no-burn' guardian pre-staged there (the free-return station). Hence the")
    print("  geometry: fore/aft (energy errors), sides (pointing errors), plus a")
    print("  no-burn guardian. Cheap, and expendable. See notes/11-prepositioning.md.")

    hr("BOTTOM LINE")
    print("""
  * Rescue must satisfy Δv AND time. The clock usually binds first.
  * Co-orbital phasing is cheap but QUANTIZED by orbit period: you cannot
    rendezvous faster than ~1 revolution, so if the clock is shorter than a
    period (or a few), the only reachable buoys are the ones already very near.
  * Cross-orbit transfers have a Δv floor (Hohmann) AND a time floor; buying
    speed costs Δv fast. There is a knee, and short clocks sit on the wrong side.
  * Ion cannot first-respond (days to deliver rescue Δv). Chemical only, for the
    emergency burn. Ion is for repositioning the fleet between calls.
  * => This splits the fleet and tightens placement. See notes/09-reachability.md.
    """)


if __name__ == "__main__":
    main()
