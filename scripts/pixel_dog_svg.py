# SPDX-License-Identifier: MIT
import math

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
    "F": "#064e3b",
    "J": "#047857",
    "A": "#10b981",
    "Y": "#34d399",
    "T": "#6ee7b7",
    "Q": "#0f172a",
    "I": "#0284c7",
    "U": "#38bdf8",
    "Z": "#7dd3fc",
    "X": "#bae6fd",
    "V": "#be123c",
    "H": "#fb7185",
    "K": "#fda4af",
    "S": "#fde047",
    "W": "#ffffff",
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

HEAD_WONDER = [
    ".OO.....OO....",
    "OGLO...OGLO...",
    "OGLGOOOGGLO...",
    ".OLLGGGGGO....",
    ".OGGCGGCGGOOO.",
    ".OGWEGGWECCEEO",
    ".OGEECCCCCCCO.",
    "..OPCCCCHCCOO.",
    "..OOCCCCCCOO..",
    "...OOOOOOOO...",
]

HEAD_SNIFF = [
    "..OO....OO....",
    ".OGLO..OGLO...",
    ".OGLGOOGGLO...",
    "..OLLGGGGGO...",
    "..OGGCGGCGGO..",
    "..OGEEGGEEGOO.",
    "..OPCCCCCCCEEO",
    "...OCCCCCCCEEO",
    "....OOOOOOOOO.",
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

BODY_HOP = [
    "....................OOO...",
    "..OOO..............OCCCO..",
    ".OCCLO.............OCCMO..",
    ".OCCGGO........OO..OMMMOO.",
    "..OOMGGGGGOOOOOBBBOOCCCO..",
    "...OGGGGGGGGGGBBSBBBOOOO..",
    "..OGGGGGGGGGGGNBBBBNO.....",
    "..OMMMMMMMGGGGCCCCCCCO....",
    "..ORRRRRMMMMMCCCCCCCCO....",
    "...OORRRRRCCCCCCCCCOO.....",
    "...OMMOO..ODDO............",
    "..OMMCO...ODDO............",
    "..OCCO.....OO.............",
    "..OOO.....................",
]

BELLY_BODY = [
    "................OOOOO....",
    "...............OCCCHOO...",
    ".....OOOOOOOOOOCCCCCCEO..",
    "...OOCCCCCCCCBNNBBCCGGEO.",
    "..OCCLLLLCCCCBBBSBGGGLLOO",
    ".OCGGGGGGGGGGGBBBGGGGGLGO",
    "OCCGMMGGGGGGGGGGGGGGGOOO.",
    ".OOMMMMMMMMMMMMMGGGGGO...",
    "..OORRRRRRRRRMMMMMGLOO...",
    "....OOOOOOOOOOOOOO.OO....",
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

TUFT_GOLD = [
    ".....GS...T.....",
    "....GPSC..Y...CS",
    ".....GG...Y..CGP",
    "..T...A..AY...J.",
    "..Y..AY..YA..AJ.",
    "..YA.JA.AYJ..JA.",
    "...YAAJ.JAA.AJ..",
    "...JAAJ.JAAJAJ..",
    "....JJF.FJJJJ...",
    "....FFF.FFFFF...",
    "...FFFFFFFFFFF..",
]

TUFT_IVORY = [
    "...C.C....T....",
    "..CCGCC...Y....",
    "...C.C...AY..C.",
    ".T..A....YA.CG.",
    ".YA.JA..AYJ.J..",
    "..YAJA..JAAJA..",
    "..JAAJ..JAAJ...",
    "...JJFF.FJJF...",
    "...FFFFFFFFF...",
    "..FFFFFFFFFFF..",
]

TUFT_GRASS = [
    ".....T....T..",
    ".T...Y...AY..",
    ".YA..YA..JA..",
    "..YA.AY.AJ...",
    "..JAAJAJAA...",
    "...JAAJAAJ...",
    "...FFJJJFF...",
    "..FFFFFFFFF..",
]

BF_MORPHO_OPEN = [
    "....Q...Q....",
    ".QQQ.Q.Q.QQQ.",
    "QWUXXQQQXXUWQ",
    "QUXXUQQQUXXUQ",
    ".QUUIQQQIUUQ.",
    "..QQIUQUIQQ..",
    "..QUXUQUXUQ..",
    "...QUI.IUQ...",
    "....Q...Q....",
]

BF_MORPHO_MID = [
    "....Q...Q....",
    "..QQQ.Q.QQQ..",
    "..QWUXQXUWQ..",
    "..QUXUQUXUQ..",
    "...QUIQIUQ...",
    "...QQUQUQQ...",
    "....QUQUQ....",
    "....QQ.QQ....",
    ".............",
]

BF_MORPHO_CLOSED = [
    "....Q.Q......",
    "....QQQQQ....",
    ".....QUXWQ...",
    "....QUXXUQ...",
    "....QUIUQ....",
    "....QQIQQ....",
    ".....QQQ.....",
    ".....Q.Q.....",
    ".............",
]

BF_MONARCH_OPEN = [
    "....E...E....",
    ".EEE.E.E.EEE.",
    "EWSGGEEEGGSWE",
    "EGSGGEEEGGSGE",
    ".EGPPEEEPPGE.",
    "..EEPGEGPEE..",
    "..EGPGEGPGE..",
    "...EPP.PPE...",
    "....E...E....",
]

BF_MONARCH_MID = [
    "....E...E....",
    "..EEE.E.EEE..",
    "..EWSGEGSWE..",
    "..EGSGEGSGE..",
    "...EPPEPPE...",
    "...EEPGPEE...",
    "....EPGPE....",
    "....EE.EE....",
    ".............",
]

BF_MONARCH_CLOSED = [
    "....E.E......",
    "....EEEEE....",
    ".....EGSWE...",
    "....EGGSGE...",
    "....EPGPE....",
    "....EEPEE....",
    ".....EEE.....",
    ".....E.E.....",
    ".............",
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
    "sparkle": (
        -4,
        -35,
        '<g fill="#0f172a"><rect x="-1" y="-35" width="3" height="9"/><rect x="-4" y="-32" width="9" height="3"/><rect x="-2" y="-33" width="5" height="5"/></g>',
        [
            "....S....",
            "....S....",
            "..Z.W.Z..",
            "...WWW...",
            "SSWWWWWSS",
            "...WWW...",
            "..Z.W.Z..",
            "....S....",
            "....S....",
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
    # WHY: Lossless painter-order underfill bridging + vertical span merging keeps shaded pixel sprites compact.
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


def flora_butterfly_defs(prefix, include_monarch=False):
    defs = [
        '<g id="%s-flg" shape-rendering="crispEdges">%s</g>' % (prefix, _merge_grid_rects(TUFT_GOLD, -8, -11)),
        '<g id="%s-fli" shape-rendering="crispEdges">%s</g>' % (prefix, _merge_grid_rects(TUFT_IVORY, -7, -10)),
        '<g id="%s-flr" shape-rendering="crispEdges">%s</g>' % (prefix, _merge_grid_rects(TUFT_GRASS, -6, -8)),
        '<g id="%s-bfm0" shape-rendering="crispEdges">%s</g>' % (prefix, _merge_grid_rects(BF_MORPHO_OPEN, -6, -9)),
        '<g id="%s-bfm1" shape-rendering="crispEdges">%s</g>' % (prefix, _merge_grid_rects(BF_MORPHO_MID, -6, -9)),
        '<g id="%s-bfm2" shape-rendering="crispEdges">%s</g>' % (prefix, _merge_grid_rects(BF_MORPHO_CLOSED, -6, -9)),
    ]
    if include_monarch:
        defs.extend(
            [
                '<g id="%s-bfg0" shape-rendering="crispEdges">%s</g>' % (prefix, _merge_grid_rects(BF_MONARCH_OPEN, -6, -9)),
                '<g id="%s-bfg1" shape-rendering="crispEdges">%s</g>' % (prefix, _merge_grid_rects(BF_MONARCH_MID, -6, -9)),
                '<g id="%s-bfg2" shape-rendering="crispEdges">%s</g>' % (prefix, _merge_grid_rects(BF_MONARCH_CLOSED, -6, -9)),
            ]
        )
    return defs


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
    defs = [
        '<g id="%s-ph">%s</g>' % (prefix, _merge_grid_rects(HEAD_AWAKE, 12, 1)),
        '<g id="%s-hw">%s</g>' % (prefix, _merge_grid_rects(HEAD_WONDER, 12, 1)),
        '<g id="%s-hs">%s</g>' % (prefix, _merge_grid_rects(HEAD_SNIFF, 14, 6)),
        '<g id="%s-pt">%s</g>' % (prefix, _merge_grid_rects(TORSO_STAND, 2, 9)),
        '<g id="%s-bh">%s</g>' % (prefix, _merge_grid_rects(BODY_HOP, 2, 5)),
        '<g id="%s-bb">%s</g>' % (prefix, _merge_grid_rects(BELLY_BODY, 3, 11)),
        '<g id="%s-pw">%s</g>' % (prefix, _merge_grid_rects(TAIL_BASE, 2, 4)),
        '<g id="%s-ln">%s</g>' % (prefix, _merge_grid_rects(LEG_NEAR, 0, 17)),
        '<g id="%s-lf">%s</g>' % (prefix, _merge_grid_rects(LEG_FAR, 0, 17)),
        '<g id="%s-ps"><use href="#%s-pw" x="1" y="4"/><use href="#%s-pt" x="-1" y="2"/>%s</g>'
        % (prefix, prefix, prefix, sit_paws),
        '<g id="%s-pl"><use href="#%s-pw" y="4"/><use href="#%s-pt" y="3"/><use href="#%s-ph" x="1" y="4"/>%s%s</g>'
        % (prefix, prefix, prefix, prefix, lie_lids, lie_paws),
    ]
    defs.extend(flora_butterfly_defs(prefix, include_monarch=True))
    return defs


def _discrete_track(events):
    kt = ";".join(num(t, 3) for t, _ in events)
    vals = ";".join(v for _, v in events)
    return kt, vals


def _tuft_ref(prefix, kind):
    if kind == "gold":
        return "#%s-flg" % prefix
    if kind == "ivory":
        return "#%s-fli" % prefix
    return "#%s-flr" % prefix


def _render_meadow_tufts(prefix, tufts, total_dur=34.0):
    # WHY: Roots sit at y=0 so SMIL skewX bends only upper blades/petals; sniff windows trigger rustle + rising golden pollen.
    live_nodes = []
    calm_nodes = []
    dur_s = "%ss" % num(total_dur, 1)

    for tx, ty, kind, sc, breeze_dur, breeze_phase, sniff_win in tufts:
        ref = _tuft_ref(prefix, kind)
        tx_s, ty_s, sc_s = num(tx, 1), num(ty, 1), num(sc, 2)
        calm_nodes.append(
            '<g transform="translate(%s %s) scale(%s %s)"><use href="%s"/></g>'
            % (tx_s, ty_s, sc_s, sc_s, ref)
        )
        if sniff_win is None:
            live_nodes.append(
                '<g transform="translate(%s %s) scale(%s %s)"><g>'
                '<animateTransform attributeName="transform" type="skewX" values="-3.6;4.2;-3.6" dur="%ss" begin="%ss" repeatCount="indefinite"/>'
                '<use href="%s"/></g></g>'
                % (tx_s, ty_s, sc_s, sc_s, num(breeze_dur, 1), num(breeze_phase, 1), ref)
            )
        else:
            t0, t1 = sniff_win
            span = t1 - t0
            rustle_pts = [
                (0.0, "0"),
                (max(0.001, t0 - 0.005), "-2.5"),
                (t0 + span * 0.14, "-9.5"),
                (t0 + span * 0.30, "8.5"),
                (t0 + span * 0.46, "-8.0"),
                (t0 + span * 0.62, "7.2"),
                (t0 + span * 0.78, "-5.5"),
                (t0 + span * 0.92, "3.5"),
                (min(0.998, t1 + 0.012), "-2.0"),
                (1.0, "0"),
            ]
            rkt = ";".join(num(p[0], 3) for p in rustle_pts)
            rvals = ";".join(p[1] for p in rustle_pts)
            live_nodes.append(
                '<g transform="translate(%s %s) scale(%s %s)"><g>'
                '<animateTransform attributeName="transform" type="skewX" values="-3.2;3.6;-3.2" dur="%ss" begin="%ss" repeatCount="indefinite"/>'
                '<g><animateTransform attributeName="transform" type="skewX" values="%s" keyTimes="%s" dur="%s" repeatCount="indefinite"/>'
                '<use href="%s"/></g></g></g>'
                % (tx_s, ty_s, sc_s, sc_s, num(breeze_dur, 1), num(breeze_phase, 1), rvals, rkt, dur_s, ref)
            )

    return live_nodes, calm_nodes


def _render_pollen_bursts(tufts, total_dur=34.0):
    dur_s = "%ss" % num(total_dur, 1)
    out = []
    mote_specs = (
        (-3.5, -13.0, -5.5, -29.0, 0.06, 0.64, PALETTE["S"], 2.2, 2.2),
        (2.8, -15.0, 8.0, -34.0, 0.20, 0.82, PALETTE["W"], 2.0, 2.0),
        (-0.4, -12.0, -2.5, -38.0, 0.34, 0.96, PALETTE["G"], 2.2, 2.2),
    )
    for tx, ty, _, sc, _, _, sniff_win in tufts:
        if sniff_win is None:
            continue
        t0, t1 = sniff_win
        span = t1 - t0
        for dx0, dy0, dx1, dy1, f_start, f_end, col, mw, mh in mote_specs:
            ma = round(t0 + span * f_start, 3)
            mb = round(t0 + span * ((f_start + f_end) * 0.5), 3)
            mc = round(t0 + span * f_end, 3)
            mx0, my0 = tx + dx0 * (sc / 1.5), ty + dy0 * (sc / 1.5)
            mx1, my1 = tx + (dx0 + dx1) * 0.5 * (sc / 1.5), ty + (dy0 + dy1) * 0.5 * (sc / 1.5)
            mx2, my2 = tx + dx1 * (sc / 1.5), ty + dy1 * (sc / 1.5)
            kt = "0;%s;%s;%s;%s;1" % (num(max(0.001, ma - 0.004), 3), num(ma, 3), num(mb, 3), num(mc, 3))
            op_v = "0;0;0.96;0.90;0;0"
            tr_v = "%s %s;%s %s;%s %s;%s %s;%s %s;%s %s" % (
                num(mx0, 1), num(my0, 1),
                num(mx0, 1), num(my0, 1),
                num(mx0, 1), num(my0, 1),
                num(mx1, 1), num(my1, 1),
                num(mx2, 1), num(my2, 1),
                num(mx2, 1), num(my2, 1),
            )
            out.append(
                '<g class="pup-live" opacity="0" shape-rendering="crispEdges" pointer-events="none">'
                '<animate attributeName="opacity" values="%s" keyTimes="%s" dur="%s" repeatCount="indefinite"/>'
                '<animateTransform attributeName="transform" type="translate" values="%s" keyTimes="%s" dur="%s" repeatCount="indefinite"/>'
                '<rect x="-0.6" y="-0.6" width="%s" height="%s" fill="%s"/>'
                '<rect width="%s" height="%s" fill="%s"/></g>'
                % (op_v, kt, dur_s, tr_v, kt, dur_s, num(mw + 1.2, 1), num(mh + 1.2, 1), PALETTE["O"], num(mw, 1), num(mh, 1), col)
            )
    return out


def _butterfly_flap_group(prefix, species_code, flap_dur="0.38s", begin="0s"):
    # WHY: 3-frame discrete SMIL wing cycle (open -> mid -> closed -> mid) keeps pixel silhouette crisp at every frame.
    f0 = "#%s-%s0" % (prefix, species_code)
    f1 = "#%s-%s1" % (prefix, species_code)
    f2 = "#%s-%s2" % (prefix, species_code)
    return (
        '<g opacity="1"><animate attributeName="opacity" calcMode="discrete" values="1;0;0;0" dur="%s" begin="%s" repeatCount="indefinite"/><use href="%s"/></g>'
        '<g opacity="0"><animate attributeName="opacity" calcMode="discrete" values="0;1;0;1" dur="%s" begin="%s" repeatCount="indefinite"/><use href="%s"/></g>'
        '<g opacity="0"><animate attributeName="opacity" calcMode="discrete" values="0;0;1;0" dur="%s" begin="%s" repeatCount="indefinite"/><use href="%s"/></g>'
        % (flap_dur, begin, f0, flap_dur, begin, f1, flap_dur, begin, f2)
    )


def _render_ambient_butterfly(prefix, species_code, motion_path, dur_s, scale=1.50, flap_dur="0.40s", begin="-3.2s"):
    sc_s = num(scale, 2)
    return (
        '<g class="pup-live" pointer-events="none">'
        '<animateMotion path="%s" dur="%s" begin="%s" repeatCount="indefinite"/>'
        '<g transform="scale(%s %s)">%s</g></g>'
        % (motion_path, dur_s, begin, sc_s, sc_s, _butterfly_flap_group(prefix, species_code, flap_dur, begin))
    )


def _render_interactive_butterfly(prefix, species_code, legs, perch_win, total_dur=34.0, scale=1.50, perch_flip=1):
    # WHY: Cosine-eased sinusoidal flight curves lock onto exact 0.1px nose-perch coordinates without arc-length drift.
    pts = []
    for idx, leg in enumerate(legs):
        t0, x0, y0, t1, x1, y1, arch, bob, steps = leg
        for s_i in range(steps):
            if idx > 0 and s_i == 0:
                continue
            u = s_i / float(steps - 1) if steps > 1 else 1.0
            t = t0 + (t1 - t0) * u
            ease = 0.5 - 0.5 * math.cos(math.pi * u)
            px = x0 + (x1 - x0) * ease
            py = y0 + (y1 - y0) * ease - arch * math.sin(math.pi * u) + bob * math.sin(2.0 * math.pi * u)
            pts.append((t, px, py))

    dur_s = "%ss" % num(total_dur, 1)
    kt = ";".join(num(p[0], 3) for p in pts)
    tr_vals = ";".join("%s %s" % (num(p[1], 1), num(p[2], 1)) for p in pts)
    sc_s = num(scale, 2)

    p0, p1 = perch_win
    perch_kt = "0;%s;%s;1" % (num(p0, 3), num(p1, 3))
    fly_op = "1;0;1;1"
    sit_op = "0;1;0;0"
    f1 = "#%s-%s1" % (prefix, species_code)
    f2 = "#%s-%s2" % (prefix, species_code)
    flip_s = "1" if perch_flip >= 0 else "-1"

    perched_inner = (
        '<g transform="scale(%s 1)">'
        '<g opacity="1"><animate attributeName="opacity" calcMode="discrete" values="1;1;0;1" dur="2.2s" repeatCount="indefinite"/><use href="%s"/></g>'
        '<g opacity="0"><animate attributeName="opacity" calcMode="discrete" values="0;0;1;0" dur="2.2s" repeatCount="indefinite"/><use href="%s"/></g>'
        "</g>" % (flip_s, f2, f1)
    )

    return (
        '<g class="pup-live" transform="translate(%s %s)" pointer-events="none">'
        '<animateTransform attributeName="transform" type="translate" values="%s" keyTimes="%s" dur="%s" repeatCount="indefinite"/>'
        '<g transform="scale(%s %s)">'
        '<g opacity="1"><animate attributeName="opacity" calcMode="discrete" values="%s" keyTimes="%s" dur="%s" repeatCount="indefinite"/>%s</g>'
        '<g opacity="0"><animate attributeName="opacity" calcMode="discrete" values="%s" keyTimes="%s" dur="%s" repeatCount="indefinite"/>%s</g>'
        "</g></g>"
        % (
            num(pts[0][1], 1),
            num(pts[0][2], 1),
            tr_vals,
            kt,
            dur_s,
            sc_s,
            sc_s,
            fly_op,
            perch_kt,
            dur_s,
            _butterfly_flap_group(prefix, species_code, "0.36s", "0s"),
            sit_op,
            perch_kt,
            dur_s,
            perched_inner,
        )
    )


def render_starlight_pup(
    prefix,
    segments,
    emote_keys=("sparkle", "heart", "zzz"),
    total_dur=34.0,
    pixel_scale=1.62,
    calm_x=None,
    calm_y=None,
    calm_dir=1,
):
    dur = "%ss" % num(total_dur, 1)
    pos_kt = ";".join(num(s[0], 3) for s in segments)
    pos_vals = ";".join("%s %s" % (num(s[1], 1), num(s[2], 1)) for s in segments)

    active_segs = segments[:-1]
    state_kt = ";".join(num(s[0], 3) for s in active_segs)
    flip_vals = ";".join("1 1" if s[4] >= 0 else "-1 1" for s in active_segs)

    pose_names = ("trot", "sniff_low", "play_pounce", "nose_perch", "belly_roll", "ear_scratch", "lie_rest")
    used_poses = [pk for pk in pose_names if any(s[3] == pk for s in active_segs)]
    pose_vals = {
        pk: ";".join("1" if s[3] == pk else "0" for s in active_segs)
        for pk in used_poses
    }

    emote_tracks = {ek: [(0.0, "0")] for ek in emote_keys}
    for idx, s in enumerate(active_segs):
        em = s[5]
        if em in emote_tracks:
            t0 = s[0]
            t1 = segments[idx + 1][0]
            span = t1 - t0
            t_on = round(t0 + span * 0.20, 3)
            t_off = round(t0 + span * 0.84, 3)
            if t_on > emote_tracks[em][-1][0]:
                emote_tracks[em].append((t_on, "1"))
                emote_tracks[em].append((t_off, "0"))

    legs_a = '<use href="#%s-lf" x="9"/><use href="#%s-lf" x="15"/><use href="#%s-ln" x="3"/><use href="#%s-ln" x="19"/>' % (prefix, prefix, prefix, prefix)
    legs_b = '<use href="#%s-lf" x="5" y="-1"/><use href="#%s-lf" x="20" y="-1"/><use href="#%s-ln" x="9" y="-1"/><use href="#%s-ln" x="15" y="-1"/>' % (prefix, prefix, prefix, prefix)
    dust_a = '<g fill="%s"><rect x="1" y="21" width="1" height="1"/><rect x="3" y="22" width="1" height="1"/></g>' % PALETTE["S"]
    dust_b = '<g fill="%s"><rect x="2" y="20" width="1" height="1"/><rect y="21" width="1" height="1"/></g>' % PALETTE["S"]

    trot_group = (
        '<g opacity="1">'
        '<animate attributeName="opacity" calcMode="discrete" values="1;0" dur="0.42s" repeatCount="indefinite"/>'
        '<use href="#%s-pw"/><use href="#%s-pt"/><use href="#%s-ph"/>%s%s</g>'
        '<g opacity="0">'
        '<animate attributeName="opacity" calcMode="discrete" values="0;1" dur="0.42s" repeatCount="indefinite"/>'
        '<g transform="translate(0 -1)"><use href="#%s-pw" x="1"/><use href="#%s-pt"/><use href="#%s-ph"/></g>%s%s</g>'
        % (prefix, prefix, prefix, legs_a, dust_a, prefix, prefix, prefix, legs_b, dust_b)
    )

    sniff_group = (
        '<g opacity="1"><animate attributeName="opacity" calcMode="discrete" values="1;0" dur="0.28s" repeatCount="indefinite"/><use href="#%s-pw" y="-1"/></g>'
        '<g opacity="0"><animate attributeName="opacity" calcMode="discrete" values="0;1" dur="0.28s" repeatCount="indefinite"/><use href="#%s-pw" x="1" y="1"/></g>'
        '<use href="#%s-pt" y="1"/>'
        '<g><animateTransform attributeName="transform" type="translate" calcMode="discrete" values="0 0;1 1" dur="0.54s" repeatCount="indefinite"/><use href="#%s-hs"/></g>'
        '<g transform="translate(1 0)">%s</g>'
        % (prefix, prefix, prefix, prefix, legs_a)
    )

    bow_paws = (
        '<use href="#%s-lf" x="8"/><use href="#%s-ln" x="3"/>'
        '<g fill="%s"><rect x="19" y="19" width="8" height="2"/></g>'
        '<g fill="%s"><rect x="20" y="19" width="6" height="1"/></g>'
        % (prefix, prefix, PALETTE["O"], PALETTE["C"])
    )
    pounce_group = (
        '<g opacity="1">'
        '<animate attributeName="opacity" calcMode="discrete" values="1;0" dur="0.68s" repeatCount="indefinite"/>'
        '<use href="#%s-pw" y="-1"/><use href="#%s-pt" y="2"/>%s<use href="#%s-hw" x="1" y="4"/></g>'
        '<g opacity="0">'
        '<animate attributeName="opacity" calcMode="discrete" values="0;1" dur="0.68s" repeatCount="indefinite"/>'
        '<use href="#%s-bh"/><use href="#%s-hw" x="-1" y="-2"/>%s</g>'
        % (prefix, prefix, bow_paws, prefix, prefix, prefix, dust_b)
    )

    perch_group = (
        '<g opacity="1"><animate attributeName="opacity" calcMode="discrete" values="1;0" dur="0.92s" repeatCount="indefinite"/><use href="#%s-pw" x="1" y="4"/></g>'
        '<g opacity="0"><animate attributeName="opacity" calcMode="discrete" values="0;1" dur="0.92s" repeatCount="indefinite"/><use href="#%s-pw" x="2" y="3"/></g>'
        '<use href="#%s-pt" x="-1" y="2"/>'
        '<g fill="%s"><rect x="3" y="18" width="19" height="2"/></g>'
        '<g fill="%s"><rect x="4" y="18" width="8" height="1"/></g>'
        '<g fill="%s"><rect x="12" y="18" width="9" height="1"/></g>'
        '<use href="#%s-ln" x="9" y="2"/><use href="#%s-ln" x="16" y="2"/>'
        '<use href="#%s-hw" x="-1" y="1"/>'
        % (prefix, prefix, prefix, PALETTE["O"], PALETTE["R"], PALETTE["C"], prefix, prefix, prefix)
    )

    roll_paws_a = (
        '<g fill="%s"><rect x="5" y="8" width="3" height="4"/><rect x="9" y="10" width="3" height="3"/><rect x="14" y="8" width="3" height="4"/><rect x="18" y="10" width="3" height="3"/></g>'
        '<g fill="%s"><rect x="6" y="8" width="2" height="2"/><rect x="10" y="10" width="2" height="2"/><rect x="15" y="8" width="2" height="2"/><rect x="18" y="10" width="2" height="2"/></g>'
        '<g fill="%s"><rect x="6" y="10" width="2" height="2"/><rect x="15" y="10" width="2" height="2"/></g>'
        % (PALETTE["O"], PALETTE["C"], PALETTE["M"])
    )
    roll_paws_b = (
        '<g fill="%s"><rect x="5" y="10" width="3" height="3"/><rect x="9" y="8" width="3" height="4"/><rect x="14" y="10" width="3" height="3"/><rect x="18" y="8" width="3" height="4"/></g>'
        '<g fill="%s"><rect x="6" y="10" width="2" height="2"/><rect x="10" y="8" width="2" height="2"/><rect x="15" y="10" width="2" height="2"/><rect x="18" y="8" width="2" height="2"/></g>'
        '<g fill="%s"><rect x="10" y="10" width="2" height="2"/><rect x="18" y="10" width="2" height="2"/></g>'
        % (PALETTE["O"], PALETTE["C"], PALETTE["M"])
    )
    belly_group = (
        '<use href="#%s-bb"/>'
        '<g opacity="1"><animate attributeName="opacity" calcMode="discrete" values="1;0" dur="0.34s" repeatCount="indefinite"/>%s</g>'
        '<g opacity="0"><animate attributeName="opacity" calcMode="discrete" values="0;1" dur="0.34s" repeatCount="indefinite"/>%s</g>'
        % (prefix, roll_paws_a, roll_paws_b)
    )

    scratch_paw_a = '<g fill="%s"><rect x="11" y="6" width="4" height="3"/></g><g fill="%s"><rect x="12" y="6" width="2" height="2"/></g>' % (PALETTE["O"], PALETTE["C"])
    scratch_paw_b = '<g fill="%s"><rect x="10" y="9" width="4" height="3"/></g><g fill="%s"><rect x="11" y="9" width="2" height="2"/></g>' % (PALETTE["O"], PALETTE["C"])
    scratch_group = (
        '<use href="#%s-ps"/>'
        '<use href="#%s-ph" y="3"/>'
        '<rect x="16" y="9" width="3" height="1" fill="%s"/>'
        '<g opacity="1"><animate attributeName="opacity" calcMode="discrete" values="1;0" dur="0.24s" repeatCount="indefinite"/>%s</g>'
        '<g opacity="0"><animate attributeName="opacity" calcMode="discrete" values="0;1" dur="0.24s" repeatCount="indefinite"/>%s</g>'
        % (prefix, prefix, PALETTE["G"], scratch_paw_a, scratch_paw_b)
    )

    breath = (
        '<rect x="6" y="13" width="7" height="1" fill="%s">'
        '<animate attributeName="opacity" calcMode="discrete" values="0;1" dur="2.4s" repeatCount="indefinite"/>'
        "</rect>" % PALETTE["L"]
    )

    pose_markup = {
        "trot": trot_group,
        "sniff_low": sniff_group,
        "play_pounce": pounce_group,
        "nose_perch": perch_group,
        "belly_roll": belly_group,
        "ear_scratch": scratch_group,
        "lie_rest": '<use href="#%s-pl"/>%s' % (prefix, breath),
    }

    bx_s = num(segments[0][1], 1)
    by_s = num(segments[0][2], 1)
    cx_s = num(calm_x if calm_x is not None else segments[0][1], 1)
    cy_s = num(calm_y if calm_y is not None else segments[0][2], 1)
    cflip_s = "1" if calm_dir >= 0 else "-1"
    ps_s = num(pixel_scale, 2)
    first_pose = active_segs[0][3]

    out = [
        '<g id="%s-pup" class="pup-live" transform="translate(%s %s)" pointer-events="none">'
        % (prefix, bx_s, by_s),
        '<animateTransform attributeName="transform" type="translate" values="%s" keyTimes="%s" dur="%s" repeatCount="indefinite"/>'
        % (pos_vals, pos_kt, dur),
        '<g transform="scale(%s %s)">' % (ps_s, ps_s),
        '<ellipse cx="1" cy="-2.2" rx="12.5" ry="2.7" fill="#030712" fill-opacity="0.58">'
        '<animate attributeName="rx" values="12.6;11.2;12.6" dur="0.42s" repeatCount="indefinite"/>'
        "</ellipse>",
        '<ellipse cx="1" cy="-2.2" rx="8.2" ry="1.35" fill="#fde047" fill-opacity="0.16"/>',
        '<g shape-rendering="crispEdges">',
        '<g transform="scale(%s 1)">' % ("1" if segments[0][4] >= 0 else "-1"),
        '<animateTransform attributeName="transform" type="scale" calcMode="discrete" values="%s" keyTimes="%s" dur="%s" repeatCount="indefinite"/>'
        % (flip_vals, state_kt, dur),
        '<g transform="translate(-14 -22)">',
    ]

    for pname in used_poses:
        init_op = "1" if pname == first_pose else "0"
        out.append(
            '<g opacity="%s">'
            '<animate attributeName="opacity" calcMode="discrete" values="%s" keyTimes="%s" dur="%s" repeatCount="indefinite"/>'
            "%s</g>"
            % (init_op, pose_vals[pname], state_kt, dur, pose_markup[pname])
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
        '<g shape-rendering="crispEdges" transform="scale(%s 1)">'
        '<g transform="translate(-14 -22)">'
        '<use href="#%s-ps"/><use href="#%s-hw" x="-1" y="1"/>'
        "</g></g></g></g>"
        % (prefix, cx_s, cy_s, ps_s, ps_s, cflip_s, prefix, prefix)
    )
    return out


def starry_matrix_pup():
    total_dur = 34.0
    tufts = [
        (304.0, 287.0, "grass", 1.45, 4.4, -0.8, None),
        (396.0, 286.5, "ivory", 1.50, 5.1, -2.1, None),
        (494.0, 286.5, "gold", 1.58, 4.8, -1.2, (0.095, 0.205)),
        (618.0, 287.0, "grass", 1.42, 4.2, -3.0, None),
        (742.0, 286.5, "ivory", 1.52, 5.3, -1.7, None),
        (886.0, 286.5, "gold", 1.55, 4.6, -2.6, None),
        (942.0, 287.0, "grass", 1.40, 4.9, -0.5, None),
    ]
    segments = [
        (0.000, 368.0, 286.5, "trot", 1, None),
        (0.095, 474.5, 286.5, "sniff_low", 1, None),
        (0.205, 474.5, 286.5, "trot", 1, None),
        (0.305, 638.0, 286.0, "play_pounce", 1, None),
        (0.385, 638.0, 286.0, "nose_perch", 1, "sparkle"),
        (0.515, 638.0, 286.0, "trot", 1, None),
        (0.590, 746.0, 286.5, "belly_roll", -1, "heart"),
        (0.685, 746.0, 286.5, "trot", -1, None),
        (0.770, 586.0, 286.5, "lie_rest", -1, "zzz"),
        (0.880, 586.0, 286.5, "trot", -1, None),
        (1.000, 368.0, 286.5, "trot", 1, None),
    ]
    morpho_legs = [
        (0.000, 386.0, 214.0, 0.145, 518.0, 232.0, 18.0, 5.0, 6),
        (0.145, 518.0, 232.0, 0.285, 658.0, 244.0, 22.0, -4.5, 6),
        (0.285, 658.0, 244.0, 0.380, 656.0, 248.0, 12.0, 5.5, 6),
        (0.380, 656.0, 248.0, 0.402, 652.6, 263.2, 3.0, 0.0, 3),
        (0.402, 652.6, 263.2, 0.506, 652.6, 263.2, 0.0, 0.0, 2),
        (0.506, 652.6, 263.2, 0.650, 744.0, 198.0, 24.0, 4.5, 6),
        (0.650, 744.0, 198.0, 0.830, 548.0, 174.0, 20.0, -5.0, 6),
        (0.830, 548.0, 174.0, 1.000, 386.0, 214.0, 16.0, 4.0, 6),
    ]
    monarch_path = "M 886,266 C 812,236 774,174 848,158 C 924,142 1036,184 996,232 C 964,262 918,274 886,266 Z"

    live_tufts, calm_tufts = _render_meadow_tufts("mat", tufts, total_dur)
    out = [
        '<g class="pup-live" pointer-events="none">%s</g>' % "".join(live_tufts),
        '<g class="pup-calm" pointer-events="none">%s</g>' % "".join(calm_tufts),
    ]
    out.extend(
        render_starlight_pup(
            "mat",
            segments,
            emote_keys=("sparkle", "heart", "zzz"),
            total_dur=total_dur,
            pixel_scale=1.62,
            calm_x=638.0,
            calm_y=286.0,
            calm_dir=1,
        )
    )
    out.extend(_render_pollen_bursts(tufts, total_dur))
    out.append(_render_interactive_butterfly("mat", "bfm", morpho_legs, (0.402, 0.506), total_dur=total_dur, scale=1.48, perch_flip=-1))
    out.append(_render_ambient_butterfly("mat", "bfg", monarch_path, "22.5s", scale=1.46, flap_dur="0.42s", begin="-6.4s"))
    out.append(
        '<g class="pup-calm" pointer-events="none">'
        '<g transform="translate(652.6 263.2) scale(-1.48 1.48)"><use href="#mat-bfm2"/></g>'
        '<g transform="translate(886 269.5) scale(1.44 1.44)"><use href="#mat-bfg1"/></g>'
        "</g>"
    )
    return ["".join(out)]


def nocturne_garden_pup():
    total_dur = 36.0
    tufts = [
        (268.0, 372.0, "grass", 1.74, 5.4, -1.1, None),
        (322.0, 368.0, "gold", 1.80, 4.7, -0.9, None),
        (384.0, 365.0, "ivory", 1.82, 5.2, -2.3, (0.665, 0.750)),
        (462.0, 367.0, "grass", 1.70, 4.3, -1.5, None),
        (544.0, 355.0, "grass", 1.66, 4.9, -3.1, None),
        (694.0, 354.0, "ivory", 1.76, 5.0, -0.6, None),
        (796.0, 360.0, "gold", 1.86, 4.5, -1.8, (0.115, 0.215)),
        (858.0, 367.0, "grass", 1.75, 4.8, -2.7, None),
    ]
    segments = [
        (0.000, 524.0, 362.0, "trot", 1, None),
        (0.115, 773.0, 360.0, "sniff_low", 1, None),
        (0.215, 773.0, 360.0, "ear_scratch", -1, "note"),
        (0.290, 773.0, 360.0, "trot", -1, None),
        (0.375, 604.0, 350.0, "play_pounce", -1, None),
        (0.450, 604.0, 350.0, "nose_perch", -1, "sparkle"),
        (0.575, 604.0, 350.0, "trot", -1, None),
        (0.665, 407.0, 365.0, "sniff_low", -1, None),
        (0.750, 407.0, 365.0, "belly_roll", 1, "heart"),
        (0.835, 407.0, 365.0, "trot", 1, None),
        (0.890, 524.0, 362.0, "lie_rest", 1, "zzz"),
        (1.000, 524.0, 362.0, "trot", 1, None),
    ]
    morpho_legs = [
        (0.000, 442.0, 246.0, 0.175, 668.0, 224.0, 22.0, 5.5, 6),
        (0.175, 668.0, 224.0, 0.355, 586.0, 298.0, 18.0, -5.0, 6),
        (0.355, 586.0, 298.0, 0.445, 582.0, 304.0, 14.0, 6.0, 6),
        (0.445, 582.0, 304.0, 0.466, 586.7, 322.9, 3.5, 0.0, 3),
        (0.466, 586.7, 322.9, 0.564, 586.7, 322.9, 0.0, 0.0, 2),
        (0.564, 586.7, 322.9, 0.720, 488.0, 232.0, 26.0, 5.0, 6),
        (0.720, 488.0, 232.0, 0.875, 372.0, 268.0, 18.0, -4.5, 6),
        (0.875, 372.0, 268.0, 1.000, 442.0, 246.0, 15.0, 4.0, 5),
    ]
    monarch_right = "M 798,336 C 742,292 818,204 918,214 C 1016,224 1044,296 958,326 C 896,348 836,352 798,336 Z"
    monarch_left = "M 226,318 C 148,284 166,198 258,208 C 344,218 368,286 304,318 C 272,334 248,328 226,318 Z"

    live_tufts, calm_tufts = _render_meadow_tufts("vg3", tufts, total_dur)
    out = [
        '<g class="pup-live" pointer-events="none">%s</g>' % "".join(live_tufts),
        '<g class="pup-calm" pointer-events="none">%s</g>' % "".join(calm_tufts),
    ]
    out.extend(
        render_starlight_pup(
            "vg3",
            segments,
            emote_keys=("note", "sparkle", "heart", "zzz"),
            total_dur=total_dur,
            pixel_scale=1.92,
            calm_x=604.0,
            calm_y=350.0,
            calm_dir=-1,
        )
    )
    out.extend(_render_pollen_bursts(tufts, total_dur))
    out.append(_render_interactive_butterfly("vg3", "bfm", morpho_legs, (0.466, 0.564), total_dur=total_dur, scale=1.68, perch_flip=1))
    out.append(_render_ambient_butterfly("vg3", "bfg", monarch_right, "24s", scale=1.64, flap_dur="0.40s", begin="-4.8s"))
    out.append(_render_ambient_butterfly("vg3", "bfg", monarch_left, "27.5s", scale=1.52, flap_dur="0.44s", begin="-11.2s"))
    out.append(
        '<g class="pup-calm" pointer-events="none">'
        '<g transform="translate(586.7 322.9) scale(1.68 1.68)"><use href="#vg3-bfm2"/></g>'
        '<g transform="translate(796 340.5) scale(1.60 1.60)"><use href="#vg3-bfg1"/></g>'
        "</g>"
    )
    return ["".join(out)]


def core_stage_butterfly_cameo():
    tufts = [
        (74.0, 536.0, "gold", 1.48, 4.8, -1.4, None),
        (114.0, 538.0, "ivory", 1.38, 5.3, -2.7, None),
    ]
    cameo_path = "M 82,508 C 46,476 48,418 86,404 C 124,390 142,442 124,484 C 110,514 96,520 82,508 Z"
    live_tufts, calm_tufts = _render_meadow_tufts("core", tufts, 20.0)
    return [
        '<g class="pup-live" pointer-events="none">%s</g>' % "".join(live_tufts),
        '<g class="pup-calm" pointer-events="none">%s</g>' % "".join(calm_tufts),
        _render_ambient_butterfly("core", "bfm", cameo_path, "19.5s", scale=1.48, flap_dur="0.42s", begin="-5.2s"),
        '<g class="pup-calm" transform="translate(74 520.2) scale(1.46 1.46)" pointer-events="none"><use href="#core-bfm1"/></g>',
    ]
