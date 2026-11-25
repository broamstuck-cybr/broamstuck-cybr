# SPDX-License-Identifier: MIT
import json
import math
import os

FONT_MONO = "'JetBrains Mono', 'Fira Code', ui-monospace, SFMono-Regular, Menlo, monospace"
FONT_DISPLAY = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif"

BG_NIGHT = "#040917"
BG_CARD_TOP = "#08152d"
BG_CARD_BOT = "#040916"
BG_WELL = "#050c1d"
BG_CONSOLE = "#040915"

PRUSSIAN = "#122b52"
COBALT = "#1f4987"
ULTRAMARINE = "#336bc0"
CERULEAN = "#60a5fa"
MILKY_DUST = "#9ccaff"
MILKY_CORE = "#e0efff"

BORDER_SUBTLE = "#1e3252"
BORDER_WARM = "#365585"

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
INK_SECOND = "#d0dff2"
INK_MUTED = "#98b0d1"
INK_FAINT = "#6881a3"

LANG_PALETTE = {
    "HTML": ("#fb923c", "#ffedd5"),
    "TypeScript": ("#38bdf8", "#e0f2fe"),
    "JavaScript": ("#fbbf24", "#fef9c3"),
    "CSS": ("#2dd4bf", "#ccfbf1"),
    "Python": ("#4ade80", "#dcfce7"),
    "Shell": ("#a5b4fc", "#e0e7ff"),
}

REDUCED_MOTION_STYLE = (
    "<style>"
    ".pup-calm { display: none; } "
    "@media (prefers-reduced-motion: reduce) { "
    ".vg-drift { animation: none !important; } "
    ".pup-live { display: none !important; } "
    ".pup-calm { display: inline !important; } "
    "} "
    "@media (prefers-reduced-motion: reduce) { "
    "g:has(> animateMotion) { display: none !important; } "
    "}"
    "</style>"
)

_VG_SCENE_CACHE = None


def load_vangogh_scene(force_reload=False):
    global _VG_SCENE_CACHE
    if _VG_SCENE_CACHE is not None and not force_reload:
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
    nr = min(255, max(0, int(round(r * factor + warm_boost * 40.0))))
    ng = min(255, max(0, int(round(g * factor + warm_boost * 28.0))))
    nb = min(255, max(0, int(round(b * factor + warm_boost * 12.0))))
    return "#%02x%02x%02x" % (nr, ng, nb)


def nocturne_defs(prefix):
    return [
        '<linearGradient id="%s-bg" x1="0" y1="0" x2="0.16" y2="1">' % prefix,
        '<stop offset="0%%" stop-color="%s"/>' % BG_CARD_TOP,
        '<stop offset="48%%" stop-color="#071329"/>',
        '<stop offset="100%%" stop-color="%s"/>' % BG_CARD_BOT,
        "</linearGradient>",
        '<radialGradient id="%s-zenith" cx="0.52" cy="0.12" r="0.72">' % prefix,
        '<stop offset="0%%" stop-color="#1d447f" stop-opacity="0.28"/>',
        '<stop offset="62%%" stop-color="#0d2247" stop-opacity="0.10"/>',
        '<stop offset="100%%" stop-color="%s" stop-opacity="0"/>' % BG_CARD_BOT,
        "</radialGradient>",
        '<linearGradient id="%s-sheen" x1="0" y1="0" x2="1" y2="0">' % prefix,
        '<stop offset="0%%" stop-color="%s" stop-opacity="0"/>' % CREAM,
        '<stop offset="26%%" stop-color="%s" stop-opacity="0.44"/>' % SKY_SOFT,
        '<stop offset="52%%" stop-color="%s" stop-opacity="0.68"/>' % IVORY_WARM,
        '<stop offset="78%%" stop-color="%s" stop-opacity="0.36"/>' % SKY_SOFT,
        '<stop offset="100%%" stop-color="%s" stop-opacity="0"/>' % CREAM,
        "</linearGradient>",
    ]


def nocturne_card(width, height, prefix, radius=16):
    return [
        '<clipPath id="%s-clip"><rect x="1" y="1" width="%s" height="%s" rx="%s"/></clipPath>'
        % (prefix, num(width - 2), num(height - 2), num(radius)),
    ], [
        '<rect x="1" y="1" width="%s" height="%s" rx="%s" fill="url(#%s-bg)" stroke="%s" stroke-width="0.95"/>'
        % (num(width - 2), num(height - 2), num(radius), prefix, BORDER_WARM),
        '<rect x="1" y="1" width="%s" height="%s" rx="%s" fill="url(#%s-zenith)" pointer-events="none"/>'
        % (num(width - 2), num(height - 2), num(radius), prefix),
        '<line x1="28" y1="1.35" x2="%s" y2="1.35" stroke="url(#%s-sheen)" stroke-width="0.9"/>'
        % (num(width - 28), prefix),
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
    opacity_scale=0.88,
    glyph_stride=1,
    stroke_limit=1400,
    layer_key="panorama",
):
    # WHY: Renders fine-tapered Structure-Tensor impasto strokes with dual-tone specular ridges and crisp calligraphic glyphs.
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
    if bg_rows:
        elems.append('<g opacity="0.76">')
        for r_idx in range(0, len(bg_rows), 2):
            x_cur = 0
            ry = r_idx * row_step
            rh = row_step * 2.15
            for bcol, blen in bg_rows[r_idx]:
                px = x_cur * col_step
                pw = blen * col_step + 0.6
                if not _inside_boxes(px + pw * 0.5, ry + rh * 0.5, boxes, pad=8.0):
                    lifted_bg = shade_hex(bcol, 1.04, 0.01)
                    elems.append('<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>' % (num(px, 1), num(ry, 1), num(pw, 1), num(rh, 1), lifted_bg))
                x_cur += blen
        elems.append("</g>")

    strokes = layer.get("strokes") or []
    elems.append('<g fill="none" stroke-linecap="round">')
    count = 0
    w_scale = 1.48 if width >= 900 else 1.06
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
        stroke_w = max(0.45, sw * w_scale)
        r_c, g_c, _ = hex_to_rgb(scol)
        is_radiant = motif in (1, 2, 4) or (r_c + g_c) >= 340
        lit_col = shade_hex(scol, 1.04, 0.03 if is_radiant else 0.01)
        d_str = "M%s,%s Q%s,%s %s,%s" % (num(px0, 1), num(py0, 1), num(pxm, 1), num(pym, 1), num(px1, 1), num(py1, 1))
        if motif in (1, 4) and count % 17 == 0:
            dur = 4.8 + (count % 7) * 0.85
            elems.append(
                '<path class="pup-live" d="%s" stroke="%s" stroke-width="%s" stroke-opacity="0.90">'
                '<animate attributeName="stroke-opacity" values="0.58;0.98;0.58" dur="%ss" repeatCount="indefinite"/>'
                "</path>"
                '<path class="pup-calm" d="%s" stroke="%s" stroke-width="%s" stroke-opacity="0.88"/>'
                % (d_str, lit_col, num(stroke_w, 2), num(dur, 1), d_str, lit_col, num(stroke_w, 2))
            )
        else:
            elems.append(
                '<path d="%s" stroke="%s" stroke-width="%s" stroke-opacity="0.88"/>'
                % (d_str, lit_col, num(stroke_w, 2))
            )
        if is_radiant and count % 4 == 0:
            spec_col = shade_hex(scol, 1.16, 0.10)
            elems.append(
                '<path d="%s" stroke="%s" stroke-width="%s" stroke-opacity="0.58"/>'
                % (d_str, spec_col, num(max(0.36, stroke_w * 0.40), 2))
            )
    elems.append("</g>")

    grid = layer.get("grid") or []
    font_sz = width / (cols * 0.60)

    for r_idx in range(0, len(grid), max(1, glyph_stride)):
        py = (r_idx + 0.82) * row_step
        runs = grid[r_idx]
        if not boxes:
            tspans = "".join('<tspan fill="%s">%s</tspan>' % (shade_hex(col_h, 1.03, 0.01), esc(ch)) for col_h, ch in runs if col_h)
            elems.append(
                '<text x="0" y="%s" textLength="%s" lengthAdjust="spacing" font-family="%s" font-size="%s" font-weight="600" xml:space="preserve">%s</text>'
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
                    tspans.append('<tspan fill="%s">%s</tspan>' % (shade_hex(col_h, 1.03, 0.01), esc(joined)))
                else:
                    tspans.append(esc(joined))
            if has_visible:
                elems.append(
                    '<text x="0" y="%s" textLength="%s" lengthAdjust="spacing" font-family="%s" font-size="%s" font-weight="600" xml:space="preserve">%s</text>'
                    % (num(py, 2), num(width, 1), FONT_MONO, num(font_sz, 2), "".join(tspans))
                )

    elems.append("</g>")
    return elems


def solar_system_orrery(cx, cy, scale_x=280.0, scale_y=62.0, tilt_deg=-9.5, opacity=0.76):
    # WHY: Sculpted Keplerian 8-planet + Halley comet celestial mechanics with fine hairline orbits and luminous solar halo.
    planets = [
        ("Mercury", 0.17, 2.2, "#e2e8f0", "8s", 25, False),
        ("Venus", 0.26, 3.0, "#fef08a", "12s", 110, False),
        ("Earth", 0.37, 3.3, "#38bdf8", "17s", 215, False),
        ("Mars", 0.48, 2.6, "#fb7185", "23s", 310, False),
        ("Jupiter", 0.63, 4.6, "#fbbf24", "34s", 55, False),
        ("Saturn", 0.78, 3.9, "#fde047", "46s", 168, True),
        ("Uranus", 0.89, 3.0, "#67e8f9", "60s", 265, False),
        ("Neptune", 1.00, 2.9, "#60a5fa", "74s", 340, False),
    ]
    elems = [
        '<g transform="translate(%s %s) rotate(%s)" opacity="%s" pointer-events="none">'
        % (num(cx, 1), num(cy, 1), num(tilt_deg, 1), num(opacity, 2))
    ]
    elems.append('<circle cx="0" cy="0" r="22" fill="%s" fill-opacity="0.12"/>' % CADMIUM)
    elems.append('<circle cx="0" cy="0" r="14.5" fill="none" stroke="%s" stroke-width="0.6" stroke-dasharray="2.4 2" stroke-opacity="0.58"/>' % CREAM)
    elems.append('<path d="%s" fill="%s" stroke="%s" stroke-width="0.75"/>' % (star_path(0, 0, 12.2, 4.3, 8), FIREFLY_GOLD, IVORY_WARM))
    elems.append('<path d="%s" fill="#ffffff"/>' % star_path(0, 0, 5.8, 2.1, 4))

    comet_rx = scale_x * 0.78
    comet_ry = scale_y * 0.44
    peri_x = -comet_rx * 0.36
    aphe_x = comet_rx * 1.64
    comet_d = "M %s,0 A %s,%s 0 1,1 %s,0 A %s,%s 0 1,1 %s,0" % (
        num(peri_x, 1), num(comet_rx, 1), num(comet_ry, 1), num(aphe_x, 1),
        num(comet_rx, 1), num(comet_ry, 1), num(peri_x, 1),
    )
    elems.append('<path d="%s" transform="rotate(17)" fill="none" stroke="%s" stroke-width="0.58" stroke-opacity="0.38" stroke-dasharray="3.5 3.5"/>' % (comet_d, TEAL_MIST))
    comet_glyph = (
        '<path d="M0,0 L-20,-2.6 L-13,0 L-20,2.6 Z" fill="%s" fill-opacity="0.78"/>'
        '<path d="%s" fill="#ffffff"/>'
        % (SKY_SOFT, star_path(0, 0, 4.1, 1.4, 4))
    )
    elems.append(
        '<g class="pup-live" transform="rotate(17)">%s'
        '<animateMotion path="%s" dur="28s" rotate="auto" repeatCount="indefinite"/></g>'
        '<g class="pup-calm" transform="rotate(17) translate(%s 0)">%s</g>'
        % (comet_glyph, comet_d, num(peri_x, 1), comet_glyph)
    )

    for name, rf, pr, pcol, dur, phase_deg, has_ring in planets:
        rx = scale_x * rf
        ry = scale_y * rf
        orbit_d = "M %s,0 A %s,%s 0 1,1 %s,0 A %s,%s 0 1,1 %s,0" % (
            num(-rx, 1), num(rx, 1), num(ry, 1), num(rx, 1),
            num(rx, 1), num(ry, 1), num(-rx, 1),
        )
        elems.append(
            '<ellipse cx="0" cy="0" rx="%s" ry="%s" fill="none" stroke="%s" stroke-width="0.58" stroke-opacity="0.36"/>'
            % (num(rx, 1), num(ry, 1), MILKY_DUST if rf > 0.5 else CREAM)
        )
        neg_begin = -round((phase_deg / 360.0) * float(dur.rstrip("s")), 1)
        body_parts = []
        if has_ring:
            body_parts.append('<ellipse cx="0" cy="0" rx="%s" ry="%s" transform="rotate(-18)" fill="none" stroke="%s" stroke-width="1.05" stroke-opacity="0.92"/>' % (num(pr * 2.45, 1), num(pr * 0.86, 1), IVORY_WARM))
        if name == "Uranus":
            body_parts.append('<ellipse cx="0" cy="0" rx="%s" ry="%s" transform="rotate(72)" fill="none" stroke="%s" stroke-width="0.72"/>' % (num(pr * 1.9, 1), num(pr * 0.65, 1), SKY_SOFT))
        body_parts.append('<path d="%s" fill="%s" stroke="#081226" stroke-width="0.45"/>' % (star_path(0, 0, pr * 1.38, pr * 0.68, 6), pcol))
        body_parts.append('<circle cx="0" cy="0" r="%s" fill="#ffffff" fill-opacity="0.78"/>' % num(max(0.7, pr * 0.28), 1))
        planet_svg = "".join(body_parts)
        p_rad = math.radians(phase_deg)
        st_x = -rx * math.cos(p_rad)
        st_y = -ry * math.sin(p_rad)
        elems.append(
            '<g class="pup-live">%s<animateMotion path="%s" dur="%s" begin="%ss" repeatCount="indefinite"/></g>'
            '<g class="pup-calm" transform="translate(%s %s)">%s</g>'
            % (planet_svg, orbit_d, dur, num(neg_begin, 1), num(st_x, 1), num(st_y, 1), planet_svg)
        )

    elems.append("</g>")
    return elems
