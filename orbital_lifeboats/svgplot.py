"""
Minimal dependency-free SVG charting: line charts, heatmaps, horizontal bars,
and stacked bars. Not a general plotting library — just enough to draw clean,
labelled figures that open in any browser. Output is plain .svg text.
"""

import math
import html

PALETTE = ["#2c7fb8", "#d95f02", "#1b9e77", "#7570b3", "#e7298a",
           "#66a61e", "#e6ab02", "#a6761d"]


# --- low-level canvas ------------------------------------------------------
class Canvas:
    def __init__(self, w=820, h=520, pad=(70, 30, 60, 70)):
        # pad = (left, right, top, bottom)
        self.w, self.h = w, h
        self.l, self.r, self.t, self.b = pad
        self.el = []
        self.px0, self.px1 = self.l, w - self.r
        self.py0, self.py1 = self.t, h - self.b   # py0 top, py1 bottom
        self.xlim = (0, 1)
        self.ylim = (0, 1)
        self.xlog = self.ylog = False

    # data -> pixel
    def X(self, x):
        a, b = self.xlim
        if self.xlog:
            x, a, b = math.log10(x), math.log10(a), math.log10(b)
        return self.px0 + (x - a) / (b - a) * (self.px1 - self.px0)

    def Y(self, y):
        a, b = self.ylim
        if self.ylog:
            y, a, b = math.log10(max(y, 1e-9)), math.log10(a), math.log10(b)
        return self.py1 - (y - a) / (b - a) * (self.py1 - self.py0)

    def add(self, s):
        self.el.append(s)

    def text(self, x, y, s, size=13, anchor="middle", fill="#222", rot=None,
             weight="normal"):
        tr = f' transform="rotate({rot} {x} {y})"' if rot is not None else ""
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" '
                 f'font-family="Helvetica,Arial,sans-serif" text-anchor="{anchor}" '
                 f'fill="{fill}" font-weight="{weight}"{tr}>{html.escape(s)}</text>')

    def line(self, x1, y1, x2, y2, stroke="#888", w=1, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                 f'stroke="{stroke}" stroke-width="{w}"{d}/>')

    def rect(self, x, y, w, h, fill, stroke="none", sw=0):
        self.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
                 f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

    def polyline(self, pts, stroke, w=2.2, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        self.add(f'<polyline points="{p}" fill="none" stroke="{stroke}" '
                 f'stroke-width="{w}"{d}/>')

    def dot(self, x, y, r, fill):
        self.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}"/>')

    def frame_and_grid(self, xticks, yticks, xfmt, yfmt):
        self.rect(self.px0, self.py0, self.px1 - self.px0, self.py1 - self.py0,
                  "#fff", "#ccc", 1)
        for xt in xticks:
            px = self.X(xt)
            self.line(px, self.py0, px, self.py1, "#eee", 1)
            self.line(px, self.py1, px, self.py1 + 5, "#888", 1)
            self.text(px, self.py1 + 18, xfmt(xt), 11)
        for yt in yticks:
            py = self.Y(yt)
            self.line(self.px0, py, self.px1, py, "#eee", 1)
            self.line(self.px0 - 5, py, self.px0, py, "#888", 1)
            self.text(self.px0 - 9, py + 4, yfmt(yt), 11, "end")

    def labels(self, title, xlabel, ylabel):
        self.text((self.px0 + self.px1) / 2, self.py0 - 12, title, 16,
                  weight="bold")
        self.text((self.px0 + self.px1) / 2, self.h - 16, xlabel, 13)
        self.text(18, (self.py0 + self.py1) / 2, ylabel, 13, rot=-90)

    def legend(self, items, x=None, y=None):
        # items: list of (label, color)
        x = self.px1 - 150 if x is None else x
        y = self.py0 + 12 if y is None else y
        self.rect(x - 8, y - 14, 158, 18 * len(items) + 8, "#ffffffcc", "#ddd", 1)
        for i, (lab, col) in enumerate(items):
            yy = y + i * 18
            self.line(x, yy, x + 22, yy, col, 3)
            self.text(x + 28, yy + 4, lab, 11, "start")

    def save(self, path):
        body = "\n".join(self.el)
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" '
               f'height="{self.h}" viewBox="0 0 {self.w} {self.h}">\n'
               f'<rect width="{self.w}" height="{self.h}" fill="#fafafa"/>\n'
               f'{body}\n</svg>\n')
        with open(path, "w") as f:
            f.write(svg)


# --- nice ticks ------------------------------------------------------------
def nice_ticks(lo, hi, n=6):
    if hi <= lo:
        hi = lo + 1
    raw = (hi - lo) / n
    mag = 10 ** math.floor(math.log10(raw))
    for m in (1, 2, 2.5, 5, 10):
        if raw <= m * mag:
            step = m * mag
            break
    start = math.ceil(lo / step) * step
    ticks, v = [], start
    while v <= hi + step * 1e-6:
        ticks.append(round(v, 10))
        v += step
    return ticks


def log_ticks(lo, hi):
    t = []
    e = math.floor(math.log10(lo))
    while 10 ** e <= hi * 1.0001:
        if 10 ** e >= lo * 0.9999:
            t.append(10 ** e)
        e += 1
    return t


# --- colormaps -------------------------------------------------------------
def _lerp(stops, t):
    t = max(0.0, min(1.0, t))
    n = len(stops) - 1
    i = min(int(t * n), n - 1)
    f = t * n - i
    c0, c1 = stops[i], stops[i + 1]
    rgb = [round(c0[k] + (c1[k] - c0[k]) * f) for k in range(3)]
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"


_VIRIDIS = [(68, 1, 84), (59, 82, 139), (33, 145, 140), (94, 201, 98),
            (253, 231, 37)]
_RDYLGN = [(215, 48, 39), (255, 255, 191), (26, 152, 80)]   # red->yellow->green


def viridis(t):  return _lerp(_VIRIDIS, t)
def rdylgn(t):   return _lerp(_RDYLGN, t)


# --- public chart builders -------------------------------------------------
def line_chart(path, series, title="", xlabel="", ylabel="",
               xlim=None, ylim=None, ylog=False, xlog=False,
               hlines=(), vlines=(), legend=True, markers=False):
    """series: list of dict {name, xs, ys, color?, dash?}."""
    c = Canvas()
    allx = [x for s in series for x in s["xs"]]
    ally = [y for s in series for y in s["ys"]]
    c.xlim = xlim or (min(allx), max(allx))
    c.ylim = ylim or (min(ally + [0]), max(ally) * 1.08)
    c.xlog, c.ylog = xlog, ylog
    xticks = log_ticks(*c.xlim) if xlog else nice_ticks(*c.xlim)
    yticks = log_ticks(*c.ylim) if ylog else nice_ticks(*c.ylim)
    fx = (lambda v: _fmt(v))
    fy = (lambda v: _fmt(v))
    c.frame_and_grid(xticks, yticks, fx, fy)
    for hl in hlines:
        c.line(c.px0, c.Y(hl["y"]), c.px1, c.Y(hl["y"]),
               hl.get("color", "#444"), 1.5, hl.get("dash", "5 4"))
        c.text(c.px0 + 6, c.Y(hl["y"]) - 4, hl.get("label", ""), 10, "start",
               hl.get("color", "#444"))
    for vl in vlines:
        c.line(c.X(vl["x"]), c.py0, c.X(vl["x"]), c.py1,
               vl.get("color", "#444"), 1.5, vl.get("dash", "5 4"))
        c.text(c.X(vl["x"]) + 4, c.py0 + 12, vl.get("label", ""), 10, "start",
               vl.get("color", "#444"))
    leg = []
    for i, s in enumerate(series):
        col = s.get("color", PALETTE[i % len(PALETTE)])
        pts = [(c.X(x), c.Y(y)) for x, y in zip(s["xs"], s["ys"])]
        c.polyline(pts, col, dash=s.get("dash"))
        if markers:
            for x, y in pts:
                c.dot(x, y, 2.6, col)
        leg.append((s["name"], col))
    c.labels(title, xlabel, ylabel)
    if legend and len(series) > 1:
        c.legend(leg)
    c.save(path)


def heatmap(path, xs, ys, grid, title="", xlabel="", ylabel="",
            cbar_label="", cmap=viridis, vmin=None, vmax=None,
            annotate=None):
    """grid[j][i] = value at (xs[i], ys[j]). annotate(value)->str or None."""
    c = Canvas(w=890, pad=(70, 140, 30, 70))
    flat = [v for row in grid for v in row if v is not None]
    vmin = min(flat) if vmin is None else vmin
    vmax = max(flat) if vmax is None else vmax
    nx, ny = len(xs), len(ys)
    cw = (c.px1 - c.px0) / nx
    ch = (c.py1 - c.py0) / ny
    for j in range(ny):
        for i in range(nx):
            v = grid[j][i]
            x = c.px0 + i * cw
            y = c.py1 - (j + 1) * ch
            if v is None:
                c.rect(x, y, cw + 0.5, ch + 0.5, "#ddd")
                continue
            t = (v - vmin) / (vmax - vmin) if vmax > vmin else 0.5
            c.rect(x, y, cw + 0.5, ch + 0.5, cmap(t))
            if annotate:
                lab = annotate(v)
                if lab:
                    c.text(x + cw / 2, y + ch / 2 + 4, lab, 10,
                           fill="#fff" if t < 0.55 else "#111")
    c.rect(c.px0, c.py0, c.px1 - c.px0, c.py1 - c.py0, "none", "#999", 1)
    # x/y ticks (label every ~nth cell)
    xstep = max(1, nx // 8)
    for i in range(0, nx, xstep):
        px = c.px0 + (i + 0.5) * cw
        c.text(px, c.py1 + 18, _fmt(xs[i]), 10)
    ystep = max(1, ny // 8)
    for j in range(0, ny, ystep):
        py = c.py1 - (j + 0.5) * ch
        c.text(c.px0 - 8, py + 4, _fmt(ys[j]), 10, "end")
    # colorbar
    bx, bw = c.px1 + 22, 18
    steps = 40
    for k in range(steps):
        t = k / (steps - 1)
        y = c.py1 - (k + 1) * (c.py1 - c.py0) / steps
        c.rect(bx, y, bw, (c.py1 - c.py0) / steps + 0.5, cmap(t))
    c.rect(bx, c.py0, bw, c.py1 - c.py0, "none", "#999", 1)
    for frac in (0, 0.5, 1):
        val = vmin + frac * (vmax - vmin)
        y = c.py1 - frac * (c.py1 - c.py0)
        c.text(bx + bw + 4, y + 4, _fmt(val), 10, "start")
    c.text(bx + bw / 2, c.py0 - 10, cbar_label, 11, "middle")
    c.labels(title, xlabel, ylabel)
    c.save(path)


def barh(path, labels, values, colors=None, title="", xlabel="",
         value_fmt=None, legend_items=None):
    """Horizontal bars. colors: list per bar. value_fmt(v)->str for end label.
    legend_items: optional list of (label, color) drawn in the right margin."""
    n = len(labels)
    rpad = 250 if legend_items else 90
    lpad = min(460, max(150, int(max(len(l) for l in labels) * 6.6) + 16))
    w = max(1000 if legend_items else 860, lpad + rpad + 430)
    c = Canvas(w=w, h=max(360, 60 + n * 34), pad=(lpad, rpad, 40, 55))
    vmax = max(values) * 1.12
    c.xlim = (0, vmax)
    c.ylim = (0, n)
    xticks = nice_ticks(0, vmax)
    for xt in xticks:
        px = c.X(xt)
        c.line(px, c.py0, px, c.py1, "#eee", 1)
        c.text(px, c.py1 + 18, _fmt(xt), 10)
    bh = (c.py1 - c.py0) / n * 0.66
    for i, (lab, v) in enumerate(zip(labels, values)):
        yc = c.py1 - (i + 0.5) * (c.py1 - c.py0) / n
        col = (colors[i] if colors else PALETTE[i % len(PALETTE)])
        c.rect(c.px0, yc - bh / 2, c.X(v) - c.px0, bh, col)
        c.text(c.px0 - 8, yc + 4, lab, 11, "end")
        if value_fmt:
            c.text(c.X(v) + 5, yc + 4, value_fmt(v), 10, "start")
    c.rect(c.px0, c.py0, c.px1 - c.px0, c.py1 - c.py0, "none", "#999", 1)
    if legend_items:
        c.legend(legend_items, x=c.px1 + 16, y=c.py0 + 12)
    c.labels(title, xlabel, "")
    c.save(path)


def stacked_bar(path, groups, components, data, colors=None, title="",
                ylabel="", value_total_fmt=None):
    """groups: x categories. components: stack segment names.
    data[group][component] = value."""
    c = Canvas(w=720, pad=(70, 170, 40, 70))
    totals = [sum(data[g].values()) for g in groups]
    c.ylim = (0, max(totals) * 1.15)
    c.xlim = (0, len(groups))
    yticks = nice_ticks(0, c.ylim[1])
    for yt in yticks:
        py = c.Y(yt)
        c.line(c.px0, py, c.px1, py, "#eee", 1)
        c.text(c.px0 - 9, py + 4, _fmt(yt), 11, "end")
    bw = (c.px1 - c.px0) / len(groups) * 0.5
    cols = colors or {comp: PALETTE[i % len(PALETTE)]
                      for i, comp in enumerate(components)}
    for gi, g in enumerate(groups):
        xc = c.px0 + (gi + 0.5) * (c.px1 - c.px0) / len(groups)
        base = 0.0
        for comp in components:
            v = data[g].get(comp, 0.0)
            if v <= 0:
                continue
            c.rect(xc - bw / 2, c.Y(base + v), bw, c.Y(base) - c.Y(base + v),
                   cols[comp])
            base += v
        c.text(xc, c.py1 + 18, g, 12)
        if value_total_fmt:
            c.text(xc, c.Y(base) - 6, value_total_fmt(base), 11, weight="bold")
    c.rect(c.px0, c.py0, c.px1 - c.px0, c.py1 - c.py0, "none", "#999", 1)
    c.legend([(comp, cols[comp]) for comp in components], x=c.px1 + 20,
             y=c.py0 + 12)
    c.labels(title, "", ylabel)
    c.save(path)


def _fmt(v):
    if v == 0:
        return "0"
    a = abs(v)
    if a >= 1000:
        return f"{v:,.0f}"
    if a >= 10:
        return f"{v:.0f}"
    if a >= 1:
        return f"{v:.1f}"
    if a >= 0.01:
        return f"{v:.2f}"
    return f"{v:.0e}"
