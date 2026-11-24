import math

from theme import (
    BG_WELL,
    BORDER_SUBTLE,
    BORDER_WARM,
    CREAM,
    EMERALD_MID,
    EMERALD_SOFT,
    FIREFLY_AMBER,
    FIREFLY_GOLD,
    FONT_DISPLAY,
    FONT_MONO,
    INK_FAINT,
    INK_MUTED,
    INK_PRIMARY,
    INK_SECOND,
    IVORY,
    IVORY_WARM,
    LANG_PALETTE,
    REDUCED_MOTION_STYLE,
    SKY_SOFT,
    TEAL_MIST,
    esc,
    fireflies_layer,
    nocturne_card,
    nocturne_defs,
    num,
    star_path,
    text,
)

CARD_W = 392
CARD_H = 248


def _art_v3():
    cx, cy = 196.0, 74.0
    elems = [
        '<ellipse cx="196" cy="112" rx="108" ry="18" fill="%s" fill-opacity="0.06"/>' % EMERALD_SOFT,
        '<polygon points="94,96 184,58 298,84 208,122" fill="#0b1322" stroke="%s" stroke-width="1.15" stroke-linejoin="round"/>' % BORDER_WARM,
        '<polygon points="94,96 208,122 208,127 94,101" fill="#070c16" stroke="%s" stroke-width="0.9"/>' % BORDER_SUBTLE,
        '<polygon points="208,122 298,84 298,89 208,127" fill="#09101d" stroke="%s" stroke-width="0.9"/>' % BORDER_SUBTLE,
        '<line x1="124" y1="83" x2="238" y2="109" stroke="%s" stroke-width="0.75" stroke-opacity="0.45"/>' % TEAL_MIST,
        '<line x1="154" y1="71" x2="268" y2="97" stroke="%s" stroke-width="0.75" stroke-opacity="0.35"/>' % TEAL_MIST,
        '<line x1="146" y1="108" x2="236" y2="70" stroke="%s" stroke-width="0.75" stroke-opacity="0.35"/>' % TEAL_MIST,
        '<polygon points="116,76 186,46 258,63 188,93" fill="#101b2e" fill-opacity="0.88" stroke="%s" stroke-width="1.2" stroke-linejoin="round"/>' % EMERALD_SOFT,
        '<polygon points="127,74 156,61 174,65 145,78" fill="%s" fill-opacity="0.16" stroke="%s" stroke-width="0.85"/>' % (EMERALD_SOFT, EMERALD_SOFT),
        '<polygon points="162,59 185,49 245,63 222,73" fill="%s" fill-opacity="0.10" stroke="%s" stroke-width="0.85"/>' % (SKY_SOFT, SKY_SOFT),
        '<polygon points="152,80 181,67 216,75 187,88" fill="%s" fill-opacity="0.12" stroke="%s" stroke-width="0.8"/>' % (CREAM, CREAM),
        '<path d="M132,48 A68,36 0 0,1 264,52" fill="none" stroke="%s" stroke-width="0.9" stroke-dasharray="3 4" stroke-opacity="0.65"/>' % CREAM,
    ]
    gx, gy = 248.0, 48.0
    top = (gx, gy - 20.0)
    bot = (gx, gy + 18.0)
    ring = [
        (gx - 18.0, gy - 2.0),
        (gx - 4.0, gy + 6.0),
        (gx + 18.0, gy - 1.0),
        (gx + 4.0, gy - 8.0),
    ]
    elems.append('<polygon points="%s,%s %s,%s %s,%s" fill="%s" fill-opacity="0.18" stroke="%s" stroke-width="1.05"/>' % (
        num(top[0]), num(top[1]), num(ring[0][0]), num(ring[0][1]), num(ring[1][0]), num(ring[1][1]), CREAM, CREAM
    ))
    elems.append('<polygon points="%s,%s %s,%s %s,%s" fill="%s" fill-opacity="0.26" stroke="%s" stroke-width="1.05"/>' % (
        num(top[0]), num(top[1]), num(ring[1][0]), num(ring[1][1]), num(ring[2][0]), num(ring[2][1]), FIREFLY_GOLD, CREAM
    ))
    elems.append('<polygon points="%s,%s %s,%s %s,%s" fill="#0f172a" fill-opacity="0.65" stroke="%s" stroke-width="0.95"/>' % (
        num(bot[0]), num(bot[1]), num(ring[0][0]), num(ring[0][1]), num(ring[1][0]), num(ring[1][1]), EMERALD_SOFT
    ))
    elems.append('<polygon points="%s,%s %s,%s %s,%s" fill="%s" fill-opacity="0.12" stroke="%s" stroke-width="0.95"/>' % (
        num(bot[0]), num(bot[1]), num(ring[1][0]), num(ring[1][1]), num(ring[2][0]), num(ring[2][1]), EMERALD_SOFT, EMERALD_SOFT
    ))
    elems.append('<circle cx="%s" cy="%s" r="2.2" fill="%s"/>' % (num(top[0]), num(top[1]), IVORY_WARM))
    return elems


def _art_v2():
    elems = [
        '<ellipse cx="196" cy="114" rx="112" ry="12" fill="none" stroke="%s" stroke-width="0.8" stroke-opacity="0.28"/>' % SKY_SOFT,
        '<ellipse cx="196" cy="114" rx="72" ry="6.5" fill="none" stroke="%s" stroke-width="0.8" stroke-opacity="0.38"/>' % CREAM,
        '<rect x="86" y="84" width="38" height="22" rx="3" fill="#0d1525" stroke="%s" stroke-width="1.05"/>' % BORDER_WARM,
        '<line x1="93" y1="91" x2="116" y2="91" stroke="%s" stroke-width="1.2"/>' % SKY_SOFT,
        '<line x1="93" y1="96" x2="111" y2="96" stroke="%s" stroke-width="1.1" stroke-opacity="0.65"/>' % SKY_SOFT,
        '<rect x="268" y="84" width="38" height="22" rx="3" fill="#0d1525" stroke="%s" stroke-width="1.05"/>' % BORDER_WARM,
        '<rect x="275" y="89" width="10" height="10" rx="1.5" fill="%s" fill-opacity="0.2" stroke="%s" stroke-width="0.9"/>' % (EMERALD_SOFT, EMERALD_SOFT),
        '<rect x="289" y="89" width="10" height="10" rx="1.5" fill="%s" fill-opacity="0.2" stroke="%s" stroke-width="0.9"/>' % (CREAM, CREAM),
        '<path d="M138,108 L142,38 L146,108" fill="none" stroke="%s" stroke-width="1.35" stroke-linejoin="round"/>' % CREAM,
        '<path d="M246,108 L250,38 L254,108" fill="none" stroke="%s" stroke-width="1.35" stroke-linejoin="round"/>' % CREAM,
        '<line x1="139" y1="56" x2="145" y2="56" stroke="%s" stroke-width="1.1"/>' % CREAM,
        '<line x1="247" y1="56" x2="253" y2="56" stroke="%s" stroke-width="1.1"/>' % CREAM,
        '<line x1="80" y1="84" x2="312" y2="84" stroke="%s" stroke-width="1.6"/>' % IVORY,
        '<line x1="84" y1="87.5" x2="308" y2="87.5" stroke="%s" stroke-width="0.85" stroke-opacity="0.65"/>' % SKY_SOFT,
        '<path d="M142,40 Q196,82 250,40" fill="none" stroke="%s" stroke-width="1.35"/>' % FIREFLY_GOLD,
        '<path d="M84,84 Q116,70 142,40" fill="none" stroke="%s" stroke-width="1.15" stroke-opacity="0.85"/>' % CREAM,
        '<path d="M250,40 Q276,70 308,84" fill="none" stroke="%s" stroke-width="1.15" stroke-opacity="0.85"/>' % CREAM,
    ]
    for i in range(1, 8):
        t = i / 8.0
        hx = 142.0 + t * 108.0
        cy_top = 40.0 + 4.0 * t * (1.0 - t) * 21.0
        elems.append('<line x1="%s" y1="%s" x2="%s" y2="84" stroke="%s" stroke-width="0.75" stroke-opacity="0.5"/>' % (
            num(hx), num(cy_top), num(hx), CREAM
        ))
    elems.append('<circle cx="142" cy="38" r="2.2" fill="%s"/>' % IVORY_WARM)
    elems.append('<circle cx="250" cy="38" r="2.2" fill="%s"/>' % IVORY_WARM)
    return elems


def _art_v1():
    return [
        '<ellipse cx="196" cy="113" rx="96" ry="14" fill="%s" fill-opacity="0.06"/>' % FIREFLY_GOLD,
        '<path d="M108,102 Q152,110 196,101 Q240,110 284,102" fill="none" stroke="%s" stroke-width="2.0" stroke-linecap="round"/>' % BORDER_WARM,
        '<path d="M112,98 Q152,86 196,98 L196,60 Q152,48 112,60 Z" fill="#0d1526" stroke="%s" stroke-width="1.25" stroke-linejoin="round"/>' % CREAM,
        '<path d="M196,98 Q240,86 280,98 L280,60 Q240,48 196,60 Z" fill="#101a2e" stroke="%s" stroke-width="1.25" stroke-linejoin="round"/>' % CREAM,
        '<path d="M118,93 Q154,83 196,94" fill="none" stroke="%s" stroke-width="0.8" stroke-opacity="0.5"/>' % CREAM,
        '<path d="M196,94 Q238,83 274,93" fill="none" stroke="%s" stroke-width="0.8" stroke-opacity="0.5"/>' % CREAM,
        '<line x1="126" y1="68" x2="178" y2="65" stroke="%s" stroke-width="0.95" stroke-opacity="0.55"/>' % INK_MUTED,
        '<line x1="126" y1="75" x2="182" y2="72" stroke="%s" stroke-width="0.95" stroke-opacity="0.45"/>' % INK_MUTED,
        '<line x1="126" y1="82" x2="170" y2="79" stroke="%s" stroke-width="0.95" stroke-opacity="0.4"/>' % INK_MUTED,
        '<line x1="212" y1="65" x2="264" y2="68" stroke="%s" stroke-width="0.95" stroke-opacity="0.55"/>' % INK_MUTED,
        '<line x1="212" y1="72" x2="266" y2="75" stroke="%s" stroke-width="0.95" stroke-opacity="0.45"/>' % INK_MUTED,
        '<line x1="212" y1="79" x2="254" y2="82" stroke="%s" stroke-width="0.95" stroke-opacity="0.4"/>' % INK_MUTED,
        '<path d="M196,60 L196,108 L191,104" fill="none" stroke="%s" stroke-width="1.3"/>' % FIREFLY_GOLD,
        '<g transform="translate(152 30) rotate(-9)">'
        '<rect x="0" y="0" width="38" height="24" rx="3.5" fill="#0f1a2e" stroke="%s" stroke-width="1.05"/>'
        '<line x1="7" y1="8" x2="29" y2="8" stroke="%s" stroke-width="1.2"/>'
        '<line x1="7" y1="14" x2="22" y2="14" stroke="%s" stroke-width="1" stroke-opacity="0.65"/>'
        "</g>" % (SKY_SOFT, SKY_SOFT, INK_SECOND),
        '<g transform="translate(204 24) rotate(8)">'
        '<rect x="0" y="0" width="40" height="25" rx="3.5" fill="#121d31" stroke="%s" stroke-width="1.1"/>'
        '<line x1="7" y1="8" x2="31" y2="8" stroke="%s" stroke-width="1.2"/>'
        '<line x1="7" y1="14" x2="25" y2="14" stroke="%s" stroke-width="1" stroke-opacity="0.7"/>'
        "</g>" % (FIREFLY_GOLD, CREAM, INK_SECOND),
        '<g transform="translate(178 14)">'
        '<rect x="0" y="0" width="36" height="22" rx="3.5" fill="#142238" stroke="%s" stroke-width="1.15"/>'
        '<circle cx="9" cy="11" r="2.5" fill="%s"/>'
        '<line x1="15" y1="9" x2="29" y2="9" stroke="%s" stroke-width="1.1"/>'
        '<line x1="15" y1="14" x2="25" y2="14" stroke="%s" stroke-width="0.9" stroke-opacity="0.7"/>'
        "</g>" % (EMERALD_SOFT, EMERALD_SOFT, IVORY, INK_SECOND),
    ]


def _render_single_card(prefix, title, subtitle, domain_tag, accent, art_nodes, meta, seed):
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
    parts.extend(
        [
            '<radialGradient id="%s-stage-glow" cx="50%%" cy="52%%" r="54%%">' % prefix,
            '<stop offset="0%%" stop-color="%s" stop-opacity="0.16"/>' % accent,
            '<stop offset="100%%" stop-color="%s" stop-opacity="0"/>' % BG_WELL,
            "</radialGradient>",
            '<clipPath id="%s-art-clip"><rect x="16" y="16" width="360" height="120" rx="11"/></clipPath>' % prefix,
            "</defs>",
        ]
    )
    parts.extend(frame_nodes)

    parts.append('<rect x="16" y="16" width="360" height="120" rx="11" fill="%s" stroke="%s" stroke-width="1"/>' % (BG_WELL, BORDER_SUBTLE))
    parts.append('<g clip-path="url(#%s-art-clip)">' % prefix)
    parts.append('<rect x="16" y="16" width="360" height="120" fill="url(#%s-stage-glow)"/>' % prefix)
    parts.extend(art_nodes)
    parts.extend(fireflies_layer(prefix, 376, 132, ambient_count=14, drifter_count=6, seed=seed))
    parts.append("</g>")

    parts.append(text(24, 166, title, INK_PRIMARY, 18.5, "start", "700", ' letter-spacing="-0.2"', FONT_DISPLAY))
    if domain_tag:
        parts.append(text(CARD_W - 24, 165, domain_tag, accent, 10.2, "end", "500"))
    parts.append(text(24, 189, subtitle, INK_SECOND, 11.5, "start", "400", "", FONT_DISPLAY))

    parts.append('<line x1="24" y1="206" x2="%d" y2="206" stroke="%s" stroke-width="1"/>' % (CARD_W - 24, BORDER_SUBTLE))

    parts.append('<circle cx="29" cy="224.5" r="3.8" fill="%s"/>' % lang_col)
    parts.append(text(40, 228.5, lang, INK_PRIMARY, 11, "start", "600"))
    parts.append('<path d="%s" fill="%s"/>' % (star_path(142, 224.2, 5.5, 2.3), FIREFLY_GOLD))
    parts.append(text(153, 228.5, str(stars), CREAM, 11, "start", "700"))
    parts.append(
        '<path d="M%d 229 L%d 220 M%d 220 H%d M%d 220 V226" fill="none" stroke="%s" stroke-width="1.35" stroke-linecap="round" stroke-linejoin="round"/>'
        % (CARD_W - 33, CARD_W - 24, CARD_W - 30, CARD_W - 24, CARD_W - 24, INK_MUTED)
    )

    parts.append("</svg>")
    return "\n".join(parts)


def render_flagship_cards(repo_map):
    specs = [
        (
            "card-fforum-v3.svg",
            "ff3",
            "f_forumv3",
            "F-Forum v3",
            "Xưởng lắp ráp UI/3D & không gian cộng đồng",
            "fforum3.vercel.app",
            EMERALD_MID,
            _art_v3(),
            303,
        ),
        (
            "card-fforum-v2.svg",
            "ff2",
            "F-Forum_v2",
            "F-Forum v2",
            "Kiến trúc cầu nối phân tầng thế hệ thứ hai",
            "v2 bridge",
            SKY_SOFT,
            _art_v2(),
            202,
        ),
        (
            "card-fforum-v1.svg",
            "ff1",
            "f-forum",
            "F-Forum v1",
            "Diễn đàn học đường, câu lạc bộ & kho đề thi",
            "f-forum.vercel.app",
            FIREFLY_GOLD,
            _art_v1(),
            101,
        ),
    ]
    out = {}
    for fname, prefix, key, title, subtitle, domain_tag, accent, art_nodes, seed in specs:
        out[fname] = _render_single_card(prefix, title, subtitle, domain_tag, accent, art_nodes, repo_map.get(key, {}), seed)
    return out
