#!/usr/bin/env python3
"""
Generate SVG figures for the (rebuilt) solar-wind turbine into ./figures/.
Reuses the generic SVG plotter from the sibling orbital_lifeboats package.

    python3 figures.py
"""

import os
import sys
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from orbital_lifeboats import svgplot                      # noqa: E402
import turbine as T                                        # noqa: E402

OUT = os.path.join(os.path.dirname(__file__), "figures")
BUBBLES_KM = [25, 50, 100, 200, 400]
P_FIXED = 2000.0


def f_net_power_grid():
    """Heatmap: net power over (bubble size x tip speed). The centerpiece."""
    xs = BUBBLES_KM
    ys = [round(T.tip_speed_limit(m) / 1000, 2) for m in T.MATERIALS]  # km/s
    grid = []
    for vt_kms in ys:
        row = []
        for bk in xs:
            s = T.Sail(bk * 1000, "plasma_magnet")
            net = (T.extracted_power(s.force(1.0), vt_kms * 1000)
                   - T.bottle_power(s.area(1.0), "superconducting", P_FIXED))
            row.append(net / 1000.0)                       # kW
        grid.append(row)
    svgplot.heatmap(
        os.path.join(OUT, "01_net_power_grid.svg"), xs, ys, grid,
        title="NET power (kW): bubble size x tip speed  [plasma magnet, 1 AU]",
        xlabel="bubble radius at 1 AU (km)",
        ylabel="tip speed (km/s) — by material",
        cbar_label="net kW", cmap=svgplot.viridis,
        annotate=lambda v: f"{v:.0f}")


def f_power_vs_distance():
    """Two sail models: plasma magnet (flat) vs rigid dipole (falls)."""
    vt = T.tip_speed_limit(T.MATERIALS[2])                 # carbon fiber
    rs = [1 + i * 0.5 for i in range(0, 59)]
    pm = [T.extracted_power(T.Sail(50_000, "plasma_magnet").force(r), vt) / 1000
          for r in rs]
    di = [T.extracted_power(T.Sail(50_000, "dipole").force(r), vt) / 1000
          for r in rs]
    pv = [T.SOLAR_CONST_1AU / r**2 * 0.3 * 1000 / 1000 for r in rs]
    svgplot.line_chart(
        os.path.join(OUT, "02_power_vs_distance.svg"),
        [{"name": "plasma magnet (bubble inflates → flat)", "xs": rs, "ys": pm},
         {"name": "rigid dipole (force ∝ r^-4/3)", "xs": rs, "ys": di},
         {"name": "solar PV (1000 m²)", "xs": rs, "ys": pv}],
        title="Power vs distance (50 km bubble @1 AU, carbon-fiber tips)",
        xlabel="distance from Sun (AU)", ylabel="power (kW)",
        ylog=True, ylim=(0.1, 600))


def f_material_limits():
    labels = [m.name for m in T.MATERIALS]
    vals = [T.tip_speed_limit(m) / 1000 for m in T.MATERIALS]
    svgplot.barh(
        os.path.join(OUT, "03_material_tip_speed.svg"), labels, vals,
        title="Tip-speed limit by cable material (spinning-tether, SF=2)",
        xlabel="max tip speed (km/s)", value_fmt=lambda v: f"{v:.2f} km/s")


def f_outbound():
    F, vt = 100.0, 1000.0                                  # representative
    fs = [i / 200 for i in range(0, 199)]                  # 0..0.995
    cpmax = 4 * T.CD / 27
    cp_n = [T.drag_cp(vt, T.V_SW * (1 - f)) / cpmax for f in fs]
    p = [T.extracted_power(F, vt, T.V_SW * (1 - f)) for f in fs]
    p_n = [pi / p[0] for pi in p]
    svgplot.line_chart(
        os.path.join(OUT, "04_outbound_tradeoff.svg"),
        [{"name": "efficiency (Cp / Cp_max)", "xs": fs, "ys": cp_n},
         {"name": "extracted power (P / P_max)", "xs": fs, "ys": p_n}],
        title="Riding outbound: efficiency climbs, absolute power collapses",
        xlabel="craft speed as fraction of wind speed",
        ylabel="fraction of maximum", ylim=(0, 1.05))


def f_field_power():
    """How you pay for bubble size: resistive (∝R^6, craters) vs superconducting."""
    vt = T.tip_speed_limit(T.MATERIALS[2])
    Rs_km = list(range(5, 151, 5))
    def pext(R):
        return T.extracted_power(T.CD * T.ram_pressure(1.0) * math.pi * R**2, vt)
    resistive = [(pext(rk*1000) - T.field_power_for_radius(rk*1000)) / 1000
                 for rk in Rs_km]
    sc = [(pext(rk*1000) - 2000) / 1000 for rk in Rs_km]
    svgplot.line_chart(
        os.path.join(OUT, "05_field_power_tradeoff.svg"),
        [{"name": "resistive coil (field bill ∝ R⁶)", "xs": Rs_km, "ys": resistive},
         {"name": "superconducting (field held ~free)", "xs": Rs_km, "ys": sc}],
        title="Net power vs bubble size: how you pay to inflate it",
        xlabel="bubble radius at 1 AU (km)", ylabel="net power (kW)",
        ylim=(-60, 160),
        hlines=[{"y": 0, "label": "break-even", "color": "#888"}])


def f_optimal_size():
    vt = T.tip_speed_limit(T.MATERIALS[2])
    Rs_km = [r * 0.5 for r in range(6, 29)]            # 3 .. 14 km
    def net_res(R):
        F = T.CD * T.ram_pressure(1.0) * math.pi * R ** 2
        return T.extracted_power(F, vt) - T.field_power_for_radius(R, 1.0)
    ys = [net_res(rk * 1000) for rk in Rs_km]
    ropt = T.optimal_radius_resistive(1.0, vt) / 1000
    svgplot.line_chart(
        os.path.join(OUT, "06_optimal_size.svg"),
        [{"name": "net power (resistive coil, 1 AU)", "xs": Rs_km, "ys": ys}],
        title="Optimal bubble size (resistive coil): net peaks, then craters",
        xlabel="bubble radius at 1 AU (km)", ylabel="net power (W)",
        ylim=(-1500, 300), markers=True,
        vlines=[{"x": ropt, "label": f"optimum ~{ropt:.0f} km", "color": "#c0392b"}],
        hlines=[{"y": 0, "label": "break-even", "color": "#888"}])


def main():
    os.makedirs(OUT, exist_ok=True)
    for fn in (f_net_power_grid, f_power_vs_distance, f_material_limits, f_outbound,
               f_field_power, f_optimal_size):
        fn()
        print(f"  wrote {fn.__name__}")
    print(f"figures in {OUT}/")


if __name__ == "__main__":
    main()
