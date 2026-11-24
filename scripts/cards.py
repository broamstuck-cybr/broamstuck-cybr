import math

try:
    from . import theme
except ImportError:
    import theme


CARD_W = 592
CARD_H = 216
CHAMBER_X = 18
CHAMBER_Y = 18
CHAMBER_W = 224
CHAMBER_H = 180
CHAMBER_RX = 10

COS30 = math.cos(math.radians(30.0))
SIN30 = 0.5


def _iso(ox, oy, u, v, z=0.0):
    return (ox + (u - v) * COS30, oy + (u + v) * SIN30 - z)


def _pts(points):
    return " ".join("%s,%s" % (theme.num(x), theme.num(y)) for x, y in points)


def _path(points, close=False):
    if not points:
        return ""
    segs = ["M%s %s" % (theme.num(points[0][0]), theme.num(points[0][1]))]
    for x, y in points[1:]:
        segs.append("L%s %s" % (theme.num(x), theme.num(y)))
    if close:
        segs.append("Z")
    return " ".join(segs)


def _rel_motion_path(points, close=True):
    x0, y0 = points[0]
    shifted = [(x - x0, y - y0) for x, y in points]
    return x0, y0, _path(shifted, close=close)


def _iso_quad(ox, oy, u0, u1, v0, v1, z):
    return [
        _iso(ox, oy, u0, v0, z),
        _iso(ox, oy, u1, v0, z),
        _iso(ox, oy, u1, v1, z),
        _iso(ox, oy, u0, v1, z),
    ]


def _iso_box(
    ox,
    oy,
    u0,
    u1,
    v0,
    v1,
    z0,
    z1,
    top_fill,
    left_fill,
    right_fill,
    stroke,
    top_stroke=None,
    stroke_w=0.85,
    top_opacity=1.0,
    side_opacity=1.0,
):
    p_tl = _iso(ox, oy, u0, v0, z1)
    p_tr = _iso(ox, oy, u1, v0, z1)
    p_tf = _iso(ox, oy, u1, v1, z1)
    p_tb = _iso(ox, oy, u0, v1, z1)

    p_br = _iso(ox, oy, u1, v0, z0)
    p_bf = _iso(ox, oy, u1, v1, z0)
    p_bb = _iso(ox, oy, u0, v1, z0)

    top_pts = _pts([p_tl, p_tr, p_tf, p_tb])
    left_pts = _pts([p_tb, p_tf, p_bf, p_bb])
    right_pts = _pts([p_tf, p_tr, p_br, p_bf])
    t_stroke = top_stroke or stroke

    return [
        '<polygon points="%s" fill="%s" fill-opacity="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>'
        % (left_pts, left_fill, theme.num(side_opacity), stroke, theme.num(stroke_w)),
        '<polygon points="%s" fill="%s" fill-opacity="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>'
        % (right_pts, right_fill, theme.num(side_opacity), stroke, theme.num(stroke_w)),
        '<polygon points="%s" fill="%s" fill-opacity="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>'
        % (top_pts, top_fill, theme.num(top_opacity), t_stroke, theme.num(stroke_w)),
    ]


def _chamfer_rect_path(x, y, w, h, c):
    x1, y1 = x + w, y + h
    return (
        "M%s %s H%s L%s %s V%s L%s %s H%s L%s %s V%s Z"
        % (
            theme.num(x + c),
            theme.num(y),
            theme.num(x1 - c),
            theme.num(x1),
            theme.num(y + c),
            theme.num(y1 - c),
            theme.num(x1 - c),
            theme.num(y1),
            theme.num(x + c),
            theme.num(x),
            theme.num(y1 - c),
            theme.num(y + c),
        )
    )


def _chamber_base_defs(prefix, accent):
    return [
        '<clipPath id="%s-chamber-clip"><rect x="%d" y="%d" width="%d" height="%d" rx="%d"/></clipPath>'
        % (prefix, CHAMBER_X, CHAMBER_Y, CHAMBER_W, CHAMBER_H, CHAMBER_RX),
        '<linearGradient id="%s-well-bg" x1="0" y1="0" x2="0" y2="1">' % prefix,
        '<stop offset="0%%" stop-color="%s"/>' % theme.BG_WELL_ALT,
        '<stop offset="55%%" stop-color="%s"/>' % theme.BG_WELL,
        '<stop offset="100%%" stop-color="%s"/>' % theme.BG_VOID,
        "</linearGradient>",
        '<radialGradient id="%s-ambient" cx="50%%" cy="54%%" r="58%%">' % prefix,
        '<stop offset="0%%" stop-color="%s" stop-opacity="0.22"/>' % accent,
        '<stop offset="52%%" stop-color="%s" stop-opacity="0.06"/>' % accent,
        '<stop offset="100%%" stop-color="%s" stop-opacity="0"/>' % theme.BG_VOID,
        "</radialGradient>",
        '<linearGradient id="%s-div-grad" gradientUnits="userSpaceOnUse" x1="264" y1="124" x2="568" y2="124">' % prefix,
        '<stop offset="0%%" stop-color="%s" stop-opacity="0.95"/>' % theme.STROKE_SPECULAR,
        '<stop offset="48%%" stop-color="%s" stop-opacity="0.8"/>' % theme.STROKE_FRAME,
        '<stop offset="100%%" stop-color="%s" stop-opacity="0.22"/>' % theme.STROKE_HAIR,
        "</linearGradient>",
        '<linearGradient id="%s-well-rim" gradientUnits="userSpaceOnUse" x1="34" y1="18.8" x2="226" y2="18.8">' % prefix,
        '<stop offset="0%%" stop-color="%s" stop-opacity="0"/>' % theme.STROKE_SPECULAR,
        '<stop offset="32%%" stop-color="%s" stop-opacity="0.65"/>' % theme.STROKE_SPECULAR,
        '<stop offset="68%%" stop-color="%s" stop-opacity="0.45"/>' % accent,
        '<stop offset="100%%" stop-color="%s" stop-opacity="0"/>' % theme.STROKE_SPECULAR,
        "</linearGradient>",
    ]


def _chamber_chrome(prefix, accent):
    cx0, cy0, cw, ch = CHAMBER_X, CHAMBER_Y, CHAMBER_W, CHAMBER_H
    marks = [
        '<rect x="%d" y="%d" width="%d" height="%d" rx="%d" fill="url(#%s-well-bg)" stroke="%s" stroke-width="1"/>'
        % (cx0, cy0, cw, ch, CHAMBER_RX, prefix, theme.STROKE_FRAME),
    ]
    overlay = [
        '<line x1="%d" y1="%s" x2="%d" y2="%s" stroke="url(#%s-well-rim)" stroke-width="1"/>'
        % (cx0 + 16, theme.num(cy0 + 0.8), cx0 + cw - 16, theme.num(cy0 + 0.8), prefix),
        '<g opacity="0.48">%s</g>'
        % theme.corner_reticles(cx0, cy0, cw, ch, arm=6, color=accent, stroke_w=0.8, inset=6),
    ]
    return marks, overlay


def _artwork_fforum(prefix):
    ox, oy = 130.0, 149.5
    z_base_top = 16.0
    z_mid_top = 44.5
    z_top_top = 73.5
    defs = [
        '<linearGradient id="%s-base-top" x1="0" y1="0" x2="1" y2="1">' % prefix,
        '<stop offset="0%%" stop-color="%s"/>' % theme.BG_PLATE_TOP,
        '<stop offset="100%%" stop-color="%s"/>' % theme.BG_WELL,
        "</linearGradient>",
        '<linearGradient id="%s-base-left" x1="0" y1="0" x2="0" y2="1">' % prefix,
        '<stop offset="0%%" stop-color="%s"/>' % theme.BG_PLATE_BOT,
        '<stop offset="100%%" stop-color="%s"/>' % theme.BG_VOID,
        "</linearGradient>",
        '<linearGradient id="%s-glass-mid" x1="0" y1="0" x2="1" y2="1">' % prefix,
        '<stop offset="0%%" stop-color="%s" stop-opacity="0.72"/>' % theme.BG_PLATE_TOP,
        '<stop offset="55%%" stop-color="%s" stop-opacity="0.52"/>' % theme.BG_WELL_ALT,
        '<stop offset="100%%" stop-color="%s" stop-opacity="0.28"/>' % theme.PHOSPHOR_DEEP,
        "</linearGradient>",
        '<linearGradient id="%s-glass-top" x1="0" y1="0" x2="1" y2="1">' % prefix,
        '<stop offset="0%%" stop-color="%s" stop-opacity="0.28"/>' % theme.PHOSPHOR,
        '<stop offset="48%%" stop-color="%s" stop-opacity="0.42"/>' % theme.BG_PLATE_TOP,
        '<stop offset="100%%" stop-color="%s" stop-opacity="0.22"/>' % theme.CYAN_DEEP,
        "</linearGradient>",
        '<linearGradient id="%s-rail-grad" gradientUnits="userSpaceOnUse" x1="130" y1="184" x2="130" y2="56">' % prefix,
        '<stop offset="0%%" stop-color="%s" stop-opacity="0.35"/>' % theme.STROKE_SPECULAR,
        '<stop offset="50%%" stop-color="%s" stop-opacity="0.72"/>' % theme.PHOSPHOR_MID,
        '<stop offset="100%%" stop-color="%s" stop-opacity="0.98"/>' % theme.PHOSPHOR_HI,
        "</linearGradient>",
        '<radialGradient id="%s-photon-halo" cx="50%%" cy="50%%" r="50%%">' % prefix,
        '<stop offset="0%%" stop-color="%s" stop-opacity="0.95"/>' % theme.PHOSPHOR_HI,
        '<stop offset="45%%" stop-color="%s" stop-opacity="0.45"/>' % theme.PHOSPHOR,
        '<stop offset="100%%" stop-color="%s" stop-opacity="0"/>' % theme.PHOSPHOR,
        "</radialGradient>",
    ]

    el = []
    el.append('<rect x="%d" y="%d" width="%d" height="%d" fill="url(#%s-ambient)"/>' % (CHAMBER_X, CHAMBER_Y, CHAMBER_W, CHAMBER_H, prefix))

    floor_outer = _iso_quad(ox, oy, -80, 80, -80, 80, 0)
    el.append(
        '<polygon points="%s" fill="%s" fill-opacity="0.65" stroke="%s" stroke-width="0.75" stroke-opacity="0.7"/>'
        % (_pts(floor_outer), theme.BG_VOID, theme.STROKE_FRAME)
    )
    for step in range(-64, 65, 16):
        is_axis = step == 0
        col = theme.PHOSPHOR_LOW if is_axis else theme.STROKE_HAIR
        op = "0.85" if is_axis else "0.7"
        sw = "0.85" if is_axis else "0.6"
        p0, p1 = _iso(ox, oy, step, -80, 0), _iso(ox, oy, step, 80, 0)
        el.append(
            '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s" stroke-opacity="%s"/>'
            % (theme.num(p0[0]), theme.num(p0[1]), theme.num(p1[0]), theme.num(p1[1]), col, sw, op)
        )
        q0, q1 = _iso(ox, oy, -80, step, 0), _iso(ox, oy, 80, step, 0)
        el.append(
            '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s" stroke-opacity="%s"/>'
            % (theme.num(q0[0]), theme.num(q0[1]), theme.num(q1[0]), theme.num(q1[1]), col, sw, op)
        )

    for tick in range(-64, 65, 16):
        ta0, ta1 = _iso(ox, oy, tick, 80, 0), _iso(ox, oy, tick, 85, 0)
        tb0, tb1 = _iso(ox, oy, 80, tick, 0), _iso(ox, oy, 85, tick, 0)
        t_col = theme.PHOSPHOR if tick == 0 else theme.STROKE_SPECULAR
        el.append(
            '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="0.75" stroke-opacity="0.8"/>'
            % (theme.num(ta0[0]), theme.num(ta0[1]), theme.num(ta1[0]), theme.num(ta1[1]), t_col)
        )
        el.append(
            '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="0.75" stroke-opacity="0.8"/>'
            % (theme.num(tb0[0]), theme.num(tb0[1]), theme.num(tb1[0]), theme.num(tb1[1]), t_col)
        )

    shadow_quad = _iso_quad(ox, oy, -54, 54, -54, 54, 0)
    el.append('<polygon points="%s" fill="%s" fill-opacity="0.82"/>' % (_pts(shadow_quad), theme.BG_VOID))

    back_b, back_t = _iso(ox, oy, -46, -46, 0), _iso(ox, oy, -46, -46, z_top_top)
    el.append(
        '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="0.85" stroke-dasharray="2.5 2.5" stroke-opacity="0.55"/>'
        % (theme.num(back_b[0]), theme.num(back_b[1]), theme.num(back_t[0]), theme.num(back_t[1]), theme.STROKE_SPECULAR)
    )

    el.extend(
        _iso_box(
            ox,
            oy,
            -50,
            50,
            -50,
            50,
            9.5,
            z_base_top,
            "url(#%s-base-top)" % prefix,
            "url(#%s-base-left)" % prefix,
            theme.BG_WELL,
            theme.STROKE_FRAME,
            top_stroke=theme.STROKE_SPECULAR,
            stroke_w=0.9,
        )
    )
    inner_bay = _iso_quad(ox, oy, -34, 34, -34, 34, z_base_top)
    el.append(
        '<polygon points="%s" fill="%s" fill-opacity="0.75" stroke="%s" stroke-width="0.7"/>'
        % (_pts(inner_bay), theme.BG_WELL, theme.STROKE_FRAME)
    )
    for bus in (-20, 0, 20):
        b0, b1 = _iso(ox, oy, bus, -32, z_base_top), _iso(ox, oy, bus, 32, z_base_top)
        el.append(
            '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="0.7" stroke-opacity="0.65"/>'
            % (theme.num(b0[0]), theme.num(b0[1]), theme.num(b1[0]), theme.num(b1[1]), theme.PHOSPHOR_LOW)
        )
    for lv in (-32, -14, 4, 22):
        l0, l1 = _iso(ox, oy, lv, 50, 11.8), _iso(ox, oy, lv + 10, 50, 11.8)
        el.append(
            '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="1.2" stroke-opacity="0.75"/>'
            % (theme.num(l0[0]), theme.num(l0[1]), theme.num(l1[0]), theme.num(l1[1]), theme.STROKE_SPECULAR)
        )
    for idx, led_v in enumerate((-26, -12, 2)):
        lp = _iso(ox, oy, 50, led_v, 13.0)
        lcol = theme.PHOSPHOR if idx == 0 else (theme.CYAN if idx == 1 else theme.AMBER)
        el.append('<circle cx="%s" cy="%s" r="1.35" fill="%s"/>' % (theme.num(lp[0]), theme.num(lp[1]), lcol))

    for cu, cv in ((-46, 46), (46, -46)):
        rb, rt = _iso(ox, oy, cu, cv, z_base_top), _iso(ox, oy, cu, cv, z_top_top)
        el.append(
            '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="url(#%s-rail-grad)" stroke-width="1.05"/>'
            % (theme.num(rb[0]), theme.num(rb[1]), theme.num(rt[0]), theme.num(rt[1]), prefix)
        )
        for z_mark in (z_base_top, z_mid_top, z_top_top):
            mp = _iso(ox, oy, cu, cv, z_mark)
            el.append(
                '<circle cx="%s" cy="%s" r="1.75" fill="%s" stroke="%s" stroke-width="0.8"/>'
                % (theme.num(mp[0]), theme.num(mp[1]), theme.BG_VOID, theme.PHOSPHOR_HI if z_mark == z_top_top else theme.CYAN)
            )

    el.extend(
        _iso_box(
            ox,
            oy,
            -46,
            46,
            -46,
            46,
            41.0,
            z_mid_top,
            "url(#%s-glass-mid)" % prefix,
            theme.BG_WELL_ALT,
            theme.BG_WELL,
            theme.STROKE_SPECULAR,
            top_stroke=theme.CYAN_DEEP,
            stroke_w=0.85,
            top_opacity=0.92,
            side_opacity=0.82,
        )
    )

    win1 = _iso_quad(ox, oy, -41, -3, -41, -4, z_mid_top)
    el.append(
        '<polygon points="%s" fill="%s" fill-opacity="0.72" stroke="%s" stroke-width="0.7"/>'
        % (_pts(win1), theme.BG_VOID, theme.STROKE_SPECULAR)
    )
    w1_bar0, w1_bar1 = _iso(ox, oy, -41, -32, z_mid_top), _iso(ox, oy, -3, -32, z_mid_top)
    el.append(
        '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="0.6"/>'
        % (theme.num(w1_bar0[0]), theme.num(w1_bar0[1]), theme.num(w1_bar1[0]), theme.num(w1_bar1[1]), theme.STROKE_FRAME)
    )
    for d_idx, du in enumerate((-35, -29, -23)):
        dp = _iso(ox, oy, du, -36.5, z_mid_top)
        dc = theme.CORAL if d_idx == 0 else (theme.AMBER if d_idx == 1 else theme.PHOSPHOR)
        el.append('<circle cx="%s" cy="%s" r="1.15" fill="%s"/>' % (theme.num(dp[0]), theme.num(dp[1]), dc))
    for row_v, row_u1 in ((-24, -10), (-17, -16), (-10, -8)):
        r0, r1 = _iso(ox, oy, -36, row_v, z_mid_top), _iso(ox, oy, row_u1, row_v, z_mid_top)
        el.append(
            '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="1.35" stroke-opacity="0.65"/>'
            % (theme.num(r0[0]), theme.num(r0[1]), theme.num(r1[0]), theme.num(r1[1]), theme.SLATE)
        )

    win2 = _iso_quad(ox, oy, 4, 41, -41, -4, z_mid_top)
    el.append(
        '<polygon points="%s" fill="%s" fill-opacity="0.76" stroke="%s" stroke-width="0.7"/>'
        % (_pts(win2), theme.BG_VOID, theme.PHOSPHOR_LOW)
    )
    wave_pts = [
        _iso(ox, oy, 8, -22, z_mid_top),
        _iso(ox, oy, 13, -30, z_mid_top),
        _iso(ox, oy, 18, -14, z_mid_top),
        _iso(ox, oy, 23, -34, z_mid_top),
        _iso(ox, oy, 28, -17, z_mid_top),
        _iso(ox, oy, 33, -27, z_mid_top),
        _iso(ox, oy, 37, -21, z_mid_top),
    ]
    el.append(
        '<polyline points="%s" fill="none" stroke="%s" stroke-width="1.2" stroke-linejoin="round"/>'
        % (_pts(wave_pts), theme.PHOSPHOR)
    )

    win3 = _iso_quad(ox, oy, -41, 6, 4, 41, z_mid_top)
    el.append(
        '<polygon points="%s" fill="%s" fill-opacity="0.68" stroke="%s" stroke-width="0.7"/>'
        % (_pts(win3), theme.BG_VOID, theme.STROKE_FRAME)
    )
    tile_specs = [
        (-37, -24, 9, 21, theme.PHOSPHOR_DEEP, theme.PHOSPHOR),
        (-21, -8, 9, 21, theme.BG_PLATE_TOP, theme.STROKE_SPECULAR),
        (-5, 3, 9, 21, theme.BG_PLATE_TOP, theme.CYAN_DEEP),
        (-37, -24, 24, 36, theme.BG_PLATE_TOP, theme.STROKE_SPECULAR),
        (-21, -8, 24, 36, theme.BG_PLATE_TOP, theme.CYAN),
        (-5, 3, 24, 36, theme.BG_PLATE_TOP, theme.STROKE_SPECULAR),
    ]
    for tu0, tu1, tv0, tv1, tf, ts in tile_specs:
        tq = _iso_quad(ox, oy, tu0, tu1, tv0, tv1, z_mid_top)
        el.append(
            '<polygon points="%s" fill="%s" fill-opacity="0.75" stroke="%s" stroke-width="0.6"/>'
            % (_pts(tq), tf, ts)
        )

    win4 = _iso_quad(ox, oy, 13, 41, 4, 41, z_mid_top)
    el.append(
        '<polygon points="%s" fill="%s" fill-opacity="0.72" stroke="%s" stroke-width="0.7"/>'
        % (_pts(win4), theme.BG_VOID, theme.CYAN_DEEP)
    )
    bars = [
        (17, 22, 10, 16, 5.5, theme.CYAN),
        (25, 30, 10, 16, 9.5, theme.PHOSPHOR),
        (17, 22, 22, 28, 7.5, theme.AMBER),
        (25, 30, 22, 28, 11.5, theme.PHOSPHOR_HI),
    ]
    for bu0, bu1, bv0, bv1, bh, bcol in bars:
        el.extend(
            _iso_box(
                ox,
                oy,
                bu0,
                bu1,
                bv0,
                bv1,
                z_mid_top,
                z_mid_top + bh,
                bcol,
                theme.BG_PLATE_TOP,
                theme.BG_WELL,
                bcol,
                stroke_w=0.55,
                top_opacity=0.85,
                side_opacity=0.85,
            )
        )

    top_glow_quad = _iso_quad(ox, oy, -46, 46, -46, 46, z_top_top)
    el.append(
        '<polygon points="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-opacity="0.58" filter="url(#%s-glow)"/>'
        % (_pts(top_glow_quad), theme.PHOSPHOR, prefix)
    )
    el.extend(
        _iso_box(
            ox,
            oy,
            -46,
            46,
            -46,
            46,
            71.0,
            z_top_top,
            "url(#%s-glass-top)" % prefix,
            theme.PHOSPHOR_DEEP,
            theme.BG_WELL_ALT,
            theme.PHOSPHOR_MID,
            top_stroke=theme.PHOSPHOR_HI,
            stroke_w=0.95,
            top_opacity=0.86,
            side_opacity=0.76,
        )
    )

    hud_bar = _iso_quad(ox, oy, -38, 38, -38, -28, z_top_top)
    el.append(
        '<polygon points="%s" fill="%s" fill-opacity="0.5" stroke="%s" stroke-width="0.6"/>'
        % (_pts(hud_bar), theme.PHOSPHOR_DEEP, theme.PHOSPHOR)
    )
    hud_view = _iso_quad(ox, oy, -38, 38, -23, 38, z_top_top)
    el.append(
        '<polygon points="%s" fill="none" stroke="%s" stroke-width="0.65" stroke-opacity="0.65" stroke-dasharray="3 2"/>'
        % (_pts(hud_view), theme.PHOSPHOR_HI)
    )
    cx_t, cy_t = _iso(ox, oy, 0, 7, z_top_top)
    el.append(
        '<ellipse cx="%s" cy="%s" rx="22" ry="11.5" fill="none" stroke="%s" stroke-width="0.9" stroke-opacity="0.85"/>'
        % (theme.num(cx_t), theme.num(cy_t), theme.PHOSPHOR)
    )
    el.append(
        '<ellipse cx="%s" cy="%s" rx="11" ry="5.8" fill="%s" fill-opacity="0.18" stroke="%s" stroke-width="0.8"/>'
        % (theme.num(cx_t), theme.num(cy_t), theme.PHOSPHOR_HI, theme.CYAN)
    )
    xh0, xh1 = _iso(ox, oy, -26, 7, z_top_top), _iso(ox, oy, 26, 7, z_top_top)
    xv0, xv1 = _iso(ox, oy, 0, -18, z_top_top), _iso(ox, oy, 0, 32, z_top_top)
    el.append(
        '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="0.65" stroke-opacity="0.7"/>'
        % (theme.num(xh0[0]), theme.num(xh0[1]), theme.num(xh1[0]), theme.num(xh1[1]), theme.PHOSPHOR_HI)
    )
    el.append(
        '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="0.65" stroke-opacity="0.7"/>'
        % (theme.num(xv0[0]), theme.num(xv0[1]), theme.num(xv1[0]), theme.num(xv1[1]), theme.PHOSPHOR_HI)
    )

    el.extend(
        _iso_box(
            ox,
            oy,
            -8,
            8,
            -1,
            15,
            77.5,
            88.0,
            theme.PHOSPHOR,
            theme.PHOSPHOR_MID,
            theme.PHOSPHOR_LOW,
            theme.PHOSPHOR_HI,
            stroke_w=0.75,
            top_opacity=0.68,
            side_opacity=0.48,
        )
    )

    front_b, front_t = _iso(ox, oy, 46, 46, z_base_top), _iso(ox, oy, 46, 46, z_top_top)
    el.append(
        '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="url(#%s-rail-grad)" stroke-width="1.05" stroke-opacity="0.9"/>'
        % (theme.num(front_b[0]), theme.num(front_b[1]), theme.num(front_t[0]), theme.num(front_t[1]), prefix)
    )
    for z_mark in (z_base_top, z_mid_top, z_top_top):
        fp = _iso(ox, oy, 46, 46, z_mark)
        el.append(
            '<circle cx="%s" cy="%s" r="1.85" fill="%s" stroke="%s" stroke-width="0.85"/>'
            % (theme.num(fp[0]), theme.num(fp[1]), theme.BG_VOID, theme.PHOSPHOR_HI if z_mark == z_top_top else theme.PHOSPHOR)
        )

    spline_pts = [
        _iso(ox, oy, -46, 46, z_top_top),
        _iso(ox, oy, -46, -46, z_top_top),
        _iso(ox, oy, 46, -46, z_top_top),
        _iso(ox, oy, 46, 46, z_top_top),
        _iso(ox, oy, 46, 46, z_mid_top),
        _iso(ox, oy, -46, 46, z_mid_top),
        _iso(ox, oy, -46, 46, z_base_top),
        _iso(ox, oy, 46, 46, z_base_top),
        _iso(ox, oy, 46, -46, z_base_top),
        _iso(ox, oy, 46, -46, z_mid_top),
        _iso(ox, oy, 46, -46, z_top_top),
        _iso(ox, oy, -46, -46, z_top_top),
    ]
    el.append(
        '<path d="%s" fill="none" stroke="%s" stroke-width="0.75" stroke-opacity="0.32"/>'
        % (_path(spline_pts, close=True), theme.PHOSPHOR_HI)
    )
    px0, py0, rel_d = _rel_motion_path(spline_pts, close=True)
    el.append(
        '<g transform="translate(%s %s)">'
        '<g filter="url(#%s-glow)">'
        '<circle r="6" fill="url(#%s-photon-halo)"/>'
        '<circle r="2.6" fill="%s"/>'
        '<circle r="1.15" fill="%s"/>'
        '<animateMotion dur="7.6s" repeatCount="indefinite" path="%s"/>'
        "</g>"
        '<circle r="1.7" fill="%s" fill-opacity="0.7">'
        '<animateMotion dur="7.6s" begin="-0.18s" repeatCount="indefinite" path="%s"/>'
        "</circle>"
        "</g>"
        % (
            theme.num(px0),
            theme.num(py0),
            prefix,
            prefix,
            theme.PHOSPHOR,
            theme.INK,
            rel_d,
            theme.PHOSPHOR_HI,
            rel_d,
        )
    )

    return defs, el


def _artwork_vault(prefix):
    ox, oy = 130.0, 158.0
    lens_cx, lens_cy = 130.0, 163.0
    defs = [
        '<radialGradient id="%s-lens-glow" cx="50%%" cy="50%%" r="50%%">' % prefix,
        '<stop offset="0%%" stop-color="%s" stop-opacity="0.9"/>' % theme.AMBER_SOFT,
        '<stop offset="42%%" stop-color="%s" stop-opacity="0.38"/>' % theme.AMBER,
        '<stop offset="100%%" stop-color="%s" stop-opacity="0"/>' % theme.BG_VOID,
        "</radialGradient>",
        '<linearGradient id="%s-slab-left" x1="0" y1="0" x2="0" y2="1">' % prefix,
        '<stop offset="0%%" stop-color="%s"/>' % theme.BG_PLATE_TOP,
        '<stop offset="55%%" stop-color="%s"/>' % theme.BG_WELL_ALT,
        '<stop offset="100%%" stop-color="%s"/>' % theme.BG_VOID,
        "</linearGradient>",
        '<linearGradient id="%s-slab-left-hi" x1="0" y1="0" x2="0" y2="1">' % prefix,
        '<stop offset="0%%" stop-color="%s" stop-opacity="0.34"/>' % theme.AMBER,
        '<stop offset="40%%" stop-color="%s" stop-opacity="0.92"/>' % theme.BG_PLATE_TOP,
        '<stop offset="100%%" stop-color="%s"/>' % theme.BG_WELL,
        "</linearGradient>",
        '<linearGradient id="%s-slab-right" x1="0" y1="0" x2="0" y2="1">' % prefix,
        '<stop offset="0%%" stop-color="%s"/>' % theme.BG_WELL_ALT,
        '<stop offset="100%%" stop-color="%s"/>' % theme.BG_VOID,
        "</linearGradient>",
        '<linearGradient id="%s-slab-top" x1="0" y1="0" x2="1" y2="1">' % prefix,
        '<stop offset="0%%" stop-color="%s" stop-opacity="0.72"/>' % theme.STROKE_SPECULAR,
        '<stop offset="100%%" stop-color="%s"/>' % theme.BG_PLATE_TOP,
        "</linearGradient>",
        '<linearGradient id="%s-slab-top-hi" x1="0" y1="0" x2="1" y2="1">' % prefix,
        '<stop offset="0%%" stop-color="%s" stop-opacity="0.88"/>' % theme.AMBER_SOFT,
        '<stop offset="100%%" stop-color="%s" stop-opacity="0.45"/>' % theme.AMBER,
        "</linearGradient>",
        '<linearGradient id="%s-scan-wash" x1="0" y1="0" x2="0" y2="1">' % prefix,
        '<stop offset="0%%" stop-color="%s" stop-opacity="0"/>' % theme.AMBER,
        '<stop offset="48%%" stop-color="%s" stop-opacity="0.28"/>' % theme.AMBER,
        '<stop offset="52%%" stop-color="%s" stop-opacity="0.28"/>' % theme.AMBER_SOFT,
        '<stop offset="100%%" stop-color="%s" stop-opacity="0"/>' % theme.AMBER,
        "</linearGradient>",
        '<linearGradient id="%s-beam-up" gradientUnits="userSpaceOnUse" x1="130" y1="163" x2="130" y2="124">' % prefix,
        '<stop offset="0%%" stop-color="%s" stop-opacity="0.92"/>' % theme.AMBER_SOFT,
        '<stop offset="100%%" stop-color="%s" stop-opacity="0.24"/>' % theme.AMBER,
        "</linearGradient>",
    ]

    el = []
    el.append('<rect x="%d" y="%d" width="%d" height="%d" fill="url(#%s-ambient)"/>' % (CHAMBER_X, CHAMBER_Y, CHAMBER_W, CHAMBER_H, prefix))

    el.append(
        '<ellipse cx="%s" cy="%s" rx="84" ry="25" fill="%s" fill-opacity="0.6" stroke="%s" stroke-width="0.7" stroke-dasharray="3 3" stroke-opacity="0.7"/>'
        % (theme.num(lens_cx), theme.num(lens_cy), theme.BG_VOID, theme.STROKE_FRAME)
    )
    el.append(
        '<ellipse cx="%s" cy="%s" rx="64" ry="19.5" fill="none" stroke="%s" stroke-width="0.9" stroke-opacity="0.55"/>'
        % (theme.num(lens_cx), theme.num(lens_cy), theme.STROKE_SPECULAR)
    )
    el.append(
        '<ellipse cx="%s" cy="%s" rx="44" ry="13.5" fill="none" stroke="%s" stroke-width="1.0" stroke-opacity="0.75"/>'
        % (theme.num(lens_cx), theme.num(lens_cy), theme.AMBER)
    )
    el.append(
        '<ellipse cx="%s" cy="%s" rx="30" ry="9.5" fill="url(#%s-lens-glow)"/>'
        % (theme.num(lens_cx), theme.num(lens_cy), prefix)
    )
    el.append(
        '<ellipse cx="%s" cy="%s" rx="18" ry="5.8" fill="%s" fill-opacity="0.4" stroke="%s" stroke-width="1.1"/>'
        % (theme.num(lens_cx), theme.num(lens_cy), theme.BG_WELL, theme.AMBER_SOFT)
    )
    el.append(
        '<ellipse cx="%s" cy="%s" rx="5.5" ry="2.0" fill="%s"/>'
        % (theme.num(lens_cx), theme.num(lens_cy), theme.AMBER_SOFT)
    )

    for i in range(24):
        ang = math.radians(i * 15.0)
        ca, sa = math.cos(ang), math.sin(ang)
        r0x, r0y = (64.0, 19.5)
        r1x, r1y = (72.0, 22.0) if i % 3 == 0 else (68.0, 20.8)
        col = theme.AMBER if i % 6 == 0 else theme.STROKE_SPECULAR
        el.append(
            '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s" stroke-opacity="0.72"/>'
            % (
                theme.num(lens_cx + ca * r0x),
                theme.num(lens_cy + sa * r0y),
                theme.num(lens_cx + ca * r1x),
                theme.num(lens_cy + sa * r1y),
                col,
                "0.95" if i % 3 == 0 else "0.65",
            )
        )

    slabs = [
        (-62, -50, -24, 2, 18, 76, False, 6),
        (-42, -29, -32, -4, 22, 90, False, 7),
        (-19, -5, -24, 10, 16, 104, True, 9),
        (5, 19, -30, 4, 20, 96, True, 8),
        (28, 41, -20, 10, 18, 86, False, 7),
        (50, 62, -26, 2, 21, 74, False, 6),
    ]
    slabs.sort(key=lambda s: (s[0] + s[1]) * 0.5 + (s[2] + s[3]) * 0.5)

    for u0, u1, v0, v1, z0, z1, is_hero, _ in slabs:
        bp = _iso(ox, oy, (u0 + u1) * 0.5, (v0 + v1) * 0.5, z0)
        el.append(
            '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="url(#%s-beam-up)" stroke-width="%s"/>'
            % (
                theme.num(lens_cx),
                theme.num(lens_cy),
                theme.num(bp[0]),
                theme.num(bp[1]),
                prefix,
                "1.25" if is_hero else "0.85",
            )
        )
        el.append(
            '<circle cx="%s" cy="%s" r="%s" fill="%s"/>'
            % (theme.num(bp[0]), theme.num(bp[1]), "2.1" if is_hero else "1.5", theme.AMBER_SOFT if is_hero else theme.AMBER)
        )

    for s_idx, (u0, u1, v0, v1, z0, z1, is_hero, n_lines) in enumerate(slabs):
        left_fill = "url(#%s-slab-left-hi)" % prefix if is_hero else "url(#%s-slab-left)" % prefix
        top_fill = "url(#%s-slab-top-hi)" % prefix if is_hero else "url(#%s-slab-top)" % prefix
        edge_col = theme.AMBER if is_hero else theme.STROKE_SPECULAR
        top_col = theme.AMBER_SOFT if is_hero else theme.SLATE

        el.extend(
            _iso_box(
                ox,
                oy,
                u0,
                u1,
                v0,
                v1,
                z0,
                z1,
                top_fill,
                left_fill,
                "url(#%s-slab-right)" % prefix,
                edge_col,
                top_stroke=top_col,
                stroke_w=0.95 if is_hero else 0.78,
                top_opacity=0.95,
                side_opacity=0.94,
            )
        )

        spine_bot = _iso(ox, oy, u1, v1, z0)
        spine_top = _iso(ox, oy, u1, v1, z1)
        el.append(
            '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s" stroke-opacity="0.9"/>'
            % (
                theme.num(spine_bot[0]),
                theme.num(spine_bot[1]),
                theme.num(spine_top[0]),
                theme.num(spine_top[1]),
                theme.AMBER_SOFT if is_hero else theme.SLATE,
                "1.15" if is_hero else "0.8",
            )
        )

        span_z = z1 - z0 - 12.0
        for li in range(n_lines):
            zl = z0 + 7.0 + (span_z * li / float(max(n_lines - 1, 1)))
            frac = 0.82 if (li + s_idx) % 3 != 0 else 0.54
            lu_end = u0 + (u1 - u0) * frac
            p0 = _iso(ox, oy, u0 + 1.8, v1, zl)
            p1 = _iso(ox, oy, lu_end - 1.2, v1, zl)
            highlight = (li % 3 == 0 and is_hero) or (li == n_lines - 2)
            lcol = theme.AMBER_SOFT if highlight else (theme.AMBER if is_hero else theme.STROKE_SPECULAR)
            lop = "0.85" if highlight else ("0.52" if is_hero else "0.62")
            el.append(
                '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="0.85" stroke-opacity="%s"/>'
                % (theme.num(p0[0]), theme.num(p0[1]), theme.num(p1[0]), theme.num(p1[1]), lcol, lop)
            )
            if li % 2 == 0:
                rp0 = _iso(ox, oy, u1, v0 + 4.0, zl)
                rp1 = _iso(ox, oy, u1, v1 - 4.0, zl)
                el.append(
                    '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="0.65" stroke-opacity="0.45"/>'
                    % (theme.num(rp0[0]), theme.num(rp0[1]), theme.num(rp1[0]), theme.num(rp1[1]), theme.AMBER if is_hero else theme.STROKE_FRAME)
                )

        cap_dot = _iso(ox, oy, (u0 + u1) * 0.5, (v0 + v1) * 0.5, z1)
        el.append(
            '<circle cx="%s" cy="%s" r="%s" fill="%s"/>'
            % (theme.num(cap_dot[0]), theme.num(cap_dot[1]), "1.7" if is_hero else "1.2", theme.INK if is_hero else theme.AMBER)
        )

    scan_y0 = 92.0
    el.append(
        '<g>'
        '<rect x="28" y="%s" width="204" height="22" fill="url(#%s-scan-wash)"/>'
        '<line x1="30" y1="%s" x2="230" y2="%s" stroke="%s" stroke-width="1.4" filter="url(#%s-glow)"/>'
        '<line x1="30" y1="%s" x2="230" y2="%s" stroke="%s" stroke-width="0.65" stroke-opacity="0.9"/>'
        '<path d="M26 %s H34 M26 %s V%s M234 %s H226 M234 %s V%s" fill="none" stroke="%s" stroke-width="1.1"/>'
        '<circle cx="130" cy="%s" r="2.2" fill="%s"/>'
        '<animateTransform attributeName="transform" type="translate" '
        'values="0 0; 0 50; 0 -46; 0 0" keyTimes="0; 0.42; 0.82; 1" '
        'calcMode="spline" keySplines="0.42 0 0.58 1; 0.42 0 0.58 1; 0.42 0 0.58 1" '
        'dur="5.8s" repeatCount="indefinite"/>'
        "</g>"
        % (
            theme.num(scan_y0 - 11.0),
            prefix,
            theme.num(scan_y0),
            theme.num(scan_y0),
            theme.AMBER_SOFT,
            prefix,
            theme.num(scan_y0),
            theme.num(scan_y0),
            theme.INK,
            theme.num(scan_y0),
            theme.num(scan_y0 - 4.0),
            theme.num(scan_y0 + 4.0),
            theme.num(scan_y0),
            theme.num(scan_y0 - 4.0),
            theme.num(scan_y0 + 4.0),
            theme.AMBER,
            theme.num(scan_y0),
            theme.INK,
        )
    )

    return defs, el


def _artwork_edunext(prefix):
    cx, cy = 130.0, 108.0
    defs = [
        '<linearGradient id="%s-pkg-grad" x1="0" y1="0" x2="1" y2="1">' % prefix,
        '<stop offset="0%%" stop-color="%s"/>' % theme.BG_PLATE_TOP,
        '<stop offset="100%%" stop-color="%s"/>' % theme.BG_VOID,
        "</linearGradient>",
        '<linearGradient id="%s-die-grad" x1="0" y1="0" x2="1" y2="1">' % prefix,
        '<stop offset="0%%" stop-color="%s" stop-opacity="0.32"/>' % theme.CYAN_DEEP,
        '<stop offset="50%%" stop-color="%s"/>' % theme.BG_WELL_ALT,
        '<stop offset="100%%" stop-color="%s"/>' % theme.BG_VOID,
        "</linearGradient>",
        '<radialGradient id="%s-core-halo" cx="50%%" cy="50%%" r="50%%">' % prefix,
        '<stop offset="0%%" stop-color="%s" stop-opacity="0.48"/>' % theme.CYAN,
        '<stop offset="65%%" stop-color="%s" stop-opacity="0.12"/>' % theme.CYAN_DEEP,
        '<stop offset="100%%" stop-color="%s" stop-opacity="0"/>' % theme.BG_VOID,
        "</radialGradient>",
    ]

    el = []
    el.append('<rect x="%d" y="%d" width="%d" height="%d" fill="url(#%s-ambient)"/>' % (CHAMBER_X, CHAMBER_Y, CHAMBER_W, CHAMBER_H, prefix))

    for gx in range(34, 227, 24):
        for gy in range(32, 185, 24):
            el.append(
                '<path d="M%d %d H%d M%d %d V%d" stroke="%s" stroke-width="0.6" stroke-opacity="0.5"/>'
                % (gx - 2, gy, gx + 2, gx, gy - 2, gy + 2, theme.STROKE_HAIR)
            )

    for fx, fy in ((37, 37), (223, 37), (37, 179), (223, 179)):
        el.append(
            '<circle cx="%d" cy="%d" r="3.8" fill="%s" stroke="%s" stroke-width="0.8"/>'
            % (fx, fy, theme.BG_VOID, theme.STROKE_SPECULAR)
        )
        el.append('<circle cx="%d" cy="%d" r="1.3" fill="%s"/>' % (fx, fy, theme.CYAN_DEEP))

    pin_offsets = [-24.5, -17.5, -10.5, -3.5, 3.5, 10.5, 17.5, 24.5]

    left_traces = [
        [(90, cy + pin_offsets[0]), (74, cy + pin_offsets[0]), (60, 68), (38, 68)],
        [(90, cy + pin_offsets[1]), (70, cy + pin_offsets[1]), (56, 78), (30, 78)],
        [(90, cy + pin_offsets[2]), (66, cy + pin_offsets[2]), (54, 92), (34, 92)],
        [(90, cy + pin_offsets[3]), (44, cy + pin_offsets[3])],
        [(90, cy + pin_offsets[4]), (48, cy + pin_offsets[4]), (38, 122), (28, 122)],
        [(90, cy + pin_offsets[5]), (66, cy + pin_offsets[5]), (54, 132), (34, 132)],
        [(90, cy + pin_offsets[6]), (72, cy + pin_offsets[6]), (58, 144), (30, 144)],
        [(90, cy + pin_offsets[7]), (78, cy + pin_offsets[7]), (64, 156), (40, 156)],
    ]
    right_traces = [
        [(170, cy + pin_offsets[0]), (186, cy + pin_offsets[0]), (200, 68), (222, 68)],
        [(170, cy + pin_offsets[1]), (190, cy + pin_offsets[1]), (204, 78), (230, 78)],
        [(170, cy + pin_offsets[2]), (194, cy + pin_offsets[2]), (206, 92), (226, 92)],
        [(170, cy + pin_offsets[3]), (216, cy + pin_offsets[3])],
        [(170, cy + pin_offsets[4]), (212, cy + pin_offsets[4]), (222, 122), (232, 122)],
        [(170, cy + pin_offsets[5]), (194, cy + pin_offsets[5]), (206, 132), (226, 132)],
        [(170, cy + pin_offsets[6]), (188, cy + pin_offsets[6]), (202, 144), (230, 144)],
        [(170, cy + pin_offsets[7]), (182, cy + pin_offsets[7]), (196, 156), (220, 156)],
    ]
    top_traces = [
        [(cx + pin_offsets[0], 68), (cx + pin_offsets[0], 54), (86, 40), (62, 40)],
        [(cx + pin_offsets[1], 68), (cx + pin_offsets[1], 48), (98, 34), (78, 34)],
        [(cx + pin_offsets[2], 68), (cx + pin_offsets[2], 42), (110, 30)],
        [(cx + pin_offsets[3], 68), (cx + pin_offsets[3], 30)],
        [(cx + pin_offsets[4], 68), (cx + pin_offsets[4], 30)],
        [(cx + pin_offsets[5], 68), (cx + pin_offsets[5], 42), (150, 30)],
        [(cx + pin_offsets[6], 68), (cx + pin_offsets[6], 48), (162, 34), (182, 34)],
        [(cx + pin_offsets[7], 68), (cx + pin_offsets[7], 54), (174, 40), (198, 40)],
    ]
    bottom_traces = [
        [(cx + pin_offsets[0], 148), (cx + pin_offsets[0], 162), (86, 176), (62, 176)],
        [(cx + pin_offsets[1], 148), (cx + pin_offsets[1], 168), (98, 182), (78, 182)],
        [(cx + pin_offsets[2], 148), (cx + pin_offsets[2], 174), (110, 186)],
        [(cx + pin_offsets[3], 148), (cx + pin_offsets[3], 186)],
        [(cx + pin_offsets[4], 148), (cx + pin_offsets[4], 186)],
        [(cx + pin_offsets[5], 148), (cx + pin_offsets[5], 174), (150, 186)],
        [(cx + pin_offsets[6], 148), (cx + pin_offsets[6], 168), (162, 182), (182, 182)],
        [(cx + pin_offsets[7], 148), (cx + pin_offsets[7], 162), (174, 176), (198, 176)],
    ]

    all_banks = [
        (left_traces, (1, 5)),
        (right_traces, (2, 6)),
        (top_traces, (1, 6)),
        (bottom_traces, (0, 5)),
    ]
    for traces, accent_idxs in all_banks:
        for idx, pts in enumerate(traces):
            is_hi = idx in accent_idxs
            t_col = theme.CYAN_DEEP if is_hi else theme.STROKE_FRAME
            t_op = "0.85" if is_hi else "0.9"
            el.append(
                '<path d="%s" fill="none" stroke="%s" stroke-width="%s" stroke-opacity="%s" stroke-linejoin="round"/>'
                % (_path(pts), t_col, "1.1" if is_hi else "0.85", t_op)
            )
            ex, ey = pts[-1]
            v_col = theme.CYAN if is_hi else theme.STROKE_SPECULAR
            el.append(
                '<circle cx="%s" cy="%s" r="2.2" fill="%s" stroke="%s" stroke-width="0.9"/>'
                % (theme.num(ex), theme.num(ey), theme.BG_VOID, v_col)
            )
            if is_hi:
                el.append('<circle cx="%s" cy="%s" r="0.85" fill="%s"/>' % (theme.num(ex), theme.num(ey), theme.CYAN))

    for smd_x, smd_y in ((43, 51), (205, 51), (43, 160), (205, 160)):
        el.append(
            '<rect x="%d" y="%d" width="12" height="5.5" rx="1" fill="%s" stroke="%s" stroke-width="0.7"/>'
            % (smd_x, smd_y, theme.BG_PLATE_TOP, theme.STROKE_SPECULAR)
        )
        el.append('<rect x="%d" y="%d" width="2.4" height="5.5" fill="%s" fill-opacity="0.75"/>' % (smd_x, smd_y, theme.SLATE))
        el.append('<rect x="%s" y="%d" width="2.4" height="5.5" fill="%s" fill-opacity="0.75"/>' % (theme.num(smd_x + 9.6), smd_y, theme.SLATE))

    pulse_path_1 = [
        (30, 78),
        (56, 78),
        (70, cy + pin_offsets[1]),
        (90, cy + pin_offsets[1]),
        (96, cy + pin_offsets[1]),
        (96, 80),
        (164, 80),
        (164, cy + pin_offsets[2]),
        (170, cy + pin_offsets[2]),
        (194, cy + pin_offsets[2]),
        (206, 92),
        (226, 92),
    ]
    pulse_path_2 = [
        (62, 176),
        (86, 176),
        (cx + pin_offsets[0], 162),
        (cx + pin_offsets[0], 148),
        (cx + pin_offsets[0], 138),
        (162, 138),
        (162, cy + pin_offsets[6]),
        (188, cy + pin_offsets[6]),
        (202, 144),
        (230, 144),
    ]
    el.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.25" stroke-opacity="0.48"/>' % (_path(pulse_path_1), theme.CYAN))
    el.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.25" stroke-opacity="0.45"/>' % (_path(pulse_path_2), theme.PHOSPHOR))

    el.append(
        '<path d="%s" fill="%s" fill-opacity="0.75"/>'
        % (_chamfer_rect_path(93, 71, 74, 74, 9.5), theme.BG_VOID)
    )

    for off in pin_offsets:
        px = cx + off
        py = cy + off
        el.append('<rect x="%s" y="67.5" width="3.2" height="7" rx="0.7" fill="%s" stroke="%s" stroke-width="0.5"/>' % (theme.num(px - 1.6), theme.SLATE, theme.STROKE_FRAME))
        el.append('<rect x="%s" y="141.5" width="3.2" height="7" rx="0.7" fill="%s" stroke="%s" stroke-width="0.5"/>' % (theme.num(px - 1.6), theme.SLATE, theme.STROKE_FRAME))
        el.append('<rect x="89.5" y="%s" width="7" height="3.2" rx="0.7" fill="%s" stroke="%s" stroke-width="0.5"/>' % (theme.num(py - 1.6), theme.SLATE, theme.STROKE_FRAME))
        el.append('<rect x="163.5" y="%s" width="7" height="3.2" rx="0.7" fill="%s" stroke="%s" stroke-width="0.5"/>' % (theme.num(py - 1.6), theme.SLATE, theme.STROKE_FRAME))

    el.append(
        '<path d="%s" fill="url(#%s-pkg-grad)" stroke="%s" stroke-width="1.2"/>'
        % (_chamfer_rect_path(96, 74, 68, 68, 8), prefix, theme.STROKE_SPECULAR)
    )
    el.append('<polygon points="102,80 107,80 102,85" fill="%s"/>' % theme.AMBER)
    el.append(
        '<path d="%s" fill="%s" stroke="%s" stroke-width="0.9" stroke-opacity="0.85"/>'
        % (_chamfer_rect_path(104, 82, 52, 52, 5.5), theme.BG_WELL, theme.CYAN_DEEP)
    )

    for bx0, by0, bx1, by1 in (
        (106, 84, 113, 91),
        (154, 84, 147, 91),
        (106, 132, 113, 125),
        (154, 132, 147, 125),
        (130, 82, 130, 90),
        (130, 134, 130, 126),
        (104, 108, 112, 108),
        (156, 108, 148, 108),
    ):
        el.append(
            '<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="0.7" stroke-opacity="0.65"/>'
            % (bx0, by0, bx1, by1, theme.CYAN)
        )

    el.append(
        '<path d="%s" fill="url(#%s-die-grad)" stroke="%s" stroke-width="1.15" filter="url(#%s-glow)"/>'
        % (_chamfer_rect_path(112, 90, 36, 36, 4), prefix, theme.CYAN, prefix)
    )
    el.append('<circle cx="%s" cy="%s" r="15" fill="url(#%s-core-halo)"/>' % (theme.num(cx), theme.num(cy), prefix))
    el.append(
        '<circle cx="%s" cy="%s" r="13.5" fill="none" stroke="%s" stroke-width="0.8" stroke-dasharray="2 2.5" stroke-opacity="0.7"/>'
        % (theme.num(cx), theme.num(cy), theme.CYAN)
    )
    el.append(
        '<circle cx="%s" cy="%s" r="11" fill="none" stroke="%s" stroke-width="1.1" stroke-opacity="0.75">'
        '<animate attributeName="r" values="10;17;10" dur="3.4s" repeatCount="indefinite"/>'
        '<animate attributeName="stroke-opacity" values="0.8;0.1;0.8" dur="3.4s" repeatCount="indefinite"/>'
        "</circle>"
        % (theme.num(cx), theme.num(cy), theme.CYAN)
    )

    el.append(
        '<path d="M116 108 H122 M138 108 H144 M130 94 V100 M130 116 V122" stroke="%s" stroke-width="0.85" stroke-opacity="0.85"/>'
        % theme.INK_SUB
    )
    el.append(theme.arch_mark(cx - 6.5, cy - 7.0, 13.0, theme.CYAN))

    p1x, p1y, d1 = _rel_motion_path(pulse_path_1, close=False)
    el.append(
        '<g transform="translate(%s %s)" filter="url(#%s-glow)">'
        '<circle r="3.4" fill="%s" fill-opacity="0.45"/>'
        '<circle r="2.0" fill="%s"/>'
        '<circle r="0.9" fill="%s"/>'
        '<animateMotion dur="3.6s" repeatCount="indefinite" path="%s"/>'
        "</g>"
        % (theme.num(p1x), theme.num(p1y), prefix, theme.CYAN, theme.CYAN, theme.INK, d1)
    )
    p2x, p2y, d2 = _rel_motion_path(pulse_path_2, close=False)
    el.append(
        '<g transform="translate(%s %s)" filter="url(#%s-glow)">'
        '<circle r="3.2" fill="%s" fill-opacity="0.45"/>'
        '<circle r="1.9" fill="%s"/>'
        '<circle r="0.85" fill="%s"/>'
        '<animateMotion dur="4.2s" begin="-1.6s" repeatCount="indefinite" path="%s"/>'
        "</g>"
        % (theme.num(p2x), theme.num(p2y), prefix, theme.PHOSPHOR, theme.PHOSPHOR_HI, theme.INK, d2)
    )

    return defs, el


def _artwork_reverser(prefix):
    cx, cy = 114.0, 108.0
    defs = [
        '<linearGradient id="%s-beam-in" gradientUnits="userSpaceOnUse" x1="20" y1="108" x2="82" y2="108">' % prefix,
        '<stop offset="0%%" stop-color="%s" stop-opacity="0.22"/>' % theme.INK,
        '<stop offset="50%%" stop-color="%s" stop-opacity="0.88"/>' % theme.INK,
        '<stop offset="100%%" stop-color="%s" stop-opacity="1"/>' % theme.INK,
        "</linearGradient>",
        '<linearGradient id="%s-facet-tl" x1="0" y1="0" x2="1" y2="1">' % prefix,
        '<stop offset="0%%" stop-color="%s" stop-opacity="0.32"/>' % theme.INK,
        '<stop offset="55%%" stop-color="%s" stop-opacity="0.22"/>' % theme.CYAN,
        '<stop offset="100%%" stop-color="%s" stop-opacity="0.45"/>' % theme.BG_PLATE_TOP,
        "</linearGradient>",
        '<linearGradient id="%s-facet-tr" x1="0" y1="0" x2="1" y2="1">' % prefix,
        '<stop offset="0%%" stop-color="%s" stop-opacity="0.36"/>' % theme.CORAL,
        '<stop offset="100%%" stop-color="%s" stop-opacity="0.65"/>' % theme.BG_PLATE_BOT,
        "</linearGradient>",
        '<linearGradient id="%s-facet-bl" x1="0" y1="0" x2="0" y2="1">' % prefix,
        '<stop offset="0%%" stop-color="%s" stop-opacity="0.68"/>' % theme.BG_WELL_ALT,
        '<stop offset="100%%" stop-color="%s" stop-opacity="0.82"/>' % theme.BG_VOID,
        "</linearGradient>",
        '<linearGradient id="%s-facet-br" x1="0" y1="0" x2="1" y2="1">' % prefix,
        '<stop offset="0%%" stop-color="%s" stop-opacity="0.24"/>' % theme.AMBER,
        '<stop offset="100%%" stop-color="%s" stop-opacity="0.78"/>' % theme.BG_VOID,
        "</linearGradient>",
        '<radialGradient id="%s-core-glow" cx="50%%" cy="50%%" r="50%%">' % prefix,
        '<stop offset="0%%" stop-color="%s" stop-opacity="0.95"/>' % theme.INK,
        '<stop offset="35%%" stop-color="%s" stop-opacity="0.65"/>' % theme.CORAL,
        '<stop offset="100%%" stop-color="%s" stop-opacity="0"/>' % theme.CORAL,
        "</radialGradient>",
    ]

    el = []
    el.append('<rect x="%d" y="%d" width="%d" height="%d" fill="url(#%s-ambient)"/>' % (CHAMBER_X, CHAMBER_Y, CHAMBER_W, CHAMBER_H, prefix))

    el.append(
        '<circle cx="%s" cy="%s" r="54" fill="none" stroke="%s" stroke-width="0.75" stroke-dasharray="2.5 3.5" stroke-opacity="0.72"/>'
        % (theme.num(cx), theme.num(cy), theme.STROKE_FRAME)
    )
    el.append(
        '<circle cx="%s" cy="%s" r="39.5" fill="none" stroke="%s" stroke-width="0.9" stroke-opacity="0.6"/>'
        % (theme.num(cx), theme.num(cy), theme.STROKE_SPECULAR)
    )

    for deg in range(0, 360, 15):
        rad = math.radians(deg)
        ca, sa = math.cos(rad), math.sin(rad)
        r0 = 39.5
        r1 = 35.0 if deg % 45 == 0 else 37.0
        el.append(
            '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="0.7" stroke-opacity="0.6"/>'
            % (
                theme.num(cx + ca * r0),
                theme.num(cy + sa * r0),
                theme.num(cx + ca * r1),
                theme.num(cy + sa * r1),
                theme.STROKE_SPECULAR,
            )
        )

    outer_ticks = ["<g>"]
    for deg in range(0, 360, 15):
        rad = math.radians(deg)
        ca, sa = math.cos(rad), math.sin(rad)
        major = deg % 45 == 0
        cardinal = deg % 90 == 0
        r0 = 51.0 if major else 52.5
        r1 = 58.0 if major else 56.2
        col = theme.CORAL if cardinal else (theme.SLATE if major else theme.STROKE_SPECULAR)
        sw = "1.1" if cardinal else ("0.85" if major else "0.65")
        outer_ticks.append(
            '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s" stroke-opacity="0.85"/>'
            % (
                theme.num(cx + ca * r0),
                theme.num(cy + sa * r0),
                theme.num(cx + ca * r1),
                theme.num(cy + sa * r1),
                col,
                sw,
            )
        )
        if cardinal:
            outer_ticks.append(
                '<circle cx="%s" cy="%s" r="1.4" fill="%s"/>'
                % (theme.num(cx + ca * 61.2), theme.num(cy + sa * 61.2), theme.CORAL)
            )
    outer_ticks.append(
        '<animateTransform attributeName="transform" type="rotate" from="0 %s %s" to="360 %s %s" dur="44s" repeatCount="indefinite"/>'
        % (theme.num(cx), theme.num(cy), theme.num(cx), theme.num(cy))
    )
    outer_ticks.append("</g>")
    el.append("".join(outer_ticks))

    el.append(theme.text(cx, 35, "000", theme.INK_MICRO, 5.8, "middle", "600", ' letter-spacing="0.4"'))
    el.append(theme.text(cx, 186, "180", theme.INK_MICRO, 5.8, "middle", "600", ' letter-spacing="0.4"'))

    hit_x, hit_y = 82.0, cy
    el.append(
        '<line x1="20" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="5.2" stroke-opacity="0.18" filter="url(#%s-glow)"/>'
        % (theme.num(hit_y), theme.num(hit_x), theme.num(hit_y), theme.INK, prefix)
    )
    el.append(
        '<line x1="20" y1="%s" x2="%s" y2="%s" stroke="url(#%s-beam-in)" stroke-width="2.2"/>'
        % (theme.num(hit_y), theme.num(hit_x), theme.num(hit_y), prefix)
    )
    el.append(
        '<line x1="20" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="0.9" stroke-opacity="0.92"/>'
        % (theme.num(hit_y), theme.num(hit_x), theme.num(hit_y), theme.INK)
    )

    v_top = (cx, cy - 42.0)
    v_bot = (cx, cy + 42.0)
    v_left = (cx - 33.0, cy)
    v_right = (cx + 33.0, cy)
    v_front = (cx - 6.0, cy + 6.0)
    v_back = (cx + 8.0, cy - 6.0)

    for target in (v_top, v_bot, v_left, v_right):
        el.append(
            '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="0.7" stroke-dasharray="2.2 2.2" stroke-opacity="0.5"/>'
            % (theme.num(v_back[0]), theme.num(v_back[1]), theme.num(target[0]), theme.num(target[1]), theme.STROKE_SPECULAR)
        )

    el.append(
        '<polygon points="%s" fill="url(#%s-facet-tl)" stroke="%s" stroke-width="0.95" stroke-linejoin="round"/>'
        % (_pts([v_top, v_left, v_front]), prefix, theme.INK_SUB)
    )
    el.append(
        '<polygon points="%s" fill="url(#%s-facet-tr)" stroke="%s" stroke-width="0.95" stroke-linejoin="round"/>'
        % (_pts([v_top, v_front, v_right]), prefix, theme.CORAL)
    )
    el.append(
        '<polygon points="%s" fill="url(#%s-facet-bl)" stroke="%s" stroke-width="0.9" stroke-linejoin="round"/>'
        % (_pts([v_left, v_bot, v_front]), prefix, theme.STROKE_SPECULAR)
    )
    el.append(
        '<polygon points="%s" fill="url(#%s-facet-br)" stroke="%s" stroke-width="0.9" stroke-linejoin="round"/>'
        % (_pts([v_front, v_right, v_bot]), prefix, theme.CORAL)
    )

    inner_scale = 0.54
    in_pts = [
        (cx + (vx - cx) * inner_scale, cy + (vy - cy) * inner_scale)
        for vx, vy in (v_top, v_right, v_bot, v_left)
    ]
    el.append(
        '<polygon points="%s" fill="none" stroke="%s" stroke-width="0.75" stroke-opacity="0.7"/>'
        % (_pts(in_pts), theme.CORAL)
    )
    for out_v, in_v in zip((v_top, v_right, v_bot, v_left), in_pts):
        el.append(
            '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="0.6" stroke-opacity="0.55"/>'
            % (theme.num(out_v[0]), theme.num(out_v[1]), theme.num(in_v[0]), theme.num(in_v[1]), theme.SLATE)
        )

    el.append(
        '<circle cx="%s" cy="%s" r="3.2" fill="%s" fill-opacity="0.7" filter="url(#%s-glow)"/>'
        % (theme.num(hit_x), theme.num(hit_y), theme.INK, prefix)
    )

    rays = [
        ("DOM", 72.0, (135.0, 92.0), theme.CYAN, "2.1s"),
        ("CSS", 96.0, (143.0, 102.0), theme.PHOSPHOR, "2.5s"),
        ("AST", 120.0, (143.0, 114.0), theme.AMBER, "2.9s"),
        ("RAW", 144.0, (135.0, 124.0), theme.CORAL, "2.3s"),
    ]
    core_x, core_y = cx - 2.0, cy
    for label, ry, exit_pt, col, dur in rays:
        el.append(
            '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="0.95" stroke-opacity="0.55"/>'
            % (theme.num(core_x), theme.num(core_y), theme.num(exit_pt[0]), theme.num(exit_pt[1]), col)
        )
        ray_pts = [exit_pt, (176.0, ry), (210.0, ry)]
        ray_d = _path(ray_pts)
        el.append(
            '<path d="%s" fill="none" stroke="%s" stroke-width="3.6" stroke-opacity="0.2" stroke-linejoin="round"/>'
            % (ray_d, col)
        )
        el.append(
            '<path d="%s" fill="none" stroke="%s" stroke-width="1.3" stroke-opacity="0.95" stroke-linejoin="round"/>'
            % (ray_d, col)
        )
        el.append(
            '<path d="%s" fill="none" stroke="%s" stroke-width="1.4" stroke-dasharray="5 12" stroke-opacity="0.95">'
            '<animate attributeName="stroke-dashoffset" from="17" to="0" dur="%s" repeatCount="indefinite"/>'
            "</path>"
            % (ray_d, theme.INK, dur)
        )
        el.append('<circle cx="210" cy="%s" r="2.1" fill="%s"/>' % (theme.num(ry), col))
        el.append(
            '<line x1="210" y1="%s" x2="210" y2="%s" stroke="%s" stroke-width="0.8" stroke-opacity="0.7"/>'
            % (theme.num(ry - 4.5), theme.num(ry + 4.5), col)
        )
        el.append(
            theme.text(235, ry + 2.4, label, col, 6.5, "end", "700", ' letter-spacing="0.6"', theme.FONT_MONO)
        )

    el.append(
        '<g filter="url(#%s-glow)">'
        '<circle cx="%s" cy="%s" r="11" fill="url(#%s-core-glow)">'
        '<animate attributeName="r" values="9;13.5;9" dur="3.2s" repeatCount="indefinite"/>'
        "</circle>"
        '<circle cx="%s" cy="%s" r="4.2" fill="none" stroke="%s" stroke-width="1.05" stroke-opacity="0.9">'
        '<animate attributeName="r" values="3.6;5.2;3.6" dur="3.2s" repeatCount="indefinite"/>'
        "</circle>"
        '<circle cx="%s" cy="%s" r="2.1" fill="%s"/>'
        "</g>"
        % (
            prefix,
            theme.num(core_x),
            theme.num(core_y),
            prefix,
            theme.num(core_x),
            theme.num(core_y),
            theme.CORAL,
            theme.num(core_x),
            theme.num(core_y),
            theme.INK,
        )
    )

    for vx, vy in (v_top, v_bot, v_left, v_right, v_front):
        el.append(
            '<circle cx="%s" cy="%s" r="1.5" fill="%s" stroke="%s" stroke-width="0.65"/>'
            % (theme.num(vx), theme.num(vy), theme.BG_VOID, theme.INK_SUB)
        )

    return defs, el


def _right_spec_plate(prefix, index_label, title, micro_spec, tag, accent, lang, stars, disk_kb):
    el = []
    el.append(
        theme.text(264, 40, index_label, accent, 9.5, "start", "700", ' letter-spacing="1.2"', theme.FONT_MONO)
    )

    el.append(
        '<path d="%s" fill="%s" stroke="%s" stroke-width="1"/>'
        % (_chamfer_rect_path(544, 24, 24, 24, 4.5), theme.BG_WELL_ALT, theme.STROKE_FRAME)
    )
    el.append('<line x1="549" y1="25" x2="557" y2="25" stroke="%s" stroke-width="0.8" stroke-opacity="0.5"/>' % theme.STROKE_SPECULAR)
    el.append(
        '<path d="M558 24 H563.5 L568 28.5 V34" fill="none" stroke="%s" stroke-width="1.05" stroke-opacity="0.72"/>'
        % accent
    )
    el.append(
        '<path d="M552 40 L560 32 M554 32 H560 V38" fill="none" stroke="%s" stroke-width="1.45" stroke-linecap="round" stroke-linejoin="round"/>'
        % theme.INK
    )

    el.append(
        theme.text(264, 76, title, theme.INK, 22, "start", "700", ' letter-spacing="-0.3"', theme.FONT_DISPLAY)
    )
    el.append(
        theme.text(264, 100, micro_spec, theme.INK_SUB, 10.5, "start", "500", ' letter-spacing="0.2"', theme.FONT_MONO)
    )

    el.append('<line x1="264" y1="124" x2="568" y2="124" stroke="url(#%s-div-grad)" stroke-width="1"/>' % prefix)
    el.append('<line x1="264" y1="124" x2="296" y2="124" stroke="%s" stroke-width="2.2"/>' % accent)
    el.append('<line x1="568" y1="121.5" x2="568" y2="126.5" stroke="%s" stroke-width="1"/>' % theme.STROKE_SPECULAR)

    tag_w = max(72.0, len(tag) * 5.45 + 22.0)
    el.append(
        '<rect x="264" y="137" width="%s" height="22" rx="4.5" fill="%s" stroke="%s" stroke-width="1"/>'
        % (theme.num(tag_w), theme.BG_WELL, theme.STROKE_FRAME)
    )
    el.append('<rect x="264.5" y="141" width="2.2" height="14" rx="1" fill="%s"/>' % accent)
    el.append(
        theme.text(275, 151.3, tag, accent, 9.0, "start", "600", ' letter-spacing="0.2"', theme.FONT_MONO)
    )

    disk_text = theme.disk_label(disk_kb)
    disk_x = 264.0 + tag_w + 10.0
    disk_w = max(56.0, len(disk_text) * 5.55 + 20.0)
    el.append(
        '<rect x="%s" y="137" width="%s" height="22" rx="4.5" fill="%s" stroke="%s" stroke-width="1"/>'
        % (theme.num(disk_x), theme.num(disk_w), theme.BG_WELL_ALT, theme.STROKE_HAIR)
    )
    el.append(
        theme.text(
            disk_x + disk_w * 0.5,
            151.3,
            disk_text,
            theme.INK_SUB,
            9.0,
            "middle",
            "500",
            ' letter-spacing="0.2"',
            theme.FONT_MONO,
        )
    )

    lang_color = theme.LANG_COLORS.get(lang, accent)
    el.append(
        '<circle cx="268.5" cy="182.2" r="5.8" fill="none" stroke="%s" stroke-width="0.85" stroke-opacity="0.32"/>'
        % lang_color
    )
    el.append('<circle cx="268.5" cy="182.2" r="3.6" fill="%s"/>' % lang_color)
    el.append(theme.text(280, 186, lang, theme.INK, 10.5, "start", "700", "", theme.FONT_MONO))

    star_cx = max(368.0, 280.0 + len(lang) * 6.5 + 22.0)
    el.append('<path d="%s" fill="%s"/>' % (theme.star_path(star_cx, 181.8, 5.4, 2.3), theme.AMBER))
    el.append(theme.text(star_cx + 10.5, 186, str(stars), theme.AMBER, 11, "start", "700", "", theme.FONT_MONO))

    el.append(
        '<circle cx="491" cy="182.8" r="1.8" fill="%s" fill-opacity="0.85">'
        '<animate attributeName="fill-opacity" values="0.9;0.25;0.9" dur="2.8s" repeatCount="indefinite"/>'
        "</circle>"
        % accent
    )
    el.append(
        theme.text(568, 186, "LIVE // SYNC", theme.INK_MICRO, 8.5, "end", "600", ' letter-spacing="0.9"', theme.FONT_MONO)
    )
    return el


def _render_card(spec, repo_map):
    prefix = spec["prefix"]
    accent = spec["accent"]
    meta = (repo_map or {}).get(spec["repo_key"]) or {}
    stars = int(meta.get("stars") or 0)
    disk_kb = int(meta.get("disk_kb") or 0)
    lang = str(meta.get("lang") or spec["default_lang"])

    chassis_defs, chassis_body = theme.chassis_plate(
        CARD_W,
        CARD_H,
        prefix,
        accent=accent,
        grid_opacity=0.52,
        radius=14,
    )
    art_defs, art_body = spec["artwork"](prefix)
    chamber_bg, chamber_top = _chamber_chrome(prefix, accent)

    defs = []
    defs.extend(theme.common_defs(prefix))
    defs.extend(chassis_defs)
    defs.extend(_chamber_base_defs(prefix, accent))
    defs.extend(art_defs)

    aria = "%s — %s" % (spec["title"], spec["micro_spec"])
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" role="img" aria-label="%s">'
        % (CARD_W, CARD_H, CARD_W, CARD_H, theme.esc(aria)),
        theme.REDUCED_MOTION_STYLE,
        "<defs>",
        *defs,
        "</defs>",
        *chassis_body,
        *chamber_bg,
        '<g clip-path="url(#%s-chamber-clip)">' % prefix,
        *art_body,
        "</g>",
        *chamber_top,
        *_right_spec_plate(
            prefix,
            spec["index"],
            spec["title"],
            spec["micro_spec"],
            spec["tag"],
            accent,
            lang,
            stars,
            disk_kb,
        ),
        "</svg>",
    ]
    return "\n".join(parts)


CARD_SPECS = (
    {
        "filename": "card-fforum.svg",
        "prefix": "ff",
        "repo_key": "f_forumv3",
        "index": "01 // PLATFORM",
        "title": "F-Forum v3",
        "micro_spec": "Spatial UI Workbench",
        "tag": "fforum3.vercel.app",
        "accent": theme.PHOSPHOR,
        "default_lang": "TypeScript",
        "artwork": _artwork_fforum,
    },
    {
        "filename": "card-vault.svg",
        "prefix": "kv",
        "repo_key": "SOURCEOFKNOWLEDGFORAI",
        "index": "02 // ARCHIVE",
        "title": "Knowledge Vault",
        "micro_spec": "6-Source UI/3D Index",
        "tag": "6 libraries",
        "accent": theme.AMBER,
        "default_lang": "HTML",
        "artwork": _artwork_vault,
    },
    {
        "filename": "card-edunext.svg",
        "prefix": "ed",
        "repo_key": "Edunext_fe",
        "index": "03 // ENGINE",
        "title": "EduNext BAS",
        "micro_spec": "DOM & Prompt Engine",
        "tag": "userscript",
        "accent": theme.CYAN,
        "default_lang": "JavaScript",
        "artwork": _artwork_edunext,
    },
    {
        "filename": "card-reverser.svg",
        "prefix": "rv",
        "repo_key": "shoptify-winter-reverser-engine",
        "index": "04 // REVERSING",
        "title": "Winter '26 Reverser",
        "micro_spec": "Offline Architecture Mirror",
        "tag": "decompiler",
        "accent": theme.CORAL,
        "default_lang": "HTML",
        "artwork": _artwork_reverser,
    },
)


def render_flagship_cards(repo_map):
    return {spec["filename"]: _render_card(spec, repo_map) for spec in CARD_SPECS}
