# SPDX-License-Identifier: MIT
import argparse
import json
import math
import os
from PIL import Image, ImageFilter


def clamp(v, lo=0.0, hi=255.0):
    return lo if v < lo else (hi if v > hi else v)


def smoothstep(edge0, edge1, x):
    t = clamp((x - edge0) / max(1e-6, edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def rgb_hex(r, g, b):
    return "#%02x%02x%02x" % (int(round(clamp(r))), int(round(clamp(g))), int(round(clamp(b))))


def quantize_channel(v, step=6):
    return int(clamp(round(v / float(step)) * step))


def sample_bilinear(px, w, h, u, v):
    x = clamp(u * (w - 1), 0.0, w - 1.001)
    y = clamp(v * (h - 1), 0.0, h - 1.001)
    x0, y0 = int(x), int(y)
    tx, ty = x - x0, y - y0
    c00 = px[x0, y0]
    c10 = px[x0 + 1, y0]
    c01 = px[x0, y0 + 1]
    c11 = px[x0 + 1, y0 + 1]
    return (
        c00[0] * (1.0 - tx) * (1.0 - ty) + c10[0] * tx * (1.0 - ty) + c01[0] * (1.0 - tx) * ty + c11[0] * tx * ty,
        c00[1] * (1.0 - tx) * (1.0 - ty) + c10[1] * tx * (1.0 - ty) + c01[1] * (1.0 - tx) * ty + c11[1] * tx * ty,
        c00[2] * (1.0 - tx) * (1.0 - ty) + c10[2] * tx * (1.0 - ty) + c01[2] * (1.0 - tx) * ty + c11[2] * tx * ty,
    )


# WHY: Preserves authentic Van Gogh cobalt/ultramarine/cerulean sky pigments and cadmium starlight instead of crushing blues into grey.
def enhance_vangogh_pigment(r, g, b):
    lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
    warm = clamp((r - b * 0.72) / 130.0, 0.0, 1.0)
    cool = clamp((b - r * 0.80) / 115.0, 0.0, 1.0)
    curve = 0.76 + 0.44 * (lum ** 0.86)
    nr = r * curve * (0.90 + 0.32 * warm) + 4.0 * warm
    ng = g * curve * (0.96 + 0.18 * warm + 0.08 * cool) + 6.0 * cool
    nb = b * (0.94 + 0.28 * lum + 0.18 * cool) + 20.0 * (1.0 - warm) * (0.35 + 0.65 * cool)
    return clamp(nr), clamp(ng), clamp(nb)


BLOSSOM_ATLAS = (
    (0.455, 0.265, 0.225),
    (0.660, 0.730, 0.225),
    (0.275, 0.700, 0.215),
    (0.825, 0.415, 0.175),
)


def sample_single_blossom(sf_px, sf_w, sf_h, atlas_idx, dx_norm, dy_norm, rot_rad=0.0):
    dist = math.hypot(dx_norm, dy_norm)
    ang = math.atan2(dy_norm, dx_norm) - rot_rad
    petal_env = 0.90 + 0.12 * math.sin(ang * 14.0 + atlas_idx * 1.3) + 0.06 * math.cos(ang * 9.0)
    if dist > petal_env:
        return 0.0, 0.0, 0.0, 0.0

    cu, cv, sr_rad = BLOSSOM_ATLAS[atlas_idx % len(BLOSSOM_ATLAS)]
    rx = math.cos(ang) * dist
    ry = math.sin(ang) * dist
    fu = clamp(cu + rx * sr_rad, 0.02, 0.98)
    fv = clamp(cv + ry * sr_rad, 0.02, 0.98)

    r, g, b = sample_bilinear(sf_px, sf_w, sf_h, fu, fv)
    max_c = max(r, g, b)
    yellow_chroma = (max_c - b) / 255.0
    is_green = (g > r * 0.88) and (b < 125) and (max_c < 185)
    chroma_mask = 1.0 if dist < 0.42 else smoothstep(0.15, 0.33, yellow_chroma + (0.22 if is_green else 0.0))
    radial_fade = 1.0 - smoothstep(petal_env * 0.74, petal_env, dist)
    alpha = chroma_mask * radial_fade
    if alpha <= 0.015:
        return 0.0, 0.0, 0.0, 0.0

    is_seed = (dist < 0.46) and (r > 85) and (g < r * 0.66) and (b < 74)
    if is_seed:
        nr = clamp(r * 0.98 + 20.0)
        ng = clamp(g * 0.74 + 6.0)
        nb = clamp(b * 0.50 + 6.0)
    elif is_green and r < g * 1.06:
        nr = clamp(r * 0.48 + 10.0)
        ng = clamp(g * 0.86 + 26.0)
        nb = clamp(b * 0.64 + 18.0)
    else:
        nr = clamp(r * 1.06 + 10.0)
        ng = clamp(g * 0.97 + 6.0)
        nb = clamp(b * 0.52 + 4.0)
    return nr, ng, nb, alpha


def render_sunflower_bed(r, g, b, motif, nx, ny, aspect, sf_px, sf_w, sf_h, blossoms):
    for bx, by, brad, a_idx, tilt in blossoms:
        if ny >= by:
            t_stem = (ny - by) / max(0.05, 1.02 - by)
            stem_x = bx + math.sin(t_stem * 2.4 + tilt) * brad * 0.30
            dist_x = abs(nx - stem_x) * aspect
            stem_half = 0.0085 + 0.004 * t_stem
            if dist_x < stem_half:
                sa = 1.0 - smoothstep(stem_half * 0.45, stem_half, dist_x)
                rib = 0.5 + 0.5 * math.cos((nx - stem_x) / max(1e-4, stem_half) * 3.14)
                sr_st, sg_st, sb_st = 22.0 + 36.0 * rib, 74.0 + 68.0 * rib, 38.0 + 28.0 * rib
                r = r * (1.0 - sa) + sr_st * sa
                g = g * (1.0 - sa) + sg_st * sa
                b = b * (1.0 - sa) + sb_st * sa
                if sa > 0.4:
                    motif = 4
            for leaf_t, side in ((0.36, -1.0), (0.64, 1.0)):
                ldy = (t_stem - leaf_t) * (1.02 - by)
                ldx = (nx - stem_x) * side
                if 0.0 <= ldx <= brad * 0.85 and abs(ldy - ldx * 0.22 * side) < brad * 0.26:
                    lu = ldx / (brad * 0.85)
                    lw = math.sin(lu * math.pi) * brad * 0.22
                    dist_leaf = abs(ldy + lu * 0.015)
                    if dist_leaf < lw:
                        la = (1.0 - smoothstep(lw * 0.5, lw, dist_leaf)) * 0.90
                        vein = 1.0 - min(1.0, dist_leaf / max(1e-4, lw))
                        lr_c, lg_c, lb_c = 24.0 + 40.0 * vein, 80.0 + 64.0 * vein, 42.0 + 28.0 * vein
                        r = r * (1.0 - la) + lr_c * la
                        g = g * (1.0 - la) + lg_c * la
                        b = b * (1.0 - la) + lb_c * la
                        if la > 0.4:
                            motif = 4

    for bx, by, brad, a_idx, rot in blossoms:
        dx_n = ((nx - bx) * aspect) / brad
        dy_n = (ny - by) / brad
        if abs(dx_n) <= 1.06 and abs(dy_n) <= 1.06:
            sr_f, sg_f, sb_f, fa = sample_single_blossom(sf_px, sf_w, sf_h, a_idx, dx_n, dy_n, rot)
            if fa > 0.02:
                r = r * (1.0 - fa) + sr_f * fa
                g = g * (1.0 - fa) + sg_f * fa
                b = b * (1.0 - fa) + sb_f * fa
                if fa > 0.30:
                    motif = 4

    return r, g, b, motif


def sample_provence_cypress_matte(pr_px, pr_w, pr_h, u, v):
    if not (0.0 <= u <= 1.0 and 0.0 <= v <= 1.0):
        return 0.0, 0.0, 0.0, 0.0
    pu = 0.28 + u * 0.44
    pv = 0.02 + v * 0.80
    r, g, b = sample_bilinear(pr_px, pr_w, pr_h, pu, pv)
    lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
    darkness = 1.0 - smoothstep(0.22, 0.37, lum)
    not_sky = 1.0 - smoothstep(70.0, 118.0, b - g * 0.35)
    taper = (0.07 + 0.29 * (v ** 0.78)) * (0.85 + 0.15 * math.sin(v * 20.0))
    center_env = math.exp(-(((u - 0.50) / max(0.05, taper)) ** 2))
    top_fade = smoothstep(0.0, 0.07, v)
    bot_fade = smoothstep(0.0, 0.07, 1.0 - v)
    alpha = clamp(darkness * (0.45 + 0.55 * not_sky) * smoothstep(0.10, 0.42, center_env) * top_fade * bot_fade, 0.0, 1.0)
    if alpha <= 0.02:
        return 0.0, 0.0, 0.0, 0.0
    flame = 0.5 + 0.5 * math.sin(u * 42.0 + v * 34.0 * math.cos(u * 8.5))
    bronze = max(0.0, flame - 0.58) * 2.3
    rim_light = smoothstep(0.34, 0.80, abs(u - 0.50) / max(0.08, taper)) * 0.62
    nr = clamp(r * 0.92 + 10.0 + flame * 20.0 + bronze * 68.0 + rim_light * 22.0)
    ng = clamp(g * 1.38 + 26.0 + flame * 52.0 + bronze * 40.0 + rim_light * 44.0)
    nb = clamp(b * 1.14 + 20.0 + flame * 36.0 + bronze * 14.0 + rim_light * 48.0)
    return nr, ng, nb, alpha


# WHY: Samples Starry Night with aspect-corrected coordinates so stars, central vortex, and top-right Crescent Moon remain round instead of 2.8x horizontally squashed.
def sample_aspect_starry_sky(st_px, st_w, st_h, nx, ny, aspect, include_moon=True, include_village=True):
    v_max = 0.95 if include_village else 0.72
    sv = clamp(0.03 + ny * (v_max - 0.03), 0.025, v_max)

    u_left = clamp(0.02 + (nx / 0.74) * 0.80, 0.02, 0.82)
    r1, g1, b1 = enhance_vangogh_pigment(*sample_bilinear(st_px, st_w, st_h, u_left, sv))

    u_right = clamp(0.76 - ((nx - 0.58) / 0.42) * 0.42, 0.32, 0.76)
    v_right = clamp(0.05 + ny * (0.86 if include_village else 0.66), 0.04, 0.88)
    r2, g2, b2 = enhance_vangogh_pigment(*sample_bilinear(st_px, st_w, st_h, u_right, v_right))

    blend_r = smoothstep(0.56, 0.76, nx)
    r = r1 * (1.0 - blend_r) + r2 * blend_r
    g = g1 * (1.0 - blend_r) + g2 * blend_r
    b = b1 * (1.0 - blend_r) + b2 * blend_r

    if include_moon:
        mcx, mcy, mrad_y = 0.895, 0.255, 0.225
        dx_m = ((nx - mcx) * aspect) / (mrad_y * (st_w / float(st_h)))
        dy_m = (ny - mcy) / mrad_y
        mdist = math.hypot(dx_m * 1.15, dy_m)
        if mdist < 1.18:
            mu = clamp(0.876 + dx_m * 0.135, 0.735, 0.992)
            mv = clamp(0.155 + dy_m * 0.145, 0.015, 0.335)
            mr, mg, mb = enhance_vangogh_pigment(*sample_bilinear(st_px, st_w, st_h, mu, mv))
            ma = 1.0 - smoothstep(0.72, 1.15, mdist)
            r = r * (1.0 - ma) + mr * ma
            g = g * (1.0 - ma) + mg * ma
            b = b * (1.0 - ma) + mb * ma

    return r, g, b


def pick_vangogh_glyph(lum, mag, theta_deg, motif, r, g, b):
    ang = theta_deg % 180.0
    if motif == 4:
        is_seed = (r > 85) and (g < r * 0.66) and (b < 68)
        if is_seed:
            seed_ramp = "#%&8@$"
            idx = int(round(clamp(lum * 1.8, 0.0, 1.0) * (len(seed_ramp) - 1)))
            return seed_ramp[max(0, min(len(seed_ramp) - 1, idx))]
        if g > r * 0.92 and r < 150:
            return "/" if ang < 70 else ("\\" if ang > 110 else "|")
        if 24.0 <= ang < 66.0:
            return "/" if lum < 0.68 else "*"
        if 114.0 < ang <= 156.0:
            return "\\" if lum < 0.68 else "*"
        if 66.0 <= ang <= 114.0:
            return "(" if lum < 0.72 else "V"
        return "~" if lum < 0.66 else "@"

    if motif == 3:
        if lum > 0.34:
            if 28.0 <= ang < 72.0:
                return "/"
            if 108.0 < ang <= 152.0:
                return "\\"
            return "S" if lum > 0.44 else ")"
        cyp_ramp = ":;|/\\()S~#MW"
        idx = int(round(clamp(lum * 2.5, 0.0, 1.0) * (len(cyp_ramp) - 1)))
        return cyp_ramp[max(2, min(len(cyp_ramp) - 1, idx))]

    if motif == 2:
        is_wheat = (r > 135) and (r > b * 1.30)
        if is_wheat:
            if 35.0 <= ang <= 85.0:
                return "/"
            if 95.0 <= ang <= 145.0:
                return "\\"
            return "|" if mag > 0.25 else "~"
        if mag > 0.26:
            if 24.0 <= ang < 66.0:
                return "/"
            if 114.0 < ang <= 156.0:
                return "\\"
            if 68.0 <= ang <= 112.0:
                return "|"
            return "=" if lum > 0.45 else "~"
        land_ramp = ".:;~+=*vcnxz#MW@"
        idx = int(round(clamp(lum * 1.35, 0.0, 1.0) * (len(land_ramp) - 1)))
        return land_ramp[max(1, min(len(land_ramp) - 1, idx))]

    if lum > 0.80:
        return "@" if lum > 0.90 else ("*" if mag < 0.36 else "%")
    if lum > 0.60:
        if 24.0 <= ang < 66.0:
            return "/"
        if 114.0 < ang <= 156.0:
            return "\\"
        if 66.0 <= ang <= 114.0:
            return "(" if r > b else ")"
        return "*" if lum > 0.72 else "~"
    if mag > 0.16:
        if 24.0 <= ang < 66.0:
            return "/"
        if 114.0 < ang <= 156.0:
            return "\\"
        if 66.0 <= ang <= 114.0:
            return "(" if ang < 90.0 else ")"
        return "~" if lum > 0.32 else "="
    sky_ramp = ":;~+=*o#@"
    idx = int(round(clamp(lum * 1.34, 0.0, 1.0) * (len(sky_ramp) - 1)))
    return sky_ramp[max(0, min(len(sky_ramp) - 1, idx))]


def build_composite_canvas(starry_im, sf_im, pr_im, mode="panorama", w=864, h=264):
    st_px = starry_im.load()
    st_w, st_h = starry_im.size
    sf_px = sf_im.load()
    sf_w, sf_h = sf_im.size
    pr_px = pr_im.load()
    pr_w, pr_h = pr_im.size
    aspect = float(w) / float(h)

    out_im = Image.new("RGB", (w, h))
    bg_im = Image.new("RGB", (w, h))
    out_px = out_im.load()
    bg_px = bg_im.load()
    motif_map = [[0] * w for _ in range(h)]

    pan_blossoms = (
        (0.036, 0.81, 0.16, 0, -0.18),
        (0.088, 0.88, 0.14, 1, 0.22),
        (0.964, 0.82, 0.15, 1, 0.20),
        (0.914, 0.89, 0.13, 2, -0.24),
    )

    garden_blossoms = (
        (0.044, 0.57, 0.20, 0, -0.15),
        (0.114, 0.67, 0.21, 1, 0.18),
        (0.058, 0.83, 0.19, 2, -0.25),
        (0.176, 0.79, 0.18, 3, 0.28),
        (0.242, 0.88, 0.15, 0, 0.12),
        (0.956, 0.57, 0.20, 1, 0.16),
        (0.886, 0.67, 0.21, 0, -0.20),
        (0.942, 0.83, 0.19, 2, 0.24),
        (0.824, 0.79, 0.18, 3, -0.26),
        (0.758, 0.88, 0.15, 1, -0.14),
    )

    for y in range(h):
        ny = (y + 0.5) / float(h)
        for x in range(w):
            nx = (x + 0.5) / float(w)

            if mode == "sky":
                r, g, b = sample_aspect_starry_sky(st_px, st_w, st_h, nx, ny, aspect, include_moon=False, include_village=False)
                seam_x = smoothstep(0.0, 0.10, nx) * smoothstep(0.0, 0.10, 1.0 - nx)
                if seam_x < 0.999:
                    wr, wg, wb = sample_aspect_starry_sky(st_px, st_w, st_h, (nx + 0.5) % 1.0, ny, aspect, include_moon=False, include_village=False)
                    r = r * seam_x + wr * (1.0 - seam_x)
                    g = g * seam_x + wg * (1.0 - seam_x)
                    b = b * seam_x + wb * (1.0 - seam_x)
                slum = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
                motif = 1 if slum > 0.50 else 0
                bg_r, bg_g, bg_b = r, g, b

            elif mode == "panorama":
                r, g, b = sample_aspect_starry_sky(st_px, st_w, st_h, nx, ny, aspect, include_moon=True, include_village=True)
                bg_r, bg_g, bg_b = r, g, b

                slum = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
                in_left_cyp = (0.06 <= nx <= 0.22) and (ny >= 0.05) and (slum < 0.27) and (r < 98) and (b < 105)
                if in_left_cyp:
                    bg_r, bg_g, bg_b = sample_aspect_starry_sky(st_px, st_w, st_h, clamp(nx + 0.16, 0.24, 0.45), ny, aspect, include_moon=False, include_village=True)
                    flame = 0.5 + 0.5 * math.sin(nx * 110.0 + ny * 40.0)
                    r = clamp(r * 0.95 + 10.0 + flame * 24.0)
                    g = clamp(g * 1.18 + 20.0 + flame * 38.0)
                    b = clamp(b * 0.96 + 14.0 + flame * 22.0)
                    motif = 3
                elif ny > 0.74 and nx > 0.24:
                    motif = 2
                elif slum > 0.50 or (0.24 <= nx <= 0.72 and 0.18 <= ny <= 0.68):
                    motif = 1
                else:
                    motif = 0

                if 0.795 <= nx <= 0.865 and ny >= 0.44:
                    cu = (nx - 0.795) / 0.070
                    cv = (ny - 0.44) / 0.56
                    cr, cg, cb, calpha = sample_provence_cypress_matte(pr_px, pr_w, pr_h, cu, cv)
                    if calpha > 0.05:
                        r = r * (1.0 - calpha) + cr * calpha
                        g = g * (1.0 - calpha) + cg * calpha
                        b = b * (1.0 - calpha) + cb * calpha
                        if calpha > 0.36:
                            motif = 3

                if nx < 0.18 or nx > 0.82:
                    r, g, b, motif = render_sunflower_bed(r, g, b, motif, nx, ny, aspect, sf_px, sf_w, sf_h, pan_blossoms)

            else:
                st_r, st_g, st_b = sample_aspect_starry_sky(st_px, st_w, st_h, nx, ny, aspect, include_moon=False, include_village=False)

                pu = clamp(0.03 + ((nx - 0.31) / 0.38) * 0.94, 0.02, 0.98)
                pv = clamp(0.02 + ny * 0.96, 0.02, 0.98)
                pr_raw_r, pr_raw_g, pr_raw_b = sample_bilinear(pr_px, pr_w, pr_h, pu, pv)
                pr_r, pr_g, pr_b = enhance_vangogh_pigment(pr_raw_r, pr_raw_g, pr_raw_b)

                if nx < 0.33 and ny > 0.50:
                    wu = clamp(0.04 + (nx / 0.33) * 0.34, 0.03, 0.38)
                    wv = clamp(0.52 + ((ny - 0.50) / 0.50) * 0.45, 0.52, 0.97)
                    wr, wg, wb = enhance_vangogh_pigment(*sample_bilinear(pr_px, pr_w, pr_h, wu, wv))
                    w_blend = smoothstep(0.50, 0.62, ny)
                    st_r = st_r * (1.0 - w_blend) + wr * w_blend
                    st_g = st_g * (1.0 - w_blend) + wg * w_blend
                    st_b = st_b * (1.0 - w_blend) + wb * w_blend
                elif nx > 0.67 and ny > 0.52:
                    ru = clamp(0.66 + ((nx - 0.67) / 0.33) * 0.30, 0.66, 0.97)
                    rv = clamp(0.54 + ((ny - 0.52) / 0.48) * 0.43, 0.54, 0.97)
                    rr, rg, rb = enhance_vangogh_pigment(*sample_bilinear(pr_px, pr_w, pr_h, ru, rv))
                    r_blend = smoothstep(0.52, 0.64, ny)
                    st_r = st_r * (1.0 - r_blend) + rr * r_blend
                    st_g = st_g * (1.0 - r_blend) + rg * r_blend
                    st_b = st_b * (1.0 - r_blend) + rb * r_blend

                prov_mask = smoothstep(0.27, 0.35, nx) * smoothstep(0.27, 0.35, 1.0 - nx)
                r = st_r * (1.0 - prov_mask) + pr_r * prov_mask
                g = st_g * (1.0 - prov_mask) + pr_g * prov_mask
                b = st_b * (1.0 - prov_mask) + pr_b * prov_mask
                bg_r, bg_g, bg_b = r, g, b

                lum_now = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
                in_center_cyp = (0.44 <= nx <= 0.55) and (ny <= 0.78) and (lum_now < 0.28)
                if in_center_cyp:
                    bg_r, bg_g, bg_b = st_r, st_g, st_b
                    motif = 3
                elif ny > 0.52:
                    motif = 2
                else:
                    motif = 1 if lum_now > 0.48 else 0

                for cx0, cx1, cy0, cy1, cflip in (
                    (0.205, 0.285, 0.08, 0.86, True),
                    (0.725, 0.805, 0.10, 0.86, False),
                ):
                    if cx0 <= nx <= cx1 and cy0 <= ny <= cy1:
                        cu = (nx - cx0) / (cx1 - cx0)
                        if cflip:
                            cu = 1.0 - cu
                        cv = (ny - cy0) / (cy1 - cy0)
                        cr, cg, cb, calpha = sample_provence_cypress_matte(pr_px, pr_w, pr_h, cu, cv)
                        if calpha > 0.05:
                            r = r * (1.0 - calpha) + cr * calpha
                            g = g * (1.0 - calpha) + cg * calpha
                            b = b * (1.0 - calpha) + cb * calpha
                            if calpha > 0.36:
                                motif = 3

                if nx < 0.34 or nx > 0.66:
                    r, g, b, motif = render_sunflower_bed(r, g, b, motif, nx, ny, aspect, sf_px, sf_w, sf_h, garden_blossoms)

            out_px[x, y] = (int(round(clamp(r))), int(round(clamp(g))), int(round(clamp(b))))
            bg_px[x, y] = (int(round(clamp(bg_r))), int(round(clamp(bg_g))), int(round(clamp(bg_b))))
            motif_map[y][x] = motif

    out_im = out_im.filter(ImageFilter.UnsharpMask(radius=1.3, percent=140, threshold=2))
    return out_im, bg_im, motif_map


def extract_calligraphic_layer(comp_im, bg_im, motif_map, cols=204, rows=60, max_strokes=3400):
    w, h = comp_im.size
    col_im = comp_im.resize((cols, rows), Image.Resampling.LANCZOS)
    bg_small = bg_im.resize((cols, rows), Image.Resampling.LANCZOS)
    gray_im = col_im.convert("L")
    cpx = col_im.load()
    bpx = bg_small.load()
    gpx = gray_im.load()

    ix_map = [[0.0] * cols for _ in range(rows)]
    iy_map = [[0.0] * cols for _ in range(rows)]
    for y in range(1, rows - 1):
        for x in range(1, cols - 1):
            tl = gpx[x - 1, y - 1] / 255.0
            tc = gpx[x, y - 1] / 255.0
            tr = gpx[x + 1, y - 1] / 255.0
            ml = gpx[x - 1, y] / 255.0
            mr = gpx[x + 1, y] / 255.0
            bl = gpx[x - 1, y + 1] / 255.0
            bc = gpx[x, y + 1] / 255.0
            br = gpx[x + 1, y + 1] / 255.0
            ix_map[y][x] = (tr + 2.0 * mr + br) - (tl + 2.0 * ml + bl)
            iy_map[y][x] = (bl + 2.0 * bc + br) - (tl + 2.0 * tc + tr)

    theta_map = [[0.0] * cols for _ in range(rows)]
    mag_map = [[0.0] * cols for _ in range(rows)]
    max_mag = 1e-6
    for y in range(1, rows - 1):
        for x in range(1, cols - 1):
            jxx = 0.0
            jxy = 0.0
            jyy = 0.0
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    wt = 4.0 if (dx == 0 and dy == 0) else (2.0 if (dx == 0 or dy == 0) else 1.0)
                    gx = ix_map[y + dy][x + dx]
                    gy = iy_map[y + dy][x + dx]
                    jxx += wt * gx * gx
                    jxy += wt * gx * gy
                    jyy += wt * gy * gy
            grad_ang = 0.5 * math.atan2(2.0 * jxy, jxx - jyy)
            tang_deg = (math.degrees(grad_ang) + 90.0) % 180.0
            theta_map[y][x] = tang_deg
            m = math.hypot(ix_map[y][x], iy_map[y][x])
            mag_map[y][x] = m
            if m > max_mag:
                max_mag = m

    cells_rows = []
    motifs_rows = []
    bg_rows = []

    for y in range(rows):
        my_src = min(h - 1, int((y + 0.5) / float(rows) * h))
        runs = []
        bg_runs = []
        m_chars = []
        cur_col = "__INIT__"
        cur_chars = []
        bg_cur_col = "__INIT__"
        bg_cur_len = 0

        for x in range(cols):
            mx_src = min(w - 1, int((x + 0.5) / float(cols) * w))
            motif = motif_map[my_src][mx_src]
            m_chars.append(str(motif))
            r, g, b = cpx[x, y]
            br, bg_g, bb = bpx[x, y]
            lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
            norm_mag = min(1.0, mag_map[y][x] / (max_mag * 0.52))
            theta_d = theta_map[y][x]
            ch = pick_vangogh_glyph(lum, norm_mag, theta_d, motif, r, g, b)
            lift = 1.06 + norm_mag * 0.22
            qr = quantize_channel(r * lift, 6)
            qg = quantize_channel(g * lift, 6)
            qb = quantize_channel(b * lift, 6)
            if max(qr, qg, qb) < 32:
                qr, qg, qb = qr + 12, qg + 22, qb + 42
            hex_c = rgb_hex(qr, qg, qb)
            if hex_c == cur_col:
                cur_chars.append(ch)
            else:
                if cur_col != "__INIT__":
                    runs.append([cur_col, "".join(cur_chars)])
                cur_col = hex_c
                cur_chars = [ch]

            b_hex = rgb_hex(quantize_channel(br * 0.82, 12), quantize_channel(bg_g * 0.82, 12), quantize_channel(bb * 0.86, 12))
            if b_hex == bg_cur_col:
                bg_cur_len += 1
            else:
                if bg_cur_col != "__INIT__":
                    bg_runs.append([bg_cur_col, bg_cur_len])
                bg_cur_col = b_hex
                bg_cur_len = 1

        if cur_chars:
            runs.append([cur_col, "".join(cur_chars)])
        if bg_cur_len > 0:
            bg_runs.append([bg_cur_col, bg_cur_len])
        cells_rows.append(runs)
        motifs_rows.append("".join(m_chars))
        bg_rows.append(bg_runs)

    strokes = []
    seed = 188905
    for y in range(1, rows - 1):
        for x in range(1, cols - 1, 2):
            seed = (1664525 * seed + 1013904223) & 0xFFFFFFFF
            jx = (((seed >> 8) & 0xFF) / 255.0 - 0.5) * 0.72
            seed = (1664525 * seed + 1013904223) & 0xFFFFFFFF
            jy = (((seed >> 8) & 0xFF) / 255.0 - 0.5) * 0.72
            nx = clamp((x + 0.5 + jx) / float(cols), 0.004, 0.996)
            ny = clamp((y + 0.5 + jy) / float(rows), 0.004, 0.996)
            mx_src = min(w - 1, int(nx * w))
            my_src = min(h - 1, int(ny * h))
            motif = motif_map[my_src][mx_src]
            r, g, b = cpx[x, y]
            lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
            norm_mag = min(1.0, mag_map[y][x] / (max_mag * 0.50))

            ang0 = math.radians(theta_map[y][x])
            tx0, ty0 = math.cos(ang0), math.sin(ang0)
            span_x = (1.55 + norm_mag * 1.15) / float(cols)
            span_y = (1.40 + norm_mag * 1.05) / float(rows)

            x_mid = clamp(nx + tx0 * span_x * 0.55, 0.002, 0.998)
            y_mid = clamp(ny + ty0 * span_y * 0.55, 0.002, 0.998)
            xm_i = min(cols - 2, max(1, int(x_mid * cols)))
            ym_i = min(rows - 2, max(1, int(y_mid * rows)))
            ang1 = math.radians(theta_map[ym_i][xm_i])
            tx1, ty1 = math.cos(ang1), math.sin(ang1)
            if tx0 * tx1 + ty0 * ty1 < 0:
                tx1, ty1 = -tx1, -ty1

            x0_s = clamp(nx - tx0 * span_x * 0.65, 0.001, 0.999)
            y0_s = clamp(ny - ty0 * span_y * 0.65, 0.001, 0.999)
            x1_s = clamp(x_mid + tx1 * span_x * 0.65, 0.001, 0.999)
            y1_s = clamp(y_mid + ty1 * span_y * 0.65, 0.001, 0.999)

            even_bonus = 0.45 if ((x // 2 + y) % 2 == 0) else 0.0
            prio = even_bonus + norm_mag * 0.45 + lum * 0.35 + (0.28 if motif in (1, 3, 4) else 0.0)
            scol = rgb_hex(quantize_channel(r * 0.88, 6), quantize_channel(g * 0.88, 6), quantize_channel(b * 0.90, 6))
            sw = round(1.30 + norm_mag * 1.10, 2)
            strokes.append((
                prio,
                [
                    round(x0_s, 4),
                    round(y0_s, 4),
                    round(x_mid, 4),
                    round(y_mid, 4),
                    round(x1_s, 4),
                    round(y1_s, 4),
                    scol,
                    sw,
                    motif,
                ],
            ))

    strokes.sort(key=lambda item: item[0], reverse=True)
    picked_strokes = [item[1] for item in strokes[:max_strokes]]

    return {
        "cols": cols,
        "rows": rows,
        "grid": cells_rows,
        "bg": bg_rows,
        "motifs": motifs_rows,
        "strokes": picked_strokes,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--starry", required=True)
    ap.add_argument("--sunflowers", required=True)
    ap.add_argument("--provence", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    starry_im = Image.open(args.starry).convert("RGB")
    sf_im = Image.open(args.sunflowers).convert("RGB")
    pr_im = Image.open(args.provence).convert("RGB")

    pan_im, pan_bg, pan_motifs = build_composite_canvas(starry_im, sf_im, pr_im, mode="panorama", w=864, h=264)
    gar_im, gar_bg, gar_motifs = build_composite_canvas(starry_im, sf_im, pr_im, mode="garden", w=864, h=288)
    sky_im, sky_bg, sky_motifs = build_composite_canvas(starry_im, sf_im, pr_im, mode="sky", w=640, h=260)

    panorama = extract_calligraphic_layer(pan_im, pan_bg, pan_motifs, cols=204, rows=60, max_strokes=3100)
    garden = extract_calligraphic_layer(gar_im, gar_bg, gar_motifs, cols=204, rows=66, max_strokes=3300)
    sky = extract_calligraphic_layer(sky_im, sky_bg, sky_motifs, cols=160, rows=56, max_strokes=2000)

    payload = {
        "panorama": panorama,
        "garden": garden,
        "sky": sky,
    }
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, separators=(",", ":"))
    print(
        "built vangogh_scene.json: pan=%dx%d, gar=%dx%d, sky=%dx%d, total=%d bytes"
        % (
            panorama["cols"], panorama["rows"],
            garden["cols"], garden["rows"],
            sky["cols"], sky["rows"],
            os.path.getsize(args.out),
        )
    )


if __name__ == "__main__":
    main()
