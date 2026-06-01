#!/usr/bin/env python3
"""
Build the self-contained data page (index.html) for the solar-wind turbine.
Every number comes from turbine.py; the page also runs test_turbine.py and shows
the result, so you can see the physics is validated.

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
import turbine as T                            # noqa: E402
import test_turbine                            # noqa: E402

HERE = os.path.dirname(__file__)
BUBBLES_KM = [25, 50, 100, 200, 400]
P_FIXED = 2000.0


def table(headers, rows):
    h = "".join(f"<th>{c}</th>" for c in headers)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f"<table><thead><tr>{h}</tr></thead><tbody>{body}</tbody></table>"


def inline_svg(name):
    p = os.path.join(HERE, "figures", name)
    return f'<div class="svgwrap">{open(p).read()}</div>' if os.path.exists(p) else ""


def fig(name, cap):
    return f'<figure>{inline_svg(name)}<figcaption>{cap}</figcaption></figure>'


CSS = """
*{box-sizing:border-box}body{margin:0;font-family:-apple-system,Helvetica,Arial,
sans-serif;color:#1d2733;background:#fff;line-height:1.55}
.topbar{display:flex;align-items:center;gap:18px;padding:11px 22px;background:#0f172a;
color:#fff;font-size:14px}.topbar a{color:#fff;text-decoration:none;opacity:.92}
.topbar .title{color:#9fb4c7;font-weight:600}.topbar .spacer{flex:1}
main{max-width:900px;margin:0 auto;padding:28px 24px}
h1{font-size:28px;margin:.2em 0}h2{font-size:21px;margin:1.4em 0 .4em;
border-top:1px solid #e3e8ee;padding-top:.8em}
.tagline{color:#5b6b7b;font-size:16px}
table{border-collapse:collapse;width:100%;margin:1em 0;font-size:14px}
th,td{border:1px solid #e3e8ee;padding:6px 10px;text-align:left}th{background:#f7f9fb}
.callout{background:#eef6fb;border:1px solid #b9dcee;border-left:5px solid #2c7fb8;
border-radius:8px;padding:14px 18px;margin:1.2em 0}.callout b{color:#1c5a82}
.tests{background:#eefaf0;border:1px solid #bfe6c9;border-left:5px solid #2e9e54;
border-radius:8px;padding:10px 16px;margin:1em 0;font-size:14px}
code{background:#f7f9fb;padding:1px 5px;border-radius:4px;font:13px SFMono-Regular,Menlo,monospace}
figure{margin:18px 0;border:1px solid #e3e8ee;border-radius:10px;padding:14px;background:#f7f9fb}
.svgwrap svg{width:100%;height:auto;display:block}
figcaption{font-size:13px;color:#5b6b7b;margin-top:8px}
pre{background:#0f172a;color:#e2e8f0;padding:16px;border-radius:8px;overflow:auto;
font:12px SFMono-Regular,Menlo,monospace;line-height:1.4}
footer{border-top:1px solid #e3e8ee;padding:22px 24px;text-align:center;color:#5b6b7b;
font-size:13px;background:#f7f9fb;margin-top:2em}footer a{color:#2c7fb8;text-decoration:none}
"""


def build():
    materials = T.MATERIALS

    # extracted-power grid + net grid (plasma magnet, 1 AU)
    def grid_rows(net):
        rows = []
        for m in materials:
            vt = T.tip_speed_limit(m)
            cells = [f"{m.name} ({vt/1000:.2f} km/s)"]
            for bk in BUBBLES_KM:
                s = T.Sail(bk * 1000, "plasma_magnet")
                p = T.extracted_power(s.force(1.0), vt)
                if net:
                    p -= T.bottle_power(s.area(1.0), "superconducting", P_FIXED)
                cells.append(("+" if net and p >= 0 else "") + T.kw(p))
            rows.append(cells)
        return rows

    hdr = ["material (tip speed)"] + [f"{b} km" for b in BUBBLES_KM]

    # distance: both models
    vt_cf = T.tip_speed_limit(materials[2])
    s_pm, s_di = T.Sail(50_000, "plasma_magnet"), T.Sail(50_000, "dipole")
    dist_rows = []
    for r in (1, 5, 10, 30):
        dist_rows.append((f"{r} AU",
            f"{s_pm.radius(r)/1000:.0f} km / {s_pm.force(r):.1f} N / "
            f"{T.kw(T.extracted_power(s_pm.force(r), vt_cf))}",
            f"{s_di.radius(r)/1000:.0f} km / {s_di.force(r):.2f} N / "
            f"{T.kw(T.extracted_power(s_di.force(r), vt_cf))}"))

    # self-powering
    rho = T.sw_mass_density(1.0)
    hd = 0.5 * T.CD * rho * T.V_SW**2 * vt_cf
    idn = T.injection_density()
    be = math.sqrt(P_FIXED / (hd * math.pi))
    self_rows = [
        ("M2P2 (inject plasma; cost ∝ bubble)", f"{idn*1e6:.1f} µW/m²",
         f"{hd*1e6:.2f} µW/m²", f"NET NEGATIVE (~{idn/hd:.0f}× short)"),
        ("Plasma magnet (superconducting; fixed)", f"~{P_FIXED/1000:.0f} kW",
         "grows with bubble area", f"NET POSITIVE above ~{be/1000:.0f} km bubble"),
    ]

    # run the tests, capture result
    tbuf = io.StringIO()
    with contextlib.redirect_stdout(tbuf):
        ok = test_turbine.run()
    test_out = tbuf.getvalue()
    n_pass = test_out.count("PASS")
    test_banner = (f"✓ {n_pass} physics tests pass" if ok
                   else "✗ TESTS FAILING")

    # raw model run
    mbuf = io.StringIO()
    with contextlib.redirect_stdout(mbuf):
        T.main()
    raw = mbuf.getvalue()

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
<p class="tagline">Every number is computed by <code>turbine.py</code> on one
consistent physical model. <span class="tests" style="display:inline-block;padding:2px 8px">{test_banner}</span></p>

<div class="callout"><b>Is it kilowatts or megawatts?</b> Both — it's a <i>grid</i>,
not a single number. Power = ½·force·tip-speed; force scales with the bubble's
area, tip-speed with the cable material. Small bubble + weak cable → kW; big
bubble + strong cable → MW. The tables below are the whole answer, and the
distance behavior depends on which sail model you pick.</div>

<h2>Extracted power — material × bubble size (plasma magnet, 1 AU)</h2>
{table(hdr, grid_rows(net=False))}
{fig("01_net_power_grid.svg", "NET power over the same grid (extracted − bottle).")}

<h2>NET power — extracted minus the ~2 kW superconducting bottle</h2>
<p>Negative = the field costs more than the spin makes. This is the metric that
matters.</p>
{table(hdr, grid_rows(net=True))}

<h2>With distance — two sail models (and the bubble is NOT fixed-size)</h2>
<p>50 km bubble <i>at 1 AU</i>, carbon-fiber tips. Plasma-magnet bubble inflates
with distance (force flat, power flat); rigid dipole's force falls as r^−4/3.</p>
{table(["distance", "plasma magnet: R / F / P", "rigid dipole: R / F / P"], dist_rows)}
{fig("02_power_vs_distance.svg", "Plasma magnet flat (bubble inflates) vs dipole falling vs PV cratering.")}

<h2>Can it power its own bottles?</h2>
<p>Not free energy (wind pays); ideal magnetic deflection does no work, so a
perfect bottle costs ~0 to maintain. Whether it self-powers depends on the tech:</p>
{table(["bottle technology", "bottle power", "harvestable", "verdict"], self_rows)}

<h2>Riding outbound — efficiency up, absolute power down</h2>
{fig("04_outbound_tradeoff.svg", "Sailing out: efficiency climbs toward λ=1/3, absolute power collapses as v_rel³.")}

<h2>Tip-speed ceiling by material</h2>
{fig("03_material_tip_speed.svg", "The cable sets the tip-speed limit, hence one axis of the power grid.")}

<h2>Physics tests (run on every build)</h2>
<pre>{mdsite.html.escape(test_out)}</pre>

<h2>Full model run (raw <code>turbine.py</code> output)</h2>
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
