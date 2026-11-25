# SPDX-License-Identifier: MIT
import json
import math
import os
import sys
import bpy
import bmesh


# WHY: Emits all 6 watertight box faces (including y0 soffit) via Blender bmesh so negative pitch and Explode views never expose hollow undersides.
def add_box(faces, x0, x1, y0, y1, z0, z1, top_col, side_col, stroke, alpha=0.92, sx=1, sz=1, emissive=False, part=0):
    bm = bmesh.new()
    dx = (x1 - x0) / float(max(1, sx))
    dz = (z1 - z0) / float(max(1, sz))
    for ix in range(max(1, sx)):
        xa, xb = x0 + ix * dx, x0 + (ix + 1) * dx
        for iz in range(max(1, sz)):
            za, zb = z0 + iz * dz, z0 + (iz + 1) * dz
            vt0 = bm.verts.new((xa, y1, za))
            vt1 = bm.verts.new((xb, y1, za))
            vt2 = bm.verts.new((xb, y1, zb))
            vt3 = bm.verts.new((xa, y1, zb))
            bm.faces.new((vt0, vt1, vt2, vt3))
            faces.append({
                "pts": [[round(v.co.x, 2), round(v.co.y, 2), round(v.co.z, 2)] for v in (vt0, vt1, vt2, vt3)],
                "fill": top_col, "stroke": stroke, "alpha": round(alpha, 2), "emissive": emissive, "part": part,
            })
            vb0 = bm.verts.new((xa, y0, zb))
            vb1 = bm.verts.new((xb, y0, zb))
            vb2 = bm.verts.new((xb, y0, za))
            vb3 = bm.verts.new((xa, y0, za))
            bm.faces.new((vb0, vb1, vb2, vb3))
            faces.append({
                "pts": [[round(v.co.x, 2), round(v.co.y, 2), round(v.co.z, 2)] for v in (vb0, vb1, vb2, vb3)],
                "fill": side_col, "stroke": stroke, "alpha": round(alpha * 0.88, 2), "emissive": False, "part": part,
            })
        faces.append({
            "pts": [[round(xa, 2), round(y0, 2), round(z0, 2)], [round(xb, 2), round(y0, 2), round(z0, 2)], [round(xb, 2), round(y1, 2), round(z0, 2)], [round(xa, 2), round(y1, 2), round(z0, 2)]],
            "fill": side_col, "stroke": stroke, "alpha": round(alpha, 2), "emissive": emissive, "part": part,
        })
        faces.append({
            "pts": [[round(xa, 2), round(y0, 2), round(z1, 2)], [round(xb, 2), round(y0, 2), round(z1, 2)], [round(xb, 2), round(y1, 2), round(z1, 2)], [round(xa, 2), round(y1, 2), round(z1, 2)]],
            "fill": side_col, "stroke": stroke, "alpha": round(alpha * 0.94, 2), "emissive": emissive, "part": part,
        })
    for iz in range(max(1, sz)):
        za, zb = z0 + iz * dz, z0 + (iz + 1) * dz
        faces.append({
            "pts": [[round(x0, 2), round(y0, 2), round(za, 2)], [round(x0, 2), round(y0, 2), round(zb, 2)], [round(x0, 2), round(y1, 2), round(zb, 2)], [round(x0, 2), round(y1, 2), round(za, 2)]],
            "fill": side_col, "stroke": stroke, "alpha": round(alpha * 0.90, 2), "emissive": emissive, "part": part,
        })
        faces.append({
            "pts": [[round(x1, 2), round(y0, 2), round(za, 2)], [round(x1, 2), round(y0, 2), round(zb, 2)], [round(x1, 2), round(y1, 2), round(zb, 2)], [round(x1, 2), round(y1, 2), round(za, 2)]],
            "fill": side_col, "stroke": stroke, "alpha": round(alpha * 0.92, 2), "emissive": emissive, "part": part,
        })
    bm.free()


def add_sculpted_cypress(faces, lines, cx, y_base, cz, height=28.0, base_r=4.6, part=1):
    bm = bmesh.new()
    rings = 7
    segs = 7
    ring_verts = []
    for r_i in range(rings + 1):
        t = r_i / float(rings)
        rad = base_r * ((1.0 - t) ** 0.82) * (0.86 + 0.18 * math.sin(t * 9.0))
        twist = t * 1.65
        sway_x = math.sin(t * 3.2) * 1.1 * t
        vy = y_base + t * height
        cur = []
        for s_i in range(segs):
            ang = twist + (s_i * 2.0 * math.pi / float(segs))
            flute = 1.0 + 0.18 * math.sin(s_i * 3.0 + r_i)
            vx = cx + sway_x + math.cos(ang) * rad * flute
            vz = cz + math.sin(ang) * rad * flute
            cur.append(bm.verts.new((vx, vy, vz)))
        ring_verts.append(cur)

    for r_i in range(rings):
        for s_i in range(segs):
            sn = (s_i + 1) % segs
            v0 = ring_verts[r_i][s_i]
            v1 = ring_verts[r_i][sn]
            v2 = ring_verts[r_i + 1][sn]
            v3 = ring_verts[r_i + 1][s_i]
            fill_c = "#0d4a3a" if (r_i + s_i) % 3 != 0 else ("#14532d" if s_i % 2 == 0 else "#78350f")
            stroke_c = "#34d399" if (r_i + s_i) % 4 == 0 else "#115e59"
            faces.append({
                "pts": [[round(v.co.x, 2), round(v.co.y, 2), round(v.co.z, 2)] for v in (v0, v1, v2, v3)],
                "fill": fill_c,
                "stroke": stroke_c,
                "alpha": 0.95,
                "emissive": (r_i + s_i) % 5 == 0,
                "part": part,
            })
    top_v = ring_verts[-1][0].co
    lines.append({
        "p0": [round(cx, 2), round(y_base + height * 0.65, 2), round(cz, 2)],
        "p1": [round(top_v.x + 0.5, 2), round(y_base + height + 2.2, 2), round(top_v.z, 2)],
        "stroke": "#fde047",
        "width": 1.1,
        "part": part,
    })
    bm.free()


def add_sculpted_sunflower(faces, lines, cx, y_ground, cz, height=8.5, rad=3.2, tilt_z=0.35, part=1):
    head_y = y_ground + height
    lines.append({
        "p0": [round(cx, 2), round(y_ground, 2), round(cz, 2)],
        "p1": [round(cx, 2), round(head_y, 2), round(cz + 0.6, 2)],
        "stroke": "#22c55e",
        "width": 1.35,
        "part": part,
    })
    petals = 8
    for i in range(petals):
        a0 = (i * 2.0 * math.pi) / petals
        a1 = ((i + 0.5) * 2.0 * math.pi) / petals
        a2 = ((i + 1.0) * 2.0 * math.pi) / petals
        in_r = rad * 0.42
        out_r = rad * (1.06 if i % 2 == 0 else 0.90)
        p0 = [round(cx + math.cos(a0) * in_r, 2), round(head_y + math.sin(a0) * in_r * math.cos(tilt_z), 2), round(cz + 0.7 + math.sin(a0) * in_r * math.sin(tilt_z), 2)]
        p1 = [round(cx + math.cos(a1) * out_r, 2), round(head_y + math.sin(a1) * out_r * math.cos(tilt_z), 2), round(cz + 0.9 + math.sin(a1) * out_r * math.sin(tilt_z), 2)]
        p2 = [round(cx + math.cos(a2) * in_r, 2), round(head_y + math.sin(a2) * in_r * math.cos(tilt_z), 2), round(cz + 0.7 + math.sin(a2) * in_r * math.sin(tilt_z), 2)]
        faces.append({
            "pts": [p0, p1, p2],
            "fill": "#fde047" if i % 2 == 0 else "#f59e0b",
            "stroke": "#fef08a",
            "alpha": 0.96,
            "emissive": True,
            "part": part,
        })
    core_pts = []
    for i in range(6):
        a = (i * math.pi) / 3.0
        cr = rad * 0.44
        core_pts.append([
            round(cx + math.cos(a) * cr, 2),
            round(head_y + math.sin(a) * cr * math.cos(tilt_z), 2),
            round(cz + 0.85 + math.sin(a) * cr * math.sin(tilt_z), 2),
        ])
    faces.append({
        "pts": core_pts,
        "fill": "#9a3412",
        "stroke": "#fbbf24",
        "alpha": 0.98,
        "emissive": True,
        "part": part,
    })


def add_cylinder_pillar(faces, cx, y0, y1, cz, rad=1.4, segs=6, fill="#1e3a5f", stroke="#fde68a", part=1):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=segs, radius1=rad, radius2=rad * 0.92, depth=y1 - y0)
    mid_y = (y0 + y1) * 0.5
    for f in bm.faces:
        pts = []
        for v in f.verts:
            pts.append([round(cx + v.co.x, 2), round(mid_y + v.co.z, 2), round(cz + v.co.y, 2)])
        faces.append({
            "pts": pts,
            "fill": fill,
            "stroke": stroke,
            "alpha": 0.94,
            "emissive": False,
            "part": part,
        })
    bm.free()


def build_v3_villa():
    faces = []
    lines = []

    add_box(faces, -62, 58, -23.5, -20.8, -28, 30, "#0b223d", "#071426", "#38bdf8", 0.92, 3, 2, False, 0)
    for rz in (18.0, 23.0, 27.5):
        lines.append({"p0": [-52, -20.5, rz], "p1": [46, -20.5, rz], "stroke": "#7dd3fc" if rz < 24 else "#fde047", "width": 0.95, "part": 0})

    add_box(faces, -46, 20, -20.8, -16.4, -22, 18, "#152b44", "#0b1726", "#5eead4", 0.96, 3, 2, False, 0)
    add_box(faces, 16, 52, -19.8, -15.4, -10, 22, "#182f49", "#0c1928", "#fbbf24", 0.96, 2, 2, False, 0)

    add_sculpted_cypress(faces, lines, -53.0, -20.8, -14.0, height=34.0, base_r=4.8, part=1)
    add_sculpted_cypress(faces, lines, 48.0, -15.4, -14.0, height=28.0, base_r=4.0, part=1)
    add_sculpted_sunflower(faces, lines, -42.0, -16.4, 14.0, height=7.4, rad=3.0, tilt_z=0.30, part=1)
    add_sculpted_sunflower(faces, lines, -35.5, -16.4, 16.0, height=6.5, rad=2.6, tilt_z=0.25, part=1)
    add_sculpted_sunflower(faces, lines, 45.0, -15.4, 18.0, height=7.0, rad=2.8, tilt_z=0.28, part=1)

    add_box(faces, -24, 10, -16.4, -1.0, -12, 10, "#9a3412", "#b45309", "#fde68a", 0.80, 2, 1, True, 1)
    add_box(faces, -34, 14, -16.4, 0.2, -16, 14, "#0f3d3e", "#115e59", "#6ee7b7", 0.42, 3, 2, True, 1)
    for mx in (-34, -22, -10, 2, 14):
        lines.append({"p0": [mx, -16.4, 14.2], "p1": [mx, 15.2, 14.2], "stroke": "#6ee7b7", "width": 1.05, "part": 1})
    add_box(faces, -40, 20, 0.2, 2.6, -20, 18, "#1c3550", "#0d1b2c", "#fde68a", 0.96, 3, 2, False, 1)

    add_box(faces, 20, 45, -15.4, 1.8, -4, 18, "#1c3148", "#d97706", "#fde68a", 0.80, 2, 1, True, 1)
    add_box(faces, 17, 48, 1.8, 3.9, -7, 21, "#1d3652", "#0e1b2b", "#5eead4", 0.96, 2, 2, False, 1)
    for sx in (26, 33, 40):
        lines.append({"p0": [sx, -15.4, 18.3], "p1": [sx, 1.8, 18.3], "stroke": "#fefce8", "width": 0.95, "part": 1})

    add_box(faces, -28, 8, 2.6, 15.0, -14, 10, "#1b334b", "#b45309", "#fde68a", 0.72, 2, 1, True, 2)
    add_box(faces, -36, 12, 2.6, 15.2, -16, 12, "#0f3a4d", "#134e4a", "#7dd3fc", 0.42, 3, 1, True, 2)
    add_box(faces, -42, 16, 15.2, 17.6, -19, 15, "#1e3a56", "#0f2034", "#6ee7b7", 0.96, 3, 2, False, 2)

    faces.append({"pts": [[-24, 17.6, -8], [2, 17.6, -8], [-6, 22.8, -1], [-16, 22.8, -1]], "fill": "#1d4ed8", "stroke": "#fde047", "alpha": 0.78, "emissive": True, "part": 3})
    faces.append({"pts": [[-24, 17.6, 6], [2, 17.6, 6], [-6, 22.8, -1], [-16, 22.8, -1]], "fill": "#2563eb", "stroke": "#fde047", "alpha": 0.82, "emissive": True, "part": 3})
    faces.append({"pts": [[-24, 17.6, -8], [-24, 17.6, 6], [-16, 22.8, -1]], "fill": "#1e40af", "stroke": "#fde047", "alpha": 0.76, "emissive": True, "part": 3})
    faces.append({"pts": [[2, 17.6, -8], [2, 17.6, 6], [-6, 22.8, -1]], "fill": "#1e40af", "stroke": "#fde047", "alpha": 0.76, "emissive": True, "part": 3})

    for i in range(4):
        a = -0.35 + i * 0.75
        px, pz = math.cos(a) * 44.0, math.sin(a) * 28.0
        tx, tz = -math.sin(a) * 6.4, math.cos(a) * 6.4
        py = 8.0 + (i % 2) * 4.5
        col = "#6ee7b7" if i % 2 == 0 else "#7dd3fc"
        faces.append({
            "pts": [[round(px - tx, 2), round(py, 2), round(pz - tz, 2)], [round(px + tx, 2), round(py, 2), round(pz + tz, 2)], [round(px + tx, 2), round(py + 7.6, 2), round(pz + tz, 2)], [round(px - tx, 2), round(py + 7.6, 2), round(pz - tz, 2)]],
            "fill": "#0f2d46", "stroke": col, "alpha": 0.62, "emissive": True, "part": 3,
        })

    return {"faces": faces, "lines": lines, "transit": False, "lanterns": False}


def build_v2_viaduct():
    faces = []
    lines = []

    faces.append({
        "pts": [[-82, -25.2, -24], [82, -25.2, -24], [82, -25.2, 24], [-82, -25.2, 24]],
        "fill": "#091b38", "stroke": "#1e3a63", "alpha": 0.88, "emissive": False, "part": 0,
    })
    for gz in (-16, -6, 6, 16):
        lines.append({"p0": [-64, -24.9, gz], "p1": [64, -24.9, gz], "stroke": "#fde047" if abs(gz) == 6 else "#38bdf8", "width": 0.95, "part": 0})

    for px in (-42.0, 42.0):
        add_box(faces, px - 9.0, px + 9.0, -25.0, -18.0, -11.2, 11.2, "#173052", "#0c1c33", "#7dd3fc", 0.96, 2, 1, False, 0)
        add_box(faces, px - 6.2, px + 6.2, -18.0, -8.8, -8.6, 8.6, "#1c3a63", "#0f223d", "#fde68a", 0.96, 1, 1, False, 0)

    add_box(faces, -84, -68.4, -24.8, -4.4, -10.5, 10.5, "#1c3558", "#0e1d34", "#fbbf24", 0.96, 1, 1, False, 0)
    add_box(faces, 68.4, 84, -24.8, -4.4, -10.5, 10.5, "#134e4a", "#0b2928", "#6ee7b7", 0.96, 1, 1, True, 0)

    add_sculpted_cypress(faces, lines, -77.0, -4.4, -6.8, height=24.0, base_r=3.8, part=0)
    add_sculpted_cypress(faces, lines, 77.0, -4.4, -6.8, height=25.0, base_r=3.9, part=0)
    add_sculpted_sunflower(faces, lines, -74.0, -4.4, 7.2, height=6.4, rad=2.6, tilt_z=0.25, part=0)
    add_sculpted_sunflower(faces, lines, 74.0, -4.4, 7.2, height=6.4, rad=2.6, tilt_z=0.25, part=0)

    segs = 20
    dx = 136.0 / segs
    for i in range(segs):
        xa = -68.0 + i * dx
        xb = xa + dx
        xm = (xa + xb) * 0.5
        camber = 1.8 * (1.0 - (xm / 68.0) ** 2)
        add_box(faces, xa, xb, -8.8 + camber, -5.0 + camber, -8.2, 8.2, "#163052", "#0b192e", "#7dd3fc", 0.96, 1, 1, False, 1)

    lines.append({"p0": [-68, -3.8, 0], "p1": [68, -3.8, 0], "stroke": "#fde047", "width": 1.55, "part": 1})
    lines.append({"p0": [-68, -3.8, -5.8], "p1": [68, -3.8, -5.8], "stroke": "#6ee7b7", "width": 1.0, "part": 1})
    lines.append({"p0": [-68, -3.8, 5.8], "p1": [68, -3.8, 5.8], "stroke": "#7dd3fc", "width": 1.0, "part": 1})

    for tx in (-42.0, 42.0):
        for sz in (-7.0, 7.0):
            add_cylinder_pillar(faces, tx, -5.0, 34.0, sz, rad=2.05, segs=6, fill="#24436c", stroke="#fde68a", part=2)
            add_cylinder_pillar(faces, tx, 34.0, 39.8, sz, rad=0.9, segs=4, fill="#fbbf24", stroke="#fef08a", part=2)
        for py, z_sc in ((4.5, 0.92), (17.5, 0.84), (30.5, 0.76)):
            add_box(faces, tx - 1.8, tx + 1.8, py - 1.3, py + 1.3, -7.0 * z_sc, 7.0 * z_sc, "#2a4d7d", "#162d4e", "#fbbf24", 0.95, 1, 1, py > 25, 2)
        lines.append({"p0": [tx, -3.8, -6.2], "p1": [tx, 16.2, 5.8], "stroke": "#7dd3fc", "width": 1.0, "part": 2})
        lines.append({"p0": [tx, -3.8, 6.2], "p1": [tx, 16.2, -5.8], "stroke": "#7dd3fc", "width": 1.0, "part": 2})
        lines.append({"p0": [tx, 18.8, -5.6], "p1": [tx, 29.5, 5.0], "stroke": "#fde68a", "width": 0.95, "part": 2})
        lines.append({"p0": [tx, 18.8, 5.6], "p1": [tx, 29.5, -5.0], "stroke": "#fde68a", "width": 0.95, "part": 2})

    def cable_y(x_val):
        if abs(x_val) <= 42.0:
            u = x_val / 42.0
            return 2.6 + 31.6 * (u * u)
        u = (abs(x_val) - 42.0) / 28.0
        return 34.2 * ((1.0 - u) ** 1.25) - 4.0 * u

    for zp, col in ((-7.0, "#7dd3fc"), (7.0, "#fde047")):
        prev = None
        for x in range(-68, 69, 4):
            cy = cable_y(float(x))
            cur = [round(float(x), 2), round(cy, 2), zp]
            if prev:
                lines.append({"p0": prev, "p1": cur, "stroke": col, "width": 1.5, "part": 3})
            prev = cur
            if x % 8 == 0 and abs(x) not in (40, 44, 68):
                camber = 1.8 * (1.0 - (x / 68.0) ** 2)
                lines.append({"p0": [float(x), round(-4.8 + camber, 2), zp], "p1": cur, "stroke": "#fde68a", "width": 0.85, "part": 3})

    return {"faces": faces, "lines": lines, "transit": True, "lanterns": False}


def build_v1_sanctuary():
    faces = []
    lines = []

    add_box(faces, -64, 64, -24.0, -20.2, -32, 34, "#132238", "#0a1322", "#2d446b", 0.96, 3, 2, False, 0)
    add_box(faces, -48, 48, -20.2, -15.4, -24, 14, "#1c2f4c", "#0f1c30", "#fbbf24", 0.96, 3, 2, False, 0)

    add_sculpted_cypress(faces, lines, -55.0, -20.2, -16.0, height=34.0, base_r=4.7, part=1)
    add_sculpted_cypress(faces, lines, 55.0, -20.2, -14.0, height=32.0, base_r=4.5, part=1)
    add_sculpted_sunflower(faces, lines, 43.0, -20.2, 22.0, height=7.2, rad=3.1, tilt_z=0.30, part=1)
    add_sculpted_sunflower(faces, lines, 50.0, -20.2, 18.0, height=6.4, rad=2.7, tilt_z=0.25, part=1)
    add_sculpted_sunflower(faces, lines, -48.0, -20.2, 22.0, height=6.8, rad=2.9, tilt_z=0.28, part=1)

    add_box(faces, -22, 22, -15.4, 9.2, -18, 2, "#9a3412", "#b45309", "#fde68a", 0.78, 2, 1, True, 1)
    for side_x in (-38.0, 22.0):
        add_box(faces, side_x, side_x + 16.0, -15.4, 9.2, -18, 6, "#0f4c45", "#115e59", "#6ee7b7", 0.50, 2, 1, True, 1)

    for px in (-40.0, -24.0, -10.0, 10.0, 24.0, 40.0):
        add_cylinder_pillar(faces, px, -15.4, 9.6, 8.0, rad=1.18, segs=6, fill="#d97706", stroke="#fde68a", part=1)

    add_box(faces, -54, 54, 9.6, 12.8, -24, 14, "#1a2e4a", "#78350f", "#fde68a", 0.96, 3, 2, False, 2)
    add_box(faces, -34, 34, 12.8, 16.0, -17, 7, "#223b5e", "#122138", "#7dd3fc", 0.96, 2, 1, False, 2)

    dome_segs = 10
    for k in range(dome_segs):
        a0 = (k * 2.0 * math.pi) / dome_segs
        a1 = ((k + 1) * 2.0 * math.pi) / dome_segs
        r_b = 20.5
        r_m = 12.5
        pb0 = [round(math.cos(a0) * r_b, 2), 16.0, round(-4.5 + math.sin(a0) * r_b * 0.76, 2)]
        pb1 = [round(math.cos(a1) * r_b, 2), 16.0, round(-4.5 + math.sin(a1) * r_b * 0.76, 2)]
        pm0 = [round(math.cos(a0) * r_m, 2), 25.4, round(-4.5 + math.sin(a0) * r_m * 0.76, 2)]
        pm1 = [round(math.cos(a1) * r_m, 2), 25.4, round(-4.5 + math.sin(a1) * r_m * 0.76, 2)]
        ptop = [0.0, 31.8, -4.5]
        faces.append({"pts": [pb0, pb1, pm1, pm0], "fill": "#1d4ed8", "stroke": "#7dd3fc" if k % 2 else "#fde047", "alpha": 0.74, "emissive": True, "part": 3})
        faces.append({"pts": [pm0, pm1, ptop], "fill": "#2563eb", "stroke": "#fde047", "alpha": 0.82, "emissive": True, "part": 3})

    add_box(faces, -8.5, 8.5, -20.2, -10.8, 13.0, 23.0, "#243757", "#142036", "#fbbf24", 0.96, 1, 1, False, 1)
    faces.append({
        "pts": [[-17.5, -9.2, 11.2], [17.5, -9.2, 11.2], [17.5, -11.4, 24.8], [-17.5, -11.4, 24.8]],
        "fill": "#78350f", "stroke": "#fbbf24", "alpha": 0.98, "emissive": False, "part": 3,
    })
    for side in (-1.0, 1.0):
        for seg in range(4):
            t0 = seg / 4.0
            t1 = (seg + 1) / 4.0
            x0 = side * (0.5 + t0 * 15.8)
            x1 = side * (0.5 + t1 * 15.8)
            arch0 = math.sin(t0 * math.pi * 0.82) * 3.4
            arch1 = math.sin(t1 * math.pi * 0.82) * 3.4
            faces.append({
                "pts": [
                    [round(x0, 2), round(-8.6 + arch0, 2), 12.0],
                    [round(x1, 2), round(-8.6 + arch1, 2), 12.2],
                    [round(x1, 2), round(-10.8 + arch1, 2), 24.0],
                    [round(x0, 2), round(-10.8 + arch0, 2), 23.8],
                ],
                "fill": "#fef3c7" if side < 0 else "#fde68a",
                "stroke": "#d97706",
                "alpha": 0.98,
                "emissive": True,
                "part": 3,
            })
        for row_t in (0.28, 0.50, 0.72):
            z_ln = round(12.2 + row_t * 11.2, 2)
            y_drop = row_t * 2.2
            lines.append({
                "p0": [round(side * 2.8, 2), round(-7.2 - y_drop, 2), z_ln],
                "p1": [round(side * 14.2, 2), round(-6.2 - y_drop, 2), z_ln],
                "stroke": "#1e3a8a",
                "width": 1.05,
                "part": 3,
            })

    return {"faces": faces, "lines": lines, "transit": False, "lanterns": True}


def main():
    argv = sys.argv
    out_path = argv[argv.index("--") + 1] if "--" in argv else "assets/models_3d.json"
    payload = {
        "v3": build_v3_villa(),
        "v2": build_v2_viaduct(),
        "v1": build_v1_sanctuary(),
    }
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, separators=(",", ":"))
    print(
        "Blender 5.3 sculpted models_3d.json: v3=%d faces, v2=%d faces, v1=%d faces (%d bytes)"
        % (
            len(payload["v3"]["faces"]),
            len(payload["v2"]["faces"]),
            len(payload["v1"]["faces"]),
            os.path.getsize(out_path),
        )
    )


if __name__ == "__main__":
    main()
