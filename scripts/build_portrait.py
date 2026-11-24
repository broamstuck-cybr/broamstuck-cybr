import json
import math
import os
import sys
from PIL import Image, ImageEnhance, ImageFilter


def clamp(v, lo=0.0, hi=255.0):
    return lo if v < lo else (hi if v > hi else v)


def rgb_hex(r, g, b):
    return "#%02x%02x%02x" % (int(round(clamp(r))), int(round(clamp(g))), int(round(clamp(b))))


def quantize_channel(v, step=6):
    return int(clamp(round(v / float(step)) * step))


def stylize_nocturne_pixel(r, g, b, nx, ny):
    lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
    # Detect coral-red shirt region (center-bottom subject)
    red_dom = (r - max(g, b)) / 255.0
    is_subject_zone = (0.31 <= nx <= 0.69) and (0.43 <= ny <= 1.0)
    is_shirt = is_subject_zone and (ny >= 0.58) and (red_dom > 0.10 or (r > 135 and r > g * 1.18))
    is_hair = (0.38 <= nx <= 0.59) and (0.43 <= ny <= 0.63) and lum < 0.28
    is_sky = ny < 0.495 and not is_hair

    if is_shirt:
        # Rich warm crimson-coral linen with crisp highlight/fold separation
        nr = clamp(r * 1.06 + 14.0)
        ng = clamp(g * 0.76 + 8.0)
        nb = clamp(b * 0.68 + 6.0)
        return nr, ng, nb

    if is_hair:
        # Preserve fine hair strand sheen instead of crushing to flat black
        boost = 1.35 if lum > 0.10 else 0.92
        nr = clamp(r * boost + 12.0)
        ng = clamp(g * boost + 13.0)
        nb = clamp(b * boost * 1.15 + 20.0)
        return nr, ng, nb

    if is_sky:
        # Harmonize daylight cloud deck into warm Saint-Remy twilight gold & Prussian slate
        sky_t = clamp((0.495 - ny) / 0.495, 0.0, 1.0)
        swirl = 0.5 + 0.5 * math.sin(nx * 9.5 + math.sin(ny * 13.0) * 1.6)
        cloud_hi = max(0.0, (lum - 0.68) / 0.32)
        prussian_r = 26.0 + 48.0 * (1.0 - sky_t) + 34.0 * swirl
        prussian_g = 42.0 + 62.0 * (1.0 - sky_t) + 36.0 * swirl
        prussian_b = 76.0 + 64.0 * sky_t + 32.0 * (1.0 - swirl)
        gold_r = 236.0
        gold_g = 198.0
        gold_b = 112.0
        mix_gold = clamp(0.24 + 0.52 * cloud_hi * (0.45 + 0.55 * (1.0 - sky_t)), 0.0, 0.82)
        nr = prussian_r * (1.0 - mix_gold) + gold_r * mix_gold
        ng = prussian_g * (1.0 - mix_gold) + gold_g * mix_gold
        nb = prussian_b * (1.0 - mix_gold) + gold_b * mix_gold
        # Blend 32% original local cloud micro-contrast
        nr = nr * 0.68 + (r * 0.92) * 0.32
        ng = ng * 0.68 + (g * 0.86) * 0.32
        nb = nb * 0.68 + (b * 0.78) * 0.32
        return clamp(nr), clamp(ng), clamp(nb)

    # Landscape rice-field warrior mural + steel balcony railing: golden-emerald nocturne vibrancy
    is_rail = ny >= 0.70 and not is_shirt and abs(b - g) < 38 and lum < 0.62 and (b >= r * 0.92)
    if is_rail:
        nr = clamp(r * 0.82 + 22.0)
        ng = clamp(g * 0.92 + 28.0)
        nb = clamp(b * 1.08 + 34.0)
        return nr, ng, nb

    # Rice paddy & warrior mural: preserve emerald, gold armor, and crimson-violet ribbons
    nr = clamp(r * 1.04 + 14.0)
    ng = clamp(g * 1.02 + 10.0)
    nb = clamp(b * 0.82 + 8.0)
    return nr, ng, nb


def pick_directional_glyph(lum, mag, gx, gy, nx, ny):
    # Directional edge-aware glyph selection for crisp architectural, fabric, and hair fidelity
    if mag > 0.20:
        ang = math.degrees(math.atan2(gy, gx)) % 180.0
        # Gradient angle is perpendicular to edge tangent; edge tangent = ang + 90
        edge_ang = (ang + 90.0) % 180.0
        if mag > 0.42:
            if 72.0 <= edge_ang <= 108.0:
                return "|" if lum < 0.55 else "!"
            if 162.0 <= edge_ang or edge_ang <= 18.0:
                return "=" if lum > 0.42 else "-"
            if 18.0 < edge_ang < 72.0:
                return "/"
            return "\\"
        if 75.0 <= edge_ang <= 105.0:
            return "I" if lum > 0.52 else "|"
        if 165.0 <= edge_ang or edge_ang <= 15.0:
            return "=" if lum > 0.52 else "~"
        if 20.0 < edge_ang < 70.0:
            return "/"
        if 110.0 < edge_ang < 160.0:
            return "\\"

    ramp = " .,:;+~*i!lI?vcnxzjft/\\|()1{}[]<>7rJCLQ0OZmwqpdbkhao#MW&8%B@$"
    # Slightly invert/remap darkness vs brightness so luminous regions carry dense crisp ink on dark ground
    vis = clamp(lum * 1.06, 0.0, 1.0)
    if ny < 0.48 and not ((0.38 <= nx <= 0.59) and (0.43 <= ny <= 0.63)):
        # Delicate atmospheric stipple & impasto weave in sky so subject pops forward
        sky_ramp = " .·-:=+~*x#%@"
        idx = int(round((vis ** 1.15) * (len(sky_ramp) - 1)))
        ch = sky_ramp[max(1, min(len(sky_ramp) - 1, idx))]
        return ":" if ch == "·" else ch

    idx = int(round((vis ** 0.88) * (len(ramp) - 1)))
    return ramp[max(2, min(len(ramp) - 1, idx))]


def build_portrait(src_path, out_path, cols=156, rows=86, atmos_n=48):
    raw = Image.open(src_path).convert("RGB")
    size = min(raw.size)
    left = (raw.width - size) // 2
    top = (raw.height - size) // 2
    square = raw.crop((left, top, left + size, top + size)).resize((480, 480), Image.Resampling.LANCZOS)

    # Multi-pass local micro-contrast enhancement for crisp shirt folds, hair strands, mural & railing
    detail = square.filter(ImageFilter.UnsharpMask(radius=2.1, percent=175, threshold=2))
    detail = ImageEnhance.Contrast(detail).enhance(1.14)
    detail = ImageEnhance.Color(detail).enhance(1.12)

    gray_img = detail.convert("L").resize((cols, rows), Image.Resampling.LANCZOS)
    col_img = detail.resize((cols, rows), Image.Resampling.LANCZOS)
    gray_px = gray_img.load()
    col_px = col_img.load()

    # Compute normalized Sobel gradients on the (cols x rows) luminance grid
    gx_map = [[0.0] * cols for _ in range(rows)]
    gy_map = [[0.0] * cols for _ in range(rows)]
    mag_map = [[0.0] * cols for _ in range(rows)]
    max_mag = 1e-6

    for y in range(1, rows - 1):
        for x in range(1, cols - 1):
            tl = gray_px[x - 1, y - 1] / 255.0
            tc = gray_px[x, y - 1] / 255.0
            tr = gray_px[x + 1, y - 1] / 255.0
            ml = gray_px[x - 1, y] / 255.0
            mr = gray_px[x + 1, y] / 255.0
            bl = gray_px[x - 1, y + 1] / 255.0
            bc = gray_px[x, y + 1] / 255.0
            br = gray_px[x + 1, y + 1] / 255.0
            gx = (tr + 2.0 * mr + br) - (tl + 2.0 * ml + bl)
            gy = (bl + 2.0 * bc + br) - (tl + 2.0 * tc + tr)
            m = math.hypot(gx, gy)
            gx_map[y][x] = gx
            gy_map[y][x] = gy
            mag_map[y][x] = m
            if m > max_mag:
                max_mag = m

    grid = []
    for y in range(rows):
        ny = (y + 0.5) / float(rows)
        dy_c = (ny - 0.5) * 2.0
        runs = []
        cur_col = "__INIT__"
        cur_chars = []

        for x in range(cols):
            nx = (x + 0.5) / float(cols)
            dx_c = (nx - 0.5) * 2.0
            if dx_c * dx_c + dy_c * dy_c > 1.03:
                cell_col = None
                ch = " "
            else:
                r, g, b = col_px[x, y]
                sr, sg, sb = stylize_nocturne_pixel(r, g, b, nx, ny)
                lum = (0.299 * sr + 0.587 * sg + 0.114 * sb) / 255.0
                norm_mag = min(1.0, mag_map[y][x] / (max_mag * 0.62))
                ch = pick_directional_glyph(lum, norm_mag, gx_map[y][x], gy_map[y][x], nx, ny)
                # Boost edge clarity slightly so hair crown, collar & mural pop cleanly
                edge_lift = 1.0 + norm_mag * 0.22
                qr = quantize_channel(sr * edge_lift, 8)
                qg = quantize_channel(sg * edge_lift, 8)
                qb = quantize_channel(sb * edge_lift, 8)
                # Ensure minimum visibility over #080d1a dark portrait ground
                if max(qr, qg, qb) < 38:
                    qr, qg, qb = qr + 22, qg + 26, qb + 38
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

    # Smooth 48x48 atmospheric under-painting layer
    atmos_img = detail.resize((atmos_n, atmos_n), Image.Resampling.LANCZOS)
    apx = atmos_img.load()
    atmos = []
    for ay in range(atmos_n):
        ny = (ay + 0.5) / float(atmos_n)
        dy_c = (ny - 0.5) * 2.0
        for ax in range(atmos_n):
            nx = (ax + 0.5) / float(atmos_n)
            dx_c = (nx - 0.5) * 2.0
            if dx_c * dx_c + dy_c * dy_c > 1.02:
                continue
            r, g, b = apx[ax, ay]
            sr, sg, sb = stylize_nocturne_pixel(r, g, b, nx, ny)
            atmos.append([
                ax,
                ay,
                rgb_hex(quantize_channel(sr * 0.86, 6), quantize_channel(sg * 0.86, 6), quantize_channel(sb * 0.86, 6)),
            ])

    # Extract crisp sub-pixel contour segments along high-gradient subject & mural ridges (120x120 grid)
    c_size = 128
    c_gray = detail.convert("L").resize((c_size, c_size), Image.Resampling.LANCZOS)
    c_rgb = detail.resize((c_size, c_size), Image.Resampling.LANCZOS)
    cg = c_gray.load()
    cr = c_rgb.load()
    contours = []
    for y in range(2, c_size - 2, 2):
        ny = y / float(c_size)
        if ny < 0.42:
            continue
        for x in range(2, c_size - 2, 2):
            nx = x / float(c_size)
            if (nx - 0.5) ** 2 + (ny - 0.5) ** 2 > 0.235:
                continue
            gx = (cg[x + 1, y] - cg[x - 1, y]) / 255.0
            gy = (cg[x, y + 1] - cg[x, y - 1]) / 255.0
            mag = math.hypot(gx, gy)
            # Prioritize subject silhouette, shirt collar/folds, railing & warrior mural
            in_focus = (0.34 <= nx <= 0.66 and 0.43 <= ny <= 0.98)
            thresh = 0.16 if in_focus else 0.25
            if mag < thresh:
                continue
            # Tangent vector along the ridge
            tx = -gy / mag
            ty = gx / mag
            r, g, b = cr[x, y]
            sr, sg, sb = stylize_nocturne_pixel(r, g, b, nx, ny)
            seg_col = rgb_hex(clamp(sr * 1.22 + 18), clamp(sg * 1.18 + 16), clamp(sb * 1.18 + 16))
            half_len = 0.0105 if in_focus else 0.0085
            contours.append([
                round(nx - tx * half_len, 4),
                round(ny - ty * half_len, 4),
                round(nx + tx * half_len, 4),
                round(ny + ty * half_len, 4),
                seg_col,
                round(min(0.68, 0.24 + mag * 0.85), 2),
            ])

    payload = {
        "cols": cols,
        "rows": rows,
        "atmos_n": atmos_n,
        "atmos": atmos,
        "contours": contours[:520],
        "grid": grid,
    }
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, separators=(",", ":"))
    print(
        "built portrait_hd.json: %dx%d grid, %d atmos cells, %d contour ridges (%d bytes)"
        % (cols, rows, len(atmos), len(payload["contours"]), os.path.getsize(out_path))
    )


if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise SystemExit("usage: python build_portrait.py <raw_avatar.png> <out_portrait_hd.json>")
    build_portrait(sys.argv[1], sys.argv[2])
