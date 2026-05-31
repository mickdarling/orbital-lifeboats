#!/usr/bin/env python3
"""
Generate the Orbital Lifeboats figure suite (pure stdlib -> SVG) into ./figures/,
write the figures-only gallery (figures/index.html), and build the integrated
site (index.html). Edit orbital_lifeboats/presets.py and re-run.

    python3 generate_figures.py
"""

import os
import math
from orbital_lifeboats import (constants as K, astro, reachability as R,
                               boiloff, failures, fleet, presets as P, svgplot,
                               figmeta)
import build_site

OUT = os.path.join(os.path.dirname(__file__), "figures")


def fig(name):
    return os.path.join(OUT, name)


def f_phasing_tradeoff():
    r = P.STATIONS[0].radius
    series = []
    for gap in (15, 40, 120, 180):
        opts = [o for o in R.phasing_options(r, gap) if o["time_s"] <= 24 * 3600]
        series.append({"name": f"{gap}° gap",
                       "xs": [o["time_s"] / 3600 for o in opts],
                       "ys": [o["dv_ms"] for o in opts]})
    svgplot.line_chart(
        fig("01_phasing_tradeoff.svg"), series,
        title="Phasing tradeoff (LEO): Δv vs time to rendezvous",
        xlabel="catch-up time (hours)", ylabel="Δv required (m/s)",
        ylim=(0, 700), markers=True,
        hlines=[{"y": 400, "label": "400 m/s budget", "color": "#c0392b"}],
        vlines=[{"x": 6, "label": "6 h clock", "color": "#c0392b"}])


def f_intercept_curve():
    r_v, r_b = K.EARTH.radius + 400, K.EARTH.radius + 1000
    floor_dv, t_hoh = R.hohmann_floor(r_b, r_v)
    pos_b, vel_b = astro.circ_pos(r_b, 0), astro.circ_vel(r_b, 0)
    th = math.radians(178)
    pos_v, vel_v = astro.circ_pos(r_v, th), astro.circ_vel(r_v, th)
    xs, ys = [], []
    for frac in [0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 1.0]:
        tof = frac * t_hoh
        best = None
        for pro in (True, False):
            sol = astro.lambert(pos_b, pos_v, tof, prograde=pro)
            if sol:
                dv = (astro.vnorm(astro.vsub(sol[0], vel_b)) +
                      astro.vnorm(astro.vsub(vel_v, sol[1])))
                best = dv if best is None else min(best, dv)
        if best:
            xs.append(tof / 3600)
            ys.append(best * 1000)
    svgplot.line_chart(
        fig("02_intercept_curve.svg"),
        [{"name": "intercept Δv", "xs": xs, "ys": ys}],
        title="Cross-orbit intercept (600 km gap): Δv vs transfer time",
        xlabel="transfer time (hours)", ylabel="Δv required (m/s)", markers=True,
        hlines=[{"y": floor_dv, "label": f"Hohmann floor {floor_dv:.0f} m/s",
                 "color": "#27ae60"}])


def f_reachability_heatmap():
    r = P.STATIONS[0].radius
    gaps = list(range(10, 181, 10))
    clocks = [1, 2, 3, 4, 6, 8, 12, 18, 24]
    grid = []
    for ch in clocks:
        row = []
        for g in gaps:
            opts = [o for o in R.phasing_options(r, g) if o["time_s"] <= ch * 3600]
            row.append(min(o["dv_ms"] for o in opts) if opts else None)
        grid.append(row)
    svgplot.heatmap(
        fig("03_reachability_heatmap.svg"), gaps, clocks, grid,
        title="Reachability (LEO): min rescue Δv (m/s)",
        xlabel="victim phase gap (degrees)", ylabel="life-support clock (hours)",
        cbar_label="Δv (m/s)", cmap=svgplot.viridis, vmax=800)


def f_period_floor():
    radii = [6778 + i * (60000 - 6778) / 60 for i in range(61)]
    svgplot.line_chart(
        fig("04_period_floor.svg"),
        [{"name": "period", "xs": radii, "ys": [astro.period(r) / 3600 for r in radii]}],
        title="Orbital period vs radius (Keplerian)",
        xlabel="orbit radius (km)", ylabel="period (hours)",
        ylog=True, ylim=(1, 40),
        hlines=[{"y": 6, "label": "6 h clock", "color": "#c0392b"}],
        vlines=[{"x": 6778, "label": "LEO", "color": "#888"},
                {"x": K.GEO_RADIUS, "label": "GEO", "color": "#888"}])


def f_boiloff():
    days = list(range(0, 366, 5))
    series = [{"name": c.name, "xs": days,
               "ys": [boiloff.fraction_remaining(c.boiloff_pct_day, d) * 100
                      for d in days]} for c in boiloff.COMMODITIES]
    svgplot.line_chart(
        fig("05_boiloff.svg"), series,
        title="Passive boiloff: tank remaining vs time",
        xlabel="days in storage", ylabel="tank remaining (%)", ylim=(0, 105))


def f_solar_power():
    bodies = [("Earth/Moon", 1.0), ("Mars", 1.524), ("Jupiter", 5.203),
              ("Saturn", 9.537)]
    svgplot.barh(
        fig("06_solar_power.svg"), [b[0] for b in bodies],
        [boiloff.solar_fraction(b[1]) * 100 for b in bodies],
        title="Sunlight vs heliocentric distance",
        xlabel="sunlight (% of Earth's)", value_fmt=lambda v: f"{v:.1f}%")


def f_failure_modes():
    fm = sorted(failures.FAILURE_MODES, key=lambda f: f.clock_h)
    catnames = sorted({f.category for f in fm})
    catcol = {c: svgplot.PALETTE[i % len(svgplot.PALETTE)]
              for i, c in enumerate(catnames)}
    svgplot.barh(
        fig("07_failure_modes.svg"), [f.name for f in fm], [f.clock_h for f in fm],
        colors=[catcol[f.category] for f in fm],
        legend_items=[(c, catcol[c]) for c in catnames],
        title="What we're rescuing: failure mode vs clock (hours)",
        xlabel="life-support clock (hours)", value_fmt=lambda v: f"{v:.0f} h")


def f_coverage_by_regime():
    clocks = list(range(1, 49))
    regimes = [("LEO (~93 min)", K.EARTH.radius + 400),
               ("MEO (~6 h)", K.EARTH.radius + 10000),
               ("GEO (~24 h)", K.GEO_RADIUS)]
    series = [{"name": nm, "xs": clocks,
               "ys": [R.max_reach_angle(ch, 400, r) for ch in clocks]}
              for nm, r in regimes]
    svgplot.line_chart(
        fig("08_coverage_by_regime.svg"), series,
        title="Coverage: reachable arc vs clock, by orbit",
        xlabel="life-support clock (hours)",
        ylabel="reachable phase arc (degrees)", ylim=(0, 185))


def f_program_cost():
    lean = fleet.size_lean(P.STATIONS)
    full = fleet.size_full(P.STATIONS)
    comps = ["Stage-1", "Stage-2", "Stage-3", "Launch", "Development"]
    data = {}
    for prog in (lean, full):
        s = prog.with_spares
        data[prog.label.split(":")[0]] = {
            "Stage-1": s.get(1, 0) * P.DEFAULT.unit_cost_b[1],
            "Stage-2": s.get(2, 0) * P.DEFAULT.unit_cost_b[2],
            "Stage-3": s.get(3, 0) * P.DEFAULT.unit_cost_b[3],
            "Launch": prog.cost_launch_b, "Development": prog.cost_dev_b}
    svgplot.stacked_bar(
        fig("09_program_cost.svg"), list(data.keys()), comps, data,
        title="Phase-1 cost breakdown", ylabel="cost ($B)",
        value_total_fmt=lambda v: f"${v:.1f}B")


def f_lifeboats_per_launch():
    lv = P.LAUNCHERS["Starship"]
    labels, vals = [], []
    for key in ("compact pod", "standard refuge", "reentry lifeboat"):
        lb = P.LIFEBOATS[key]
        r = fleet.lifeboats_per_launch(lv, lb)
        labels.append(f"{lb.name} — {r['seats']} seats")
        vals.append(r["n"])
    svgplot.barh(
        fig("10_lifeboats_per_launch.svg"), labels, vals,
        title="Lifeboats per Starship launch (~100 t to LEO, ~1000 m³)",
        xlabel="units per launch", value_fmt=lambda v: f"{int(v)}/launch")


def f_launch_cost():
    mass = fleet.size_full(P.STATIONS).mass_t
    order = ["Falcon 9", "Falcon Heavy", "Starship", "Starship (goal)"]
    svgplot.barh(
        fig("11_launch_cost_by_vehicle.svg"),
        [P.LAUNCHERS[k].name for k in order],
        [mass * P.LAUNCHERS[k].cost_b_per_t for k in order],
        title=f"Launch cost of the Phase-1 fleet (~{mass:.0f} t) by vehicle",
        xlabel="launch cost ($B)", value_fmt=lambda v: f"${v:.2f}B")


def write_gallery():
    rows = []
    for f in figmeta.FIGURES:
        rows.append(
            f'<figure><img src="{f["file"]}" alt="{f["title"]}"/>'
            f'<figcaption><b>{f["title"]}</b><br>{f["caption"]}</figcaption></figure>')
    html = f"""<!doctype html><meta charset="utf-8">
<title>Orbital Lifeboats — figures</title>
<style>
 body{{font-family:Helvetica,Arial,sans-serif;max-width:980px;margin:24px auto;
   padding:0 16px;color:#222;background:#fff}}
 figure{{margin:0 0 40px;border:1px solid #eee;border-radius:8px;padding:14px;
   background:#fafafa}}
 img{{width:100%;height:auto}} figcaption{{font-size:14px;color:#444;margin-top:8px}}
 p.note{{color:#666;font-size:13px}}
</style>
<h1>Orbital Lifeboats — figure suite</h1>
<p class="note">Generated by <code>generate_figures.py</code>. For the integrated
documentation + figures page, open <code>../index.html</code>.</p>
{''.join(rows)}
"""
    with open(os.path.join(OUT, "index.html"), "w") as fh:
        fh.write(html)


def main():
    os.makedirs(OUT, exist_ok=True)
    print(f"Lambert self-test OK (error {astro.test_astro():.4f} m/s)")
    for fn in (f_phasing_tradeoff, f_intercept_curve, f_reachability_heatmap,
               f_period_floor, f_boiloff, f_solar_power, f_failure_modes,
               f_coverage_by_regime, f_program_cost, f_lifeboats_per_launch,
               f_launch_cost):
        fn()
        print(f"  wrote {fn.__name__}")
    write_gallery()
    print(f"{len(figmeta.FIGURES)} figures + figures/index.html gallery")
    build_site.build()
    print("integrated site -> index.html")


if __name__ == "__main__":
    main()
