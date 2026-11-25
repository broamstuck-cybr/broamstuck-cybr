# SPDX-License-Identifier: MIT
import json
import math
import os

FONT_MONO = "'JetBrains Mono', 'Fira Code', ui-monospace, SFMono-Regular, Menlo, monospace"
FONT_DISPLAY = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif"

BG_NIGHT = "#040814"
BG_CARD_TOP = "#071124"
BG_CARD_BOT = "#040915"
BG_WELL = "#040814"
BG_CONSOLE = "#040812"

PRUSSIAN = "#102546"
COBALT = "#1c4076"
ULTRAMARINE = "#2d5fa8"
CERULEAN = "#60a5fa"
MILKY_DUST = "#93c5fd"
MILKY_CORE = "#dbeafe"

BORDER_SUBTLE = "#1a2a44"
BORDER_WARM = "#2d446b"

IVORY = "#f8fafc"
IVORY_WARM = "#fefce8"
CREAM = "#fde68a"
CADMIUM = "#fde047"
FIREFLY_GOLD = "#fbbf24"
FIREFLY_AMBER = "#f59e0b"
CRESCENT_ORANGE = "#fb923c"
EMERALD_SOFT = "#6ee7b7"
EMERALD_MID = "#34d399"
TEAL_MIST = "#5eead4"
SKY_SOFT = "#7dd3fc"

INK_PRIMARY = "#f8fafc"
INK_SECOND = "#c5d4ea"
INK_MUTED = "#8fa5c4"
INK_FAINT = "#5d7393"

LANG_PALETTE = {
    "HTML": ("#fb923c", "#fed7aa"),
    "TypeScript": ("#38bdf8", "#bae6fd"),
    "JavaScript": ("#fbbf24", "#fef08a"),
    "CSS": ("#2dd4bf", "#99f6e4"),
    "Python": ("#4ade80", "#bbf7d0"),
    "Shell": ("#a5b4fc", "#e0e7ff"),
}

REDUCED_MOTION_STYLE = (
    "<style>"
    "@media (prefers-reduced-motion: reduce) { "
    "animate, animateTransform, animateMotion { display: none; } "
    ".vg-drift { animation: none !important; } "
    "}"
    "</style>"
)

_VG_SCENE_CACHE = None


def load_vangogh_scene():
    global _VG_SCENE_CACHE
    if _VG_SCENE_CACHE is not None:
        return _VG_SCENE_CACHE
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(root, "assets", "vangogh_scene.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as fh:
            _VG_SCENE_CACHE = json.load(fh)
    else:
        _VG_SCENE_CACHE = {}
    return _VG_SCENE_CACHE


def num(value, places=2):
    val = ("%." + str(places) + "f") % float(value)
    if "." in val:
        val = val.rstrip("0").rstrip(".")
    return "0" if val in ("", "-0") else val


def esc(value):
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def text(x, y, body, fill=INK_PRIMARY, size=12, anchor="start", weight="400", extra="", family=FONT_MONO):
    return (
        '<text x="%s" y="%s" font-family="%s" font-size="%s" font-weight="%s" '
        'fill="%s" text-anchor="%s"%s>%s</text>'
        % (num(x), num(y), family, num(size), weight, fill, anchor, extra, esc(body))
    )


def raw_text(x, y, inner, fill=INK_PRIMARY, size=12, anchor="start", weight="400", extra="", family=FONT_MONO):
    return (
        '<text x="%s" y="%s" font-family="%s" font-size="%s" font-weight="%s" '
        'fill="%s" text-anchor="%s" xml:space="preserve"%s>%s</text>'
        % (num(x), num(y), family, num(size), weight, fill, anchor, extra, inner)
    )


def star_path(cx, cy, outer_r, inner_r, points=5, rot_deg=-90.0):
    pts = []
    total = points * 2
    base_a = math.radians(rot_deg)
    for i in range(total):
        angle = base_a + i * math.pi / float(points)
        r = outer_r if i % 2 == 0 else inner_r
        pts.append("%s,%s" % (num(cx + math.cos(angle) * r, 1), num(cy + math.sin(angle) * r, 1)))
    return "M" + " L".join(pts) + " Z"


def compact(value):
    for suffix, scale in (("B", 1000000000.0), ("M", 1000000.0), ("K", 1000.0)):
        if value >= scale:
            return "%.1f%s" % (value / scale, suffix)
    return str(int(value))


def hex_to_rgb(hex_col):
    h = hex_col.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def shade_hex(hex_col, factor, warm_boost=0.0):
    r, g, b = hex_to_rgb(hex_col)
    nr = min(255, max(0, int(round(r * factor + warm_boost * 38.0))))
    ng = min(255, max(0, int(round(g * factor + warm_boost * 26.0))))
    nb = min(255, max(0, int(round(b * factor + warm_boost * 8.0))))
    return "#%02x%02x%02x" % (nr, ng, nb)


def nocturne_defs(prefix):
    return [
        '<linearGradient id="%s-bg" x1="0" y1="0" x2="0.18" y2="1">' % prefix,
        '<stop offset="0%%" stop-color="%s"/>' % BG_CARD_TOP,
        '<stop offset="52%%" stop-color="#061022"/>',
        '<stop offset="100%%" stop-color="%s"/>' % BG_CARD_BOT,
        "</linearGradient>",
        '<linearGradient id="%s-sheen" x1="0" y1="0" x2="1" y2="0">' % prefix,
        '<stop offset="0%%" stop-color="%s" stop-opacity="0"/>' % CREAM,
        '<stop offset="30%%" stop-color="%s" stop-opacity="0.34"/>' % SKY_SOFT,
        '<stop offset="55%%" stop-color="%s" stop-opacity="0.46"/>' % CREAM,
        '<stop offset="80%%" stop-color="%s" stop-opacity="0.24"/>' % SKY_SOFT,
        '<stop offset="100%%" stop-color="%s" stop-opacity="0"/>' % CREAM,
        "</linearGradient>",
    ]


def nocturne_card(width, height, prefix, radius=16):
    return [
        '<clipPath id="%s-clip"><rect x="1" y="1" width="%s" height="%s" rx="%s"/></clipPath>'
        % (prefix, num(width - 2), num(height - 2), num(radius)),
    ], [
        '<rect x="1" y="1" width="%s" height="%s" rx="%s" fill="url(#%s-bg)" stroke="%s" stroke-width="1.1"/>'
        % (num(width - 2), num(height - 2), num(radius), prefix, BORDER_WARM),
        '<line x1="32" y1="1.5" x2="%s" y2="1.5" stroke="url(#%s-sheen)" stroke-width="1.1"/>'
        % (num(width - 32), prefix),
    ]


def _inside_boxes(px, py, boxes, pad=0.0):
    for bx, by, bw, bh in boxes:
        if (bx - pad) <= px <= (bx + bw + pad) and (by - pad) <= py <= (by + bh + pad):
            return True
    return False


def van_gogh_starry_backdrop(
    prefix,
    width,
    height,
    avoid_boxes=None,
    opacity_scale=0.85,
    glyph_stride=1,
    stroke_limit=1400,
    layer_key="panorama",
):
    # WHY: Renders authentic Structure-Tensor impasto brushstrokes and tangent calligraphic glyphs extracted from Van Gogh's 3 reference paintings (zero blurry dots).
    scene = load_vangogh_scene()
    layer = scene.get(layer_key) or scene.get("panorama")
    if not layer:
        return []

    boxes = avoid_boxes or []
    elems = ['<g pointer-events="none" opacity="%s">' % num(opacity_scale, 2)]

    cols = max(1, int(layer.get("cols") or 204))
    rows = max(1, int(layer.get("rows") or 60))
    row_step = height / float(rows)
    col_step = width / float(cols)

    bg_rows = layer.get("bg") or []
    if bg_rows and opacity_scale >= 0.70:
        elems.append('<g opacity="0.58">')
        for r_idx in range(0, len(bg_rows), 2):
            x_cur = 0
            ry = r_idx * row_step
            rh = row_step * 2.15
            for bcol, blen in bg_rows[r_idx]:
                px = x_cur * col_step
                pw = blen * col_step + 0.6
                if not _inside_boxes(px + pw * 0.5, ry + rh * 0.5, boxes, pad=8.0):
                    elems.append('<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>' % (num(px, 1), num(ry, 1), num(pw, 1), num(rh, 1), bcol))
                x_cur += blen
        elems.append("</g>")

    strokes = layer.get("strokes") or []
    elems.append('<g fill="none" stroke-linecap="round">')
    count = 0
    for item in strokes:
        if count >= stroke_limit:
            break
        x0, y0, xm, ym, x1, y1, scol, sw, motif = item
        px0, py0 = x0 * width, y0 * height
        pxm, pym = xm * width, ym * height
        px1, py1 = x1 * width, y1 * height
        if _inside_boxes(pxm, pym, boxes, pad=6.0):
            continue
        count += 1
        stroke_w = sw * (1.85 if width >= 900 else 1.25)
        if motif in (1, 4) and count % 19 == 0:
            dur = 5.2 + (count % 7) * 0.9
            elems.append(
                '<path d="M%s,%s Q%s,%s %s,%s" stroke="%s" stroke-width="%s" stroke-opacity="0.86">'
                '<animate attributeName="stroke-opacity" values="0.52;0.96;0.52" dur="%ss" repeatCount="indefinite"/>'
                "</path>"
                % (num(px0, 1), num(py0, 1), num(pxm, 1), num(pym, 1), num(px1, 1), num(py1, 1), scol, num(stroke_w, 2), num(dur, 1))
            )
        else:
            elems.append(
                '<path d="M%s,%s Q%s,%s %s,%s" stroke="%s" stroke-width="%s" stroke-opacity="0.84"/>'
                % (num(px0, 1), num(py0, 1), num(pxm, 1), num(pym, 1), num(px1, 1), num(py1, 1), scol, num(stroke_w, 2))
            )
    elems.append("</g>")

    grid = layer.get("grid") or []
    font_sz = width / (cols * 0.60)

    for r_idx in range(0, len(grid), max(1, glyph_stride)):
        py = (r_idx + 0.82) * row_step
        runs = grid[r_idx]
        if not boxes:
            tspans = "".join('<tspan fill="%s">%s</tspan>' % (col_h, esc(ch)) for col_h, ch in runs if col_h)
            elems.append(
                '<text x="0" y="%s" textLength="%s" lengthAdjust="spacing" font-family="%s" font-size="%s" font-weight="700" xml:space="preserve">%s</text>'
                % (num(py, 2), num(width, 1), FONT_MONO, num(font_sz, 2), tspans)
            )
        else:
            tspans = []
            col_cur = 0
            has_visible = False
            for col_h, chunk in runs:
                masked_chars = []
                for k, ch in enumerate(chunk):
                    px = (col_cur + k + 0.5) * col_step
                    if _inside_boxes(px, py - row_step * 0.35, boxes, pad=8.0):
                        masked_chars.append(" ")
                    else:
                        masked_chars.append(ch)
                        if ch != " ":
                            has_visible = True
                col_cur += len(chunk)
                joined = "".join(masked_chars)
                if joined.strip() and col_h:
                    tspans.append('<tspan fill="%s">%s</tspan>' % (col_h, esc(joined)))
                else:
                    tspans.append(esc(joined))
            if has_visible:
                elems.append(
                    '<text x="0" y="%s" textLength="%s" lengthAdjust="spacing" font-family="%s" font-size="%s" font-weight="700" xml:space="preserve">%s</text>'
                    % (num(py, 2), num(width, 1), FONT_MONO, num(font_sz, 2), "".join(tspans))
                )

    elems.append("</g>")
    return elems


def solar_system_orrery(cx, cy, scale_x=280.0, scale_y=62.0, tilt_deg=-9.5, opacity=0.68):
    # WHY: Sculpted Keplerian 8-planet + Halley comet celestial mechanics using engraved multi-ray stellar geometry instead of flat circles.
    planets = [
        ("Mercury", 0.17, 2.2, "#cbd5e1", "8s", 25, False),
        ("Venus", 0.26, 3.0, "#fde68a", "12s", 110, False),
        ("Earth", 0.37, 3.3, "#38bdf8", "17s", 215, False),
        ("Mars", 0.48, 2.6, "#fb7185", "23s", 310, False),
        ("Jupiter", 0.63, 4.6, "#fbbf24", "34s", 55, False),
        ("Saturn", 0.78, 3.9, "#fcd34d", "46s", 168, True),
        ("Uranus", 0.89, 3.0, "#67e8f9", "60s", 265, False),
        ("Neptune", 1.00, 2.9, "#60a5fa", "74s", 340, False),
    ]
    elems = [
        '<g transform="translate(%s %s) rotate(%s)" opacity="%s" pointer-events="none">'
        % (num(cx, 1), num(cy, 1), num(tilt_deg, 1), num(opacity, 2))
    ]
    elems.append('<path d="%s" fill="%s" stroke="%s" stroke-width="0.9"/>' % (star_path(0, 0, 11.5, 4.2, 8), FIREFLY_GOLD, IVORY_WARM))
    elems.append('<path d="%s" fill="#ffffff"/>' % star_path(0, 0, 5.2, 2.0, 4))

    comet_rx = scale_x * 0.78
    comet_ry = scale_y * 0.44
    peri_x = -comet_rx * 0.36
    aphe_x = comet_rx * 1.64
    comet_d = "M %s,0 A %s,%s 0 1,1 %s,0 A %s,%s 0 1,1 %s,0" % (
        num(peri_x, 1), num(comet_rx, 1), num(comet_ry, 1), num(aphe_x, 1),
        num(comet_rx, 1), num(comet_ry, 1), num(peri_x, 1),
    )
    elems.append('<path d="%s" transform="rotate(17)" fill="none" stroke="%s" stroke-width="0.75" stroke-opacity="0.34" stroke-dasharray="4 4"/>' % (comet_d, TEAL_MIST))
    elems.append(
        '<g transform="rotate(17)">'
        '<path d="M0,0 L-18,-2.8 L-12,0 L-18,2.8 Z" fill="%s" fill-opacity="0.72"/>'
        '<path d="%s" fill="#ffffff"/>'
        '<animateMotion path="%s" dur="28s" rotate="auto" repeatCount="indefinite"/></g>'
        % (SKY_SOFT, star_path(0, 0, 3.8, 1.3, 4), comet_d)
    )

    for name, rf, pr, pcol, dur, phase_deg, has_ring in planets:
        rx = scale_x * rf
        ry = scale_y * rf
        orbit_d = "M %s,0 A %s,%s 0 1,1 %s,0 A %s,%s 0 1,1 %s,0" % (
            num(-rx, 1), num(rx, 1), num(ry, 1), num(rx, 1),
            num(rx, 1), num(ry, 1), num(-rx, 1),
        )
        elems.append(
            '<ellipse cx="0" cy="0" rx="%s" ry="%s" fill="none" stroke="%s" stroke-width="0.75" stroke-opacity="0.32"/>'
            % (num(rx, 1), num(ry, 1), MILKY_DUST if rf > 0.5 else CREAM)
        )
        neg_begin = -round((phase_deg / 360.0) * float(dur.rstrip("s")), 1)
        elems.append("<g>")
        if has_ring:
            elems.append('<ellipse cx="0" cy="0" rx="%s" ry="%s" transform="rotate(-18)" fill="none" stroke="%s" stroke-width="1.35"/>' % (num(pr * 2.4, 1), num(pr * 0.86, 1), CREAM))
        if name == "Uranus":
            elems.append('<ellipse cx="0" cy="0" rx="%s" ry="%s" transform="rotate(72)" fill="none" stroke="%s" stroke-width="0.9"/>' % (num(pr * 1.9, 1), num(pr * 0.65, 1), SKY_SOFT))
        elems.append('<path d="%s" fill="%s" stroke="#081226" stroke-width="0.55"/>' % (star_path(0, 0, pr * 1.35, pr * 0.68, 6), pcol))
        elems.append('<animateMotion path="%s" dur="%s" begin="%ss" repeatCount="indefinite"/>' % (orbit_d, dur, num(neg_begin, 1)))
        elems.append("</g>")

    elems.append("</g>")
    return elems
