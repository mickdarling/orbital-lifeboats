"""
A small dependency-free Markdown -> HTML converter. Handles the subset used in
this repo's notes: ATX headings, GFM pipe tables, ordered/unordered (nested)
lists, fenced code blocks, blockquotes, horizontal rules, and inline
bold/italic/code/links. Not a general Markdown engine — just enough for clean,
self-contained pages with no runtime dependencies.
"""

import re
import html

_TOK = "\x00{}\x00"


def _inline(text):
    """Inline formatting: code spans, links, bold, italic — escaping safely."""
    codes = []

    def grab(m):
        codes.append(html.escape(m.group(1)))
        return _TOK.format(len(codes) - 1)

    text = re.sub(r"`([^`]+)`", grab, text)
    text = html.escape(text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*(?!\*)([^*]+?)\*(?!\*)", r"<em>\1</em>", text)
    text = re.sub(r"\x00(\d+)\x00",
                  lambda m: f"<code>{codes[int(m.group(1))]}</code>", text)
    return text


def _is_table_sep(line):
    return bool(re.match(r"^\s*\|?[\s:|-]+\|[\s:|-]*$", line)) and "-" in line


def _split_row(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in line.split("|")]


def markdown_to_html(md):
    lines = md.split("\n")
    out = []
    i, n = 0, len(lines)

    def close_para(buf):
        if buf:
            out.append("<p>" + _inline(" ".join(buf)) + "</p>")
            buf.clear()

    para = []
    while i < n:
        line = lines[i]
        stripped = line.strip()

        # fenced code
        if stripped.startswith("```"):
            close_para(para)
            i += 1
            code = []
            while i < n and not lines[i].strip().startswith("```"):
                code.append(html.escape(lines[i]))
                i += 1
            i += 1
            out.append("<pre><code>" + "\n".join(code) + "</code></pre>")
            continue

        # blank
        if not stripped:
            close_para(para)
            i += 1
            continue

        # horizontal rule
        if re.match(r"^(-{3,}|_{3,}|\*{3,})$", stripped):
            close_para(para)
            out.append("<hr>")
            i += 1
            continue

        # heading
        m = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if m:
            close_para(para)
            lvl = len(m.group(1))
            out.append(f"<h{lvl}>{_inline(m.group(2))}</h{lvl}>")
            i += 1
            continue

        # table
        if "|" in line and i + 1 < n and _is_table_sep(lines[i + 1]):
            close_para(para)
            header = _split_row(line)
            i += 2
            rows = []
            while i < n and "|" in lines[i] and lines[i].strip():
                rows.append(_split_row(lines[i]))
                i += 1
            t = ["<table><thead><tr>"]
            t += [f"<th>{_inline(h)}</th>" for h in header]
            t.append("</tr></thead><tbody>")
            for r in rows:
                t.append("<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in r)
                         + "</tr>")
            t.append("</tbody></table>")
            out.append("".join(t))
            continue

        # blockquote
        if stripped.startswith(">"):
            close_para(para)
            quote = []
            while i < n and lines[i].strip().startswith(">"):
                quote.append(lines[i].strip()[1:].strip())
                i += 1
            out.append("<blockquote>" + _inline(" ".join(quote)) + "</blockquote>")
            continue

        # lists (nested by indent)
        if re.match(r"^\s*([-*]|\d+\.)\s+", line):
            close_para(para)
            out.append(_parse_list(lines, i, _list_end(lines, i)))
            i = _list_end(lines, i)
            continue

        # paragraph text
        para.append(stripped)
        i += 1

    close_para(para)
    return "\n".join(out)


def _list_end(lines, start):
    i = start
    n = len(lines)
    while i < n:
        s = lines[i]
        if s.strip() == "":
            # allow a single blank inside a list only if next line is a list item
            if i + 1 < n and re.match(r"^\s*([-*]|\d+\.)\s+", lines[i + 1]):
                i += 1
                continue
            break
        if re.match(r"^\s*([-*]|\d+\.)\s+", s) or s.startswith("  "):
            i += 1
        else:
            break
    return i


def _parse_list(lines, start, end):
    items = []
    for i in range(start, end):
        s = lines[i]
        if not s.strip():
            continue
        m = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)$", s)
        if m:
            indent = len(m.group(1))
            ordered = bool(re.match(r"\d+\.", m.group(2)))
            items.append([indent, ordered, m.group(3)])
        elif items:  # continuation line
            items[-1][2] += " " + s.strip()
    s, _ = _render_list(items, 0)
    return s


def _render_list(items, pos, indent=0):
    if pos >= len(items):
        return "", pos
    html_out = []
    ordered = items[pos][1]
    tag = "ol" if ordered else "ul"
    html_out.append(f"<{tag}>")
    while pos < len(items):
        ind, ordr, text = items[pos]
        if ind < indent:
            break
        if ind > indent:
            sub, pos = _render_list(items, pos, ind)
            if html_out and html_out[-1].endswith("</li>"):
                html_out[-1] = html_out[-1][:-5] + sub + "</li>"
            else:
                html_out.append(sub)
            continue
        html_out.append(f"<li>{_inline(text)}</li>")
        pos += 1
    html_out.append(f"</{tag}>")
    return "".join(html_out), pos
