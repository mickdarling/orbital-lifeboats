#!/usr/bin/env python3
"""
Generate SVG figures for the solar-wind turbine into ./figures/.
Reuses the (generic) SVG plotter from the sibling orbital_lifeboats package.

    python3 figures.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from orbital_lifeboats import svgplot                      # noqa: E402
import turbine as T                                        # noqa: E402

OUT = os.path.join(os.path.dirname(__file__), "figures")


def f_power_vs_distance():
    t = T.Turbine()
    rs = [1 + i * 0.5 for i in range(0, 59)]               # 1..30 AU
    turb = [t.mech_power() / 1000 for _ in rs]             # flat (constant force)
    pv = [T.pv_power(r, 1000) / 1000 for r in rs]
    svgplot.line_chart(
        os.path.join(OUT, "01_power_vs_distance.svg"),
        [{"name": "solar-wind turbine (const. force)", "xs": rs, "ys": turb},
         {"name": "solar PV (1000 m², 30%)", "xs": rs, "ys": pv}],
        title="Power vs distance: turbine stays flat, PV craters",
        xlabel="distance from Sun (AU)", ylabel="power (kW)",
        ylog=True, ylim=(0.1, 600))


def f_power_vs_bubble():
    t = T.Turbine()
    radii = [50, 150, 300, 500, 1000, 1500]
    labels = [f"{r} km bubble" for r in radii]
    vals = [T.CAPTURE * T.bubble_force(r * 1000, t.ref_au) * t.tip_speed_ms / 1000
            for r in radii]                                # kW
    svgplot.barh(
        os.path.join(OUT, "02_power_vs_bubble.svg"), labels, vals,
        title="Extracted power vs bubble size (tip speed fixed at 1 km/s)",
        xlabel="mechanical power (kW)",
        value_fmt=lambda v: f"{v/1000:.1f} MW" if v >= 1000 else f"{v:.0f} kW")


def f_outbound():
    import math
    t = T.Turbine()
    area = math.pi * t.bubble_radius_m ** 2
    rho = T.sw_mass_density(t.ref_au)
    cpmax = 4 * T.CD / 27
    fs = [i / 200 for i in range(0, 199)]              # 0 .. 0.995
    cp_n, p_vals = [], []
    for f in fs:
        vr = T.relative_wind(f)
        cp = T.drag_cp(t.tip_speed_ms, vr)
        cp_n.append(cp / cpmax)
        p_vals.append(cp * 0.5 * rho * vr ** 3 * area)
    p0 = p_vals[0]
    p_n = [p / p0 for p in p_vals]
    svgplot.line_chart(
        os.path.join(OUT, "04_outbound_tradeoff.svg"),
        [{"name": "turbine efficiency (Cp / Cp_max)", "xs": fs, "ys": cp_n},
         {"name": "extracted power (P / P_max)", "xs": fs, "ys": p_n}],
        title="Riding outbound: efficiency climbs, absolute power collapses",
        xlabel="craft speed as fraction of wind speed",
        ylabel="fraction of maximum", ylim=(0, 1.05))


def f_material_limits():
    labels = [m.name for m in T.MATERIALS]
    vals = [T.tip_speed_limit(m, 2.0) / 1000 for m in T.MATERIALS]
    svgplot.barh(
        os.path.join(OUT, "03_material_tip_speed.svg"), labels, vals,
        title="Tip-speed limit by cable material (spinning-tether, SF=2)",
        xlabel="max tip speed (km/s)", value_fmt=lambda v: f"{v:.2f} km/s")


def main():
    os.makedirs(OUT, exist_ok=True)
    for fn in (f_power_vs_distance, f_power_vs_bubble, f_material_limits,
               f_outbound):
        fn()
        print(f"  wrote {fn.__name__}")
    print(f"figures in {OUT}/")


if __name__ == "__main__":
    main()
