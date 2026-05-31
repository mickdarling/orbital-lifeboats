#!/usr/bin/env python3
"""
Build the integrated single-page site (index.html) that weaves the documentation
(README + notes/) together with the figures, inlined as SVG so the page is fully
self-contained — no runtime dependencies, works offline.

    python3 build_site.py          # (assumes figures/*.svg already exist)
    python3 generate_figures.py    # regenerates figures, then calls build()
"""

import os
import re
import glob
from orbital_lifeboats import mdsite, figmeta

ROOT = os.path.dirname(__file__)
NOTES_DIR = os.path.join(ROOT, "notes")
FIG_DIR = os.path.join(ROOT, "figures")


def _title_of(md, fallback):
    m = re.search(r"^#\s+(.*)$", md, re.M)
    return m.group(1) if m else fallback


def _note_number(path):
    m = re.match(r"(\d+)", os.path.basename(path))
    return int(m.group(1)) if m else 0


def _inline_svg(filename):
    p = os.path.join(FIG_DIR, filename)
    if not os.path.exists(p):
        return ""
    with open(p) as f:
        return f.read()


def _figure_block(fig):
    svg = _inline_svg(fig["file"])
    if not svg:
        return ""
    return (f'<figure class="fig"><div class="svgwrap">{svg}</div>'
            f'<figcaption><b>{fig["title"]}</b> — {fig["caption"]}</figcaption>'
            f'</figure>')


CSS = """
:root{--fg:#1d2733;--muted:#5b6b7b;--accent:#2c7fb8;--line:#e3e8ee;--bg:#ffffff;
  --panel:#f7f9fb}
*{box-sizing:border-box}
body{margin:0;font-family:-apple-system,Helvetica,Arial,sans-serif;color:var(--fg);
  background:var(--bg);line-height:1.55}
.layout{display:flex;align-items:flex-start;max-width:1180px;margin:0 auto}
nav.toc{position:sticky;top:0;align-self:flex-start;width:268px;height:100vh;
  overflow:auto;padding:24px 16px;border-right:1px solid var(--line);
  background:var(--panel);font-size:14px}
nav.toc h2{font-size:13px;text-transform:uppercase;letter-spacing:.05em;
  color:var(--muted);margin:18px 0 6px}
nav.toc a{display:block;color:var(--fg);text-decoration:none;padding:3px 0;
  border-left:2px solid transparent;padding-left:8px}
nav.toc a:hover{color:var(--accent);border-left-color:var(--accent)}
main{flex:1;min-width:0;padding:32px 40px;max-width:880px}
header.hero{padding:8px 0 4px}
header.hero h1{font-size:30px;margin:0 0 6px}
.tagline{color:var(--muted);font-size:16px;margin:0 0 8px}
section{padding:18px 0;border-top:1px solid var(--line)}
section#intro{border-top:none}
h1{font-size:26px;margin:.2em 0 .4em} h2{font-size:20px;margin:1.2em 0 .4em}
h3{font-size:16px;margin:1.1em 0 .3em}
p{margin:.6em 0} a{color:var(--accent)}
code{background:var(--panel);padding:1px 5px;border-radius:4px;
  font:13px/1.4 SFMono-Regular,Menlo,Consolas,monospace}
pre{background:#0f172a;color:#e2e8f0;padding:14px 16px;border-radius:8px;
  overflow:auto} pre code{background:none;color:inherit;padding:0}
blockquote{margin:.8em 0;padding:.4em 1em;border-left:4px solid var(--accent);
  background:var(--panel);color:#2b3a47}
table{border-collapse:collapse;width:100%;margin:1em 0;font-size:14px;display:block;
  overflow-x:auto}
th,td{border:1px solid var(--line);padding:6px 10px;text-align:left;
  vertical-align:top}
th{background:var(--panel)}
ul,ol{margin:.5em 0;padding-left:1.4em} li{margin:.2em 0}
hr{border:none;border-top:1px solid var(--line);margin:1.2em 0}
figure.fig{margin:22px 0;border:1px solid var(--line);border-radius:10px;
  padding:14px;background:var(--panel)}
.svgwrap svg{width:100%;height:auto;display:block}
figure.fig figcaption{font-size:13.5px;color:var(--muted);margin-top:10px}
.note-tag{display:inline-block;font-size:12px;color:#fff;background:var(--accent);
  border-radius:10px;padding:1px 9px;margin-right:8px;vertical-align:middle}
@media(max-width:820px){nav.toc{display:none}main{padding:20px}}
.topbar{display:flex;align-items:center;gap:18px;padding:11px 22px;
  background:#0f172a;color:#fff;font-size:14px}
.topbar a{color:#fff;text-decoration:none;opacity:.92}
.topbar a:hover{opacity:1;text-decoration:underline}
.topbar a.home{font-weight:600}
.topbar .title{color:#9fb4c7;font-weight:600}
.topbar .spacer{flex:1}
footer.sitefoot{border-top:1px solid var(--line);padding:22px 24px;
  text-align:center;color:var(--muted);font-size:13px;background:var(--panel)}
footer.sitefoot a{color:var(--accent);text-decoration:none}
footer.sitefoot a:hover{text-decoration:underline}
"""


def build():
    # collect docs: README first, then notes in order
    readme = open(os.path.join(ROOT, "README.md")).read()
    note_paths = sorted(glob.glob(os.path.join(NOTES_DIR, "*.md")),
                        key=_note_number)

    toc = ['<h2>Overview</h2>', '<a href="#intro">README — the concept</a>',
           '<h2>Design notes</h2>']
    sections = []

    # intro (strip the leading H1 + its italic tagline; the hero already shows them)
    readme_body = re.sub(r"\A#\s+.*\n", "", readme).lstrip("\n")
    readme_body = re.sub(r"\A\*.*?\*\s*", "", readme_body, flags=re.S).lstrip("\n")
    sections.append(f'<section id="intro">{mdsite.markdown_to_html(readme_body)}</section>')

    # notes, each followed by its figures
    for path in note_paths:
        n = _note_number(path)
        md = open(path).read()
        title = _title_of(md, os.path.basename(path))
        anchor = f"note-{n}"
        toc.append(f'<a href="#{anchor}">{title}</a>')
        body = mdsite.markdown_to_html(md)
        figs = "".join(_figure_block(f) for f in figmeta.for_note(n))
        sections.append(f'<section id="{anchor}"><span class="note-tag">'
                        f'note {n:02d}</span>{body}{figs}</section>')

    # a final all-figures gallery section
    toc.append('<h2>Figures</h2><a href="#figures">All figures</a>')
    gallery = "".join(_figure_block(f) for f in figmeta.FIGURES)
    sections.append(f'<section id="figures"><h1>All figures</h1>{gallery}</section>')

    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Orbital Lifeboats</title><style>{CSS}</style></head><body>
<header class="topbar">
<a class="home" href="https://www.mickdarling.com/">&larr; mickdarling.com</a>
<span class="title">Orbital Lifeboats</span><span class="spacer"></span>
<a href="https://github.com/mickdarling/orbital-lifeboats">GitHub</a></header>
<div class="layout">
<nav class="toc"><header class="hero"><h1>Orbital&nbsp;Lifeboats</h1></header>
{''.join(toc)}</nav>
<main><header class="hero"><h1>Orbital Lifeboats</h1>
<p class="tagline">Napkin math for a solar-system emergency-cache &amp; rescue
network — the WWII Channel rescue buoy, reimagined for spaceflight.</p></header>
{''.join(sections)}
<hr><p class="tagline">Generated from the <code>orbital_lifeboats</code> toolkit
(pure stdlib). Edit <code>presets.py</code> and run
<code>python3 generate_figures.py</code> to rebuild. Figures-only gallery:
<code>figures/index.html</code>.</p>
</main></div>
<footer class="sitefoot">
&copy; 2026 <a href="https://www.mickdarling.com/">Mick Darling</a> &nbsp;·&nbsp;
Code <a href="https://github.com/mickdarling/orbital-lifeboats/blob/main/LICENSE">MIT</a>
&nbsp;·&nbsp; Writing &amp; figures
<a href="https://github.com/mickdarling/orbital-lifeboats/blob/main/LICENSE-CONTENT.md">CC&nbsp;BY&nbsp;4.0</a>
&nbsp;·&nbsp; <a href="https://github.com/mickdarling/orbital-lifeboats">source on GitHub</a>
</footer>
</body></html>
"""
    out = os.path.join(ROOT, "index.html")
    with open(out, "w") as f:
        f.write(page)
    return out


if __name__ == "__main__":
    print("wrote", build())
