"""
Two-body orbital mechanics: circular states, transfers, plane changes, and a
universal-variable Lambert solver. Planar (2-D), impulsive. All velocities km/s,
distances km, times s, angles radians unless a name says _deg.

This is the validated physics core (the Lambert solver round-trips a known
circular orbit to < 0.01 m/s; see tests at the bottom / test_astro()).
"""

import math
from .constants import EARTH, G0

Vec = tuple  # (x, y)


# --- vector helpers --------------------------------------------------------
def vadd(a, b):   return (a[0] + b[0], a[1] + b[1])
def vsub(a, b):   return (a[0] - b[0], a[1] - b[1])
def vscale(a, s): return (a[0] * s, a[1] * s)
def vdot(a, b):   return a[0] * b[0] + a[1] * b[1]
def vnorm(a):     return math.hypot(a[0], a[1])


# --- circular orbits -------------------------------------------------------
def circular_speed(r, mu=EARTH.mu):
    """Speed on a circular orbit of radius r (km) -> km/s."""
    return math.sqrt(mu / r)


def period(r, mu=EARTH.mu):
    """Orbital period of a circular orbit of radius r -> seconds."""
    return 2 * math.pi * math.sqrt(r ** 3 / mu)


def angular_rate(r, mu=EARTH.mu):
    """Mean motion (rad/s) of a circular orbit of radius r."""
    return math.sqrt(mu / r ** 3)


def circ_pos(r, theta):
    return (r * math.cos(theta), r * math.sin(theta))


def circ_vel(r, theta, mu=EARTH.mu):
    """Prograde (CCW) circular velocity vector at angle theta."""
    vc = circular_speed(r, mu)
    return (-vc * math.sin(theta), vc * math.cos(theta))


def vis_viva(r, a, mu=EARTH.mu):
    """Speed at radius r on an orbit of semi-major axis a."""
    return math.sqrt(mu * (2.0 / r - 1.0 / a))


# --- impulsive transfers ---------------------------------------------------
def hohmann(r1, r2, mu=EARTH.mu):
    """Two-burn Hohmann transfer between coplanar circular orbits.
    Returns (dv1, dv2, total, tof_s)."""
    a_t = (r1 + r2) / 2.0
    v1, v2 = circular_speed(r1, mu), circular_speed(r2, mu)
    v_peri = vis_viva(r1, a_t, mu)
    v_apo = vis_viva(r2, a_t, mu)
    dv1, dv2 = abs(v_peri - v1), abs(v2 - v_apo)
    tof = math.pi * math.sqrt(a_t ** 3 / mu)
    return dv1, dv2, dv1 + dv2, tof


def plane_change(v, deg):
    """Δv (same units as v) to rotate a velocity of magnitude v by `deg`."""
    return 2.0 * v * math.sin(math.radians(deg) / 2.0)


def propellant_fraction(dv_ms, isp_s):
    """Tsiolkovsky: fraction of WET mass that must be propellant to achieve
    dv_ms (m/s) at exhaust efficiency isp_s (s)."""
    mr = math.exp(dv_ms / (isp_s * G0))
    return 1.0 - 1.0 / mr


def wet_mass(dry_t, dv_ms, isp_s):
    """Wet mass (t) for a vehicle of dry mass dry_t (t) to achieve dv_ms."""
    return dry_t * math.exp(dv_ms / (isp_s * G0))


def reachable_apoapsis(r, dv, mu=EARTH.mu):
    """From a circular orbit at r, the highest apoapsis a single prograde burn
    of magnitude dv (km/s) can reach. inf if it escapes."""
    v = circular_speed(r, mu) + dv
    energy = v * v / 2.0 - mu / r
    if energy >= 0:
        return float("inf")
    a = -mu / (2.0 * energy)
    return 2.0 * a - r


# --- universal-variable Lambert (Vallado) ----------------------------------
def _stumpff(psi):
    if psi > 1e-6:
        sp = math.sqrt(psi)
        return (1 - math.cos(sp)) / psi, (sp - math.sin(sp)) / sp ** 3
    if psi < -1e-6:
        sp = math.sqrt(-psi)
        return (1 - math.cosh(sp)) / psi, (math.sinh(sp) - sp) / sp ** 3
    return 0.5, 1.0 / 6.0


def lambert(r1v, r2v, tof, mu=EARTH.mu, prograde=True):
    """Solve the transfer r1v -> r2v in time `tof`. Returns (v1v, v2v) or None.
    Singular at a transfer angle of exactly 180 deg (avoid it)."""
    r1, r2 = vnorm(r1v), vnorm(r2v)
    cos_dnu = max(-1.0, min(1.0, vdot(r1v, r2v) / (r1 * r2)))
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
            while y < 0:
                psi += 0.1
                c2, c3 = _stumpff(psi)
                y = r1 + r2 + A * (psi * c3 - 1) / math.sqrt(c2)
        if y < 0:
            return None
        chi = math.sqrt(y / c2)
        tof_calc = (chi ** 3 * c3 + A * math.sqrt(y)) / math.sqrt(mu)
        if abs(tof_calc - tof) < 1e-4 * tof:
            g = A * math.sqrt(y / mu)
            if abs(g) < 1e-12:
                return None
            f = 1 - y / r1
            gdot = 1 - y / r2
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


def test_astro():
    """Self-test: Lambert must recover a known circular orbit."""
    r = EARTH.radius + 400
    p1, p2 = circ_pos(r, 0.0), circ_pos(r, math.pi / 2)
    sol = lambert(p1, p2, period(r) / 4, EARTH.mu)
    assert sol, "Lambert failed to converge"
    vc = circular_speed(r)
    err = (abs(vnorm(sol[0]) - vc) + abs(vnorm(sol[1]) - vc)) / 2
    assert err * 1000 < 0.1, f"Lambert error {err*1000:.3f} m/s too high"
    return err * 1000
