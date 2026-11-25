# SPDX-License-Identifier: MIT
import datetime
import json
import math
import os
import shutil
import urllib.request

from cards import render_flagship_cards
from pixel_dog_svg import nocturne_garden_pup, pup_defs, starry_matrix_pup
from theme import (
    BG_CONSOLE,
    BG_NIGHT,
    BORDER_SUBTLE,
    BORDER_WARM,
    CADMIUM,
    CERULEAN,
    CREAM,
    EMERALD_MID,
    EMERALD_SOFT,
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
    MILKY_CORE,
    REDUCED_MOTION_STYLE,
    SKY_SOFT,
    TEAL_MIST,
    compact,
    esc,
    load_vangogh_scene,
    nocturne_card,
    nocturne_defs,
    num,
    raw_text,
    shade_hex,
    solar_system_orrery,
    star_path,
    text,
    van_gogh_starry_backdrop,
)

USERNAME = os.environ.get("GH_PROFILE_USERNAME", "broamstuck-cybr")
DISPLAY = os.environ.get("GH_PROFILE_DISPLAY", "BroAmStuck")
TOKEN = os.environ.get("GITHUB_TOKEN", "") or os.environ.get("GH_TOKEN", "")
API = (os.environ.get("GITHUB_API_URL", "") or "https://api.github.com").rstrip("/")
GQL = (os.environ.get("GITHUB_GRAPHQL_URL", "") or "https://api.github.com/graphql").rstrip("/")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
DOCS_ASSETS = os.path.join(ROOT, "docs", "assets")


def request_json(url, payload=None):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "broamstuck-profile-generator",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if TOKEN:
        headers["Authorization"] = "Bearer " + TOKEN
    body = None
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    call = urllib.request.Request(url, data=body, headers=headers)
    try:
        with urllib.request.urlopen(call, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as error:
        print("warning: %s %s" % (url, error))
        return None


def clock(stamp):
    if not stamp:
        return "--:--"
    try:
        moment = datetime.datetime.fromisoformat(stamp.replace("Z", "+00:00"))
        return moment.astimezone(datetime.timezone.utc).strftime("%H:%M")
    except Exception:
        return stamp[11:16] or "--:--"


def repo_label(full_name):
    return (full_name or "").split("/")[-1]


def truncate_clean(body, max_len):
    text_s = (body or "").strip()
    if len(text_s) <= max_len:
        return text_s
    cut = text_s[: max_len - 1]
    if " " in cut and cut.rfind(" ") >= max_len // 2:
        cut = cut[: cut.rfind(" ")]
    return cut.rstrip(" ,;:-/.") + "…"


def collect_events(limit=8):
    commits = []
    seen = set()
    events = request_json("%s/users/%s/events/public?per_page=100" % (API, USERNAME))
    if isinstance(events, list):
        for event in events:
            if event.get("type") != "PushEvent":
                continue
            for commit in reversed((event.get("payload") or {}).get("commits") or []):
                sha = (commit.get("sha") or "")[:7]
                if not sha or sha in seen:
                    continue
                seen.add(sha)
                repo_s = repo_label((event.get("repo") or {}).get("name"))
                commits.append(
                    {
                        "sha": sha,
                        "repo": repo_s,
                        "message": (commit.get("message") or "").split("\n")[0].strip(),
                        "time": clock(event.get("created_at")),
                        "url": "https://github.com/%s/%s/commit/%s" % (USERNAME, repo_s, commit.get("sha") or sha),
                    }
                )
                if len(commits) >= limit:
                    return commits
    if len(commits) < limit:
        search = request_json(
            "%s/search/commits?q=author:%s&sort=committer-date&order=desc&per_page=%d"
            % (API, USERNAME, limit * 3)
        )
        for item in ((search or {}).get("items") or []):
            sha = (item.get("sha") or "")[:7]
            if not sha or sha in seen:
                continue
            seen.add(sha)
            detail = item.get("commit") or {}
            repo_s = repo_label((item.get("repository") or {}).get("full_name"))
            commits.append(
                {
                    "sha": sha,
                    "repo": repo_s,
                    "message": (detail.get("message") or "").split("\n")[0].strip(),
                    "time": clock((detail.get("committer") or {}).get("date")),
                    "url": item.get("html_url") or ("https://github.com/%s/%s" % (USERNAME, repo_s)),
                }
            )
            if len(commits) >= limit:
                break
    return commits[:limit]


def load_cached_telemetry():
    path = os.path.join(ASSETS, "telemetry.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def collect():
    data = {
        "days": {},
        "weeks": [],
        "total": 0,
        "commits": 0,
        "stars": 0,
        "repos": 0,
        "repo_map": {},
        "langs": [],
        "lang_repos": {},
        "lang_stars": {},
        "events": [],
        "bytes": 0,
    }
    if TOKEN:
        query = (
            "query($login:String!){user(login:$login){"
            "contributionsCollection{totalCommitContributions "
            "contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}"
            "repositories(first:100,ownerAffiliations:OWNER,isFork:false,privacy:PUBLIC){totalCount "
            "nodes{name description homepageUrl stargazerCount diskUsage primaryLanguage{name} "
            "languages(first:20,orderBy:{field:SIZE,direction:DESC})"
            "{edges{size node{name}}}}}}}"
        )
        result = request_json(GQL, {"query": query, "variables": {"login": USERNAME}})
        if result and result.get("data") and result["data"].get("user"):
            user = result["data"]["user"]
            collection = user.get("contributionsCollection") or {}
            calendar = collection.get("contributionCalendar") or {}
            data["total"] = int(calendar.get("totalContributions") or 0)
            data["commits"] = int(collection.get("totalCommitContributions") or 0)
            for week in calendar.get("weeks") or []:
                week_sum = 0
                for day in week.get("contributionDays") or []:
                    c = int(day.get("contributionCount") or 0)
                    data["days"][day.get("date")] = c
                    week_sum += c
                data["weeks"].append(week_sum)
            repos = user.get("repositories") or {}
            data["repos"] = int(repos.get("totalCount") or 0)
            sizes = {}
            lang_repos = {}
            lang_stars = {}
            for node in repos.get("nodes") or []:
                name = node.get("name") or ""
                stars = int(node.get("stargazerCount") or 0)
                data["stars"] += stars
                if name:
                    data["repo_map"][name] = {
                        "name": name,
                        "description": node.get("description") or "",
                        "homepage": node.get("homepageUrl") or "",
                        "stars": stars,
                        "lang": ((node.get("primaryLanguage") or {}).get("name")) or "TypeScript",
                    }
                seen_in_repo = set()
                for edge in (node.get("languages") or {}).get("edges") or []:
                    lang_name = ((edge.get("node") or {}).get("name")) or ""
                    edge_size = int(edge.get("size") or 0)
                    if lang_name and edge_size > 0:
                        data["bytes"] += edge_size
                        sizes[lang_name] = sizes.get(lang_name, 0) + edge_size
                        if lang_name not in seen_in_repo:
                            seen_in_repo.add(lang_name)
                            lang_repos[lang_name] = lang_repos.get(lang_name, 0) + 1
                            lang_stars[lang_name] = lang_stars.get(lang_name, 0) + max(1, stars + 1)
            data["langs"] = sorted(sizes.items(), key=lambda item: item[1], reverse=True)
            data["lang_repos"] = lang_repos
            data["lang_stars"] = lang_stars

    if not data["days"]:
        cached = load_cached_telemetry()
        if cached:
            m = cached.get("metrics") or {}
            data["days"] = cached.get("days") or {}
            data["weeks"] = ((cached.get("streaks") or {}).get("weeks52")) or []
            data["total"] = int(m.get("contributions") or 0)
            data["commits"] = int(m.get("commits") or 0)
            data["stars"] = int(m.get("stars") or 0)
            data["repos"] = int(m.get("repos") or 0)
            data["bytes"] = int(m.get("bytes") or 0)
            for l in cached.get("langs5d") or []:
                nm = l["name"]
                data["langs"].append((nm, int(l.get("bytes") or 0)))
                data["lang_repos"][nm] = int(l.get("repos") or 1)
                data["lang_stars"][nm] = max(1, int(round((float(l.get("d4Gravity") or 0.5) - 0.38) * 10)))
            data["langs"].sort(key=lambda item: item[1], reverse=True)
            for f in cached.get("forums") or []:
                r_key = f.get("repo")
                if r_key:
                    data["repo_map"][r_key] = {
                        "name": r_key,
                        "lang": f.get("lang") or "TypeScript",
                        "stars": int(f.get("stars") or 1),
                    }
            data["events"] = cached.get("events") or []

    fresh_events = collect_events()
    if fresh_events:
        data["events"] = fresh_events
    return data


def compute_streaks(day_map, weeks):
    ordered = sorted(day_map.items())
    longest = 0
    current = 0
    run = 0
    peak = 0
    for _, count in ordered:
        if count > peak:
            peak = count
        if count > 0:
            run += 1
            if run > longest:
                longest = run
        else:
            run = 0
    for _, count in reversed(ordered):
        if count > 0:
            current += 1
        else:
            break
    w52 = list(weeks[-52:])
    if len(w52) < 52:
        w52 = ([0] * (52 - len(w52))) + w52
    return {"longest": longest, "current": current, "peak": peak, "weeks52": w52}


def lang_percentages(langs):
    total = sum(size for _, size in langs) or 1
    raw = [size * 100.0 / total for _, size in langs]
    counts = [int(value) for value in raw]
    order = sorted(range(len(raw)), key=lambda i: raw[i] - counts[i], reverse=True)
    for i in order[: max(0, 100 - sum(counts))]:
        counts[i] += 1
    return counts


def starry_matrix_svg(day_map, total_contribs, streaks):
    width, height = 1200, 492
    clip_defs, frame_nodes = nocturne_card(width, height, "mat", radius=18)
    weeks52 = streaks["weeks52"]
    max_w = max(weeks52) if any(weeks52) else 1

    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 492" width="1200" height="492" role="img" aria-label="Van Gogh Starry Night Observatory and 52-Week Contribution Constellation">',
        REDUCED_MOTION_STYLE,
        "<defs>",
    ]
    parts.extend(nocturne_defs("mat"))
    parts.extend(clip_defs)
    parts.extend(pup_defs("mat"))
    parts.extend(
        [
            '<clipPath id="mat-dome-clip"><rect x="16" y="16" width="1168" height="236" rx="10"/></clipPath>',
            '<clipPath id="mat-well-clip"><rect x="16" y="290" width="1168" height="186" rx="10"/></clipPath>',
            '<linearGradient id="mat-top-scrim" x1="0" y1="0" x2="0" y2="1">',
            '<stop offset="0%" stop-color="#040916" stop-opacity="0.72"/>',
            '<stop offset="100%" stop-color="#040916" stop-opacity="0"/>',
            "</linearGradient>",
            '<linearGradient id="mat-left-scrim" x1="0" y1="0" x2="1" y2="0">',
            '<stop offset="0%" stop-color="#040916" stop-opacity="0.72"/>',
            '<stop offset="100%" stop-color="#040916" stop-opacity="0"/>',
            "</linearGradient>",
            '<linearGradient id="mat-water" x1="0" y1="0" x2="1" y2="0">',
            '<stop offset="0%%" stop-color="%s" stop-opacity="0"/>' % BORDER_WARM,
            '<stop offset="28%%" stop-color="%s" stop-opacity="0.58"/>' % CERULEAN,
            '<stop offset="66%%" stop-color="%s" stop-opacity="0.74"/>' % CREAM,
            '<stop offset="100%%" stop-color="%s" stop-opacity="0"/>' % BORDER_WARM,
            "</linearGradient>",
            "</defs>",
        ]
    )
    parts.extend(frame_nodes)
    parts.append('<g clip-path="url(#mat-clip)">')

    parts.append('<g clip-path="url(#mat-dome-clip)">')
    parts.append('<rect x="16" y="16" width="1168" height="236" fill="#061126"/>')
    parts.append('<g transform="translate(16 16)">')
    parts.extend(
        van_gogh_starry_backdrop(
            "mat-pan",
            1168,
            236,
            avoid_boxes=[],
            opacity_scale=0.98,
            glyph_stride=1,
            stroke_limit=2900,
            layer_key="panorama",
        )
    )
    parts.extend(solar_system_orrery(cx=560.0, cy=118.0, scale_x=296.0, scale_y=56.0, tilt_deg=-9.5, opacity=0.78))
    parts.append("</g>")
    parts.append("</g>")
    parts.append('<rect x="16" y="16" width="1168" height="236" rx="10" fill="none" stroke="%s" stroke-width="0.85"/>' % BORDER_WARM)
    parts.append('<line x1="120" y1="252" x2="1080" y2="252" stroke="url(#mat-sheen)" stroke-width="0.85"/>')

    parts.append(
        raw_text(
            24,
            277,
            '<tspan fill="%s" font-weight="700">%s</tspan><tspan fill="%s">&#160;contributions&#160;&#160;&#183;&#160;&#160;</tspan><tspan fill="%s" font-weight="600">%dd</tspan><tspan fill="%s">&#160;streak</tspan>'
            % (CREAM, "{:,}".format(total_contribs), INK_SECOND, SKY_SOFT, streaks["longest"], INK_SECOND),
            INK_PRIMARY,
            13.2,
            "start",
            "500",
            "",
            FONT_DISPLAY,
        )
    )

    parts.append(text(1028, 277, "Less", INK_MUTED, 10.2, "end", "500", "", FONT_DISPLAY))
    for lx, pts_n, r_out, r_in, lcol in (
        (1044, 4, 3.0, 1.0, "#2c4875"),
        (1062, 4, 4.2, 1.6, SKY_SOFT),
        (1082, 6, 5.0, 2.0, EMERALD_MID),
        (1104, 8, 5.8, 2.3, FIREFLY_GOLD),
        (1128, 8, 6.8, 2.6, CADMIUM),
    ):
        parts.append('<path d="%s" fill="%s"/>' % (star_path(lx, 273, r_out, r_in, pts_n), lcol))
    parts.append(text(1144, 277, "More", INK_MUTED, 10.2, "start", "500", "", FONT_DISPLAY))

    parts.append('<g clip-path="url(#mat-well-clip)">')
    parts.append('<rect x="16" y="290" width="1168" height="186" fill="#040916"/>')
    parts.append('<g transform="translate(16 290)">')
    parts.extend(
        van_gogh_starry_backdrop(
            "mat-sky",
            1168,
            186,
            avoid_boxes=[],
            opacity_scale=0.80,
            glyph_stride=1,
            stroke_limit=1650,
            layer_key="sky",
        )
    )
    parts.append('<rect x="0" y="0" width="1168" height="186" fill="#040916" fill-opacity="0.58"/>')
    parts.append('<rect x="0" y="0" width="1168" height="28" fill="url(#mat-top-scrim)"/>')
    parts.append('<rect x="0" y="0" width="62" height="186" fill="url(#mat-left-scrim)"/>')
    parts.append("</g>")

    ordered_dates = sorted(day_map.keys())
    today = datetime.date.fromisoformat(ordered_dates[-1]) if ordered_dates else datetime.date.today()
    days_since_sun = (today.weekday() + 1) % 7
    end_sunday = today - datetime.timedelta(days=days_since_sun)
    start_sunday = end_sunday - datetime.timedelta(weeks=51)

    grid_x = 74.0
    grid_y = 324.0
    pitch_x = 21.0
    pitch_y = 17.6

    month_names = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
    last_month = -1
    last_printed_w = -9
    for w in range(52):
        d = start_sunday + datetime.timedelta(weeks=w)
        if d.month != last_month:
            if w == 0 and d.day > 16:
                last_month = d.month
                continue
            last_month = d.month
            if w - last_printed_w >= 3:
                parts.append(text(grid_x + w * pitch_x, 308, month_names[d.month - 1], INK_SECOND, 10.2, "middle", "600", "", FONT_DISPLAY))
                last_printed_w = w

    for row, lbl in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        parts.append(text(56, grid_y + row * pitch_y + 3.5, lbl, INK_MUTED, 9.6, "end", "500"))

    coords = {}
    for w in range(52):
        for r in range(7):
            d = start_sunday + datetime.timedelta(weeks=w, days=r)
            if d > today:
                continue
            cx = grid_x + w * pitch_x
            cy = grid_y + r * pitch_y
            c = int(day_map.get(d.isoformat(), 0))
            coords[(w, r)] = (cx, cy, c, d)

    parts.append('<g stroke-linecap="round">')
    for (w, r), (cx, cy, c, _) in coords.items():
        if c < 2:
            continue
        nw, nr = (w, r + 1) if r < 6 else (w + 1, 0)
        if (nw, nr) in coords and coords[(nw, nr)][2] >= 2 and abs(nw - w) <= 1 and not (r == 6 and nw != w):
            nx, ny, nc, _ = coords[(nw, nr)]
            col = CADMIUM if (c + nc) >= 22 else SKY_SOFT
            op = min(0.74, 0.28 + (c + nc) / 82.0)
            parts.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="0.92" stroke-opacity="%s"/>' % (num(cx), num(cy), num(nx), num(ny), col, num(op)))
            if (c + nc) >= 24:
                parts.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="#ffffff" stroke-width="0.38" stroke-opacity="0.55"/>' % (num(cx), num(cy), num(nx), num(ny)))
        if (w + 1, r) in coords and coords[(w + 1, r)][2] >= 4 and c >= 4:
            nx, ny, nc, _ = coords[(w + 1, r)]
            col = CREAM if (c + nc) >= 30 else TEAL_MIST
            op = min(0.62, 0.24 + (c + nc) / 96.0)
            parts.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="0.82" stroke-opacity="%s"/>' % (num(cx), num(cy), num(nx), num(ny), col, num(op)))
    parts.append("</g>")

    for (w, r), (cx, cy, c, _) in coords.items():
        if c == 0:
            parts.append(
                '<path d="M%s %s H%s M%s %s V%s" stroke="#28436f" stroke-width="0.72" stroke-opacity="0.84"/>'
                % (num(cx - 1.6, 1), num(cy, 1), num(cx + 1.6, 1), num(cx, 1), num(cy - 1.6, 1), num(cy + 1.6, 1))
            )
        elif c <= 3:
            parts.append('<path d="%s" fill="%s"/>' % (star_path(cx, cy, 4.2, 1.4, 4), SKY_SOFT))
        elif c <= 10:
            parts.append('<circle cx="%s" cy="%s" r="5.6" fill="%s" fill-opacity="0.12"/>' % (num(cx, 1), num(cy, 1), EMERALD_SOFT))
            parts.append('<path d="%s" fill="%s" stroke="%s" stroke-width="0.42"/>' % (star_path(cx, cy, 5.4, 2.0, 6), EMERALD_SOFT, IVORY_WARM))
        elif c <= 24:
            parts.append('<circle cx="%s" cy="%s" r="7.4" fill="%s" fill-opacity="0.14"/>' % (num(cx, 1), num(cy, 1), FIREFLY_GOLD))
            parts.append('<circle cx="%s" cy="%s" r="6.3" fill="none" stroke="%s" stroke-width="0.78" stroke-dasharray="2.8 2.1" stroke-opacity="0.82"/>' % (num(cx, 1), num(cy, 1), CADMIUM))
            parts.append('<path d="%s" fill="%s" stroke="#ffffff" stroke-width="0.48"/>' % (star_path(cx, cy, 5.6, 2.0, 8), FIREFLY_GOLD))
        else:
            parts.append('<circle cx="%s" cy="%s" r="9.4" fill="%s" fill-opacity="0.18"/>' % (num(cx, 1), num(cy, 1), CADMIUM))
            parts.append(
                '<circle cx="%s" cy="%s" r="7.8" fill="none" stroke="%s" stroke-width="0.9" stroke-dasharray="3.2 2.1" stroke-opacity="0.92">'
                '<animateTransform attributeName="transform" type="rotate" from="0 %s %s" to="360 %s %s" dur="18s" repeatCount="indefinite"/>'
                "</circle>"
                % (num(cx, 1), num(cy, 1), CADMIUM, num(cx, 1), num(cy, 1), num(cx, 1), num(cy, 1))
            )
            parts.append('<path d="%s" fill="%s" stroke="#ffffff" stroke-width="0.58"/>' % (star_path(cx, cy, 6.9, 2.4, 8), IVORY_WARM))

    water_y = 447.0
    parts.append('<line x1="44" y1="%s" x2="1168" y2="%s" stroke="url(#mat-water)" stroke-width="0.9"/>' % (num(water_y), num(water_y)))
    for w in range(52):
        val = weeks52[w]
        if val <= 0:
            continue
        norm = (val / float(max_w)) ** 0.62
        wx = grid_x + w * pitch_x
        glyph_str = "≈~≈" if norm > 0.55 else ("~~" if norm > 0.25 else "~")
        col = CADMIUM if norm > 0.45 else SKY_SOFT
        parts.append(text(wx, water_y + 15 + (w % 2) * 5, glyph_str, col, 9.4, "middle", "600", ' opacity="%s"' % num(0.46 + norm * 0.50, 2)))

    parts.append("</g>")
    parts.append('<rect x="16" y="290" width="1168" height="186" rx="10" fill="none" stroke="%s" stroke-width="0.85"/>' % BORDER_WARM)
    parts.append('<line x1="250" y1="290" x2="960" y2="290" stroke="url(#mat-sheen)" stroke-width="0.85"/>')
    parts.extend(starry_matrix_pup())
    parts.append("</g>")
    parts.append("</svg>")
    return "\n".join(parts)


def _project_so4_5d(cx, cy, x, y, z, w_coord=1.0, hyper_angle=0.52):
    ca, sa = math.cos(hyper_angle), math.sin(hyper_angle)
    x4 = x * ca - w_coord * 18.0 * sa
    w4 = (x / 98.0) * sa + w_coord * ca
    z4 = z * math.cos(hyper_angle * 0.5) + w_coord * 14.0 * math.sin(hyper_angle * 0.5)

    w_scale = 1.0 / max(0.55, 1.36 - 0.30 * w4)
    xw = x4 * w_scale
    yw = y * w_scale
    zw = z4 * w_scale

    yaw = math.radians(-24.0)
    tilt = math.radians(56.0)
    rx = xw * math.cos(yaw) - yw * math.sin(yaw)
    ry = xw * math.sin(yaw) + yw * math.cos(yaw)
    sx = cx + rx
    sy = cy + ry * math.cos(tilt) - zw * math.sin(tilt)
    return sx, sy, ry


def render_stack_crystal(langs, lang_repos, lang_stars):
    cx, cy = 712.0, 206.0
    radius_max = 94.0
    crown_z = 58.0
    apex_z = 74.0

    axes = ["HTML", "TypeScript", "JavaScript", "CSS", "Python", "Shell"]
    lang_map = dict(langs)
    pcts = lang_percentages(langs)
    pct_map = {name: pcts[i] for i, (name, _) in enumerate(langs)}
    total_bytes = sum(size for _, size in langs) or 1
    max_repos = max([lang_repos.get(a, 1) for a in axes] + [1])
    max_stars = max([lang_stars.get(a, 1) for a in axes] + [1])

    elems = [
        text(508, 42, "Stack Architecture", INK_PRIMARY, 14.0, "start", "700", "", FONT_DISPLAY),
        '<ellipse cx="%s" cy="%s" rx="146" ry="96" fill="url(#core-crystal-glow)" pointer-events="none"/>' % (num(cx, 1), num(cy - 6.0, 1)),
    ]

    arm_pts = []
    for deg in range(0, 360, 6):
        rad = math.radians(deg)
        px, py, _ = _project_so4_5d(cx, cy, math.cos(rad) * (radius_max * 1.12), math.sin(rad) * (radius_max * 1.12), 0.0, 1.0, 0.0)
        arm_pts.append((px, py))
        if deg % 15 == 0:
            in_len = 0.99 if deg % 60 == 0 else 1.05
            ix, iy, _ = _project_so4_5d(cx, cy, math.cos(rad) * (radius_max * in_len), math.sin(rad) * (radius_max * in_len), 0.0, 1.0, 0.0)
            elems.append(
                '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s" stroke-opacity="%s"/>'
                % (num(ix, 1), num(iy, 1), num(px, 1), num(py, 1), CREAM if deg % 60 == 0 else SKY_SOFT, "0.95" if deg % 60 == 0 else "0.55", "0.84" if deg % 60 == 0 else "0.42")
            )
    elems.append(
        '<polygon points="%s" fill="#061226" fill-opacity="0.88" stroke="%s" stroke-width="0.95"/>'
        % (" ".join("%s,%s" % (num(px, 1), num(py, 1)) for px, py in arm_pts), BORDER_WARM)
    )

    for ring_f in (0.32, 0.56, 0.80, 1.00):
        h_pts = []
        for i in range(6):
            ang = -math.pi / 2.0 + i * math.pi / 3.0
            sx, sy, _ = _project_so4_5d(cx, cy, math.cos(ang) * radius_max * ring_f, math.sin(ang) * radius_max * ring_f, 0.0, 1.0, 0.0)
            h_pts.append("%s,%s" % (num(sx, 1), num(sy, 1)))
        elems.append('<polygon points="%s" fill="none" stroke="%s" stroke-width="0.65"/>' % (" ".join(h_pts), BORDER_WARM if ring_f >= 0.8 else BORDER_SUBTLE))

    origin_x, origin_y, _ = _project_so4_5d(cx, cy, 0.0, 0.0, 0.0, 1.0, 0.0)
    zenith_x, zenith_y, zenith_d = _project_so4_5d(cx, cy, 0.0, 0.0, apex_z, 1.0, 0.0)
    inner_zen_x, inner_zen_y, inner_zen_d = _project_so4_5d(cx, cy, 0.0, 0.0, apex_z * 0.58, -0.75, 0.42)

    outer_verts = []
    inner_verts = []
    crown_anchors = []
    base_anchors = []

    for i, axis in enumerate(axes):
        ang = -math.pi / 2.0 + i * math.pi / 3.0
        b_size = lang_map.get(axis, 0)
        r_count = lang_repos.get(axis, 0)
        s_weight = lang_stars.get(axis, 0)

        log_byte_norm = math.log10(max(1.0, b_size)) / math.log10(max(10.0, total_bytes)) if b_size > 0 else 0.15
        norm_repos = (r_count / float(max_repos)) if r_count > 0 else 0.16
        composite = 0.62 * log_byte_norm + 0.38 * norm_repos
        reach = 0.36 + 0.62 * min(1.0, composite)
        elev = 16.0 + crown_z * (0.42 * log_byte_norm + 0.58 * norm_repos)
        norm_grav = 0.38 + 0.56 * (s_weight / float(max_stars))

        wx = math.cos(ang) * radius_max * reach
        wy = math.sin(ang) * radius_max * reach
        vx, vy, depth = _project_so4_5d(cx, cy, wx, wy, elev, 1.0, 0.0)
        bx, by, bdepth = _project_so4_5d(cx, cy, wx, wy, 0.0, 1.0, 0.0)
        ix, iy, idepth = _project_so4_5d(
            cx, cy,
            wx * (0.58 * (0.68 + 0.32 * norm_grav)),
            wy * (0.58 * (0.68 + 0.32 * norm_grav)),
            elev * 0.56 + 9.0,
            -0.75,
            0.42,
        )

        ax_b = _project_so4_5d(cx, cy, math.cos(ang) * radius_max, math.sin(ang) * radius_max, 0.0, 1.0, 0.0)[:2]
        ax_c = _project_so4_5d(cx, cy, math.cos(ang) * radius_max, math.sin(ang) * radius_max, crown_z, 1.0, 0.0)[:2]
        base_anchors.append(ax_b)
        crown_anchors.append(ax_c)
        elems.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="0.8"/>' % (num(origin_x, 1), num(origin_y, 1), num(ax_b[0], 1), num(ax_b[1], 1), BORDER_SUBTLE))

        outer_verts.append({"i": i, "axis": axis, "vx": vx, "vy": vy, "bx": bx, "by": by, "depth": depth, "bdepth": bdepth})
        inner_verts.append({"i": i, "axis": axis, "ix": ix, "iy": iy, "depth": idepth})

    facets = []
    outer_tones = ("#fb923c", "#38bdf8", "#fbbf24", "#2dd4bf", "#4ade80", "#818cf8")
    facet_light = (0.94, 1.18, 1.24, 1.04, 0.78, 0.84)
    for i in range(6):
        j = (i + 1) % 6
        vi, vj = outer_verts[i], outer_verts[j]
        ii, ij = inner_verts[i], inner_verts[j]
        in_depth = (inner_zen_d + ii["depth"] + ij["depth"]) / 3.0 - 4.0
        facets.append((in_depth, "inner4d", [(inner_zen_x, inner_zen_y), (ii["ix"], ii["iy"]), (ij["ix"], ij["iy"])], CERULEAN if i % 2 == 0 else CADMIUM, 0.38, MILKY_CORE, 0.88))
        sk_depth = (vi["bdepth"] + vj["bdepth"] + vi["depth"] + vj["depth"]) / 4.0 - 2.0
        sk_lit = shade_hex("#102f58", facet_light[i], 0.06 if i in (1, 2) else 0.0)
        facets.append((sk_depth, "skirt", [(vi["bx"], vi["by"]), (vj["bx"], vj["by"]), (vj["vx"], vj["vy"]), (vi["vx"], vi["vy"])], sk_lit, 0.48 if i in (1, 2, 3) else 0.32, TEAL_MIST, 0.58))
        rf_depth = (zenith_d + vi["depth"] + vj["depth"]) / 3.0
        is_front = (vi["vy"] + vj["vy"]) / 2.0 > cy - 8.0
        rf_col = shade_hex(outer_tones[i], facet_light[i], 0.14 if i in (1, 2) else 0.02)
        rf_op = 0.36 if i in (1, 2) else (0.28 if is_front else 0.17)
        facets.append((rf_depth, "roof", [(zenith_x, zenith_y), (vi["vx"], vi["vy"]), (vj["vx"], vj["vy"])], rf_col, rf_op, IVORY_WARM if is_front else SKY_SOFT, 0.92 if is_front else 0.62))

    facets.sort(key=lambda item: item[0])
    for _, kind, pts, f_col, f_op, s_col, s_op in facets:
        pts_s = " ".join("%s,%s" % (num(px, 1), num(py, 1)) for px, py in pts)
        sw = "0.96" if kind == "roof" else ("0.82" if kind == "inner4d" else "0.68")
        elems.append('<polygon points="%s" fill="%s" fill-opacity="%s" stroke="%s" stroke-width="%s" stroke-opacity="%s" stroke-linejoin="round"/>' % (pts_s, f_col, num(f_op, 2), s_col, sw, num(s_op, 2)))

    for i in range(6):
        ov, iv = outer_verts[i], inner_verts[i]
        elems.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="0.88" stroke-opacity="0.90"/>' % (num(iv["ix"], 1), num(iv["iy"], 1), num(ov["vx"], 1), num(ov["vy"], 1), CADMIUM if i % 2 == 0 else TEAL_MIST))

    rim_pts = " ".join("%s,%s" % (num(v["vx"], 1), num(v["vy"], 1)) for v in outer_verts)
    elems.append('<polygon points="%s" fill="none" stroke="%s" stroke-width="1.35" stroke-linejoin="round"/>' % (rim_pts, CREAM))
    elems.append('<polygon points="%s" fill="none" stroke="#ffffff" stroke-width="0.48" stroke-opacity="0.72" stroke-linejoin="round"/>' % rim_pts)

    for v in outer_verts:
        col_main, col_hi = LANG_PALETTE.get(v["axis"], (CREAM, IVORY))
        elems.append('<circle cx="%s" cy="%s" r="5.8" fill="%s" fill-opacity="0.18"/>' % (num(v["vx"], 1), num(v["vy"], 1), col_main))
        elems.append('<path d="%s" fill="%s" stroke="#ffffff" stroke-width="0.62"/>' % (star_path(v["vx"], v["vy"], 5.6, 2.0, 4), col_hi))

    elems.append('<circle cx="%s" cy="%s" r="9.2" fill="%s" fill-opacity="0.22"/>' % (num(zenith_x, 1), num(zenith_y, 1), CADMIUM))
    elems.append('<path d="%s" fill="%s" stroke="#ffffff" stroke-width="0.7"/>' % (star_path(zenith_x, zenith_y, 7.2, 2.4, 8), IVORY_WARM))

    for i, axis in enumerate(axes):
        ux, uy = crown_anchors[i]
        bx, by = base_anchors[i]
        mx = ux * 0.56 + bx * 0.44
        my = uy * 0.56 + by * 0.44
        col_main, _ = LANG_PALETTE.get(axis, (CREAM, IVORY))
        pct = pct_map.get(axis, 0)
        pct_str = "%d%%" % pct if pct > 0 else "<1%"

        if i == 0:
            lx, ly, anchor = mx, uy - 14.0, "middle"
        elif i in (1, 2):
            lx = max(mx + 12.0, cx + 106.0)
            ly = my + (-8.0 if i == 1 else 14.0)
            anchor = "start"
        elif i == 3:
            lx, ly, anchor = bx, by + 20.0, "middle"
        else:
            lx = min(mx - 12.0, cx - 106.0)
            ly = my + (14.0 if i == 4 else -8.0)
            anchor = "end"

        elems.append(
            raw_text(
                lx,
                ly,
                '<tspan fill="%s" font-weight="700">%s</tspan><tspan fill="%s" font-weight="600">&#160;%s</tspan>'
                % (col_main, esc(axis), INK_PRIMARY if pct >= 5 else INK_SECOND, esc(pct_str)),
                INK_PRIMARY,
                11.0,
                anchor,
                "600",
            )
        )

    return elems


def load_portrait_hd():
    path = os.path.join(ASSETS, "portrait_hd.json")
    if not os.path.exists(path):
        return {"cols": 1, "rows": 1, "hatch_n": 1, "under_strokes": [], "sky_strokes": [], "contours": [], "grid": [[[CREAM, "@"]]]}
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def core_stage_svg(portrait_hd, langs, lang_repos, lang_stars, chars, commits, stars, total_contribs, events):
    width, height = 1200, 564
    clip_defs, frame_nodes = nocturne_card(width, height, "core", radius=16)

    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 564" width="1200" height="564" role="img" aria-label="BroAmStuck 4K Calligraphic Portrait, Stack Architecture and GitHub Activity">',
        REDUCED_MOTION_STYLE,
        "<defs>",
    ]
    parts.extend(nocturne_defs("core"))
    parts.extend(clip_defs)
    parts.extend(
        [
            '<clipPath id="core-left-clip"><rect x="1" y="1" width="483" height="562"/></clipPath>',
            '<clipPath id="core-avatar-clip"><circle cx="246" cy="252" r="204"/></clipPath>',
            '<radialGradient id="core-crystal-glow" cx="0.50" cy="0.46" r="0.52">',
            '<stop offset="0%" stop-color="#38bdf8" stop-opacity="0.18"/>',
            '<stop offset="54%" stop-color="#1d447f" stop-opacity="0.09"/>',
            '<stop offset="100%" stop-color="#040916" stop-opacity="0"/>',
            "</radialGradient>",
            "</defs>",
        ]
    )
    parts.extend(frame_nodes)
    parts.append('<g clip-path="url(#core-clip)">')

    acx, acy, ar = 246.0, 252.0, 204.0
    parts.append('<g clip-path="url(#core-left-clip)">')
    parts.extend(
        van_gogh_starry_backdrop(
            "core",
            484,
            height,
            avoid_boxes=[],
            opacity_scale=0.72,
            glyph_stride=1,
            stroke_limit=1200,
            layer_key="sky",
        )
    )
    parts.append('<rect x="1" y="1" width="483" height="562" fill="#040916" fill-opacity="0.30"/>')
    parts.append("</g>")

    parts.append('<circle cx="%s" cy="%s" r="%s" fill="#060d1c" stroke="%s" stroke-width="1.05"/>' % (num(acx), num(acy), num(ar + 5), BORDER_WARM))
    for deg in range(0, 360, 15):
        rad = math.radians(deg)
        r0 = ar + 5.0
        r1 = ar + (11.5 if deg % 45 == 0 else 8.2)
        parts.append(
            '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s" stroke-opacity="%s"/>'
            % (
                num(acx + math.cos(rad) * r0, 1),
                num(acy + math.sin(rad) * r0, 1),
                num(acx + math.cos(rad) * r1, 1),
                num(acy + math.sin(rad) * r1, 1),
                CREAM if deg % 90 == 0 else SKY_SOFT,
                "0.95" if deg % 45 == 0 else "0.58",
                "0.80" if deg % 45 == 0 else "0.38",
            )
        )

    parts.append('<g clip-path="url(#core-avatar-clip)">')
    diam = ar * 2.0
    x_left = acx - ar
    y_top = acy - ar

    hatch_n = max(int(portrait_hd.get("hatch_n") or 76), 1)
    under_strokes = portrait_hd.get("under_strokes") or []
    if under_strokes:
        hstep = diam / float(hatch_n)
        parts.append('<g stroke-linecap="round" opacity="0.90">')
        for ax_i, ay_i, hcol, _, ang_deg in under_strokes:
            px_a = x_left + (ax_i + 0.5) * hstep
            py_a = y_top + (ay_i + 0.5) * hstep
            rad = math.radians(ang_deg)
            dx = math.cos(rad) * hstep * 0.74
            dy = math.sin(rad) * hstep * 0.74
            parts.append(
                '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s"/>'
                % (num(px_a - dx, 1), num(py_a - dy, 1), num(px_a + dx, 1), num(py_a + dy, 1), hcol, num(hstep * 0.92, 2))
            )
        parts.append("</g>")

    sky_strokes = portrait_hd.get("sky_strokes") or []
    if sky_strokes:
        parts.append('<g fill="none" stroke-linecap="round">')
        for s0x, s0y, smx, smy, s1x, s1y, scol, sop in sky_strokes:
            parts.append(
                '<path d="M%s,%s Q%s,%s %s,%s" stroke="%s" stroke-width="1.05" stroke-opacity="%s"/>'
                % (
                    num(x_left + s0x * diam, 1), num(y_top + s0y * diam, 1),
                    num(x_left + smx * diam, 1), num(y_top + smy * diam, 1),
                    num(x_left + s1x * diam, 1), num(y_top + s1y * diam, 1),
                    scol, num(sop, 2),
                )
            )
        parts.append("</g>")

    cols = max(int(portrait_hd.get("cols") or 216), 1)
    rows = max(int(portrait_hd.get("rows") or 126), 1)
    grid = portrait_hd.get("grid") or []
    row_step = diam / float(rows)
    font_sz = diam / (cols * 0.601)
    start_y = y_top + row_step * 0.80

    for r_idx, runs in enumerate(grid):
        tspan_parts = []
        has_ink = False
        for col_hex, chunk in runs:
            escaped = esc(chunk)
            if col_hex is None:
                tspan_parts.append(escaped)
            else:
                has_ink = True
                tspan_parts.append('<tspan fill="%s">%s</tspan>' % (col_hex, escaped))
        if has_ink:
            parts.append(
                '<text x="%s" y="%s" textLength="%s" lengthAdjust="spacing" font-family="%s" font-size="%s" font-weight="700" xml:space="preserve">%s</text>'
                % (num(x_left, 1), num(start_y + r_idx * row_step, 2), num(diam, 1), FONT_MONO, num(font_sz, 2), "".join(tspan_parts))
            )

    contours = portrait_hd.get("contours") or []
    if contours:
        parts.append('<g stroke-linecap="round">')
        for item in contours:
            x0, y0, x1, y1, scol, sop = item[0], item[1], item[2], item[3], item[4], item[5]
            parts.append(
                '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="0.62" stroke-opacity="%s"/>'
                % (
                    num(x_left + x0 * diam, 1),
                    num(y_top + y0 * diam, 1),
                    num(x_left + x1 * diam, 1),
                    num(y_top + y1 * diam, 1),
                    scol,
                    num(sop, 2),
                )
            )
        parts.append("</g>")

    parts.append("</g>")
    parts.append('<circle cx="%s" cy="%s" r="%s" fill="none" stroke="%s" stroke-width="1.05" stroke-opacity="0.74"/>' % (num(acx), num(acy), num(ar), CREAM))

    parts.append('<rect x="168" y="473" width="156" height="54" rx="10" fill="#050b18" fill-opacity="0.86" stroke="%s" stroke-width="0.8"/>' % BORDER_WARM)
    parts.append(text(acx, 497, DISPLAY, INK_PRIMARY, 20.5, "middle", "700", ' letter-spacing="-0.2"', FONT_DISPLAY))
    parts.append(text(acx, 517, "@%s" % USERNAME, INK_MUTED, 11.0, "middle", "500"))

    parts.append('<line x1="484" y1="32" x2="484" y2="532" stroke="%s" stroke-width="0.85"/>' % BORDER_SUBTLE)

    parts.extend(render_stack_crystal(langs, lang_repos, lang_stars))

    parts.append('<line x1="956" y1="44" x2="956" y2="332" stroke="%s" stroke-width="0.85"/>' % BORDER_SUBTLE)
    metrics = [
        (978, 86, compact(chars), "Source", CREAM, False),
        (978, 158, "{:,}".format(commits), "Commits", INK_PRIMARY, False),
        (978, 230, str(stars), "Stars", FIREFLY_GOLD, True),
        (978, 302, "{:,}".format(total_contribs), "Total", EMERALD_SOFT, False),
    ]
    for mx, my, mval, mlbl, mcol, with_star in metrics:
        parts.append(text(mx, my, mval, mcol, 26, "start", "700", ' letter-spacing="-0.5"'))
        if with_star:
            sx = mx + len(mval) * 16.5 + 12.0
            parts.append('<path d="%s" fill="%s"/>' % (star_path(sx, my - 9.0, 6.8, 2.9), FIREFLY_GOLD))
        parts.append(text(mx, my + 20, mlbl, INK_SECOND, 11.2, "start", "500", "", FONT_DISPLAY))

    cx0, cy0, cw, ch = 510, 350, 662, 184
    parts.append('<rect x="%d" y="%d" width="%d" height="%d" rx="12" fill="%s" stroke="%s" stroke-width="1.05"/>' % (cx0, cy0, cw, ch, BG_CONSOLE, BORDER_WARM))
    parts.append(
        raw_text(
            cx0 + 20,
            cy0 + 23,
            '<tspan fill="%s">$</tspan><tspan fill="%s">&#160;gh&#160;activity</tspan>' % (EMERALD_SOFT, INK_MUTED),
            INK_MUTED,
            10.5,
            "start",
            "600",
        )
    )
    parts.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="1"/>' % (cx0 + 14, cy0 + 35, cx0 + cw - 14, cy0 + 35, BORDER_SUBTLE))

    rows_ev = events[:5] if events else [{"time": "--:--", "sha": "-------", "repo": USERNAME, "message": "awaiting public push event"}]
    for i, ev in enumerate(rows_ev):
        ry = cy0 + 58 + i * 25.5
        repo_s = ev["repo"][:16]
        msg_s = truncate_clean(ev["message"], 42)
        parts.append(text(cx0 + 20, ry, ev["time"], INK_MUTED, 10.6, "start", "500"))
        parts.append(text(cx0 + 70, ry, ev["sha"], CREAM, 10.6, "start", "600"))
        parts.append(text(cx0 + 138, ry, repo_s, SKY_SOFT, 10.6, "start", "600"))
        parts.append(text(cx0 + 278, ry, msg_s, INK_PRIMARY if i == 0 else INK_SECOND, 10.6, "start", "500" if i == 0 else "400"))

    parts.append("</g>")
    parts.append("</svg>")
    return "\n".join(parts)


def vangogh_nocturne_svg():
    width, height = 1200, 388
    clip_defs, frame_nodes = nocturne_card(width, height, "vg3", radius=16)
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 388" width="1200" height="388" role="img" aria-label="4K Calligraphic Synthesis of Van Gogh Starry Night, Sunflowers Garden and Country Road in Provence Cypresses">',
        REDUCED_MOTION_STYLE,
        "<defs>",
    ]
    parts.extend(nocturne_defs("vg3"))
    parts.extend(clip_defs)
    parts.extend(pup_defs("vg3"))
    parts.extend(
        [
            '<radialGradient id="vg3-road-glow" cx="0.52" cy="0.86" r="0.46">',
            '<stop offset="0%" stop-color="#60a5fa" stop-opacity="0.16"/>',
            '<stop offset="100%" stop-color="#061024" stop-opacity="0"/>',
            "</radialGradient>",
            "</defs>",
        ]
    )
    parts.extend(frame_nodes)
    parts.append('<g clip-path="url(#vg3-clip)">')
    parts.append('<rect x="1" y="1" width="1198" height="386" fill="#061126"/>')
    parts.extend(
        van_gogh_starry_backdrop(
            "vg3",
            width,
            height,
            avoid_boxes=[],
            opacity_scale=0.99,
            glyph_stride=1,
            stroke_limit=3400,
            layer_key="garden",
        )
    )
    parts.append('<rect x="1" y="1" width="1198" height="386" fill="url(#vg3-road-glow)" pointer-events="none"/>')
    parts.extend(nocturne_garden_pup())
    parts.append("</g>")
    parts.append("</svg>")
    return "\n".join(parts)


def build_telemetry_payload(data, streaks):
    axes = ["HTML", "TypeScript", "JavaScript", "CSS", "Python", "Shell"]
    lang_map = dict(data["langs"])
    pcts = lang_percentages(data["langs"])
    pct_map = {name: pcts[i] for i, (name, _) in enumerate(data["langs"])}
    total_bytes = sum(size for _, size in data["langs"]) or 1
    max_repos = max([data["lang_repos"].get(a, 1) for a in axes] + [1])
    max_stars = max([data["lang_stars"].get(a, 1) for a in axes] + [1])

    langs_5d = []
    for axis in axes:
        b_val = int(lang_map.get(axis, 0))
        share = b_val / float(total_bytes)
        pct_val = share * 100.0
        r_cnt = int(data["lang_repos"].get(axis, 0))
        s_w = int(data["lang_stars"].get(axis, 0))
        col_main, col_hi = LANG_PALETTE.get(axis, (CREAM, IVORY))
        log_byte_norm = math.log10(max(1.0, b_val)) / math.log10(max(10.0, total_bytes)) if b_val > 0 else 0.15
        norm_repos = (r_cnt / float(max_repos)) if r_cnt > 0 else 0.16
        composite = 0.62 * log_byte_norm + 0.38 * norm_repos
        langs_5d.append(
            {
                "name": axis,
                "bytes": b_val,
                "bytesCompact": compact(b_val),
                "percent": pct_map.get(axis, 0),
                "percentExact": round(pct_val, 2),
                "repos": r_cnt,
                "d2Volume": round(min(1.0, composite), 3),
                "d3Breadth": round(norm_repos, 3),
                "d4Gravity": round(0.38 + 0.62 * (s_w / float(max_stars)), 3),
                "d5Velocity": round(0.48 + 0.52 * min(1.0, (r_cnt + pct_val * 0.05) / 7.5), 3),
                "color": col_main,
                "highlight": col_hi,
            }
        )

    forums = [
        {
            "id": "v3",
            "repo": "f_forumv3",
            "title": "F-Forum v3",
            "subtitle": "7,750 UI/3D specimens, live studio & chat",
            "summary": "7,750 UI/3D specimens, live studio & chat.",
            "repoUrl": "https://github.com/%s/f_forumv3" % USERNAME,
            "liveUrl": "https://fforum3.vercel.app",
            "domain": "fforum3.vercel.app",
            "lang": (data["repo_map"].get("f_forumv3") or {}).get("lang") or "TypeScript",
            "stars": int((data["repo_map"].get("f_forumv3") or {}).get("stars") or 1),
            "accent": EMERALD_MID,
        },
        {
            "id": "v2",
            "repo": "F-Forum_v2",
            "title": "F-Forum v2",
            "subtitle": "Twin-pylon catenary suspension viaduct",
            "summary": "Twin-pylon catenary suspension viaduct.",
            "repoUrl": "https://github.com/%s/F-Forum_v2" % USERNAME,
            "liveUrl": "https://github.com/%s/F-Forum_v2" % USERNAME,
            "domain": "",
            "lang": (data["repo_map"].get("F-Forum_v2") or {}).get("lang") or "TypeScript",
            "stars": int((data["repo_map"].get("F-Forum_v2") or {}).get("stars") or 1),
            "accent": SKY_SOFT,
        },
        {
            "id": "v1",
            "repo": "f-forum",
            "title": "F-Forum v1",
            "subtitle": "Campus Q&A, math codex, clubs & live chat",
            "summary": "Campus Q&A, math codex, clubs & live chat.",
            "repoUrl": "https://github.com/%s/f-forum" % USERNAME,
            "liveUrl": "https://f-forum.vercel.app",
            "domain": "f-forum.vercel.app",
            "lang": (data["repo_map"].get("f-forum") or {}).get("lang") or "HTML",
            "stars": int((data["repo_map"].get("f-forum") or {}).get("stars") or 2),
            "accent": FIREFLY_GOLD,
        },
    ]

    return {
        "updatedAt": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "username": USERNAME,
        "display": DISPLAY,
        "metrics": {
            "bytes": data["bytes"],
            "bytesCompact": compact(data["bytes"]),
            "commits": data["commits"],
            "stars": data["stars"],
            "contributions": data["total"],
            "repos": data["repos"],
        },
        "streaks": streaks,
        "days": data["days"],
        "langs5d": langs_5d,
        "events": data["events"],
        "forums": forums,
    }


def write(name, content):
    path = os.path.join(ASSETS, name)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(content)
    print("wrote %s (%d bytes)" % (name, len(content.encode("utf-8"))))


def sync_docs_assets():
    if not os.path.isdir(os.path.join(ROOT, "docs")):
        return
    os.makedirs(DOCS_ASSETS, exist_ok=True)
    telem_src = os.path.join(ASSETS, "telemetry.json")
    if os.path.exists(telem_src):
        shutil.copy2(telem_src, os.path.join(DOCS_ASSETS, "telemetry.json"))


def main():
    os.makedirs(ASSETS, exist_ok=True)
    data = collect()
    if not data["days"] and not data["total"] and not data["repos"]:
        raise SystemExit("error: GitHub API returned no profile data, assets left untouched")
    streaks = compute_streaks(data["days"], data["weeks"])

    write("01-starry-matrix.svg", starry_matrix_svg(data["days"], data["total"], streaks))
    write(
        "02-core-stage.svg",
        core_stage_svg(
            load_portrait_hd(),
            data["langs"],
            data["lang_repos"],
            data["lang_stars"],
            data["bytes"],
            data["commits"],
            data["stars"],
            data["total"],
            data["events"],
        ),
    )
    write("03-vangogh-nocturne.svg", vangogh_nocturne_svg())
    for card_name, card_svg in render_flagship_cards(data["repo_map"]).items():
        write(card_name, card_svg)

    telemetry = build_telemetry_payload(data, streaks)
    write("telemetry.json", json.dumps(telemetry, indent=2))
    sync_docs_assets()

    print(
        "synced %s: %d contributions, %d commits, %d stars, %d repos, longest=%dd, peak=%d"
        % (
            USERNAME,
            data["total"],
            data["commits"],
            data["stars"],
            data["repos"],
            streaks["longest"],
            streaks["peak"],
        )
    )


if __name__ == "__main__":
    main()
