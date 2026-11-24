import datetime
import json
import math
import os
import urllib.request

from cards import render_flagship_cards
from theme import (
    AMBER,
    BG_VOID,
    BG_WELL,
    BG_WELL_ALT,
    CORAL,
    CYAN,
    CYAN_DEEP,
    FONT_DISPLAY,
    FONT_MONO,
    HEAT_LEVELS,
    INK,
    INK_DIM,
    INK_MICRO,
    INK_SUB,
    LANG_COLORS,
    PHOSPHOR,
    PHOSPHOR_DEEP,
    PHOSPHOR_HI,
    PHOSPHOR_LOW,
    PHOSPHOR_MID,
    REDUCED_MOTION_STYLE,
    SLATE,
    STROKE_FRAME,
    STROKE_HAIR,
    STROKE_SPECULAR,
    arch_mark,
    chassis_plate,
    common_defs,
    compact,
    corner_reticles,
    esc,
    num,
    raw_text,
    text,
)

USERNAME = os.environ.get("GH_PROFILE_USERNAME", "broamstuck-cybr")
HANDLE = os.environ.get("GH_PROFILE_HANDLE", "broamstuck")
DISPLAY = os.environ.get("GH_PROFILE_DISPLAY", "Bro Am Stuck")
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
        "disk": 0,
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
            disk_kb = int(node.get("diskUsage") or 0)
            data["stars"] += stars
            data["disk"] += disk_kb * 1024
            if name:
                data["repo_map"][name] = {
                    "name": name,
                    "description": node.get("description") or "",
                    "homepage": node.get("homepageUrl") or "",
                    "stars": stars,
                    "disk_kb": disk_kb,
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


def compute_telemetry(day_map, weeks):
    if not day_map:
        return {
            "longest": 0,
            "current": 0,
            "peak": 0,
            "peak_date": "--",
            "active_weeks_pct": 0,
            "weeks52": [0] * 52,
            "spark12": [0] * 12,
        }
    ordered = sorted(day_map.items())
    longest = 0
    run = 0
    peak = 0
    peak_date = "--"
    for iso_date, count in ordered:
        if count > peak:
            peak = count
            peak_date = iso_date
        if count > 0:
            run += 1
            if run > longest:
                longest = run
        else:
            run = 0
    current = 0
    today = datetime.date.today()
    cursor = today
    if day_map.get(cursor.isoformat(), 0) == 0:
        cursor = today - datetime.timedelta(days=1)
    while day_map.get(cursor.isoformat(), 0) > 0:
        current += 1
        cursor -= datetime.timedelta(days=1)
    active_weeks = sum(1 for w in weeks if w > 0)
    active_weeks_pct = int(round((active_weeks / float(max(len(weeks), 1))) * 100.0))
    w52 = list(weeks[-52:])
    if len(w52) < 52:
        w52 = ([0] * (52 - len(w52))) + w52
    return {
        "longest": longest,
        "current": current,
        "peak": peak,
        "peak_date": peak_date[5:] if len(peak_date) >= 10 else peak_date,
        "active_weeks_pct": active_weeks_pct,
        "weeks52": w52,
        "spark12": w52[-12:],
    }


def truncate_clean(body, max_len):
    text_s = (body or "").strip()
    if len(text_s) <= max_len:
        return text_s
    cut = text_s[: max_len - 1]
    if " " in cut and cut.rfind(" ") >= max_len // 2:
        cut = cut[: cut.rfind(" ")]
    return cut.rstrip(" ,;:-/") + "…"


def smooth_curve_path(points):
    if len(points) < 2:
        return ""
    cmds = ["M%s,%s" % (num(points[0][0]), num(points[0][1]))]
    for i in range(1, len(points)):
        x0, y0 = points[i - 1]
        x1, y1 = points[i]
        mx = (x0 + x1) / 2.0
        cmds.append("C%s,%s %s,%s %s,%s" % (num(mx), num(y0), num(mx), num(y1), num(x1), num(y1)))
    return " ".join(cmds)


def lang_percentages(langs):
    total = sum(size for _, size in langs) or 1
    raw = [size * 100.0 / total for _, size in langs]
    counts = [int(value) for value in raw]
    order = sorted(range(len(raw)), key=lambda i: raw[i] - counts[i], reverse=True)
    for i in order[: max(0, 100 - sum(counts))]:
        counts[i] += 1
    return counts


def monolith_hero_svg(total_contribs, commits, telemetry):
    width, height = 1200, 300
    clip_defs, frame_nodes = chassis_plate(width, height, "hero", PHOSPHOR, grid_opacity=0.55, radius=14)
    weeks52 = telemetry["weeks52"]
    max_w = max(weeks52) if any(weeks52) else 1

    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 300" width="1200" height="300" role="img" aria-label="BroAmStuck Telemetry Monolith">',
        REDUCED_MOTION_STYLE,
        "<defs>",
    ]
    parts.extend(common_defs("hero"))
    parts.extend(clip_defs)
    parts.extend(
        [
            '<linearGradient id="hero-word" x1="0" y1="0" x2="0" y2="1">',
            '<stop offset="0%" stop-color="#ffffff"/>',
            '<stop offset="100%" stop-color="#cbd5e1"/>',
            "</linearGradient>",
            '<radialGradient id="hero-aura" cx="76%" cy="48%" r="42%">',
            '<stop offset="0%%" stop-color="%s" stop-opacity="0.14"/>' % PHOSPHOR,
            '<stop offset="55%%" stop-color="%s" stop-opacity="0.05"/>' % CYAN,
            '<stop offset="100%%" stop-color="%s" stop-opacity="0"/>' % BG_VOID,
            "</radialGradient>",
            '<linearGradient id="hero-curtain" x1="0" y1="0" x2="0" y2="1">',
            '<stop offset="0%%" stop-color="%s" stop-opacity="0.34"/>' % PHOSPHOR,
            '<stop offset="65%%" stop-color="%s" stop-opacity="0.08"/>' % CYAN_DEEP,
            '<stop offset="100%%" stop-color="%s" stop-opacity="0"/>' % BG_WELL,
            "</linearGradient>",
            '<linearGradient id="hero-sweep" x1="0" y1="0" x2="1" y2="0">',
            '<stop offset="0%%" stop-color="%s" stop-opacity="0"/>' % CYAN,
            '<stop offset="85%%" stop-color="%s" stop-opacity="0.16"/>' % CYAN,
            '<stop offset="100%%" stop-color="%s" stop-opacity="0.72"/>' % PHOSPHOR_HI,
            "</linearGradient>",
            '<clipPath id="hero-scope"><rect x="556" y="24" width="618" height="252" rx="10"/></clipPath>',
            "</defs>",
        ]
    )
    parts.extend(frame_nodes)
    parts.append('<rect x="1" y="1" width="1198" height="298" rx="14" fill="url(#hero-aura)"/>')

    gx, gy = 78, 84
    parts.append('<circle cx="%d" cy="%d" r="35" fill="none" stroke="%s" stroke-width="0.9"/>' % (gx, gy, STROKE_FRAME))
    parts.append(
        '<circle cx="%d" cy="%d" r="31" fill="none" stroke="%s" stroke-width="1.2" stroke-dasharray="16 14 4 14" stroke-opacity="0.65">'
        '<animateTransform attributeName="transform" type="rotate" from="0 %d %d" to="360 %d %d" dur="34s" repeatCount="indefinite"/></circle>'
        % (gx, gy, CYAN, gx, gy, gx, gy)
    )
    for deg in range(0, 360, 15):
        rad = math.radians(deg)
        r0 = 35.0
        r1 = 38.5 if deg % 45 == 0 else 37.0
        parts.append(
            '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s"/>'
            % (
                num(gx + math.cos(rad) * r0),
                num(gy + math.sin(rad) * r0),
                num(gx + math.cos(rad) * r1),
                num(gy + math.sin(rad) * r1),
                CYAN if deg % 90 == 0 else STROKE_SPECULAR,
                "1.2" if deg % 90 == 0 else "0.7",
            )
        )
    parts.append('<circle cx="%d" cy="%d" r="24" fill="%s" stroke="%s" stroke-width="1"/>' % (gx, gy, BG_WELL, STROKE_SPECULAR))
    parts.append(arch_mark(gx - 12, gy - 12, 24, CYAN))

    parts.append(text(132, 90, "BROAMSTUCK", "url(#hero-word)", 42, "start", "800", ' letter-spacing="2.2"', FONT_DISPLAY))
    parts.append(
        raw_text(
            134,
            116,
            '<tspan fill="%s" font-weight="600">@%s</tspan>'
            '<tspan fill="%s">   /   </tspan>'
            '<tspan fill="%s">ARCH 6.12 LTS</tspan>'
            '<tspan fill="%s">   /   </tspan>'
            '<tspan fill="%s" font-weight="600">HYPRLAND</tspan>'
            % (CYAN, esc(USERNAME), INK_MICRO, INK_SUB, INK_MICRO, PHOSPHOR),
            INK_SUB,
            11.2,
            "start",
            "500",
            ' letter-spacing="0.6"',
        )
    )

    parts.append('<line x1="42" y1="148" x2="526" y2="148" stroke="%s" stroke-width="1"/>' % STROKE_FRAME)
    for tx in range(42, 527, 22):
        th = 6 if (tx - 42) % 88 == 0 else 3
        parts.append('<line x1="%d" y1="148" x2="%d" y2="%d" stroke="%s" stroke-width="0.9"/>' % (tx, tx, 148 + th, STROKE_SPECULAR))

    commit_ratio = min(1.0, commits / float(max(total_contribs, 1)))
    spark12 = telemetry["spark12"]
    spark_max = max(spark12) if any(spark12) else 1
    channels = [
        (42, str(total_contribs), "CONTRIBS", PHOSPHOR_HI, "spark"),
        (166, str(commits), "COMMITS", INK, "bar"),
        (290, "%dd" % telemetry["longest"], "MAX STREAK", AMBER, "ticks"),
        (414, "%dd" % telemetry["current"], "ACTIVE", CYAN, "pulse"),
    ]
    for cx, val, lbl, col, deco in channels:
        cw, ch = 114, 102
        cy = 172
        parts.append('<rect x="%d" y="%d" width="%d" height="%d" rx="9" fill="%s" stroke="%s" stroke-width="1"/>' % (cx, cy, cw, ch, BG_WELL, STROKE_FRAME))
        parts.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="2" stroke-opacity="0.88"/>' % (cx + 12, cy + 1, cx + 44, cy + 1, col))
        parts.append(text(cx + 13, cy + 22, lbl, INK_DIM, 8.6, "start", "600", ' letter-spacing="1.2"'))
        parts.append(text(cx + 13, cy + 58, val, col, 26, "start", "700", ' letter-spacing="-0.6"'))
        if deco == "spark":
            for si, sv in enumerate(spark12):
                bh = max(3.0, 20.0 * (sv / float(spark_max)))
                bx = cx + 13 + si * 7.5
                parts.append(
                    '<rect x="%s" y="%s" width="4.5" height="%s" rx="1.5" fill="%s" fill-opacity="%s"/>'
                    % (num(bx), num(cy + 90 - bh), num(bh), PHOSPHOR if sv > 0 else STROKE_FRAME, "0.85" if sv > 0 else "0.5")
                )
        elif deco == "bar":
            parts.append('<rect x="%d" y="%d" width="88" height="5" rx="2.5" fill="%s"/>' % (cx + 13, cy + 82, STROKE_HAIR))
            parts.append('<rect x="%d" y="%d" width="%s" height="5" rx="2.5" fill="%s"/>' % (cx + 13, cy + 82, num(88.0 * commit_ratio), PHOSPHOR))
            parts.append(text(cx + 101, cy + 77, "%d%%" % int(round(commit_ratio * 100)), INK_DIM, 8, "end", "600"))
        elif deco == "ticks":
            filled = min(10, max(1, int(round(telemetry["longest"] / 3.0))))
            for ti in range(10):
                tx = cx + 13 + ti * 9.0
                parts.append(
                    '<rect x="%s" y="%d" width="6" height="10" rx="1.5" fill="%s" fill-opacity="%s"/>'
                    % (num(tx), cy + 78, AMBER if ti < filled else STROKE_FRAME, "0.9" if ti < filled else "0.45")
                )
        else:
            parts.append('<circle cx="%d" cy="%d" r="3.5" fill="%s" filter="url(#hero-glow)"/>' % (cx + 18, cy + 83, PHOSPHOR_HI))
            parts.append(
                '<circle cx="%d" cy="%d" r="3.5" fill="none" stroke="%s" stroke-width="1">'
                '<animate attributeName="r" values="3.5;11" dur="2.6s" repeatCount="indefinite"/>'
                '<animate attributeName="opacity" values="0.85;0" dur="2.6s" repeatCount="indefinite"/></circle>'
                % (cx + 18, cy + 83, PHOSPHOR_HI)
            )
            parts.append(text(cx + 30, cy + 86, "LIVE", PHOSPHOR, 9, "start", "600", ' letter-spacing="1.2"'))

    vx, vy, vw, vh = 556, 24, 618, 252
    parts.append('<rect x="%d" y="%d" width="%d" height="%d" rx="10" fill="%s" stroke="%s" stroke-width="1"/>' % (vx, vy, vw, vh, BG_WELL, STROKE_FRAME))
    parts.append('<g clip-path="url(#hero-scope)">')

    for gy_line in (72, 114, 156, 198, 240):
        parts.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="0.7" stroke-opacity="0.75"/>' % (vx, gy_line, vx + vw, gy_line, STROKE_HAIR))
    for gx_line in range(vx + 48, vx + vw, 52):
        parts.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="0.6" stroke-dasharray="2 5" stroke-opacity="0.6"/>' % (gx_line, vy + 36, gx_line, vy + vh - 16, STROKE_HAIR))

    layers = [
        (0.28, -56, -24, 0.22, STROKE_SPECULAR, 0.8),
        (0.42, -42, -16, 0.28, CYAN_DEEP, 0.9),
        (0.56, -28, -10, 0.36, CYAN_DEEP, 1.0),
        (0.72, -16, -5, 0.48, CYAN, 1.1),
        (0.86, -7, -2, 0.62, PHOSPHOR_MID, 1.25),
    ]
    base_y = vy + vh - 26
    x_start = vx + 26
    x_span = vw - 58
    amp_max = 136.0

    for scale, dy_off, dx_off, op, col, sw in layers:
        pts = []
        for idx, val in enumerate(weeks52):
            t = idx / 51.0
            px = x_start + dx_off + t * x_span
            norm = (val / float(max_w)) ** 0.72 if val > 0 else 0.0
            harmonic = 0.04 * math.sin(idx * 0.42 + scale * 4.0)
            py = base_y + dy_off - (norm * amp_max * scale) - (harmonic * 18.0)
            pts.append((px, py))
        parts.append('<path d="%s" fill="none" stroke="%s" stroke-width="%s" stroke-opacity="%s"/>' % (smooth_curve_path(pts), col, num(sw), num(op)))

    main_pts = []
    peak_idx = 0
    peak_val = -1
    for idx, val in enumerate(weeks52):
        t = idx / 51.0
        px = x_start + t * x_span
        norm = (val / float(max_w)) ** 0.72 if val > 0 else 0.0
        py = base_y - (norm * amp_max)
        main_pts.append((px, py))
        if val > peak_val:
            peak_val = val
            peak_idx = idx
    curve_d = smooth_curve_path(main_pts)
    area_d = curve_d + " L%s,%s L%s,%s Z" % (num(main_pts[-1][0]), num(base_y + 18), num(main_pts[0][0]), num(base_y + 18))
    parts.append('<path d="%s" fill="url(#hero-curtain)"/>' % area_d)
    parts.append('<path d="%s" fill="none" stroke="%s" stroke-width="2" filter="url(#hero-glow)"/>' % (curve_d, PHOSPHOR_HI))

    parts.append(
        '<rect x="%d" y="%d" width="44" height="%d" fill="url(#hero-sweep)">'
        '<animateTransform attributeName="transform" type="translate" from="-44 0" to="%d 0" dur="8.5s" repeatCount="indefinite"/></rect>'
        % (vx, vy, vh, vw + 60)
    )
    parts.append(
        '<circle r="3.4" fill="%s" filter="url(#hero-glow)">'
        '<animateMotion dur="7.5s" repeatCount="indefinite" path="%s"/></circle>'
        % (PHOSPHOR_HI, curve_d)
    )

    pkx, pky = main_pts[peak_idx]
    parts.append('<line x1="%s" y1="%s" x2="%s" y2="%d" stroke="%s" stroke-width="1" stroke-dasharray="3 3" stroke-opacity="0.75"/>' % (num(pkx), num(pky), num(pkx), base_y + 12, AMBER))
    parts.append('<circle cx="%s" cy="%s" r="9" fill="none" stroke="%s" stroke-width="1" stroke-opacity="0.75"/>' % (num(pkx), num(pky), AMBER))
    parts.append('<circle cx="%s" cy="%s" r="3.2" fill="%s" filter="url(#hero-glow)"/>' % (num(pkx), num(pky), AMBER))
    tag_w = 132.0
    if pkx > vx + 260:
        tag_x = pkx - tag_w - 22.0
        leader_x0, leader_x1 = tag_x + tag_w, pkx - 10.0
    else:
        tag_x = pkx + 22.0
        leader_x0, leader_x1 = pkx + 10.0, tag_x
    tag_y = max(vy + 42.0, min(pky - 11.0, vy + 96.0))
    parts.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="0.9" stroke-opacity="0.75"/>' % (num(leader_x0), num(tag_y + 11.0), num(leader_x1), num(pky), AMBER))
    parts.append('<rect x="%s" y="%s" width="%s" height="22" rx="4" fill="%s" fill-opacity="0.94" stroke="%s" stroke-width="0.95"/>' % (num(tag_x), num(tag_y), num(tag_w), BG_VOID, AMBER))
    parts.append(text(tag_x + tag_w / 2.0, tag_y + 14.5, "PEAK %d · %s" % (telemetry["peak"], telemetry["peak_date"]), AMBER, 9, "middle", "700", ' letter-spacing="0.5"'))

    today_d = datetime.date.today()
    end_sun = today_d - datetime.timedelta(days=(today_d.weekday() + 1) % 7)
    start_sun = end_sun - datetime.timedelta(weeks=51)
    m_abbr = ("JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC")
    for wi in (0, 9, 18, 27, 36, 45, 51):
        wx = x_start + (wi / 51.0) * x_span
        wd = start_sun + datetime.timedelta(weeks=wi)
        parts.append('<line x1="%s" y1="%d" x2="%s" y2="%d" stroke="%s" stroke-width="0.8"/>' % (num(wx), base_y + 6, num(wx), base_y + 11, STROKE_SPECULAR))
        parts.append(text(wx, base_y + 20, m_abbr[wd.month - 1], INK_MICRO, 7.6, "middle", "600", ' letter-spacing="0.8"'))

    for idx_y, y_lbl in enumerate(("0", "33", "66", "100")):
        yy = base_y - idx_y * (amp_max / 3.0)
        parts.append('<line x1="%d" y1="%s" x2="%d" y2="%s" stroke="%s" stroke-width="0.9"/>' % (vx + vw - 22, num(yy), vx + vw - 16, num(yy), STROKE_SPECULAR))
        parts.append(text(vx + vw - 26, yy + 3, y_lbl, INK_MICRO, 7.5, "end"))

    parts.append(text(vx + 16, vy + 22, "SIGNAL TERRAIN  //  52W", INK_DIM, 8.8, "start", "600", ' letter-spacing="1.2"'))
    parts.append('<circle cx="%d" cy="%d" r="3" fill="%s"/>' % (vx + vw - 76, vy + 18.5, PHOSPHOR))
    parts.append(text(vx + vw - 16, vy + 22, "SYNCED", PHOSPHOR, 8.5, "end", "600", ' letter-spacing="1.1"'))

    parts.append("</g>")
    parts.append(corner_reticles(vx, vy, vw, vh, arm=8, color=STROKE_SPECULAR, stroke_w=0.9, inset=6))
    parts.append("</svg>")
    return "\n".join(parts)


def portrait_luminance_runs(line):
    # WHY: Grouping adjacent ASCII chars by luminance tier keeps SVG lightweight while giving 4-tier optical 3D shading.
    def tier_color(ch):
        if ch == "@":
            return PHOSPHOR_HI, "700"
        if ch in ("%#"):
            return PHOSPHOR, "600"
        if ch in ("*+="):
            return PHOSPHOR_MID, "500"
        return PHOSPHOR_LOW, "400"

    spans = []
    cur_style = None
    buf = []
    for ch in line:
        if ch == " ":
            style = ("space", "400")
        else:
            style = tier_color(ch)
        if style == cur_style:
            buf.append(ch)
        else:
            if buf:
                chunk = esc("".join(buf))
                if cur_style[0] == "space":
                    spans.append(chunk)
                else:
                    spans.append('<tspan fill="%s" font-weight="%s">%s</tspan>' % (cur_style[0], cur_style[1], chunk))
            cur_style = style
            buf = [ch]
    if buf:
        chunk = esc("".join(buf))
        if cur_style[0] == "space":
            spans.append(chunk)
        else:
            spans.append('<tspan fill="%s" font-weight="%s">%s</tspan>' % (cur_style[0], cur_style[1], chunk))
    return "".join(spans)


def identity_telemetry_svg(portrait_lines, langs, stars, repos, chars, disk, events, telemetry):
    width, height = 1200, 468
    clip_defs, frame_nodes = chassis_plate(width, height, "id", CYAN, grid_opacity=0.45, radius=14)

    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 468" width="1200" height="468" role="img" aria-label="Identity Portrait and Live Telemetry">',
        REDUCED_MOTION_STYLE,
        "<defs>",
    ]
    parts.extend(common_defs("id"))
    parts.extend(clip_defs)
    parts.extend(
        [
            '<radialGradient id="id-crt" cx="50%" cy="46%" r="48%">',
            '<stop offset="0%%" stop-color="%s" stop-opacity="0.16"/>' % PHOSPHOR,
            '<stop offset="55%%" stop-color="%s" stop-opacity="0.05"/>' % PHOSPHOR_DEEP,
            '<stop offset="100%%" stop-color="%s" stop-opacity="0"/>' % BG_WELL,
            "</radialGradient>",
            '<linearGradient id="id-scan" x1="0" y1="0" x2="0" y2="1">',
            '<stop offset="0%%" stop-color="%s" stop-opacity="0"/>' % PHOSPHOR,
            '<stop offset="70%%" stop-color="%s" stop-opacity="0.12"/>' % PHOSPHOR,
            '<stop offset="100%%" stop-color="%s" stop-opacity="0.55"/>' % PHOSPHOR_HI,
            "</linearGradient>",
            '<linearGradient id="id-sweep" x1="0" y1="0" x2="1" y2="1">',
            '<stop offset="0%%" stop-color="%s" stop-opacity="0.34"/>' % PHOSPHOR,
            '<stop offset="100%%" stop-color="%s" stop-opacity="0"/>' % PHOSPHOR,
            "</linearGradient>",
            '<linearGradient id="id-arc" x1="0" y1="0" x2="1" y2="1">',
            '<stop offset="0%%" stop-color="%s"/>' % CYAN,
            '<stop offset="100%%" stop-color="%s"/>' % PHOSPHOR_HI,
            "</linearGradient>",
            '<pattern id="id-raster" width="8" height="6" patternUnits="userSpaceOnUse">',
            '<line x1="0" y1="0" x2="8" y2="0" stroke="#ffffff" stroke-width="0.6" stroke-opacity="0.025"/>',
            "</pattern>",
            '<clipPath id="id-portrait-clip"><rect x="20" y="20" width="548" height="428" rx="10"/></clipPath>',
            "</defs>",
        ]
    )
    parts.extend(frame_nodes)

    px, py, pw, ph = 20, 20, 548, 428
    parts.append('<rect x="%d" y="%d" width="%d" height="%d" rx="10" fill="%s" stroke="%s" stroke-width="1"/>' % (px, py, pw, ph, BG_WELL, STROKE_FRAME))
    parts.append('<g clip-path="url(#id-portrait-clip)">')
    parts.append('<rect x="%d" y="%d" width="%d" height="%d" fill="url(#id-crt)"/>' % (px, py, pw, ph))
    parts.append('<rect x="%d" y="%d" width="%d" height="%d" fill="url(#id-raster)"/>' % (px, py, pw, ph))

    for ry in range(py + 46, py + ph - 44, 16):
        tick = 7 if (ry - py) % 64 == 0 else 3.5
        parts.append('<line x1="%d" y1="%d" x2="%s" y2="%d" stroke="%s" stroke-width="0.8"/>' % (px + 8, ry, num(px + 8 + tick), ry, STROKE_SPECULAR))
        parts.append('<line x1="%s" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="0.8"/>' % (num(px + pw - 8 - tick), ry, px + pw - 8, ry, STROKE_SPECULAR))

    parts.append(text(px + 18, py + 24, "OPTICAL PORTRAIT  //  TTY1", INK_DIM, 8.6, "start", "600", ' letter-spacing="1.2"'))
    parts.append(text(px + pw - 18, py + 24, "HYPRLAND", CYAN, 8.6, "end", "600", ' letter-spacing="1.1"'))

    max_len = max((len(line) for line in portrait_lines), default=1)
    line_count = max(len(portrait_lines), 1)
    step = min(334.0 / line_count, 9.2)
    font_size = min(step * 1.16, (pw - 64.0) / max(max_len * 0.61, 1.0))
    total_h = line_count * step
    start_y = py + 44 + (342.0 - total_h) / 2.0 + font_size * 0.78
    center_x = px + pw / 2.0

    for idx, raw_line in enumerate(portrait_lines):
        padded = raw_line.ljust(max_len)
        if not padded.strip():
            continue
        inner = portrait_luminance_runs(padded)
        parts.append(
            '<text x="%s" y="%s" font-family="%s" font-size="%s" text-anchor="middle" xml:space="preserve">%s</text>'
            % (num(center_x), num(start_y + idx * step), FONT_MONO, num(font_size), inner)
        )

    parts.append(
        '<rect x="%d" y="%d" width="%d" height="28" fill="url(#id-scan)">'
        '<animateTransform attributeName="transform" type="translate" from="0 -30" to="0 %d" dur="7.2s" repeatCount="indefinite"/></rect>'
        % (px, py + 28, pw, ph - 48)
    )

    parts.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="1"/>' % (px + 16, py + ph - 38, px + pw - 16, py + ph - 38, STROKE_HAIR))
    parts.append(
        raw_text(
            px + 20,
            py + ph - 16,
            '<tspan fill="%s">%s@arch</tspan>'
            '<tspan fill="%s">:~$ </tspan>'
            '<tspan fill="%s" font-weight="700">%s</tspan>'
            % (CYAN, esc(HANDLE), INK_DIM, PHOSPHOR_HI, esc(DISPLAY)),
            INK,
            10.5,
            "start",
            "500",
        )
    )
    cursor_x = px + 20 + (len(HANDLE) + len(DISPLAY) + 10) * 6.45
    parts.append(
        '<rect x="%s" y="%d" width="7" height="12" rx="1.5" fill="%s">'
        '<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.48;0.52;1" dur="1.15s" repeatCount="indefinite"/></rect>'
        % (num(cursor_x), py + ph - 26, PHOSPHOR_HI)
    )
    parts.append(text(px + pw - 20, py + ph - 16, "WAYLAND", INK_MICRO, 8.5, "end", "600", ' letter-spacing="1.1"'))
    parts.append("</g>")
    parts.append(corner_reticles(px, py, pw, ph, arm=8, color=STROKE_SPECULAR, stroke_w=0.9, inset=6))

    rx, ry, rw, rh = 584, 20, 368, 240
    parts.append('<rect x="%d" y="%d" width="%d" height="%d" rx="10" fill="%s" stroke="%s" stroke-width="1"/>' % (rx, ry, rw, rh, BG_WELL, STROKE_FRAME))
    parts.append(text(rx + 16, ry + 24, "STACK RADAR", INK_DIM, 8.8, "start", "600", ' letter-spacing="1.2"'))
    parts.append(text(rx + rw - 16, ry + 24, "%d LANGS" % len(langs), CYAN, 8.5, "end", "600", ' letter-spacing="1.0"'))

    axes = ["HTML", "TypeScript", "JavaScript", "CSS", "Python", "Shell"]
    short_axes = {"HTML": "HTML", "TypeScript": "TS", "JavaScript": "JS", "CSS": "CSS", "Python": "PY", "Shell": "SH"}
    lang_map = dict(langs)
    pct_list = lang_percentages(langs)
    pct_map = {name: pct_list[i] for i, (name, _) in enumerate(langs)}
    top_size = max([lang_map.get(a, 0) for a in axes] or [1]) or 1

    rcx, rcy, rrad = rx + rw / 2.0, ry + 132.0, 74.0
    parts.append('<circle cx="%s" cy="%s" r="%s" fill="none" stroke="%s" stroke-width="0.7" stroke-dasharray="2 4"/>' % (num(rcx), num(rcy), num(rrad + 10), STROKE_FRAME))
    for deg in range(0, 360, 30):
        rad = math.radians(deg)
        parts.append(
            '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="0.8"/>'
            % (
                num(rcx + math.cos(rad) * (rrad + 8)),
                num(rcy + math.sin(rad) * (rrad + 8)),
                num(rcx + math.cos(rad) * (rrad + 12)),
                num(rcy + math.sin(rad) * (rrad + 12)),
                STROKE_SPECULAR if deg % 60 == 0 else STROKE_HAIR,
            )
        )
    for ring in (0.33, 0.66, 1.0):
        r = rrad * ring
        ring_pts = []
        for i in range(6):
            ang = -math.pi / 2.0 + i * math.pi / 3.0
            ring_pts.append("%s,%s" % (num(rcx + math.cos(ang) * r), num(rcy + math.sin(ang) * r)))
        parts.append('<polygon points="%s" fill="none" stroke="%s" stroke-width="%s"/>' % (" ".join(ring_pts), STROKE_FRAME if ring == 1.0 else STROKE_HAIR, "1" if ring == 1.0 else "0.75"))
    sweep_a1 = -math.pi / 2.0
    sweep_a2 = sweep_a1 + math.pi / 3.2
    parts.append(
        '<path d="M%s,%s L%s,%s A%s,%s 0 0,1 %s,%s Z" fill="url(#id-sweep)">'
        '<animateTransform attributeName="transform" type="rotate" from="0 %s %s" to="360 %s %s" dur="9.5s" repeatCount="indefinite"/></path>'
        % (
            num(rcx), num(rcy),
            num(rcx + math.cos(sweep_a1) * rrad), num(rcy + math.sin(sweep_a1) * rrad),
            num(rrad), num(rrad),
            num(rcx + math.cos(sweep_a2) * rrad), num(rcy + math.sin(sweep_a2) * rrad),
            num(rcx), num(rcy), num(rcx), num(rcy),
        )
    )
    data_pts = []
    for i, axis in enumerate(axes):
        ang = -math.pi / 2.0 + i * math.pi / 3.0
        ex = rcx + math.cos(ang) * rrad
        ey = rcy + math.sin(ang) * rrad
        parts.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="0.75"/>' % (num(rcx), num(rcy), num(ex), num(ey), STROKE_HAIR))
        val = lang_map.get(axis, 0)
        ratio = 0.14 + 0.86 * math.sqrt(val / float(top_size)) if val > 0 else 0.12
        dx = rcx + math.cos(ang) * rrad * ratio
        dy = rcy + math.sin(ang) * rrad * ratio
        data_pts.append((dx, dy, axis))

        lx = rcx + math.cos(ang) * (rrad + 25)
        ly = rcy + math.sin(ang) * (rrad + 21)
        anchor = "middle"
        if i in (1, 2):
            anchor = "start"
            lx += 4
        elif i in (4, 5):
            anchor = "end"
            lx -= 4
        elif i == 0:
            ly -= 2
        elif i == 3:
            ly += 8
        pct = pct_map.get(axis, 0)
        pct_str = "%d%%" % pct if pct > 0 else "<1%"
        col = LANG_COLORS.get(axis, CYAN)
        parts.append(
            raw_text(
                lx,
                ly,
                '<tspan fill="%s" font-weight="700">%s</tspan><tspan fill="%s"> %s</tspan>'
                % (col, short_axes[axis], INK_DIM, esc(pct_str)),
                INK_SUB,
                9.2,
                anchor,
                "600",
            )
        )

    poly_str = " ".join("%s,%s" % (num(dx), num(dy)) for dx, dy, _ in data_pts)
    parts.append('<polygon points="%s" fill="%s" fill-opacity="0.18" stroke="%s" stroke-width="1.8" filter="url(#id-glow)"/>' % (poly_str, PHOSPHOR, PHOSPHOR_HI))
    for dx, dy, axis in data_pts:
        parts.append('<circle cx="%s" cy="%s" r="3" fill="%s" stroke="%s" stroke-width="1"/>' % (num(dx), num(dy), PHOSPHOR_HI, BG_WELL))
    parts.append('<circle cx="%s" cy="%s" r="2.2" fill="%s"/>' % (num(rcx), num(rcy), CYAN))

    gx, gy, gw, gh = 964, 20, 216, 240
    parts.append('<rect x="%d" y="%d" width="%d" height="%d" rx="10" fill="%s" stroke="%s" stroke-width="1"/>' % (gx, gy, gw, gh, BG_WELL, STROKE_FRAME))
    parts.append(text(gx + 16, gy + 24, "CADENCE", INK_DIM, 8.8, "start", "600", ' letter-spacing="1.2"'))

    dcx, dcy, dr = gx + gw / 2.0, gy + 88.0, 38.0
    circum = 2.0 * math.pi * dr
    active_pct = telemetry["active_weeks_pct"]
    dash_on = circum * (active_pct / 100.0)
    for deg in range(0, 360, 12):
        rad = math.radians(deg)
        r0 = dr + 6.5
        r1 = dr + (10.5 if deg % 36 == 0 else 8.5)
        parts.append(
            '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s"/>'
            % (
                num(dcx + math.cos(rad) * r0),
                num(dcy + math.sin(rad) * r0),
                num(dcx + math.cos(rad) * r1),
                num(dcy + math.sin(rad) * r1),
                STROKE_SPECULAR if deg % 36 == 0 else STROKE_HAIR,
                "1.0" if deg % 36 == 0 else "0.7",
            )
        )
    parts.append('<circle cx="%s" cy="%s" r="%s" fill="none" stroke="%s" stroke-width="5.5"/>' % (num(dcx), num(dcy), num(dr), STROKE_HAIR))
    parts.append(
        '<circle cx="%s" cy="%s" r="%s" fill="none" stroke="url(#id-arc)" stroke-width="5.5" stroke-linecap="round" '
        'stroke-dasharray="%s %s" transform="rotate(-90 %s %s)" filter="url(#id-glow)"/>'
        % (num(dcx), num(dcy), num(dr), num(dash_on), num(circum), num(dcx), num(dcy))
    )
    parts.append(text(dcx, dcy + 6, "%d%%" % active_pct, INK, 19, "middle", "700"))
    parts.append(text(dcx, dcy + 19, "ACTIVE", INK_DIM, 7.2, "middle", "600", ' letter-spacing="1.1"'))

    parts.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="1"/>' % (gx + 14, gy + 148, gx + gw - 14, gy + 148, STROKE_HAIR))
    parts.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="1"/>' % (gx + 14, gy + 194, gx + gw - 14, gy + 194, STROKE_HAIR))
    parts.append('<line x1="%s" y1="%d" x2="%s" y2="%d" stroke="%s" stroke-width="1"/>' % (num(dcx), gy + 154, num(dcx), gy + 232, STROKE_HAIR))

    mini_stats = [
        (gx + 18, gy + 172, str(stars), "STARS", AMBER),
        (gx + 120, gy + 172, str(repos), "REPOS", CYAN),
        (gx + 18, gy + 218, compact(chars), "CHARS", PHOSPHOR_HI),
        (gx + 120, gy + 218, "%.2fG" % (disk / 1073741824.0), "DISK", INK),
    ]
    for sx, sy, sv, sl, sc in mini_stats:
        parts.append(text(sx, sy, sv, sc, 15.5, "start", "700"))
        parts.append(text(sx, sy + 13, sl, INK_DIM, 7.6, "start", "600", ' letter-spacing="1.1"'))

    lx, ly, lw, lh = 584, 272, 596, 176
    parts.append('<rect x="%d" y="%d" width="%d" height="%d" rx="10" fill="%s" stroke="%s" stroke-width="1"/>' % (lx, ly, lw, lh, BG_WELL, STROKE_FRAME))
    parts.append(text(lx + 16, ly + 24, "COMMIT STREAM", INK_DIM, 8.8, "start", "600", ' letter-spacing="1.2"'))
    parts.append('<circle cx="%d" cy="%d" r="3" fill="%s"/>' % (lx + lw - 62, ly + 20.5, PHOSPHOR))
    parts.append(text(lx + lw - 16, ly + 24, "LIVE", PHOSPHOR, 8.5, "end", "600", ' letter-spacing="1.1"'))
    parts.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="1"/>' % (lx + 16, ly + 34, lx + lw - 16, ly + 34, STROKE_HAIR))

    rows = events[:5] if events else [{"time": "--:--", "sha": "-------", "repo": USERNAME, "message": "awaiting push event"}]
    if len(rows) > 1:
        parts.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="1"/>' % (lx + 24, ly + 52, lx + 24, ly + 52 + (len(rows) - 1) * 26, STROKE_FRAME))
    for i, ev in enumerate(rows):
        row_y = ly + 56 + i * 26
        node_y = row_y - 3.5
        if i == 0:
            parts.append('<circle cx="%d" cy="%s" r="3.2" fill="%s" filter="url(#id-glow)"/>' % (lx + 24, num(node_y), PHOSPHOR_HI))
            parts.append(
                '<circle cx="%d" cy="%s" r="3.2" fill="none" stroke="%s" stroke-width="0.9">'
                '<animate attributeName="r" values="3.2;8.5" dur="2.8s" repeatCount="indefinite"/>'
                '<animate attributeName="opacity" values="0.8;0" dur="2.8s" repeatCount="indefinite"/></circle>'
                % (lx + 24, num(node_y), PHOSPHOR_HI)
            )
        else:
            parts.append('<circle cx="%d" cy="%s" r="2.2" fill="%s"/>' % (lx + 24, num(node_y), STROKE_SPECULAR))
        repo_short = ev["repo"][:15]
        msg = truncate_clean(ev["message"], 38)
        parts.append(text(lx + 40, row_y, ev["time"], INK_DIM, 9.6, "start", "500"))
        parts.append(text(lx + 84, row_y, ev["sha"], AMBER, 9.6, "start", "600"))
        parts.append(text(lx + 142, row_y, repo_short, CYAN, 9.6, "start", "600"))
        parts.append(text(lx + 266, row_y, msg, INK if i == 0 else INK_SUB, 9.6, "start", "500" if i == 0 else "400"))

    parts.append("</svg>")
    return "\n".join(parts)


def activity_matrix_svg(day_map, telemetry):
    width, height = 1200, 272
    clip_defs, frame_nodes = chassis_plate(width, height, "mat", PHOSPHOR, grid_opacity=0.4, radius=14)
    weeks52 = telemetry["weeks52"]
    max_w = max(weeks52) if any(weeks52) else 1

    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 272" width="1200" height="272" role="img" aria-label="52-Week Activity Matrix">',
        REDUCED_MOTION_STYLE,
        "<defs>",
    ]
    parts.extend(common_defs("mat"))
    parts.extend(clip_defs)
    parts.extend(
        [
            '<linearGradient id="mat-curve" x1="0" y1="0" x2="1" y2="0">',
            '<stop offset="0%%" stop-color="%s" stop-opacity="0.45"/>' % CYAN,
            '<stop offset="55%%" stop-color="%s"/>' % CYAN,
            '<stop offset="100%%" stop-color="%s"/>' % PHOSPHOR_HI,
            "</linearGradient>",
            '<linearGradient id="mat-fill" x1="0" y1="0" x2="0" y2="1">',
            '<stop offset="0%%" stop-color="%s" stop-opacity="0.24"/>' % PHOSPHOR,
            '<stop offset="100%%" stop-color="%s" stop-opacity="0"/>' % BG_WELL,
            "</linearGradient>",
            "</defs>",
        ]
    )
    parts.extend(frame_nodes)

    parts.append(text(28, 30, "ACTIVITY MATRIX  //  52 WEEKS", INK_SUB, 9.2, "start", "600", ' letter-spacing="1.4"'))
    parts.append(text(1056, 30, "0", INK_DIM, 8.5, "end", "600"))
    for li, lcol in enumerate(HEAT_LEVELS):
        lx = 1064 + li * 16
        parts.append('<rect x="%d" y="21" width="11" height="11" rx="2.5" fill="%s" stroke="%s" stroke-width="0.6"/>' % (lx, lcol, STROKE_FRAME if li == 0 else lcol))
    parts.append(text(1152, 30, "MAX", INK_DIM, 8.5, "start", "600"))

    mx, my, mw, mh = 20, 44, 1160, 208
    parts.append('<rect x="%d" y="%d" width="%d" height="%d" rx="10" fill="%s" stroke="%s" stroke-width="1"/>' % (mx, my, mw, mh, BG_WELL, STROKE_FRAME))

    today = datetime.date.today()
    days_since_sun = (today.weekday() + 1) % 7
    end_sunday = today - datetime.timedelta(days=days_since_sun)
    start_sunday = end_sunday - datetime.timedelta(weeks=51)

    grid_x = 64.0
    grid_y = 70.0
    pitch_x = 21.15
    pitch_y = 15.8
    cell_w = 16.2
    cell_h = 11.8

    month_names = ("JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC")
    last_month = -1
    last_printed_w = -9
    for w in range(52):
        d = start_sunday + datetime.timedelta(weeks=w)
        if d.month != last_month:
            last_month = d.month
            if w - last_printed_w >= 3:
                parts.append(text(grid_x + w * pitch_x, 62, month_names[d.month - 1], INK_DIM, 8.5, "start", "600", ' letter-spacing="0.8"'))
                last_printed_w = w

    for row, lbl in ((1, "MON"), (3, "WED"), (5, "FRI")):
        parts.append(text(54, grid_y + row * pitch_y + 9.2, lbl, INK_DIM, 8.2, "end", "600"))

    for w in range(52):
        for r in range(7):
            d = start_sunday + datetime.timedelta(weeks=w, days=r)
            if d > today:
                continue
            c = int(day_map.get(d.isoformat(), 0))
            if c == 0:
                lvl = 0
            elif c <= 3:
                lvl = 1
            elif c <= 9:
                lvl = 2
            elif c <= 20:
                lvl = 3
            else:
                lvl = 4
            cx = grid_x + w * pitch_x
            cy = grid_y + r * pitch_y
            fill = HEAT_LEVELS[lvl]
            stroke = PHOSPHOR_HI if lvl == 4 else (STROKE_HAIR if lvl == 0 else "none")
            sw = "0.9" if lvl == 4 else "0.6"
            parts.append(
                '<rect x="%s" y="%s" width="%s" height="%s" rx="2.6" fill="%s"%s/>'
                % (
                    num(cx), num(cy), num(cell_w), num(cell_h), fill,
                    (' stroke="%s" stroke-width="%s"' % (stroke, sw)) if stroke != "none" else "",
                )
            )
            if lvl >= 2:
                parts.append(
                    '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="#ffffff" stroke-width="0.7" stroke-opacity="%s"/>'
                    % (num(cx + 3), num(cy + 1.4), num(cx + cell_w - 3), num(cy + 1.4), "0.35" if lvl == 4 else "0.18")
                )

    spec_top = 194.0
    spec_bot = 240.0
    spec_h = spec_bot - spec_top
    parts.append('<line x1="64" y1="186" x2="1162" y2="186" stroke="%s" stroke-width="0.8"/>' % STROKE_HAIR)
    parts.append(text(54, 224, "VEL", INK_MICRO, 8, "end", "600", ' letter-spacing="0.8"'))

    curve_pts = []
    for w in range(52):
        val = weeks52[w]
        norm = (val / float(max_w)) ** 0.72 if val > 0 else 0.0
        bh = max(2.0, norm * spec_h)
        bx = grid_x + w * pitch_x
        bar_col = PHOSPHOR if norm > 0.45 else (CYAN_DEEP if norm > 0 else STROKE_HAIR)
        parts.append(
            '<rect x="%s" y="%s" width="6" height="%s" rx="1.8" fill="%s" fill-opacity="%s"/>'
            % (num(bx + 5), num(spec_bot - bh), num(bh), bar_col, "0.6" if val > 0 else "0.75")
        )
        curve_pts.append((bx + cell_w / 2.0, spec_bot - norm * (spec_h - 2.0)))

    vel_d = smooth_curve_path(curve_pts)
    vel_area = vel_d + " L%s,%s L%s,%s Z" % (num(curve_pts[-1][0]), num(spec_bot), num(curve_pts[0][0]), num(spec_bot))
    parts.append('<path d="%s" fill="url(#mat-fill)"/>' % vel_area)
    parts.append('<path d="%s" fill="none" stroke="url(#mat-curve)" stroke-width="1.6"/>' % vel_d)
    parts.append(
        '<circle r="2.8" fill="%s" filter="url(#mat-glow)">'
        '<animateMotion dur="7s" repeatCount="indefinite" path="%s"/></circle>'
        % (PHOSPHOR_HI, vel_d)
    )

    parts.append("</svg>")
    return "\n".join(parts)


def constellation_specs_svg(repo_map, langs):
    width, height = 1200, 256
    clip_defs, frame_nodes = chassis_plate(width, height, "sys", AMBER, grid_opacity=0.45, radius=14)

    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 256" width="1200" height="256" role="img" aria-label="Ecosystem Topology and Arch Stack">',
        REDUCED_MOTION_STYLE,
        "<defs>",
    ]
    parts.extend(common_defs("sys"))
    parts.extend(clip_defs)
    parts.append("</defs>")
    parts.extend(frame_nodes)

    lx, ly, lw, lh = 20, 20, 672, 216
    parts.append('<rect x="%d" y="%d" width="%d" height="%d" rx="10" fill="%s" stroke="%s" stroke-width="1"/>' % (lx, ly, lw, lh, BG_WELL, STROKE_FRAME))
    parts.append(text(lx + 16, ly + 23, "SYSTEM TOPOLOGY", INK_DIM, 8.8, "start", "600", ' letter-spacing="1.2"'))
    parts.append(text(lx + lw - 16, ly + 23, "%d REPOS" % max(len(repo_map), 10), PHOSPHOR, 8.5, "end", "600", ' letter-spacing="1.0"'))

    cx, cy = lx + lw / 2.0, ly + 124.0
    clusters = [
        (lx + 18, ly + 42, 224, 68, PHOSPHOR, "01 // FORUMS", "f_forumv3 · f-forum · v2", "M356,144 C292,144 282,96 262,96", "4.4s"),
        (lx + 430, ly + 42, 224, 68, AMBER, "02 // VAULT", "SOURCEOFKNOWLEDGFORAI", "M356,144 C420,144 430,96 450,96", "5.0s"),
        (lx + 18, ly + 130, 224, 68, CYAN, "03 // ENGINE", "Edunext_fe · legacy · shoptify", "M356,144 C292,144 282,184 262,184", "5.4s"),
        (lx + 430, ly + 130, 224, 68, CORAL, "04 // LABS", "Socratic · resourcepack", "M356,144 C420,144 430,184 450,184", "4.8s"),
    ]

    for _, _, _, _, col, _, _, path_d, dur in clusters:
        parts.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.4"/>' % (path_d, STROKE_FRAME))
        parts.append(
            '<path d="%s" fill="none" stroke="%s" stroke-width="1.3" stroke-dasharray="4 6" stroke-opacity="0.65">'
            '<animate attributeName="stroke-dashoffset" from="20" to="0" dur="2.1s" repeatCount="indefinite"/></path>'
            % (path_d, col)
        )
        parts.append('<circle r="2.6" fill="%s" filter="url(#sys-glow)"><animateMotion dur="%s" repeatCount="indefinite" path="%s"/></circle>' % (col, dur, path_d))

    parts.append('<circle cx="%s" cy="%s" r="44" fill="none" stroke="%s" stroke-width="0.9" stroke-dasharray="3 6" stroke-opacity="0.6">'
                 '<animateTransform attributeName="transform" type="rotate" from="0 %s %s" to="360 %s %s" dur="24s" repeatCount="indefinite"/></circle>'
                 % (num(cx), num(cy), CYAN, num(cx), num(cy), num(cx), num(cy)))
    parts.append('<circle cx="%s" cy="%s" r="35" fill="%s" stroke="%s" stroke-width="1.3"/>' % (num(cx), num(cy), BG_WELL_ALT, PHOSPHOR))
    parts.append(arch_mark(cx - 9, cy - 22, 18, CYAN))
    parts.append(text(cx, cy + 12, "CORE", INK, 10.5, "middle", "700", ' letter-spacing="1.4"'))
    parts.append(text(cx, cy + 24, "ARCH", PHOSPHOR, 7.6, "middle", "600", ' letter-spacing="1.0"'))

    for bx, by, bw, bh, col, code, repos_line, _, _ in clusters:
        parts.append('<rect x="%d" y="%d" width="%d" height="%d" rx="8" fill="%s" stroke="%s" stroke-width="1"/>' % (bx, by, bw, bh, BG_WELL_ALT, STROKE_FRAME))
        parts.append('<rect x="%d" y="%d" width="3" height="%d" rx="1.5" fill="%s"/>' % (bx + 1, by + 12, bh - 24, col))
        parts.append(text(bx + 16, by + 26, code, col, 9.2, "start", "700", ' letter-spacing="1.0"'))
        parts.append(text(bx + 16, by + 48, repos_line, INK_SUB, 9.6, "start", "500"))

    rx, ry, rw, rh = 708, 20, 472, 216
    parts.append('<rect x="%d" y="%d" width="%d" height="%d" rx="10" fill="%s" stroke="%s" stroke-width="1"/>' % (rx, ry, rw, rh, BG_WELL, STROKE_FRAME))
    parts.append(text(rx + 18, ry + 23, "STACK SPECTRUM  //  RUNTIME", INK_DIM, 8.8, "start", "600", ' letter-spacing="1.2"'))

    top6 = langs[:6]
    total_b = sum(sz for _, sz in top6) or 1
    pcts = lang_percentages(top6)
    bar_x = rx + 18.0
    bar_y = ry + 42.0
    bar_w = rw - 36.0
    gap = 3.0
    usable_w = bar_w - gap * max(len(top6) - 1, 0)
    cur_x = bar_x
    for idx, (lname, lsize) in enumerate(top6):
        seg_w = max(8.0, usable_w * (lsize / float(total_b)))
        if idx == len(top6) - 1:
            seg_w = max(6.0, (bar_x + bar_w) - cur_x)
        col = LANG_COLORS.get(lname, SLATE)
        parts.append('<rect x="%s" y="%s" width="%s" height="11" rx="2.5" fill="%s"/>' % (num(cur_x), num(bar_y), num(seg_w), col))
        parts.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="#ffffff" stroke-width="0.8" stroke-opacity="0.28"/>' % (num(cur_x + 2), num(bar_y + 1.5), num(cur_x + seg_w - 2), num(bar_y + 1.5)))
        cur_x += seg_w + gap

    for idx, (lname, _) in enumerate(top6):
        c_col = idx % 3
        c_row = idx // 3
        ix = rx + 18 + c_col * 150
        iy = ry + 75 + c_row * 19
        col = LANG_COLORS.get(lname, SLATE)
        pct_str = "%d%%" % pcts[idx] if pcts[idx] > 0 else "<1%"
        parts.append('<circle cx="%d" cy="%d" r="3.2" fill="%s"/>' % (ix + 3, iy - 3.5, col))
        parts.append(text(ix + 12, iy, lname, INK, 9.6, "start", "600"))
        parts.append(text(ix + 126, iy, pct_str, INK_DIM, 9.4, "end", "600"))

    parts.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="1"/>' % (rx + 18, ry + 114, rx + rw - 18, ry + 114, STROKE_HAIR))
    specs = [
        ("OS", "Arch 6.12 LTS"),
        ("WM", "Hyprland"),
        ("SHELL", "zsh 5.9 / tmux"),
        ("EDITOR", "neovim 0.10"),
        ("TERM", "kitty / mono"),
        ("DISPLAY", "Wayland"),
    ]
    for idx, (k, v) in enumerate(specs):
        col = idx % 2
        row = idx // 2
        sx = rx + 18 + col * 224
        sy = ry + 140 + row * 28
        parts.append(text(sx, sy, k, INK_DIM, 8.6, "start", "600", ' letter-spacing="1.1"'))
        parts.append(text(sx + 66, sy, v, INK, 10.2, "start", "600"))

    parts.append("</svg>")
    return "\n".join(parts)


def write(name, content):
    path = os.path.join(ASSETS, name)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(content)
    print("wrote %s (%d bytes)" % (name, len(content.encode("utf-8"))))


def load_portrait():
    path = os.path.join(ASSETS, "portrait.txt")
    if not os.path.exists(path):
        return ["broamstuck", "arch linux"]
    with open(path, "r", encoding="utf-8") as handle:
        lines = [line.rstrip() for line in handle.read().split("\n")]
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return lines or ["broamstuck"]


def main():
    os.makedirs(ASSETS, exist_ok=True)
    data = collect()
    if not data["days"] and not data["total"] and not data["repos"]:
        raise SystemExit("error: GitHub API returned no profile data, assets left untouched")
    telemetry = compute_telemetry(data["days"], data["weeks"])

    write("01-monolith-hero.svg", monolith_hero_svg(data["total"], data["commits"], telemetry))
    write(
        "02-identity-telemetry.svg",
        identity_telemetry_svg(
            load_portrait(),
            data["langs"],
            data["stars"],
            data["repos"],
            data["bytes"],
            data["disk"],
            data["events"],
            telemetry,
        ),
    )
    write("03-activity-matrix.svg", activity_matrix_svg(data["days"], telemetry))
    for card_name, card_svg in render_flagship_cards(data["repo_map"]).items():
        write(card_name, card_svg)
    write("04-constellation-specs.svg", constellation_specs_svg(data["repo_map"], data["langs"]))

    print(
        "synced %s: %d contributions, %d commits, %d stars, %d repos, longest=%dd, current=%dd, peak=%d"
        % (
            USERNAME,
            data["total"],
            data["commits"],
            data["stars"],
            data["repos"],
            telemetry["longest"],
            telemetry["current"],
            telemetry["peak"],
        )
    )


if __name__ == "__main__":
    main()
