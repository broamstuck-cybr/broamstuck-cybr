# SPDX-License-Identifier: MIT
from theme import num

PALETTE = {
    "O": "#451a03",
    "D": "#78350f",
    "R": "#b45309",
    "M": "#f59e0b",
    "G": "#fbbf24",
    "L": "#fef3c7",
    "C": "#fffbeb",
    "B": "#2563eb",
    "N": "#1e3a8a",
    "P": "#fb923c",
    "E": "#1c0a00",
    "W": "#ffffff",
    "S": "#fde047",
    "Q": "#0f172a",
    "V": "#be123c",
    "H": "#fb7185",
    "K": "#fda4af",
    "Z": "#7dd3fc",
    "T": "#6ee7b7",
}

LAYER_ORDER = tuple(PALETTE.keys())
LAYER_RANK = {ch: idx for idx, ch in enumerate(LAYER_ORDER)}

HEAD_AWAKE = [
    "..OO.....OO...",
    ".OGLO...OGLO..",
    ".OGLGOOOGGLO..",
    "..OLLGGGGGO...",
    "..OGGCGGCGGO..",
    "..OGWEGGWEGO..",
    "..OGEECCEEGO..",
    "..OPCCCCCCEEO.",
    "..OCCCOCCPCCO.",
]

TORSO_STAND = [
    "...OOROOOOOOO............",
    "...OLLLLLLLLGONBBBSBBOO..",
    "..OGGGGGGGGGGGBBBBBBNBO..",
    ".OGGGGGGGGGGGGNBBBBNNBO..",
    ".OMMMMMMMMMGGGGNNBNOCCCO.",
    ".OMMMMMMMMMMMGGCCCCCCCO..",
    ".ORRRRRRMMMMMMCCCCCCCCO..",
    "..OORRRRRRCCCCCCCCCCOO...",
]

TAIL_BASE = [
    "..OOO...",
    ".OCCLO..",
    "OCCGGO..",
    "OCGMRO..",
    ".OOMROO.",
]

LEG_NEAR = [
    ".OMMO",
    "OMMCO",
    "OCCO.",
    "OOO..",
]

LEG_FAR = [
    "ODDO",
    "ODDO",
    ".OO.",
]

EMOTES = {
    "heart": (
        -4,
        -33,
        '<g fill="#0f172a"><rect x="-4" y="-33" width="9" height="4"/><rect x="-3" y="-29" width="7" height="2"/><rect x="-1" y="-27" width="3" height="2"/></g>',
        [
            ".........",
            ".KKH.HHH.",
            ".HHHHHHH.",
            "..HHHHH..",
            "...HHH...",
            "....H....",
        ],
    ),
    "zzz": (
        -4,
        -32,
        '<g fill="#0f172a"><rect x="-1" y="-32" width="5" height="6"/><rect x="-4" y="-27" width="5" height="6"/></g>',
        [
            ".........",
            "....SSS..",
            ".....S...",
            "....S....",
            "....SSS..",
            ".........",
            ".ZZZ.....",
            "..Z......",
            ".Z.......",
            ".ZZZ.....",
        ],
    ),
    "note": (
        -4,
        -33,
        '<g fill="#0f172a"><rect x="-2" y="-33" width="7" height="5"/><rect x="-4" y="-30" width="9" height="4"/></g>',
        [
            ".........",
            "...SSSS..",
            "...S..S..",
            "...S..S..",
            ".TTS.TTS.",
        ],
    ),
}


def _merge_grid_rects(rows, ox=0, oy=0):
    # WHY: Lossless painter-order underfill bridging + vertical span merging keeps shaded 28x24 sprites <10 KB.
    present = {ch for row in rows for ch in row if ch != "."}
    elems = []
    for ch in LAYER_ORDER:
        if ch not in present:
            continue
        rank = LAYER_RANK[ch]
        runs = []
        for r_idx, row in enumerate(rows):
            w = len(row)
            c_idx = 0
            while c_idx < w:
                if row[c_idx] != ch:
                    c_idx += 1
                    continue
                last_need = c_idx
                scan = c_idx + 1
                while scan < w:
                    cell = row[scan]
                    if cell == ch:
                        last_need = scan
                        scan += 1
                    elif cell != "." and LAYER_RANK[cell] > rank:
                        scan += 1
                    else:
                        break
                runs.append([ox + c_idx, oy + r_idx, last_need - c_idx + 1, 1])
                c_idx = last_need + 1

        merged = []
        active = {}
        for x, y, rw, rh in runs:
            key = (x, rw)
            prev = active.get(key)
            if prev is not None and prev[1] + prev[3] == y:
                prev[3] += rh
            else:
                item = [x, y, rw, rh]
                merged.append(item)
                active[key] = item
        rects = []
        for x, y, rw, rh in merged:
            xa = ' x="%d"' % x if x else ""
            ya = ' y="%d"' % y if y else ""
            rects.append('<rect%s%s width="%d" height="%d"/>' % (xa, ya, rw, rh))
        elems.append('<g fill="%s">%s</g>' % (PALETTE[ch], "".join(rects)))
    return "".join(elems)


def pup_defs(prefix):
    lie_lids = '<g fill="%s"><rect x="17" y="10" width="2" height="1"/><rect x="21" y="10" width="2" height="1"/></g>' % PALETTE["G"]
    lie_paws = (
        '<g fill="%s"><rect x="4" y="19" width="23" height="1"/><rect x="10" y="20" width="6" height="1"/><rect x="19" y="20" width="6" height="1"/></g>'
        '<g fill="%s"><rect x="11" y="19" width="5" height="1"/><rect x="19" y="19" width="6" height="1"/></g>'
        % (PALETTE["O"], PALETTE["C"])
    )
    sit_paws = (
        '<g fill="%s"><rect x="3" y="18" width="19" height="2"/></g>'
        '<g fill="%s"><rect x="4" y="18" width="8" height="1"/></g>'
        '<g fill="%s"><rect x="12" y="18" width="9" height="1"/></g>'
        '<use href="#%s-ln" x="9" y="2"/><use href="#%s-ln" x="16" y="2"/>'
        % (PALETTE["O"], PALETTE["R"], PALETTE["C"], prefix, prefix)
    )
    return [
        '<g id="%s-ph">%s</g>' % (prefix, _merge_grid_rects(HEAD_AWAKE, 12, 1)),
        '<g id="%s-pt">%s</g>' % (prefix, _merge_grid_rects(TORSO_STAND, 2, 9)),
        '<g id="%s-pw">%s</g>' % (prefix, _merge_grid_rects(TAIL_BASE, 2, 4)),
        '<g id="%s-ln">%s</g>' % (prefix, _merge_grid_rects(LEG_NEAR, 0, 17)),
        '<g id="%s-lf">%s</g>' % (prefix, _merge_grid_rects(LEG_FAR, 0, 17)),
        '<g id="%s-ps"><use href="#%s-pw" x="1" y="4"/><use href="#%s-pt" x="-1" y="2"/>%s</g>'
        % (prefix, prefix, prefix, sit_paws),
        '<g id="%s-pl"><use href="#%s-pw" y="4"/><use href="#%s-pt" y="3"/><use href="#%s-ph" x="1" y="4"/>%s%s</g>'
        % (prefix, prefix, prefix, prefix, lie_lids, lie_paws),
    ]


def _discrete_track(events):
    kt = ";".join(num(t, 3) for t, _ in events)
    vals = ";".join(v for _, v in events)
    return kt, vals


def render_starlight_pup(prefix, segments, emote_keys=("heart", "zzz"), total_dur=26.0, pixel_scale=1.62):
    # WHY: Uses exact SMIL keyTimes state transitions + independent 0.44s bouncy trot stride and 2.2s rest breathing (<9.5 KB total).
    dur = "%ss" % num(total_dur, 1)
    pos_kt = ";".join(num(s[0], 3) for s in segments)
    pos_vals = ";".join("%s %s" % (num(s[1], 1), num(s[2], 1)) for s in segments)

    active_segs = segments[:-1]
    state_kt = ";".join(num(s[0], 3) for s in active_segs)
    flip_vals = ";".join("1 1" if s[4] >= 0 else "-1 1" for s in active_segs)

    pose_names = ("trot", "sniff", "sit", "lie")
    pose_vals = {
        pk: ";".join("1" if s[3] == pk else "0" for s in active_segs)
        for pk in pose_names
    }

    emote_tracks = {ek: [(0.0, "0")] for ek in emote_keys}
    for idx, s in enumerate(active_segs):
        em = s[5]
        if em in emote_tracks:
            t0 = s[0]
            t1 = segments[idx + 1][0]
            span = t1 - t0
            t_on = round(t0 + span * 0.24, 3)
            t_off = round(t0 + span * 0.82, 3)
            if t_on > emote_tracks[em][-1][0]:
                emote_tracks[em].append((t_on, "1"))
                emote_tracks[em].append((t_off, "0"))

    legs_a = '<use href="#%s-lf" x="9"/><use href="#%s-lf" x="15"/><use href="#%s-ln" x="3"/><use href="#%s-ln" x="19"/>' % (prefix, prefix, prefix, prefix)
    legs_b = '<use href="#%s-lf" x="5" y="-1"/><use href="#%s-lf" x="20" y="-1"/><use href="#%s-ln" x="9" y="-1"/><use href="#%s-ln" x="15" y="-1"/>' % (prefix, prefix, prefix, prefix)
    dust_a = '<g fill="%s"><rect x="1" y="21" width="1" height="1"/><rect x="3" y="22" width="1" height="1"/></g>' % PALETTE["S"]
    dust_b = '<g fill="%s"><rect x="2" y="20" width="1" height="1"/><rect y="21" width="1" height="1"/></g>' % PALETTE["S"]
    trot_group = (
        '<g opacity="1">'
        '<animate attributeName="opacity" calcMode="discrete" values="1;0" dur="0.44s" repeatCount="indefinite"/>'
        '<use href="#%s-pw"/><use href="#%s-pt"/><use href="#%s-ph"/>%s%s</g>'
        '<g opacity="0">'
        '<animate attributeName="opacity" calcMode="discrete" values="0;1" dur="0.44s" repeatCount="indefinite"/>'
        '<g transform="translate(0 -1)"><use href="#%s-pw" x="1"/><use href="#%s-pt"/><use href="#%s-ph"/></g>%s%s</g>'
        % (prefix, prefix, prefix, legs_a, dust_a, prefix, prefix, prefix, legs_b, dust_b)
    )
    breath = (
        '<rect x="6" y="13" width="7" height="1" fill="%s">'
        '<animate attributeName="opacity" calcMode="discrete" values="0;1" dur="2.2s" repeatCount="indefinite"/>'
        "</rect>" % PALETTE["L"]
    )
    pose_markup = {
        "trot": ("1", trot_group),
        "sniff": (
            "0",
            '<use href="#%s-pw" x="1" y="-1"/><use href="#%s-pt"/><use href="#%s-ph" x="2" y="3"/><g transform="translate(1 0)">%s</g>'
            % (prefix, prefix, prefix, legs_a),
        ),
        "sit": (
            "0",
            '<use href="#%s-ps"/><g><animateTransform attributeName="transform" type="translate" calcMode="discrete" values="0 0;0 1" dur="1.6s" repeatCount="indefinite"/><use href="#%s-ph" x="-1" y="2"/></g>'
            % (prefix, prefix),
        ),
        "lie": ("0", '<use href="#%s-pl"/>%s' % (prefix, breath)),
    }

    bx_s = num(segments[0][1], 1)
    by_s = num(segments[0][2], 1)
    ps_s = num(pixel_scale, 2)
    out = [
        '<g id="%s-pup" class="pup-live" transform="translate(%s %s)" pointer-events="none">'
        % (prefix, bx_s, by_s),
        '<animateTransform attributeName="transform" type="translate" values="%s" keyTimes="%s" dur="%s" repeatCount="indefinite"/>'
        % (pos_vals, pos_kt, dur),
        '<g transform="scale(%s %s)">' % (ps_s, ps_s),
        '<ellipse cx="1" cy="-2.2" rx="12.5" ry="2.7" fill="#030712" fill-opacity="0.58">'
        '<animate attributeName="rx" values="12.6;11.2;12.6" dur="0.44s" repeatCount="indefinite"/>'
        "</ellipse>",
        '<ellipse cx="1" cy="-2.2" rx="8.2" ry="1.35" fill="#fde047" fill-opacity="0.16"/>',
        '<g shape-rendering="crispEdges">',
        '<g transform="scale(%s 1)">' % ("1" if segments[0][4] >= 0 else "-1"),
        '<animateTransform attributeName="transform" type="scale" calcMode="discrete" values="%s" keyTimes="%s" dur="%s" repeatCount="indefinite"/>'
        % (flip_vals, state_kt, dur),
        '<g transform="translate(-14 -22)">',
    ]

    for pname in pose_names:
        init_op, inner = pose_markup[pname]
        out.append(
            '<g opacity="%s">'
            '<animate attributeName="opacity" calcMode="discrete" values="%s" keyTimes="%s" dur="%s" repeatCount="indefinite"/>'
            "%s</g>"
            % (init_op, pose_vals[pname], state_kt, dur, inner)
        )

    out.append("</g></g>")

    for ename in emote_keys:
        ex, ey, ebg, egrid = EMOTES[ename]
        ekt, evals = _discrete_track(emote_tracks[ename])
        out.append(
            '<g opacity="0">'
            '<animate attributeName="opacity" calcMode="discrete" values="%s" keyTimes="%s" dur="%s" repeatCount="indefinite"/>'
            '<animateTransform attributeName="transform" type="translate" values="0 0;0 -1.5;0 -2.8" dur="1.8s" repeatCount="indefinite"/>'
            "%s%s</g>"
            % (evals, ekt, dur, ebg, _merge_grid_rects(egrid, ex, ey))
        )

    out.append(
        '</g></g></g>'
        '<g id="%s-pup-calm" class="pup-calm" transform="translate(%s %s)" pointer-events="none">'
        '<g transform="scale(%s %s)">'
        '<ellipse cx="1" cy="-2.2" rx="11.8" ry="2.7" fill="#030712" fill-opacity="0.58"/>'
        '<g shape-rendering="crispEdges" transform="translate(-14 -22)">'
        '<use href="#%s-ps"/><use href="#%s-ph" x="-1" y="2"/>'
        "</g></g></g>"
        % (prefix, bx_s, by_s, ps_s, ps_s, prefix, prefix)
    )
    return ["".join(out)]


def starry_matrix_pup():
    segments = [
        (0.000, 340.0, 287.0, "trot", 1, None),
        (0.240, 645.0, 285.0, "sniff", 1, None),
        (0.315, 645.0, 285.0, "sit", 1, "heart"),
        (0.455, 645.0, 285.0, "trot", 1, None),
        (0.585, 882.0, 286.0, "trot", -1, None),
        (0.745, 508.0, 286.0, "lie", -1, "zzz"),
        (0.915, 508.0, 286.0, "trot", -1, None),
        (1.000, 340.0, 287.0, "trot", 1, None),
    ]
    return render_starlight_pup("mat", segments, emote_keys=("heart", "zzz"), total_dur=28.0, pixel_scale=1.62)


def nocturne_garden_pup():
    segments = [
        (0.000, 486.0, 366.0, "trot", 1, None),
        (0.220, 772.0, 356.0, "sniff", 1, None),
        (0.300, 772.0, 356.0, "sit", -1, "note"),
        (0.440, 772.0, 356.0, "trot", -1, None),
        (0.595, 598.0, 336.0, "trot", -1, None),
        (0.720, 412.0, 362.0, "lie", 1, "zzz"),
        (0.900, 412.0, 362.0, "trot", 1, None),
        (1.000, 486.0, 366.0, "trot", 1, None),
    ]
    return render_starlight_pup("vg3", segments, emote_keys=("note", "zzz"), total_dur=32.0, pixel_scale=1.92)
