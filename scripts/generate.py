import datetime
import json
import math
import os
import urllib.request

from cards import render_flagship_cards
from theme import (
    BG_CONSOLE,
    BG_NIGHT,
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
    compact,
    esc,
    fireflies_layer,
    nocturne_card,
    nocturne_defs,
    num,
    raw_text,
    star_path,
    text,
)

USERNAME = os.environ.get("GH_PROFILE_USERNAME", "broamstuck-cybr")
DISPLAY = os.environ.get("GH_PROFILE_DISPLAY", "BroAmStuck")
TOKEN = os.environ.get("GITHUB_TOKEN", "") or os.environ.get("GH_TOKEN", "")
API = (os.environ.get("GITHUB_API_URL", "") or "https://api.github.com").rstrip("/")
GQL = (os.environ.get("GITHUB_GRAPHQL_URL", "") or "https://api.github.com/graphql").rstrip("/")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")


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
    return cut.rstrip(" ,;:-/") + "…"


def collect_events(limit=5):
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
                commits.append(
                    {
                        "sha": sha,
                        "repo": repo_label((event.get("repo") or {}).get("name")),
                        "message": (commit.get("message") or "").split("\n")[0].strip(),
                        "time": clock(event.get("created_at")),
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
            commits.append(
                {
                    "sha": sha,
                    "repo": repo_label((item.get("repository") or {}).get("full_name")),
                    "message": (detail.get("message") or "").split("\n")[0].strip(),
                    "time": clock((detail.get("committer") or {}).get("date")),
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
                    "lang": ((node.get("primaryLanguage") or {}).get("name")) or "Code",
                }
            for edge in (node.get("languages") or {}).get("edges") or []:
                lang_name = ((edge.get("node") or {}).get("name")) or ""
                if lang_name:
                    data["bytes"] += int(edge.get("size") or 0)
                    sizes[lang_name] = sizes.get(lang_name, 0) + int(edge.get("size") or 0)
        data["langs"] = sorted(sizes.items(), key=lambda item: item[1], reverse=True)
    data["events"] = collect_events()
    return data


def compute_streaks(day_map, weeks):
    ordered = sorted(day_map.items())
    longest = 0
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
    w52 = list(weeks[-52:])
    if len(w52) < 52:
        w52 = ([0] * (52 - len(w52))) + w52
    return {"longest": longest, "peak": peak, "weeks52": w52}


def lang_percentages(langs):
    total = sum(size for _, size in langs) or 1
    raw = [size * 100.0 / total for _, size in langs]
    counts = [int(value) for value in raw]
    order = sorted(range(len(raw)), key=lambda i: raw[i] - counts[i], reverse=True)
    for i in order[: max(0, 100 - sum(counts))]:
        counts[i] += 1
    return counts


def firefly_matrix_svg(day_map, total_contribs, streaks):
    width, height = 1200, 276
    clip_defs, frame_nodes = nocturne_card(width, height, "mat", radius=16)
    weeks52 = streaks["weeks52"]
    max_w = max(weeks52) if any(weeks52) else 1

    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 276" width="1200" height="276" role="img" aria-label="Bioluminescent 52-Week Activity Constellation">',
        REDUCED_MOTION_STYLE,
        "<defs>",
    ]
    parts.extend(nocturne_defs("mat"))
    parts.extend(clip_defs)
    parts.extend(
        [
            '<radialGradient id="mat-sky" cx="76%%" cy="48%%" r="46%%">',
            '<stop offset="0%%" stop-color="%s" stop-opacity="0.11"/>' % FIREFLY_GOLD,
            '<stop offset="52%%" stop-color="%s" stop-opacity="0.05"/>' % EMERALD_MID,
            '<stop offset="100%%" stop-color="%s" stop-opacity="0"/>' % BG_NIGHT,
            "</radialGradient>",
            '<linearGradient id="mat-water" x1="0" y1="0" x2="1" y2="0">',
            '<stop offset="0%%" stop-color="%s" stop-opacity="0"/>' % BORDER_WARM,
            '<stop offset="50%%" stop-color="%s" stop-opacity="0.65"/>' % BORDER_WARM,
            '<stop offset="78%%" stop-color="%s" stop-opacity="0.48"/>' % CREAM,
            '<stop offset="100%%" stop-color="%s" stop-opacity="0"/>' % BORDER_WARM,
            "</linearGradient>",
            "</defs>",
        ]
    )
    parts.extend(frame_nodes)
    parts.append('<g clip-path="url(#mat-clip)">')
    parts.append('<rect x="1" y="1" width="1198" height="274" fill="url(#mat-sky)"/>')

    parts.append(text(34, 36, "Nhịp độ hoạt động · 52 tuần", INK_PRIMARY, 14, "start", "600", "", FONT_DISPLAY))
    parts.append(
        raw_text(
            262,
            36,
            '<tspan fill="%s">%d đóng góp</tspan><tspan fill="%s">  ·  </tspan><tspan fill="%s">chuỗi %d ngày</tspan>'
            % (CREAM, total_contribs, INK_FAINT, INK_SECOND, streaks["longest"]),
            INK_SECOND,
            11.5,
            "start",
            "500",
            "",
            FONT_DISPLAY,
        )
    )

    parts.append(text(1024, 36, "Ít", INK_MUTED, 10.5, "end", "500", "", FONT_DISPLAY))
    legend_specs = [
        (1040, 2.0, "#1c273d", 0),
        (1058, 3.2, "#34d399", 0),
        (1078, 4.2, "#a3e635", 0),
        (1100, 5.1, FIREFLY_GOLD, 8.5),
        (1124, 5.8, IVORY_WARM, 11.0),
    ]
    for lx, lr, lcol, halo in legend_specs:
        if halo > 0:
            parts.append('<circle cx="%d" cy="32" r="%s" fill="url(#mat-ff-gold)"/>' % (lx, num(halo)))
        parts.append('<circle cx="%d" cy="32" r="%s" fill="%s"/>' % (lx, num(lr), lcol))
    parts.append(text(1142, 36, "Nhiều", INK_MUTED, 10.5, "start", "500", "", FONT_DISPLAY))

    today = datetime.date.today()
    days_since_sun = (today.weekday() + 1) % 7
    end_sunday = today - datetime.timedelta(days=days_since_sun)
    start_sunday = end_sunday - datetime.timedelta(weeks=51)

    grid_x = 68.0
    grid_y = 78.0
    pitch_x = 21.35
    pitch_y = 19.2

    month_names = ("Th1", "Th2", "Th3", "Th4", "Th5", "Th6", "Th7", "Th8", "Th9", "Th10", "Th11", "Th12")
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
                parts.append(text(grid_x + w * pitch_x, 62, month_names[d.month - 1], INK_MUTED, 10, "middle", "500", "", FONT_DISPLAY))
                last_printed_w = w

    for row, lbl in ((1, "T2"), (3, "T4"), (5, "T6")):
        parts.append(text(46, grid_y + row * pitch_y + 3.8, lbl, INK_MUTED, 9.8, "end", "500"))

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
            col = FIREFLY_GOLD if (c + nc) >= 24 else EMERALD_SOFT
            op = min(0.48, 0.16 + (c + nc) / 110.0)
            parts.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="1.05" stroke-opacity="%s"/>' % (num(cx), num(cy), num(nx), num(ny), col, num(op)))
        if (w + 1, r) in coords and coords[(w + 1, r)][2] >= 4 and c >= 4:
            nx, ny, nc, _ = coords[(w + 1, r)]
            col = CREAM if (c + nc) >= 32 else TEAL_MIST
            op = min(0.42, 0.14 + (c + nc) / 130.0)
            parts.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="0.95" stroke-opacity="%s"/>' % (num(cx), num(cy), num(nx), num(ny), col, num(op)))
    parts.append("</g>")

    for (w, r), (cx, cy, c, _) in coords.items():
        if c == 0:
            parts.append('<circle cx="%s" cy="%s" r="2.15" fill="#1e2b45"/>' % (num(cx), num(cy)))
            parts.append('<circle cx="%s" cy="%s" r="0.85" fill="#33476b"/>' % (num(cx), num(cy)))
        elif c <= 3:
            parts.append('<circle cx="%s" cy="%s" r="5.2" fill="%s" fill-opacity="0.14"/>' % (num(cx), num(cy), EMERALD_MID))
            parts.append('<circle cx="%s" cy="%s" r="3.1" fill="%s"/>' % (num(cx), num(cy), EMERALD_MID))
        elif c <= 10:
            parts.append('<circle cx="%s" cy="%s" r="6.8" fill="#a3e635" fill-opacity="0.16"/>' % (num(cx), num(cy)))
            parts.append('<circle cx="%s" cy="%s" r="3.9" fill="#a3e635"/>' % (num(cx), num(cy)))
            parts.append('<circle cx="%s" cy="%s" r="1.5" fill="%s"/>' % (num(cx), num(cy), IVORY_WARM))
        elif c <= 25:
            parts.append('<circle cx="%s" cy="%s" r="9.5" fill="url(#mat-ff-gold)"/>' % (num(cx), num(cy)))
            parts.append('<circle cx="%s" cy="%s" r="4.6" fill="%s"/>' % (num(cx), num(cy), FIREFLY_GOLD))
            parts.append('<circle cx="%s" cy="%s" r="1.9" fill="#ffffff"/>' % (num(cx), num(cy)))
        else:
            parts.append('<circle cx="%s" cy="%s" r="13.5" fill="url(#mat-ff-gold)"/>' % (num(cx), num(cy)))
            parts.append('<circle cx="%s" cy="%s" r="5.5" fill="%s"/>' % (num(cx), num(cy), CREAM))
            parts.append('<circle cx="%s" cy="%s" r="2.5" fill="#ffffff"/>' % (num(cx), num(cy)))
            parts.append(
                '<path d="M%s %s V%s M%s %s H%s" stroke="#ffffff" stroke-width="0.85" stroke-opacity="0.75"/>'
                % (num(cx), num(cy - 8.2), num(cy + 8.2), num(cx - 8.2), num(cy), num(cx + 8.2))
            )

    water_y = 224.0
    breeze_path = "M84,158 C260,118 470,174 680,128 C820,98 920,136 1012,118"
    parts.append('<path d="%s" fill="none" stroke="%s" stroke-width="0.9" stroke-dasharray="2 6" stroke-opacity="0.22"/>' % (breeze_path, CREAM))
    for bi, b_dur in enumerate(("14s", "19s")):
        parts.append(
            '<g><circle r="5.5" fill="url(#mat-ff-gold)"/><circle r="1.5" fill="%s"/>'
            '<animate attributeName="opacity" values="0.25;0.92;0.4;0.95;0.25" dur="4.2s" begin="-%ds" repeatCount="indefinite"/>'
            '<animateMotion path="%s" dur="%s" begin="-%ds" repeatCount="indefinite"/></g>'
            % (IVORY_WARM, bi * 3, breeze_path, b_dur, bi * 8)
        )
    parts.append('<line x1="48" y1="%s" x2="1166" y2="%s" stroke="url(#mat-water)" stroke-width="1"/>' % (num(water_y), num(water_y)))
    for w in range(52):
        val = weeks52[w]
        if val <= 0:
            continue
        norm = (val / float(max_w)) ** 0.65
        wx = grid_x + w * pitch_x
        for ri in range(1, 4):
            rw = (3.5 + norm * 11.0) * (1.0 - ri * 0.2)
            ry = water_y + ri * 7.5 + (w % 2) * 1.5
            op = norm * (0.48 - ri * 0.11)
            col = CREAM if norm > 0.45 else EMERALD_SOFT
            parts.append(
                '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="1.2" stroke-linecap="round" stroke-opacity="%s"/>'
                % (num(wx - rw), num(ry), num(wx + rw), num(ry), col, num(op))
            )

    parts.extend(fireflies_layer("mat", width, height, ambient_count=38, drifter_count=18, seed=707, avoid_boxes=[(24, 14, 480, 32)]))
    parts.append("</g>")
    parts.append("</svg>")
    return "\n".join(parts)


def _project_3d(cx, cy, x, y, z):
    # WHY: True 3D axonometric projection (yaw=-20deg, tilt=57deg) gives genuine elevation depth z alongside radial x,y.
    yaw = math.radians(-20.0)
    tilt = math.radians(57.0)
    rx = x * math.cos(yaw) - y * math.sin(yaw)
    ry = x * math.sin(yaw) + y * math.cos(yaw)
    sx = cx + rx
    sy = cy + ry * math.cos(tilt) - z * math.sin(tilt)
    return sx, sy, ry


def render_3d_stack_radar(langs):
    cx, cy = 706.0, 212.0
    radius_max = 114.0
    mid_z = 36.0
    crown_z = 72.0
    apex_z = 88.0

    axes = ["HTML", "TypeScript", "JavaScript", "CSS", "Python", "Shell"]
    lang_map = dict(langs)
    pcts = lang_percentages(langs)
    pct_map = {name: pcts[i] for i, (name, _) in enumerate(langs)}
    total_bytes = sum(size for _, size in langs) or 1

    elems = [
        text(512, 50, "Stack Radar · 3D", INK_PRIMARY, 14, "start", "600", "", FONT_DISPLAY),
    ]

    outer_base = []
    outer_under = []
    outer_mid = []
    outer_crown = []
    for i in range(6):
        ang = -math.pi / 2.0 + i * math.pi / 3.0
        wx = math.cos(ang) * radius_max
        wy = math.sin(ang) * radius_max
        outer_base.append(_project_3d(cx, cy, wx, wy, 0.0)[:2])
        outer_under.append(_project_3d(cx, cy, wx, wy, -8.0)[:2])
        outer_mid.append(_project_3d(cx, cy, wx * 0.72, wy * 0.72, mid_z)[:2])
        outer_crown.append(_project_3d(cx, cy, wx, wy, crown_z)[:2])

    for i in range(6):
        j = (i + 1) % 6
        p0, p1 = outer_base[i], outer_base[j]
        u0, u1 = outer_under[i], outer_under[j]
        if (p0[1] + p1[1]) / 2.0 > cy - 4.0:
            elems.append(
                '<polygon points="%s,%s %s,%s %s,%s %s,%s" fill="#09101d" stroke="%s" stroke-width="0.95"/>'
                % (num(p0[0]), num(p0[1]), num(p1[0]), num(p1[1]), num(u1[0]), num(u1[1]), num(u0[0]), num(u0[1]), BORDER_WARM)
            )

    elems.append(
        '<polygon points="%s" fill="#090f1c" fill-opacity="0.90" stroke="%s" stroke-width="1.2"/>'
        % (" ".join("%s,%s" % (num(px), num(py)) for px, py in outer_base), BORDER_WARM)
    )

    for ring in (0.28, 0.54, 0.78):
        r_pts = []
        for i in range(6):
            ang = -math.pi / 2.0 + i * math.pi / 3.0
            sx, sy, _ = _project_3d(cx, cy, math.cos(ang) * radius_max * ring, math.sin(ang) * radius_max * ring, 0.0)
            r_pts.append("%s,%s" % (num(sx), num(sy)))
        elems.append('<polygon points="%s" fill="none" stroke="%s" stroke-width="0.85" stroke-dasharray="%s"/>' % (
            " ".join(r_pts), BORDER_SUBTLE, "2 3" if ring == 0.28 else "none"
        ))

    origin_x, origin_y, _ = _project_3d(cx, cy, 0.0, 0.0, 0.0)
    for i in range(6):
        bx, by = outer_base[i]
        ux, uy = outer_crown[i]
        elems.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="0.8"/>' % (num(origin_x), num(origin_y), num(bx), num(by), BORDER_SUBTLE))
        elems.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="0.8" stroke-dasharray="2 3" stroke-opacity="0.6"/>' % (num(bx), num(by), num(ux), num(uy), BORDER_WARM))

    elems.append(
        '<polygon points="%s" fill="none" stroke="%s" stroke-width="0.75" stroke-opacity="0.30" stroke-dasharray="2 4"/>'
        % (" ".join("%s,%s" % (num(px), num(py)) for px, py in outer_mid), EMERALD_SOFT)
    )
    elems.append(
        '<polygon points="%s" fill="none" stroke="%s" stroke-width="0.85" stroke-opacity="0.42" stroke-dasharray="3 4"/>'
        % (" ".join("%s,%s" % (num(px), num(py)) for px, py in outer_crown), SKY_SOFT)
    )

    orb_pts = []
    for deg in range(0, 361, 15):
        rad = math.radians(deg)
        ox, oy, _ = _project_3d(cx, cy, math.cos(rad) * (radius_max * 0.92), math.sin(rad) * (radius_max * 0.92), mid_z * 0.85 + math.sin(rad) * 10.0)
        orb_pts.append((ox, oy))
    orb_d = "M" + " L".join("%s,%s" % (num(px), num(py)) for px, py in orb_pts)
    elems.append('<path d="%s" fill="none" stroke="%s" stroke-width="0.75" stroke-opacity="0.22" stroke-dasharray="2 5"/>' % (orb_d, CREAM))
    elems.append(
        '<g><circle r="5.2" fill="url(#core-ff-gold)"/><circle r="1.5" fill="%s"/>'
        '<animateMotion path="%s" dur="18s" repeatCount="indefinite"/></g>'
        % (IVORY_WARM, orb_d)
    )

    top_ax, top_ay, _ = _project_3d(cx, cy, 0.0, 0.0, apex_z + 10.0)
    elems.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="0.9" stroke-dasharray="2 3" stroke-opacity="0.65"/>' % (
        num(origin_x), num(origin_y), num(top_ax), num(top_ay), CREAM
    ))

    verts_3d = []
    base_footprint = []
    for i, axis in enumerate(axes):
        ang = -math.pi / 2.0 + i * math.pi / 3.0
        share = lang_map.get(axis, 0) / float(total_bytes)
        pct_val = share * 100.0
        norm = math.log1p(pct_val * 6.0) / math.log1p(460.0) if pct_val > 0 else 0.0
        reach = 0.28 + 0.72 * norm if share > 0 else 0.22
        elev = 16.0 + (crown_z - 4.0) * norm if share > 0 else 12.0
        wx = math.cos(ang) * radius_max * reach
        wy = math.sin(ang) * radius_max * reach
        vx, vy, depth = _project_3d(cx, cy, wx, wy, elev)
        bx, by, bdepth = _project_3d(cx, cy, wx, wy, 0.0)
        verts_3d.append({"i": i, "axis": axis, "vx": vx, "vy": vy, "bx": bx, "by": by, "depth": depth, "bdepth": bdepth, "share": share})
        base_footprint.append((bx, by))

    elems.append(
        '<polygon points="%s" fill="%s" fill-opacity="0.10" stroke="%s" stroke-width="0.9" stroke-opacity="0.38"/>'
        % (" ".join("%s,%s" % (num(px), num(py)) for px, py in base_footprint), EMERALD_SOFT, EMERALD_SOFT)
    )

    ax, ay, adepth = _project_3d(cx, cy, 0.0, 0.0, apex_z)

    facets = []
    side_tones = ("#0e3a3e", "#134e4a", "#1e3a5f", "#2a3f5f", "#3b3526", "#16443b")
    roof_tones = ("#fde047", "#38bdf8", "#34d399", "#2dd4bf", "#fbbf24", "#fb923c")
    for i in range(6):
        j = (i + 1) % 6
        vi, vj = verts_3d[i], verts_3d[j]
        skirt_depth = (vi["bdepth"] + vj["bdepth"] + vi["depth"] + vj["depth"]) / 4.0 - 2.0
        facets.append((
            skirt_depth,
            "skirt",
            [(vi["bx"], vi["by"]), (vj["bx"], vj["by"]), (vj["vx"], vj["vy"]), (vi["vx"], vi["vy"])],
            side_tones[i],
            0.34,
            TEAL_MIST,
            0.45,
        ))
        roof_depth = (adepth + vi["depth"] + vj["depth"]) / 3.0
        is_front = (vi["vy"] + vj["vy"]) / 2.0 > cy - 8.0
        facets.append((
            roof_depth,
            "roof",
            [(ax, ay), (vi["vx"], vi["vy"]), (vj["vx"], vj["vy"])],
            roof_tones[i],
            0.27 if is_front else 0.17,
            CREAM if is_front else SKY_SOFT,
            0.82 if is_front else 0.52,
        ))

    facets.sort(key=lambda item: item[0])
    for _, kind, pts, fill_c, fill_op, stroke_c, stroke_op in facets:
        pts_str = " ".join("%s,%s" % (num(px), num(py)) for px, py in pts)
        elems.append(
            '<polygon points="%s" fill="%s" fill-opacity="%s" stroke="%s" stroke-width="%s" stroke-opacity="%s" stroke-linejoin="round"/>'
            % (pts_str, fill_c, num(fill_op), stroke_c, "1.2" if kind == "roof" else "0.85", num(stroke_op))
        )

    rim_pts = " ".join("%s,%s" % (num(v["vx"]), num(v["vy"])) for v in verts_3d)
    elems.append('<polygon points="%s" fill="none" stroke="%s" stroke-width="1.6" stroke-linejoin="round" filter="url(#core-bloom)"/>' % (rim_pts, CREAM))

    for v in verts_3d:
        elems.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="0.9" stroke-opacity="0.55"/>' % (
            num(v["bx"]), num(v["by"]), num(v["vx"]), num(v["vy"]), CREAM
        ))
        col_main, col_hi = LANG_PALETTE.get(v["axis"], (CREAM, IVORY))
        elems.append('<circle cx="%s" cy="%s" r="5.8" fill="url(#core-ff-gold)"/>' % (num(v["vx"]), num(v["vy"])))
        elems.append('<circle cx="%s" cy="%s" r="2.7" fill="%s" stroke="#ffffff" stroke-width="0.8"/>' % (num(v["vx"]), num(v["vy"]), col_hi))

    elems.append('<circle cx="%s" cy="%s" r="8.5" fill="url(#core-ff-gold)"/>' % (num(ax), num(ay)))
    elems.append('<circle cx="%s" cy="%s" r="3.1" fill="#ffffff"/>' % (num(ax), num(ay)))

    for i, axis in enumerate(axes):
        ux, uy = outer_crown[i]
        bx, by = outer_base[i]
        mx = (ux * 0.55 + bx * 0.45)
        my = (uy * 0.55 + by * 0.45)
        col_main, _ = LANG_PALETTE.get(axis, (CREAM, IVORY))
        pct = pct_map.get(axis, 0)
        pct_str = "%d%%" % pct if pct > 0 else "<1%"

        if i == 0:
            lx, ly, anchor = mx, uy - 16.0, "middle"
            elems.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="0.9" stroke-opacity="0.6"/>' % (num(ux), num(uy - 2), num(lx), num(ly + 5), col_main))
        elif i in (1, 2):
            lx = max(mx + 18.0, cx + 124.0)
            ly = my + (0.0 if i == 1 else 10.0)
            anchor = "start"
            elems.append('<polyline points="%s,%s %s,%s %s,%s" fill="none" stroke="%s" stroke-width="0.9" stroke-opacity="0.6"/>' % (
                num(mx + 3), num(my), num(lx - 12), num(ly - 4), num(lx - 4), num(ly - 4), col_main
            ))
        elif i == 3:
            lx, ly, anchor = bx, by + 24.0, "middle"
            elems.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="0.9" stroke-opacity="0.6"/>' % (num(bx), num(by + 3), num(lx), num(ly - 13), col_main))
        else:
            lx = min(mx - 18.0, cx - 120.0)
            ly = my + (10.0 if i == 4 else -2.0)
            anchor = "end"
            elems.append('<polyline points="%s,%s %s,%s %s,%s" fill="none" stroke="%s" stroke-width="0.9" stroke-opacity="0.6"/>' % (
                num(mx - 3), num(my), num(lx + 12), num(ly - 4), num(lx + 4), num(ly - 4), col_main
            ))

        elems.append(
            raw_text(
                lx,
                ly,
                '<tspan fill="%s" font-weight="700">%s</tspan><tspan fill="%s" font-weight="600"> %s</tspan>'
                % (col_main, esc(axis), INK_PRIMARY if pct >= 5 else INK_SECOND, esc(pct_str)),
                INK_PRIMARY,
                11.8,
                anchor,
                "600",
            )
        )

    return elems


def load_portrait_hd():
    path = os.path.join(ASSETS, "portrait_hd.json")
    if not os.path.exists(path):
        return {"cols": 1, "rows": 1, "grid": [[[CREAM, "@"]]]}
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def core_stage_svg(portrait_hd, langs, chars, commits, stars, total_contribs, events):
    width, height = 1200, 548
    clip_defs, frame_nodes = nocturne_card(width, height, "core", radius=16)

    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 548" width="1200" height="548" role="img" aria-label="Character Portrait, 3D Stack Radar, Telemetry and GitHub Console">',
        REDUCED_MOTION_STYLE,
        "<defs>",
    ]
    parts.extend(nocturne_defs("core"))
    parts.extend(clip_defs)
    parts.extend(
        [
            '<radialGradient id="core-aura-left" cx="21%%" cy="46%%" r="32%%">',
            '<stop offset="0%%" stop-color="%s" stop-opacity="0.10"/>' % CREAM,
            '<stop offset="100%%" stop-color="%s" stop-opacity="0"/>' % BG_NIGHT,
            "</radialGradient>",
            '<radialGradient id="core-aura-3d" cx="60%%" cy="36%%" r="30%%">',
            '<stop offset="0%%" stop-color="%s" stop-opacity="0.10"/>' % SKY_SOFT,
            '<stop offset="55%%" stop-color="%s" stop-opacity="0.06"/>' % FIREFLY_GOLD,
            '<stop offset="100%%" stop-color="%s" stop-opacity="0"/>' % BG_NIGHT,
            "</radialGradient>",
            '<filter id="core-atmos-blur" x="-15%%" y="-15%%" width="130%%" height="130%%">',
            '<feGaussianBlur stdDeviation="8.2"/>',
            "</filter>",
            '<clipPath id="core-avatar-clip"><circle cx="246" cy="248" r="198"/></clipPath>',
            "</defs>",
        ]
    )
    parts.extend(frame_nodes)
    parts.append('<g clip-path="url(#core-clip)">')
    parts.append('<rect x="1" y="1" width="1198" height="546" fill="url(#core-aura-left)"/>')
    parts.append('<rect x="1" y="1" width="1198" height="546" fill="url(#core-aura-3d)"/>')

    acx, acy, ar = 246.0, 248.0, 198.0
    parts.append('<circle cx="%s" cy="%s" r="%s" fill="#0d1320" stroke="%s" stroke-width="1.2"/>' % (num(acx), num(acy), num(ar + 6), BORDER_WARM))
    parts.append('<circle cx="%s" cy="%s" r="%s" fill="#0b101b"/>' % (num(acx), num(acy), num(ar)))

    parts.append('<g clip-path="url(#core-avatar-clip)">')
    atmos_n = max(int(portrait_hd.get("atmos_n") or 28), 1)
    atmos_cells = portrait_hd.get("atmos") or []
    if atmos_cells:
        cell_step = (ar * 2.0) / float(atmos_n)
        parts.append('<g filter="url(#core-atmos-blur)" opacity="0.52">')
        for ax_i, ay_i, acol in atmos_cells:
            px_a = (acx - ar) + (ax_i + 0.5) * cell_step
            py_a = (acy - ar) + (ay_i + 0.5) * cell_step
            parts.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (num(px_a, 1), num(py_a, 1), num(cell_step * 0.85, 1), acol))
        parts.append("</g>")
    cols = max(int(portrait_hd.get("cols") or 112), 1)
    rows = max(int(portrait_hd.get("rows") or 58), 1)
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
                % (num(acx), num(start_y + r_idx * row_step), FONT_MONO, num(font_sz, 2), "".join(tspan_parts))
            )
    parts.append("</g>")
    parts.append('<circle cx="%s" cy="%s" r="%s" fill="none" stroke="%s" stroke-width="1.2" stroke-opacity="0.45"/>' % (num(acx), num(acy), num(ar), CREAM))

    parts.append(text(acx, 486, DISPLAY, INK_PRIMARY, 21, "middle", "700", ' letter-spacing="0.2"', FONT_DISPLAY))
    parts.append(text(acx, 510, "@%s" % USERNAME, INK_MUTED, 11.5, "middle", "500"))

    parts.append('<line x1="484" y1="34" x2="484" y2="514" stroke="%s" stroke-width="1"/>' % BORDER_SUBTLE)

    parts.extend(render_3d_stack_radar(langs))

    parts.append('<line x1="946" y1="48" x2="946" y2="322" stroke="%s" stroke-width="1"/>' % BORDER_SUBTLE)
    metrics = [
        (970, 86, compact(chars), "Ký tự mã nguồn", CREAM, False),
        (970, 156, str(commits), "Commits trong năm", INK_PRIMARY, False),
        (970, 226, str(stars), "Stars đạt được", FIREFLY_GOLD, True),
        (970, 296, str(total_contribs), "Tổng đóng góp", EMERALD_SOFT, False),
    ]
    for mx, my, mval, mlbl, mcol, with_star in metrics:
        parts.append(text(mx, my, mval, mcol, 26, "start", "700", ' letter-spacing="-0.5"'))
        if with_star:
            sx = mx + len(mval) * 16.5 + 12.0
            parts.append('<path d="%s" fill="%s"/>' % (star_path(sx, my - 9.0, 6.8, 2.9), FIREFLY_GOLD))
        parts.append(text(mx, my + 20, mlbl, INK_SECOND, 11.2, "start", "400", "", FONT_DISPLAY))

    cx0, cy0, cw, ch = 510, 344, 662, 178
    parts.append('<rect x="%d" y="%d" width="%d" height="%d" rx="12" fill="%s" stroke="%s" stroke-width="1"/>' % (cx0, cy0, cw, ch, BG_CONSOLE, BORDER_SUBTLE))
    for di, dcol in enumerate(("#334155", "#475569", "#64748b")):
        parts.append('<circle cx="%d" cy="%d" r="3.2" fill="%s"/>' % (cx0 + 18 + di * 12, cy0 + 19, dcol))
    parts.append(
        raw_text(
            cx0 + 62,
            cy0 + 23,
            '<tspan fill="%s">$</tspan><tspan fill="%s"> gh activity --recent</tspan>' % (EMERALD_SOFT, INK_MUTED),
            INK_MUTED,
            10.5,
            "start",
            "500",
        )
    )
    parts.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="1"/>' % (cx0 + 14, cy0 + 34, cx0 + cw - 14, cy0 + 34, BORDER_SUBTLE))

    rows_ev = events[:5] if events else [{"time": "--:--", "sha": "-------", "repo": USERNAME, "message": "awaiting push event"}]
    for i, ev in enumerate(rows_ev):
        ry = cy0 + 57 + i * 25
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

    avoid = [
        (acx - ar + 8, acy - ar + 8, (ar - 8) * 2, (ar - 8) * 2),
        (cx0, cy0, cw, ch),
        (956, 48, 210, 276),
    ]
    parts.extend(fireflies_layer("core", width, height, ambient_count=42, drifter_count=20, seed=909, avoid_boxes=avoid))
    parts.append("</g>")
    parts.append("</svg>")
    return "\n".join(parts)


def write(name, content):
    path = os.path.join(ASSETS, name)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(content)
    print("wrote %s (%d bytes)" % (name, len(content.encode("utf-8"))))


def main():
    os.makedirs(ASSETS, exist_ok=True)
    data = collect()
    if not data["days"] and not data["total"] and not data["repos"]:
        raise SystemExit("error: GitHub API returned no profile data, assets left untouched")
    streaks = compute_streaks(data["days"], data["weeks"])

    write("01-firefly-matrix.svg", firefly_matrix_svg(data["days"], data["total"], streaks))
    write(
        "02-core-stage.svg",
        core_stage_svg(
            load_portrait_hd(),
            data["langs"],
            data["bytes"],
            data["commits"],
            data["stars"],
            data["total"],
            data["events"],
        ),
    )
    for card_name, card_svg in render_flagship_cards(data["repo_map"]).items():
        write(card_name, card_svg)

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
