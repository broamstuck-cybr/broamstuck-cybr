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
    ".pup-calm, .cel-calm, .eco-calm { display: none; } "
    ".cel-live, .eco-live { will-change: transform, opacity; } "
    "@keyframes vg-spin360 { to { transform: rotate(360deg); } } "
    ".vg-spin { transform-box: fill-box; transform-origin: center; will-change: transform; animation: vg-spin360 18s linear infinite; } "
    "@media (prefers-reduced-motion: reduce) { "
    "*, *::before, *::after { animation: none !important; transition: none !important; } "
    ".vg-drift, .vg-spin { animation: none !important; } "
    ".pup-live, .cel-live, .eco-live { display: none !important; } "
    ".pup-calm, .cel-calm, .eco-calm { display: inline !important; } "
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


def quant_hex(hex_col, step=6):
    r, g, b = hex_to_rgb(hex_col)
    qr = min(255, ((r + step // 2) // step) * step)
    qg = min(255, ((g + step // 2) // step) * step)
    qb = min(255, ((b + step // 2) // step) * step)
    return "#%02x%02x%02x" % (qr, qg, qb)


def merge_close_runs(runs, tol=9):
    merged = []
    prev_rgb = None
    for col_h, txt in runs:
        if not txt:
            continue
        if col_h is None:
            if merged and merged[-1][0] is None:
                merged[-1][1] += txt
            else:
                merged.append([None, txt])
                prev_rgb = None
            continue
        rgb = hex_to_rgb(col_h)
        if (
            merged
            and merged[-1][0] is not None
            and prev_rgb is not None
            and abs(rgb[0] - prev_rgb[0]) <= tol
            and abs(rgb[1] - prev_rgb[1]) <= tol
            and abs(rgb[2] - prev_rgb[2]) <= tol
        ):
            merged[-1][1] += txt
        else:
            merged.append([col_h, txt])
            prev_rgb = rgb
    return merged


def nocturne_defs(prefix):
    return [
        '<linearGradient id="%s-bg" x1="0" y1="0" x2="0.16" y2="1">' % prefix,
        '<stop offset="0%%" stop-color="%s"/>' % BG_CARD_TOP,
        '<stop offset="48%" stop-color="#071329"/>',
        '<stop offset="100%%" stop-color="%s"/>' % BG_CARD_BOT,
        "</linearGradient>",
        '<radialGradient id="%s-zenith" cx="0.52" cy="0.12" r="0.72">' % prefix,
        '<stop offset="0%" stop-color="#1d447f" stop-opacity="0.28"/>',
        '<stop offset="62%" stop-color="#0d2247" stop-opacity="0.10"/>',
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


def celestial_defs(prefix):
    # WHY: Shared GPU-composited gradients and sculpted celestial glyphs keep 60s Day-Night and 10s Giant Meteors ultra-compact.
    sun_flare = star_path(0, 0, 22.5, 9.5, 12, -90.0)
    sun_rays = star_path(0, 0, 68.0, 12.0, 8, -67.5)
    crescent_d = "M -4.2,-14.2 A 14.8,14.8 0 1,0 12.6,9.2 A 11.2,11.2 0 1,1 -4.2,-14.2 Z"
    return [
        '<linearGradient id="%s-dn-dawn-g" x1="0" y1="0" x2="0.06" y2="1">' % prefix,
        '<stop offset="0%" stop-color="#3b0764" stop-opacity="0.76"/>',
        '<stop offset="38%" stop-color="#be185d" stop-opacity="0.66"/>',
        '<stop offset="74%" stop-color="#fb7185" stop-opacity="0.58"/>',
        '<stop offset="100%" stop-color="#fde047" stop-opacity="0.34"/>',
        "</linearGradient>",
        '<linearGradient id="%s-dn-day-g" x1="0" y1="0" x2="0.08" y2="1">' % prefix,
        '<stop offset="0%" stop-color="#0284c7" stop-opacity="0.84"/>',
        '<stop offset="36%" stop-color="#38bdf8" stop-opacity="0.72"/>',
        '<stop offset="70%" stop-color="#7dd3fc" stop-opacity="0.50"/>',
        '<stop offset="88%" stop-color="#bae6fd" stop-opacity="0.34"/>',
        '<stop offset="100%" stop-color="#fef08a" stop-opacity="0.24"/>',
        "</linearGradient>",
        '<linearGradient id="%s-dn-dusk-g" x1="0" y1="0" x2="0.05" y2="1">' % prefix,
        '<stop offset="0%" stop-color="#2e1065" stop-opacity="0.78"/>',
        '<stop offset="38%" stop-color="#7e22ce" stop-opacity="0.68"/>',
        '<stop offset="74%" stop-color="#f97316" stop-opacity="0.62"/>',
        '<stop offset="100%" stop-color="#facc15" stop-opacity="0.36"/>',
        "</linearGradient>",
        '<linearGradient id="%s-dn-meadow-g" x1="0" y1="0" x2="0" y2="1">' % prefix,
        '<stop offset="0%" stop-color="#fef08a" stop-opacity="0"/>',
        '<stop offset="35%" stop-color="#fde047" stop-opacity="0.18"/>',
        '<stop offset="75%" stop-color="#4ade80" stop-opacity="0.20"/>',
        '<stop offset="100%" stop-color="#fbbf24" stop-opacity="0.16"/>',
        "</linearGradient>",
        '<linearGradient id="%s-dn-pan-dawn-g" x1="0" y1="0" x2="0.04" y2="1">' % prefix,
        '<stop offset="0%" stop-color="#3b0764" stop-opacity="0.76"/>',
        '<stop offset="28%" stop-color="#be185d" stop-opacity="0.68"/>',
        '<stop offset="52%" stop-color="#fb7185" stop-opacity="0.62"/>',
        '<stop offset="68%" stop-color="#fde047" stop-opacity="0.38"/>',
        '<stop offset="85%" stop-color="#fb923c" stop-opacity="0.16"/>',
        '<stop offset="100%" stop-color="#451a03" stop-opacity="0.08"/>',
        "</linearGradient>",
        '<linearGradient id="%s-dn-pan-day-g" x1="0" y1="0" x2="0.06" y2="1">' % prefix,
        '<stop offset="0%" stop-color="#0284c7" stop-opacity="0.86"/>',
        '<stop offset="28%" stop-color="#38bdf8" stop-opacity="0.74"/>',
        '<stop offset="50%" stop-color="#7dd3fc" stop-opacity="0.54"/>',
        '<stop offset="66%" stop-color="#fef08a" stop-opacity="0.34"/>',
        '<stop offset="84%" stop-color="#fde047" stop-opacity="0.16"/>',
        '<stop offset="100%" stop-color="#4ade80" stop-opacity="0.14"/>',
        "</linearGradient>",
        '<linearGradient id="%s-dn-pan-dusk-g" x1="0" y1="0" x2="0.04" y2="1">' % prefix,
        '<stop offset="0%" stop-color="#2e1065" stop-opacity="0.78"/>',
        '<stop offset="30%" stop-color="#7e22ce" stop-opacity="0.68"/>',
        '<stop offset="54%" stop-color="#f97316" stop-opacity="0.62"/>',
        '<stop offset="70%" stop-color="#facc15" stop-opacity="0.38"/>',
        '<stop offset="86%" stop-color="#ea580c" stop-opacity="0.16"/>',
        '<stop offset="100%" stop-color="#1e1b4b" stop-opacity="0.08"/>',
        "</linearGradient>",
        '<linearGradient id="%s-dn-amb-g" x1="0" y1="0" x2="0" y2="1">' % prefix,
        '<stop offset="0%" stop-color="#38bdf8" stop-opacity="0.16"/>',
        '<stop offset="55%" stop-color="#fef08a" stop-opacity="0.06"/>',
        '<stop offset="100%" stop-color="#040916" stop-opacity="0"/>',
        "</linearGradient>",
        '<linearGradient id="%s-dn-water-g" x1="0" y1="0" x2="0" y2="1">' % prefix,
        '<stop offset="0%" stop-color="#38bdf8" stop-opacity="0"/>',
        '<stop offset="45%" stop-color="#38bdf8" stop-opacity="0.24"/>',
        '<stop offset="100%" stop-color="#fef08a" stop-opacity="0.28"/>',
        "</linearGradient>",
        '<radialGradient id="%s-sun-aura" cx="0.5" cy="0.5" r="0.5">' % prefix,
        '<stop offset="0%" stop-color="#ffffff" stop-opacity="0.95"/>',
        '<stop offset="22%" stop-color="#fef08a" stop-opacity="0.78"/>',
        '<stop offset="56%" stop-color="#fbbf24" stop-opacity="0.34"/>',
        '<stop offset="100%" stop-color="#fb923c" stop-opacity="0"/>',
        "</radialGradient>",
        '<radialGradient id="%s-moon-aura" cx="0.5" cy="0.5" r="0.5">' % prefix,
        '<stop offset="0%" stop-color="#fef08a" stop-opacity="0.48"/>',
        '<stop offset="48%" stop-color="#60a5fa" stop-opacity="0.18"/>',
        '<stop offset="100%" stop-color="#1e3a8a" stop-opacity="0"/>',
        "</radialGradient>",
        '<g id="%s-sun-glyph">' % prefix,
        '<circle cx="0" cy="0" r="58" fill="url(#%s-sun-aura)"/>' % prefix,
        '<path d="%s" fill="url(#%s-sun-aura)" fill-opacity="0.58"/>' % (sun_rays, prefix),
        '<circle cx="0" cy="0" r="29" fill="none" stroke="#fef08a" stroke-width="1.4" stroke-dasharray="5.4 3.4" stroke-opacity="0.88"/>',
        '<circle cx="0" cy="0" r="22" fill="none" stroke="#fb923c" stroke-width="1.2" stroke-dasharray="3.8 2.8" stroke-opacity="0.82"/>',
        '<path d="%s" fill="#fde047" stroke="#f59e0b" stroke-width="0.85"/>' % sun_flare,
        '<circle cx="0" cy="0" r="11.8" fill="#fef9c3" stroke="#fbbf24" stroke-width="1.4"/>',
        '<circle cx="0" cy="0" r="6.8" fill="#ffffff"/>',
        "</g>",
        '<g id="%s-moon-glyph">' % prefix,
        '<circle cx="0" cy="0" r="34" fill="url(#%s-moon-aura)"/>' % prefix,
        '<circle cx="0" cy="0" r="20.5" fill="none" stroke="#fde68a" stroke-width="0.95" stroke-dasharray="4.2 3.1" stroke-opacity="0.68"/>',
        '<path d="%s" fill="#fde047" stroke="#fb923c" stroke-width="0.85"/>' % crescent_d,
        '<path d="M -2.5,-11.2 A 12.2,12.2 0 0,0 8.5,7.2" fill="none" stroke="#fefce8" stroke-width="1.05" stroke-linecap="round" stroke-opacity="0.85"/>',
        "</g>",
        '<linearGradient id="%s-mtail-outer" x1="1" y1="0.5" x2="0" y2="0.5">' % prefix,
        '<stop offset="0%" stop-color="#38bdf8" stop-opacity="0.92"/>',
        '<stop offset="32%" stop-color="#60a5fa" stop-opacity="0.62"/>',
        '<stop offset="68%" stop-color="#818cf8" stop-opacity="0.28"/>',
        '<stop offset="100%" stop-color="#0ea5e9" stop-opacity="0"/>',
        "</linearGradient>",
        '<linearGradient id="%s-mtail-core" x1="1" y1="0.5" x2="0" y2="0.5">' % prefix,
        '<stop offset="0%" stop-color="#ffffff" stop-opacity="1"/>',
        '<stop offset="24%" stop-color="#fef08a" stop-opacity="0.95"/>',
        '<stop offset="58%" stop-color="#fb923c" stop-opacity="0.54"/>',
        '<stop offset="100%" stop-color="#f59e0b" stop-opacity="0"/>',
        "</linearGradient>",
        '<radialGradient id="%s-mflash-g" cx="0.5" cy="0.5" r="0.5">' % prefix,
        '<stop offset="0%" stop-color="#e0f2fe" stop-opacity="0.46"/>',
        '<stop offset="45%" stop-color="#38bdf8" stop-opacity="0.20"/>',
        '<stop offset="100%" stop-color="#38bdf8" stop-opacity="0"/>',
        "</radialGradient>",
        '<radialGradient id="%s-mhead-cyan" cx="0.5" cy="0.5" r="0.5">' % prefix,
        '<stop offset="0%" stop-color="#ffffff" stop-opacity="0.95"/>',
        '<stop offset="38%" stop-color="#38bdf8" stop-opacity="0.68"/>',
        '<stop offset="100%" stop-color="#0284c7" stop-opacity="0"/>',
        "</radialGradient>",
        '<radialGradient id="%s-mhead-gold" cx="0.5" cy="0.5" r="0.5">' % prefix,
        '<stop offset="0%" stop-color="#ffffff" stop-opacity="1"/>',
        '<stop offset="48%" stop-color="#fef08a" stop-opacity="0.82"/>',
        '<stop offset="100%" stop-color="#fbbf24" stop-opacity="0"/>',
        "</radialGradient>",
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


def _lum_rgb(r, g, b):
    return 0.299 * r + 0.587 * g + 0.114 * b


def _tint_vg_rgb(r, g, b, motif):
    span = max(r, g, b) - min(r, g, b)
    lum = _lum_rgb(r, g, b)
    if span < 26 and lum > 138:
        lift = (26 - span) / 26.0
        if motif in (2, 4) or r > b + 4:
            r = min(255, int(r + 16 * lift))
            g = min(252, int(g + 8 * lift))
            b = max(118, int(b - 34 * lift))
        else:
            r = max(182, int(r - 12 * lift))
            g = min(248, int(g + 6 * lift))
            b = min(255, int(b + 20 * lift))
    return r, g, b


def _build_top_palette(rgb_weights, max_colors=56, step=16):
    hs = step // 2
    buckets = {}
    for (r, g, b), w in rgb_weights.items():
        qr = min(255, ((r + hs) // step) * step)
        qg = min(255, ((g + hs) // step) * step)
        qb = min(255, ((b + hs) // step) * step)
        k = (qr, qg, qb)
        buckets[k] = buckets.get(k, 0.0) + w
    if not buckets:
        return ["#08152d"], {}
    scored = sorted(
        buckets.items(),
        key=lambda kv: kv[1] * (1.0 + 0.008 * (max(kv[0]) - min(kv[0])) + 0.002 * _lum_rgb(*kv[0])),
        reverse=True,
    )
    chosen_rgb = [kv[0] for kv in scored[:max_colors]]
    chosen_hex = ["#%02x%02x%02x" % c for c in chosen_rgb]
    lut = {}
    for k in buckets:
        if k in chosen_rgb:
            lut[k] = chosen_rgb.index(k)
        else:
            kr, kg, kb = k
            best_i = 0
            best_d = 1e18
            for idx, (cr, cg, cb) in enumerate(chosen_rgb):
                dr, dg, db = kr - cr, kg - cg, kb - cb
                d = 2 * dr * dr + 4 * dg * dg + 3 * db * db
                if d < best_d:
                    best_d = d
                    best_i = idx
            lut[k] = best_i
    return chosen_hex, (step, hs, lut, chosen_rgb)


def _map_palette_idx(r, g, b, pal_meta):
    step, hs, lut, chosen_rgb = pal_meta
    qr = min(255, ((r + hs) // step) * step)
    qg = min(255, ((g + hs) // step) * step)
    qb = min(255, ((b + hs) // step) * step)
    idx = lut.get((qr, qg, qb))
    if idx is not None:
        return idx
    best_i = 0
    best_d = 1e18
    for i, (cr, cg, cb) in enumerate(chosen_rgb):
        dr, dg, db = qr - cr, qg - cg, qb - cb
        d = 2 * dr * dr + 4 * dg * dg + 3 * db * db
        if d < best_d:
            best_d = d
            best_i = i
    lut[(qr, qg, qb)] = best_i
    return best_i


def glyph_rel_path(ch, cx, cy, cw, ch_h, prec=1):
    rx = cw * 0.34
    ry = ch_h * 0.33
    p = lambda v: num(v, prec)
    if ch == "~":
        w, ay = rx * 1.04, ry * 0.58
        return "M%s,%sq%s,%s %s,0t%s,0" % (p(cx - w), p(cy), p(w * 0.5), p(-ay), p(w), p(w))
    if ch == "≈":
        w, ay, dy = rx * 1.02, ry * 0.44, ry * 0.38
        return "M%s,%sq%s,%s %s,0t%s,0M%s,%sq%s,%s %s,0t%s,0" % (
            p(cx - w), p(cy - dy), p(w * 0.5), p(-ay), p(w), p(w),
            p(cx - w), p(cy + dy), p(w * 0.5), p(-ay), p(w), p(w),
        )
    if ch == "(":
        return "M%s,%sq%s,%s 0,%s" % (p(cx + rx * 0.42), p(cy - ry * 0.94), p(-rx * 1.28), p(ry * 0.94), p(ry * 1.88))
    if ch == ")":
        return "M%s,%sq%s,%s 0,%s" % (p(cx - rx * 0.42), p(cy - ry * 0.94), p(rx * 1.28), p(ry * 0.94), p(ry * 1.88))
    if ch == "╭":
        return "M%s,%sq0,%s %s,%s" % (p(cx - rx * 0.82), p(cy + ry * 0.76), p(-ry * 1.52), p(rx * 1.64), p(-ry * 1.52))
    if ch == "╮":
        return "M%s,%sq%s,0 %s,%s" % (p(cx - rx * 0.82), p(cy - ry * 0.76), p(rx * 1.64), p(rx * 1.64), p(ry * 1.52))
    if ch == "╯":
        return "M%s,%sq0,%s %s,%s" % (p(cx + rx * 0.82), p(cy - ry * 0.76), p(ry * 1.52), p(-rx * 1.64), p(ry * 1.52))
    if ch == "╰":
        return "M%s,%sq0,%s %s,%s" % (p(cx - rx * 0.82), p(cy - ry * 0.76), p(ry * 1.52), p(rx * 1.64), p(ry * 1.52))
    if ch in ("S", "s"):
        sc = 0.82 if ch == "s" else 1.0
        rxs, rys = rx * sc, ry * sc
        return "M%s,%sa%s,%s 0 1,0 %s,%sa%s,%s 0 1,1 %s,%s" % (
            p(cx + rxs * 0.70), p(cy - rys * 0.60),
            p(rxs * 0.74), p(rys * 0.46), p(-rxs * 0.70), p(rys * 0.60),
            p(rxs * 0.74), p(rys * 0.46), p(-rxs * 0.70), p(rys * 0.60),
        )
    if ch in ("C", "c"):
        sc = 0.80 if ch == "c" else 1.0
        rxc, ryc = rx * sc, ry * sc
        return "M%s,%sa%s,%s 0 1,0 0,%s" % (p(cx + rxc * 0.72), p(cy - ryc * 0.58), p(rxc * 0.84), p(ryc * 0.88), p(ryc * 1.16))
    if ch in ("O", "o", "0"):
        sc = 0.72 if ch == "o" else 1.0
        rxo, ryo = rx * 0.86 * sc, ry * 0.88 * sc
        return "M%s,%sa%s,%s 0 1,0 %s,0a%s,%s 0 1,0 %s,0" % (
            p(cx - rxo), p(cy), p(rxo), p(ryo), p(rxo * 2.0), p(rxo), p(ryo), p(-rxo * 2.0),
        )
    if ch == "/":
        return "M%s,%sl%s,%s" % (p(cx - rx * 0.78), p(cy + ry * 0.90), p(rx * 1.56), p(-ry * 1.80))
    if ch == "\\":
        return "M%s,%sl%s,%s" % (p(cx - rx * 0.78), p(cy - ry * 0.90), p(rx * 1.56), p(ry * 1.80))
    if ch in ("|", "!"):
        return "M%s,%sv%s" % (p(cx), p(cy - ry * 0.95), p(ry * 1.90))
    if ch == "-":
        return "M%s,%sh%s" % (p(cx - rx * 0.84), p(cy), p(rx * 1.68))
    if ch == "=":
        dy, w = ry * 0.34, rx * 1.72
        return "M%s,%sh%sm%s,%sh%s" % (p(cx - rx * 0.86), p(cy - dy), p(w), p(-w), p(dy * 2.0), p(w))
    if ch == "^":
        return "M%s,%sl%s,%sl%s,%s" % (p(cx - rx * 0.82), p(cy + ry * 0.18), p(rx * 0.82), p(-ry * 0.92), p(rx * 0.82), p(ry * 0.92))
    if ch == "v":
        return "M%s,%sl%s,%sl%s,%s" % (p(cx - rx * 0.80), p(cy - ry * 0.56), p(rx * 0.80), p(ry * 1.22), p(rx * 0.80), p(-ry * 1.22))
    if ch == "+":
        return "M%s,%sh%sM%s,%sv%s" % (p(cx - rx * 0.86), p(cy), p(rx * 1.72), p(cx), p(cy - ry * 0.68), p(ry * 1.36))
    if ch == "*":
        dx, dy, vy = rx * 0.82, ry * 0.46, ry * 0.76
        return "M%s,%sv%sM%s,%sl%s,%sM%s,%sl%s,%s" % (
            p(cx), p(cy - vy), p(vy * 2.0),
            p(cx - dx), p(cy - dy), p(dx * 2.0), p(dy * 2.0),
            p(cx - dx), p(cy + dy), p(dx * 2.0), p(-dy * 2.0),
        )
    if ch == "#":
        return "M%s,%sl%s,%sM%s,%sl%s,%sM%s,%sh%sM%s,%sh%s" % (
            p(cx - rx * 0.28), p(cy - ry * 0.84), p(-rx * 0.22), p(ry * 1.68),
            p(cx + rx * 0.50), p(cy - ry * 0.84), p(-rx * 0.22), p(ry * 1.68),
            p(cx - rx * 0.88), p(cy - ry * 0.30), p(rx * 1.76),
            p(cx - rx * 0.88), p(cy + ry * 0.30), p(rx * 1.76),
        )
    if ch == "%":
        rp = max(0.45 if prec >= 1 else 2.0, rx * 0.28)
        return "M%s,%sl%s,%sM%s,%sa%s,%s 0 1,0 %s,0a%s,%s 0 1,0 %s,0M%s,%sa%s,%s 0 1,0 %s,0a%s,%s 0 1,0 %s,0" % (
            p(cx - rx * 0.80), p(cy + ry * 0.82), p(rx * 1.60), p(-ry * 1.64),
            p(cx - rx * 0.54 - rp), p(cy - ry * 0.50), p(rp), p(rp), p(rp * 2.0), p(rp), p(rp), p(-rp * 2.0),
            p(cx + rx * 0.54 - rp), p(cy + ry * 0.50), p(rp), p(rp), p(rp * 2.0), p(rp), p(rp), p(-rp * 2.0),
        )
    if ch == "@":
        return "M%s,%sa%s,%s 0 1,0 0,%sl0,%sv%sq%s,%s %s,%sa%s,%s 0 1,0 %s,%s" % (
            p(cx + rx * 0.38), p(cy - ry * 0.26),
            p(rx * 0.38), p(ry * 0.38), p(ry * 0.54),
            p(-ry * 0.54), p(ry * 0.54),
            p(rx * 0.52), p(ry * 0.10), p(rx * 0.52), p(-ry * 0.24),
            p(rx * 0.92), p(ry * 0.92), p(-rx * 0.36), p(ry * 0.78),
        )
    if ch == "8":
        r8x, r8y = rx * 0.68, ry * 0.43
        return "M%s,%sa%s,%s 0 1,0 %s,0a%s,%s 0 1,0 %s,0M%s,%sa%s,%s 0 1,0 %s,0a%s,%s 0 1,0 %s,0" % (
            p(cx - r8x), p(cy - r8y), p(r8x), p(r8y), p(r8x * 2.0), p(r8x), p(r8y), p(-r8x * 2.0),
            p(cx - r8x), p(cy + r8y), p(r8x), p(r8y), p(r8x * 2.0), p(r8x), p(r8y), p(-r8x * 2.0),
        )
    if ch == "x":
        return "M%s,%sl%s,%sM%s,%sl%s,%s" % (
            p(cx - rx * 0.74), p(cy - ry * 0.66), p(rx * 1.48), p(ry * 1.32),
            p(cx - rx * 0.74), p(cy + ry * 0.66), p(rx * 1.48), p(-ry * 1.32),
        )
    if ch == "z":
        return "M%s,%sh%sl%s,%sh%s" % (
            p(cx - rx * 0.74), p(cy - ry * 0.64), p(rx * 1.48), p(-rx * 1.48), p(ry * 1.28), p(rx * 1.48),
        )
    if ch == "°":
        ro = max(0.5 if prec >= 1 else 2.0, rx * 0.38)
        return "M%s,%sa%s,%s 0 1,0 %s,0a%s,%s 0 1,0 %s,0" % (
            p(cx - ro), p(cy - ry * 0.44), p(ro), p(ro), p(ro * 2.0), p(ro), p(ro), p(-ro * 2.0),
        )
    if ch in (":", ";"):
        dv = 0.15 if prec >= 1 else 1.0
        return "M%s,%sv%sM%s,%sv%s" % (p(cx), p(cy - ry * 0.44), p(dv), p(cx), p(cy + ry * 0.42), p(dv))
    dv = 0.15 if prec >= 1 else 1.0
    return "M%s,%sv%s" % (p(cx), p(cy), p(dv))


def _dim_factor_at(px, py, dim_boxes):
    if not dim_boxes:
        return 1.0
    fac = 1.0
    feather = 18.0
    for item in dim_boxes:
        bx, by, bw, bh = item[0], item[1], item[2], item[3]
        target = item[4] if len(item) >= 5 else 0.38
        dx = max(bx - px, 0.0, px - (bx + bw))
        dy = max(by - py, 0.0, py - (by + bh))
        dist = math.hypot(dx, dy)
        if dist < feather:
            t = dist / feather
            s = t * t * (3.0 - 2.0 * t)
            fac = min(fac, target + (1.0 - target) * s)
    return fac


def _pick_backdrop_char(base_ch, tr, tc, gx, gy, lum, m_val):
    h = (tr * 37 + tc * 73) & 31
    tx, ty = -gy, gx
    gmag = math.hypot(tx, ty)
    if m_val == 4:
        if lum > 175:
            return ("@", "*", "#", "%", "+", "O")[h % 6]
        if lum > 125:
            return ("*", "+", "/", "\\", "(", ")", "S", "C")[h % 8]
        return ("/", "\\", "(", ")", "~", "^", "v", ":")[h % 8]
    if m_val == 3:
        if lum > 105:
            return ("|", "/", "\\", "S", "(", ")", "^", "#")[h % 8]
        return ("|", "/", "\\", "(", ")", "^", ":")[h % 7]
    if m_val == 1 or lum > 202:
        if lum > 224:
            return ("@", "*", "+", "O", "°", "#")[h % 6]
        if gmag > 6.0:
            if abs(tx) > abs(ty) * 1.3:
                return ("~", "≈", "╭", "╮", "╯", "╰")[h % 6]
            return ("(", ")", "/", "\\", "S", "C")[h % 6]
        return ("*", "+", "O", "°", "~", "≈")[h % 6]
    if base_ch and base_ch not in (" ", "~"):
        if base_ch == "o":
            return "O" if lum > 155 else "o"
        if base_ch in ("s", "c"):
            return base_ch.upper() if lum > 135 else base_ch
        return base_ch
    if gmag > 6.8:
        ax, ay = abs(tx), abs(ty)
        if ay > ax * 1.45:
            return ("(", ")", "S", "C", "/", "\\")[h % 6]
        if ax > ay * 1.55:
            if lum > 140:
                return ("~", "≈", "=", "S")[h % 4]
            return ("~", "≈", "=", "-")[h % 4]
        if tx * ty < 0.0:
            return ("/", "╭", "╯", "(", "~")[h % 5]
        return ("\\", "╮", "╰", ")", "~")[h % 5]
    if lum < 44:
        return (":", "·", "-", "~", "=")[h % 5]
    if lum < 92:
        return ("~", "-", "=", ":", "/", "\\")[h % 6]
    return ("~", "≈", "=", "(", ")", "S", "C", "+")[h % 8]


def van_gogh_starry_backdrop(
    prefix,
    width,
    height,
    avoid_boxes=None,
    opacity_scale=0.88,
    glyph_stride=1,
    stroke_limit=1400,
    layer_key="panorama",
    dim_boxes=None,
    occlude_circle=None,
):
    # WHY: Smooth wave underpainting + curved Bezier impasto + <=42 batched 4K calligraphic glyph <path>s eliminate blocky tiles at 60fps.
    scene = load_vangogh_scene()
    layer = scene.get(layer_key) or scene.get("panorama")
    if not layer:
        return []

    boxes = avoid_boxes or []
    op_s = min(1.0, max(0.25, float(opacity_scale)))
    elems = ['<g pointer-events="none">']

    def _bake(r, g, b, alpha):
        a = min(1.0, max(0.0, alpha))
        ia = 1.0 - a
        return (int(5 * ia + r * a), int(12 * ia + g * a), int(28 * ia + b * a))

    cols = max(1, int(layer.get("cols") or 204))
    rows = max(1, int(layer.get("rows") or 60))
    bg_rows = layer.get("bg") or []
    grid = layer.get("grid") or []
    motifs_raw = layer.get("motifs") or []

    bg_cells = [[(8, 21, 45)] * cols for _ in range(rows)]
    for r_idx in range(min(rows, len(bg_rows))):
        c_cur = 0
        for bcol, blen in bg_rows[r_idx]:
            rgb_b = hex_to_rgb(shade_hex(bcol, 1.02, 0.01))
            end_c = min(cols, c_cur + blen)
            for c_i in range(c_cur, end_c):
                bg_cells[r_idx][c_i] = rgb_b
            c_cur = end_c

    grid_cells = [[None] * cols for _ in range(rows)]
    for r_idx in range(min(rows, len(grid))):
        c_cur = 0
        for col_h, chunk in grid[r_idx]:
            rgb_g = hex_to_rgb(col_h) if col_h else None
            for ch in chunk:
                if c_cur >= cols:
                    break
                if ch != " " and rgb_g is not None:
                    grid_cells[r_idx][c_cur] = (rgb_g, ch)
                c_cur += 1

    elems.append('<g opacity="0.46">')
    n_bands = min(16, max(8, int(round(height / 24.0))))
    band_h = height / float(n_bands)
    for b_i in range(n_bands):
        r0 = int(b_i * rows / float(n_bands))
        r1 = max(r0 + 1, int((b_i + 1) * rows / float(n_bands)))
        sr_a = sg_a = sb_a = cnt_a = 0
        for rr in range(r0, min(rows, r1)):
            row_b = bg_cells[rr]
            for cc in range(0, cols, 3):
                br, bg_v, bb = row_b[cc]
                sr_a += br
                sg_a += bg_v
                sb_a += bb
                cnt_a += 1
        if cnt_a > 0:
            mr, mg, mb = _bake(sr_a // cnt_a, sg_a // cnt_a, sb_a // cnt_a, op_s * 0.88)
            b_hex = "#%02x%02x%02x" % (mr, mg, mb)
            y_top = max(0.0, b_i * band_h - 3.5)
            y_bot = min(float(height), (b_i + 1) * band_h + 3.5)
            amp = min(6.5, band_h * 0.28) * (1.0 if b_i % 2 == 0 else -1.0)
            d_band = "M0,%sQ%s,%s %s,%sT%s,%sV%sQ%s,%s %s,%sT0,%sZ" % (
                num(y_top, 1),
                num(width * 0.25, 1), num(y_top - amp, 1), num(width * 0.5, 1), num(y_top, 1),
                num(width, 1), num(y_top, 1),
                num(y_bot, 1),
                num(width * 0.75, 1), num(y_bot + amp, 1), num(width * 0.5, 1), num(y_bot, 1),
                num(y_bot, 1),
            )
            elems.append('<path fill="%s" d="%s"/>' % (b_hex, d_band))

    glow_spots = []
    g_step_r = max(4, rows // 6)
    g_step_c = max(8, cols // 8)
    for gr_i in range(g_step_r // 2, rows, g_step_r):
        m_row = motifs_raw[gr_i] if gr_i < len(motifs_raw) else ""
        for gc_i in range(g_step_c // 2, cols, g_step_c):
            br, bg_v, bb = bg_cells[gr_i][gc_i]
            gc_cell = grid_cells[gr_i][gc_i]
            if gc_cell is not None:
                (kr, kg, kb), _ = gc_cell
                br = (br + kr) // 2
                bg_v = (bg_v + kg) // 2
                bb = (bb + kb) // 2
            m_v = int(m_row[gc_i]) if gc_i < len(m_row) and m_row[gc_i].isdigit() else 0
            lum_g = _lum_rgb(br, bg_v, bb)
            score_g = lum_g + (45.0 if m_v in (1, 3, 4) else 0.0)
            gx_p = (gc_i + 0.5) * (width / float(cols))
            gy_p = (gr_i + 0.5) * (height / float(rows))
            if occlude_circle is not None:
                ocx, ocy, ocr = occlude_circle
                if (gx_p - ocx) ** 2 + (gy_p - ocy) ** 2 < (ocr * 0.85) ** 2:
                    continue
            glow_spots.append((score_g, gx_p, gy_p, br, bg_v, bb, m_v))
    glow_spots.sort(key=lambda it: it[0], reverse=True)
    rx_glow = num(max(24.0, width / 7.2), 1)
    ry_glow = num(max(16.0, height / 4.8), 1)
    for _, gx_p, gy_p, br, bg_v, bb, m_v in glow_spots[:14]:
        df = _dim_factor_at(gx_p, gy_p, dim_boxes)
        mr, mg, mb = _bake(*_tint_vg_rgb(br, bg_v, bb, m_v), op_s * 0.80 * df)
        elems.append(
            '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="#%02x%02x%02x" fill-opacity="0.44"/>'
            % (num(gx_p, 1), num(gy_p, 1), rx_glow, ry_glow, mr, mg, mb)
        )
    elems.append("</g>")

    strokes = layer.get("strokes") or []
    scale_f = max(0.58, min(1.10, width / 1100.0))
    w_under = num(max(1.5, 2.6 * scale_f), 1)
    target_n = min(stroke_limit, 420 if width >= 900 else (300 if width >= 440 else 210))
    stride_s = max(1, len(strokes) // max(1, target_n))
    raw_stroke_cmds = []
    stroke_weights = {}

    for item in strokes[::stride_s][:target_n]:
        x0, y0, xm, ym, x1, y1, scol, _, motif = item
        pxm, pym = xm * width, ym * height
        if boxes and _inside_boxes(pxm, pym, boxes, pad=6.0):
            continue
        if occlude_circle is not None:
            ocx, ocy, ocr = occlude_circle
            if (pxm - ocx) ** 2 + (pym - ocy) ** 2 < ocr * ocr:
                continue
        df = _dim_factor_at(pxm, pym, dim_boxes)
        ex0 = pxm + (x0 * width - pxm) * 1.25
        ey0 = pym + (y0 * height - pym) * 1.25
        ex1 = pxm + (x1 * width - pxm) * 1.25
        ey1 = pym + (y1 * height - pym) * 1.25
        sr, sg, sb = _tint_vg_rgb(*hex_to_rgb(scol), motif)
        bk_rgb = _bake(sr, sg, sb, op_s * 0.82 * df)
        stroke_weights[bk_rgb] = stroke_weights.get(bk_rgb, 0.0) + (2.0 if motif in (1, 3, 4) else 1.0)
        d_str = "M%s,%sQ%s,%s %s,%s" % (num(ex0, 1), num(ey0, 1), num(pxm, 1), num(pym, 1), num(ex1, 1), num(ey1, 1))
        raw_stroke_cmds.append((bk_rgb, d_str))

    if stroke_weights:
        st_hex_list, st_meta = _build_top_palette(stroke_weights, max_colors=14, step=18)
        elems.append('<g fill="none" stroke-linecap="round" opacity="0.38">')
        buckets = {}
        for bk_rgb, d_cmd in raw_stroke_cmds:
            c_hex = st_hex_list[_map_palette_idx(bk_rgb[0], bk_rgb[1], bk_rgb[2], st_meta)]
            buckets.setdefault(c_hex, []).append(d_cmd)
        for c_hex, segs in buckets.items():
            elems.append('<path stroke="%s" stroke-width="%s" d="%s"/>' % (c_hex, w_under, "".join(segs)))
        elems.append("</g>")

    cw_target = 5.25 if width < 440 else (5.45 if width >= 900 else 5.35)
    rh_target = 7.85 if height < 200 else 8.00
    t_cols = max(24, int(round(width / cw_target)))
    t_rows = max(12, int(round(height / rh_target)))
    cw = width / float(t_cols)
    rh = height / float(t_rows)

    lum_grid = [[0.0] * cols for _ in range(rows)]
    rgb_comp = [[(8, 21, 45)] * cols for _ in range(rows)]
    for rr in range(rows):
        for cc in range(cols):
            br, bg_v, bb = bg_cells[rr][cc]
            gc = grid_cells[rr][cc]
            if gc is not None:
                (gr, gg, gb), _ = gc
                cr = int(br * 0.24 + gr * 0.76)
                cg = int(bg_v * 0.24 + gg * 0.76)
                cb = int(bb * 0.24 + gb * 0.76)
            else:
                cr, cg, cb = br, bg_v, bb
            rgb_comp[rr][cc] = (cr, cg, cb)
            lum_grid[rr][cc] = _lum_rgb(cr, cg, cb)

    lum_sm = [[0.0] * cols for _ in range(rows)]
    for rr in range(rows):
        r0_s, r1_s = max(0, rr - 1), min(rows - 1, rr + 1)
        for cc in range(cols):
            c0_s, c1_s = max(0, cc - 1), min(cols - 1, cc + 1)
            lum_sm[rr][cc] = (
                lum_grid[r0_s][c0_s] + lum_grid[r0_s][cc] + lum_grid[r0_s][c1_s]
                + lum_grid[rr][c0_s] + lum_grid[rr][cc] * 2.0 + lum_grid[rr][c1_s]
                + lum_grid[r1_s][c0_s] + lum_grid[r1_s][cc] + lum_grid[r1_s][c1_s]
            ) / 10.0

    fine_cmds = []
    bold_cmds = []
    char_weights = {}
    sparkles = []

    for tr in range(t_rows):
        py = (tr + 0.5) * rh
        sr = min(rows - 1, int(((tr + 0.5) / float(t_rows)) * rows))
        m_row = motifs_raw[sr] if sr < len(motifs_raw) else ""
        sr_m = max(0, sr - 1)
        sr_p = min(rows - 1, sr + 1)
        for tc in range(t_cols):
            px = (tc + 0.5) * cw
            if boxes and _inside_boxes(px, py, boxes, pad=5.0):
                continue
            if occlude_circle is not None:
                ocx, ocy, ocr = occlude_circle
                if (px - ocx) ** 2 + (py - ocy) ** 2 < ocr * ocr:
                    continue
            sc = min(cols - 1, int(((tc + 0.5) / float(t_cols)) * cols))
            sc_m = max(0, sc - 1)
            sc_p = min(cols - 1, sc + 1)

            cr, cg, cb = rgb_comp[sr][sc]
            gc = grid_cells[sr][sc]
            base_ch = gc[1] if gc is not None else " "
            m_val = int(m_row[sc]) if sc < len(m_row) and m_row[sc].isdigit() else 0
            lum_v = lum_grid[sr][sc]
            gx = (lum_sm[sr][sc_p] - lum_sm[sr][sc_m]) * 0.5
            gy = (lum_sm[sr_p][sc] - lum_sm[sr_m][sc]) * 0.5

            ch_use = _pick_backdrop_char(base_ch, tr, tc, gx, gy, lum_v, m_val)

            tr_c, tg_c, tb_c = _tint_vg_rgb(cr, cg, cb, m_val)
            lift = 1.18 if lum_v < 110 else 1.09
            floor_b = 16 if m_val == 0 else 10
            lr = min(255, int(tr_c * lift + (floor_b * 0.45)))
            lg = min(255, int(tg_c * lift + (floor_b * 0.78)))
            lb = min(255, int(tb_c * lift + (floor_b * 1.35 if m_val == 0 else floor_b * 0.45)))

            df = _dim_factor_at(px, py, dim_boxes)
            bk_rgb = _bake(lr, lg, lb, op_s * df)
            w_imp = 3.2 if m_val in (1, 3, 4) else (1.8 if lum_v > 155 else 1.0)
            char_weights[bk_rgb] = char_weights.get(bk_rgb, 0.0) + w_imp

            g_d = glyph_rel_path(ch_use, px, py, cw, rh, prec=1)
            is_bold = (df > 0.72) and ((m_val in (1, 4) and lum_v >= 148) or lum_v >= 186)
            if is_bold:
                bold_cmds.append((bk_rgb, g_d))
                if lum_v >= 226 and ((tr * 19 + tc * 41) % 37 == 0) and len(sparkles) < 8:
                    sp_ch = "✦" if (tr + tc) % 2 == 0 else "*"
                    sparkles.append((px, py + rh * 0.32, "#%02x%02x%02x" % bk_rgb, sp_ch))
            else:
                fine_cmds.append((bk_rgb, g_d))

    if char_weights:
        ch_hex_list, ch_meta = _build_top_palette(char_weights, max_colors=24, step=14)
        elems.append('<g fill="none" stroke-linecap="round" stroke-linejoin="round" opacity="0.96">')
        f_buckets = {}
        for bk_rgb, g_d in fine_cmds:
            c_hex = ch_hex_list[_map_palette_idx(bk_rgb[0], bk_rgb[1], bk_rgb[2], ch_meta)]
            f_buckets.setdefault(c_hex, []).append(g_d)
        for c_hex, segs in f_buckets.items():
            elems.append('<path stroke="%s" stroke-width="1.05" d="%s"/>' % (c_hex, "".join(segs)))
        b_buckets = {}
        for bk_rgb, g_d in bold_cmds:
            c_hex = ch_hex_list[_map_palette_idx(bk_rgb[0], bk_rgb[1], bk_rgb[2], ch_meta)]
            b_buckets.setdefault(c_hex, []).append(g_d)
        for c_hex, segs in b_buckets.items():
            elems.append('<path stroke="%s" stroke-width="1.35" d="%s"/>' % (c_hex, "".join(segs)))
        elems.append("</g>")

    if sparkles:
        sp_sz = num(max(7.8, rh * 0.98), 1)
        elems.append('<g font-family="%s" font-size="%s" font-weight="700" text-anchor="middle" aria-hidden="true">' % (FONT_MONO, sp_sz))
        for sx_p, sy_p, scol_h, sp_ch in sparkles:
            elems.append('<text x="%s" y="%s" fill="%s">%s</text>' % (num(sx_p, 1), num(sy_p, 1), scol_h, esc(sp_ch)))
        elems.append("</g>")

    elems.append("</g>")
    return elems


def van_gogh_garden_band(prefix, width, height, avoid_boxes=None, opacity_scale=0.99, glyph_stride=1, stroke_limit=3400, dim_boxes=None):
    return van_gogh_starry_backdrop(
        prefix,
        width,
        height,
        avoid_boxes=avoid_boxes,
        opacity_scale=opacity_scale,
        glyph_stride=glyph_stride,
        stroke_limit=stroke_limit,
        layer_key="garden",
        dim_boxes=dim_boxes,
    )


def render_day_night_cycle(prefix, width, height, zone_rects, sun_arc=None, moon_arc=None):
    # WHY: 60s continuous GPU-composited environmental cycle (Midnight -> Rose Dawn -> Arles Daylight -> Sunset -> Twilight) via opacity + translate3d.
    rects = zone_rects or [(0, 0, width, height, "sky")]
    sky_rect = next((r for r in rects if len(r) >= 5 and r[4] in ("sky", "panorama_sky")), rects[0])
    sx, sy, sw, raw_sh = sky_rect[0], sky_rect[1], sky_rect[2], sky_rect[3]
    is_pan = len(sky_rect) >= 5 and sky_rect[4] == "panorama_sky"
    sh = raw_sh * 0.64 if is_pan else raw_sh

    if sun_arc is None:
        sun_pts = [
            (0.00, sx + sw * 0.10, sy + sh * 0.94, 0.82),
            (22.5, sx + sw * 0.12, sy + sh * 0.86, 0.86),
            (28.0, sx + sw * 0.21, sy + sh * 0.54, 0.94),
            (35.0, sx + sw * 0.31, sy + max(32.0, sh * 0.31), 0.98),
            (44.0, sx + sw * 0.40, sy + max(28.0, sh * 0.22), 1.02),
            (53.3, sx + sw * 0.49, sy + max(26.0, sh * 0.19), 1.05),
            (62.0, sx + sw * 0.59, sy + max(28.0, sh * 0.23), 1.02),
            (70.0, sx + sw * 0.70, sy + max(34.0, sh * 0.34), 0.98),
            (78.0, sx + sw * 0.80, sy + sh * 0.56, 0.95),
            (85.5, sx + sw * 0.88, sy + sh * 0.86, 0.88),
            (100.0, sx + sw * 0.90, sy + sh * 0.95, 0.82),
        ]
    else:
        sun_pts = sun_arc

    if moon_arc is None:
        mx0, my0 = sx + sw * 0.83, sy + max(34.0, sh * 0.25)
        moon_pts = [
            (0.0, mx0, my0, 0.96, 1.00),
            (22.0, mx0 - sw * 0.03, my0 - sh * 0.02, 0.94, 1.00),
            (31.0, mx0 - sw * 0.06, my0 - sh * 0.04, 0.42, 0.94),
            (38.3, mx0 - sw * 0.09, my0 - sh * 0.05, 0.16, 0.90),
            (53.3, mx0 - sw * 0.11, my0 - sh * 0.05, 0.14, 0.88),
            (68.3, mx0 - sw * 0.07, my0 - sh * 0.03, 0.20, 0.92),
            (78.0, mx0 - sw * 0.03, my0 + sh * 0.01, 0.46, 0.96),
            (88.0, mx0 - sw * 0.01, my0 + sh * 0.01, 0.88, 0.99),
            (100.0, mx0, my0, 0.96, 1.00),
        ]
    else:
        moon_pts = moon_arc

    sun_op_map = {
        0.0: 0.0,
        22.5: 0.0,
        28.0: 0.84,
        35.0: 0.98,
        44.0: 1.0,
        53.3: 1.0,
        62.0: 1.0,
        70.0: 0.96,
        78.0: 0.82,
        85.5: 0.0,
        100.0: 0.0,
    }
    sun_kf_rules = []
    for pct, px_s, py_s, sc_s in sun_pts:
        op_v = sun_op_map.get(pct, 1.0 if 28.0 <= pct <= 78.0 else 0.0)
        sun_kf_rules.append(
            "%s%% { opacity: %s; transform: translate3d(%spx, %spx, 0px) scale(%s); }"
            % (num(pct, 1), num(op_v, 2), num(px_s, 1), num(py_s, 1), num(sc_s, 2))
        )

    moon_kf_rules = []
    for pct, px_m, py_m, op_m, sc_m in moon_pts:
        moon_kf_rules.append(
            "%s%% { opacity: %s; transform: translate3d(%spx, %spx, 0px) scale(%s); }"
            % (num(pct, 1), num(op_m, 2), num(px_m, 1), num(py_m, 1), num(sc_m, 2))
        )

    css = (
        "<style>"
        "@keyframes %(p)s-kf-dawn {"
        " 0%%, 21%% { opacity: 0; }"
        " 26%% { opacity: 0.42; }"
        " 30.8%% { opacity: 0.66; }"
        " 36%% { opacity: 0.34; }"
        " 41%%, 100%% { opacity: 0; }"
        "} "
        "@keyframes %(p)s-kf-day {"
        " 0%%, 23.3%% { opacity: 0; }"
        " 31%% { opacity: 0.30; }"
        " 38.3%% { opacity: 0.78; }"
        " 53.3%% { opacity: 0.84; }"
        " 68.3%% { opacity: 0.76; }"
        " 75.5%% { opacity: 0.26; }"
        " 82.5%%, 100%% { opacity: 0; }"
        "} "
        "@keyframes %(p)s-kf-dusk {"
        " 0%%, 65%% { opacity: 0; }"
        " 71%% { opacity: 0.44; }"
        " 76.7%% { opacity: 0.68; }"
        " 83%% { opacity: 0.38; }"
        " 89.5%% { opacity: 0.15; }"
        " 96%%, 100%% { opacity: 0; }"
        "} "
        "@keyframes %(p)s-kf-clouds {"
        " 0%%, 24%% { opacity: 0; transform: translate3d(-10px, 0px, 0px); }"
        " 34%% { opacity: 0.58; transform: translate3d(-4px, 0px, 0px); }"
        " 53.3%% { opacity: 0.88; transform: translate3d(6px, 0px, 0px); }"
        " 68.3%% { opacity: 0.78; transform: translate3d(12px, 0px, 0px); }"
        " 79%% { opacity: 0.36; transform: translate3d(15px, 0px, 0px); }"
        " 86%%, 100%% { opacity: 0; transform: translate3d(18px, 0px, 0px); }"
        "} "
        "@keyframes %(p)s-kf-meadow {"
        " 0%%, 24%% { opacity: 0; }"
        " 38.3%% { opacity: 0.82; }"
        " 53.3%% { opacity: 0.95; }"
        " 68.3%% { opacity: 0.82; }"
        " 78%% { opacity: 0.42; }"
        " 86%%, 100%% { opacity: 0; }"
        "} "
        "@keyframes %(p)s-kf-sun { %(sun_kf)s } "
        "@keyframes %(p)s-kf-moon { %(moon_kf)s } "
        "@keyframes %(p)s-kf-spin { 0%% { transform: rotate(0deg); } 100%% { transform: rotate(360deg); } } "
        ".%(p)s-dn-dawn { opacity: 0; will-change: opacity; animation: %(p)s-kf-dawn 60s linear infinite; } "
        ".%(p)s-dn-day { opacity: 0; will-change: opacity; animation: %(p)s-kf-day 60s linear infinite; } "
        ".%(p)s-dn-dusk { opacity: 0; will-change: opacity; animation: %(p)s-kf-dusk 60s linear infinite; } "
        ".%(p)s-dn-clouds { opacity: 0; will-change: transform, opacity; animation: %(p)s-kf-clouds 60s linear infinite; } "
        ".%(p)s-dn-meadow { opacity: 0; will-change: opacity; animation: %(p)s-kf-meadow 60s linear infinite; } "
        ".%(p)s-dn-sun { opacity: 0; will-change: transform, opacity; animation: %(p)s-kf-sun 60s linear infinite; } "
        ".%(p)s-dn-moon { opacity: 0.96; will-change: transform, opacity; animation: %(p)s-kf-moon 60s linear infinite; } "
        ".%(p)s-sun-spin { will-change: transform; animation: %(p)s-kf-spin 24s linear infinite; }"
        "</style>"
    ) % {
        "p": prefix,
        "sun_kf": " ".join(sun_kf_rules),
        "moon_kf": " ".join(moon_kf_rules),
    }

    out = [css, '<g class="cel-live" pointer-events="none">']
    for r_item in rects:
        rx, ry, rw, rh = r_item[0], r_item[1], r_item[2], r_item[3]
        rkind = r_item[4] if len(r_item) >= 5 else "sky"
        rx_s, ry_s, rw_s, rh_s = num(rx, 1), num(ry, 1), num(rw, 1), num(rh, 1)
        if rkind == "sky":
            out.append('<rect class="%s-dn-dawn" x="%s" y="%s" width="%s" height="%s" fill="url(#%s-dn-dawn-g)"/>' % (prefix, rx_s, ry_s, rw_s, rh_s, prefix))
            out.append('<rect class="%s-dn-day" x="%s" y="%s" width="%s" height="%s" fill="url(#%s-dn-day-g)"/>' % (prefix, rx_s, ry_s, rw_s, rh_s, prefix))
            out.append('<rect class="%s-dn-dusk" x="%s" y="%s" width="%s" height="%s" fill="url(#%s-dn-dusk-g)"/>' % (prefix, rx_s, ry_s, rw_s, rh_s, prefix))
        elif rkind == "panorama_sky":
            out.append('<rect class="%s-dn-dawn" x="%s" y="%s" width="%s" height="%s" fill="url(#%s-dn-pan-dawn-g)"/>' % (prefix, rx_s, ry_s, rw_s, rh_s, prefix))
            out.append('<rect class="%s-dn-day" x="%s" y="%s" width="%s" height="%s" fill="url(#%s-dn-pan-day-g)"/>' % (prefix, rx_s, ry_s, rw_s, rh_s, prefix))
            out.append('<rect class="%s-dn-dusk" x="%s" y="%s" width="%s" height="%s" fill="url(#%s-dn-pan-dusk-g)"/>' % (prefix, rx_s, ry_s, rw_s, rh_s, prefix))
        elif rkind == "meadow":
            out.append('<rect class="%s-dn-meadow" x="%s" y="%s" width="%s" height="%s" fill="url(#%s-dn-meadow-g)"/>' % (prefix, rx_s, ry_s, rw_s, rh_s, prefix))
        elif rkind == "water":
            out.append('<rect class="%s-dn-meadow" x="%s" y="%s" width="%s" height="%s" fill="url(#%s-dn-water-g)"/>' % (prefix, rx_s, ry_s, rw_s, rh_s, prefix))
        elif rkind == "ambient":
            out.append(
                '<g opacity="0.10">'
                '<rect class="%s-dn-day" x="%s" y="%s" width="%s" height="%s" fill="url(#%s-dn-day-g)"/>'
                '<rect class="%s-dn-dusk" x="%s" y="%s" width="%s" height="%s" fill="url(#%s-dn-dusk-g)"/>'
                "</g>" % (prefix, rx_s, ry_s, rw_s, rh_s, prefix, prefix, rx_s, ry_s, rw_s, rh_s, prefix)
            )

    c1x, c1y = sx + sw * 0.20, sy + sh * 0.30
    c2x, c2y = sx + sw * 0.62, sy + sh * 0.26
    c3x, c3y = sx + sw * 0.82, sy + sh * 0.38
    cw_u = max(44.0, sw * 0.085)

    out.append('<g class="%s-dn-clouds">' % prefix)
    for cx_b, cy_b, c_sc in ((c1x, c1y, 1.0), (c2x, c2y, 1.12), (c3x, c3y, 0.86)):
        rx_m = cw_u * c_sc
        ry_m = max(9.0, rx_m * 0.24)
        out.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="#e0f2fe" fill-opacity="0.22"/>' % (num(cx_b, 1), num(cy_b + 2.0, 1), num(rx_m * 1.08, 1), num(ry_m * 0.85, 1)))
        out.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="#fefce8" fill-opacity="0.28"/>' % (num(cx_b - rx_m * 0.24, 1), num(cy_b - 2.5, 1), num(rx_m * 0.62, 1), num(ry_m * 0.92, 1)))
        out.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="#fef9c3" fill-opacity="0.26"/>' % (num(cx_b + rx_m * 0.22, 1), num(cy_b - 1.5, 1), num(rx_m * 0.56, 1), num(ry_m * 0.82, 1)))
        d_rim = "M%s,%s Q%s,%s %s,%s Q%s,%s %s,%s" % (
            num(cx_b - rx_m * 0.72, 1), num(cy_b + 1.0, 1),
            num(cx_b - rx_m * 0.26, 1), num(cy_b - ry_m * 1.25, 1),
            num(cx_b + rx_m * 0.04, 1), num(cy_b - ry_m * 0.45, 1),
            num(cx_b + rx_m * 0.36, 1), num(cy_b - ry_m * 1.05, 1),
            num(cx_b + rx_m * 0.72, 1), num(cy_b + 1.5, 1),
        )
        out.append('<path d="%s" fill="none" stroke="#fef08a" stroke-width="1.35" stroke-linecap="round" stroke-opacity="0.54"/>' % d_rim)
    out.append("</g>")

    out.append('<g class="%s-dn-moon"><use href="#%s-moon-glyph"/></g>' % (prefix, prefix))
    out.append('<g class="%s-dn-sun"><g class="%s-sun-spin"><use href="#%s-sun-glyph"/></g></g>' % (prefix, prefix, prefix))
    out.append("</g>")

    calm_mx, calm_my = moon_pts[0][1], moon_pts[0][2]
    calm_grad = "%s-dn-pan-dusk-g" if is_pan else "%s-dn-dusk-g"
    out.append(
        '<g class="cel-calm" pointer-events="none">'
        '<rect x="%s" y="%s" width="%s" height="%s" fill="url(#%s)" opacity="0.14"/>'
        '<g transform="translate(%s %s) scale(0.96)"><use href="#%s-moon-glyph"/></g>'
        "</g>"
        % (num(sx, 1), num(sy, 1), num(sw, 1), num(raw_sh, 1), calm_grad % prefix, num(calm_mx, 1), num(calm_my, 1), prefix)
    )
    return out


def _meteor_body_markup(prefix, tail_len):
    tl = float(tail_len)
    core_l = tl * 0.78
    hot_l = tl * 0.48
    outer_pts = "4,0 -7,-8.2 -%s,0 -7,8.2" % num(tl, 1)
    core_pts = "4,0 -5,-4.5 -%s,0 -5,4.5" % num(core_l, 1)
    head_star4 = star_path(0, 0, 18.2, 3.2, 4, 0.0)
    head_star8 = star_path(0, 0, 10.2, 3.0, 8, 22.5)
    embers = [
        (-tl * 0.14, -3.4, 3.8, "#ffffff"),
        (-tl * 0.26, 3.9, 3.5, "#fef08a"),
        (-tl * 0.39, -4.6, 3.2, "#38bdf8"),
        (-tl * 0.52, 3.1, 2.9, "#fbbf24"),
        (-tl * 0.66, -3.5, 2.6, "#7dd3fc"),
        (-tl * 0.79, 2.5, 2.3, "#fde047"),
        (-tl * 0.91, -2.0, 2.0, "#fb923c"),
    ]
    em_svg = "".join(
        '<path d="%s" fill="%s"/>' % (star_path(ex, ey, er, er * 0.38, 4, 0.0), ecol)
        for ex, ey, er, ecol in embers
    )
    return (
        '<polygon points="%s" fill="url(#%s-mtail-outer)"/>'
        '<polygon points="%s" fill="url(#%s-mtail-core)"/>'
        '<line x1="3" y1="0" x2="-%s" y2="0" stroke="#ffffff" stroke-width="2.6" stroke-linecap="round"/>'
        '<g class="%s-ember-tw">%s</g>'
        '<circle cx="0" cy="0" r="20.5" fill="url(#%s-mhead-cyan)"/>'
        '<path d="M 4.2,-10.4 Q 14.8,0 4.2,10.4" fill="none" stroke="#38bdf8" stroke-width="1.85" stroke-linecap="round" stroke-opacity="0.92"/>'
        '<circle cx="0" cy="0" r="12.2" fill="url(#%s-mhead-gold)"/>'
        '<path d="%s" fill="#fef08a"/>'
        '<path d="%s" fill="#ffffff"/>'
        '<circle cx="0" cy="0" r="3.9" fill="#ffffff"/>'
        % (outer_pts, prefix, core_pts, prefix, num(hot_l, 1), prefix, em_svg, prefix, prefix, head_star4, head_star8)
    )


def render_giant_meteors(prefix, width, height, trajectories=None):
    # WHY: Launches 4 large shooting stars every 10s (dur=10s) along staggered diagonal sky trajectories using GPU translate3d + opacity.
    if trajectories is None:
        sky_h = min(height * 0.56, 232.0)
        specs = [
            (0.40, 1.95, width * 0.09, 22.0, width * 0.54, sky_h * 0.88, 196.0),
            (2.70, 4.30, width * 0.91, 20.0, width * 0.44, sky_h * 0.94, 216.0),
            (4.85, 6.45, width * 0.35, 16.0, width * 0.83, sky_h * 0.82, 178.0),
            (7.55, 9.20, width * 0.76, 18.0, width * 0.23, sky_h * 0.92, 220.0),
        ]
    else:
        specs = trajectories

    css_parts = [
        "<style>",
        "@keyframes %s-kf-ember { 0%%, 100%% { opacity: 0.52; } 50%% { opacity: 1; } } " % prefix,
        ".%s-ember-tw { will-change: opacity; animation: %s-kf-ember 0.28s linear infinite; } " % (prefix, prefix),
    ]
    meteor_nodes = []

    for idx, (t0, t1, x0, y0, x1, y1, tail_l) in enumerate(specs, start=1):
        dx = x1 - x0
        dy = y1 - y0
        dist = math.hypot(dx, dy)
        ang = math.degrees(math.atan2(dy, dx))

        p_pre = max(0.0, round(t0 * 10.0 - 0.2, 2))
        p_on = round((t0 + (t1 - t0) * 0.16) * 10.0, 2)
        p_mid = round((t0 + (t1 - t0) * 0.52) * 10.0, 2)
        p_fade = round((t0 + (t1 - t0) * 0.80) * 10.0, 2)
        p_end = min(99.8, round(t1 * 10.0, 2))

        css_parts.append(
            "@keyframes %(p)s-kf-m%(i)d {"
            " 0%%, %(pre)s%% { opacity: 0; transform: translate3d(0px, 0px, 0px) scaleX(0.38); }"
            " %(on)s%% { opacity: 1; transform: translate3d(%(d1)spx, 0px, 0px) scaleX(0.96); }"
            " %(mid)s%% { opacity: 1; transform: translate3d(%(dm)spx, 0px, 0px) scaleX(1.06); }"
            " %(fade)s%% { opacity: 0.92; transform: translate3d(%(df)spx, 0px, 0px) scaleX(0.98); }"
            " %(end)s%%, 100%% { opacity: 0; transform: translate3d(%(d2)spx, 0px, 0px) scaleX(0.52); }"
            "} "
            "@keyframes %(p)s-kf-mf%(i)d {"
            " 0%%, %(pre)s%% { opacity: 0; }"
            " %(mid)s%% { opacity: 0.44; }"
            " %(end)s%%, 100%% { opacity: 0; }"
            "} "
            ".%(p)s-m%(i)d { opacity: 0; will-change: transform, opacity; animation: %(p)s-kf-m%(i)d 10s linear infinite; } "
            ".%(p)s-mf%(i)d { opacity: 0; will-change: opacity; animation: %(p)s-kf-mf%(i)d 10s linear infinite; } "
            % {
                "p": prefix,
                "i": idx,
                "pre": num(p_pre, 2),
                "on": num(p_on, 2),
                "mid": num(p_mid, 2),
                "fade": num(p_fade, 2),
                "end": num(p_end, 2),
                "d1": num(dist * 0.18, 1),
                "dm": num(dist * 0.54, 1),
                "df": num(dist * 0.82, 1),
                "d2": num(dist, 1),
            }
        )

        meteor_nodes.append(
            '<g transform="translate(%s %s) rotate(%s)">'
            '<ellipse class="%s-mf%d" cx="%s" cy="0" rx="%s" ry="20" fill="url(#%s-mflash-g)"/>'
            '<g class="%s-m%d">%s</g>'
            "</g>"
            % (
                num(x0, 1),
                num(y0, 1),
                num(ang, 1),
                prefix,
                idx,
                num(dist * 0.48, 1),
                num(dist * 0.46, 1),
                prefix,
                prefix,
                idx,
                _meteor_body_markup(prefix, tail_l),
            )
        )

    css_parts.append("</style>")
    return ["".join(css_parts), '<g class="cel-live" pointer-events="none">', "".join(meteor_nodes), "</g>"]


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
        '<g transform="translate(%s %s) rotate(%s)" pointer-events="none">'
        % (num(cx, 1), num(cy, 1), num(tilt_deg, 1))
    ]
    elems.append('<circle cx="0" cy="0" r="22" fill="%s" fill-opacity="0.12"/>' % CADMIUM)
    elems.append('<circle cx="0" cy="0" r="14.5" fill="none" stroke="%s" stroke-width="0.6" stroke-dasharray="2.4 2" stroke-opacity="0.58"/>' % CREAM)
    elems.append('<path d="%s" fill="%s" stroke="%s" stroke-width="0.75"/>' % (star_path(0, 0, 12.2, 4.3, 8), FIREFLY_GOLD, IVORY_WARM))
    elems.append('<path d="%s" fill="#ffffff"/>' % star_path(0, 0, 5.8, 2.1, 4))

    comet_rx = scale_x * 0.78
    comet_ry = scale_y * 0.44
    peri_x = -comet_rx * 0.36
    aphe_x = comet_rx * 1.64
    comet_cx = (peri_x + aphe_x) * 0.5
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
    orr_css = ["<style>"]
    cm_kf = []
    for st_i in range(13):
        ang_c = math.pi + (2.0 * math.pi * st_i / 12.0)
        cx_p = comet_cx + comet_rx * math.cos(ang_c)
        cy_p = comet_ry * math.sin(ang_c)
        rot_p = math.degrees(math.atan2(comet_ry * math.cos(ang_c), -comet_rx * math.sin(ang_c)))
        cm_kf.append("%s%%{transform:translate3d(%spx,%spx,0) rotate(%sdeg)}" % (num(st_i * 100.0 / 12.0, 1), num(cx_p, 1), num(cy_p, 1), num(rot_p, 1)))
    orr_css.append("@keyframes orr-cm{%s}.orr-cm{will-change:transform;animation:orr-cm 28s linear infinite}" % "".join(cm_kf))

    planet_nodes = [
        '<g class="pup-live" transform="rotate(17)"><g class="orr-cm">%s</g></g>'
        '<g class="pup-calm" transform="rotate(17) translate(%s 0)">%s</g>'
        % (comet_glyph, num(peri_x, 1), comet_glyph)
    ]

    for p_idx, (name, rf, pr, pcol, dur, phase_deg, has_ring) in enumerate(planets):
        rx = scale_x * rf
        ry = scale_y * rf
        elems.append(
            '<ellipse cx="0" cy="0" rx="%s" ry="%s" fill="none" stroke="%s" stroke-width="0.58" stroke-opacity="0.36"/>'
            % (num(rx, 1), num(ry, 1), MILKY_DUST if rf > 0.5 else CREAM)
        )
        p_kf = []
        p0_rad = math.radians(phase_deg)
        for st_i in range(13):
            ang_p = p0_rad + (2.0 * math.pi * st_i / 12.0)
            px_o = -rx * math.cos(ang_p)
            py_o = -ry * math.sin(ang_p)
            p_kf.append("%s%%{transform:translate3d(%spx,%spx,0)}" % (num(st_i * 100.0 / 12.0, 1), num(px_o, 1), num(py_o, 1)))
        orr_css.append("@keyframes orr-p%d{%s}.orr-p%d{will-change:transform;animation:orr-p%d %s linear infinite}" % (p_idx, "".join(p_kf), p_idx, p_idx, dur))

        body_parts = []
        if has_ring:
            body_parts.append('<ellipse cx="0" cy="0" rx="%s" ry="%s" transform="rotate(-18)" fill="none" stroke="%s" stroke-width="1.05" stroke-opacity="0.92"/>' % (num(pr * 2.45, 1), num(pr * 0.86, 1), IVORY_WARM))
        if name == "Uranus":
            body_parts.append('<ellipse cx="0" cy="0" rx="%s" ry="%s" transform="rotate(72)" fill="none" stroke="%s" stroke-width="0.72"/>' % (num(pr * 1.9, 1), num(pr * 0.65, 1), SKY_SOFT))
        body_parts.append('<path d="%s" fill="%s" stroke="#081226" stroke-width="0.45"/>' % (star_path(0, 0, pr * 1.38, pr * 0.68, 6), pcol))
        body_parts.append('<circle cx="0" cy="0" r="%s" fill="#ffffff" fill-opacity="0.78"/>' % num(max(0.7, pr * 0.28), 1))
        planet_svg = "".join(body_parts)
        st_x = -rx * math.cos(p0_rad)
        st_y = -ry * math.sin(p0_rad)
        planet_nodes.append(
            '<g class="pup-live orr-p%d">%s</g>'
            '<g class="pup-calm" transform="translate(%s %s)">%s</g>'
            % (p_idx, planet_svg, num(st_x, 1), num(st_y, 1), planet_svg)
        )

    orr_css.append("</style>")
    elems.append("".join(orr_css))
    elems.extend(planet_nodes)

    elems.append("</g>")
    return elems
