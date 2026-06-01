#!/usr/bin/env python3
"""
Tests for the solar-wind turbine model. Pure stdlib (no pytest). These assert the
PHYSICS — scaling laws, energy limits, the drag-turbine curve — so the model can't
silently go incoherent again (which is exactly what happened before).

    python3 test_turbine.py
"""

import math
import turbine as T

TESTS = []
def test(fn):
    TESTS.append(fn)
    return fn

def approx(a, b, rel=1e-6, msg=""):
    assert abs(a - b) <= rel * max(abs(a), abs(b), 1e-30), \
        f"{msg}: {a} != {b} (rel {rel})"


# --- environment -----------------------------------------------------------
@test
def density_falls_as_inverse_r2():
    approx(T.sw_number_density(2), T.sw_number_density(1) / 4, 1e-9,
           "density should be 1/r^2")
    approx(T.ram_pressure(3), T.ram_pressure(1) / 9, 1e-9, "ram ~ 1/r^2")


# --- sail scaling: the thing that was incoherent before --------------------
@test
def plasma_magnet_force_is_constant_with_distance():
    s = T.Sail(50_000, "plasma_magnet")
    f1, f10, f30 = s.force(1), s.force(10), s.force(30)
    approx(f1, f10, 1e-9, "plasma-magnet force must be flat")
    approx(f1, f30, 1e-9, "plasma-magnet force must be flat")

@test
def plasma_magnet_radius_grows_linearly():
    s = T.Sail(50_000, "plasma_magnet")
    approx(s.radius(10) / s.radius(1), 10.0, 1e-9, "R ∝ r")
    # so the bubble is NOT 50 km everywhere -- it's 500 km at 10 AU
    approx(s.radius(10), 500_000, 1e-9, "bubble must inflate with distance")

@test
def dipole_force_falls_as_r_minus_4_3():
    s = T.Sail(50_000, "dipole")
    approx(s.force(8) / s.force(1), 8 ** (-4 / 3), 1e-9, "dipole F ∝ r^-4/3")

@test
def dipole_radius_grows_as_cube_root():
    s = T.Sail(50_000, "dipole")
    approx(s.radius(27) / s.radius(1), 3.0, 1e-9, "dipole R ∝ r^(1/3)")


# --- extracted power -------------------------------------------------------
@test
def extracted_power_scales_with_bubble_area():
    # double the radius -> 4x the force -> 4x the power (same distance, tips)
    p1 = T.extracted_power(T.Sail(50_000).force(1), 1000)
    p2 = T.extracted_power(T.Sail(100_000).force(1), 1000)
    approx(p2 / p1, 4.0, 1e-9, "power ∝ R^2")

@test
def extracted_power_scales_with_tip_speed_when_slow():
    # at genuinely slow tips (lambda -> 0) the (1-lambda)^2 term vanishes and
    # P is linear in v_tip; at higher tips it falls slightly below linear.
    f = T.Sail(50_000).force(1)
    approx(T.extracted_power(f, 200) / T.extracted_power(f, 100), 2.0, 1e-3,
           "P ~ v_tip for slow tips")
    # and the (1-lambda)^2 correction makes faster tips sub-linear:
    assert T.extracted_power(f, 1000) / T.extracted_power(f, 500) < 2.0, \
        "faster tips should fall below linear (drag correction)"

@test
def extracted_never_exceeds_available_flux():
    # energy conservation: can't pull out more than the wind carries through it
    s = T.Sail(50_000)
    avail = T.energy_flux(1.0) * s.area(1.0)
    for vt in (100, 1000, 1e4, 1e5, 3e5):
        assert T.extracted_power(s.force(1), vt) <= avail + 1e-6, \
            f"extracted exceeds available flux at v_tip={vt}"

@test
def small_tip_limit_is_half_F_vtip():
    f = T.Sail(50_000).force(1)
    approx(T.extracted_power(f, 1000), 0.5 * f * 1000, 1e-2,
           "slow-tip limit P≈1/2 F v_tip")


# --- drag turbine curve ----------------------------------------------------
@test
def drag_cp_peaks_at_one_third():
    vrel = 400_000
    cp_opt = T.drag_cp(vrel / 3, vrel)
    approx(cp_opt, 4 * T.CD / 27, 1e-6, "Cp_max = 4Cd/27 at lambda=1/3")
    # and it's actually the max over a sweep
    best = max(T.drag_cp(vrel * lam, vrel) for lam in [i / 1000 for i in range(1, 1000)])
    approx(best, cp_opt, 1e-3, "lambda=1/3 is the maximum")

@test
def drag_cp_zero_when_tip_matches_wind():
    assert T.drag_cp(400_000, 400_000) == 0.0, "no power when tip = wind speed"
    assert T.drag_cp(500_000, 400_000) == 0.0, "no power when tip > wind"


# --- material limit --------------------------------------------------------
@test
def tip_speed_limit_matches_formula():
    m = T.MATERIALS[2]  # carbon fiber
    approx(T.tip_speed_limit(m, 2.0),
           math.sqrt(2 * (m.sigma_pa / 2.0) / m.rho), 1e-9, "v=sqrt(2 sigma/SF/rho)")


# --- net / self-powering ---------------------------------------------------
@test
def field_power_buys_radius_as_sixth_root():
    # doubling the bubble needs 2^6 = 64x the resistive coil power
    r1 = T.radius_from_field_power(1e3, 1.0)
    r2 = T.radius_from_field_power(64e3, 1.0)
    approx(r2 / r1, 2.0, 1e-6, "R ∝ P^(1/6): 64x power -> 2x radius")
    # round-trip
    approx(T.field_power_for_radius(T.radius_from_field_power(5e4, 1.0), 1.0),
           5e4, 1e-6, "field_power<->radius must invert")

@test
def resistive_field_bill_explodes_as_r6():
    # holding twice the bubble costs 64x the continuous power
    approx(T.field_power_for_radius(30_000) / T.field_power_for_radius(15_000),
           64.0, 1e-6, "resistive field power ∝ R^6")

@test
def m2p2_injection_cannot_self_power():
    # harvest density must be far below M2P2 injection cost
    rho = T.sw_mass_density(1.0)
    harvest = 0.5 * T.CD * rho * T.V_SW ** 2 * T.tip_speed_limit(T.MATERIALS[2])
    assert T.injection_density() > 5 * harvest, \
        "M2P2 injection should dwarf harvestable density"

@test
def superconducting_net_goes_positive_above_breakeven():
    vt = T.tip_speed_limit(T.MATERIALS[2])
    rho = T.sw_mass_density(1.0)
    hd = 0.5 * T.CD * rho * T.V_SW ** 2 * vt
    be = math.sqrt(2000.0 / (hd * math.pi))           # break-even radius
    small = T.net_power(T.Sail(be * 0.5), vt, 1.0, "superconducting", 2000.0)
    big = T.net_power(T.Sail(be * 2.0), vt, 1.0, "superconducting", 2000.0)
    assert small < 0 < big, f"net should cross zero at break-even ({small}, {big})"

@test
def net_power_flat_with_distance_for_plasma_magnet():
    s = T.Sail(200_000, "plasma_magnet")
    vt = T.tip_speed_limit(T.MATERIALS[2])
    # extracted is flat; bottle (superconducting) is fixed -> net flat
    n1 = T.net_power(s, vt, 1.0)
    n30 = T.net_power(s, vt, 30.0)
    approx(n1, n30, 1e-9, "plasma-magnet net should be flat with distance")


def run():
    passed = failed = 0
    for fn in TESTS:
        try:
            fn()
            print(f"  PASS  {fn.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"  FAIL  {fn.__name__}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    import sys
    sys.exit(0 if run() else 1)
