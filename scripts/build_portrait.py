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


def rgb_hex(r, g, b):
    return "#%02x%02x%02x" % (int(round(clamp(r))), int(round(clamp(g))), int(round(clamp(b))))


def quantize_channel(v, step=5):
    return int(clamp(round(v / float(step)) * step))


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

    head_rx = (nx - 0.494) / 0.090
    head_ry = (ny - 0.534) / 0.085
    head_r2 = head_rx * head_rx + head_ry * head_ry

    # WHY: Solid inner cranial core prevents bright crown hair-part highlights from misclassifying as Starry Night sky holes.
    in_inner_crown = (((nx - 0.494) / 0.068) ** 2 + ((ny - 0.530) / 0.064) ** 2) <= 1.0
    is_hair = in_inner_crown or (head_r2 <= 1.18 and lum < 0.38 and r < 124 and (b >= r - 20))

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
        warm = clamp((sr - sb * 0.72) / 135.0, 0.0, 1.0)
        cool = clamp((sb - sr * 0.80) / 115.0, 0.0, 1.0)
        in_cyp = (0.09 <= u <= 0.27) and (slum < 0.26) and (sr < 95) and (sb < 95)
        if in_cyp:
            flame = 0.5 + 0.5 * math.sin(nx * 105.0 + ny * 42.0)
            return (
                clamp(sr * 0.92 + 10.0 + flame * 24.0),
                clamp(sg * 1.20 + 20.0 + flame * 38.0),
                clamp(sb * 0.98 + 14.0 + flame * 22.0),
            )
        nr = sr * (0.78 + 0.44 * warm + 0.20 * slum)
        ng = sg * (0.86 + 0.30 * warm + 0.20 * slum)
        nb = sb * (0.98 + 0.24 * slum + 0.14 * cool) + 18.0 * (1.0 - warm)
        return clamp(nr), clamp(ng), clamp(nb)

    sky_t = clamp((hy - ny) / max(0.1, hy), 0.0, 1.0)
    swirl = 0.5 + 0.5 * math.sin(nx * 15.0 + ny * 9.5)
    return (
        clamp(14.0 + 38.0 * swirl),
        clamp(32.0 + 74.0 * swirl),
        clamp(76.0 + 98.0 * sky_t + 64.0 * swirl),
    )


def _stylize_field_rgb(r, g, b, lum, local_diff, nx, ny):
    hy = hill_horizon_y(nx)
    dist_from_h = max(0.0, ny - hy)
    foothill_band = 1.0 - smoothstep(0.0, 0.042, dist_from_h)
    sat = (max(r, g, b) - min(r, g, b)) / 255.0
    haze_suppress = foothill_band * (1.0 - clamp(sat * 3.4, 0.0, 1.0) * 0.50)

    micro = local_diff * 165.0
    fr = clamp(r * 0.96 + 6.0 + micro * 1.10)
    fg = clamp(g * 1.02 + 8.0 + micro * 1.14)
    fb = clamp(b * 0.86 + 14.0 + micro * 0.88)

    ridge_tex = 0.5 + 0.5 * math.sin(nx * 36.0 + ny * 52.0)
    hill_r = 12.0 + 20.0 * ridge_tex
    hill_g = 30.0 + 44.0 * ridge_tex
    hill_b = 68.0 + 58.0 * ridge_tex

    nr = fr * (1.0 - haze_suppress) + hill_r * haze_suppress
    ng = fg * (1.0 - haze_suppress) + hill_g * haze_suppress
    nb = fb * (1.0 - haze_suppress) + hill_b * haze_suppress
    return clamp(nr), clamp(ng), clamp(nb)


def stylize_nocturne_pixel(r, g, b, nx, ny, local_diff=0.0, meta=None, refs=None):
    info = meta or classify_pixel(r, g, b, nx, ny)
    lum = info["lum"]
    refs = refs or {}

    if info["is_shirt"]:
        fold = (lum - 0.54) * 106.0 + local_diff * 235.0
        moon_rim = smoothstep(0.04, 0.14, abs(nx - 0.502)) * (0.62 if nx > 0.50 else 0.34)
        nr = clamp(r * 1.08 + 14.0 + fold * 0.96 + moon_rim * 30.0)
        ng = clamp(g * 0.63 + 6.0 + fold * 0.55 + moon_rim * 22.0)
        nb = clamp(b * 0.61 + 8.0 + fold * 0.48 + moon_rim * 14.0)
        return nr, ng, nb

    if info["is_skin"]:
        micro = local_diff * 130.0
        nr = clamp(r * 1.08 + 18.0 + micro)
        ng = clamp(g * 0.92 + 12.0 + micro * 0.85)
        nb = clamp(b * 0.80 + 10.0 + micro * 0.70)
        return nr, ng, nb

    if info["is_hair"]:
        whirl_dx = nx - 0.496
        whirl_dy = (ny - 0.502) * 1.12
        whirl_r = math.hypot(whirl_dx, whirl_dy)
        whirl_th = math.atan2(whirl_dy, whirl_dx)
        lock_wave = 0.5 + 0.5 * math.sin(whirl_th * 12.0 + whirl_r * 42.0)

        head_rx = (nx - 0.494) / 0.088
        head_ry = (ny - 0.534) / 0.082
        radial = math.hypot(head_rx, head_ry)
        rim = smoothstep(0.55, 1.02, radial) * smoothstep(0.62, 0.45, ny)
        warm_side = smoothstep(-0.2, 0.7, head_rx)

        eff_lum = min(0.28, lum)
        strand_boost = clamp(eff_lum * 3.1 + clamp(local_diff, -0.15, 0.18) * 4.4 + lock_wave * 0.28, 0.0, 1.0)
        nr = 14.0 + strand_boost * 44.0 + rim * (24.0 + 42.0 * warm_side)
        ng = 22.0 + strand_boost * 64.0 + rim * (40.0 + 34.0 * warm_side)
        nb = 42.0 + strand_boost * 98.0 + rim * (74.0 - 16.0 * warm_side)
        return clamp(nr), clamp(ng), clamp(nb)

    if info["is_rail"]:
        spec = max(0.0, lum - 0.64) * 135.0 + max(0.0, local_diff) * 160.0
        nr = clamp(r * 0.70 + 16.0 + spec * 0.74)
        ng = clamp(g * 0.88 + 26.0 + spec * 0.92)
        nb = clamp(b * 1.10 + 42.0 + spec * 1.08)
        return nr, ng, nb

    smix = info["sky_mix"]
    if smix >= 0.995:
        return _stylize_sky_rgb(nx, ny, refs.get("starry"))
    if smix <= 0.005:
        return _stylize_field_rgb(r, g, b, lum, local_diff, nx, ny)
    sr, sg, sb = _stylize_sky_rgb(nx, ny, refs.get("starry"))
    fr, fg, fb = _stylize_field_rgb(r, g, b, lum, local_diff, nx, ny)
    return (
        clamp(sr * smix + fr * (1.0 - smix)),
        clamp(sg * smix + fg * (1.0 - smix)),
        clamp(sb * smix + fb * (1.0 - smix)),
    )


def pick_directional_glyph(lum, mag, gx, gy, nx, ny, meta):
    if meta["is_sky"]:
        edge_ang = (math.degrees(math.atan2(gy, gx)) + 90.0) % 180.0
        if lum > 0.78:
            return "@" if lum > 0.88 else ("*" if mag < 0.35 else "%")
        if lum > 0.62:
            if 24.0 <= edge_ang < 66.0:
                return "/"
            if 114.0 < edge_ang <= 156.0:
                return "\\"
            return "*" if mag < 0.26 else "~"
        if mag > 0.22:
            if 24.0 <= edge_ang < 66.0:
                return "/"
            if 114.0 < edge_ang <= 156.0:
                return "\\"
            if 66.0 <= edge_ang <= 114.0:
                return "(" if nx < 0.5 else ")"
            return "~" if lum > 0.36 else "="
        sky_ramp = ":;~+=*o#@"
        idx = int(round(clamp(lum * 1.25, 0.0, 1.0) * (len(sky_ramp) - 1)))
        return sky_ramp[max(0, min(len(sky_ramp) - 1, idx))]

    if meta["is_hair"]:
        whirl_dx = nx - 0.496
        whirl_dy = ny - 0.502
        tang_ang = (math.degrees(math.atan2(whirl_dy, whirl_dx)) + 90.0) % 180.0
        if lum > 0.30:
            if 25.0 <= tang_ang < 68.0:
                return "/"
            if 112.0 < tang_ang <= 155.0:
                return "\\"
            if 68.0 <= tang_ang <= 112.0:
                return "(" if whirl_dx < 0 else ")"
        hair_ramp = ":;~+i!lI/|()vcnxzsJCSM#@"
        idx = int(round((clamp(lum * 2.30, 0.0, 1.0) ** 0.76) * (len(hair_ramp) - 1)))
        return hair_ramp[max(2, min(len(hair_ramp) - 1, idx))]

    if mag > 0.33:
        ang = math.degrees(math.atan2(gy, gx)) % 180.0
        edge_ang = (ang + 90.0) % 180.0
        if 74.0 <= edge_ang <= 106.0:
            return "|" if lum < 0.56 else "I"
        if (edge_ang >= 166.0 or edge_ang <= 14.0) and (meta["is_rail"] or mag > 0.50):
            return "=" if lum > 0.45 else "-"
        if 24.0 < edge_ang < 66.0:
            return "/"
        if 114.0 < edge_ang < 156.0:
            return "\\"

    ramp = " .,:;+~*i!lI?vcnxzjft/\\|()1{}[]<>7rJCLQ0OZmwqpdbkhao#MW&8%B@$"
    vis = clamp(lum * 1.08 + mag * 0.11, 0.0, 1.0)
    idx = int(round((vis ** 0.84) * (len(ramp) - 1)))
    return ramp[max(3, min(len(ramp) - 1, idx))]


def build_sky_impasto_vectors(starry_img=None):
    strokes = []
    if starry_img is not None:
        sw, sh = 148, 114
        s_rgb = starry_img.resize((sw, sh), Image.Resampling.LANCZOS)
        s_gray = s_rgb.convert("L")
        spx = s_rgb.load()
        sgx = s_gray.load()
        for v_step in range(2, 54, 3):
            ny = v_step / 104.0
            hy = hill_horizon_y(0.5)
            if ny >= hy - 0.010:
                continue
            for u_step in range(2, 103, 3):
                nx = u_step / 104.0
                if (nx - 0.5) ** 2 + (ny - 0.5) ** 2 > 0.258:
                    continue
                su, sv = _map_portrait_sky_uv(nx, ny, hill_horizon_y(nx))
                ix = min(sw - 2, max(1, int(su * (sw - 1))))
                iy = min(sh - 2, max(1, int(sv * (sh - 1))))
                gx = (sgx[ix + 1, iy] - sgx[ix - 1, iy]) / 255.0
                gy = (sgx[ix, iy + 1] - sgx[ix, iy - 1]) / 255.0
                gm = math.hypot(gx, gy)
                if gm < 0.045:
                    continue
                tx, ty = -gy / gm, gx / gm
                r, g, b = spx[ix, iy]
                warm = clamp((r - b * 0.72) / 140.0, 0.0, 1.0)
                sr = clamp(r * (0.82 + 0.42 * warm) + 10.0)
                sg = clamp(g * (0.88 + 0.32 * warm) + 10.0)
                sb = clamp(b * 1.02 + 16.0 * (1.0 - warm))
                span = 0.016 + min(0.016, gm * 0.036)
                mx = nx + tx * span * 0.5 - ty * 0.003
                my = ny + ty * span * 0.5 + tx * 0.003
                strokes.append([
                    round(nx - tx * span * 0.45, 4),
                    round(ny - ty * span * 0.45, 4),
                    round(mx, 4),
                    round(my, 4),
                    round(nx + tx * span * 0.55, 4),
                    round(ny + ty * span * 0.55, 4),
                    rgb_hex(quantize_channel(sr, 6), quantize_channel(sg, 6), quantize_channel(sb, 6)),
                    round(min(0.72, 0.30 + gm * 0.85), 2),
                ])
        return strokes[:420]
    return strokes


def _load_ref(path):
    if not path or not os.path.exists(path):
        return None, None
    im = Image.open(path).convert("RGB")
    im = ImageEnhance.Contrast(im).enhance(1.16)
    im = ImageEnhance.Color(im).enhance(1.15)
    return im, (im.load(), im.width, im.height)


# WHY: Horizontally inpaints occluded field pixels behind railing/subject so 2.5D parallax never exposes dark silhouette voids.
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
                inpainted[y][x] = (34.0, 82.0, 44.0) if ny > hill_horizon_y(nx) else _stylize_sky_rgb(nx, ny, refs.get("starry"))
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
            if left_p and right_p:
                t = (x - left_p[0]) / float(max(1, right_p[0] - left_p[0]))
                c0, c1 = left_p[1], right_p[1]
                inpainted[y][x] = (
                    c0[0] * (1.0 - t) + c1[0] * t,
                    c0[1] * (1.0 - t) + c1[1] * t,
                    c0[2] * (1.0 - t) + c1[2] * t,
                )
            elif left_p:
                inpainted[y][x] = left_p[1]
            else:
                inpainted[y][x] = right_p[1]
    return inpainted


def build_portrait(src_path, out_path, starry_path=None, sunflowers_path=None, provence_path=None, cols=208, rows=122, hatch_n=76):
    raw = Image.open(src_path).convert("RGB")
    size = min(raw.size)
    left = (raw.width - size) // 2
    top = (raw.height - size) // 2
    square = raw.crop((left, top, left + size, top + size)).resize((640, 640), Image.Resampling.LANCZOS)

    sharp = square.filter(ImageFilter.UnsharpMask(radius=1.6, percent=170, threshold=2))
    sharp = ImageEnhance.Contrast(sharp).enhance(1.18)
    sharp = ImageEnhance.Color(sharp).enhance(1.18)

    starry_im, starry_ref = _load_ref(starry_path)
    refs = {"starry": starry_ref}

    gray_hi = sharp.convert("L")
    blur_hi = gray_hi.filter(ImageFilter.GaussianBlur(radius=7.5))

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
                norm_mag = min(1.0, mag_map[y][x] / (max_mag * 0.54))
                ch = pick_directional_glyph(lum, norm_mag, gx_map[y][x], gy_map[y][x], nx, ny, meta)
                edge_lift = 1.0 + norm_mag * (0.22 if meta["plane"] >= 2 else 0.14)
                q_step = 6 if meta["is_sky"] else 5
                qr = quantize_channel(sr * edge_lift, q_step)
                qg = quantize_channel(sg * edge_lift, q_step)
                qb = quantize_channel(sb * edge_lift, q_step)
                if max(qr, qg, qb) < 32:
                    qr, qg, qb = qr + 14, qg + 22, qb + 38
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
                wdx, wdy = nx - 0.496, ny - 0.502
                wm = math.hypot(wdx, wdy) or 1.0
                tx, ty = -wdy / wm, wdx / wm
            elif 0 < ax < hatch_n - 1 and 0 < ay < hatch_n - 1:
                gx_h = h_lum[ay][ax + 1] - h_lum[ay][ax - 1]
                gy_h = h_lum[ay + 1][ax] - h_lum[ay - 1][ax]
                gm = math.hypot(gx_h, gy_h)
                if gm > 0.03:
                    tx, ty = -gy_h / gm, gx_h / gm
                else:
                    tx, ty = (0.0, 1.0) if meta["is_shirt"] else (1.0, 0.0)
            else:
                tx, ty = 1.0, 0.0

            ang_deg = int(round(math.degrees(math.atan2(ty, tx)))) % 180
            under_strokes.append([
                ax,
                ay,
                rgb_hex(quantize_channel(sr * 0.78, 8), quantize_channel(sg * 0.78, 8), quantize_channel(sb * 0.78, 8)),
                meta["plane"],
                ang_deg,
            ])

            if meta["plane"] >= 2:
                br, bg_g, bb = h_bg_inpaint[ay][ax]
                bg_pl = 0 if ny <= hill_horizon_y(nx) else 1
                bg_under_strokes.append([
                    ax,
                    ay,
                    rgb_hex(quantize_channel(br * 0.82, 8), quantize_channel(bg_g * 0.82, 8), quantize_channel(bb * 0.82, 8)),
                    bg_pl,
                ])
                if meta["plane"] == 3 and ((0.716 <= ny <= 0.750) or (0.822 <= ny <= 0.856)):
                    bg_under_strokes.append([ax, ay, "#4a78a8", 2])

    c_size = 188
    c_gray = gray_hi.resize((c_size, c_size), Image.Resampling.LANCZOS)
    c_blur = blur_hi.resize((c_size, c_size), Image.Resampling.LANCZOS)
    c_rgb = sharp.resize((c_size, c_size), Image.Resampling.LANCZOS)
    cg = c_gray.load()
    cb = c_blur.load()
    cr = c_rgb.load()
    candidates = []
    for y in range(2, c_size - 2, 2):
        ny = y / float(c_size)
        if ny < 0.460:
            continue
        for x in range(2, c_size - 2, 2):
            nx = x / float(c_size)
            if (nx - 0.5) ** 2 + (ny - 0.5) ** 2 > 0.242:
                continue
            hy = hill_horizon_y(nx)
            if abs(ny - hy) < 0.022 and not (0.40 <= nx <= 0.59):
                continue
            gx = (cg[x + 1, y] - cg[x - 1, y]) / 255.0
            gy = (cg[x, y + 1] - cg[x, y - 1]) / 255.0
            mag = math.hypot(gx, gy)
            r, g, b = cr[x, y]
            meta = classify_pixel(r, g, b, nx, ny)
            if meta["is_hair"]:
                if mag < 0.12 or mag > 0.36:
                    continue
                seg_col = "#365686"
                seg_op = 0.34
            else:
                is_fg = meta["plane"] >= 2
                in_warrior = meta["plane"] == 1 and 0.54 <= ny <= 0.90
                thresh = 0.148 if is_fg else (0.175 if in_warrior else 0.23)
                if mag < thresh:
                    continue
                ldiff = (cg[x, y] - cb[x, y]) / 255.0
                sr, sg, sb = stylize_nocturne_pixel(r, g, b, nx, ny, ldiff, meta, refs)
                seg_col = rgb_hex(clamp(sr * 1.20 + 16), clamp(sg * 1.16 + 14), clamp(sb * 1.16 + 14))
                seg_op = round(min(0.76, 0.26 + mag * 0.85), 2)

            tx = -gy / mag
            ty = gx / mag
            half_len = 0.0092 if meta["plane"] >= 2 else 0.0078
            priority = mag * (1.55 if meta["plane"] == 3 else (1.35 if meta["plane"] == 2 else 1.15))
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
    contours = [item[1] for item in candidates[:820]]
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
