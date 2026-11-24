import math

from theme import (
    BG_WELL,
    BORDER_SUBTLE,
    BORDER_WARM,
    CADMIUM,
    CERULEAN,
    CREAM,
    EMERALD_MID,
    EMERALD_SOFT,
    FIREFLY_GOLD,
    FONT_DISPLAY,
    FONT_MONO,
    INK_MUTED,
    INK_PRIMARY,
    INK_SECOND,
    IVORY,
    IVORY_WARM,
    LANG_PALETTE,
    MILKY_DUST,
    REDUCED_MOTION_STYLE,
    SKY_SOFT,
    TEAL_MIST,
    esc,
    nocturne_card,
    nocturne_defs,
    num,
    star_path,
    text,
    van_gogh_starry_backdrop,
)

CARD_W = 392
CARD_H = 264


def _cam_project(vx, vy, vz, cx=196.0, cy=82.0, yaw_deg=-34.0, pitch_deg=26.0, fov=260.0, cam_dist=210.0):
    yaw = math.radians(yaw_deg)
    pitch = math.radians(pitch_deg)
    x1 = vx * math.cos(yaw) - vz * math.sin(yaw)
    z1 = vx * math.sin(yaw) + vz * math.cos(yaw)
    y2 = vy * math.cos(pitch) - z1 * math.sin(pitch)
    z2 = vy * math.sin(pitch) + z1 * math.cos(pitch)
    scale = fov / max(60.0, cam_dist + z2)
    return cx + x1 * scale, cy - y2 * scale, z2


def _render_mesh(faces, lines, cx=196.0, cy=82.0, yaw_deg=-34.0, pitch_deg=26.0):
    drawable = []
    for pts3d, fill_col, fill_op, stroke_col, stroke_w, stroke_op in faces:
        proj = [_cam_project(px, py, pz, cx, cy, yaw_deg, pitch_deg) for px, py, pz in pts3d]
        avg_z = sum(p[2] for p in proj) / float(len(proj))
        pts_attr = " ".join("%s,%s" % (num(p[0], 1), num(p[1], 1)) for p in proj)
        svg = (
            '<polygon points="%s" fill="%s" fill-opacity="%s" stroke="%s" stroke-width="%s" stroke-opacity="%s" stroke-linejoin="round"/>'
            % (pts_attr, fill_col, num(fill_op, 2), stroke_col, num(stroke_w, 2), num(stroke_op, 2))
        )
        drawable.append((avg_z, svg))

    for p0, p1, col, sw, sop, dash in lines:
        a = _cam_project(p0[0], p0[1], p0[2], cx, cy, yaw_deg, pitch_deg)
        b = _cam_project(p1[0], p1[1], p1[2], cx, cy, yaw_deg, pitch_deg)
        avg_z = (a[2] + b[2]) * 0.5 - 0.5
        dash_attr = ' stroke-dasharray="%s"' % dash if dash else ""
        svg = '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s" stroke-opacity="%s" stroke-linecap="round"%s/>' % (
            num(a[0], 1), num(a[1], 1), num(b[0], 1), num(b[1], 1), col, num(sw, 2), num(sop, 2), dash_attr
        )
        drawable.append((avg_z, svg))

    # Sort back-to-front (largest z2 is farthest away)
    drawable.sort(key=lambda item: item[0], reverse=True)
    return [svg for _, svg in drawable]


def _box_faces(x0, x1, y0, y1, z0, z1, top_fill, side_fill, stroke_col, fill_op=0.82, stroke_w=0.95):
    return [
        ([(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)], top_fill, fill_op, stroke_col, stroke_w, 0.85),
        ([(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)], side_fill, fill_op, stroke_col, stroke_w * 0.85, 0.72),
        ([(x1, y0, z0), (x1, y0, z1), (x1, y1, z1), (x1, y1, z0)], side_fill, fill_op * 0.9, stroke_col, stroke_w * 0.85, 0.72),
        ([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], side_fill, fill_op * 0.75, stroke_col, stroke_w * 0.8, 0.55),
        ([(x0, y0, z0), (x0, y0, z1), (x0, y1, z1), (x0, y1, z0)], side_fill, fill_op * 0.85, stroke_col, stroke_w * 0.8, 0.65),
    ]


def _art_v3_citadel():
    # 3D Astral UI Atrium & Spatial Workbench Citadel (Octagonal terraced plinth + central 12-facet crystal + orbital UI frames)
    faces = []
    lines = []

    for tier_i, (rad, y_bot, y_top, fill_t, fill_s, strk) in enumerate((
        (56.0, -28.0, -21.0, "#0b1c2c", "#07121e", BORDER_WARM),
        (41.0, -21.0, -14.0, "#0f293c", "#091a28", TEAL_MIST),
        (26.0, -14.0, -9.0, "#123548", "#0b2232", EMERALD_SOFT),
    )):
        pts_top = []
        pts_bot = []
        for k in range(8):
            ang = k * math.pi / 4.0 + math.pi / 8.0
            pts_top.append((math.cos(ang) * rad, y_top, math.sin(ang) * rad))
            pts_bot.append((math.cos(ang) * rad, y_bot, math.sin(ang) * rad))
        faces.append((pts_top, fill_t, 0.86, strk, 1.0, 0.82 if tier_i > 0 else 0.58))
        for k in range(8):
            nk = (k + 1) % 8
            faces.append(([pts_bot[k], pts_bot[nk], pts_top[nk], pts_top[k]], fill_s, 0.88, strk, 0.8, 0.62))

    # 4 floating glass UI specimen panels around the atrium
    for idx, ang_deg in enumerate((25.0, 115.0, 205.0, 295.0)):
        ang = math.radians(ang_deg)
        dist = 36.0
        px, pz = math.cos(ang) * dist, math.sin(ang) * dist
        tx, tz = -math.sin(ang) * 11.5, math.cos(ang) * 11.5
        col_s = EMERALD_SOFT if idx % 2 == 0 else SKY_SOFT
        panel = [
            (px - tx, 1.0, pz - tz),
            (px + tx, 1.0, pz + tz),
            (px + tx, 15.5, pz + tz),
            (px - tx, 15.5, pz - tz),
        ]
        faces.append((panel, "#102840", 0.56, col_s, 1.05, 0.88))
        lines.append(((px, -9.0, pz), (px, 1.0, pz), col_s, 0.8, 0.52, "2 2"))

    # Central 12-facet illuminated bipyramid holo-crystal
    apex_top = (0.0, 31.0, 0.0)
    apex_bot = (0.0, -4.0, 0.0)
    ring_c = []
    for k in range(6):
        ang = k * math.pi / 3.0
        ring_c.append((math.cos(ang) * 14.5, 13.5, math.sin(ang) * 14.5))
    for k in range(6):
        nk = (k + 1) % 6
        c_fill = CADMIUM if k in (0, 5) else (EMERALD_MID if k in (1, 2) else SKY_SOFT)
        faces.append(([apex_top, ring_c[k], ring_c[nk]], c_fill, 0.34, CREAM, 1.1, 0.92))
        faces.append(([apex_bot, ring_c[nk], ring_c[k]], "#134e4a", 0.42, EMERALD_SOFT, 0.95, 0.78))

    # Dual tilted brass armillary meridian rings
    for tilt_x, tilt_z, r_orb, r_col in ((0.38, -0.22, 48.0, CREAM), (-0.32, 0.30, 44.0, SKY_SOFT)):
        prev = None
        for step in range(25):
            a = step * 2.0 * math.pi / 24.0
            ox = math.cos(a) * r_orb
            oz = math.sin(a) * r_orb
            oy = 9.0 + ox * tilt_x + oz * tilt_z
            cur = (ox, oy, oz)
            if prev is not None:
                lines.append((prev, cur, r_col, 0.95, 0.58, "3 2" if r_col == SKY_SOFT else ""))
            prev = cur

    nodes = _render_mesh(faces, lines, cx=196.0, cy=81.0, yaw_deg=-32.0, pitch_deg=24.0)
    ax, ay, _ = _cam_project(0.0, 31.0, 0.0, cx=196.0, cy=81.0, yaw_deg=-32.0, pitch_deg=24.0)
    nodes.append('<circle cx="%s" cy="%s" r="9.5" fill="url(#ff3-ff-gold)"/>' % (num(ax, 1), num(ay, 1)))
    nodes.append('<circle cx="%s" cy="%s" r="2.6" fill="#ffffff"/>' % (num(ax, 1), num(ay, 1)))
    return nodes


def _art_v2_viaduct():
    # 3D Twin-Pylon Catenary Suspension Viaduct (Perspective bridge deck + A-frame lattice towers + parabolic cables + hangers)
    faces = []
    lines = []

    # Water reflection ellipses under the piers
    for px in (-42.0, 42.0):
        faces.extend(_box_faces(px - 8.5, px + 8.5, -28.0, -19.0, -10.5, 10.5, "#132946", "#0b192e", SKY_SOFT, 0.88, 0.9))

    # Orthotropic 3D bridge deck spanning x = -78..+78
    faces.extend(_box_faces(-78.0, 78.0, -9.5, -5.2, -8.0, 8.0, "#132948", "#0a172b", SKY_SOFT, 0.90, 1.0))
    # Glowing center transit lane on deck
    lines.append(((-76.0, -4.9, 0.0), (76.0, -4.9, 0.0), CADMIUM, 1.35, 0.88, "5 4"))
    lines.append(((-76.0, -4.9, -5.2), (76.0, -4.9, -5.2), TEAL_MIST, 0.85, 0.55, ""))
    lines.append(((-76.0, -4.9, 5.2), (76.0, -4.9, 5.2), TEAL_MIST, 0.85, 0.55, ""))

    # Twin A-frame lattice suspension towers at x = -42 and x = +42
    for tx in (-42.0, 42.0):
        for side_z in (-7.2, 7.2):
            lines.append(((tx - 3.2, -19.0, side_z), (tx - 1.1, 32.0, side_z * 0.42), CREAM, 1.5, 0.92, ""))
            lines.append(((tx + 3.2, -19.0, side_z), (tx + 1.1, 32.0, side_z * 0.42), CREAM, 1.5, 0.92, ""))
        for portal_y, z_scale in ((4.0, 0.78), (18.0, 0.58), (31.0, 0.44)):
            lines.append(((tx, portal_y, -7.2 * z_scale), (tx, portal_y, 7.2 * z_scale), FIREFLY_GOLD, 1.25, 0.85, ""))
        # Cross-bracing X struts
        lines.append(((tx, 4.0, -5.6), (tx, 18.0, 4.2), SKY_SOFT, 0.8, 0.55, ""))
        lines.append(((tx, 4.0, 5.6), (tx, 18.0, -4.2), SKY_SOFT, 0.8, 0.55, ""))

    # Dual parabolic main catenary cables & vertical suspender hangers (front & rear planes)
    def cable_y(x_val):
        if abs(x_val) <= 42.0:
            u = x_val / 42.0
            return 2.5 + 29.5 * (u * u)
        u = (abs(x_val) - 42.0) / 36.0
        return 32.0 * ((1.0 - u) ** 1.35) - 5.0 * u

    for z_plane, c_col, c_op in ((-6.8, SKY_SOFT, 0.65), (6.8, CADMIUM, 0.95)):
        prev_pt = None
        for step in range(-78, 79, 6):
            fx = float(step)
            cur_pt = (fx, cable_y(fx), z_plane * (0.45 + 0.55 * (1.0 - cable_y(fx) / 36.0)))
            if prev_pt is not None:
                lines.append((prev_pt, cur_pt, c_col, 1.35, c_op, ""))
            prev_pt = cur_pt
            if step % 12 == 0 and abs(step) not in (42, 78):
                lines.append(((fx, -5.0, z_plane * 0.85), cur_pt, CREAM, 0.72, c_op * 0.58, ""))

    nodes = _render_mesh(faces, lines, cx=196.0, cy=83.0, yaw_deg=-25.0, pitch_deg=20.0)
    # Animated starlight packet traversing deck from v1 anchorage to v3 anchorage
    p_start = _cam_project(-74.0, -4.8, 0.0, cx=196.0, cy=83.0, yaw_deg=-25.0, pitch_deg=20.0)
    p_end = _cam_project(74.0, -4.8, 0.0, cx=196.0, cy=83.0, yaw_deg=-25.0, pitch_deg=20.0)
    deck_path = "M%s,%s L%s,%s" % (num(p_start[0], 1), num(p_start[1], 1), num(p_end[0], 1), num(p_end[1], 1))
    nodes.append(
        '<g><circle r="5.5" fill="url(#ff2-ff-gold)"/><circle r="1.7" fill="#ffffff"/>'
        '<animateMotion path="%s" dur="5.8s" repeatCount="indefinite"/></g>' % deck_path
    )
    return nodes


def _art_v1_rotunda():
    # 3D Socratic Rotunda & Sculpted Open Codex Pavilion (Stepped circular amphitheater + 8 fluted columns + ribbed dome + 3D open codex)
    faces = []
    lines = []

    for rad, y_b, y_t, f_top, f_side, strk in (
        (54.0, -28.0, -22.0, "#142038", "#0b1324", BORDER_WARM),
        (44.0, -22.0, -16.5, "#192946", "#0e192d", FIREFLY_GOLD),
    ):
        pts_t = []
        pts_b = []
        for k in range(12):
            ang = k * 2.0 * math.pi / 12.0
            pts_t.append((math.cos(ang) * rad, y_t, math.sin(ang) * rad))
            pts_b.append((math.cos(ang) * rad, y_b, math.sin(ang) * rad))
        faces.append((pts_t, f_top, 0.88, strk, 0.95, 0.72))
        for k in range(12):
            nk = (k + 1) % 12
            faces.append(([pts_b[k], pts_b[nk], pts_t[nk], pts_t[k]], f_side, 0.90, strk, 0.75, 0.55))

    # 8 classical rotunda columns supporting upper entablature ring & celestial dome ribs
    col_r = 37.0
    ring_pts = []
    for k in range(16):
        ang = k * 2.0 * math.pi / 16.0
        ring_pts.append((math.cos(ang) * col_r, 15.0, math.sin(ang) * col_r))
    for k in range(16):
        lines.append((ring_pts[k], ring_pts[(k + 1) % 16], CREAM, 1.25, 0.82, ""))

    for k in range(8):
        ang = k * 2.0 * math.pi / 8.0 + 0.22
        cx_p = math.cos(ang) * col_r
        cz_p = math.sin(ang) * col_r
        lines.append(((cx_p, -16.5, cz_p), (cx_p, 15.0, cz_p), IVORY_WARM, 1.85, 0.86, ""))
        # Ribbed observatory dome meridian from entablature to oculus
        prev_d = (cx_p, 15.0, cz_p)
        for st in range(1, 6):
            u = st / 5.0
            dr = col_r * math.cos(u * math.pi * 0.44)
            dy = 15.0 + math.sin(u * math.pi * 0.44) * 19.0
            cur_d = (math.cos(ang) * dr, dy, math.sin(ang) * dr)
            lines.append((prev_d, cur_d, SKY_SOFT if k % 2 else FIREFLY_GOLD, 0.88, 0.55, ""))
            prev_d = cur_d

    # Sculpted 3D Open Codex Monument on central lectern
    faces.extend(_box_faces(-6.0, 6.0, -16.5, -8.5, -5.0, 5.0, "#243452", "#131d33", CREAM, 0.9, 0.9))
    left_page = [(-1.0, -7.5, -10.0), (-19.5, -2.5, -9.0), (-19.5, -2.5, 9.5), (-1.0, -7.5, 10.5)]
    right_page = [(1.0, -7.5, -10.0), (19.5, -2.5, -9.0), (19.5, -2.5, 9.5), (1.0, -7.5, 10.5)]
    faces.append((left_page, "#1c2d4a", 0.94, CADMIUM, 1.15, 0.95))
    faces.append((right_page, "#223659", 0.94, CADMIUM, 1.15, 0.95))
    for row_z in (-5.0, -1.0, 3.0, 6.5):
        lines.append(((-4.0, -6.4, row_z), (-16.0, -3.2, row_z), CREAM, 0.85, 0.68, ""))
        lines.append(((4.0, -6.4, row_z), (16.0, -3.2, row_z), SKY_SOFT, 0.85, 0.68, ""))

    nodes = _render_mesh(faces, lines, cx=196.0, cy=84.0, yaw_deg=-30.0, pitch_deg=24.0)
    ox, oy, _ = _cam_project(0.0, 33.5, 0.0, cx=196.0, cy=84.0, yaw_deg=-30.0, pitch_deg=24.0)
    nodes.append('<circle cx="%s" cy="%s" r="8.5" fill="url(#ff1-ff-gold)"/>' % (num(ox, 1), num(oy, 1)))
    nodes.append('<circle cx="%s" cy="%s" r="2.3" fill="#ffffff"/>' % (num(ox, 1), num(oy, 1)))
    return nodes


def _render_single_card(prefix, title, subtitle, domain_tag, badge_tag, accent, art_nodes, meta, seed):
    clip_defs, frame_nodes = nocturne_card(CARD_W, CARD_H, prefix, radius=16)
    raw_lang = meta.get("lang") or ""
    lang = "TypeScript" if raw_lang in ("", "Code") else raw_lang
    stars = int(meta.get("stars") or 0)
    lang_col = LANG_PALETTE.get(lang, (accent, CREAM))[0]

    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" role="img" aria-label="%s — %s">'
        % (CARD_W, CARD_H, CARD_W, CARD_H, esc(title), esc(subtitle)),
        REDUCED_MOTION_STYLE,
        "<defs>",
    ]
    parts.extend(nocturne_defs(prefix))
    parts.extend(clip_defs)
    parts.extend(
        [
            '<radialGradient id="%s-stage-glow" cx="50%%" cy="54%%" r="56%%">' % prefix,
            '<stop offset="0%%" stop-color="%s" stop-opacity="0.20"/>' % accent,
            '<stop offset="65%%" stop-color="%s" stop-opacity="0.06"/>' % CERULEAN,
            '<stop offset="100%%" stop-color="%s" stop-opacity="0"/>' % BG_WELL,
            "</radialGradient>",
            '<clipPath id="%s-art-clip"><rect x="16" y="16" width="360" height="134" rx="11"/></clipPath>' % prefix,
            "</defs>",
        ]
    )
    parts.extend(frame_nodes)

    parts.append('<rect x="16" y="16" width="360" height="134" rx="11" fill="%s" stroke="%s" stroke-width="1"/>' % (BG_WELL, BORDER_WARM))
    parts.append('<g clip-path="url(#%s-art-clip)">' % prefix)
    parts.append('<rect x="16" y="16" width="360" height="134" fill="url(#%s-stage-glow)"/>' % prefix)
    parts.extend(
        van_gogh_starry_backdrop(
            prefix,
            376,
            148,
            seed=seed,
            stroke_count=46,
            star_aureoles=3,
            moon_pos=(336.0, 42.0, 7.5) if prefix == "ff3" else None,
            opacity_scale=0.82,
        )
    )
    parts.extend(art_nodes)
    # 360° 3D architectural badge inside top-left of viewport well
    parts.append('<rect x="25" y="25" width="68" height="19" rx="5" fill="#071020" fill-opacity="0.84" stroke="%s" stroke-width="0.8"/>' % BORDER_WARM)
    parts.append(text(59, 38, badge_tag, MILKY_DUST, 9.2, "middle", "600"))
    parts.append("</g>")

    parts.append(text(24, 180, title, INK_PRIMARY, 18.5, "start", "700", ' letter-spacing="-0.2"', FONT_DISPLAY))
    if domain_tag:
        parts.append(text(CARD_W - 24, 179, domain_tag, accent, 10.2, "end", "600"))
    parts.append(text(24, 203, subtitle, INK_SECOND, 11.4, "start", "400", "", FONT_DISPLAY))

    parts.append('<line x1="24" y1="221" x2="%d" y2="221" stroke="%s" stroke-width="1"/>' % (CARD_W - 24, BORDER_SUBTLE))

    parts.append('<circle cx="29" cy="240.5" r="3.8" fill="%s"/>' % lang_col)
    parts.append(text(40, 244.5, lang, INK_PRIMARY, 11, "start", "600"))
    parts.append('<path d="%s" fill="%s"/>' % (star_path(138, 240.2, 5.5, 2.3), FIREFLY_GOLD))
    parts.append(text(149, 244.5, str(stars), CREAM, 11, "start", "700"))
    parts.append(text(CARD_W - 40, 244.5, "360° 3D", INK_MUTED, 10, "end", "500"))
    parts.append(
        '<path d="M%d 245 L%d 236 M%d 236 H%d M%d 236 V242" fill="none" stroke="%s" stroke-width="1.35" stroke-linecap="round" stroke-linejoin="round"/>'
        % (CARD_W - 33, CARD_W - 24, CARD_W - 30, CARD_W - 24, CARD_W - 24, accent)
    )

    parts.append("</svg>")
    return "\n".join(parts)


def render_flagship_cards(repo_map):
    specs = [
        (
            "card-fforum-v3.svg",
            "ff3",
            "f_forumv3",
            "F-Forum v3",
            "Spatial UI/3D Workbench & 7,750-Specimen Vault",
            "fforum3.vercel.app",
            "CITADEL 3D",
            EMERALD_MID,
            _art_v3_citadel(),
            303,
        ),
        (
            "card-fforum-v2.svg",
            "ff2",
            "F-Forum_v2",
            "F-Forum v2",
            "Generational Catenary Bridge Architecture",
            "v2-bridge",
            "VIADUCT 3D",
            SKY_SOFT,
            _art_v2_viaduct(),
            202,
        ),
        (
            "card-fforum-v1.svg",
            "ff1",
            "f-forum",
            "F-Forum v1",
            "Campus Q&A Forum, Student Clubs & Exam Vault",
            "f-forum.vercel.app",
            "ROTUNDA 3D",
            FIREFLY_GOLD,
            _art_v1_rotunda(),
            101,
        ),
    ]
    out = {}
    for fname, prefix, key, title, subtitle, domain_tag, badge_tag, accent, art_nodes, seed in specs:
        out[fname] = _render_single_card(prefix, title, subtitle, domain_tag, badge_tag, accent, art_nodes, repo_map.get(key, {}), seed)
    return out
