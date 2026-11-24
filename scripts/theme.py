import math

FONT_MONO = "'JetBrains Mono', 'Fira Code', ui-monospace, SFMono-Regular, Menlo, monospace"
FONT_DISPLAY = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif"

BG_VOID = "#06090f"
BG_PLATE_TOP = "#0c121e"
BG_PLATE_BOT = "#080d17"
BG_WELL = "#05080f"
BG_WELL_ALT = "#0a101c"

STROKE_HAIR = "#162033"
STROKE_FRAME = "#1f2e47"
STROKE_SPECULAR = "#344b6e"

PHOSPHOR = "#39d353"
PHOSPHOR_HI = "#7dff95"
PHOSPHOR_MID = "#239a3b"
PHOSPHOR_LOW = "#124d26"
PHOSPHOR_DEEP = "#0c2b1a"

CYAN = "#38bdf8"
CYAN_DEEP = "#1793d1"
AMBER = "#f5b942"
AMBER_SOFT = "#fbbf24"
CORAL = "#f97316"
SLATE = "#94a3b8"

INK = "#f4f7fb"
INK_SUB = "#9fb0c8"
INK_DIM = "#5c6f89"
INK_MICRO = "#3b4c66"

HEAT_LEVELS = ("#0d1422", "#0d3a24", "#0e6d39", "#26a641", "#4ade80")

LANG_COLORS = {
    "HTML": "#f97316",
    "TypeScript": "#38bdf8",
    "JavaScript": "#f5b942",
    "CSS": "#22d3ee",
    "Python": "#39d353",
    "Shell": "#94a3b8",
}

ARCH_PATH = (
    "M11.39.605C10.376 3.092 9.764 4.72 8.635 7.132c.693.734 1.543 1.589 2.923 2.554"
    "-1.484-.61-2.496-1.224-3.252-1.86C6.86 10.842 4.596 15.138 0 23.395"
    "c3.612-2.085 6.412-3.37 9.021-3.862a6.61 6.61 0 01-.171-1.547l.003-.115"
    "c.058-2.315 1.261-4.095 2.687-3.973 1.426.12 2.534 2.096 2.478 4.409"
    "a6.52 6.52 0 01-.146 1.243c2.58.505 5.352 1.787 8.914 3.844"
    "-.702-1.293-1.33-2.459-1.929-3.57-.943-.73-1.926-1.682-3.933-2.713"
    "1.38.359 2.367.772 3.137 1.234-6.09-11.334-6.582-12.84-8.67-17.74z"
    "M22.898 21.36v-.623h-.234v-.084h.562v.084h-.234v.623h.331v-.707h.142"
    "l.167.5.034.107a2.26 2.26 0 01.038-.114l.17-.493H24v.707h-.091v-.593"
    "l-.206.593h-.084l-.205-.602v.602h-.091"
)

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


def text(x, y, body, fill=INK, size=11, anchor="start", weight="400", extra="", family=FONT_MONO):
    return (
        '<text x="%s" y="%s" font-family="%s" font-size="%s" font-weight="%s" '
        'fill="%s" text-anchor="%s"%s>%s</text>'
        % (num(x), num(y), family, num(size), weight, fill, anchor, extra, esc(body))
    )


def raw_text(x, y, inner, fill=INK, size=11, anchor="start", weight="400", extra="", family=FONT_MONO):
    return (
        '<text x="%s" y="%s" font-family="%s" font-size="%s" font-weight="%s" '
        'fill="%s" text-anchor="%s"%s>%s</text>'
        % (num(x), num(y), family, num(size), weight, fill, anchor, extra, inner)
    )


def arch_mark(x, y, size, fill=CYAN):
    return '<g transform="translate(%s %s) scale(%s)"><path d="%s" fill="%s"/></g>' % (
        num(x),
        num(y),
        num(size / 24.0, 4),
        ARCH_PATH,
        fill,
    )


def star_path(cx, cy, outer_r, inner_r):
    pts = []
    for i in range(10):
        angle = -math.pi / 2.0 + i * math.pi / 5.0
        r = outer_r if i % 2 == 0 else inner_r
        pts.append("%s,%s" % (num(cx + math.cos(angle) * r), num(cy + math.sin(angle) * r)))
    return "M" + " L".join(pts) + " Z"


def common_defs(prefix):
    return [
        '<linearGradient id="%s-plate" x1="0" y1="0" x2="0" y2="1">' % prefix,
        '<stop offset="0%%" stop-color="%s"/>' % BG_PLATE_TOP,
        '<stop offset="100%%" stop-color="%s"/>' % BG_PLATE_BOT,
        "</linearGradient>",
        '<linearGradient id="%s-rim" x1="0" y1="0" x2="1" y2="0">' % prefix,
        '<stop offset="0%%" stop-color="%s" stop-opacity="0"/>' % STROKE_SPECULAR,
        '<stop offset="25%%" stop-color="%s" stop-opacity="0.75"/>' % STROKE_SPECULAR,
        '<stop offset="50%%" stop-color="%s" stop-opacity="0.45"/>' % CYAN,
        '<stop offset="75%%" stop-color="%s" stop-opacity="0.75"/>' % STROKE_SPECULAR,
        '<stop offset="100%%" stop-color="%s" stop-opacity="0"/>' % STROKE_SPECULAR,
        "</linearGradient>",
        '<pattern id="%s-grid" width="24" height="24" patternUnits="userSpaceOnUse">' % prefix,
        '<circle cx="1" cy="1" r="0.65" fill="%s" fill-opacity="0.38"/>' % STROKE_SPECULAR,
        "</pattern>",
        '<filter id="%s-glow" x="-35%%" y="-35%%" width="170%%" height="170%%">' % prefix,
        '<feGaussianBlur stdDeviation="2.6" result="b"/>',
        "<feMerge><feMergeNode in=\"b\"/><feMergeNode in=\"SourceGraphic\"/></feMerge>",
        "</filter>",
        '<filter id="%s-glow-soft" x="-45%%" y="-45%%" width="190%%" height="190%%">' % prefix,
        '<feGaussianBlur stdDeviation="5.5" result="b"/>',
        "<feMerge><feMergeNode in=\"b\"/><feMergeNode in=\"SourceGraphic\"/></feMerge>",
        "</filter>",
    ]


def corner_reticles(x, y, w, h, arm=11, color=STROKE_SPECULAR, stroke_w=1.1, inset=8):
    x0, y0 = x + inset, y + inset
    x1, y1 = x + w - inset, y + h - inset
    return (
        '<g fill="none" stroke="%s" stroke-width="%s" stroke-linecap="square" stroke-opacity="0.8">'
        '<path d="M%s %s V%s H%s"/>'
        '<path d="M%s %s H%s V%s"/>'
        '<path d="M%s %s V%s H%s"/>'
        '<path d="M%s %s H%s V%s"/>'
        "</g>"
        % (
            color,
            num(stroke_w),
            num(x0), num(y0 + arm), num(y0), num(x0 + arm),
            num(x1 - arm), num(y0), num(x1), num(y0 + arm),
            num(x0), num(y1 - arm), num(y1), num(x0 + arm),
            num(x1 - arm), num(y1), num(x1), num(y1 - arm),
        )
    )


def chassis_plate(width, height, prefix, accent=PHOSPHOR, grid_opacity=0.65, radius=14):
    clip_id = "%s-clip" % prefix
    return [
        '<clipPath id="%s"><rect x="1" y="1" width="%s" height="%s" rx="%s"/></clipPath>'
        % (clip_id, num(width - 2), num(height - 2), num(radius)),
    ], [
        '<rect x="1" y="1" width="%s" height="%s" rx="%s" fill="url(#%s-plate)" stroke="%s" stroke-width="1"/>'
        % (num(width - 2), num(height - 2), num(radius), prefix, STROKE_FRAME),
        '<rect x="1" y="1" width="%s" height="%s" rx="%s" fill="url(#%s-grid)" opacity="%s"/>'
        % (num(width - 2), num(height - 2), num(radius), prefix, num(grid_opacity)),
        '<line x1="28" y1="1.5" x2="%s" y2="1.5" stroke="url(#%s-rim)" stroke-width="1.2"/>'
        % (num(width - 28), prefix),
        '<line x1="24" y1="1.5" x2="88" y2="1.5" stroke="%s" stroke-width="1.6" stroke-opacity="0.85"/>'
        % accent,
        corner_reticles(1, 1, width - 2, height - 2, arm=10, color=STROKE_SPECULAR, stroke_w=1.0, inset=10),
    ]


def compact(value):
    for suffix, scale in (("B", 1000000000.0), ("M", 1000000.0), ("K", 1000.0)):
        if value >= scale:
            return "%.1f%s" % (value / scale, suffix)
    return str(int(value))


def disk_label(disk_kb):
    mb = float(disk_kb or 0) / 1024.0
    if mb >= 1024.0:
        return "%.2f GB" % (mb / 1024.0)
    if mb >= 10.0:
        return "%.0f MB" % mb
    if mb >= 1.0:
        return "%.1f MB" % mb
    return "%d KB" % int(disk_kb or 0)
