import math

FONT_MONO = "'JetBrains Mono', 'Fira Code', ui-monospace, SFMono-Regular, Menlo, monospace"
FONT_DISPLAY = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif"

BG_NIGHT = "#070a12"
BG_CARD_TOP = "#0c111d"
BG_CARD_BOT = "#080c15"
BG_WELL = "#060911"
BG_CONSOLE = "#05080f"

BORDER_SUBTLE = "#172033"
BORDER_WARM = "#273249"

IVORY = "#f8fafc"
IVORY_WARM = "#fefce8"
CREAM = "#fde68a"
FIREFLY_GOLD = "#fbbf24"
FIREFLY_AMBER = "#f59e0b"
EMERALD_SOFT = "#6ee7b7"
EMERALD_MID = "#34d399"
TEAL_MIST = "#5eead4"
SKY_SOFT = "#7dd3fc"

INK_PRIMARY = "#f4f7fb"
INK_SECOND = "#b0bfd4"
INK_MUTED = "#7e91ab"
INK_FAINT = "#566882"

LANG_PALETTE = {
    "HTML": ("#fb923c", "#fdba74"),
    "TypeScript": ("#38bdf8", "#bae6fd"),
    "JavaScript": ("#fbbf24", "#fde68a"),
    "CSS": ("#2dd4bf", "#99f6e4"),
    "Python": ("#4ade80", "#bbf7d0"),
    "Shell": ("#94a3b8", "#cbd5e1"),
}

REDUCED_MOTION_STYLE = (
    "<style>"
    "@media (prefers-reduced-motion: reduce) { "
    "animate, animateTransform, animateMotion { display: none; } "
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


def star_path(cx, cy, outer_r, inner_r):
    pts = []
    for i in range(10):
        angle = -math.pi / 2.0 + i * math.pi / 5.0
        r = outer_r if i % 2 == 0 else inner_r
        pts.append("%s,%s" % (num(cx + math.cos(angle) * r), num(cy + math.sin(angle) * r)))
    return "M" + " L".join(pts) + " Z"


def compact(value):
    for suffix, scale in (("B", 1000000000.0), ("M", 1000000.0), ("K", 1000.0)):
        if value >= scale:
            return "%.1f%s" % (value / scale, suffix)
    return str(int(value))


def nocturne_defs(prefix):
    return [
        '<linearGradient id="%s-bg" x1="0" y1="0" x2="0" y2="1">' % prefix,
        '<stop offset="0%%" stop-color="%s"/>' % BG_CARD_TOP,
        '<stop offset="100%%" stop-color="%s"/>' % BG_CARD_BOT,
        "</linearGradient>",
        '<linearGradient id="%s-sheen" x1="0" y1="0" x2="1" y2="0">' % prefix,
        '<stop offset="0%%" stop-color="%s" stop-opacity="0"/>' % CREAM,
        '<stop offset="35%%" stop-color="%s" stop-opacity="0.28"/>' % CREAM,
        '<stop offset="65%%" stop-color="%s" stop-opacity="0.18"/>' % SKY_SOFT,
        '<stop offset="100%%" stop-color="%s" stop-opacity="0"/>' % CREAM,
        "</linearGradient>",
        '<radialGradient id="%s-ff-gold" cx="50%%" cy="50%%" r="50%%">' % prefix,
        '<stop offset="0%%" stop-color="%s" stop-opacity="0.95"/>' % IVORY_WARM,
        '<stop offset="28%%" stop-color="%s" stop-opacity="0.55"/>' % FIREFLY_GOLD,
        '<stop offset="68%%" stop-color="%s" stop-opacity="0.14"/>' % FIREFLY_AMBER,
        '<stop offset="100%%" stop-color="%s" stop-opacity="0"/>' % FIREFLY_AMBER,
        "</radialGradient>",
        '<radialGradient id="%s-ff-white" cx="50%%" cy="50%%" r="50%%">' % prefix,
        '<stop offset="0%%" stop-color="#ffffff" stop-opacity="0.95"/>',
        '<stop offset="32%%" stop-color="%s" stop-opacity="0.42"/>' % CREAM,
        '<stop offset="100%%" stop-color="%s" stop-opacity="0"/>' % CREAM,
        "</radialGradient>",
        '<filter id="%s-bloom" x="-40%%" y="-40%%" width="180%%" height="180%%">' % prefix,
        '<feGaussianBlur stdDeviation="2.4" result="b"/>',
        "<feMerge><feMergeNode in=\"b\"/><feMergeNode in=\"SourceGraphic\"/></feMerge>",
        "</filter>",
    ]


def nocturne_card(width, height, prefix, radius=16):
    return [
        '<clipPath id="%s-clip"><rect x="1" y="1" width="%s" height="%s" rx="%s"/></clipPath>'
        % (prefix, num(width - 2), num(height - 2), num(radius)),
    ], [
        '<rect x="1" y="1" width="%s" height="%s" rx="%s" fill="url(#%s-bg)" stroke="%s" stroke-width="1"/>'
        % (num(width - 2), num(height - 2), num(radius), prefix, BORDER_SUBTLE),
        '<line x1="36" y1="1.5" x2="%s" y2="1.5" stroke="url(#%s-sheen)" stroke-width="1"/>'
        % (num(width - 36), prefix),
    ]


def _rng(seed):
    state = seed & 0xFFFFFFFF
    while True:
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        yield (state >> 8) / float(0xFFFFFF)


def fireflies_layer(prefix, width, height, ambient_count=34, drifter_count=16, seed=42, avoid_boxes=None):
    # WHY: Deterministic PRNG keeps organic firefly trails stable across daily cron runs while avoiding text/portrait occlusion.
    gen = _rng(seed)
    boxes = avoid_boxes or []
    elems = ['<g pointer-events="none">']

    def inside_avoid(px, py):
        for bx, by, bw, bh in boxes:
            if bx <= px <= bx + bw and by <= py <= by + bh:
                return True
        return False

    placed = 0
    attempts = 0
    while placed < ambient_count and attempts < ambient_count * 8:
        attempts += 1
        x = 18.0 + next(gen) * (width - 36.0)
        y = 14.0 + next(gen) * (height - 28.0)
        if inside_avoid(x, y):
            continue
        placed += 1
        r = 0.75 + next(gen) * 1.05
        is_gold = next(gen) > 0.42
        col = CREAM if is_gold else IVORY
        dur = 3.8 + next(gen) * 5.6
        begin = -next(gen) * 9.0
        peak_op = 0.45 + next(gen) * 0.48
        min_op = 0.08 + next(gen) * 0.14
        elems.append(
            '<circle cx="%s" cy="%s" r="%s" fill="%s">'
            '<animate attributeName="opacity" values="%s;%s;%s" dur="%ss" begin="%ss" repeatCount="indefinite"/>'
            "</circle>"
            % (num(x, 1), num(y, 1), num(r, 2), col, num(min_op, 2), num(peak_op, 2), num(min_op, 2), num(dur, 1), num(begin, 1))
        )

    d_placed = 0
    d_attempts = 0
    while d_placed < drifter_count and d_attempts < drifter_count * 10:
        d_attempts += 1
        x = 28.0 + next(gen) * (width - 56.0)
        y = 22.0 + next(gen) * (height - 44.0)
        if inside_avoid(x, y):
            continue
        d_placed += 1
        halo_r = 4.6 + next(gen) * 4.4
        core_r = 1.15 + next(gen) * 0.95
        grad_id = "%s-ff-gold" % prefix if next(gen) > 0.32 else "%s-ff-white" % prefix
        core_col = IVORY_WARM if "gold" in grad_id else "#ffffff"
        dx1 = (next(gen) - 0.5) * 38.0
        dy1 = -8.0 - next(gen) * 22.0
        dx2 = (next(gen) - 0.5) * 44.0
        dy2 = (next(gen) - 0.5) * 28.0
        dx3 = (next(gen) - 0.5) * 30.0
        dy3 = 6.0 + next(gen) * 20.0
        motion_path = "M0,0 C%s,%s %s,%s %s,%s C%s,%s %s,%s 0,0" % (
            num(dx1, 1), num(dy1, 1),
            num(dx2, 1), num(dy2, 1),
            num(dx2 * 0.6, 1), num(dy2 * 0.7, 1),
            num(dx3, 1), num(dy3, 1),
            num(-dx1 * 0.5, 1), num(-dy1 * 0.4, 1),
        )
        m_dur = 11.5 + next(gen) * 11.0
        p_dur = 3.4 + next(gen) * 4.2
        begin = -next(gen) * 14.0
        elems.append(
            '<g transform="translate(%s %s)">'
            "<g>"
            '<circle cx="0" cy="0" r="%s" fill="url(#%s)"/>'
            '<circle cx="0" cy="0" r="%s" fill="%s"/>'
            '<animate attributeName="opacity" values="0.18;0.96;0.42;0.9;0.18" dur="%ss" begin="%ss" repeatCount="indefinite"/>'
            '<animateMotion path="%s" dur="%ss" begin="%ss" repeatCount="indefinite"/>'
            "</g>"
            "</g>"
            % (
                num(x, 1), num(y, 1),
                num(halo_r, 1), grad_id,
                num(core_r, 2), core_col,
                num(p_dur, 1), num(begin, 1),
                motion_path, num(m_dur, 1), num(begin, 1),
            )
        )

    elems.append("</g>")
    return elems
