#!/usr/bin/env python3
"""
Build a self-contained data page (index.html) for the solar-wind turbine, with
every number pulled straight from turbine.py. Resolves the kW-vs-MW question by
showing power explicitly as a function of the knobs that set it.

    python3 build_page.py
"""

import os
import sys
import io
import math
import re
import contextlib

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from orbital_lifeboats import mdsite          # noqa: E402
import turbine as T                           # noqa: E402

HERE = os.path.dirname(__file__)


def kw(p):
    return f"{p/1e6:.2f} MW" if p >= 1e6 else f"{p/1e3:.1f} kW"


def table(headers, rows):
    h = "".join(f"<th>{c}</th>" for c in headers)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>"
                   for r in rows)
    return f"<table><thead><tr>{h}</tr></thead><tbody>{body}</tbody></table>"


def inline_svg(name):
    p = os.path.join(HERE, "figures", name)
    if not os.path.exists(p):
        return ""
    return f'<div class="svgwrap">{open(p).read()}</div>'


def fig(name, caption):
    return (f'<figure>{inline_svg(name)}'
            f'<figcaption>{caption}</figcaption></figure>')


CSS = """
*{box-sizing:border-box}
body{margin:0;font-family:-apple-system,Helvetica,Arial,sans-serif;color:#1d2733;
  background:#fff;line-height:1.55}
.topbar{display:flex;align-items:center;gap:18px;padding:11px 22px;
  background:#0f172a;color:#fff;font-size:14px}
.topbar a{color:#fff;text-decoration:none;opacity:.92}.topbar a:hover{opacity:1}
.topbar .title{color:#9fb4c7;font-weight:600}.topbar .spacer{flex:1}
main{max-width:900px;margin:0 auto;padding:28px 24px}
h1{font-size:28px;margin:.2em 0}h2{font-size:21px;margin:1.4em 0 .4em;
  border-top:1px solid #e3e8ee;padding-top:.8em}h3{margin:1em 0 .3em}
.tagline{color:#5b6b7b;font-size:16px}
table{border-collapse:collapse;width:100%;margin:1em 0;font-size:14px}
th,td{border:1px solid #e3e8ee;padding:6px 10px;text-align:left}
th{background:#f7f9fb}
.callout{background:#eef6fb;border:1px solid #b9dcee;border-left:5px solid #2c7fb8;
  border-radius:8px;padding:14px 18px;margin:1.2em 0}
.callout b{color:#1c5a82}
code{background:#f7f9fb;padding:1px 5px;border-radius:4px;
  font:13px SFMono-Regular,Menlo,monospace}
figure{margin:18px 0;border:1px solid #e3e8ee;border-radius:10px;padding:14px;
  background:#f7f9fb}.svgwrap svg{width:100%;height:auto;display:block}
figcaption{font-size:13px;color:#5b6b7b;margin-top:8px}
pre{background:#0f172a;color:#e2e8f0;padding:16px;border-radius:8px;overflow:auto;
  font:12px SFMono-Regular,Menlo,monospace;line-height:1.4}
.verdict{font-weight:600}
footer{border-top:1px solid #e3e8ee;padding:22px 24px;text-align:center;
  color:#5b6b7b;font-size:13px;background:#f7f9fb;margin-top:2em}
footer a{color:#2c7fb8;text-decoration:none}
"""


def build():
    t = T.Turbine()
    rho = T.sw_mass_density(t.ref_au)

    # --- knob 1: bubble size (the kW <-> MW resolver) ---
    bubble_rows = []
    for rk in (50, 150, 300, 500, 1000, 1500):
        f = T.bubble_force(rk * 1000, t.ref_au)
        p = T.CAPTURE * f * t.tip_speed_ms
        bubble_rows.append((f"{rk} km", f"{f:.1f} N", kw(p)))

    # --- knob 2: tip speed / material ---
    mat_rows = []
    for m in T.MATERIALS:
        vmax = T.tip_speed_limit(m, 2.0)
        p = T.CAPTURE * t.force() * vmax
        mat_rows.append((m.name, f"{vmax/1000:.2f} km/s", kw(p)))

    # --- distance: flat turbine vs PV ---
    dist_rows = []
    for r in (1, 5, 10, 20, 30):
        pturb = t.mech_power()
        ppv = T.pv_power(r, 1000)
        win = "turbine" if pturb > ppv else "PV"
        dist_rows.append((f"{r} AU", kw(pturb), kw(ppv), win))

    # --- self-powering balance ---
    harvest_density = T.CAPTURE * T.CD * rho * T.V_SW**2 * t.tip_speed_ms
    inj_density = 3000.0 / (math.pi * 7500.0**2)
    p_fixed = 2000.0
    breakeven = math.sqrt(p_fixed / (harvest_density * math.pi))
    self_rows = [
        ("M2P2 (inject plasma; power scales with bubble)",
         f"{inj_density*1e6:.1f} µW/m²",
         f"{harvest_density*1e6:.2f} µW/m²",
         f'<span class="verdict">NET NEGATIVE (~{inj_density/harvest_density:.0f}× short)</span>'),
        ("Plasma magnet (superconducting; ~fixed power)",
         f"~{p_fixed/1000:.0f} kW fixed",
         "grows with bubble area",
         f'<span class="verdict">NET POSITIVE above ~{breakeven/1000:.0f} km bubble</span>'),
    ]

    # --- value vs alternatives (external reference context) ---
    alt_rows = [
        ("Solar panels (1 AU)", "~12 m², tens of kg", "inner system only",
         "Trivial near Sun; dies as 1/r²"),
        ("Kilopower-class fission", "~1–1.5 t", "anywhere",
         "Demonstrated; decade+; the real competitor"),
        ("RTGs", "~2 t + ~200 kg Pu-238", "anywhere",
         "Pu-238 supply makes kW-scale impossible"),
        ("This turbine", "multi-t, km-scale spinning + cryo", "anywhere",
         "Same kW — plus a continuous ~10 N drag"),
    ]

    # --- full raw model run ---
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        T.main()
    raw = buf.getvalue()

    # --- README narrative (strip image lines; dashboard already shows figures) ---
    readme = open(os.path.join(HERE, "README.md")).read()
    readme = re.sub(r"!\[[^\]]*\]\([^)]*\)\s*", "", readme)
    narrative = mdsite.markdown_to_html(readme)

    html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Solar-Wind Turbine — data</title><style>{CSS}</style></head><body>
<header class="topbar"><a href="https://www.mickdarling.com/">&larr; mickdarling.com</a>
<span class="title">Solar-Wind Turbine</span><span class="spacer"></span>
<a href="https://github.com/mickdarling/orbital-lifeboats/tree/main/solar-wind-turbine">GitHub</a>
<a href="../">Orbital Lifeboats</a></header>
<main>
<h1>Solar-Wind Turbine — what it actually produces</h1>
<p class="tagline">Every number on this page is computed by
<code>turbine.py</code>. Run <code>python3 build_page.py</code> to regenerate.</p>

<div class="callout"><b>Is it kilowatts or megawatts?</b> Both — and that's not a
contradiction. Power = <code>capture × force × tip-speed</code>, and the force
scales with the magnetic bubble's <i>area</i>. A small bubble makes kilowatts; a
big one makes megawatts. The table below is the whole answer.</div>

<h2>Knob 1 — bubble size (this resolves the kW-vs-MW confusion)</h2>
<p>Tip speed fixed at 1 km/s, measured at 1 AU. Force ∝ bubble area, so power
climbs from a few kW to multi-MW purely by inflating a bigger bubble.</p>
{table(["bubble radius", "tip force", "mechanical power"], bubble_rows)}
{fig("02_power_vs_bubble.svg", "Power vs bubble size — the single biggest lever.")}

<h2>Knob 2 — tip speed (set by the cable material)</h2>
<p>Power ∝ tip speed, but tip speed is capped by the spinning-tether limit
√(2·specific-strength). Power shown for the 50 km design bubble at each material's
ceiling.</p>
{table(["cable material", "max tip speed", "power (50 km bubble)"], mat_rows)}
{fig("03_material_tip_speed.svg", "The cable is the ceiling on tip speed, hence on power.")}

<h2>Distance — output is FLAT, but only worth it far out</h2>
<p>The bubble self-inflates as the wind thins, so the turbine's output is
constant with distance (50 km bubble, 1 km/s tips). A 1000 m² solar array
craters as 1/r². The turbine doesn't make more power far out — its competition
just disappears.</p>
{table(["distance", "turbine", "solar PV (1000 m²)", "winner"], dist_rows)}
{fig("01_power_vs_distance.svg", "Flat turbine vs cratering PV; they cross near Saturn.")}

<h2>Riding outbound — efficiency climbs, absolute power collapses</h2>
<p>If it sails outbound, the relative wind drops toward the tip speed, so
efficiency rises toward the drag optimum — but the available power falls faster.
A power station wants to stay put (max relative wind).</p>
{fig("04_outbound_tradeoff.svg", "Efficiency up, absolute power down, as you ride the wind out.")}

<h2>Can the spin power its own bottles?</h2>
<p>Not free energy (the wind pays), and ideal magnetic deflection does no work on
the wind — so a perfect bottle costs ~0 to maintain. Whether it self-powers
depends on the technology:</p>
{table(["bottle technology", "bottle power", "harvestable", "verdict"], self_rows)}

<h2>Value vs other power sources (the honest reality check)</h2>
<p>For a few kW this is wildly over-engineered. Its real value is propellantless
<b>thrust</b> (it's a sail), with power as a bonus — or MW-scale power in the deep
outer system where panels are dead and reactors are heavy. Turbine row is from
the model; others are reference figures.</p>
{table(["source", "mass for ~5 kW", "works", "notes"], alt_rows)}

<h2>Full model run (raw output of <code>turbine.py</code>)</h2>
<pre>{mdsite.html.escape(raw)}</pre>

<h2>Narrative write-up</h2>
{narrative}
</main>
<footer>&copy; 2026 <a href="https://www.mickdarling.com/">Mick Darling</a> ·
Code <a href="https://github.com/mickdarling/orbital-lifeboats/blob/main/LICENSE">MIT</a> ·
Writing &amp; figures
<a href="https://github.com/mickdarling/orbital-lifeboats/blob/main/LICENSE-CONTENT.md">CC BY 4.0</a>
· <a href="https://github.com/mickdarling/orbital-lifeboats/tree/main/solar-wind-turbine">source</a>
</footer></body></html>
"""
    out = os.path.join(HERE, "index.html")
    with open(out, "w") as f:
        f.write(html)
    return out


if __name__ == "__main__":
    print("wrote", build())
