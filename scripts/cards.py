# SPDX-License-Identifier: MIT
import json
import math
import os

from theme import (
    BG_WELL,
    BORDER_SUBTLE,
    BORDER_WARM,
    CADMIUM,
    CREAM,
    EMERALD_MID,
    FIREFLY_GOLD,
    FONT_DISPLAY,
    INK_MUTED,
    INK_PRIMARY,
    INK_SECOND,
    LANG_PALETTE,
    REDUCED_MOTION_STYLE,
    SKY_SOFT,
    esc,
    nocturne_card,
    nocturne_defs,
    num,
    shade_hex,
    star_path,
    text,
    van_gogh_starry_backdrop,
)

CARD_W = 392
CARD_H = 264


def _load_blender_models():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(root, "assets", "models_3d.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    return {}


def _cam_project(vx, vy, vz, cx=196.0, cy=100.0, yaw_deg=28.0, pitch_deg=21.0, fov=268.0, cam_dist=218.0):
    yaw = math.radians(yaw_deg)
    pitch = math.radians(pitch_deg)
    x1 = vx * math.cos(yaw) + vz * math.sin(yaw)
    z1 = -vx * math.sin(yaw) + vz * math.cos(yaw)
    y2 = vy * math.cos(pitch) - z1 * math.sin(pitch)
    z2 = vy * math.sin(pitch) + z1 * math.cos(pitch)
    scale = fov / max(62.0, cam_dist - z2)
    return cx + x1 * scale, cy - y2 * scale, z2


def _face_normal(pts):
    if len(pts) < 3:
        return 0.0, 1.0, 0.0
    ax, ay, az = pts[1][0] - pts[0][0], pts[1][1] - pts[0][1], pts[1][2] - pts[0][2]
    bx, by, bz = pts[2][0] - pts[0][0], pts[2][1] - pts[0][1], pts[2][2] - pts[0][2]
    nx = ay * bz - az * by
    ny = az * bx - ax * bz
    nz = ax * by - ay * bx
    ln = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
    return nx / ln, ny / ln, nz / ln


def _render_blender_model(model_data, yaw_deg=28.0, pitch_deg=21.0, fov=262.0, cy=102.0):
    lx, ly, lz = 0.42, 0.78, 0.46
    drawable = []

    for f in model_data.get("faces") or []:
        pts3d = f["pts"]
        proj = [_cam_project(px, py, pz, 196.0, cy, yaw_deg, pitch_deg, fov) for px, py, pz in pts3d]
        avg_z = sum(p[2] for p in proj) / float(len(proj))
        nx, ny, nz = _face_normal(pts3d)
        ndotl = abs(nx * lx + ny * ly + nz * lz)
        cx_f = sum(p[0] for p in pts3d) / float(len(pts3d))
        cy_f = sum(p[1] for p in pts3d) / float(len(pts3d))
        cz_f = sum(p[2] for p in pts3d) / float(len(pts3d))
        hearth = math.exp(-(cx_f * cx_f + (cy_f - 2.0) ** 2 + cz_f * cz_f) / 1450.0)
        emissive = bool(f.get("emissive"))
        shade = 0.68 + 0.52 * ndotl + (0.28 if emissive else 0.0)
        lit_col = shade_hex(f["fill"], shade, hearth * (0.45 if emissive else 0.14))
        pts_attr = " ".join("%s,%s" % (num(p[0], 1), num(p[1], 1)) for p in proj)
        svg = (
            '<polygon points="%s" fill="%s" fill-opacity="%s" stroke="%s" stroke-width="0.78" stroke-opacity="0.78" stroke-linejoin="round"/>'
            % (pts_attr, lit_col, num(f.get("alpha", 0.92), 2), f["stroke"])
        )
        drawable.append((avg_z, svg))

    for ln in model_data.get("lines") or []:
        p0, p1 = ln["p0"], ln["p1"]
        a = _cam_project(p0[0], p0[1], p0[2], 196.0, cy, yaw_deg, pitch_deg, fov)
        b = _cam_project(p1[0], p1[1], p1[2], 196.0, cy, yaw_deg, pitch_deg, fov)
        avg_z = (a[2] + b[2]) * 0.5 + 0.55
        svg = '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s" stroke-linecap="round"/>' % (
            num(a[0], 1), num(a[1], 1), num(b[0], 1), num(b[1], 1), ln["stroke"], num(ln.get("width", 1.0), 2)
        )
        drawable.append((avg_z, svg))

    drawable.sort(key=lambda item: item[0])
    nodes = [svg for _, svg in drawable]

    if model_data.get("transit"):
        p_start = _cam_project(-66.0, -3.5, 0.0, 196.0, cy, yaw_deg, pitch_deg, fov)
        p_end = _cam_project(66.0, -3.5, 0.0, 196.0, cy, yaw_deg, pitch_deg, fov)
        deck_path = "M%s,%s L%s,%s" % (num(p_start[0], 1), num(p_start[1], 1), num(p_end[0], 1), num(p_end[1], 1))
        nodes.append(
            '<g><path d="%s" fill="%s"/><animateMotion path="%s" dur="5.5s" repeatCount="indefinite"/></g>'
            % (star_path(0, 0, 4.2, 1.6, 4), CADMIUM, deck_path)
        )
    return nodes


def _render_single_card(prefix, title, subtitle, domain_tag, accent, art_nodes, meta):
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
    parts.append('<clipPath id="%s-art-clip"><rect x="14" y="14" width="364" height="142" rx="11"/></clipPath>' % prefix)
    parts.append("</defs>")
    parts.extend(frame_nodes)

    parts.append('<rect x="14" y="14" width="364" height="142" rx="11" fill="%s" stroke="%s" stroke-width="1"/>' % (BG_WELL, BORDER_WARM))
    parts.append('<g clip-path="url(#%s-art-clip)">' % prefix)
    parts.append('<g transform="translate(14 14)">')
    parts.extend(
        van_gogh_starry_backdrop(
            prefix,
            364,
            142,
            opacity_scale=0.64,
            glyph_stride=1,
            stroke_limit=560,
            layer_key="sky",
        )
    )
    parts.append("</g>")
    parts.extend(art_nodes)
    parts.append("</g>")

    parts.append(text(22, 182, title, INK_PRIMARY, 18.0, "start", "700", ' letter-spacing="-0.2"', FONT_DISPLAY))
    if domain_tag:
        parts.append(text(CARD_W - 22, 181, domain_tag, accent, 10.2, "end", "600"))
    parts.append(text(22, 204, subtitle, INK_SECOND, 11.2, "start", "400", "", FONT_DISPLAY))

    parts.append('<line x1="22" y1="222" x2="%d" y2="222" stroke="%s" stroke-width="1"/>' % (CARD_W - 22, BORDER_SUBTLE))

    parts.append('<path d="%s" fill="%s"/>' % (star_path(27, 242, 4.4, 1.9, 4), lang_col))
    parts.append(text(38, 246, lang, INK_PRIMARY, 11, "start", "600"))
    parts.append('<path d="%s" fill="%s"/>' % (star_path(136, 241.8, 5.4, 2.2, 5), FIREFLY_GOLD))
    parts.append(text(147, 246, str(stars), CREAM, 11, "start", "700"))
    parts.append(text(CARD_W - 38, 246, "360°", INK_MUTED, 10, "end", "600"))
    parts.append(
        '<path d="M%d 246.5 L%d 237.5 M%d 237.5 H%d M%d 237.5 V243.5" fill="none" stroke="%s" stroke-width="1.35" stroke-linecap="round" stroke-linejoin="round"/>'
        % (CARD_W - 31, CARD_W - 22, CARD_W - 28, CARD_W - 22, CARD_W - 22, accent)
    )

    parts.append("</svg>")
    return "\n".join(parts)


def render_flagship_cards(repo_map):
    models = _load_blender_models()
    specs = [
        (
            "card-fforum-v3.svg",
            "ff3",
            "f_forumv3",
            "F-Forum v3",
            "7,750 UI/3D specimens, live studio & chat",
            "fforum3.vercel.app",
            EMERALD_MID,
            _render_blender_model(models.get("v3", {}), yaw_deg=29.0, pitch_deg=21.0, fov=252.0, cy=95.0),
        ),
        (
            "card-fforum-v2.svg",
            "ff2",
            "F-Forum_v2",
            "F-Forum v2",
            "Twin-pylon catenary suspension viaduct",
            "v2-bridge",
            SKY_SOFT,
            _render_blender_model(models.get("v2", {}), yaw_deg=25.0, pitch_deg=19.0, fov=236.0, cy=96.0),
        ),
        (
            "card-fforum-v1.svg",
            "ff1",
            "f-forum",
            "F-Forum v1",
            "Campus Q&A, math codex, clubs & live chat",
            "f-forum.vercel.app",
            FIREFLY_GOLD,
            _render_blender_model(models.get("v1", {}), yaw_deg=23.0, pitch_deg=22.0, fov=252.0, cy=104.0),
        ),
    ]
    out = {}
    for fname, prefix, key, title, subtitle, domain_tag, accent, art_nodes in specs:
        out[fname] = _render_single_card(prefix, title, subtitle, domain_tag, accent, art_nodes, repo_map.get(key, {}))
    return out
