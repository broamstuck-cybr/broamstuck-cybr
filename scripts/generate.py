import datetime
import json
import math
import os
import shutil
import urllib.request

from cards import render_flagship_cards
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
    MILKY_DUST,
    REDUCED_MOTION_STYLE,
    SKY_SOFT,
    TEAL_MIST,
    compact,
    esc,
    nocturne_card,
    nocturne_defs,
    num,
    raw_text,
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
                if sha in seen:
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
            if sha in seen:
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
    data["events"] = collect_events()
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
    width, height = 1200, 296
    clip_defs, frame_nodes = nocturne_card(width, height, "mat", radius=16)
    weeks52 = streaks["weeks52"]
    max_w = max(weeks52) if any(weeks52) else 1

    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 296" width="1200" height="296" role="img" aria-label="Celestial 52-Week Activity Matrix under Van Gogh Starry Sky, Milky Way and Solar System">',
        REDUCED_MOTION_STYLE,
        "<defs>",
    ]
    parts.extend(nocturne_defs("mat"))
    parts.extend(clip_defs)
    parts.extend(
        [
            '<linearGradient id="mat-water" x1="0" y1="0" x2="1" y2="0">',
            '<stop offset="0%%" stop-color="%s" stop-opacity="0"/>' % BORDER_WARM,
            '<stop offset="32%%" stop-color="%s" stop-opacity="0.55"/>' % CERULEAN,
            '<stop offset="68%%" stop-color="%s" stop-opacity="0.65"/>' % CREAM,
            '<stop offset="100%%" stop-color="%s" stop-opacity="0"/>' % BORDER_WARM,
            "</linearGradient>",
            "</defs>",
        ]
    )
    parts.extend(frame_nodes)
    parts.append('<g clip-path="url(#mat-clip)">')

    # Saint-Remy Starry Night + Milky Way + Waning Crescent Moon + Heliocentric Solar System Orrery
    parts.extend(
        van_gogh_starry_backdrop(
            "mat",
            width,
            height,
            seed=1889,
            avoid_boxes=[(22, 12, 680, 36), (975, 12, 205, 36), (620, 46, 360, 26)],
            moon_pos=(836.0, 29.0, 7.6),
            vortex_centers=[
                (445.0, 134.0, 1.45, 112.0),
                (672.0, 152.0, -1.15, 94.0),
                (224.0, 118.0, 0.92, 86.0),
            ],
            stroke_count=148,
            star_aureoles=6,
            opacity_scale=0.92,
        )
    )
    parts.extend(solar_system_orrery("mat", cx=568.0, cy=148.0, scale_x=290.0, scale_y=64.0, tilt_deg=-9.5, opacity=0.46))

    parts.append(text(34, 35, "Celestial Activity Matrix · 52 Weeks", INK_PRIMARY, 14.2, "start", "700", "", FONT_DISPLAY))
    parts.append(
        raw_text(
            306,
            35,
            '<tspan fill="%s">%d contributions</tspan><tspan fill="%s">  ·  </tspan>'
            '<tspan fill="%s">%d-day longest streak</tspan><tspan fill="%s">  ·  </tspan>'
            '<tspan fill="%s">Milky Way &amp; Solar Orrery</tspan>'
            % (CREAM, total_contribs, INK_FAINT, INK_SECOND, streaks["longest"], INK_FAINT, SKY_SOFT),
            INK_SECOND,
            11.4,
            "start",
            "500",
            "",
            FONT_DISPLAY,
        )
    )

    parts.append(text(1012, 35, "Quiet", INK_MUTED, 10.2, "end", "500", "", FONT_DISPLAY))
    legend_specs = [
        (1028, 2.2, "#1e3252", 0),
        (1046, 3.2, CERULEAN, 0),
        (1066, 4.1, EMERALD_MID, 0),
        (1088, 5.0, FIREFLY_GOLD, 8.5),
        (1112, 5.8, IVORY_WARM, 11.5),
    ]
    for lx, lr, lcol, halo in legend_specs:
        if halo > 0:
            parts.append('<circle cx="%d" cy="31" r="%s" fill="url(#mat-ff-gold)"/>' % (lx, num(halo)))
        parts.append('<circle cx="%d" cy="31" r="%s" fill="%s"/>' % (lx, num(lr), lcol))
    parts.append(text(1128, 35, "Supernova", INK_MUTED, 10.2, "start", "500", "", FONT_DISPLAY))

    today = datetime.date.today()
    days_since_sun = (today.weekday() + 1) % 7
    end_sunday = today - datetime.timedelta(days=days_since_sun)
    start_sunday = end_sunday - datetime.timedelta(weeks=51)

    grid_x = 70.0
    grid_y = 82.0
    pitch_x = 21.3
    pitch_y = 19.6

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
                parts.append(text(grid_x + w * pitch_x, 64, month_names[d.month - 1], INK_MUTED, 10.2, "middle", "600", "", FONT_DISPLAY))
                last_printed_w = w

    for row, lbl in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        parts.append(text(50, grid_y + row * pitch_y + 3.8, lbl, INK_MUTED, 9.8, "end", "500"))

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
            op = min(0.55, 0.18 + (c + nc) / 100.0)
            parts.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="1.1" stroke-opacity="%s"/>' % (num(cx), num(cy), num(nx), num(ny), col, num(op)))
        if (w + 1, r) in coords and coords[(w + 1, r)][2] >= 4 and c >= 4:
            nx, ny, nc, _ = coords[(w + 1, r)]
            col = CREAM if (c + nc) >= 30 else TEAL_MIST
            op = min(0.46, 0.16 + (c + nc) / 120.0)
            parts.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="0.95" stroke-opacity="%s"/>' % (num(cx), num(cy), num(nx), num(ny), col, num(op)))
    parts.append("</g>")

    for (w, r), (cx, cy, c, _) in coords.items():
        if c == 0:
            parts.append('<circle cx="%s" cy="%s" r="2.1" fill="#182a49" fill-opacity="0.88"/>' % (num(cx), num(cy)))
            parts.append('<circle cx="%s" cy="%s" r="0.8" fill="#365382"/>' % (num(cx), num(cy)))
        elif c <= 3:
            parts.append('<circle cx="%s" cy="%s" r="5.2" fill="%s" fill-opacity="0.16"/>' % (num(cx), num(cy), CERULEAN))
            parts.append('<circle cx="%s" cy="%s" r="3.0" fill="%s"/>' % (num(cx), num(cy), SKY_SOFT))
        elif c <= 10:
            parts.append('<circle cx="%s" cy="%s" r="6.8" fill="%s" fill-opacity="0.18"/>' % (num(cx), num(cy), EMERALD_MID))
            parts.append('<circle cx="%s" cy="%s" r="3.8" fill="%s"/>' % (num(cx), num(cy), EMERALD_SOFT))
            parts.append('<circle cx="%s" cy="%s" r="1.4" fill="%s"/>' % (num(cx), num(cy), IVORY_WARM))
        elif c <= 25:
            parts.append('<circle cx="%s" cy="%s" r="9.8" fill="url(#mat-ff-gold)"/>' % (num(cx), num(cy)))
            parts.append('<circle cx="%s" cy="%s" r="5.8" fill="none" stroke="%s" stroke-width="0.75" stroke-dasharray="2.4 2" stroke-opacity="0.65"/>' % (num(cx), num(cy), CADMIUM))
            parts.append('<circle cx="%s" cy="%s" r="4.3" fill="%s"/>' % (num(cx), num(cy), FIREFLY_GOLD))
            parts.append('<circle cx="%s" cy="%s" r="1.8" fill="#ffffff"/>' % (num(cx), num(cy)))
        else:
            parts.append('<circle cx="%s" cy="%s" r="13.8" fill="url(#mat-ff-gold)"/>' % (num(cx), num(cy)))
            parts.append('<circle cx="%s" cy="%s" r="7.4" fill="none" stroke="%s" stroke-width="0.9" stroke-dasharray="3 2.2" stroke-opacity="0.8"/>' % (num(cx), num(cy), CADMIUM))
            parts.append('<circle cx="%s" cy="%s" r="5.2" fill="%s"/>' % (num(cx), num(cy), CREAM))
            parts.append('<circle cx="%s" cy="%s" r="2.3" fill="#ffffff"/>' % (num(cx), num(cy)))
            parts.append(
                '<path d="M%s %s V%s M%s %s H%s" stroke="#ffffff" stroke-width="0.85" stroke-opacity="0.78"/>'
                % (num(cx), num(cy - 8.4), num(cy + 8.4), num(cx - 8.4), num(cy), num(cx + 8.4))
            )

    # Liquid Starry-Sky Mirror Horizon & Fluid Reflection Ripples
    water_y = 236.0
    parts.append('<line x1="48" y1="%s" x2="1166" y2="%s" stroke="url(#mat-water)" stroke-width="1.15"/>' % (num(water_y), num(water_y)))
    for w in range(52):
        val = weeks52[w]
        if val <= 0:
            continue
        norm = (val / float(max_w)) ** 0.62
        wx = grid_x + w * pitch_x
        for ri in range(1, 4):
            rw = (4.0 + norm * 12.0) * (1.0 - ri * 0.18)
            ry = water_y + ri * 8.2 + (w % 2) * 1.6
            op = norm * (0.52 - ri * 0.11)
            col = CADMIUM if norm > 0.45 else SKY_SOFT
            parts.append(
                '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="1.25" stroke-linecap="round" stroke-opacity="%s">'
                '<animate attributeName="x1" values="%s;%s;%s" dur="%ss" repeatCount="indefinite"/>'
                '<animate attributeName="x2" values="%s;%s;%s" dur="%ss" repeatCount="indefinite"/>'
                "</line>"
                % (
                    num(wx - rw), num(ry), num(wx + rw), num(ry), col, num(op),
                    num(wx - rw), num(wx - rw - 2.4), num(wx - rw), num(4.4 + (w % 5) * 0.7, 1),
                    num(wx + rw), num(wx + rw + 2.4), num(wx + rw), num(4.4 + (w % 5) * 0.7, 1),
                )
            )

    parts.append("</g>")
    parts.append("</svg>")
    return "\n".join(parts)


def _project_5d(cx, cy, x, y, z, w_coord=0.0):
    # WHY: Schlegel 4D->3D perspective fold coupled with axonometric 3D->2D projection encodes 5 true engineering dimensions.
    w_scale = 1.0 / (1.0 + 0.28 * (1.0 - w_coord))
    xw = x * w_scale
    yw = y * w_scale
    zw = z * w_scale + w_coord * 14.0
    yaw = math.radians(-22.0)
    tilt = math.radians(56.0)
    rx = xw * math.cos(yaw) - yw * math.sin(yaw)
    ry = xw * math.sin(yaw) + yw * math.cos(yaw)
    sx = cx + rx
    sy = cy + ry * math.cos(tilt) - zw * math.sin(tilt)
    return sx, sy, ry


def render_5d_stack_astrolabe(langs, lang_repos, lang_stars, total_repos):
    cx, cy = 708.0, 214.0
    radius_max = 96.0
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
        text(508, 42, "5D Stack Astrolabe · Schlegel Hyper-Radar", INK_PRIMARY, 13.8, "start", "700", "", FONT_DISPLAY),
        text(508, 338, "D1 Domain · D2 Byte Share · D3 Repo Breadth · D4 4D Gravity · D5 Phase", INK_MUTED, 9.5, "start", "500", "", FONT_DISPLAY),
    ]

    # 1. Graduated Celestial Armillary Azimuth Ring & Degree Ticks
    arm_pts = []
    for deg in range(0, 360, 6):
        rad = math.radians(deg)
        px, py, _ = _project_5d(cx, cy, math.cos(rad) * (radius_max * 1.10), math.sin(rad) * (radius_max * 1.10), 0.0, 1.0)
        arm_pts.append((px, py))
        if deg % 15 == 0:
            in_len = 0.99 if deg % 60 == 0 else 1.04
            ix, iy, _ = _project_5d(cx, cy, math.cos(rad) * (radius_max * in_len), math.sin(rad) * (radius_max * in_len), 0.0, 1.0)
            elems.append(
                '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s" stroke-opacity="%s"/>'
                % (num(ix, 1), num(iy, 1), num(px, 1), num(py, 1), CREAM if deg % 60 == 0 else SKY_SOFT, "1.1" if deg % 60 == 0 else "0.7", "0.7" if deg % 60 == 0 else "0.36")
            )
    elems.append(
        '<polygon points="%s" fill="#071021" fill-opacity="0.76" stroke="%s" stroke-width="1.1"/>'
        % (" ".join("%s,%s" % (num(px, 1), num(py, 1)) for px, py in arm_pts), BORDER_WARM)
    )

    # Concentric geodesic hex rings on base plane
    for ring_f in (0.30, 0.56, 0.82):
        h_pts = []
        for i in range(6):
            ang = -math.pi / 2.0 + i * math.pi / 3.0
            sx, sy, _ = _project_5d(cx, cy, math.cos(ang) * radius_max * ring_f, math.sin(ang) * radius_max * ring_f, 0.0, 1.0)
            h_pts.append("%s,%s" % (num(sx, 1), num(sy, 1)))
        elems.append(
            '<polygon points="%s" fill="none" stroke="%s" stroke-width="0.8" stroke-dasharray="%s"/>'
            % (" ".join(h_pts), BORDER_WARM if ring_f == 0.82 else BORDER_SUBTLE, "2 3" if ring_f == 0.30 else "none")
        )

    # Tilted Celestial Meridian & Ecliptic Harmonic Phase Rings (Dimension 5)
    for m_idx, (z_amp, col_m, dur_m) in enumerate(((32.0, SKY_SOFT, "17s"), (-26.0, CADMIUM, "23s"))):
        m_pts = []
        for deg in range(0, 361, 12):
            rad = math.radians(deg)
            mx_p, my_p, _ = _project_5d(
                cx, cy,
                math.cos(rad) * (radius_max * 0.96),
                math.sin(rad) * (radius_max * 0.96),
                28.0 + math.sin(rad + m_idx * 1.1) * z_amp,
                1.0,
            )
            m_pts.append("%s,%s" % (num(mx_p, 1), num(my_p, 1)))
        m_path = "M" + " L".join(m_pts)
        elems.append('<path d="%s" fill="none" stroke="%s" stroke-width="0.85" stroke-opacity="0.28" stroke-dasharray="3 4"/>' % (m_path, col_m))
        elems.append(
            '<g><circle r="4.8" fill="url(#core-ff-gold)"/><circle r="1.4" fill="#ffffff"/>'
            '<animateMotion path="%s" dur="%s" repeatCount="indefinite"/></g>' % (m_path, dur_m)
        )

    origin_x, origin_y, _ = _project_5d(cx, cy, 0.0, 0.0, 0.0, 1.0)
    zenith_x, zenith_y, zenith_d = _project_5d(cx, cy, 0.0, 0.0, apex_z, 1.0)
    inner_zen_x, inner_zen_y, inner_zen_d = _project_5d(cx, cy, 0.0, 0.0, apex_z * 0.56, -0.45)

    elems.append(
        '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="0.95" stroke-dasharray="2 3" stroke-opacity="0.62"/>'
        % (num(origin_x, 1), num(origin_y, 1), num(zenith_x, 1), num(zenith_y, 1), CREAM)
    )

    # Compute Outer 3D Polytope (w=+1) & Inner 4D W-Folded Tesseract Cell (w=-0.45)
    outer_verts = []
    inner_verts = []
    crown_anchors = []
    base_anchors = []

    for i, axis in enumerate(axes):
        ang = -math.pi / 2.0 + i * math.pi / 3.0
        share = lang_map.get(axis, 0) / float(total_bytes)
        pct_val = share * 100.0
        r_count = lang_repos.get(axis, 0)
        s_weight = lang_stars.get(axis, 0)

        # D2: Log byte volume reach
        norm_vol = math.log1p(pct_val * 6.5) / math.log1p(480.0) if pct_val > 0 else 0.0
        reach = 0.30 + 0.70 * norm_vol if share > 0 else 0.24
        # D3: Repository breadth Z-elevation
        norm_repos = (r_count / float(max_repos)) if r_count > 0 else 0.15
        elev = 14.0 + crown_z * (0.45 * norm_vol + 0.55 * norm_repos)
        # D4: Star-weighted 4D hyper-cell coordinate
        norm_grav = 0.34 + 0.52 * (s_weight / float(max_stars))

        wx = math.cos(ang) * radius_max * reach
        wy = math.sin(ang) * radius_max * reach
        vx, vy, depth = _project_5d(cx, cy, wx, wy, elev, 1.0)
        bx, by, bdepth = _project_5d(cx, cy, wx, wy, 0.0, 1.0)

        ix, iy, idepth = _project_5d(
            cx, cy,
            math.cos(ang) * radius_max * (reach * 0.54 * (0.65 + 0.35 * norm_grav)),
            math.sin(ang) * radius_max * (reach * 0.54 * (0.65 + 0.35 * norm_grav)),
            elev * 0.54 + 8.0,
            -0.55,
        )

        ax_b = _project_5d(cx, cy, math.cos(ang) * radius_max, math.sin(ang) * radius_max, 0.0, 1.0)[:2]
        ax_c = _project_5d(cx, cy, math.cos(ang) * radius_max, math.sin(ang) * radius_max, crown_z, 1.0)[:2]
        base_anchors.append(ax_b)
        crown_anchors.append(ax_c)
        elems.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="0.8"/>' % (num(origin_x, 1), num(origin_y, 1), num(ax_b[0], 1), num(ax_b[1], 1), BORDER_SUBTLE))
        elems.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="0.75" stroke-dasharray="2 3" stroke-opacity="0.52"/>' % (num(ax_b[0], 1), num(ax_b[1], 1), num(ax_c[0], 1), num(ax_c[1], 1), BORDER_WARM))

        outer_verts.append({"i": i, "axis": axis, "vx": vx, "vy": vy, "bx": bx, "by": by, "depth": depth, "bdepth": bdepth, "repos": r_count})
        inner_verts.append({"i": i, "axis": axis, "ix": ix, "iy": iy, "depth": idepth})

    # Base footprint shadow polygon
    elems.append(
        '<polygon points="%s" fill="%s" fill-opacity="0.10" stroke="%s" stroke-width="0.9" stroke-opacity="0.42"/>'
        % (" ".join("%s,%s" % (num(v["bx"], 1), num(v["by"], 1)) for v in outer_verts), SKY_SOFT, SKY_SOFT)
    )

    # Render depth-sorted facets for BOTH Inner 4D Hyper-Cell AND Outer 3D Polytope
    facets = []
    outer_tones = ("#fb923c", "#38bdf8", "#fbbf24", "#2dd4bf", "#4ade80", "#818cf8")
    for i in range(6):
        j = (i + 1) % 6
        vi, vj = outer_verts[i], outer_verts[j]
        ii, ij = inner_verts[i], inner_verts[j]

        # Inner 4D W-Tesseract cell facet
        in_depth = (inner_zen_d + ii["depth"] + ij["depth"]) / 3.0 - 4.0
        facets.append((
            in_depth,
            "inner4d",
            [(inner_zen_x, inner_zen_y), (ii["ix"], ii["iy"]), (ij["ix"], ij["iy"])],
            CERULEAN if i % 2 == 0 else CADMIUM,
            0.30,
            MILKY_CORE,
            0.78,
        ))
        # Outer elevation skirt
        sk_depth = (vi["bdepth"] + vj["bdepth"] + vi["depth"] + vj["depth"]) / 4.0 - 2.0
        facets.append((
            sk_depth,
            "skirt",
            [(vi["bx"], vi["by"]), (vj["bx"], vj["by"]), (vj["vx"], vj["vy"]), (vi["vx"], vi["vy"])],
            "#0e294b",
            0.32,
            TEAL_MIST,
            0.46,
        ))
        # Outer polytope crown facet
        rf_depth = (zenith_d + vi["depth"] + vj["depth"]) / 3.0
        is_front = (vi["vy"] + vj["vy"]) / 2.0 > cy - 8.0
        facets.append((
            rf_depth,
            "roof",
            [(zenith_x, zenith_y), (vi["vx"], vi["vy"]), (vj["vx"], vj["vy"])],
            outer_tones[i],
            0.24 if is_front else 0.14,
            CREAM if is_front else SKY_SOFT,
            0.84 if is_front else 0.52,
        ))

    facets.sort(key=lambda item: item[0])
    for _, kind, pts, f_col, f_op, s_col, s_op in facets:
        pts_s = " ".join("%s,%s" % (num(px, 1), num(py, 1)) for px, py in pts)
        sw = "1.15" if kind == "roof" else ("0.95" if kind == "inner4d" else "0.8")
        elems.append(
            '<polygon points="%s" fill="%s" fill-opacity="%s" stroke="%s" stroke-width="%s" stroke-opacity="%s" stroke-linejoin="round"/>'
            % (pts_s, f_col, num(f_op, 2), s_col, sw, num(s_op, 2))
        )

    # 4D Schlegel Tesseract Projection Struts connecting Inner 4D Cell -> Outer 3D Polytope
    elems.append(
        '<polygon points="%s" fill="none" stroke="%s" stroke-width="1.15" stroke-dasharray="2.5 2" stroke-opacity="0.88"/>'
        % (" ".join("%s,%s" % (num(iv["ix"], 1), num(iv["iy"], 1)) for iv in inner_verts), SKY_SOFT)
    )
    elems.append(
        '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="1.1" stroke-opacity="0.85"/>'
        % (num(inner_zen_x, 1), num(inner_zen_y, 1), num(zenith_x, 1), num(zenith_y, 1), CADMIUM)
    )
    for i in range(6):
        ov = outer_verts[i]
        iv = inner_verts[i]
        elems.append(
            '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="1.05" stroke-opacity="0.78"/>'
            % (num(iv["ix"], 1), num(iv["iy"], 1), num(ov["vx"], 1), num(ov["vy"], 1), CADMIUM if i % 2 == 0 else TEAL_MIST)
        )
        elems.append('<circle cx="%s" cy="%s" r="2.0" fill="%s"/>' % (num(iv["ix"], 1), num(iv["iy"], 1), MILKY_CORE))

    # Glowing outer 3D rim & vertex nodes
    rim_pts = " ".join("%s,%s" % (num(v["vx"], 1), num(v["vy"], 1)) for v in outer_verts)
    elems.append('<polygon points="%s" fill="none" stroke="%s" stroke-width="1.55" stroke-linejoin="round" filter="url(#core-bloom)"/>' % (rim_pts, CREAM))

    for v in outer_verts:
        elems.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="0.85" stroke-opacity="0.52"/>' % (
            num(v["bx"], 1), num(v["by"], 1), num(v["vx"], 1), num(v["vy"], 1), CREAM
        ))
        _, col_hi = LANG_PALETTE.get(v["axis"], (CREAM, IVORY))
        elems.append('<circle cx="%s" cy="%s" r="5.6" fill="url(#core-ff-gold)"/>' % (num(v["vx"], 1), num(v["vy"], 1)))
        elems.append('<circle cx="%s" cy="%s" r="2.6" fill="%s" stroke="#ffffff" stroke-width="0.8"/>' % (num(v["vx"], 1), num(v["vy"], 1), col_hi))

    elems.append('<circle cx="%s" cy="%s" r="8.2" fill="url(#core-ff-gold)"/>' % (num(zenith_x, 1), num(zenith_y, 1)))
    elems.append('<circle cx="%s" cy="%s" r="2.9" fill="#ffffff"/>' % (num(zenith_x, 1), num(zenith_y, 1)))

    # 6 Precision English Axis Callouts (Language + Share % + Repo Count)
    for i, axis in enumerate(axes):
        ux, uy = crown_anchors[i]
        bx, by = base_anchors[i]
        mx = ux * 0.55 + bx * 0.45
        my = uy * 0.55 + by * 0.45
        col_main, _ = LANG_PALETTE.get(axis, (CREAM, IVORY))
        pct = pct_map.get(axis, 0)
        pct_str = "%d%%" % pct if pct > 0 else "<1%"
        r_cnt = lang_repos.get(axis, 0)
        repo_tag = " · %dr" % r_cnt if r_cnt > 0 else ""

        if i == 0:
            lx, ly, anchor = mx, uy - 14.0, "middle"
            elems.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="0.9" stroke-opacity="0.62"/>' % (num(ux, 1), num(uy - 2, 1), num(lx, 1), num(ly + 4, 1), col_main))
        elif i in (1, 2):
            lx = max(mx + 16.0, cx + 114.0)
            ly = my + (-2.0 if i == 1 else 12.0)
            anchor = "start"
            elems.append('<polyline points="%s,%s %s,%s %s,%s" fill="none" stroke="%s" stroke-width="0.9" stroke-opacity="0.62"/>' % (
                num(mx + 3, 1), num(my, 1), num(lx - 10, 1), num(ly - 4, 1), num(lx - 3, 1), num(ly - 4, 1), col_main
            ))
        elif i == 3:
            lx, ly, anchor = bx, by + 23.0, "middle"
            elems.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="0.9" stroke-opacity="0.62"/>' % (num(bx, 1), num(by + 3, 1), num(lx, 1), num(ly - 12, 1), col_main))
        else:
            lx = min(mx - 16.0, cx - 112.0)
            ly = my + (12.0 if i == 4 else -2.0)
            anchor = "end"
            elems.append('<polyline points="%s,%s %s,%s %s,%s" fill="none" stroke="%s" stroke-width="0.9" stroke-opacity="0.62"/>' % (
                num(mx - 3, 1), num(my, 1), num(lx + 10, 1), num(ly - 4, 1), num(lx + 3, 1), num(ly - 4, 1), col_main
            ))

        elems.append(
            raw_text(
                lx,
                ly,
                '<tspan fill="%s" font-weight="700">%s</tspan>'
                '<tspan fill="%s" font-weight="600"> %s</tspan>'
                '<tspan fill="%s" font-weight="500">%s</tspan>'
                % (col_main, esc(axis), INK_PRIMARY if pct >= 5 else INK_SECOND, esc(pct_str), INK_MUTED, esc(repo_tag)),
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
        return {"cols": 1, "rows": 1, "atmos_n": 1, "atmos": [], "contours": [], "grid": [[[CREAM, "@"]]]}
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def core_stage_svg(portrait_hd, langs, lang_repos, lang_stars, total_repos, chars, commits, stars, total_contribs, events):
    width, height = 1200, 568
    clip_defs, frame_nodes = nocturne_card(width, height, "core", radius=16)

    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 568" width="1200" height="568" role="img" aria-label="Ultra-HD Optical Character Portrait, 5D Schlegel Stack Astrolabe, Live Engineering Telemetry and Recent GitHub Activity Console">',
        REDUCED_MOTION_STYLE,
        "<defs>",
    ]
    parts.extend(nocturne_defs("core"))
    parts.extend(clip_defs)
    parts.extend(
        [
            '<radialGradient id="core-aura-left" cx="21%%" cy="45%%" r="32%%">',
            '<stop offset="0%%" stop-color="%s" stop-opacity="0.14"/>' % CREAM,
            '<stop offset="55%%" stop-color="%s" stop-opacity="0.06"/>' % CERULEAN,
            '<stop offset="100%%" stop-color="%s" stop-opacity="0"/>' % BG_NIGHT,
            "</radialGradient>",
            '<radialGradient id="core-aura-5d" cx="59%%" cy="35%%" r="30%%">',
            '<stop offset="0%%" stop-color="%s" stop-opacity="0.14"/>' % SKY_SOFT,
            '<stop offset="58%%" stop-color="%s" stop-opacity="0.06"/>' % FIREFLY_GOLD,
            '<stop offset="100%%" stop-color="%s" stop-opacity="0"/>' % BG_NIGHT,
            "</radialGradient>",
            '<filter id="core-atmos-blur" x="-15%%" y="-15%%" width="130%%" height="130%%">',
            '<feGaussianBlur stdDeviation="5.6"/>',
            "</filter>",
            '<clipPath id="core-avatar-clip"><circle cx="246" cy="252" r="198"/></clipPath>',
            "</defs>",
        ]
    )
    parts.extend(frame_nodes)
    parts.append('<g clip-path="url(#core-clip)">')
    parts.append('<rect x="1" y="1" width="1198" height="566" fill="url(#core-aura-left)"/>')
    parts.append('<rect x="1" y="1" width="1198" height="566" fill="url(#core-aura-5d)"/>')

    acx, acy, ar = 246.0, 252.0, 198.0
    avoid = [
        (acx - ar - 10, acy - ar - 10, (ar + 10) * 2, (ar + 10) * 2),
        (500, 26, 444, 314),
        (506, 350, 670, 192),
        (952, 46, 224, 286),
    ]
    parts.extend(
        van_gogh_starry_backdrop(
            "core",
            width,
            height,
            seed=2027,
            avoid_boxes=avoid,
            moon_pos=(1154.0, 44.0, 9.2),
            stroke_count=96,
            star_aureoles=6,
            opacity_scale=0.84,
        )
    )

    # Engraved Celestial Astrolabe Bezel around Ultra-HD Character Portrait
    parts.append('<circle cx="%s" cy="%s" r="%s" fill="none" stroke="%s" stroke-width="1.0" stroke-opacity="0.65" stroke-dasharray="3 5"/>' % (num(acx), num(acy), num(ar + 13), BORDER_WARM))
    parts.append('<circle cx="%s" cy="%s" r="%s" fill="#0b1324" stroke="%s" stroke-width="1.3"/>' % (num(acx), num(acy), num(ar + 6), BORDER_WARM))
    for deg in range(0, 360, 10):
        rad = math.radians(deg)
        r0 = ar + 6.0
        r1 = ar + (12.5 if deg % 30 == 0 else 9.5)
        parts.append(
            '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s" stroke-opacity="%s"/>'
            % (
                num(acx + math.cos(rad) * r0, 1),
                num(acy + math.sin(rad) * r0, 1),
                num(acx + math.cos(rad) * r1, 1),
                num(acy + math.sin(rad) * r1, 1),
                CREAM if deg % 90 == 0 else SKY_SOFT,
                "1.2" if deg % 30 == 0 else "0.75",
                "0.75" if deg % 30 == 0 else "0.35",
            )
        )
    parts.append('<circle cx="%s" cy="%s" r="%s" fill="#070d1a"/>' % (num(acx), num(acy), num(ar)))

    # Ultra-HD Portrait Layer 1 (48x48 smooth atmospheric under-painting) + Layer 2 (156x86 directional glyphs) + Layer 3 (micro-contours)
    parts.append('<g clip-path="url(#core-avatar-clip)">')
    atmos_n = max(int(portrait_hd.get("atmos_n") or 48), 1)
    atmos_cells = portrait_hd.get("atmos") or []
    if atmos_cells:
        cell_step = (ar * 2.0) / float(atmos_n)
        parts.append('<g filter="url(#core-atmos-blur)" opacity="0.58">')
        for ax_i, ay_i, acol in atmos_cells:
            px_a = (acx - ar) + (ax_i + 0.5) * cell_step
            py_a = (acy - ar) + (ay_i + 0.5) * cell_step
            parts.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (num(px_a, 1), num(py_a, 1), num(cell_step * 0.92, 1), acol))
        parts.append("</g>")

    cols = max(int(portrait_hd.get("cols") or 156), 1)
    rows = max(int(portrait_hd.get("rows") or 86), 1)
    grid = portrait_hd.get("grid") or []
    diam = ar * 2.0
    row_step = diam / float(rows)
    font_sz = diam / (cols * 0.601)
    start_y = acy - ar + row_step * 0.80

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
                '<text x="%s" y="%s" font-family="%s" font-size="%s" font-weight="700" text-anchor="middle" xml:space="preserve">%s</text>'
                % (num(acx), num(start_y + r_idx * row_step, 2), FONT_MONO, num(font_sz, 2), "".join(tspan_parts))
            )

    contours = portrait_hd.get("contours") or []
    if contours:
        parts.append('<g stroke-linecap="round">')
        for x0, y0, x1, y1, scol, sop in contours:
            parts.append(
                '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="0.72" stroke-opacity="%s"/>'
                % (
                    num((acx - ar) + x0 * diam, 1),
                    num((acy - ar) + y0 * diam, 1),
                    num((acx - ar) + x1 * diam, 1),
                    num((acy - ar) + y1 * diam, 1),
                    scol,
                    num(sop, 2),
                )
            )
        parts.append("</g>")

    parts.append("</g>")
    parts.append('<circle cx="%s" cy="%s" r="%s" fill="none" stroke="%s" stroke-width="1.25" stroke-opacity="0.52"/>' % (num(acx), num(acy), num(ar), CREAM))

    parts.append(text(acx, 496, DISPLAY, INK_PRIMARY, 21.5, "middle", "700", ' letter-spacing="0.2"', FONT_DISPLAY))
    parts.append(text(acx, 519, "@%s · Optical Glyph Portrait" % USERNAME, INK_MUTED, 11.2, "middle", "500"))

    parts.append('<line x1="484" y1="32" x2="484" y2="536" stroke="%s" stroke-width="1"/>' % BORDER_SUBTLE)

    parts.extend(render_5d_stack_astrolabe(langs, lang_repos, lang_stars, total_repos))

    parts.append('<line x1="952" y1="44" x2="952" y2="332" stroke="%s" stroke-width="1"/>' % BORDER_SUBTLE)
    metrics = [
        (974, 86, compact(chars), "Source Characters", CREAM, False),
        (974, 158, str(commits), "Annual Commits", INK_PRIMARY, False),
        (974, 230, str(stars), "Stars Earned", FIREFLY_GOLD, True),
        (974, 302, str(total_contribs), "Total Contributions", EMERALD_SOFT, False),
    ]
    for mx, my, mval, mlbl, mcol, with_star in metrics:
        parts.append(text(mx, my, mval, mcol, 26, "start", "700", ' letter-spacing="-0.5"'))
        if with_star:
            sx = mx + len(mval) * 16.5 + 12.0
            parts.append('<path d="%s" fill="%s"/>' % (star_path(sx, my - 9.0, 6.8, 2.9), FIREFLY_GOLD))
        parts.append(text(mx, my + 20, mlbl, INK_SECOND, 11.2, "start", "500", "", FONT_DISPLAY))

    cx0, cy0, cw, ch = 510, 354, 662, 182
    parts.append('<rect x="%d" y="%d" width="%d" height="%d" rx="12" fill="%s" stroke="%s" stroke-width="1.05"/>' % (cx0, cy0, cw, ch, BG_CONSOLE, BORDER_WARM))
    for di, dcol in enumerate(("#334155", "#475569", "#64748b")):
        parts.append('<circle cx="%d" cy="%d" r="3.2" fill="%s"/>' % (cx0 + 18 + di * 12, cy0 + 19, dcol))
    parts.append(
        raw_text(
            cx0 + 62,
            cy0 + 23,
            '<tspan fill="%s">$</tspan><tspan fill="%s"> gh activity --recent --format=telemetry</tspan>' % (EMERALD_SOFT, INK_MUTED),
            INK_MUTED,
            10.5,
            "start",
            "500",
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
        if i == 0:
            cur_x = cx0 + 278 + len(msg_s) * 6.5 + 6.0
            if cur_x < cx0 + cw - 18:
                parts.append(
                    '<rect x="%s" y="%s" width="6" height="12" rx="1.2" fill="%s">'
                    '<animate attributeName="opacity" values="0.95;0.95;0.1;0.1" keyTimes="0;0.48;0.52;1" dur="1.25s" repeatCount="indefinite"/></rect>'
                    % (num(cur_x), num(ry - 10), CREAM)
                )

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
        langs_5d.append(
            {
                "name": axis,
                "bytes": b_val,
                "bytesCompact": compact(b_val),
                "percent": pct_map.get(axis, 0),
                "percentExact": round(pct_val, 2),
                "repos": r_cnt,
                "d2Volume": round(math.log1p(pct_val * 6.5) / math.log1p(480.0), 3) if pct_val > 0 else 0.12,
                "d3Breadth": round(r_cnt / float(max_repos), 3) if r_cnt > 0 else 0.14,
                "d4Gravity": round(0.32 + 0.68 * (s_w / float(max_stars)), 3),
                "d5Velocity": round(0.45 + 0.55 * min(1.0, (r_cnt + pct_val * 0.05) / 8.0), 3),
                "color": col_main,
                "highlight": col_hi,
            }
        )

    forums = [
        {
            "id": "v3",
            "repo": "f_forumv3",
            "title": "F-Forum v3",
            "badge": "CITADEL 3D",
            "subtitle": "Spatial UI/3D Workbench & 7,750-Specimen Vault",
            "summary": "Third-generation spatial studio combining 7,750 directly viewable UI and 3D specimens with a sandboxed live workbench, community feed, and real-time messenger.",
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
            "badge": "VIADUCT 3D",
            "subtitle": "Generational Catenary Bridge Architecture",
            "summary": "Architectural transition bridge linking the original student learning forum to the modular third-generation spatial workbench and public specimen archive.",
            "repoUrl": "https://github.com/%s/F-Forum_v2" % USERNAME,
            "liveUrl": "https://github.com/%s/F-Forum_v2" % USERNAME,
            "domain": "v2-bridge",
            "lang": (data["repo_map"].get("F-Forum_v2") or {}).get("lang") or "TypeScript",
            "stars": int((data["repo_map"].get("F-Forum_v2") or {}).get("stars") or 1),
            "accent": SKY_SOFT,
        },
        {
            "id": "v1",
            "repo": "f-forum",
            "title": "F-Forum v1",
            "badge": "ROTUNDA 3D",
            "subtitle": "Campus Q&A Forum, Student Clubs & Exam Vault",
            "summary": "First-generation student forum uniting subject Q&A with math typesetting, PDF exam archives, flashcards, student clubs, and real-time chat.",
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
    for fname in os.listdir(ASSETS):
        if fname.endswith((".svg", ".json")):
            shutil.copy2(os.path.join(ASSETS, fname), os.path.join(DOCS_ASSETS, fname))


def main():
    os.makedirs(ASSETS, exist_ok=True)
    data = collect()
    if not data["days"] and not data["total"] and not data["repos"]:
        raise SystemExit("error: GitHub API returned no profile data, assets left untouched")
    streaks = compute_streaks(data["days"], data["weeks"])

    # Teardown legacy asset name if present
    legacy_matrix = os.path.join(ASSETS, "01-firefly-matrix.svg")
    if os.path.exists(legacy_matrix):
        os.remove(legacy_matrix)

    write("01-starry-matrix.svg", starry_matrix_svg(data["days"], data["total"], streaks))
    write(
        "02-core-stage.svg",
        core_stage_svg(
            load_portrait_hd(),
            data["langs"],
            data["lang_repos"],
            data["lang_stars"],
            data["repos"],
            data["bytes"],
            data["commits"],
            data["stars"],
            data["total"],
            data["events"],
        ),
    )
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
