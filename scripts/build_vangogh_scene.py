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


# WHY: Soft-knee highlight roll-off preserves luminous ivory/cadmium detail inside stars and moon without flat white clipping.
def soft_channel(v, knee=224.0, ceiling=252.0):
    if v <= 0.0:
        return 0.0
    if v <= knee:
        return v
    span = max(1.0, ceiling - knee)
    return knee + span * (1.0 - math.exp(-(v - knee) / (span * 1.35)))


def rgb_hex(r, g, b):
    return "#%02x%02x%02x" % (
        int(round(clamp(soft_channel(r)))),
        int(round(clamp(soft_channel(g)))),
        int(round(clamp(soft_channel(b)))),
    )


def quantize_channel(v, step=4):
    return int(clamp(round(soft_channel(v) / float(step)) * step))


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


# WHY: Lifts crushed nocturnal midtones while separating warm cadmium-amber starlight from cobalt-cerulean sky currents.
def enhance_vangogh_pigment(r, g, b):
    lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
    warm = clamp((r - b * 0.78) / 108.0, 0.0, 1.0)
    cool = clamp((b - r * 0.82) / 104.0, 0.0, 1.0)
    halo = smoothstep(0.44, 0.86, lum) * smoothstep(-14.0, 28.0, (r + g) * 0.5 - b * 0.92)
    warm_eff = clamp(max(warm, halo * 0.78), 0.0, 1.0)

    mid_lift = 0.86 + 0.44 * (lum ** 0.74)
    cerulean_mid = math.sin(clamp(lum, 0.0, 1.0) * math.pi) * cool

    nr = r * mid_lift * (0.92 + 0.34 * warm_eff) + 12.0 * warm_eff + 5.0 * lum
    ng = g * mid_lift * (1.00 + 0.22 * warm_eff + 0.14 * cool) + 10.0 * warm_eff + 14.0 * cerulean_mid + 6.0 * cool
    nb = (
        b * (1.02 + 0.30 * (lum ** 0.80) + 0.18 * cool - 0.10 * warm_eff)
        + 24.0 * (1.0 - warm_eff) * (0.38 + 0.62 * cool)
        + 12.0 * cerulean_mid
    )
    return soft_channel(nr), soft_channel(ng), soft_channel(nb)


BLOSSOM_ATLAS = (
    (0.455, 0.265, 0.225),
    (0.660, 0.730, 0.225),
    (0.275, 0.700, 0.215),
    (0.825, 0.415, 0.175),
)


def sample_single_blossom(sf_px, sf_w, sf_h, atlas_idx, dx_norm, dy_norm, rot_rad=0.0):
    dist = math.hypot(dx_norm, dy_norm)
    ang = math.atan2(dy_norm, dx_norm) - rot_rad
    petal_wave = 0.5 + 0.5 * math.sin(ang * 18.0 + atlas_idx * 1.7 + math.sin(ang * 5.0) * 0.35)
    petal_env = 0.88 + 0.13 * math.sin(ang * 16.0 + atlas_idx * 1.3) + 0.06 * math.cos(ang * 9.0)
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
    chroma_mask = 1.0 if dist < 0.44 else smoothstep(0.14, 0.31, yellow_chroma + (0.22 if is_green else 0.0))
    radial_fade = 1.0 - smoothstep(petal_env * 0.75, petal_env, dist)
    alpha = chroma_mask * radial_fade
    if alpha <= 0.015:
        return 0.0, 0.0, 0.0, 0.0

    is_seed = (dist < 0.41) and ((g < r * 0.68 and b < 84) or dist < (0.31 if atlas_idx in (0, 1) else 0.22))
    if is_seed:
        stipple = 0.5 + 0.5 * math.sin(dx_norm * 48.0 + dy_norm * 44.0) * math.cos(dx_norm * 40.0 - dy_norm * 46.0)
        pollen_ring = smoothstep(0.25, 0.39, dist)
        core_depth = 1.0 - smoothstep(0.0, 0.22, dist)
        nr = (118.0 + r * 0.32) * (1.0 - 0.42 * core_depth) + stipple * 24.0 + pollen_ring * 82.0
        ng = (48.0 + g * 0.22) * (1.0 - 0.48 * core_depth) + stipple * 12.0 + pollen_ring * 54.0
        nb = (18.0 + b * 0.16) * (1.0 - 0.45 * core_depth) + pollen_ring * 10.0
    elif is_green and r < g * 1.06:
        nr = r * 0.48 + 14.0
        ng = g * 0.96 + 36.0
        nb = b * 0.64 + 20.0
    else:
        sun_lit = clamp(0.5 - (dx_norm * 0.32 + dy_norm * 0.38), 0.0, 1.0)
        tip_glow = smoothstep(0.44, 0.86, dist)
        edge_ochre = smoothstep(0.72, 0.96, dist / max(0.2, petal_env))
        ridge = 0.30 + 0.70 * petal_wave
        nr = r * 1.08 + 20.0 + ridge * 20.0 + sun_lit * 14.0 - edge_ochre * 10.0
        ng = g * 0.96 + 8.0 + ridge * 26.0 + sun_lit * 14.0 - (1.0 - ridge) * 20.0 - edge_ochre * 24.0
        nb = b * 0.34 + 4.0 + tip_glow * 10.0 * ridge
    return soft_channel(nr), soft_channel(ng), soft_channel(nb), alpha


def render_sunflower_bed(r, g, b, motif, nx, ny, aspect, sf_px, sf_w, sf_h, blossoms):
    for bx, by, brad, a_idx, tilt in blossoms:
        if ny >= by:
            t_stem = (ny - by) / max(0.05, 1.02 - by)
            stem_x = bx + math.sin(t_stem * 2.4 + tilt) * brad * 0.30
            dist_x = abs(nx - stem_x) * aspect
            stem_half = 0.0082 + 0.0038 * t_stem
            if dist_x < stem_half:
                sa = 1.0 - smoothstep(stem_half * 0.45, stem_half, dist_x)
                rib = 0.5 + 0.5 * math.cos((nx - stem_x) / max(1e-4, stem_half) * 3.14)
                sr_st = 24.0 + 48.0 * rib
                sg_st = 84.0 + 82.0 * rib
                sb_st = 42.0 + 36.0 * rib
                r = r * (1.0 - sa) + sr_st * sa
                g = g * (1.0 - sa) + sg_st * sa
                b = b * (1.0 - sa) + sb_st * sa
                if sa > 0.4:
                    motif = 4
            for leaf_t, side in ((0.36, -1.0), (0.64, 1.0)):
                ldy = (t_stem - leaf_t) * (1.02 - by)
                ldx = (nx - stem_x) * side
                if 0.0 <= ldx <= brad * 0.86 and abs(ldy - ldx * 0.22 * side) < brad * 0.26:
                    lu = ldx / (brad * 0.86)
                    lw = math.sin(lu * math.pi) * brad * 0.22
                    dist_leaf = abs(ldy + lu * 0.015)
                    if dist_leaf < lw:
                        la = (1.0 - smoothstep(lw * 0.5, lw, dist_leaf)) * 0.92
                        vein = 1.0 - min(1.0, dist_leaf / max(1e-4, lw))
                        upper_lit = 1.0 if (ldy + lu * 0.015) < 0.0 else 0.62
                        lr_c = 22.0 + 52.0 * vein * upper_lit
                        lg_c = 86.0 + 84.0 * vein * upper_lit
                        lb_c = 46.0 + 38.0 * vein
                        r = r * (1.0 - la) + lr_c * la
                        g = g * (1.0 - la) + lg_c * la
                        b = b * (1.0 - la) + lb_c * la
                        if la > 0.4:
                            motif = 4

    for bx, by, brad, a_idx, rot in blossoms:
        dx_n = ((nx - bx) * aspect) / brad
        dy_n = (ny - by) / brad
        dist_b = math.hypot(dx_n, dy_n)
        if dist_b <= 1.12:
            foliage_halo = (1.0 - smoothstep(0.76, 1.10, dist_b)) * 0.46
            r = r * (1.0 - foliage_halo) + 18.0 * foliage_halo
            g = g * (1.0 - foliage_halo) + 64.0 * foliage_halo
            b = b * (1.0 - foliage_halo) + 42.0 * foliage_halo
        if abs(dx_n) <= 1.06 and abs(dy_n) <= 1.06:
            sr_f, sg_f, sb_f, fa = sample_single_blossom(sf_px, sf_w, sf_h, a_idx, dx_n, dy_n, rot)
            if fa > 0.02:
                r = r * (1.0 - fa) + sr_f * fa
                g = g * (1.0 - fa) + sg_f * fa
                b = b * (1.0 - fa) + sb_f * fa
                if fa > 0.30:
                    motif = 4

    return r, g, b, motif


# WHY: Sculpts 3-tier indigo core, viridian-emerald mid-flames, and moonlit teal/warm-bronze rims on all Provence cypresses.
def sculpt_cypress_impasto(r, g, b, u_rel, v_rel, moon_side=1.0):
    flame_a = 0.5 + 0.5 * math.sin(u_rel * 44.0 + v_rel * 32.0 * math.cos(u_rel * 7.5))
    flame_b = 0.5 + 0.5 * math.cos(u_rel * 78.0 - v_rel * 48.0)
    flame = 0.64 * flame_a + 0.36 * flame_b
    bronze = max(0.0, flame - 0.64) * 2.35
    edge_dist = abs(u_rel - 0.50) * 2.0
    side_bias = 0.60 + 0.40 * clamp((u_rel - 0.50) * 2.2 * moon_side, -1.0, 1.0)
    rim_light = smoothstep(0.46, 0.96, edge_dist) * (0.42 + 0.42 * side_bias) * smoothstep(0.96, 0.10, v_rel)
    indigo_core = (1.0 - smoothstep(0.0, 0.62, edge_dist)) * (1.0 - flame * 0.45)

    base_r = min(r, 64.0)
    base_g = min(g, 76.0)
    base_b = min(b, 84.0)
    nr = base_r * 0.55 + 8.0 + flame * 20.0 + bronze * 64.0 + rim_light * 22.0 - indigo_core * 4.0
    ng = base_g * 0.92 + 20.0 + flame * 58.0 + bronze * 38.0 + rim_light * 52.0 - indigo_core * 8.0
    nb = base_b * 0.86 + 26.0 + flame * 36.0 + bronze * 12.0 + rim_light * 58.0 + indigo_core * 22.0
    return soft_channel(nr), soft_channel(ng), soft_channel(nb)


def sample_provence_cypress_matte(pr_px, pr_w, pr_h, u, v, moon_side=1.0):
    if not (0.0 <= u <= 1.0 and 0.0 <= v <= 1.0):
        return 0.0, 0.0, 0.0, 0.0
    pu = 0.28 + u * 0.44
    pv = 0.02 + v * 0.80
    r, g, b = sample_bilinear(pr_px, pr_w, pr_h, pu, pv)
    lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
    darkness = 1.0 - smoothstep(0.23, 0.38, lum)
    not_sky = 1.0 - smoothstep(70.0, 118.0, b - g * 0.35)
    taper = (0.07 + 0.29 * (v ** 0.78)) * (0.85 + 0.15 * math.sin(v * 20.0))
    center_env = math.exp(-(((u - 0.50) / max(0.05, taper)) ** 2))
    top_fade = smoothstep(0.0, 0.07, v)
    bot_fade = smoothstep(0.0, 0.07, 1.0 - v)
    alpha = clamp(darkness * (0.45 + 0.55 * not_sky) * smoothstep(0.10, 0.42, center_env) * top_fade * bot_fade, 0.0, 1.0)
    if alpha <= 0.02:
        return 0.0, 0.0, 0.0, 0.0
    local_u = clamp(0.50 + (u - 0.50) / max(0.12, taper * 2.1), 0.0, 1.0)
    nr, ng, nb = sculpt_cypress_impasto(r, g, b, local_u, v, moon_side=moon_side)
    return nr, ng, nb, alpha


# WHY: Samples Starry Night with aspect-corrected coordinates, cobalt-to-cerulean horizon glow, and warm cadmium stellar/lunar halos.
def sample_aspect_starry_sky(st_px, st_w, st_h, nx, ny, aspect, include_moon=True, include_village=True, include_cypress=True):
    v_max = 0.95 if include_village else 0.70
    sv = clamp(0.03 + ny * (v_max - 0.03), 0.025, v_max)

    if not include_cypress:
        u_sky = clamp(0.30 + nx * 0.47, 0.30, 0.77)
        r, g, b = enhance_vangogh_pigment(*sample_bilinear(st_px, st_w, st_h, u_sky, sv))
        hz = smoothstep(0.36, 0.96, ny)
        slum = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
        star_w = smoothstep(0.56, 0.86, slum)
        r += 8.0 * hz + 20.0 * star_w
        g += 22.0 * hz + 14.0 * star_w
        b += 30.0 * hz - 8.0 * star_w
        return soft_channel(r), soft_channel(g), soft_channel(b)

    u_left = clamp(0.02 + (nx / 0.74) * 0.80, 0.02, 0.82)
    r1, g1, b1 = enhance_vangogh_pigment(*sample_bilinear(st_px, st_w, st_h, u_left, sv))

    u_right = clamp(0.76 - ((nx - 0.58) / 0.42) * 0.42, 0.32, 0.76)
    v_right = clamp(0.05 + ny * (0.86 if include_village else 0.66), 0.04, 0.88)
    r2, g2, b2 = enhance_vangogh_pigment(*sample_bilinear(st_px, st_w, st_h, u_right, v_right))

    blend_r = smoothstep(0.56, 0.76, nx)
    r = r1 * (1.0 - blend_r) + r2 * blend_r
    g = g1 * (1.0 - blend_r) + g2 * blend_r
    b = b1 * (1.0 - blend_r) + b2 * blend_r

    slum_base = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
    not_dark_cyp = smoothstep(0.18, 0.34, slum_base)
    if include_village:
        horizon_glow = math.exp(-(((ny - 0.64) / 0.115) ** 2)) * not_dark_cyp * smoothstep(0.16, 0.28, nx)
        r += horizon_glow * 12.0
        g += horizon_glow * 28.0
        b += horizon_glow * 38.0
    else:
        horizon_glow = smoothstep(0.28, 0.62, ny) * (1.0 - smoothstep(0.66, 0.86, ny)) * not_dark_cyp
        r += horizon_glow * 10.0
        g += horizon_glow * 24.0
        b += horizon_glow * 34.0

    pan_stars = (
        (0.090, 0.092, 0.058),
        (0.232, 0.252, 0.064),
        (0.342, 0.558, 0.088),
        (0.562, 0.172, 0.062),
        (0.710, 0.302, 0.066),
    )
    if include_moon:
        for scx, scy, srad in pan_stars:
            sdx = ((nx - scx) * aspect) / (srad * 2.8)
            sdy = (ny - scy) / srad
            sd = math.hypot(sdx, sdy)
            if sd < 1.35:
                ring = math.exp(-(((sd - 0.52) / 0.38) ** 2)) * not_dark_cyp
                core = (1.0 - smoothstep(0.0, 0.48, sd)) * not_dark_cyp
                r += ring * 30.0 + core * 22.0
                g += ring * 22.0 + core * 18.0
                b -= ring * 10.0

        mcx, mcy, mrad_y = 0.895, 0.255, 0.225
        dx_m = ((nx - mcx) * aspect) / (mrad_y * (st_w / float(st_h)))
        dy_m = (ny - mcy) / mrad_y
        mdist = math.hypot(dx_m * 1.15, dy_m)
        if mdist < 1.22:
            mu = clamp(0.876 + dx_m * 0.135, 0.735, 0.992)
            mv = clamp(0.155 + dy_m * 0.145, 0.015, 0.335)
            raw_mr, raw_mg, raw_mb = sample_bilinear(st_px, st_w, st_h, mu, mv)
            mr, mg, mb = enhance_vangogh_pigment(raw_mr, raw_mg, raw_mb)
            amber_crescent = smoothstep(28.0, 74.0, raw_mr - raw_mg * 0.78) * (1.0 - smoothstep(0.46, 0.72, mdist))
            corona = math.exp(-(((mdist - 0.66) / 0.34) ** 2)) * (1.0 - amber_crescent)
            mr = mr * 1.03 + corona * 24.0 + amber_crescent * 22.0
            mg = mg * (1.01 - 0.16 * amber_crescent) + corona * 18.0 - amber_crescent * 10.0
            mb = mb * (0.86 - 0.38 * amber_crescent) - corona * 8.0
            ma = 1.0 - smoothstep(0.72, 1.20, mdist)
            r = r * (1.0 - ma) + mr * ma
            g = g * (1.0 - ma) + mg * ma
            b = b * (1.0 - ma) + mb * ma

    return soft_channel(r), soft_channel(g), soft_channel(b)


def pick_vangogh_glyph(lum, mag, theta_deg, motif, r, g, b):
    ang = theta_deg % 180.0
    if motif == 4:
        is_seed = (r > 75) and (g < r * 0.68) and (b < 76)
        if is_seed:
            seed_ramp = "+*x#%8@"
            idx = int(round(clamp(lum * 1.85, 0.0, 1.0) * (len(seed_ramp) - 1)))
            return seed_ramp[max(0, min(len(seed_ramp) - 1, idx))]
        if g > r * 0.92 and r < 160:
            return "/" if ang < 68.0 else ("\\" if ang > 112.0 else "|")
        if 22.0 <= ang < 68.0:
            return "/" if lum < 0.74 else "*"
        if 112.0 < ang <= 158.0:
            return "\\" if lum < 0.74 else "*"
        if 68.0 <= ang <= 112.0:
            return "(" if lum < 0.76 else "v"
        return "~" if lum < 0.72 else "*"

    if motif == 3:
        if lum > 0.30:
            if 26.0 <= ang < 70.0:
                return "/"
            if 110.0 < ang <= 154.0:
                return "\\"
            if 70.0 <= ang <= 110.0:
                return "(" if (int(r + g) % 2 == 0) else ")"
            return "s" if lum > 0.44 else "~"
        cyp_ramp = ":;~|/)s+vx#"
        idx = int(round(clamp(lum * 2.6, 0.0, 1.0) * (len(cyp_ramp) - 1)))
        return cyp_ramp[max(1, min(len(cyp_ramp) - 1, idx))]

    if motif == 2:
        is_wheat = (r > 130) and (r > b * 1.25)
        if is_wheat:
            if 30.0 <= ang <= 84.0:
                return "/"
            if 96.0 <= ang <= 150.0:
                return "\\"
            return "|" if mag > 0.24 else "~"
        if mag > 0.22:
            if 22.0 <= ang < 68.0:
                return "/"
            if 112.0 < ang <= 158.0:
                return "\\"
            if 68.0 <= ang <= 112.0:
                return "|"
            return "=" if lum > 0.48 else "~"
        land_ramp = ":;~+=*vcxz#%@"
        idx = int(round(clamp(lum * 1.32, 0.0, 1.0) * (len(land_ramp) - 1)))
        return land_ramp[max(0, min(len(land_ramp) - 1, idx))]

    if lum > 0.84:
        return "@" if lum > 0.93 else ("*" if mag < 0.40 else "%")
    if lum > 0.62:
        if 22.0 <= ang < 68.0:
            return "/"
        if 112.0 < ang <= 158.0:
            return "\\"
        if 68.0 <= ang <= 112.0:
            return "(" if r > b else ")"
        return "*" if lum > 0.75 else "~"
    if mag > 0.14:
        if 22.0 <= ang < 68.0:
            return "/"
        if 112.0 < ang <= 158.0:
            return "\\"
        if 68.0 <= ang <= 112.0:
            return "(" if ang < 90.0 else ")"
        return "~" if lum > 0.30 else "="
    sky_ramp = ":;~+=*o%@"
    idx = int(round(clamp(lum * 1.32, 0.0, 1.0) * (len(sky_ramp) - 1)))
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
                r, g, b = sample_aspect_starry_sky(
                    st_px, st_w, st_h, nx, ny, aspect,
                    include_moon=False, include_village=False, include_cypress=False,
                )
                seam_x = smoothstep(0.0, 0.16, nx) * smoothstep(0.0, 0.16, 1.0 - nx)
                if seam_x < 0.999:
                    wr, wg, wb = sample_aspect_starry_sky(
                        st_px, st_w, st_h, (nx + 0.5) % 1.0, ny, aspect,
                        include_moon=False, include_village=False, include_cypress=False,
                    )
                    r = r * seam_x + wr * (1.0 - seam_x)
                    g = g * seam_x + wg * (1.0 - seam_x)
                    b = b * seam_x + wb * (1.0 - seam_x)
                slum = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
                motif = 1 if slum > 0.52 else 0
                bg_r, bg_g, bg_b = r, g, b

            elif mode == "panorama":
                r, g, b = sample_aspect_starry_sky(st_px, st_w, st_h, nx, ny, aspect, include_moon=True, include_village=True)
                bg_r, bg_g, bg_b = r, g, b

                u_raw_l = clamp(0.02 + (nx / 0.74) * 0.80, 0.02, 0.82)
                v_raw_l = clamp(0.03 + ny * 0.92, 0.025, 0.95)
                raw_lr, raw_lg, raw_lb = sample_bilinear(st_px, st_w, st_h, u_raw_l, v_raw_l)
                raw_llum = (0.299 * raw_lr + 0.587 * raw_lg + 0.114 * raw_lb) / 255.0
                slum = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
                in_left_cyp = (0.06 <= nx <= 0.235) and (ny >= 0.04) and (raw_llum < 0.33) and (raw_lr < 106) and (raw_lb < 112)
                if in_left_cyp:
                    cyp_u = clamp((nx - 0.075) / 0.145, 0.0, 1.0)
                    cyp_v = clamp((ny - 0.04) / 0.92, 0.0, 1.0)
                    r, g, b = sculpt_cypress_impasto(raw_lr, raw_lg, raw_lb, cyp_u, cyp_v, moon_side=1.0)
                    core_w = 0.92 * (1.0 - smoothstep(0.80, 1.0, abs(cyp_u - 0.5) * 2.0))
                    bg_r = 18.0 * (1.0 - core_w) + (r * 0.74) * core_w
                    bg_g = 42.0 * (1.0 - core_w) + (g * 0.78) * core_w
                    bg_b = 88.0 * (1.0 - core_w) + (b * 0.82) * core_w
                    motif = 3
                elif ny > 0.74 and nx > 0.24:
                    warm_win = smoothstep(18.0, 56.0, r - b * 0.85) * smoothstep(0.76, 0.84, ny)
                    r = soft_channel(r * 1.08 + 8.0 + warm_win * 36.0)
                    g = soft_channel(g * 1.08 + 10.0 + warm_win * 24.0)
                    b = soft_channel(b * 1.10 + 14.0)
                    motif = 2
                elif slum > 0.50 or (0.24 <= nx <= 0.72 and 0.18 <= ny <= 0.68):
                    motif = 1
                else:
                    motif = 0

                if 0.795 <= nx <= 0.865 and ny >= 0.44:
                    cu = (nx - 0.795) / 0.070
                    cv = (ny - 0.44) / 0.56
                    cr, cg, cb, calpha = sample_provence_cypress_matte(pr_px, pr_w, pr_h, cu, cv, moon_side=1.0)
                    if calpha > 0.05:
                        r = r * (1.0 - calpha) + cr * calpha
                        g = g * (1.0 - calpha) + cg * calpha
                        b = b * (1.0 - calpha) + cb * calpha
                        if calpha > 0.36:
                            motif = 3

                if nx < 0.18 or nx > 0.82:
                    prev_m = motif
                    r, g, b, motif = render_sunflower_bed(r, g, b, motif, nx, ny, aspect, sf_px, sf_w, sf_h, pan_blossoms)
                    if motif == 4 and prev_m != 4:
                        bg_r = bg_r * 0.38 + r * 0.52
                        bg_g = bg_g * 0.38 + g * 0.50
                        bg_b = bg_b * 0.42 + b * 0.44

            else:
                st_r, st_g, st_b = sample_aspect_starry_sky(
                    st_px, st_w, st_h, nx, ny, aspect,
                    include_moon=False, include_village=False,
                )

                pu = clamp(0.03 + ((nx - 0.31) / 0.38) * 0.94, 0.02, 0.98)
                pv = clamp(0.02 + ny * 0.96, 0.02, 0.98)
                pr_raw_r, pr_raw_g, pr_raw_b = sample_bilinear(pr_px, pr_w, pr_h, pu, pv)
                pr_r, pr_g, pr_b = enhance_vangogh_pigment(pr_raw_r, pr_raw_g, pr_raw_b)

                is_wheat_zone = (ny > 0.50) and (pr_raw_r > pr_raw_b * 1.18) and (pr_raw_r > 105)
                is_road_zone = (ny > 0.54) and (pu > 0.46) and (pr_raw_b > pr_raw_r * 0.88) and (pr_raw_g > 110)
                if is_wheat_zone:
                    pr_r = soft_channel(pr_r * 1.12 + 18.0)
                    pr_g = soft_channel(pr_g * 1.04 + 12.0)
                    pr_b = soft_channel(pr_b * 0.78 + 4.0)
                elif is_road_zone:
                    pr_r = soft_channel(pr_r * 0.96 + 10.0)
                    pr_g = soft_channel(pr_g * 1.08 + 18.0)
                    pr_b = soft_channel(pr_b * 1.12 + 22.0)

                if nx < 0.33 and ny > 0.50:
                    wu = clamp(0.04 + (nx / 0.33) * 0.34, 0.03, 0.38)
                    wv = clamp(0.52 + ((ny - 0.50) / 0.50) * 0.45, 0.52, 0.97)
                    wr, wg, wb = enhance_vangogh_pigment(*sample_bilinear(pr_px, pr_w, pr_h, wu, wv))
                    wr = soft_channel(wr * 1.12 + 16.0)
                    wg = soft_channel(wg * 1.04 + 10.0)
                    w_blend = smoothstep(0.50, 0.62, ny)
                    st_r = st_r * (1.0 - w_blend) + wr * w_blend
                    st_g = st_g * (1.0 - w_blend) + wg * w_blend
                    st_b = st_b * (1.0 - w_blend) + wb * w_blend
                elif nx > 0.67 and ny > 0.52:
                    ru = clamp(0.66 + ((nx - 0.67) / 0.33) * 0.30, 0.66, 0.97)
                    rv = clamp(0.54 + ((ny - 0.52) / 0.48) * 0.43, 0.54, 0.97)
                    rr, rg, rb = enhance_vangogh_pigment(*sample_bilinear(pr_px, pr_w, pr_h, ru, rv))
                    rg = soft_channel(rg * 1.06 + 12.0)
                    rb = soft_channel(rb * 1.08 + 16.0)
                    r_blend = smoothstep(0.52, 0.64, ny)
                    st_r = st_r * (1.0 - r_blend) + rr * r_blend
                    st_g = st_g * (1.0 - r_blend) + rg * r_blend
                    st_b = st_b * (1.0 - r_blend) + rb * r_blend

                prov_mask = smoothstep(0.27, 0.35, nx) * smoothstep(0.27, 0.35, 1.0 - nx)
                r = st_r * (1.0 - prov_mask) + pr_r * prov_mask
                g = st_g * (1.0 - prov_mask) + pr_g * prov_mask
                b = st_b * (1.0 - prov_mask) + pr_b * prov_mask
                bg_r, bg_g, bg_b = r, g, b

                raw_lum_pr = (0.299 * pr_raw_r + 0.587 * pr_raw_g + 0.114 * pr_raw_b) / 255.0
                cyp_half = 0.032 + 0.036 * smoothstep(0.02, 0.58, ny)
                in_cyp_cone = abs(nx - 0.496) <= cyp_half and ny <= 0.775
                not_pr_sky = (pr_raw_b - pr_raw_g * 0.55) < 76.0
                in_center_cyp = in_cyp_cone and (raw_lum_pr < 0.38) and not_pr_sky and (prov_mask > 0.45)
                if in_center_cyp:
                    cyp_u = clamp(0.50 + (nx - 0.496) / max(0.04, cyp_half * 2.0), 0.0, 1.0)
                    cyp_v = clamp(ny / 0.775, 0.0, 1.0)
                    r, g, b = sculpt_cypress_impasto(pr_raw_r, pr_raw_g, pr_raw_b, cyp_u, cyp_v, moon_side=1.0)
                    core_w = 0.92 * (1.0 - smoothstep(0.78, 1.0, abs(cyp_u - 0.5) * 2.0))
                    bg_r = min(st_r, 34.0) * (1.0 - core_w) + (r * 0.74) * core_w
                    bg_g = min(st_g, 68.0) * (1.0 - core_w) + (g * 0.78) * core_w
                    bg_b = min(st_b, 118.0) * (1.0 - core_w) + (b * 0.82) * core_w
                    motif = 3
                elif ny > 0.52:
                    motif = 2
                else:
                    lum_now = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
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
                        cr, cg, cb, calpha = sample_provence_cypress_matte(
                            pr_px, pr_w, pr_h, cu, cv,
                            moon_side=(-1.0 if cflip else 1.0),
                        )
                        if calpha > 0.05:
                            r = r * (1.0 - calpha) + cr * calpha
                            g = g * (1.0 - calpha) + cg * calpha
                            b = b * (1.0 - calpha) + cb * calpha
                            c_bg = max(0.0, (calpha - 0.28) * 1.15)
                            bg_r = bg_r * (1.0 - c_bg) + (cr * 0.70) * c_bg
                            bg_g = bg_g * (1.0 - c_bg) + (cg * 0.74) * c_bg
                            bg_b = bg_b * (1.0 - c_bg) + (cb * 0.78) * c_bg
                            if calpha > 0.36:
                                motif = 3

                if nx < 0.34 or nx > 0.66:
                    prev_m = motif
                    r, g, b, motif = render_sunflower_bed(r, g, b, motif, nx, ny, aspect, sf_px, sf_w, sf_h, garden_blossoms)
                    if motif == 4 and prev_m != 4:
                        bg_r = bg_r * 0.36 + r * 0.54
                        bg_g = bg_g * 0.36 + g * 0.52
                        bg_b = bg_b * 0.40 + b * 0.44

            out_px[x, y] = (int(round(clamp(r))), int(round(clamp(g))), int(round(clamp(b))))
            bg_px[x, y] = (int(round(clamp(bg_r))), int(round(clamp(bg_g))), int(round(clamp(bg_b))))
            motif_map[y][x] = motif

    out_im = out_im.filter(ImageFilter.UnsharpMask(radius=1.15, percent=128, threshold=2))
    return out_im, bg_im, motif_map


# WHY: Builds 3-tier back-to-front impasto strokes (base ribbons, mid bristles, fine luminous filaments) for delicate 3D brushwork.
def extract_calligraphic_layer(comp_im, bg_im, motif_map, cols=204, rows=60, max_strokes=3100, wrap_x=False):
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
        for x in range(cols):
            xm1 = (x - 1) % cols if wrap_x else max(0, x - 1)
            xp1 = (x + 1) % cols if wrap_x else min(cols - 1, x + 1)
            tl = gpx[xm1, y - 1] / 255.0
            tc = gpx[x, y - 1] / 255.0
            tr = gpx[xp1, y - 1] / 255.0
            ml = gpx[xm1, y] / 255.0
            mr = gpx[xp1, y] / 255.0
            bl = gpx[xm1, y + 1] / 255.0
            bc = gpx[x, y + 1] / 255.0
            br = gpx[xp1, y + 1] / 255.0
            ix_map[y][x] = (tr + 2.0 * mr + br) - (tl + 2.0 * ml + bl)
            iy_map[y][x] = (bl + 2.0 * bc + br) - (tl + 2.0 * tc + tr)

    theta_map = [[0.0] * cols for _ in range(rows)]
    mag_map = [[0.0] * cols for _ in range(rows)]
    max_mag = 1e-6
    for y in range(1, rows - 1):
        for x in range(cols):
            if not wrap_x and (x == 0 or x == cols - 1):
                continue
            jxx = 0.0
            jxy = 0.0
            jyy = 0.0
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    wt = 4.0 if (dx == 0 and dy == 0) else (2.0 if (dx == 0 or dy == 0) else 1.0)
                    sx = (x + dx) % cols if wrap_x else (x + dx)
                    gx = ix_map[y + dy][sx]
                    gy = iy_map[y + dy][sx]
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
            norm_mag = min(1.0, mag_map[y][x] / (max_mag * 0.50))
            theta_d = theta_map[y][x]
            ch = pick_vangogh_glyph(lum, norm_mag, theta_d, motif, r, g, b)
            lift = 1.08 + norm_mag * 0.18
            qr = quantize_channel(r * lift, 5)
            qg = quantize_channel(g * lift, 5)
            qb = quantize_channel(b * lift, 5)
            if max(qr, qg, qb) < 38:
                qr, qg, qb = qr + 14, qg + 26, qb + 48
            hex_c = rgb_hex(qr, qg, qb)
            if hex_c == cur_col:
                cur_chars.append(ch)
            else:
                if cur_col != "__INIT__":
                    runs.append([cur_col, "".join(cur_chars)])
                cur_col = hex_c
                cur_chars = [ch]

            b_hex = rgb_hex(
                quantize_channel(br * 0.90 + 4.0, 10),
                quantize_channel(bg_g * 0.91 + 6.0, 10),
                quantize_channel(bb * 0.94 + 8.0, 10),
            )
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

    candidates = []
    seed = 188905

    def trace_curve(nx, ny, tx0, ty0, span_x, span_y):
        x_mid = clamp(nx + tx0 * span_x * 0.48, 0.003, 0.997)
        y_mid = clamp(ny + ty0 * span_y * 0.48, 0.003, 0.997)
        xm_i = min(cols - 2, max(1, int(x_mid * cols)))
        ym_i = min(rows - 2, max(1, int(y_mid * rows)))
        ang1 = math.radians(theta_map[ym_i][xm_i])
        tx1, ty1 = math.cos(ang1), math.sin(ang1)
        if tx0 * tx1 + ty0 * ty1 < 0:
            tx1, ty1 = -tx1, -ty1
        x0_s = clamp(nx - tx0 * span_x * 0.56, 0.002, 0.998)
        y0_s = clamp(ny - ty0 * span_y * 0.56, 0.002, 0.998)
        x1_s = clamp(x_mid + tx1 * span_x * 0.56, 0.002, 0.998)
        y1_s = clamp(y_mid + ty1 * span_y * 0.56, 0.002, 0.998)
        return x0_s, y0_s, x_mid, y_mid, x1_s, y1_s

    for y in range(1, rows - 1):
        for x in range(1, cols - 1):
            seed = (1664525 * seed + 1013904223) & 0xFFFFFFFF
            jx = (((seed >> 8) & 0xFF) / 255.0 - 0.5) * 0.62
            seed = (1664525 * seed + 1013904223) & 0xFFFFFFFF
            jy = (((seed >> 8) & 0xFF) / 255.0 - 0.5) * 0.62
            nx = clamp((x + 0.5 + jx) / float(cols), 0.006, 0.994)
            ny = clamp((y + 0.5 + jy) / float(rows), 0.006, 0.994)
            if wrap_x and (nx < 0.018 or nx > 0.982):
                continue

            mx_src = min(w - 1, int(nx * w))
            my_src = min(h - 1, int(ny * h))
            motif = motif_map[my_src][mx_src]
            r, g, b = cpx[x, y]
            lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
            norm_mag = min(1.0, mag_map[y][x] / (max_mag * 0.48))

            ang0 = math.radians(theta_map[y][x])
            tx0, ty0 = math.cos(ang0), math.sin(ang0)

            if (x + y) % 2 == 0:
                tier = 0 if ((x // 2 + y) % 2 == 0 and norm_mag < 0.46 and motif in (0, 2)) else 1
                if tier == 0:
                    span_x = (1.36 + (1.0 - norm_mag) * 0.62) / float(cols)
                    span_y = (1.20 + (1.0 - norm_mag) * 0.54) / float(rows)
                    sw = round(0.96 + (1.0 - norm_mag * 0.35) * 0.32, 2)
                    scol = rgb_hex(
                        quantize_channel(r * 0.96 + 4.0, 5),
                        quantize_channel(g * 0.97 + 5.0, 5),
                        quantize_channel(b * 0.99 + 6.0, 5),
                    )
                    prio = 0.42 + lum * 0.28 + norm_mag * 0.24
                else:
                    detail_scale = 0.78 if motif in (3, 4) else 1.0
                    span_x = (1.02 + norm_mag * 0.58) * detail_scale / float(cols)
                    span_y = (0.90 + norm_mag * 0.50) * detail_scale / float(rows)
                    sw = round(0.68 + norm_mag * 0.30, 2)
                    scol = rgb_hex(
                        quantize_channel(r * 1.05 + 6.0, 5),
                        quantize_channel(g * 1.05 + 6.0, 5),
                        quantize_channel(b * 1.05 + 6.0, 5),
                    )
                    prio = 0.50 + norm_mag * 0.46 + lum * 0.32 + (0.26 if motif in (1, 3, 4) else 0.0)

                x0_s, y0_s, xm_s, ym_s, x1_s, y1_s = trace_curve(nx, ny, tx0, ty0, span_x, span_y)
                candidates.append((
                    prio,
                    tier,
                    [
                        round(x0_s, 4),
                        round(y0_s, 4),
                        round(xm_s, 4),
                        round(ym_s, 4),
                        round(x1_s, 4),
                        round(y1_s, 4),
                        scol,
                        sw,
                        motif,
                    ],
                ))

            is_filament = (norm_mag > 0.30) or (lum > 0.62) or (motif in (3, 4) and (x + y * 3) % 3 == 0)
            if is_filament and ((x * 3 + y * 5) % 3 == 0):
                f_span_x = (0.68 + norm_mag * 0.44) / float(cols)
                f_span_y = (0.60 + norm_mag * 0.38) / float(rows)
                f_nx = clamp(nx - ty0 * (0.18 / float(cols)), 0.006, 0.994)
                f_ny = clamp(ny + tx0 * (0.18 / float(rows)), 0.006, 0.994)
                x0_f, y0_f, xm_f, ym_f, x1_f, y1_f = trace_curve(f_nx, f_ny, tx0, ty0, f_span_x, f_span_y)
                warm_fil = clamp((r - b * 0.78) / 120.0, 0.0, 1.0)
                fr = r * 1.14 + 14.0 + warm_fil * 10.0
                fg = g * 1.13 + 13.0 + warm_fil * 6.0
                fb = b * (1.12 - 0.08 * warm_fil) + 12.0 * (1.0 - warm_fil)
                fcol = rgb_hex(quantize_channel(fr, 4), quantize_channel(fg, 4), quantize_channel(fb, 4))
                fsw = round(0.46 + min(0.26, norm_mag * 0.24), 2)
                fprio = 0.56 + norm_mag * 0.50 + lum * 0.38 + (0.30 if motif in (1, 3, 4) else 0.0)
                candidates.append((
                    fprio,
                    2,
                    [
                        round(x0_f, 4),
                        round(y0_f, 4),
                        round(xm_f, 4),
                        round(ym_f, 4),
                        round(x1_f, 4),
                        round(y1_f, 4),
                        fcol,
                        fsw,
                        motif,
                    ],
                ))

    tier_pools = [[], [], []]
    for prio, tier, stroke in candidates:
        tier_pools[tier].append((prio, tier, stroke))
    for tp in tier_pools:
        tp.sort(key=lambda item: item[0], reverse=True)

    n0 = int(round(max_strokes * 0.28))
    n1 = int(round(max_strokes * 0.44))
    n2 = max(0, max_strokes - n0 - n1)
    top_pool = tier_pools[0][:n0] + tier_pools[1][:n1] + tier_pools[2][:n2]
    top_pool.sort(key=lambda item: item[0], reverse=True)

    # WHY: Chunks by priority bands while ordering Tier 0 -> Tier 1 -> Tier 2 inside each band so both partial SVG prefixes and full Web canvases layer fine highlights over base brushwork.
    band_size = 550
    picked_strokes = []
    for start in range(0, len(top_pool), band_size):
        chunk = top_pool[start:start + band_size]
        chunk.sort(key=lambda item: (item[1], -item[0]))
        for item in chunk:
            picked_strokes.append(item[2])

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

    panorama = extract_calligraphic_layer(pan_im, pan_bg, pan_motifs, cols=204, rows=60, max_strokes=3100, wrap_x=False)
    garden = extract_calligraphic_layer(gar_im, gar_bg, gar_motifs, cols=204, rows=66, max_strokes=3300, wrap_x=False)
    sky = extract_calligraphic_layer(sky_im, sky_bg, sky_motifs, cols=160, rows=56, max_strokes=2000, wrap_x=True)

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
