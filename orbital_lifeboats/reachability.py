"""
The two-budget rescue model: a rescue must satisfy Δv AND a life-support clock.

Two engines, picked by geometry:
  * phasing_*  — co-orbital rescue (buoy & victim share an orbit). Cheap but
                 quantized by orbital period.
  * lambert    — cross-orbit transfer (different orbits). Has a Δv floor and a
                 steep speed penalty.

All Δv returned in m/s, times in seconds, angles in degrees at the API edge.
"""

import math
from .constants import EARTH
from .astro import (circular_speed, period, angular_rate, vis_viva,
                    circ_pos, circ_vel, lambert, vnorm, vsub)


# --- co-orbital phasing ----------------------------------------------------
def phasing_options(r, dphi_deg, n_max=12, mu=EARTH.mu):
    """Buoy and victim share a circular orbit radius r; victim leads/lags by
    dphi_deg. The buoy drops into a phasing orbit, does N revs, and re-meets the
    victim (velocities match -> automatic docking).

    Returns list of dicts {revs, time_s, dv_ms} for N = 1..n_max. More revs =>
    less Δv but more time."""
    T = period(r, mu)
    vc = circular_speed(r, mu)
    frac = abs(dphi_deg) / 360.0
    out = []
    for n in range(1, n_max + 1):
        t_phase = T * (1 - frac / n)
        if t_phase <= 0:
            continue
        a_phase = (mu * (t_phase / (2 * math.pi)) ** 2) ** (1.0 / 3.0)
        under = 2.0 / r - 1.0 / a_phase
        if under <= 0:
            continue
        dv = 2.0 * abs(vc - math.sqrt(mu * under))
        out.append({"revs": n, "time_s": n * t_phase, "dv_ms": dv * 1000.0})
    return out


def phasing_best(r, dphi_deg, clock_h, budget_ms, mu=EARTH.mu):
    """Cheapest feasible phasing option within the clock & budget, or None."""
    clock_s = clock_h * 3600.0
    feas = [o for o in phasing_options(r, dphi_deg, mu=mu)
            if o["time_s"] <= clock_s and o["dv_ms"] <= budget_ms]
    return min(feas, key=lambda o: o["dv_ms"]) if feas else None


def max_reach_angle(clock_h, budget_ms, r, mu=EARTH.mu, dmax=179):
    """Largest co-orbital phase angle (deg) reachable within clock & budget."""
    best = 0
    for d in range(1, dmax + 1):
        if phasing_best(r, d, clock_h, budget_ms, mu):
            best = d
    return best


def responders_for_ring(clock_h, budget_ms, r, mu=EARTH.mu):
    """How many co-orbital responders to keep ANY point on the ring reachable."""
    ang = max_reach_angle(clock_h, budget_ms, r, mu)
    return math.ceil(360 / (2 * ang)) if ang > 0 else math.inf


# --- cross-orbit intercept (Lambert) ---------------------------------------
def intercept_curve(r_buoy, r_victim, lead_deg, tof_list, mu=EARTH.mu):
    """Buoy on circular r_buoy intercepts a victim on circular r_victim leading
    by lead_deg, for each time-of-flight in tof_list (s). The buoy carries all
    Δv (departs, then matches the victim's velocity to dock).

    Returns list of {tof_s, dv_ms} (skips non-converged TOFs)."""
    pos_b, vel_b = circ_pos(r_buoy, 0.0), circ_vel(r_buoy, 0.0, mu)
    w = angular_rate(r_victim, mu)
    out = []
    for tof in tof_list:
        th = math.radians(lead_deg) + w * tof
        pos_v, vel_v = circ_pos(r_victim, th), circ_vel(r_victim, th, mu)
        best = None
        for pro in (True, False):
            sol = lambert(pos_b, pos_v, tof, mu, prograde=pro)
            if sol:
                dv = vnorm(vsub(sol[0], vel_b)) + vnorm(vsub(vel_v, sol[1]))
                best = dv if best is None else min(best, dv)
        if best is not None:
            out.append({"tof_s": tof, "dv_ms": best * 1000.0})
    return out


def hohmann_floor(r_buoy, r_victim, mu=EARTH.mu):
    """The min-energy (Hohmann) Δv floor (m/s) and its transfer time (s)."""
    a_t = (r_buoy + r_victim) / 2.0
    dv = (abs(circular_speed(r_buoy, mu) - vis_viva(r_buoy, a_t, mu)) +
          abs(circular_speed(r_victim, mu) - vis_viva(r_victim, a_t, mu)))
    return dv * 1000.0, math.pi * math.sqrt(a_t ** 3 / mu)


# --- low-thrust feasibility ------------------------------------------------
def ion_time(dv_ms, accel=5e-4):
    """Lower-bound time (s) for an electric tug of acceleration `accel` (m/s^2)
    to deliver dv_ms (m/s)."""
    return dv_ms / accel


def ion_deliverable(time_s, accel=5e-4):
    """Δv (m/s) an electric tug can deliver in the available time."""
    return accel * time_s
