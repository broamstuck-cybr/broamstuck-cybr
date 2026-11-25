# SPDX-License-Identifier: MIT
import argparse
import json
import math
import os
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

COORD_SZ = 2000


def smooth_up(e0, e1, x):
    t = np.clip((x - e0) / np.maximum(1e-6, e1 - e0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def rgb_hex(r, g, b):
    return "#%02x%02x%02x" % (
        int(round(float(np.clip(r, 0, 255)))),
        int(round(float(np.clip(g, 0, 255)))),
        int(round(float(np.clip(b, 0, 255)))),
    )


# WHY: Edge-preserving bilateral filter removes sensor grain on linen/skin/meadow while keeping Guan Yu mural and seam edges sharp.
def bilateral_smooth(img_f32, spatial_sigma=2.0, range_sigma=22.0, radius=2, passes=2):
    out = img_f32.astype(np.float32, copy=True)
    inv_2s2 = 0.5 / (spatial_sigma * spatial_sigma)
    inv_2r2 = 0.5 / (range_sigma * range_sigma)
    shifts = []
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            shifts.append((dy, dx, math.exp(-(dx * dx + dy * dy) * inv_2s2)))
    h, w, _ = out.shape
    for _ in range(passes):
        padded = np.pad(out, ((radius, radius), (radius, radius), (0, 0)), mode="edge")
        acc = np.zeros_like(out)
        wsum = np.zeros((h, w, 1), dtype=np.float32)
        for dy, dx, sw in shifts:
            nb = padded[radius + dy : radius + dy + h, radius + dx : radius + dx + w]
            diff = nb - out
            d2 = 0.30 * diff[:, :, 0] ** 2 + 0.59 * diff[:, :, 1] ** 2 + 0.11 * diff[:, :, 2] ** 2
            wt = (sw * np.exp(-d2 * inv_2r2))[:, :, None]
            acc += nb * wt
            wsum += wt
        out = acc / np.maximum(wsum, 1e-6)
    return out


def fill_holes_fast(mask):
    h, w = mask.shape
    im = Image.new("L", (w + 2, h + 2), 0)
    im.paste(Image.fromarray((mask.astype(np.uint8) * 255), mode="L"), (1, 1))
    ImageDraw.floodfill(im, (0, 0), 128)
    arr = np.asarray(im, dtype=np.uint8)[1 : h + 1, 1 : w + 1]
    return arr != 128


def keep_seed_component_fast(mask, seed_xy):
    h, w = mask.shape
    sx, sy = int(seed_xy[0]), int(seed_xy[1])
    im = Image.fromarray((mask.astype(np.uint8) * 255), mode="L").copy()
    if im.getpixel((sx, sy)) != 255:
        found = False
        for r in range(1, 35):
            for dy in range(-r, r + 1):
                for dx in range(-r, r + 1):
                    nx_i, ny_i = sx + dx, sy + dy
                    if 0 <= nx_i < w and 0 <= ny_i < h and im.getpixel((nx_i, ny_i)) == 255:
                        sx, sy = nx_i, ny_i
                        found = True
                        break
                if found:
                    break
            if found:
                break
    ImageDraw.floodfill(im, (sx, sy), 128)
    return np.asarray(im, dtype=np.uint8) == 128


def morph_dilate(mask, r=1):
    if r <= 0:
        return mask.copy()
    im = Image.fromarray((mask.astype(np.uint8) * 255), mode="L")
    return np.asarray(im.filter(ImageFilter.MaxFilter(size=2 * r + 1)), dtype=np.uint8) > 127


def morph_erode(mask, r=1):
    if r <= 0:
        return mask.copy()
    im = Image.fromarray((mask.astype(np.uint8) * 255), mode="L")
    return np.asarray(im.filter(ImageFilter.MinFilter(size=2 * r + 1)), dtype=np.uint8) > 127


def smooth_binary_mask(mask, blur_radius=2.0, thresh=0.5):
    im = Image.fromarray((mask.astype(np.uint8) * 255), mode="L")
    return np.asarray(im.filter(ImageFilter.GaussianBlur(radius=blur_radius)), dtype=np.float32) >= (thresh * 255.0)


def extrapolate_masked_rgb(rgb, mask, iterations=10):
    out = rgb.copy()
    valid = mask.copy()
    h, w, _ = out.shape
    for _ in range(iterations):
        if np.all(valid):
            break
        p_rgb = np.pad(out, ((1, 1), (1, 1), (0, 0)), mode="edge")
        p_val = np.pad(valid.astype(np.float32), ((1, 1), (1, 1)), mode="constant", constant_values=0.0)
        acc = np.zeros_like(out)
        wsum = np.zeros((h, w), dtype=np.float32)
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
            wt = 1.0 if (dy == 0 or dx == 0) else 0.7
            v_nb = p_val[1 + dy : 1 + dy + h, 1 + dx : 1 + dx + w] * wt
            acc += p_rgb[1 + dy : 1 + dy + h, 1 + dx : 1 + dx + w] * v_nb[:, :, None]
            wsum += v_nb
        fill_now = (~valid) & (wsum > 0.0)
        if not np.any(fill_now):
            break
        out[fill_now] = acc[fill_now] / wsum[fill_now, None]
        valid[fill_now] = True
    return out


def marching_squares_loops(mask, x0_map, y0_map, sx_scale, sy_scale, min_pts=6):
    h, w = mask.shape
    p = np.zeros((h + 2, w + 2), dtype=np.uint8)
    p[1 : h + 1, 1 : w + 1] = mask.astype(np.uint8)

    tl = p[:-1, :-1]
    tr = p[:-1, 1:]
    br = p[1:, 1:]
    bl = p[1:, :-1]
    code = (tl << 3) | (tr << 2) | (br << 1) | bl

    adj = {}

    def add_seg(p1, p2):
        adj.setdefault(p1, []).append(p2)

    ys, xs = np.where((code > 0) & (code < 15))
    for cy, cx in zip(ys.tolist(), xs.tolist()):
        c = int(code[cy, cx])
        top = (2 * cx + 1, 2 * cy)
        right = (2 * cx + 2, 2 * cy + 1)
        bot = (2 * cx + 1, 2 * cy + 2)
        left = (2 * cx, 2 * cy + 1)
        if c == 1:
            add_seg(left, bot)
        elif c == 2:
            add_seg(bot, right)
        elif c == 3:
            add_seg(left, right)
        elif c == 4:
            add_seg(right, top)
        elif c == 5:
            add_seg(left, top)
            add_seg(right, bot)
        elif c == 6:
            add_seg(bot, top)
        elif c == 7:
            add_seg(left, top)
        elif c == 8:
            add_seg(top, left)
        elif c == 9:
            add_seg(top, bot)
        elif c == 10:
            add_seg(top, right)
            add_seg(bot, left)
        elif c == 11:
            add_seg(top, right)
        elif c == 12:
            add_seg(right, left)
        elif c == 13:
            add_seg(right, bot)
        elif c == 14:
            add_seg(bot, left)

    loops = []
    while adj:
        start = next(iter(adj))
        cur = start
        pts = []
        while True:
            pts.append(cur)
            nxt_list = adj.get(cur)
            if not nxt_list:
                break
            nxt = nxt_list.pop()
            if not nxt_list:
                del adj[cur]
            cur = nxt
            if cur == start:
                break
        if len(pts) >= min_pts:
            arr_pts = np.array(pts, dtype=np.float32)
            gx = (arr_pts[:, 0] * 0.5) - 1.0
            gy = (arr_pts[:, 1] * 0.5) - 1.0
            loops.append(np.stack([x0_map + gx * sx_scale, y0_map + gy * sy_scale], axis=1))
    return loops


# WHY: Area-preserving Taubin smoothing removes pixel stair-stepping without shrinking fine mural features or thin ribbons.
def taubin_smooth_loop(pts, iters=3, lam=0.45, mu=-0.473):
    if len(pts) < 5:
        return pts
    cur = pts.copy()
    for _ in range(iters):
        prv = np.roll(cur, 1, axis=0)
        nxt = np.roll(cur, -1, axis=0)
        cur = cur + lam * (0.5 * (prv + nxt) - cur)
        prv = np.roll(cur, 1, axis=0)
        nxt = np.roll(cur, -1, axis=0)
        cur = cur + mu * (0.5 * (prv + nxt) - cur)
    return cur


def rdp_closed(pts, eps=1.4):
    n = len(pts)
    if n <= 6:
        return pts

    def rdp_open(arr):
        m = len(arr)
        if m <= 2:
            return arr
        p0, p1 = arr[0], arr[-1]
        vec = p1 - p0
        vlen2 = float(vec[0] * vec[0] + vec[1] * vec[1])
        rel = arr[1:-1] - p0
        dists = np.hypot(rel[:, 0], rel[:, 1]) if vlen2 < 1e-8 else (np.abs(rel[:, 0] * vec[1] - rel[:, 1] * vec[0]) / math.sqrt(vlen2))
        idx = int(np.argmax(dists))
        if float(dists[idx]) > eps:
            left = rdp_open(arr[: idx + 2])
            right = rdp_open(arr[idx + 1 :])
            return np.vstack([left[:-1], right])
        return np.vstack([p0, p1])

    i0 = int(np.argmin(pts[:, 0] + pts[:, 1] * 0.31))
    rolled = np.roll(pts, -i0, axis=0)
    half = n // 2
    first_h = rdp_open(rolled[: half + 1])
    second_h = rdp_open(np.vstack([rolled[half:], rolled[:1]]))
    merged = np.vstack([first_h[:-1], second_h[:-1]])
    return merged if len(merged) >= 3 else rolled[:3]


# WHY: Midpoint-knot relative quadratic Bezier encoding delivers C1 smooth curves at 0.5-permille precision under 450KB JSON.
def loop_to_compact_bezier(pts):
    n = len(pts)
    if n < 3:
        return ""
    if n <= 4:
        ix = np.rint(pts[:, 0]).astype(np.int32)
        iy = np.rint(pts[:, 1]).astype(np.int32)
        cx, cy = int(ix[0]), int(iy[0])
        parts = ["M%d,%d" % (cx, cy)]
        for i in range(1, n):
            dx, dy = int(ix[i]) - cx, int(iy[i]) - cy
            if dx != 0 or dy != 0:
                parts.append("l%d,%d" % (dx, dy))
                cx, cy = int(ix[i]), int(iy[i])
        parts.append("z")
        return "".join(parts)

    mids = 0.5 * (pts + np.roll(pts, -1, axis=0))
    mx = np.rint(mids[:, 0]).astype(np.int32)
    my = np.rint(mids[:, 1]).astype(np.int32)
    vx = np.rint(pts[:, 0]).astype(np.int32)
    vy = np.rint(pts[:, 1]).astype(np.int32)

    cx, cy = int(mx[0]), int(my[0])
    parts = ["M%d,%d" % (cx, cy)]
    for i in range(1, n):
        dx1, dy1 = int(vx[i]) - cx, int(vy[i]) - cy
        dx, dy = int(mx[i]) - cx, int(my[i]) - cy
        if dx == 0 and dy == 0 and dx1 == 0 and dy1 == 0:
            continue
        parts.append("q%d,%d %d,%d" % (dx1, dy1, dx, dy))
        cx += dx
        cy += dy
    dx1, dy1 = int(vx[0]) - cx, int(vy[0]) - cy
    dx, dy = int(mx[0]) - cx, int(my[0]) - cy
    parts.append("q%d,%d %d,%dz" % (dx1, dy1, dx, dy))
    return "".join(parts)


def mask_to_svg_d(mask, x0_map, y0_map, sx_scale, sy_scale, min_pts=6, taubin_iters=3, rdp_eps=1.2):
    loops = marching_squares_loops(mask, x0_map, y0_map, sx_scale, sy_scale, min_pts=min_pts)
    parts = []
    for lp in loops:
        sm = taubin_smooth_loop(lp, iters=taubin_iters)
        simp = rdp_closed(sm, eps=rdp_eps)
        d = loop_to_compact_bezier(simp)
        if d:
            parts.append(d)
    return "".join(parts)


def weighted_kmeans_rgb(pixels_f32, weights_f32, k=32, iters=13, seed=42):
    rng = np.random.default_rng(seed)
    n = len(pixels_f32)
    if n <= k:
        return pixels_f32.copy(), np.arange(n, dtype=np.int32)

    scale = np.array([1.10, 1.22, 0.92], dtype=np.float32)
    px_s = pixels_f32 * scale
    probs = weights_f32 / max(float(weights_f32.sum()), 1e-8)

    sub_n = min(n, 11000)
    sub_idx = rng.choice(n, size=sub_n, replace=False, p=probs)
    sub_px = px_s[sub_idx]
    sub_w = weights_f32[sub_idx]

    centers = np.empty((k, 3), dtype=np.float32)
    centers[0] = sub_px[int(rng.integers(0, sub_n))]
    min_d2 = np.sum((sub_px - centers[0]) ** 2, axis=1)

    for ci in range(1, k):
        w_d2 = min_d2 * sub_w
        s = float(w_d2.sum())
        pick = int(rng.choice(sub_n, p=w_d2 / s)) if s > 1e-8 else int(rng.integers(0, sub_n))
        centers[ci] = sub_px[pick]
        min_d2 = np.minimum(min_d2, np.sum((sub_px - centers[ci]) ** 2, axis=1))

    for _ in range(iters):
        dists = np.sum((sub_px[:, None, :] - centers[None, :, :]) ** 2, axis=2)
        assign = np.argmin(dists, axis=1)
        for ci in range(k):
            sel = assign == ci
            if np.any(sel):
                w_sel = sub_w[sel][:, None]
                centers[ci] = np.sum(sub_px[sel] * w_sel, axis=0) / max(float(w_sel.sum()), 1e-6)

    full_assign = np.empty(n, dtype=np.int32)
    for i0 in range(0, n, 32768):
        sl = px_s[i0 : i0 + 32768]
        d2 = np.sum((sl[:, None, :] - centers[None, :, :]) ** 2, axis=2)
        full_assign[i0 : i0 + 32768] = np.argmin(d2, axis=1)

    return np.clip(centers / scale, 0.0, 255.0), full_assign


def cluster_region_to_polys(
    rgb_field,
    region_mask,
    weights,
    k_colors,
    plane_idx,
    x0_map,
    y0_map,
    sx_scale,
    sy_scale,
    mode_passes=1,
    min_loop_pts=10,
    taubin_iters=3,
    rdp_eps=1.7,
    seam_stroke=1.6,
    base_fill_hex=None,
    clip_base_d=None,
    inner_mask=None,
    seed=42,
):
    trace_mask = inner_mask if inner_mask is not None else region_mask
    ys, xs = np.where(trace_mask)
    if len(ys) == 0:
        return []
    centers, assign = weighted_kmeans_rgb(rgb_field[ys, xs], weights[ys, xs], k=k_colors, iters=13, seed=seed)

    h, w = trace_mask.shape
    label_u8 = np.full((h, w), 255, dtype=np.uint8)
    label_u8[ys, xs] = assign.astype(np.uint8)
    for _ in range(mode_passes):
        label_u8 = np.asarray(
            Image.fromarray(label_u8, mode="L").filter(ImageFilter.ModeFilter(size=3)),
            dtype=np.uint8,
        )

    polys = []
    if base_fill_hex and clip_base_d:
        polys.append({
            "plane": plane_idx,
            "fill": base_fill_hex,
            "opacity": 1.0,
            "rule": "evenodd",
            "d": clip_base_d,
        })

    cluster_items = []
    for ci in range(len(centers)):
        cmask = (label_u8 == ci) & trace_mask
        cnt = int(cmask.sum())
        if cnt < 4:
            continue
        mean_rgb = rgb_field[cmask].mean(axis=0)
        lum = float(0.299 * mean_rgb[0] + 0.587 * mean_rgb[1] + 0.114 * mean_rgb[2])
        cluster_items.append((cnt, lum, mean_rgb, cmask))

    cluster_items.sort(key=lambda it: (-it[0], it[1]))

    for idx_c, (_, _, mean_rgb, cmask) in enumerate(cluster_items):
        if idx_c == 0 and base_fill_hex and clip_base_d:
            polys[0]["fill"] = rgb_hex(mean_rgb[0], mean_rgb[1], mean_rgb[2])
            continue
        d_str = mask_to_svg_d(
            cmask,
            x0_map,
            y0_map,
            sx_scale,
            sy_scale,
            min_pts=min_loop_pts,
            taubin_iters=taubin_iters,
            rdp_eps=rdp_eps,
        )
        if not d_str:
            continue
        entry = {
            "plane": plane_idx,
            "fill": rgb_hex(mean_rgb[0], mean_rgb[1], mean_rgb[2]),
            "opacity": 1.0,
            "rule": "evenodd",
            "d": d_str,
        }
        if seam_stroke > 0.0:
            entry["seam"] = round(seam_stroke, 1)
        polys.append(entry)
    return polys


def segment_subject_masks(arr_hi):
    h, w, _ = arr_hi.shape
    yy, xx = np.mgrid[0:h, 0:w]
    nx = (xx + 0.5) / float(w)
    ny = (yy + 0.5) / float(h)

    r = arr_hi[:, :, 0]
    g = arr_hi[:, :, 1]
    b = arr_hi[:, :, 2]
    lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0

    taper = 0.065 - 0.022 * smooth_up(0.540, 0.612, ny)
    hrx = (nx - 0.4945) / np.maximum(0.02, taper)
    hry = (ny - 0.533) / 0.075
    in_head_env = (hrx * hrx + hry * hry <= 1.18) & (ny >= 0.456) & (ny <= 0.614)
    in_crown_core = (((nx - 0.4945) / 0.048) ** 2 + ((ny - 0.532) / 0.052) ** 2) <= 1.0
    hair_raw = in_crown_core | (in_head_env & (lum < 0.37) & (r < 118.0) & (b >= r - 24.0))
    hair_mask = keep_seed_component_fast(hair_raw, (int(w * 0.495), int(h * 0.53)))
    hair_mask = fill_holes_fast(morph_dilate(hair_mask, 1))
    hair_mask = smooth_binary_mask(hair_mask, blur_radius=2.2, thresh=0.48)

    sh_left_upper = 0.452 - np.maximum(0.0, ny - 0.625) * 1.48
    sh_right_upper = 0.545 + np.maximum(0.0, ny - 0.628) * 1.44
    in_upper = (ny >= 0.616) & (ny < 0.695) & (nx >= sh_left_upper) & (nx <= sh_right_upper)
    in_sleeves = (ny >= 0.695) & (ny <= 0.826) & (nx >= 0.352) & (nx <= 0.658)
    torso_left = 0.413 - 0.014 * smooth_up(0.830, 1.000, ny)
    torso_right = 0.614 + 0.024 * smooth_up(0.830, 1.000, ny)
    in_torso = (ny > 0.823) & (nx >= torso_left) & (nx <= torso_right)
    in_shirt_env = in_upper | in_sleeves | in_torso

    is_neck_hue = (ny < 0.633) & (g > b + 6.0) & ((r - g) < 82.0)
    in_cuff_shadow = (
        (ny >= 0.768)
        & (ny <= 0.820)
        & (((nx >= 0.362) & (nx <= 0.422)) | ((nx >= 0.594) & (nx <= 0.648)))
        & (lum < 0.36)
        & (~((b > g + 6.0) & (g > r + 10.0)))
    )
    is_coral = (
        (((r - g) > 28.0) & (r > 72.0) & (b >= g * 0.85 - 5.0))
        | ((ny >= 0.640) & (np.abs(nx - 0.510) <= 0.092) & (r > g + 8.0))
        | in_cuff_shadow
    )
    is_rail_steel = (b > r + 4.0) & (g > r)
    shirt_raw = in_shirt_env & (~hair_mask) & (~is_neck_hue) & (~is_rail_steel) & is_coral
    shirt_clean = morph_dilate(morph_erode(shirt_raw, 2), 2)
    shirt_mask = keep_seed_component_fast(shirt_clean, (int(w * 0.50), int(h * 0.74)))
    shirt_mask = fill_holes_fast(morph_dilate(shirt_mask, 2))
    shirt_mask = morph_erode(shirt_mask, 1)
    shirt_mask = smooth_binary_mask(shirt_mask, blur_radius=2.6, thresh=0.50) & (~hair_mask)

    in_left_ear = (((nx - 0.443) / 0.011) ** 2 + ((ny - 0.571) / 0.021) ** 2 <= 1.0) & (r > 125.0) & ((r - g) > 16.0)
    in_right_ear = (((nx - 0.546) / 0.010) ** 2 + ((ny - 0.572) / 0.020) ** 2 <= 1.0) & (r > 125.0) & ((r - g) > 16.0)
    in_neck = (
        (ny >= 0.576)
        & (ny <= 0.636)
        & (nx >= 0.456)
        & (nx <= 0.540)
        & (r > 110.0)
        & ((r - g) > 15.0)
        & (lum < 0.76)
    )
    in_forearms = (
        (ny >= 0.798)
        & (ny <= 0.828)
        & (((nx >= 0.362) & (nx <= 0.412)) | ((nx >= 0.598) & (nx <= 0.642)))
        & (r > 122.0)
        & ((r - g) > 18.0)
        & (~is_rail_steel)
    )
    skin_raw = (in_left_ear | in_right_ear | in_neck | in_forearms) & (~hair_mask) & (~shirt_mask)
    neck_bridge = (ny >= 0.584) & (ny <= 0.638) & (nx >= 0.462) & (nx <= 0.534) & morph_dilate(in_neck, 4)
    skin_mask = smooth_binary_mask(morph_dilate(skin_raw | neck_bridge, 1), blur_radius=1.8, thresh=0.46)

    return hair_mask, shirt_mask, skin_mask


# WHY: Two-axis directional inpainting removes foreground railing and boy from Plane 1 so parallax shifts never reveal occluded bars.
def build_meadow_plane(arr_work, subject_mask_work, sunflowers_bias=(0.0, 0.0)):
    h, w, _ = arr_work.shape
    yy, xx = np.mgrid[0:h, 0:w]
    nx = -0.03 + 1.06 * (xx + 0.5) / float(w)
    ny = -0.03 + 1.06 * (yy + 0.5) / float(h)

    r = arr_work[:, :, 0]
    g = arr_work[:, :, 1]
    b = arr_work[:, :, 2]

    in_top_rail = (ny >= 0.711) & (ny <= 0.758)
    in_mid_rail = (ny >= 0.817) & (ny <= 0.860)
    in_bot_rail = ny >= 0.948
    is_steel_bar = (ny >= 0.710) & (b >= g * 0.86) & (r < g * 0.96)
    is_right_post = (ny >= 0.748) & (nx >= 0.916) & (nx <= 0.985) & (b >= g * 0.82)

    subj_dil = morph_dilate(subject_mask_work, 4)
    vert_bars_mask = morph_dilate((is_steel_bar | is_right_post) & (~in_top_rail) & (~in_mid_rail) & (~in_bot_rail), 2)
    horiz_rails_mask = morph_dilate(in_top_rail | in_mid_rail | in_bot_rail, 1)

    meadow = arr_work.copy()
    for y in range(int(h * 0.68), h):
        occ = vert_bars_mask[y] | subj_dil[y]
        if np.any(occ) and not np.all(occ):
            valid_x = np.where(~occ)[0]
            occ_x = np.where(occ)[0]
            for ch in range(3):
                meadow[y, occ_x, ch] = np.interp(occ_x, valid_x, meadow[y, valid_x, ch])

    for x in range(w):
        occ_y_mask = horiz_rails_mask[:, x] & (ny[:, x] >= 0.700)
        if np.any(occ_y_mask):
            valid_y = np.where((~occ_y_mask) & (ny[:, x] >= 0.53) & (~subj_dil[:, x]))[0]
            if len(valid_y) >= 2:
                occ_y = np.where(occ_y_mask)[0]
                for ch in range(3):
                    meadow[occ_y, x, ch] = np.interp(occ_y, valid_y, meadow[valid_y, x, ch])

    for y in range(int(h * 0.46), h):
        occ = subj_dil[y]
        if np.any(occ) and not np.all(occ):
            valid_x = np.where(~occ)[0]
            occ_x = np.where(occ)[0]
            for ch in range(3):
                meadow[y, occ_x, ch] = np.interp(occ_x, valid_x, meadow[y, valid_x, ch])

    meadow_sm = bilateral_smooth(meadow, spatial_sigma=1.9, range_sigma=17.0, radius=2, passes=2)

    mr = meadow_sm[:, :, 0]
    mg = meadow_sm[:, :, 1]
    mb = meadow_sm[:, :, 2]
    mlum = (0.299 * mr + 0.587 * mg + 0.114 * mb) / 255.0
    mean_c = (mr + mg + mb) / 3.0

    gr = mean_c + (mr - mean_c) * 1.24 + 2.0
    gg = mean_c + (mg - mean_c) * 1.26 + 5.0
    gb = mean_c + (mb - mean_c) * 1.18

    yellow_armor = smooth_up(18.0, 56.0, 0.5 * (mr + mg) - mb) * smooth_up(118.0, 175.0, mr) * smooth_up(118.0, 175.0, mg)
    plum_ribbon = smooth_up(2.0, 26.0, mr - mg * 1.00) * smooth_up(48.0, 118.0, mr) * (1.0 - yellow_armor)
    dark_mural = (1.0 - smooth_up(0.24, 0.46, mlum)) * (1.0 - plum_ribbon * 0.55) * smooth_up(0.53, 0.56, ny)

    gr = gr + yellow_armor * (16.0 + sunflowers_bias[0]) + plum_ribbon * 18.0 - dark_mural * 18.0
    gg = gg + yellow_armor * (12.0 + sunflowers_bias[1]) - plum_ribbon * 10.0 - dark_mural * 12.0
    gb = gb - yellow_armor * 18.0 + plum_ribbon * 14.0 - dark_mural * 8.0

    hy = 0.506 + 0.008 * np.sin(np.clip(nx, 0, 1) * 10.2 + 0.35) - 0.006 * np.cos(np.clip(nx, 0, 1) * 17.5 - 0.6)
    haze = (1.0 - smooth_up(hy + 0.002, hy + 0.024, ny)) * smooth_up(hy - 0.01, hy + 0.005, ny)
    ridge_wave = 0.5 + 0.5 * np.sin(nx * 38.0 + ny * 60.0)
    gr = gr * (1.0 - haze * 0.76) + (20.0 + 24.0 * ridge_wave) * (haze * 0.76)
    gg = gg * (1.0 - haze * 0.76) + (48.0 + 48.0 * ridge_wave) * (haze * 0.76)
    gb = gb * (1.0 - haze * 0.76) + (82.0 + 58.0 * ridge_wave) * (haze * 0.76)

    styled_meadow = np.clip(np.stack([gr, gg, gb], axis=-1), 0.0, 255.0)
    return meadow, styled_meadow, hy, yellow_armor, plum_ribbon, dark_mural


def build_meadow_mural_accents(raw_inpainted_meadow, nx_w, ny_w, x0_map, y0_map, sx_w, sy_w):
    lum = (
        0.299 * raw_inpainted_meadow[:, :, 0]
        + 0.587 * raw_inpainted_meadow[:, :, 1]
        + 0.114 * raw_inpainted_meadow[:, :, 2]
    ) / 255.0
    blur_lum = np.asarray(
        Image.fromarray(np.clip(lum * 255.0, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(radius=4.2)),
        dtype=np.float32,
    ) / 255.0
    ldiff = lum - blur_lum

    in_guanyu = (nx_w >= 0.01) & (nx_w <= 0.455) & (ny_w >= 0.552) & (ny_w <= 0.945)
    in_ribbon = (nx_w >= 0.525) & (nx_w <= 0.99) & (ny_w >= 0.552) & (ny_w <= 0.945)

    dark_lines = in_guanyu & (ldiff < -0.052) & (lum < 0.49)
    gold_glints = in_guanyu & (ldiff > 0.058) & (lum > 0.62) & (raw_inpainted_meadow[:, :, 0] > raw_inpainted_meadow[:, :, 2] + 28.0)
    plum_edges = in_ribbon & (ldiff < -0.048) & (raw_inpainted_meadow[:, :, 0] > raw_inpainted_meadow[:, :, 1] * 0.96)

    accents = []
    for mask_a, col_hex, op_a in (
        (dark_lines, "#243f29", 0.86),
        (gold_glints, "#f5ea76", 0.84),
        (plum_edges, "#572439", 0.80),
    ):
        d_s = mask_to_svg_d(mask_a, x0_map, y0_map, sx_w, sy_w, min_pts=11, taubin_iters=2, rdp_eps=1.95)
        if d_s:
            accents.append({"plane": 1, "fill": col_hex, "opacity": op_a, "rule": "evenodd", "d": d_s})
    return accents


def build_sky_plane(w, h, starry_path=None, provence_path=None):
    yy, xx = np.mgrid[0:h, 0:w]
    nx = -0.03 + 1.06 * (xx + 0.5) / float(w)
    ny = -0.03 + 1.06 * (yy + 0.5) / float(h)
    hy = 0.506 + 0.008 * np.sin(np.clip(nx, 0, 1) * 10.2 + 0.35) - 0.006 * np.cos(np.clip(nx, 0, 1) * 17.5 - 0.6)

    if starry_path and os.path.exists(starry_path):
        starry_im = Image.open(starry_path).convert("RGB")
        starry_im = ImageEnhance.Contrast(starry_im).enhance(1.18)
        starry_im = ImageEnhance.Color(starry_im).enhance(1.24)
        s_arr = np.asarray(starry_im.resize((w, h), Image.Resampling.LANCZOS), dtype=np.float32)

        prov_tint = 0.0
        if provence_path and os.path.exists(provence_path):
            p_im = Image.open(provence_path).convert("RGB").resize((64, 64), Image.Resampling.BILINEAR)
            prov_tint = float(np.asarray(p_im, dtype=np.float32)[:24, :, 2].mean()) * 0.02

        dome_t = np.clip((ny - 0.01) / np.maximum(0.15, hy + 0.01), 0.0, 1.0)
        su = np.clip(0.515 + (nx - 0.485) * (1.08 - 0.06 * dome_t), 0.01, 0.99)
        sv = np.clip(0.01 + dome_t * 0.72, 0.01, 0.75)

        sx_i = np.clip((su * (w - 1)).astype(np.int32), 0, w - 1)
        sy_i = np.clip((sv * (h - 1)).astype(np.int32), 0, h - 1)
        sky_rgb = s_arr[sy_i, sx_i].copy()

        sr, sg, sb = sky_rgb[:, :, 0], sky_rgb[:, :, 1], sky_rgb[:, :, 2]
        slum = (0.299 * sr + 0.587 * sg + 0.114 * sb) / 255.0
        warm = np.clip((sr - sb * 0.75) / 108.0, 0.0, 1.0)
        cool = np.clip((sb - sr * 0.80) / 105.0, 0.0, 1.0)
        in_cyp = (su >= 0.09) & (su <= 0.265) & (slum < 0.28) & (sr < 104.0) & (sb < 108.0)

        nr = sr * (0.86 + 0.38 * warm) + 10.0 * warm
        ng = sg * (0.96 + 0.26 * warm + 0.10 * cool) + 8.0 * warm + 6.0 * cool
        nb = sb * (1.08 + 0.18 * cool - 0.08 * warm) + 18.0 * (1.0 - warm) + prov_tint

        flame = 0.5 + 0.5 * np.sin(nx * 110.0 + ny * 46.0)
        nr = np.where(in_cyp, sr * 0.80 + 12.0 + flame * 26.0, nr)
        ng = np.where(in_cyp, sg * 1.24 + 22.0 + flame * 44.0, ng)
        nb = np.where(in_cyp, sb * 1.05 + 20.0 + flame * 30.0, nb)
        sky_styled = np.clip(np.stack([nr, ng, nb], axis=-1), 0.0, 255.0)
    else:
        swirl = 0.5 + 0.5 * np.sin(nx * 14.0 + ny * 9.0)
        sky_styled = np.stack([20.0 + 44.0 * swirl, 46.0 + 84.0 * swirl, 108.0 + 96.0 * swirl], axis=-1)
        in_cyp = np.zeros((h, w), dtype=bool)

    sky_sm = bilateral_smooth(sky_styled, spatial_sigma=2.2, range_sigma=24.0, radius=2, passes=2)
    return sky_sm, hy, in_cyp


def build_railing_polys():
    batches = {}

    def add_quad(col, pts, op=1.0):
        key = (col, round(op, 2))
        x0, y0 = int(round(pts[0][0])), int(round(pts[0][1]))
        x1, y1 = int(round(pts[1][0])), int(round(pts[1][1]))
        x2, y2 = int(round(pts[2][0])), int(round(pts[2][1]))
        x3, y3 = int(round(pts[3][0])), int(round(pts[3][1]))
        seg = "M%d,%dl%d,%dl%d,%dl%d,%dz" % (x0, y0, x1 - x0, y1 - y0, x2 - x1, y2 - y1, x3 - x2, y3 - y2)
        batches.setdefault(key, []).append(seg)

    vp_x, vp_y = 1000.0, -2300.0
    y_b0, y_b1 = 1498.0, 1916.0
    bar_centers_top = [-6.0 + i * 124.2 for i in range(15)]

    for xc_top in bar_centers_top:
        slope = (xc_top - vp_x) / (1530.0 - vp_y)
        x_top = vp_x + slope * (y_b0 - vp_y)
        x_bot = vp_x + slope * (y_b1 - vp_y)
        hw_t, hw_b = 11.5, 12.6
        add_quad("#234154", [(x_top - hw_t, y_b0), (x_top + hw_t, y_b0), (x_bot + hw_b, y_b1), (x_bot - hw_b, y_b1)])
        add_quad("#4b7791", [(x_top - hw_t * 0.55, y_b0), (x_top + hw_t * 0.72, y_b0), (x_bot + hw_b * 0.72, y_b1), (x_bot - hw_b * 0.55, y_b1)])
        add_quad("#bae6fd", [(x_top - hw_t * 0.14, y_b0), (x_top + hw_t * 0.28, y_b0), (x_bot + hw_b * 0.28, y_b1), (x_bot - hw_b * 0.14, y_b1)])
        for sy0, sy1 in ((1502.0, 1524.0), (1704.0, 1726.0)):
            sx0 = vp_x + slope * (sy0 - vp_y)
            sx1 = vp_x + slope * (sy1 - vp_y)
            add_quad("#162c3b", [(sx0 - hw_t, sy0), (sx0 + hw_t, sy0), (sx1 + hw_t, sy1), (sx1 - hw_t, sy1)])

    p_tl, p_tr = 1860.0, 1948.0
    p_bl, p_br = 1843.0, 1931.0
    add_quad("#203c4f", [(p_tl, 1496.0), (p_tr, 1496.0), (p_br, 1924.0), (p_bl, 1924.0)])
    add_quad("#3e6882", [(p_tl + 10.0, 1496.0), (p_tr - 14.0, 1496.0), (p_br - 14.0, 1924.0), (p_bl + 10.0, 1924.0)])
    add_quad("#8cc0db", [(p_tl + 4.0, 1496.0), (p_tl + 18.0, 1496.0), (p_bl + 18.0, 1924.0), (p_bl + 4.0, 1924.0)])
    add_quad("#162c3b", [(p_tl, 1500.0), (p_tr, 1500.0), (p_tr - 1.0, 1528.0), (p_tl - 1.0, 1528.0)])
    add_quad("#162c3b", [(p_tl - 8.0, 1704.0), (p_tr - 8.0, 1704.0), (p_tr - 9.0, 1730.0), (p_tl - 9.0, 1730.0)])

    xl, xr = -64.0, 2064.0
    add_quad("#1d384a", [(xl, 1906.0), (xr, 1906.0), (xr, 2060.0), (xl, 2060.0)])
    add_quad("#48738c", [(xl, 1910.0), (xr, 1910.0), (xr, 1932.0), (xl, 1932.0)])
    add_quad("#d8f0fc", [(xl, 1940.0), (xr, 1940.0), (xr, 1950.0), (xl, 1950.0)])
    add_quad("#79a7bf", [(xl, 1950.0), (xr, 1950.0), (xr, 1964.0), (xl, 1964.0)])
    for gy in (1972.0, 1988.0, 2004.0):
        add_quad("#94bfd6", [(xl, gy), (xr, gy), (xr, gy + 5.0), (xl, gy + 5.0)])
    for gi in range(-2, 42):
        gx_t = gi * 51.0
        gx_b = vp_x + (gx_t - vp_x) * 1.03
        add_quad("#294a5e", [(gx_t, 1948.0), (gx_t + 6.5, 1948.0), (gx_b + 7.0, 2052.0), (gx_b, 2052.0)])

    for y0, y1, bcol in (
        (1640.0, 1649.0, "#bae6fd"),
        (1649.0, 1660.0, "#f0f9ff"),
        (1660.0, 1673.0, "#87b5cf"),
        (1673.0, 1687.0, "#4c7891"),
        (1687.0, 1700.0, "#26485e"),
        (1700.0, 1709.0, "#3a6375"),
    ):
        add_quad(bcol, [(xl, y0), (xr, y0), (xr, y1), (xl, y1)])

    for y0, y1, bcol in (
        (1428.0, 1449.0, "#e0f2fe"),
        (1428.0, 1442.0, "#f8fafc"),
        (1449.0, 1456.0, "#bae6fd"),
        (1456.0, 1471.0, "#55829c"),
        (1471.0, 1491.0, "#3e6882"),
        (1491.0, 1502.0, "#2c5066"),
        (1502.0, 1509.0, "#193345"),
    ):
        add_quad(bcol, [(xl, y0), (xr, y0), (xr, y1), (xl, y1)])

    return [
        {"plane": 2, "fill": col, "opacity": op, "rule": "nonzero", "d": "".join(segs)}
        for (col, op), segs in batches.items()
    ]


def build_flow_strokes(
    rgb_arr,
    valid_mask,
    plane_idx,
    x0_map,
    y0_map,
    sx_scale,
    sy_scale,
    step=6,
    max_strokes=720,
    len_range=(28.0, 62.0),
    width_buckets=(5.0, 7.8),
    op_val=0.84,
    k_palette=16,
    grad_min=0.018,
    boost=1.08,
    weight_map=None,
    seed=11,
):
    h, w, _ = rgb_arr.shape
    lum = (0.299 * rgb_arr[:, :, 0] + 0.587 * rgb_arr[:, :, 1] + 0.114 * rgb_arr[:, :, 2]) / 255.0
    lum_sm = np.asarray(
        Image.fromarray(np.clip(lum * 255.0, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(radius=1.8)),
        dtype=np.float32,
    ) / 255.0

    gx = np.zeros_like(lum_sm)
    gy = np.zeros_like(lum_sm)
    gx[:, 1:-1] = (lum_sm[:, 2:] - lum_sm[:, :-2]) * 0.5
    gy[1:-1, :] = (lum_sm[2:, :] - lum_sm[:-2, :]) * 0.5
    mag = np.hypot(gx, gy)

    def blur_f(arr_f, rad=3.0):
        lo, hi = float(arr_f.min()), float(arr_f.max())
        if hi - lo < 1e-9:
            return arr_f
        u8 = np.clip((arr_f - lo) / (hi - lo) * 255.0, 0, 255).astype(np.uint8)
        sm = np.asarray(Image.fromarray(u8).filter(ImageFilter.GaussianBlur(radius=rad)), dtype=np.float32)
        return lo + (sm / 255.0) * (hi - lo)

    jxx = blur_f(gx * gx, 3.0)
    jxy = blur_f(gx * gy, 3.0)
    jyy = blur_f(gy * gy, 3.0)
    theta_grad = 0.5 * np.arctan2(2.0 * jxy, jxx - jyy)
    tx_map = -np.sin(theta_grad)
    ty_map = np.cos(theta_grad)

    rng = np.random.default_rng(seed)
    cands = []
    for y in range(step // 2 + 2, h - 3, step):
        for x in range(step // 2 + 2, w - 3, step):
            jx = min(w - 3, max(2, x + int(rng.integers(-1, 2))))
            jy = min(h - 3, max(2, y + int(rng.integers(-1, 2))))
            if not valid_mask[jy, jx]:
                continue
            ux = x0_map + jx * sx_scale
            uy = y0_map + jy * sy_scale
            if (ux - 1000.0) ** 2 + (uy - 1000.0) ** 2 > 1064.0 ** 2:
                continue
            gm = float(mag[jy, jx])
            lv = float(lum[jy, jx])
            imp = float(weight_map[jy, jx]) if weight_map is not None else 1.0
            if gm * imp < grad_min and lv < 0.62:
                continue
            tx, ty = float(tx_map[jy, jx]), float(ty_map[jy, jx])
            span = len_range[0] + (len_range[1] - len_range[0]) * min(1.0, gm * 7.5 + lv * 0.25)
            half = span * 0.5
            dx_px = tx * (half / sx_scale)
            dy_px = ty * (half / sy_scale)
            x_f = int(np.clip(round(jx + dx_px), 1, w - 2))
            y_f = int(np.clip(round(jy + dy_px), 1, h - 2))
            x_b = int(np.clip(round(jx - dx_px), 1, w - 2))
            y_b = int(np.clip(round(jy - dy_px), 1, h - 2))
            if not (valid_mask[y_f, x_f] and valid_mask[y_b, x_b]):
                continue
            tfx, tfy = float(tx_map[y_f, x_f]), float(ty_map[y_f, x_f])
            if tfx * tx + tfy * ty < 0.0:
                tfx, tfy = -tfx, -tfy
            tbx, tby = float(tx_map[y_b, x_b]), float(ty_map[y_b, x_b])
            if tbx * tx + tby * ty < 0.0:
                tbx, tby = -tbx, -tby

            p0x = int(round(ux - 0.5 * (tx + tbx) * half))
            p0y = int(round(uy - 0.5 * (ty + tby) * half))
            p1x = int(round(ux + 0.5 * (tx + tfx) * half))
            p1y = int(round(uy + 0.5 * (ty + tfy) * half))
            bend = (0.13 * span) * (1.0 if ((jx + jy) % 2 == 0) else -1.0) * min(1.0, gm * 8.0 + 0.25)
            cx_u = int(round(ux - ty * bend))
            cy_u = int(round(uy + tx * bend))

            col = np.clip(rgb_arr[jy, jx] * boost + (8.0 if lv > 0.55 else 2.0), 0.0, 255.0)
            wb = width_buckets[0] if (gm > 0.070 or lv > 0.68) else width_buckets[-1]
            score = (gm * 2.2 + lv * 0.42) * imp
            cands.append((score, col, wb, (p0x, p0y, cx_u - p0x, cy_u - p0y, p1x - p0x, p1y - p0y)))

    cands.sort(key=lambda item: item[0], reverse=True)
    picked = cands[:max_strokes]
    if not picked:
        return []

    cols_np = np.array([it[1] for it in picked], dtype=np.float32)
    centers, assign = weighted_kmeans_rgb(cols_np, np.ones(len(picked), dtype=np.float32), k=min(k_palette, len(picked)), iters=11, seed=seed)

    grouped = {}
    for idx_s, (_, _, wb, (x0, y0, qdx1, qdy1, qdx, qdy)) in enumerate(picked):
        ci = int(assign[idx_s])
        chex = rgb_hex(centers[ci, 0], centers[ci, 1], centers[ci, 2])
        key = (chex, round(float(wb), 1))
        grouped.setdefault(key, []).append("M%d,%dq%d,%d %d,%d" % (x0, y0, qdx1, qdy1, qdx, qdy))

    return [
        {"plane": plane_idx, "stroke": chex, "width": wb, "opacity": round(op_val, 2), "cap": "round", "d": "".join(segs)}
        for (chex, wb), segs in grouped.items()
    ]


def build_sky_celestial_accents(sky_rgb, hy_grid, in_cyp, x0_map, y0_map, sx_scale, sy_scale):
    polys = []
    strokes = []

    mcx, mcy = 1658, 292
    for rad, col, op in ((124, "#fde047", 0.14), (90, "#fef08a", 0.20)):
        d_circ = "M%d,%da%d,%d 0 1,0 %d,0a%d,%d 0 1,0 -%d,0z" % (mcx - rad, mcy, rad, rad, 2 * rad, rad, rad, 2 * rad)
        polys.append({"plane": 0, "fill": col, "opacity": op, "rule": "nonzero", "d": d_circ})

    crescent_d = "M%d,%dA42,42 0 1,1 %d,%dA33,35 0 1,0 %d,%dZ" % (mcx + 12, mcy - 39, mcx - 20, mcy + 36, mcx + 12, mcy - 39)
    polys.append({"plane": 0, "fill": "#f59e0b", "opacity": 0.88, "rule": "nonzero", "d": crescent_d})

    ring_gold, ring_ivory = [], []
    rng = np.random.default_rng(73)
    halo_centers = [(mcx, mcy, 62, 134, 18), (695, 745, 36, 86, 12), (465, 255, 28, 62, 10), (1215, 140, 28, 64, 10)]
    for hcx, hcy, r_in, r_out, n_arcs in halo_centers:
        for ai in range(n_arcs):
            rr = float(rng.uniform(r_in, r_out))
            a0 = (ai / float(n_arcs)) * math.tau + float(rng.uniform(-0.18, 0.18))
            da = float(rng.uniform(0.32, 0.56))
            a1 = a0 + da
            am = 0.5 * (a0 + a1)
            rm = rr / math.cos(da * 0.5)
            x0, y0 = int(round(hcx + math.cos(a0) * rr)), int(round(hcy + math.sin(a0) * rr))
            xm, ym = int(round(hcx + math.cos(am) * rm)), int(round(hcy + math.sin(am) * rm))
            x1, y1 = int(round(hcx + math.cos(a1) * rr)), int(round(hcy + math.sin(a1) * rr))
            seg = "M%d,%dq%d,%d %d,%d" % (x0, y0, xm - x0, ym - y0, x1 - x0, y1 - y0)
            if ai % 2 == 0:
                ring_gold.append(seg)
            else:
                ring_ivory.append(seg)
    strokes.append({"plane": 0, "stroke": "#fde047", "width": 4.8, "opacity": 0.86, "cap": "round", "d": "".join(ring_gold)})
    strokes.append({"plane": 0, "stroke": "#fef9c3", "width": 3.8, "opacity": 0.88, "cap": "round", "d": "".join(ring_ivory)})

    h, w, _ = sky_rgb.shape
    lum = (0.299 * sky_rgb[:, :, 0] + 0.587 * sky_rgb[:, :, 1] + 0.114 * sky_rgb[:, :, 2]) / 255.0
    used = [(mcx, mcy)]
    sp_ivory, sp_gold, sp_cyan = [], [], []

    for y in range(12, int(h * 0.48), 5):
        for x in range(12, w - 12, 5):
            ux = x0_map + x * sx_scale
            uy = y0_map + y * sy_scale
            if (ux - 1000.0) ** 2 + (uy - 1000.0) ** 2 > 930.0 ** 2:
                continue
            if uy > (hy_grid[y, x] * 2000.0 - 76.0) or in_cyp[y, x]:
                continue
            if ((ux - 990.0) / 175.0) ** 2 + ((uy - 1050.0) / 180.0) ** 2 < 1.15:
                continue
            lv = float(lum[y, x])
            if lv < 0.60:
                continue
            if any((ux - px) ** 2 + (uy - py) ** 2 < 74.0 ** 2 for px, py in used):
                continue
            used.append((ux, uy))
            ro = int(round(7.5 + min(7.0, (lv - 0.58) * 20.0)))
            ri = max(2, int(round(ro * 0.30)))
            ix, iy = int(round(ux)), int(round(uy))
            sd = "M%d,%dl%d,%dl%d,%dl%d,%dl%d,%dl%d,%dl%d,%dl%d,%dz" % (
                ix, iy - ro,
                ri, ro - ri,
                ro - ri, ri,
                -(ro - ri), ri,
                -ri, ro - ri,
                -ri, -(ro - ri),
                -(ro - ri), -ri,
                ro - ri, -ri,
            )
            rc, _, bc = sky_rgb[y, x]
            if rc > bc * 0.95 and lv > 0.74:
                sp_ivory.append((lv, sd))
            elif rc > bc * 0.85:
                sp_gold.append((lv, sd))
            else:
                sp_cyan.append((lv, sd))

    picked = (
        [("ivory", d) for _, d in sorted(sp_ivory, reverse=True)[:24]]
        + [("gold", d) for _, d in sorted(sp_gold, reverse=True)[:24]]
        + [("cyan", d) for _, d in sorted(sp_cyan, reverse=True)[:20]]
    )[:68]

    buckets = {"ivory": [], "gold": [], "cyan": []}
    for k, d in picked:
        buckets[k].append(d)
    for k, col, op in (("gold", "#fde047", 0.92), ("cyan", "#bae6fd", 0.86), ("ivory", "#fffbeb", 0.96)):
        if buckets[k]:
            polys.append({"plane": 0, "fill": col, "opacity": op, "rule": "nonzero", "d": "".join(buckets[k])})

    return polys, strokes


def build_subject_plane(arr_hi, hair_mask, shirt_mask, skin_mask):
    h, w, _ = arr_hi.shape
    pad_b = int(round(h * 0.032))
    arr_ext = np.pad(arr_hi, ((0, pad_b), (0, 0), (0, 0)), mode="edge")
    hair_ext = np.pad(hair_mask, ((0, pad_b), (0, 0)), mode="constant", constant_values=False)
    shirt_ext = np.pad(shirt_mask, ((0, pad_b), (0, 0)), mode="edge")
    skin_ext = np.pad(skin_mask, ((0, pad_b), (0, 0)), mode="constant", constant_values=False)

    he, we, _ = arr_ext.shape
    sx_s = float(COORD_SZ) / float(w)
    sy_s = float(COORD_SZ) / float(h)

    skin_under_hi = morph_dilate(skin_ext, 4) & (hair_ext | shirt_ext | skin_ext)
    skin_base_d = mask_to_svg_d(skin_under_hi, 0.0, 0.0, sx_s, sy_s, min_pts=6, taubin_iters=4, rdp_eps=0.9)
    shirt_base_d = mask_to_svg_d(shirt_ext, 0.0, 0.0, sx_s, sy_s, min_pts=8, taubin_iters=4, rdp_eps=0.9)
    hair_base_d = mask_to_svg_d(hair_ext, 0.0, 0.0, sx_s, sy_s, min_pts=8, taubin_iters=4, rdp_eps=0.85)

    sh_h2, sh_w2 = he // 2, we // 2
    arr_h = arr_ext[::2, ::2][:sh_h2, :sh_w2]
    hair_mask_h = hair_ext[::2, ::2][:sh_h2, :sh_w2]
    shirt_mask_h = shirt_ext[::2, ::2][:sh_h2, :sh_w2]
    skin_mask_h = skin_ext[::2, ::2][:sh_h2, :sh_w2]
    skin_under_h = skin_under_hi[::2, ::2][:sh_h2, :sh_w2]

    yy_h, xx_h = np.mgrid[0:sh_h2, 0:sh_w2]
    nx_h = (xx_h + 0.5) / float(w // 2)
    ny_h = (yy_h + 0.5) / float(h // 2)

    subject_polys = []
    subject_strokes = []

    skin_rgb_ext = extrapolate_masked_rgb(arr_h, skin_mask_h, iterations=10)
    skin_sm = bilateral_smooth(skin_rgb_ext, spatial_sigma=1.8, range_sigma=18.0, radius=2, passes=2)
    skr = np.clip(skin_sm[:, :, 0] * 1.05 + 14.0, 145.0, 246.0)
    skg = np.clip(skin_sm[:, :, 1] * 0.96 + 10.0, 98.0, 206.0)
    skb = np.clip(skin_sm[:, :, 2] * 0.88 + 10.0, 84.0, 184.0)
    skin_styled = np.stack([skr, skg, skb], axis=-1)

    subject_polys.extend(
        cluster_region_to_polys(
            skin_styled,
            skin_under_h,
            np.ones((sh_h2, sh_w2), dtype=np.float32),
            k_colors=7,
            plane_idx=3,
            x0_map=0.0,
            y0_map=0.0,
            sx_scale=sx_s * 2.0,
            sy_scale=sy_s * 2.0,
            mode_passes=1,
            min_loop_pts=6,
            taubin_iters=4,
            rdp_eps=1.1,
            seam_stroke=1.5,
            base_fill_hex="#d48973",
            clip_base_d=skin_base_d,
            inner_mask=morph_erode(skin_under_h, 1),
            seed=21,
        )
    )

    shirt_rgb_ext = extrapolate_masked_rgb(arr_h, shirt_mask_h, iterations=10)
    shirt_sm = bilateral_smooth(shirt_rgb_ext, spatial_sigma=2.0, range_sigma=18.0, radius=2, passes=2)
    sr, sg, sb = shirt_sm[:, :, 0], shirt_sm[:, :, 1], shirt_sm[:, :, 2]

    blur_sh = np.asarray(
        Image.fromarray(np.clip(shirt_sm, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(radius=5.0)),
        dtype=np.float32,
    )
    fold_diff = np.clip(
        (0.299 * (sr - blur_sh[:, :, 0]) + 0.587 * (sg - blur_sh[:, :, 1]) + 0.114 * (sb - blur_sh[:, :, 2])) / 255.0,
        -0.14,
        0.16,
    )

    collar_hi = np.exp(-(((ny_h - 0.626) / 0.011) ** 2)) * (1.0 - smooth_up(0.032, 0.056, np.abs(nx_h - 0.500))) * 14.0
    yoke_seam = np.exp(-(((ny_h - 0.684) / 0.008) ** 2)) * (1.0 - smooth_up(0.065, 0.115, np.abs(nx_h - 0.502))) * 11.0
    moon_rim = smooth_up(0.055, 0.145, nx_h - 0.500) * (1.0 - smooth_up(0.64, 0.84, ny_h)) * 15.0

    cr = np.clip(sr * 1.04 + 8.0 + fold_diff * 95.0 + collar_hi + yoke_seam + moon_rim, 134.0, 252.0)
    cg = np.clip(sg * 0.94 + 6.0 + fold_diff * 66.0 + (collar_hi + yoke_seam + moon_rim) * 0.78, 50.0, 178.0)
    cb = np.clip(sb * 0.94 + 8.0 + fold_diff * 68.0 + (collar_hi + yoke_seam + moon_rim) * 0.72, 64.0, 188.0)
    cg = np.minimum(cg, cr * 0.72)
    cb = np.clip(cb, cg * 1.02, cr * 0.78)
    shirt_styled_h = np.stack([cr, cg, cb], axis=-1)

    sh_weights = np.ones((sh_h2, sh_w2), dtype=np.float32) + np.where((ny_h >= 0.618) & (ny_h <= 0.705), 1.8, 0.0)

    subject_polys.extend(
        cluster_region_to_polys(
            shirt_styled_h,
            shirt_mask_h,
            sh_weights,
            k_colors=26,
            plane_idx=3,
            x0_map=0.0,
            y0_map=0.0,
            sx_scale=sx_s * 2.0,
            sy_scale=sy_s * 2.0,
            mode_passes=2,
            min_loop_pts=10,
            taubin_iters=4,
            rdp_eps=1.35,
            seam_stroke=1.7,
            base_fill_hex="#d4566a",
            clip_base_d=shirt_base_d,
            inner_mask=morph_erode(shirt_mask_h, 1),
            seed=33,
        )
    )

    shirt_strokes = build_flow_strokes(
        shirt_styled_h,
        morph_erode(shirt_mask_h, 3),
        plane_idx=3,
        x0_map=0.0,
        y0_map=0.0,
        sx_scale=sx_s * 2.0,
        sy_scale=sy_s * 2.0,
        step=8,
        max_strokes=110,
        len_range=(22.0, 44.0),
        width_buckets=(3.4, 4.8),
        op_val=0.46,
        k_palette=6,
        grad_min=0.018,
        boost=1.05,
        seed=77,
    )
    shirt_strokes.append({
        "plane": 3,
        "stroke": "#ffb8c3",
        "width": 3.2,
        "opacity": 0.62,
        "cap": "round",
        "d": "M916,1273q84,-9 172,2M776,1378q226,-19 456,4",
    })
    shirt_strokes.append({
        "plane": 3,
        "stroke": "#a8384e",
        "width": 2.8,
        "opacity": 0.44,
        "cap": "round",
        "d": "M914,1277q86,-9 176,2M778,1382q224,-19 452,4",
    })
    subject_strokes.extend(shirt_strokes)

    hair_rgb_ext = extrapolate_masked_rgb(arr_h, hair_mask_h, iterations=8)
    hair_sm = bilateral_smooth(hair_rgb_ext, spatial_sigma=1.6, range_sigma=16.0, radius=2, passes=2)
    hlum = (0.299 * hair_sm[:, :, 0] + 0.587 * hair_sm[:, :, 1] + 0.114 * hair_sm[:, :, 2]) / 255.0

    wdx = nx_h - 0.496
    wdy = (ny_h - 0.495) * 1.10
    wr = np.hypot(wdx, wdy)
    wth = np.arctan2(wdy, wdx)
    lock_wave = 0.62 * (0.5 + 0.5 * np.sin(wth * 12.0 + wr * 42.0)) + 0.38 * (0.5 + 0.5 * np.cos(wth * 21.0 - wr * 26.0))
    radial_h = np.hypot((nx_h - 0.4945) / 0.064, (ny_h - 0.533) / 0.072)
    top_crown_only = 1.0 - smooth_up(0.468, 0.542, ny_h)
    nape_shadow = smooth_up(0.555, 0.605, ny_h)
    crown_rim = smooth_up(0.54, 0.98, radial_h) * top_crown_only
    moon_side = smooth_up(-0.20, 0.75, (nx_h - 0.495) / 0.064)
    part_glow = np.exp(-((wr / 0.022) ** 2)) * 0.28

    s_boost = np.clip((np.minimum(0.26, hlum) * 2.5 + lock_wave * 0.26 + part_glow) * (1.0 - 0.55 * nape_shadow), 0.0, 1.0)
    hr_c = 6.0 + s_boost * 22.0 + crown_rim * (20.0 + 28.0 * moon_side)
    hg_c = 11.0 + s_boost * 38.0 + crown_rim * (42.0 + 26.0 * moon_side)
    hb_c = 22.0 + s_boost * 64.0 + crown_rim * (78.0 + 12.0 * moon_side)
    hair_styled_h = np.clip(np.stack([hr_c, hg_c, hb_c], axis=-1), 0.0, 255.0)

    subject_polys.extend(
        cluster_region_to_polys(
            hair_styled_h,
            hair_mask_h,
            np.ones((sh_h2, sh_w2), dtype=np.float32),
            k_colors=12,
            plane_idx=3,
            x0_map=0.0,
            y0_map=0.0,
            sx_scale=sx_s * 2.0,
            sy_scale=sy_s * 2.0,
            mode_passes=1,
            min_loop_pts=8,
            taubin_iters=3,
            rdp_eps=1.1,
            seam_stroke=1.5,
            base_fill_hex="#081020",
            clip_base_d=hair_base_d,
            inner_mask=morph_erode(hair_mask_h, 1),
            seed=55,
        )
    )

    whirl_cx, whirl_cy = 992.0, 992.0
    lock_segs_dark, lock_segs_mid, lock_segs_rim = [], [], []
    rng_h = np.random.default_rng(91)
    for i in range(68):
        ang = (i / 68.0) * math.tau + float(rng_h.uniform(-0.04, 0.04))
        r0 = float(rng_h.uniform(16.0, 64.0))
        r1 = r0 + float(rng_h.uniform(32.0, 56.0))
        ex0 = whirl_cx + math.cos(ang) * r0 * 0.92
        ey0 = whirl_cy + math.sin(ang) * r0 * 1.08 + 36.0
        swirl_a = ang + 0.28 * (1.0 if math.cos(ang) >= 0 else -0.8)
        ex1 = whirl_cx + math.cos(swirl_a) * r1 * 0.95
        ey1 = whirl_cy + math.sin(swirl_a) * r1 * 1.12 + 44.0
        mx = 0.5 * (ex0 + ex1) - math.sin(ang) * 9.0
        my = 0.5 * (ey0 + ey1) + math.cos(ang) * 9.0
        ix = int(np.clip(round(ex1 / sx_s), 0, we - 1))
        iy = int(np.clip(round(ey1 / sy_s), 0, he - 1))
        if not hair_ext[iy, ix]:
            continue
        x0_i, y0_i = int(round(ex0)), int(round(ey0))
        seg = "M%d,%dq%d,%d %d,%d" % (
            x0_i, y0_i,
            int(round(mx)) - x0_i, int(round(my)) - y0_i,
            int(round(ex1)) - x0_i, int(round(ey1)) - y0_i,
        )
        if ey1 < 1045.0 and r1 > 80.0:
            lock_segs_rim.append(seg)
        elif i % 2 == 0:
            lock_segs_mid.append(seg)
        else:
            lock_segs_dark.append(seg)

    wisp_d = "M986,946q-10,-21 -23,-18M994,944q3,-23 17,-19M1002,948q14,-19 28,-12M976,950q-16,-15 -30,-5"
    if lock_segs_dark:
        subject_strokes.append({"plane": 3, "stroke": "#060c19", "width": 3.8, "opacity": 0.76, "cap": "round", "d": "".join(lock_segs_dark)})
    if lock_segs_mid:
        subject_strokes.append({"plane": 3, "stroke": "#1f3a66", "width": 3.2, "opacity": 0.58, "cap": "round", "d": "".join(lock_segs_mid)})
    if lock_segs_rim:
        subject_strokes.append({"plane": 3, "stroke": "#5c8ec7", "width": 2.8, "opacity": 0.64, "cap": "round", "d": "".join(lock_segs_rim)})
    subject_strokes.append({"plane": 3, "stroke": "#142645", "width": 2.6, "opacity": 0.84, "cap": "round", "d": wisp_d})

    return subject_polys, subject_strokes


# WHY: Emits <320 pure-vector color-batched <path> elements with zero <image> or <tspan> tags for GitHub CSP and 60fps Skia caching.
def render_portrait_svg(portrait_hd, acx, acy, ar):
    diam = float(ar) * 2.0
    x_left = float(acx) - float(ar)
    y_top = float(acy) - float(ar)
    coord_sz = float((portrait_hd or {}).get("coord_size") or COORD_SZ)
    scale = diam / max(1.0, coord_sz)
    clip_id = "p4k-clip-%d-%d" % (int(round(acx)), int(round(acy)))
    bg_fill = (portrait_hd or {}).get("bg_fill") or "#081833"
    vl = (portrait_hd or {}).get("vector_layers") or {}

    parts = [
        '<clipPath id="%s"><circle cx="%.2f" cy="%.2f" r="%.2f"/></clipPath>' % (clip_id, acx, acy, ar),
        '<g clip-path="url(#%s)">' % clip_id,
        '<g transform="translate(%.2f %.2f) scale(%.6f)">' % (x_left, y_top, scale),
        '<path fill="%s" d="M-80,-80H2080V2080H-80Z"/>' % bg_fill,
    ]

    for lname, lkind in (
        ("sky_polys", "poly"),
        ("sky_strokes", "stroke"),
        ("meadow_polys", "poly"),
        ("meadow_strokes", "stroke"),
        ("rail_polys", "poly"),
        ("subject_polys", "poly"),
        ("subject_strokes", "stroke"),
    ):
        for it in vl.get(lname) or []:
            d = it.get("d") or ""
            if not d:
                continue
            if lkind == "poly":
                fill = it["fill"]
                op = float(it.get("opacity", 1.0))
                rule = it.get("rule") or "nonzero"
                seam = float(it.get("seam") or 0.0)
                attrs = ['fill="%s"' % fill]
                if op < 0.995:
                    attrs.append('fill-opacity="%.2f"' % op)
                if rule == "evenodd":
                    attrs.append('fill-rule="evenodd"')
                if seam > 0.0:
                    attrs.append('stroke="%s" stroke-width="%.1f" stroke-linejoin="round"' % (fill, seam))
                parts.append('<path %s d="%s"/>' % (" ".join(attrs), d))
            else:
                scol = it["stroke"]
                sw = float(it.get("width", 3.0))
                sop = float(it.get("opacity", 0.8))
                cap = it.get("cap") or "round"
                attrs = [
                    'fill="none"',
                    'stroke="%s"' % scol,
                    'stroke-width="%.1f"' % sw,
                    'stroke-linecap="%s"' % cap,
                    'stroke-linejoin="round"',
                ]
                if sop < 0.995:
                    attrs.append('stroke-opacity="%.2f"' % sop)
                parts.append('<path %s d="%s"/>' % (" ".join(attrs), d))

    parts.append("</g>")
    parts.append("</g>")
    return parts


def build_portrait(src_path, out_path, starry_path=None, sunflowers_path=None, provence_path=None):
    raw = Image.open(src_path).convert("RGB")
    size = min(raw.size)
    left = (raw.width - size) // 2
    top = (raw.height - size) // 2
    square = raw.crop((left, top, left + size, top + size))

    hi_im = square.resize((920, 920), Image.Resampling.LANCZOS)
    hi_sharp = ImageEnhance.Contrast(
        hi_im.filter(ImageFilter.UnsharpMask(radius=1.3, percent=135, threshold=2))
    ).enhance(1.08)
    arr_hi = np.asarray(hi_sharp, dtype=np.float32)

    hair_hi, shirt_hi, skin_hi = segment_subject_masks(arr_hi)
    subject_hi = hair_hi | shirt_hi | skin_hi

    sun_bias = (0.0, 0.0)
    if sunflowers_path and os.path.exists(sunflowers_path):
        sf_im = Image.open(sunflowers_path).convert("RGB").resize((64, 64), Image.Resampling.BILINEAR)
        sf_arr = np.asarray(sf_im, dtype=np.float32)
        sun_bias = (
            float(np.clip((sf_arr[:, :, 0].mean() - 180.0) * 0.06, 0.0, 4.0)),
            float(np.clip((sf_arr[:, :, 1].mean() - 150.0) * 0.05, 0.0, 3.0)),
        )

    gw, gh = 480, 480
    pad_px = max(1, int(round(square.width * 0.0304)))
    raw_np = np.asarray(square.resize((460, 460), Image.Resampling.LANCZOS), dtype=np.float32)
    raw_pad = np.pad(raw_np, ((14, 14), (14, 14), (0, 0)), mode="edge")
    work_im = Image.fromarray(raw_pad.astype(np.uint8)).resize((gw, gh), Image.Resampling.LANCZOS)
    work_im = ImageEnhance.Contrast(work_im.filter(ImageFilter.UnsharpMask(radius=1.15, percent=145, threshold=2))).enhance(1.12)
    arr_work = np.asarray(work_im, dtype=np.float32)

    subj_460 = subject_hi[::2, ::2]
    subj_pad = np.pad(subj_460, ((14, 14), (14, 14)), mode="edge")
    subj_work = np.asarray(
        Image.fromarray((subj_pad.astype(np.uint8) * 255)).resize((gw, gh), Image.Resampling.NEAREST),
        dtype=np.uint8,
    ) > 127

    x0_map = -60.87
    y0_map = -60.87
    sx_w = 2121.74 / float(gw)
    sy_w = 2121.74 / float(gh)

    sky_sm, hy_sky, in_cyp = build_sky_plane(gw, gh, starry_path, provence_path)
    yy_w, xx_w = np.mgrid[0:gh, 0:gw]
    ny_w = (y0_map + (yy_w + 0.5) * sy_w) / float(COORD_SZ)
    nx_w = (x0_map + (xx_w + 0.5) * sx_w) / float(COORD_SZ)
    sky_region = ny_w <= (hy_sky + 0.024)

    slum_w = (0.299 * sky_sm[:, :, 0] + 0.587 * sky_sm[:, :, 1] + 0.114 * sky_sm[:, :, 2]) / 255.0
    sky_weights = np.ones((gh, gw), dtype=np.float32) + np.where(slum_w > 0.62, 2.5, 0.0) + np.where(in_cyp, 2.0, 0.0)

    sky_polys = cluster_region_to_polys(
        sky_sm[::2, ::2],
        sky_region[::2, ::2],
        sky_weights[::2, ::2],
        k_colors=26,
        plane_idx=0,
        x0_map=x0_map,
        y0_map=y0_map,
        sx_scale=sx_w * 2.0,
        sy_scale=sy_w * 2.0,
        mode_passes=2,
        min_loop_pts=12,
        taubin_iters=3,
        rdp_eps=2.85,
        seam_stroke=2.8,
        base_fill_hex="#0c234a",
        clip_base_d="M-70,-70H2070V1110H-70Z",
        seed=12,
    )
    cel_polys, cel_strokes = build_sky_celestial_accents(sky_sm, hy_sky, in_cyp, x0_map, y0_map, sx_w, sy_w)
    sky_polys.extend(cel_polys)

    sky_strokes = build_flow_strokes(
        sky_sm,
        sky_region,
        plane_idx=0,
        x0_map=x0_map,
        y0_map=y0_map,
        sx_scale=sx_w,
        sy_scale=sy_w,
        step=7,
        max_strokes=700,
        len_range=(30.0, 62.0),
        width_buckets=(5.0, 7.8),
        op_val=0.84,
        k_palette=16,
        grad_min=0.018,
        boost=1.08,
        seed=19,
    )
    sky_strokes.extend(cel_strokes)

    raw_inpainted_meadow, styled_meadow, hy_m, yellow_armor, plum_ribbon, dark_mural = build_meadow_plane(
        arr_work, subj_work, sun_bias
    )
    meadow_region = ny_w >= (hy_m - 0.004)
    meadow_base_d = mask_to_svg_d(meadow_region, x0_map, y0_map, sx_w, sy_w, min_pts=8, taubin_iters=4, rdp_eps=1.4)

    m_weights = np.ones((gh, gw), dtype=np.float32)
    in_guanyu = (nx_w >= -0.02) & (nx_w <= 0.47) & (ny_w >= 0.535) & (ny_w <= 0.955)
    in_ribbon = (nx_w >= 0.52) & (nx_w <= 1.02) & (ny_w >= 0.535) & (ny_w <= 0.955)
    m_weights += np.where(in_guanyu, 3.0 + 4.5 * yellow_armor + 4.0 * dark_mural, 0.0)
    m_weights += np.where(in_ribbon, 2.0 + 4.2 * plum_ribbon, 0.0)

    mg_w, mg_h = 296, 296
    meadow_g = np.asarray(
        Image.fromarray(styled_meadow.astype(np.uint8)).resize((mg_w, mg_h), Image.Resampling.LANCZOS),
        dtype=np.float32,
    )
    mreg_g = np.asarray(
        Image.fromarray((meadow_region.astype(np.uint8) * 255)).resize((mg_w, mg_h), Image.Resampling.NEAREST),
        dtype=np.uint8,
    ) > 127
    mw_g = np.asarray(
        Image.fromarray(np.clip(m_weights * 20.0, 0, 255).astype(np.uint8)).resize((mg_w, mg_h), Image.Resampling.BILINEAR),
        dtype=np.float32,
    ) / 20.0

    meadow_polys = cluster_region_to_polys(
        meadow_g,
        mreg_g,
        mw_g,
        k_colors=42,
        plane_idx=1,
        x0_map=x0_map,
        y0_map=y0_map,
        sx_scale=2121.74 / float(mg_w),
        sy_scale=2121.74 / float(mg_h),
        mode_passes=1,
        min_loop_pts=12,
        taubin_iters=3,
        rdp_eps=2.30,
        seam_stroke=1.4,
        base_fill_hex="#5d9e52",
        clip_base_d=meadow_base_d,
        inner_mask=morph_erode(mreg_g, 1),
        seed=29,
    )
    meadow_polys.extend(build_meadow_mural_accents(raw_inpainted_meadow, nx_w, ny_w, x0_map, y0_map, sx_w, sy_w))

    stroke_imp = np.where(in_guanyu, 2.2, np.where(in_ribbon, 1.9, 0.75)).astype(np.float32)
    meadow_strokes = build_flow_strokes(
        styled_meadow,
        morph_erode(meadow_region, 3),
        plane_idx=1,
        x0_map=x0_map,
        y0_map=y0_map,
        sx_scale=sx_w,
        sy_scale=sy_w,
        step=7,
        max_strokes=320,
        len_range=(16.0, 34.0),
        width_buckets=(2.4, 3.4),
        op_val=0.46,
        k_palette=12,
        grad_min=0.032,
        boost=1.04,
        weight_map=stroke_imp,
        seed=41,
    )

    rail_polys = build_railing_polys()
    subject_polys, subject_strokes = build_subject_plane(arr_hi, hair_hi, shirt_hi, skin_hi)

    payload = {
        "version": 2,
        "coord_size": COORD_SZ,
        "bg_fill": "#081833",
        "vector_layers": {
            "sky_polys": sky_polys,
            "sky_strokes": sky_strokes,
            "meadow_polys": meadow_polys,
            "meadow_strokes": meadow_strokes,
            "rail_polys": rail_polys,
            "subject_polys": subject_polys,
            "subject_strokes": subject_strokes,
        },
        "planes": [
            {"plane": 0, "name": "sky", "layers": ["sky_polys", "sky_strokes"]},
            {"plane": 1, "name": "meadow", "layers": ["meadow_polys", "meadow_strokes"]},
            {"plane": 2, "name": "railing", "layers": ["rail_polys"]},
            {"plane": 3, "name": "subject", "layers": ["subject_polys", "subject_strokes"]},
        ],
    }

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, separators=(",", ":"))

    svg_count = sum(1 for s in render_portrait_svg(payload, 246.0, 252.0, 204.0) if s.startswith("<path "))
    print(
        "built portrait_hd.json: %d vector paths across 4 planes (%d bytes)"
        % (svg_count, os.path.getsize(out_path))
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
