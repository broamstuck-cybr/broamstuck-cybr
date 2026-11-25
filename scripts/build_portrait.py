# SPDX-License-Identifier: MIT
import argparse
import json
import math
import os
from PIL import Image, ImageEnhance, ImageFilter


def clamp(v, lo=0.0, hi=255.0):
    return lo if v < lo else (hi if v > hi else v)


def smoothstep(edge0, edge1, x):
    t = clamp((x - edge0) / max(1e-6, edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


# WHY: Soft-knee highlight roll-off preserves warm ivory star cores and specular rail/hair sheen without flat white clipping.
def soft_channel(v, knee=226.0, ceiling=252.0):
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


def hill_horizon_y(nx):
    return 0.504 + 0.012 * math.sin(nx * 9.6 + 0.40) - 0.009 * math.cos(nx * 16.2 - 0.70)


def in_shirt_envelope(nx, ny):
    if ny < 0.600:
        return False
    if ny < 0.645:
        return 0.432 <= nx <= 0.566
    if ny < 0.704:
        half_w = 0.068 + (ny - 0.645) * 1.70
        return abs(nx - 0.502) <= half_w
    if ny <= 0.835:
        return 0.342 <= nx <= 0.664
    return 0.382 <= nx <= 0.644


def classify_pixel(r, g, b, nx, ny):
    lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
    red_dom = (r - max(g, b)) / 255.0

    ear_taper = 0.088 - 0.013 * smoothstep(0.515, 0.585, ny)
    head_rx = (nx - 0.494) / ear_taper
    head_ry = (ny - 0.534) / 0.084
    head_r2 = head_rx * head_rx + head_ry * head_ry

    # WHY: Solid inner cranial core prevents bright crown hair-part highlights from misclassifying as Starry Night sky holes.
    in_inner_crown = (((nx - 0.494) / 0.066) ** 2 + ((ny - 0.528) / 0.063) ** 2) <= 1.0
    is_hair = in_inner_crown or (head_r2 <= 1.14 and lum < 0.39 and r < 126 and (b >= r - 22))

    is_neck_skin = (
        (0.415 <= nx <= 0.575)
        and (0.525 <= ny <= 0.638)
        and (not is_hair)
        and red_dom > 0.030
        and lum > 0.22
    )
    is_arm_skin = (
        ((0.365 <= nx <= 0.422) or (0.588 <= nx <= 0.642))
        and (0.785 <= ny <= 0.855)
        and red_dom > 0.035
        and lum > 0.25
    )
    is_skin = is_neck_skin or is_arm_skin

    is_shirt = (
        in_shirt_envelope(nx, ny)
        and (not is_hair)
        and (red_dom > 0.072 or (r > 122 and r > g * 1.13))
    )

    in_top_rail_band = (0.714 <= ny <= 0.752) and not (is_shirt or is_skin)
    in_mid_rail_band = (0.820 <= ny <= 0.858) and not (is_shirt or is_skin)
    in_bot_deck = (ny >= 0.946) and not is_shirt
    is_cool_steel = (
        (ny >= 0.714)
        and not (is_shirt or is_skin)
        and (b >= g * 0.92)
        and (r <= g * 0.95)
        and abs(b - g) < 38
    )
    is_rail = in_top_rail_band or in_mid_rail_band or in_bot_deck or is_cool_steel

    hy = hill_horizon_y(nx)
    sky_mix = 0.0
    if not (is_hair or is_skin or is_shirt or is_rail):
        sky_mix = 1.0 - smoothstep(hy - 0.012, hy + 0.018, ny)

    is_sky = sky_mix > 0.50

    if is_shirt or is_hair or is_skin:
        plane = 3
    elif is_rail:
        plane = 2
    elif is_sky:
        plane = 0
    else:
        plane = 1

    return {
        "lum": lum,
        "sky_mix": sky_mix,
        "is_hair": is_hair,
        "is_skin": is_skin,
        "is_shirt": is_shirt,
        "is_sky": is_sky,
        "is_rail": is_rail,
        "plane": plane,
    }


def _sample_bilinear_rgb(px_acc, w, h, u, v):
    x = clamp(u * (w - 1), 0.0, w - 1.001)
    y = clamp(v * (h - 1), 0.0, h - 1.001)
    x0, y0 = int(x), int(y)
    tx, ty = x - x0, y - y0
    c00 = px_acc[x0, y0]
    c10 = px_acc[x0 + 1, y0]
    c01 = px_acc[x0, y0 + 1]
    c11 = px_acc[x0 + 1, y0 + 1]
    return (
        c00[0] * (1.0 - tx) * (1.0 - ty) + c10[0] * tx * (1.0 - ty) + c01[0] * (1.0 - tx) * ty + c11[0] * tx * ty,
        c00[1] * (1.0 - tx) * (1.0 - ty) + c10[1] * tx * (1.0 - ty) + c01[1] * (1.0 - tx) * ty + c11[1] * tx * ty,
        c00[2] * (1.0 - tx) * (1.0 - ty) + c10[2] * tx * (1.0 - ty) + c01[2] * (1.0 - tx) * ty + c11[2] * tx * ty,
    )


def _map_portrait_sky_uv(nx, ny, hy):
    dome_y = clamp(ny / max(0.12, hy + 0.025), 0.0, 1.0)
    span_u = 1.04 - 0.10 * dome_y
    u = clamp(0.50 + (nx - 0.50) * span_u, 0.025, 0.975)
    v = clamp(0.03 + dome_y * 0.69, 0.025, 0.73)
    return u, v


def _stylize_sky_rgb(nx, ny, starry_ref=None):
    hy = hill_horizon_y(nx)
    if starry_ref is not None:
        spx, sw, sh = starry_ref
        u, v = _map_portrait_sky_uv(nx, ny, hy)
        sr, sg, sb = _sample_bilinear_rgb(spx, sw, sh, u, v)
        slum = (0.299 * sr + 0.587 * sg + 0.114 * sb) / 255.0
        warm = clamp((sr - sb * 0.76) / 112.0, 0.0, 1.0)
        cool = clamp((sb - sr * 0.80) / 108.0, 0.0, 1.0)
        halo = smoothstep(0.46, 0.86, slum) * smoothstep(-12.0, 28.0, (sr + sg) * 0.5 - sb * 0.92)
        warm_eff = max(warm, halo * 0.76)

        in_cyp = (0.09 <= u <= 0.27) and (slum < 0.28) and (sr < 102) and (sb < 106)
        if in_cyp:
            cyp_u = clamp((u - 0.10) / 0.16, 0.0, 1.0)
            flame_a = 0.5 + 0.5 * math.sin(nx * 108.0 + ny * 44.0)
            flame_b = 0.5 + 0.5 * math.cos(nx * 165.0 - ny * 58.0)
            flame = 0.65 * flame_a + 0.35 * flame_b
            bronze = max(0.0, flame - 0.62) * 2.2
            rim = smoothstep(0.36, 0.92, abs(cyp_u - 0.5) * 2.0) * 0.68
            return (
                soft_channel(sr * 0.84 + 12.0 + flame * 24.0 + bronze * 54.0 + rim * 20.0),
                soft_channel(sg * 1.28 + 26.0 + flame * 56.0 + bronze * 36.0 + rim * 46.0),
                soft_channel(sb * 1.10 + 24.0 + flame * 36.0 + bronze * 12.0 + rim * 52.0),
            )

        hz = smoothstep(0.58, 0.99, ny / max(0.12, hy))
        mid_lift = 0.86 + 0.42 * (slum ** 0.76)
        nr = sr * mid_lift * (0.90 + 0.36 * warm_eff) + 12.0 * warm_eff + 10.0 * hz
        ng = sg * mid_lift * (0.98 + 0.24 * warm_eff + 0.12 * cool) + 10.0 * warm_eff + 24.0 * hz
        nb = sb * (1.02 + 0.28 * (slum ** 0.80) + 0.16 * cool - 0.10 * warm_eff) + 22.0 * (1.0 - warm_eff) + 32.0 * hz
        return soft_channel(nr), soft_channel(ng), soft_channel(nb)

    sky_t = clamp((hy - ny) / max(0.1, hy), 0.0, 1.0)
    swirl = 0.5 + 0.5 * math.sin(nx * 15.0 + ny * 9.5)
    return (
        soft_channel(18.0 + 44.0 * swirl),
        soft_channel(40.0 + 84.0 * swirl),
        soft_channel(88.0 + 104.0 * sky_t + 68.0 * swirl),
    )


# WHY: Separates sunlit golden-citrine paddy inlays, emerald-jade fields, plum ribbons, and dark warrior contours behind the railing.
def _stylize_field_rgb(r, g, b, lum, local_diff, nx, ny):
    hy = hill_horizon_y(nx)
    dist_from_h = max(0.0, ny - hy)
    foothill_band = 1.0 - smoothstep(0.0, 0.036, dist_from_h)
    sat = (max(r, g, b) - min(r, g, b)) / 255.0
    haze_suppress = foothill_band * (1.0 - clamp(sat * 3.6, 0.0, 1.0) * 0.54)

    micro = local_diff * 188.0
    yellow_inlay = smoothstep(26.0, 72.0, (r + g) * 0.5 - b) * smoothstep(115.0, 175.0, r) * smoothstep(115.0, 175.0, g)
    plum_ribbon = smoothstep(4.0, 34.0, r - g * 1.02) * smoothstep(58.0, 118.0, r) * (1.0 - yellow_inlay)
    dark_mural = (1.0 - smoothstep(0.20, 0.36, lum)) * (1.0 - plum_ribbon * 0.6)

    fr = r * 1.02 + 10.0 + micro * 1.12
    fg = g * 1.12 + 14.0 + micro * 1.18
    fb = b * 0.84 + 12.0 + micro * 0.82

    if yellow_inlay > 0.02:
        yr = r * 1.12 + 22.0 + micro * 1.15
        yg = g * 1.12 + 18.0 + micro * 1.12
        yb = b * 0.66 + 6.0 + micro * 0.60
        fr = fr * (1.0 - yellow_inlay) + yr * yellow_inlay
        fg = fg * (1.0 - yellow_inlay) + yg * yellow_inlay
        fb = fb * (1.0 - yellow_inlay) + yb * yellow_inlay

    if plum_ribbon > 0.02:
        pr = r * 1.16 + 20.0 + micro * 1.10
        pg = g * 0.84 + 8.0 + micro * 0.80
        pb = b * 1.02 + 18.0 + micro * 0.95
        fr = fr * (1.0 - plum_ribbon) + pr * plum_ribbon
        fg = fg * (1.0 - plum_ribbon) + pg * plum_ribbon
        fb = fb * (1.0 - plum_ribbon) + pb * plum_ribbon

    if dark_mural > 0.05:
        dr = r * 0.86 + 10.0 + micro * 1.25
        dg = g * 1.06 + 18.0 + micro * 1.30
        db = b * 0.94 + 20.0 + micro * 1.00
        fr = fr * (1.0 - dark_mural * 0.72) + dr * (dark_mural * 0.72)
        fg = fg * (1.0 - dark_mural * 0.72) + dg * (dark_mural * 0.72)
        fb = fb * (1.0 - dark_mural * 0.72) + db * (dark_mural * 0.72)

    ridge_tex = 0.5 + 0.5 * math.sin(nx * 36.0 + ny * 52.0)
    hill_r = 16.0 + 26.0 * ridge_tex
    hill_g = 42.0 + 56.0 * ridge_tex
    hill_b = 78.0 + 68.0 * ridge_tex

    nr = fr * (1.0 - haze_suppress) + hill_r * haze_suppress
    ng = fg * (1.0 - haze_suppress) + hill_g * haze_suppress
    nb = fb * (1.0 - haze_suppress) + hill_b * haze_suppress
    return soft_channel(nr), soft_channel(ng), soft_channel(nb)


def _rail_bevel_profile(ny):
    if 0.714 <= ny <= 0.752:
        t = (ny - 0.714) / 0.038
        hi = math.exp(-(((t - 0.22) / 0.20) ** 2))
        lo = smoothstep(0.66, 0.98, t)
        return hi, lo
    if 0.820 <= ny <= 0.858:
        t = (ny - 0.820) / 0.038
        hi = math.exp(-(((t - 0.24) / 0.22) ** 2)) * 0.88
        lo = smoothstep(0.68, 0.98, t) * 0.88
        return hi, lo
    if ny >= 0.946:
        hi = math.exp(-(((ny - 0.952) / 0.012) ** 2)) * 0.70
        return hi, 0.25
    return 0.18, 0.12


def stylize_nocturne_pixel(r, g, b, nx, ny, local_diff=0.0, meta=None, refs=None):
    info = meta or classify_pixel(r, g, b, nx, ny)
    lum = info["lum"]
    refs = refs or {}

    if info["is_shirt"]:
        smooth_diff = clamp(local_diff, -0.14, 0.16)
        fold = (lum - 0.52) * 118.0 + smooth_diff * 215.0
        collar_hi = math.exp(-(((ny - 0.618) / 0.014) ** 2)) * (1.0 - smoothstep(0.035, 0.068, abs(nx - 0.500))) * 0.75
        yoke_hi = math.exp(-(((ny - 0.678) / 0.010) ** 2)) * (1.0 - smoothstep(0.06, 0.11, abs(nx - 0.502))) * 0.55
        shoulder_hi = smoothstep(0.72, 0.625, ny) * smoothstep(0.03, 0.10, abs(nx - 0.502)) * 0.52
        moon_rim = smoothstep(0.04, 0.145, abs(nx - 0.502)) * (0.76 if nx > 0.50 else 0.42)
        sheen = collar_hi + yoke_hi + shoulder_hi + moon_rim

        nr = r * 1.10 + 18.0 + fold * 0.98 + sheen * 28.0
        ng = g * 0.66 + 9.0 + fold * 0.62 + sheen * 22.0
        nb = b * 0.63 + 11.0 + fold * 0.54 + sheen * 16.0
        return soft_channel(nr), soft_channel(ng), soft_channel(nb)

    if info["is_skin"]:
        micro = clamp(local_diff, -0.12, 0.14) * 135.0
        rim = smoothstep(0.02, 0.06, abs(nx - 0.495)) * 14.0
        nr = r * 1.10 + 22.0 + micro + rim
        ng = g * 0.95 + 15.0 + micro * 0.86 + rim * 0.78
        nb = b * 0.82 + 12.0 + micro * 0.70 + rim * 0.55
        return soft_channel(nr), soft_channel(ng), soft_channel(nb)

    if info["is_hair"]:
        whirl_dx = nx - 0.496
        whirl_dy = (ny - 0.498) * 1.12
        whirl_r = math.hypot(whirl_dx, whirl_dy)
        whirl_th = math.atan2(whirl_dy, whirl_dx)
        lock_a = 0.5 + 0.5 * math.sin(whirl_th * 13.0 + whirl_r * 44.0)
        lock_b = 0.5 + 0.5 * math.cos(whirl_th * 23.0 - whirl_r * 28.0)
        lock_wave = 0.66 * lock_a + 0.34 * lock_b

        head_rx = (nx - 0.494) / 0.088
        head_ry = (ny - 0.534) / 0.082
        radial = math.hypot(head_rx, head_ry)
        crown_arc = smoothstep(0.48, 0.98, radial) * smoothstep(0.61, 0.445, ny)
        outer_halo = smoothstep(0.76, 1.06, radial) * smoothstep(0.58, 0.455, ny)
        part_glow = math.exp(-((whirl_r / 0.026) ** 2)) * 0.38
        warm_side = smoothstep(-0.15, 0.72, head_rx)

        eff_lum = min(0.32, lum)
        strand_boost = clamp(
            eff_lum * 3.25 + clamp(local_diff, -0.14, 0.20) * 4.6 + lock_wave * 0.32 + part_glow,
            0.0,
            1.0,
        )
        nr = 16.0 + strand_boost * 48.0 + crown_arc * (30.0 + 48.0 * warm_side) + outer_halo * 28.0
        ng = 26.0 + strand_boost * 74.0 + crown_arc * (54.0 + 42.0 * warm_side) + outer_halo * 46.0
        nb = 48.0 + strand_boost * 112.0 + crown_arc * (96.0 - 14.0 * warm_side) + outer_halo * 64.0
        return soft_channel(nr), soft_channel(ng), soft_channel(nb)

    if info["is_rail"]:
        bevel_hi, bevel_lo = _rail_bevel_profile(ny)
        spec = max(0.0, lum - 0.60) * 145.0 + max(0.0, local_diff) * 175.0 + bevel_hi * 44.0
        shade = 1.0 - bevel_lo * 0.24
        nr = (r * 0.74 + 20.0) * shade + spec * 0.80
        ng = (g * 0.92 + 32.0) * shade + spec * 0.96
        nb = (b * 1.12 + 48.0) * shade + spec * 1.12
        return soft_channel(nr), soft_channel(ng), soft_channel(nb)

    smix = info["sky_mix"]
    if smix >= 0.995:
        return _stylize_sky_rgb(nx, ny, refs.get("starry"))
    if smix <= 0.005:
        return _stylize_field_rgb(r, g, b, lum, local_diff, nx, ny)
    sr, sg, sb = _stylize_sky_rgb(nx, ny, refs.get("starry"))
    fr, fg, fb = _stylize_field_rgb(r, g, b, lum, local_diff, nx, ny)
    return (
        soft_channel(sr * smix + fr * (1.0 - smix)),
        soft_channel(sg * smix + fg * (1.0 - smix)),
        soft_channel(sb * smix + fb * (1.0 - smix)),
    )


def pick_directional_glyph(lum, mag, gx, gy, nx, ny, meta):
    if meta["is_sky"]:
        edge_ang = (math.degrees(math.atan2(gy, gx)) + 90.0) % 180.0
        if lum > 0.82:
            return "@" if lum > 0.91 else ("*" if mag < 0.38 else "%")
        if lum > 0.62:
            if 22.0 <= edge_ang < 68.0:
                return "/"
            if 112.0 < edge_ang <= 158.0:
                return "\\"
            return "*" if mag < 0.28 else "~"
        if mag > 0.19:
            if 22.0 <= edge_ang < 68.0:
                return "/"
            if 112.0 < edge_ang <= 158.0:
                return "\\"
            if 68.0 <= edge_ang <= 112.0:
                return "(" if nx < 0.5 else ")"
            return "~" if lum > 0.34 else "="
        sky_ramp = ":;~+=*o%@"
        idx = int(round(clamp(lum * 1.28, 0.0, 1.0) * (len(sky_ramp) - 1)))
        return sky_ramp[max(0, min(len(sky_ramp) - 1, idx))]

    if meta["is_hair"]:
        whirl_dx = nx - 0.496
        whirl_dy = ny - 0.498
        tang_ang = (math.degrees(math.atan2(whirl_dy, whirl_dx)) + 90.0) % 180.0
        if lum > 0.26:
            if 24.0 <= tang_ang < 68.0:
                return "/"
            if 112.0 < tang_ang <= 156.0:
                return "\\"
            if 68.0 <= tang_ang <= 112.0:
                return "(" if whirl_dx < 0 else ")"
            return "~" if lum < 0.46 else "*"
        hair_ramp = ":;~+i!l/|()vcxzsJC#@"
        idx = int(round((clamp(lum * 2.40, 0.0, 1.0) ** 0.74) * (len(hair_ramp) - 1)))
        return hair_ramp[max(1, min(len(hair_ramp) - 1, idx))]

    if meta["is_rail"]:
        if (0.714 <= ny <= 0.752) or (0.820 <= ny <= 0.858) or (ny >= 0.946):
            if lum > 0.72:
                return "="
            if lum > 0.48:
                return "~" if mag < 0.28 else "="
            return "-"
        if mag > 0.24:
            return "|" if lum < 0.62 else "I"

    if mag > 0.29:
        ang = math.degrees(math.atan2(gy, gx)) % 180.0
        edge_ang = (ang + 90.0) % 180.0
        if 72.0 <= edge_ang <= 108.0:
            return "|" if lum < 0.58 else "I"
        if (edge_ang >= 164.0 or edge_ang <= 16.0) and mag > 0.44:
            return "=" if lum > 0.46 else "-"
        if 22.0 < edge_ang < 68.0:
            return "/"
        if 112.0 < edge_ang < 158.0:
            return "\\"

    ramp = ":;+~*i!lI/\\|()vcnxzjft1{}[]<>7rJCLQ0OZmwqpdbkhao#MW&8%B@$"
    vis = clamp(lum * 1.10 + mag * 0.12, 0.0, 1.0)
    idx = int(round((vis ** 0.82) * (len(ramp) - 1)))
    return ramp[max(0, min(len(ramp) - 1, idx))]


def build_sky_impasto_vectors(starry_img=None):
    if starry_img is None:
        return []
    sw, sh = 156, 120
    s_rgb = starry_img.resize((sw, sh), Image.Resampling.LANCZOS)
    s_gray = s_rgb.convert("L")
    spx = s_rgb.load()
    sgx = s_gray.load()
    base_strokes = []
    fine_strokes = []

    for v_step in range(2, 54, 2):
        ny = v_step / 104.0
        hy = hill_horizon_y(0.5)
        if ny >= hy - 0.010:
            continue
        for u_step in range(2, 103, 2):
            if (u_step + v_step) % 2 != 0:
                continue
            nx = u_step / 104.0
            if (nx - 0.5) ** 2 + (ny - 0.5) ** 2 > 0.258:
                continue
            su, sv = _map_portrait_sky_uv(nx, ny, hill_horizon_y(nx))
            ix = min(sw - 2, max(1, int(su * (sw - 1))))
            iy = min(sh - 2, max(1, int(sv * (sh - 1))))
            gx = (sgx[ix + 1, iy] - sgx[ix - 1, iy]) / 255.0
            gy = (sgx[ix, iy + 1] - sgx[ix, iy - 1]) / 255.0
            gm = math.hypot(gx, gy)
            if gm < 0.042:
                continue
            tx, ty = -gy / gm, gx / gm
            r, g, b = spx[ix, iy]
            lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
            warm = clamp((r - b * 0.76) / 118.0, 0.0, 1.0)
            sr = r * (0.90 + 0.42 * warm) + 14.0
            sg = g * (0.96 + 0.30 * warm) + 14.0
            sb = b * (1.06 - 0.08 * warm) + 20.0 * (1.0 - warm)

            is_hi = lum > 0.58 or gm > 0.16
            span = (0.011 + min(0.011, gm * 0.026)) if is_hi else (0.016 + min(0.015, gm * 0.034))
            mx = nx + tx * span * 0.5 - ty * 0.0026
            my = ny + ty * span * 0.5 + tx * 0.0026
            entry = (
                gm + lum * 0.45,
                [
                    round(nx - tx * span * 0.46, 4),
                    round(ny - ty * span * 0.46, 4),
                    round(mx, 4),
                    round(my, 4),
                    round(nx + tx * span * 0.54, 4),
                    round(ny + ty * span * 0.54, 4),
                    rgb_hex(
                        quantize_channel(sr * (1.08 if is_hi else 0.98), 5),
                        quantize_channel(sg * (1.08 if is_hi else 0.98), 5),
                        quantize_channel(sb * (1.06 if is_hi else 0.99), 5),
                    ),
                    round(min(0.78, (0.36 if is_hi else 0.28) + gm * 0.82), 2),
                ],
            )
            if is_hi:
                fine_strokes.append(entry)
            else:
                base_strokes.append(entry)

    base_strokes.sort(key=lambda item: item[0], reverse=True)
    fine_strokes.sort(key=lambda item: item[0], reverse=True)
    return [s[1] for s in base_strokes[:260]] + [s[1] for s in fine_strokes[:220]]


def _load_ref(path):
    if not path or not os.path.exists(path):
        return None, None
    im = Image.open(path).convert("RGB")
    im = ImageEnhance.Contrast(im).enhance(1.16)
    im = ImageEnhance.Color(im).enhance(1.16)
    return im, (im.load(), im.width, im.height)


# WHY: Horizontally inpaints occluded field pixels with organic paddy grain so 2.5D parallax never exposes dark silhouette voids.
def _inpaint_field_grid(raw_rgb, ldiff_grid, meta_grid, cols, rows, refs):
    inpainted = [[(0.0, 0.0, 0.0)] * cols for _ in range(rows)]
    for y in range(rows):
        ny = (y + 0.5) / float(rows)
        hy_mid = hill_horizon_y(0.5)
        if ny < hy_mid - 0.03:
            for x in range(cols):
                nx = (x + 0.5) / float(cols)
                inpainted[y][x] = _stylize_sky_rgb(nx, ny, refs.get("starry"))
            continue

        field_pts = []
        for x in range(cols):
            m = meta_grid[y][x]
            if m["plane"] in (0, 1):
                nx = (x + 0.5) / float(cols)
                r, g, b = raw_rgb[y][x]
                lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
                hy = hill_horizon_y(nx)
                if ny <= hy:
                    col = _stylize_sky_rgb(nx, ny, refs.get("starry"))
                else:
                    col = _stylize_field_rgb(r, g, b, lum, ldiff_grid[y][x], nx, ny)
                field_pts.append((x, col))
                inpainted[y][x] = col

        if not field_pts:
            for x in range(cols):
                nx = (x + 0.5) / float(cols)
                if ny > hill_horizon_y(nx):
                    furrow = math.sin(nx * 84.0 + ny * 56.0) * 6.0
                    inpainted[y][x] = (46.0 + furrow, 108.0 + furrow * 1.3, 52.0 + furrow * 0.6)
                else:
                    inpainted[y][x] = _stylize_sky_rgb(nx, ny, refs.get("starry"))
            continue

        for x in range(cols):
            if meta_grid[y][x]["plane"] in (0, 1):
                continue
            nx = (x + 0.5) / float(cols)
            if ny <= hill_horizon_y(nx):
                inpainted[y][x] = _stylize_sky_rgb(nx, ny, refs.get("starry"))
                continue
            left_p = None
            right_p = None
            for fx, fcol in field_pts:
                if fx < x:
                    left_p = (fx, fcol)
                elif fx > x:
                    right_p = (fx, fcol)
                    break
            furrow = math.sin(nx * 96.0 + ny * 62.0) * 4.5
            if left_p and right_p:
                t = (x - left_p[0]) / float(max(1, right_p[0] - left_p[0]))
                ts = t * t * (3.0 - 2.0 * t)
                c0, c1 = left_p[1], right_p[1]
                inpainted[y][x] = (
                    clamp(c0[0] * (1.0 - ts) + c1[0] * ts + furrow * 0.8),
                    clamp(c0[1] * (1.0 - ts) + c1[1] * ts + furrow * 1.1),
                    clamp(c0[2] * (1.0 - ts) + c1[2] * ts + furrow * 0.6),
                )
            elif left_p:
                c0 = left_p[1]
                inpainted[y][x] = (clamp(c0[0] + furrow * 0.8), clamp(c0[1] + furrow * 1.1), clamp(c0[2] + furrow * 0.6))
            else:
                c1 = right_p[1]
                inpainted[y][x] = (clamp(c1[0] + furrow * 0.8), clamp(c1[1] + furrow * 1.1), clamp(c1[2] + furrow * 0.6))
    return inpainted


def build_portrait(src_path, out_path, starry_path=None, sunflowers_path=None, provence_path=None, cols=208, rows=122, hatch_n=76):
    raw = Image.open(src_path).convert("RGB")
    size = min(raw.size)
    left = (raw.width - size) // 2
    top = (raw.height - size) // 2
    square = raw.crop((left, top, left + size, top + size)).resize((640, 640), Image.Resampling.LANCZOS)

    sharp = square.filter(ImageFilter.UnsharpMask(radius=1.45, percent=158, threshold=2))
    sharp = ImageEnhance.Contrast(sharp).enhance(1.16)
    sharp = ImageEnhance.Color(sharp).enhance(1.18)

    starry_im, starry_ref = _load_ref(starry_path)
    refs = {"starry": starry_ref}

    gray_hi = sharp.convert("L")
    blur_hi = gray_hi.filter(ImageFilter.GaussianBlur(radius=7.0))

    gray_img = gray_hi.resize((cols, rows), Image.Resampling.LANCZOS)
    blur_img = blur_hi.resize((cols, rows), Image.Resampling.LANCZOS)
    col_img = sharp.resize((cols, rows), Image.Resampling.LANCZOS)

    gray_px = gray_img.load()
    blur_px = blur_img.load()
    col_px = col_img.load()

    raw_rgb = [[(0, 0, 0)] * cols for _ in range(rows)]
    ldiff_grid = [[0.0] * cols for _ in range(rows)]
    stylized_rgb = [[(0.0, 0.0, 0.0)] * cols for _ in range(rows)]
    stylized_lum = [[0.0] * cols for _ in range(rows)]
    meta_grid = [[None] * cols for _ in range(rows)]

    for y in range(rows):
        ny = (y + 0.5) / float(rows)
        for x in range(cols):
            nx = (x + 0.5) / float(cols)
            r, g, b = col_px[x, y]
            ldiff = (gray_px[x, y] - blur_px[x, y]) / 255.0
            meta = classify_pixel(r, g, b, nx, ny)
            sr, sg, sb = stylize_nocturne_pixel(r, g, b, nx, ny, ldiff, meta, refs)
            raw_rgb[y][x] = (r, g, b)
            ldiff_grid[y][x] = ldiff
            meta_grid[y][x] = meta
            stylized_rgb[y][x] = (sr, sg, sb)
            stylized_lum[y][x] = (0.299 * sr + 0.587 * sg + 0.114 * sb) / 255.0

    gx_map = [[0.0] * cols for _ in range(rows)]
    gy_map = [[0.0] * cols for _ in range(rows)]
    mag_map = [[0.0] * cols for _ in range(rows)]
    max_mag = 1e-6

    for y in range(1, rows - 1):
        for x in range(1, cols - 1):
            tl = stylized_lum[y - 1][x - 1]
            tc = stylized_lum[y - 1][x]
            tr = stylized_lum[y - 1][x + 1]
            ml = stylized_lum[y][x - 1]
            mr = stylized_lum[y][x + 1]
            bl = stylized_lum[y + 1][x - 1]
            bc = stylized_lum[y + 1][x]
            br = stylized_lum[y + 1][x + 1]
            gx = (tr + 2.0 * mr + br) - (tl + 2.0 * ml + bl)
            gy = (bl + 2.0 * bc + br) - (tl + 2.0 * tc + tr)
            m = math.hypot(gx, gy)
            gx_map[y][x] = gx
            gy_map[y][x] = gy
            mag_map[y][x] = m
            if m > max_mag:
                max_mag = m

    grid = []
    planes = []
    for y in range(rows):
        ny = (y + 0.5) / float(rows)
        dy_c = (ny - 0.5) * 2.0
        runs = []
        row_planes = []
        cur_col = "__INIT__"
        cur_chars = []

        for x in range(cols):
            nx = (x + 0.5) / float(cols)
            dx_c = (nx - 0.5) * 2.0
            if dx_c * dx_c + dy_c * dy_c > 1.085:
                cell_col = None
                ch = " "
                row_planes.append("0")
            else:
                meta = meta_grid[y][x]
                row_planes.append(str(meta["plane"]))
                sr, sg, sb = stylized_rgb[y][x]
                lum = stylized_lum[y][x]
                norm_mag = min(1.0, mag_map[y][x] / (max_mag * 0.52))
                ch = pick_directional_glyph(lum, norm_mag, gx_map[y][x], gy_map[y][x], nx, ny, meta)
                edge_lift = 1.02 + norm_mag * (0.20 if meta["plane"] >= 2 else 0.14)
                q_step = 5 if meta["is_sky"] else 4
                qr = quantize_channel(sr * edge_lift, q_step)
                qg = quantize_channel(sg * edge_lift, q_step)
                qb = quantize_channel(sb * edge_lift, q_step)
                if max(qr, qg, qb) < 36:
                    qr, qg, qb = qr + 16, qg + 26, qb + 44
                cell_col = rgb_hex(qr, qg, qb)

            if cell_col == cur_col:
                cur_chars.append(ch)
            else:
                if cur_col != "__INIT__":
                    runs.append([cur_col, "".join(cur_chars)])
                cur_col = cell_col
                cur_chars = [ch]
        if cur_chars:
            runs.append([cur_col, "".join(cur_chars)])
        grid.append(runs)
        planes.append("".join(row_planes))

    h_img = sharp.resize((hatch_n, hatch_n), Image.Resampling.LANCZOS)
    h_gray = gray_hi.resize((hatch_n, hatch_n), Image.Resampling.LANCZOS)
    h_blur = blur_hi.resize((hatch_n, hatch_n), Image.Resampling.LANCZOS)
    hpx = h_img.load()
    hgx = h_gray.load()
    hbx = h_blur.load()
    h_raw = [[(0, 0, 0)] * hatch_n for _ in range(hatch_n)]
    h_ldiff = [[0.0] * hatch_n for _ in range(hatch_n)]
    h_lum = [[0.0] * hatch_n for _ in range(hatch_n)]
    h_rgb = [[(0.0, 0.0, 0.0)] * hatch_n for _ in range(hatch_n)]
    h_meta = [[None] * hatch_n for _ in range(hatch_n)]

    for ay in range(hatch_n):
        ny = (ay + 0.5) / float(hatch_n)
        for ax in range(hatch_n):
            nx = (ax + 0.5) / float(hatch_n)
            r, g, b = hpx[ax, ay]
            ldiff = (hgx[ax, ay] - hbx[ax, ay]) / 255.0
            m = classify_pixel(r, g, b, nx, ny)
            sr, sg, sb = stylize_nocturne_pixel(r, g, b, nx, ny, ldiff, m, refs)
            h_raw[ay][ax] = (r, g, b)
            h_ldiff[ay][ax] = ldiff
            h_meta[ay][ax] = m
            h_rgb[ay][ax] = (sr, sg, sb)
            h_lum[ay][ax] = (0.299 * sr + 0.587 * sg + 0.114 * sb) / 255.0

    h_bg_inpaint = _inpaint_field_grid(h_raw, h_ldiff, h_meta, hatch_n, hatch_n, refs)

    under_strokes = []
    bg_under_strokes = []
    for ay in range(hatch_n):
        ny = (ay + 0.5) / float(hatch_n)
        dy_c = (ny - 0.5) * 2.0
        for ax in range(hatch_n):
            nx = (ax + 0.5) / float(hatch_n)
            dx_c = (nx - 0.5) * 2.0
            if dx_c * dx_c + dy_c * dy_c > 1.09:
                continue
            meta = h_meta[ay][ax]
            sr, sg, sb = h_rgb[ay][ax]
            if meta["is_hair"]:
                wdx, wdy = nx - 0.496, ny - 0.498
                wm = math.hypot(wdx, wdy) or 1.0
                tx, ty = -wdy / wm, wdx / wm
            elif meta["is_rail"] and ((0.714 <= ny <= 0.752) or (0.820 <= ny <= 0.858)):
                tx, ty = 1.0, 0.0
            elif 0 < ax < hatch_n - 1 and 0 < ay < hatch_n - 1:
                gx_h = h_lum[ay][ax + 1] - h_lum[ay][ax - 1]
                gy_h = h_lum[ay + 1][ax] - h_lum[ay - 1][ax]
                gm = math.hypot(gx_h, gy_h)
                if gm > 0.028:
                    tx, ty = -gy_h / gm, gx_h / gm
                else:
                    tx, ty = (0.0, 1.0) if meta["is_shirt"] else (1.0, 0.0)
            else:
                tx, ty = 1.0, 0.0

            ang_deg = int(round(math.degrees(math.atan2(ty, tx)))) % 180
            under_strokes.append([
                ax,
                ay,
                rgb_hex(quantize_channel(sr * 0.85, 6), quantize_channel(sg * 0.85, 6), quantize_channel(sb * 0.86, 6)),
                meta["plane"],
                ang_deg,
            ])

            if meta["plane"] >= 2:
                br, bg_g, bb = h_bg_inpaint[ay][ax]
                bg_pl = 0 if ny <= hill_horizon_y(nx) else 1
                bg_under_strokes.append([
                    ax,
                    ay,
                    rgb_hex(quantize_channel(br * 0.88, 6), quantize_channel(bg_g * 0.88, 6), quantize_channel(bb * 0.89, 6)),
                    bg_pl,
                ])
                if meta["plane"] == 3 and ((0.714 <= ny <= 0.752) or (0.820 <= ny <= 0.858)):
                    b_hi, b_lo = _rail_bevel_profile(ny)
                    r_rail = (96.0 + b_hi * 78.0) * (1.0 - b_lo * 0.28)
                    g_rail = (142.0 + b_hi * 82.0) * (1.0 - b_lo * 0.25)
                    b_rail = (196.0 + b_hi * 54.0) * (1.0 - b_lo * 0.20)
                    bg_under_strokes.append([ax, ay, rgb_hex(r_rail, g_rail, b_rail), 2])

    c_size = 192
    c_gray = gray_hi.resize((c_size, c_size), Image.Resampling.LANCZOS)
    c_blur = blur_hi.resize((c_size, c_size), Image.Resampling.LANCZOS)
    c_rgb = sharp.resize((c_size, c_size), Image.Resampling.LANCZOS)
    cg = c_gray.load()
    cb = c_blur.load()
    cr = c_rgb.load()
    candidates = []
    for y in range(2, c_size - 2, 2):
        ny = y / float(c_size)
        if ny < 0.442:
            continue
        for x in range(2, c_size - 2, 2):
            nx = x / float(c_size)
            if (nx - 0.5) ** 2 + (ny - 0.5) ** 2 > 0.242:
                continue
            hy = hill_horizon_y(nx)
            if abs(ny - hy) < 0.020 and not (0.39 <= nx <= 0.60):
                continue
            gx = (cg[x + 1, y] - cg[x - 1, y]) / 255.0
            gy = (cg[x, y + 1] - cg[x, y - 1]) / 255.0
            mag = math.hypot(gx, gy)
            r, g, b = cr[x, y]
            meta = classify_pixel(r, g, b, nx, ny)
            if meta["is_hair"]:
                head_rx = (nx - 0.494) / 0.088
                head_ry = (ny - 0.534) / 0.082
                radial = math.hypot(head_rx, head_ry)
                is_crown_rim = (0.76 <= radial <= 1.08) and (ny <= 0.555)
                if is_crown_rim and mag >= 0.085:
                    warm_rim = smoothstep(-0.1, 0.7, head_rx)
                    seg_col = rgb_hex(124 + warm_rim * 72, 182 + warm_rim * 38, 238 - warm_rim * 34)
                    seg_op = round(min(0.66, 0.34 + mag * 0.75), 2)
                elif 0.11 <= mag <= 0.36:
                    seg_col = "#4670a8"
                    seg_op = 0.38
                else:
                    continue
            else:
                is_fg = meta["plane"] >= 2
                in_warrior = meta["plane"] == 1 and 0.54 <= ny <= 0.92
                thresh = 0.138 if is_fg else (0.160 if in_warrior else 0.215)
                if mag < thresh:
                    continue
                ldiff = (cg[x, y] - cb[x, y]) / 255.0
                sr, sg, sb = stylize_nocturne_pixel(r, g, b, nx, ny, ldiff, meta, refs)
                seg_col = rgb_hex(sr * 1.18 + 18.0, sg * 1.16 + 16.0, sb * 1.16 + 16.0)
                seg_op = round(min(0.78, 0.28 + mag * 0.86), 2)

            if mag < 1e-5:
                continue
            tx = -gy / mag
            ty = gx / mag
            half_len = 0.0086 if meta["plane"] >= 2 else 0.0072
            priority = mag * (1.60 if meta["plane"] == 3 else (1.40 if meta["plane"] == 2 else 1.18))
            candidates.append((
                priority,
                [
                    round(nx - tx * half_len, 4),
                    round(ny - ty * half_len, 4),
                    round(nx + tx * half_len, 4),
                    round(ny + ty * half_len, 4),
                    seg_col,
                    seg_op,
                    meta["plane"],
                ],
            ))

    candidates.sort(key=lambda item: item[0], reverse=True)
    contours = [item[1] for item in candidates[:880]]
    sky_strokes = build_sky_impasto_vectors(starry_im)

    payload = {
        "cols": cols,
        "rows": rows,
        "hatch_n": hatch_n,
        "under_strokes": under_strokes,
        "bg_under": bg_under_strokes,
        "sky_strokes": sky_strokes,
        "contours": contours,
        "planes": planes,
        "grid": grid,
    }
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, separators=(",", ":"))
    print(
        "built portrait_hd.json: %dx%d grid, %d under_strokes, %d bg_under, %d sky strokes, %d contours (%d bytes)"
        % (cols, rows, len(under_strokes), len(bg_under_strokes), len(sky_strokes), len(contours), os.path.getsize(out_path))
    )


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--starry")
    ap.add_argument("--sunflowers")
    ap.add_argument("--provence")
    args = ap.parse_args()
    build_portrait(args.src, args.out, args.starry, args.sunflowers, args.provence)
