import math

FONT_MONO = "'JetBrains Mono', 'Fira Code', ui-monospace, SFMono-Regular, Menlo, monospace"
FONT_DISPLAY = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif"

BG_NIGHT = "#050914"
BG_CARD_TOP = "#091326"
BG_CARD_BOT = "#050a16"
BG_WELL = "#050914"
BG_CONSOLE = "#040812"

PRUSSIAN = "#13294b"
COBALT = "#1e4278"
ULTRAMARINE = "#2f5fa8"
CERULEAN = "#60a5fa"
MILKY_DUST = "#93c5fd"
MILKY_CORE = "#dbeafe"

BORDER_SUBTLE = "#1a2942"
BORDER_WARM = "#2c4166"

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
INK_SECOND = "#c2d2e9"
INK_MUTED = "#8da2c0"
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
        'fill="%s" text-anchor="%s"%s>%s</text>'
        % (num(x), num(y), family, num(size), weight, fill, anchor, extra, inner)
    )


def star_path(cx, cy, outer_r, inner_r, points=5):
    pts = []
    total = points * 2
    for i in range(total):
        angle = -math.pi / 2.0 + i * math.pi / float(points)
        r = outer_r if i % 2 == 0 else inner_r
        pts.append("%s,%s" % (num(cx + math.cos(angle) * r), num(cy + math.sin(angle) * r)))
    return "M" + " L".join(pts) + " Z"


def compact(value):
    for suffix, scale in (("B", 1000000000.0), ("M", 1000000.0), ("K", 1000.0)):
        if value >= scale:
            return "%.1f%s" % (value / scale, suffix)
    return str(int(value))


def _rng(seed):
    state = seed & 0xFFFFFFFF
    while True:
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        yield (state >> 8) / float(0xFFFFFF)


def nocturne_defs(prefix):
    return [
        '<linearGradient id="%s-bg" x1="0" y1="0" x2="0.15" y2="1">' % prefix,
        '<stop offset="0%%" stop-color="%s"/>' % BG_CARD_TOP,
        '<stop offset="52%%" stop-color="#071020"/>',
        '<stop offset="100%%" stop-color="%s"/>' % BG_CARD_BOT,
        "</linearGradient>",
        '<linearGradient id="%s-sheen" x1="0" y1="0" x2="1" y2="0">' % prefix,
        '<stop offset="0%%" stop-color="%s" stop-opacity="0"/>' % CREAM,
        '<stop offset="28%%" stop-color="%s" stop-opacity="0.32"/>' % SKY_SOFT,
        '<stop offset="56%%" stop-color="%s" stop-opacity="0.42"/>' % CREAM,
        '<stop offset="82%%" stop-color="%s" stop-opacity="0.22"/>' % SKY_SOFT,
        '<stop offset="100%%" stop-color="%s" stop-opacity="0"/>' % CREAM,
        "</linearGradient>",
        '<linearGradient id="%s-milky" x1="0" y1="0.88" x2="1" y2="0.12">' % prefix,
        '<stop offset="0%%" stop-color="%s" stop-opacity="0"/>' % PRUSSIAN,
        '<stop offset="22%%" stop-color="%s" stop-opacity="0.14"/>' % COBALT,
        '<stop offset="48%%" stop-color="%s" stop-opacity="0.22"/>' % MILKY_DUST,
        '<stop offset="66%%" stop-color="%s" stop-opacity="0.18"/>' % CREAM,
        '<stop offset="86%%" stop-color="%s" stop-opacity="0.12"/>' % ULTRAMARINE,
        '<stop offset="100%%" stop-color="%s" stop-opacity="0"/>' % PRUSSIAN,
        "</linearGradient>",
        '<radialGradient id="%s-ff-gold" cx="50%%" cy="50%%" r="50%%">' % prefix,
        '<stop offset="0%%" stop-color="%s" stop-opacity="0.98"/>' % IVORY_WARM,
        '<stop offset="26%%" stop-color="%s" stop-opacity="0.62"/>' % CADMIUM,
        '<stop offset="62%%" stop-color="%s" stop-opacity="0.18"/>' % FIREFLY_AMBER,
        '<stop offset="100%%" stop-color="%s" stop-opacity="0"/>' % FIREFLY_AMBER,
        "</radialGradient>",
        '<radialGradient id="%s-ff-white" cx="50%%" cy="50%%" r="50%%">' % prefix,
        '<stop offset="0%%" stop-color="#ffffff" stop-opacity="0.96"/>',
        '<stop offset="30%%" stop-color="%s" stop-opacity="0.48"/>' % SKY_SOFT,
        '<stop offset="70%%" stop-color="%s" stop-opacity="0.12"/>' % ULTRAMARINE,
        '<stop offset="100%%" stop-color="%s" stop-opacity="0"/>' % ULTRAMARINE,
        "</radialGradient>",
        '<radialGradient id="%s-moon-halo" cx="50%%" cy="50%%" r="50%%">' % prefix,
        '<stop offset="0%%" stop-color="%s" stop-opacity="0.52"/>' % CADMIUM,
        '<stop offset="38%%" stop-color="%s" stop-opacity="0.24"/>' % FIREFLY_GOLD,
        '<stop offset="72%%" stop-color="%s" stop-opacity="0.08"/>' % SKY_SOFT,
        '<stop offset="100%%" stop-color="%s" stop-opacity="0"/>' % BG_NIGHT,
        "</radialGradient>",
        '<filter id="%s-bloom" x="-40%%" y="-40%%" width="180%%" height="180%%">' % prefix,
        '<feGaussianBlur stdDeviation="2.3" result="b"/>',
        '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>',
        "</filter>",
        '<filter id="%s-nebula" x="-25%%" y="-25%%" width="150%%" height="150%%">' % prefix,
        '<feGaussianBlur stdDeviation="22"/>',
        "</filter>",
    ]


def nocturne_card(width, height, prefix, radius=16):
    return [
        '<clipPath id="%s-clip"><rect x="1" y="1" width="%s" height="%s" rx="%s"/></clipPath>'
        % (prefix, num(width - 2), num(height - 2), num(radius)),
    ], [
        '<rect x="1" y="1" width="%s" height="%s" rx="%s" fill="url(#%s-bg)" stroke="%s" stroke-width="1.1"/>'
        % (num(width - 2), num(height - 2), num(radius), prefix, BORDER_WARM),
        '<line x1="32" y1="1.5" x2="%s" y2="1.5" stroke="url(#%s-sheen)" stroke-width="1.15"/>'
        % (num(width - 32), prefix),
    ]


def _inside_boxes(px, py, boxes):
    for bx, by, bw, bh in boxes:
        if bx <= px <= bx + bw and by <= py <= by + bh:
            return True
    return False


def van_gogh_starry_backdrop(
    prefix,
    width,
    height,
    seed=1889,
    avoid_boxes=None,
    moon_pos=None,
    vortex_centers=None,
    stroke_count=120,
    star_aureoles=7,
    opacity_scale=1.0,
):
    # WHY: Models Saint-Remy Starry Night curl turbulence + diagonal Milky Way spine while keeping foreground text contrast crisp.
    gen = _rng(seed)
    boxes = avoid_boxes or []
    elems = ['<g pointer-events="none">']

    # 1. Soft Feathered Milky Way Galactic Core Nebula Clouds (no hard stripe edges)
    mw_y0 = height * 0.84
    mw_y1 = height * 0.12
    elems.append('<g filter="url(#%s-nebula)" opacity="%s">' % (prefix, num(0.88 * opacity_scale, 2)))
    nebula_nodes = (
        (0.16, 0.74, width * 0.18, height * 0.20, COBALT, 0.34),
        (0.36, 0.56, width * 0.22, height * 0.22, ULTRAMARINE, 0.30),
        (0.54, 0.42, width * 0.20, height * 0.19, MILKY_DUST, 0.22),
        (0.72, 0.28, width * 0.19, height * 0.18, CERULEAN, 0.26),
        (0.88, 0.18, width * 0.15, height * 0.16, CREAM, 0.16),
    )
    for nx_f, ny_f, rx_n, ry_n, ncol, nop in nebula_nodes:
        elems.append(
            '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" transform="rotate(-21 %s %s)" fill="%s" fill-opacity="%s"/>'
            % (
                num(width * nx_f, 1), num(height * ny_f, 1),
                num(rx_n, 1), num(ry_n, 1),
                num(width * nx_f, 1), num(height * ny_f, 1),
                ncol, num(nop, 2),
            )
        )
    elems.append("</g>")

    # 2. Van Gogh Turbulent Curl-Field Impasto Brushstrokes
    if vortex_centers is None:
        vortex_centers = [
            (width * 0.44, height * 0.42, 1.35, min(width, height) * 0.34),
            (width * 0.63, height * 0.56, -1.05, min(width, height) * 0.24),
            (width * 0.22, height * 0.30, 0.80, min(width, height) * 0.26),
        ]

    def flow_vec(px, py):
        vx = 0.85
        vy = -0.16 + 0.24 * math.sin(px * 0.011)
        for cx_v, cy_v, strength, rad_v in vortex_centers:
            dx = px - cx_v
            dy = py - cy_v
            d2 = dx * dx + dy * dy + 180.0
            falloff = math.exp(-d2 / (2.0 * rad_v * rad_v))
            inv_r = 1.0 / math.sqrt(d2)
            vx += (-dy * inv_r) * strength * falloff * 2.1
            vy += (dx * inv_r) * strength * falloff * 2.1
        mag = math.hypot(vx, vy) or 1.0
        return vx / mag, vy / mag

    impasto_palette = (
        (PRUSSIAN, 0.42),
        (COBALT, 0.38),
        (ULTRAMARINE, 0.34),
        (CERULEAN, 0.24),
        (TEAL_MIST, 0.18),
        (CREAM, 0.22),
        (FIREFLY_GOLD, 0.20),
    )

    elems.append('<g stroke-linecap="round" fill="none">')
    placed = 0
    tries = 0
    while placed < stroke_count and tries < stroke_count * 5:
        tries += 1
        sx = 12.0 + next(gen) * (width - 24.0)
        sy = 10.0 + next(gen) * (height - 20.0)
        if _inside_boxes(sx, sy, boxes):
            continue
        placed += 1
        step_len = 8.0 + next(gen) * 11.0
        v1x, v1y = flow_vec(sx, sy)
        mx = sx + v1x * step_len
        my = sy + v1y * step_len
        v2x, v2y = flow_vec(mx, my)
        ex = mx + v2x * step_len
        ey = my + v2y * step_len
        if _inside_boxes(ex, ey, boxes):
            continue
        pal_idx = int(next(gen) * len(impasto_palette)) % len(impasto_palette)
        col, base_op = impasto_palette[pal_idx]
        sw = 1.0 + next(gen) * 1.65
        op = base_op * opacity_scale * (0.72 + next(gen) * 0.42)
        if placed % 9 == 0:
            dur = 6.5 + next(gen) * 7.5
            elems.append(
                '<path d="M%s,%s Q%s,%s %s,%s" stroke="%s" stroke-width="%s" stroke-opacity="%s">'
                '<animate attributeName="stroke-opacity" values="%s;%s;%s" dur="%ss" repeatCount="indefinite"/>'
                "</path>"
                % (
                    num(sx, 1), num(sy, 1), num(mx, 1), num(my, 1), num(ex, 1), num(ey, 1),
                    col, num(sw, 2), num(op, 2),
                    num(op * 0.45, 2), num(min(0.65, op * 1.55), 2), num(op * 0.45, 2), num(dur, 1),
                )
            )
        else:
            elems.append(
                '<path d="M%s,%s Q%s,%s %s,%s" stroke="%s" stroke-width="%s" stroke-opacity="%s"/>'
                % (num(sx, 1), num(sy, 1), num(mx, 1), num(my, 1), num(ex, 1), num(ey, 1), col, num(sw, 2), num(op, 2))
            )
    elems.append("</g>")

    # 3. Flowing Liquid-Sky Impasto Stream Ribbons
    for ri in range(2):
        ry_base = height * (0.31 + ri * 0.25)
        r_col = CERULEAN if ri == 0 else CADMIUM
        ribbon = "M%s,%s C%s,%s %s,%s %s,%s S%s,%s %s,%s" % (
            num(24, 0), num(ry_base, 1),
            num(width * 0.24, 1), num(ry_base - 34 + ri * 14, 1),
            num(width * 0.45, 1), num(ry_base + 38 - ri * 12, 1),
            num(width * 0.62, 1), num(ry_base - 12, 1),
            num(width * 0.84, 1), num(ry_base + 24, 1),
            num(width - 24, 0), num(ry_base - 16, 1),
        )
        elems.append(
            '<path d="%s" fill="none" stroke="%s" stroke-width="1.35" stroke-dasharray="10 14 5 12" stroke-linecap="round" stroke-opacity="%s">'
            '<animate attributeName="stroke-dashoffset" from="0" to="%d" dur="%ds" repeatCount="indefinite"/>'
            "</path>"
            % (ribbon, r_col, num(0.24 * opacity_scale, 2), -82 if ri == 0 else 82, 19 + ri * 5)
        )

    # 4. Milky Way Fine Starfield Dust
    dust_n = int(stroke_count * 0.65)
    for i in range(dust_n):
        t = next(gen)
        # Cluster 65% along the diagonal Milky Way band
        if next(gen) < 0.65:
            spread = (next(gen) - 0.5) * height * 0.42
            px = t * width
            py = mw_y0 * (1.0 - t) + mw_y1 * t + spread
        else:
            px = 14.0 + next(gen) * (width - 28.0)
            py = 12.0 + next(gen) * (height - 24.0)
        if not (8.0 <= px <= width - 8.0 and 8.0 <= py <= height - 8.0):
            continue
        if _inside_boxes(px, py, boxes):
            continue
        sr = 0.55 + next(gen) * 0.95
        scol = MILKY_CORE if next(gen) > 0.38 else CREAM
        sop = (0.22 + next(gen) * 0.48) * opacity_scale
        elems.append('<circle cx="%s" cy="%s" r="%s" fill="%s" fill-opacity="%s"/>' % (
            num(px, 1), num(py, 1), num(sr, 2), scol, num(sop, 2)
        ))

    # 5. Van Gogh Concentric Impasto Star Aureoles
    a_placed = 0
    a_tries = 0
    while a_placed < star_aureoles and a_tries < star_aureoles * 10:
        a_tries += 1
        ax = 36.0 + next(gen) * (width - 72.0)
        ay = 26.0 + next(gen) * (height - 52.0)
        if _inside_boxes(ax, ay, boxes):
            continue
        if moon_pos and math.hypot(ax - moon_pos[0], ay - moon_pos[1]) < moon_pos[2] * 2.4:
            continue
        a_placed += 1
        base_r = 4.5 + next(gen) * 5.2
        is_warm = next(gen) > 0.30
        ring_col = CADMIUM if is_warm else SKY_SOFT
        grad_ref = "%s-ff-gold" % prefix if is_warm else "%s-ff-white" % prefix
        dur = 4.2 + next(gen) * 4.8
        elems.append('<g transform="translate(%s %s)">' % (num(ax, 1), num(ay, 1)))
        elems.append('<circle cx="0" cy="0" r="%s" fill="url(#%s)" opacity="%s"/>' % (
            num(base_r * 2.1, 1), grad_ref, num(0.68 * opacity_scale, 2)
        ))
        elems.append(
            '<circle cx="0" cy="0" r="%s" fill="none" stroke="%s" stroke-width="1.05" stroke-dasharray="3.2 2.6" stroke-linecap="round" stroke-opacity="%s">'
            '<animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="%ss" repeatCount="indefinite"/>'
            "</circle>"
            % (num(base_r, 1), ring_col, num(0.50 * opacity_scale, 2), num(18.0 + a_placed * 3.5, 1))
        )
        elems.append(
            '<circle cx="0" cy="0" r="%s" fill="none" stroke="%s" stroke-width="0.85" stroke-dasharray="4.5 3.8" stroke-linecap="round" stroke-opacity="%s"/>'
            % (num(base_r * 1.55, 1), CREAM if is_warm else MILKY_DUST, num(0.30 * opacity_scale, 2))
        )
        elems.append(
            '<circle cx="0" cy="0" r="%s" fill="#ffffff">'
            '<animate attributeName="opacity" values="0.55;1;0.55" dur="%ss" repeatCount="indefinite"/>'
            "</circle>"
            % (num(1.35 + next(gen) * 0.65, 2), num(dur, 1))
        )
        elems.append("</g>")

    # 6. Saint-Remy Waning Crescent Moon with Concentric Impasto Corona
    if moon_pos is not None:
        mx, my, mr = moon_pos
        elems.append('<g transform="translate(%s %s)">' % (num(mx, 1), num(my, 1)))
        elems.append('<circle cx="0" cy="0" r="%s" fill="url(#%s-moon-halo)" opacity="%s"/>' % (
            num(mr * 2.9, 1), prefix, num(0.92 * opacity_scale, 2)
        ))
        for ring_k, dash_pat, r_col, r_op in (
            (1.32, "5 3.5", CADMIUM, 0.65),
            (1.72, "7 4.5", CREAM, 0.44),
            (2.15, "6 5.5", SKY_SOFT, 0.28),
        ):
            elems.append(
                '<circle cx="0" cy="0" r="%s" fill="none" stroke="%s" stroke-width="1.25" stroke-dasharray="%s" stroke-linecap="round" stroke-opacity="%s">'
                '<animateTransform attributeName="transform" type="rotate" from="0" to="%d" dur="%ds" repeatCount="indefinite"/>'
                "</circle>"
                % (
                    num(mr * ring_k, 1), r_col, dash_pat, num(r_op * opacity_scale, 2),
                    360 if ring_k != 1.72 else -360, int(28 + ring_k * 10),
                )
            )
        # Sculpted waning crescent moon path
        r_in = mr * 0.78
        crescent_d = "M 0,%s A %s,%s 0 1,1 0,%s A %s,%s 0 1,0 0,%s Z" % (
            num(-mr, 1), num(mr, 1), num(mr, 1), num(mr, 1),
            num(r_in, 1), num(r_in * 0.92, 1), num(-mr, 1),
        )
        elems.append('<path d="%s" transform="rotate(-24)" fill="%s" stroke="%s" stroke-width="0.9"/>' % (
            crescent_d, CRESCENT_ORANGE, CADMIUM
        ))
        elems.append("</g>")

    elems.append("</g>")
    return elems


def solar_system_orrery(prefix, cx, cy, scale_x=185.0, scale_y=52.0, tilt_deg=-11.0, opacity=0.88):
    # WHY: Accurate 8-planet heliocentric order (Mercury..Neptune) with Keplerian relative periods & Saturn ring geometry.
    planets = [
        ("Mercury", 0.18, 1.6, "#cbd5e1", "7s", 25, False),
        ("Venus", 0.27, 2.2, "#fde68a", "11s", 110, False),
        ("Earth", 0.38, 2.5, "#38bdf8", "16s", 215, False),
        ("Mars", 0.49, 2.0, "#fb7185", "22s", 310, False),
        ("Jupiter", 0.64, 3.8, "#fbbf24", "32s", 55, False),
        ("Saturn", 0.79, 3.2, "#fcd34d", "44s", 168, True),
        ("Uranus", 0.90, 2.4, "#67e8f9", "58s", 265, False),
        ("Neptune", 1.00, 2.3, "#60a5fa", "72s", 340, False),
    ]
    elems = [
        '<g transform="translate(%s %s) rotate(%s)" opacity="%s" pointer-events="none">'
        % (num(cx, 1), num(cy, 1), num(tilt_deg, 1), num(opacity, 2))
    ]
    # Heliocentric Sun core & corona
    elems.append('<circle cx="0" cy="0" r="18" fill="url(#%s-ff-gold)"/>' % prefix)
    elems.append('<circle cx="0" cy="0" r="5.6" fill="%s" stroke="#ffffff" stroke-width="0.9"/>' % FIREFLY_GOLD)
    elems.append('<circle cx="0" cy="0" r="2.5" fill="#ffffff"/>')

    for name, rf, pr, pcol, dur, phase_deg, has_ring in planets:
        rx = scale_x * rf
        ry = scale_y * rf
        orbit_d = "M %s,0 A %s,%s 0 1,1 %s,0 A %s,%s 0 1,1 %s,0" % (
            num(-rx, 1), num(rx, 1), num(ry, 1), num(rx, 1),
            num(rx, 1), num(ry, 1), num(-rx, 1),
        )
        elems.append(
            '<ellipse cx="0" cy="0" rx="%s" ry="%s" fill="none" stroke="%s" stroke-width="0.75" stroke-opacity="0.34" stroke-dasharray="%s"/>'
            % (num(rx, 1), num(ry, 1), MILKY_DUST if rf > 0.5 else CREAM, "2 3" if rf in (0.49, 0.90) else "none")
        )
        neg_begin = -round((phase_deg / 360.0) * float(dur.rstrip("s")), 1)
        elems.append("<g>")
        if has_ring:
            elems.append(
                '<ellipse cx="0" cy="0" rx="%s" ry="%s" transform="rotate(-18)" fill="none" stroke="%s" stroke-width="1.15" stroke-opacity="0.88"/>'
                % (num(pr * 2.35, 1), num(pr * 0.85, 1), CREAM)
            )
        elems.append('<circle cx="0" cy="0" r="%s" fill="%s" stroke="#0b1324" stroke-width="0.6"/>' % (num(pr, 1), pcol))
        if name == "Earth":
            elems.append('<circle cx="%s" cy="%s" r="0.95" fill="#f8fafc"/>' % (num(pr + 2.4, 1), num(-pr - 1.2, 1)))
        elems.append('<animateMotion path="%s" dur="%s" begin="%ss" repeatCount="indefinite"/>' % (orbit_d, dur, num(neg_begin, 1)))
        elems.append("</g>")

    elems.append("</g>")
    return elems
