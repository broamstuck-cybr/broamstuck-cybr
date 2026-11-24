import datetime
import json
import math
import os
import urllib.request

FONT = "'JetBrains Mono', 'Fira Code', ui-monospace, monospace"
SANS = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
USERNAME = os.environ.get("GH_PROFILE_USERNAME", "broamstuck-cybr")
HANDLE = os.environ.get("GH_PROFILE_HANDLE", "broamstuck")
DISPLAY = os.environ.get("GH_PROFILE_DISPLAY", "Bro Am Stuck")
TOKEN = os.environ.get("GITHUB_TOKEN", "") or os.environ.get("GH_TOKEN", "")
API = (os.environ.get("GITHUB_API_URL", "") or "https://api.github.com").rstrip("/")
GQL = (os.environ.get("GITHUB_GRAPHQL_URL", "") or "https://api.github.com/graphql").rstrip("/")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")

BG = "#080c14"
BG_DEEP = "#05080f"
CARD = "#0f1523"
CARD_ALT = "#131b2c"
BORDER = "#1e293b"
BORDER_HI = "#2c3d57"
ARCH = "#1793d1"
ARCH_SOFT = "#38bdf8"
TERM = "#39d353"
TERM_MID = "#26a641"
AMBER = "#e3b341"
TEXT = "#f1f5f9"
MUTED = "#8b949e"
DIM = "#64748b"
LEVELS = ["#161e2e", "#0e4429", "#006d32", "#26a641", "#39d353"]

ARCH_PATH = (
    "M11.39.605C10.376 3.092 9.764 4.72 8.635 7.132c.693.734 1.543 1.589 2.923 2.554"
    "-1.484-.61-2.496-1.224-3.252-1.86C6.86 10.842 4.596 15.138 0 23.395"
    "c3.612-2.085 6.412-3.37 9.021-3.862a6.61 6.61 0 01-.171-1.547l.003-.115"
    "c.058-2.315 1.261-4.095 2.687-3.973 1.426.12 2.534 2.096 2.478 4.409"
    "a6.52 6.52 0 01-.146 1.243c2.58.505 5.352 1.787 8.914 3.844"
    "-.702-1.293-1.33-2.459-1.929-3.57-.943-.73-1.926-1.682-3.933-2.713"
    "1.38.359 2.367.772 3.137 1.234-6.09-11.334-6.582-12.84-8.67-17.74z"
    "M22.898 21.36v-.623h-.234v-.084h.562v.084h-.234v.623h.331v-.707h.142"
    "l.167.5.034.107a2.26 2.26 0 01.038-.114l.17-.493H24v.707h-.091v-.593"
    "l-.206.593h-.084l-.205-.602v.602h-.091"
)

LANG_COLORS = {
    "TypeScript": "#3178c6",
    "JavaScript": "#e3b341",
    "HTML": "#f97316",
    "CSS": "#38bdf8",
    "Python": "#39d353",
    "Shell": "#94a3b8",
}

REDUCED_MOTION_STYLE = (
    "<style>"
    "@media (prefers-reduced-motion: reduce) { "
    "animate, animateTransform, animateMotion { display: none; } "
    "}"
    "</style>"
)


def num(value, places=2):
    val = ("%." + str(places) + "f") % float(value)
    if "." in val:
        val = val.rstrip("0").rstrip(".")
    return "0" if val in ("", "-0") else val


def esc(value):
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def text(x, y, body, fill=TEXT, size=11, anchor="start", weight="400", extra="", family=FONT):
    return (
        '<text x="%s" y="%s" font-family="%s" font-size="%s" font-weight="%s" '
        'fill="%s" text-anchor="%s"%s>%s</text>'
        % (num(x), num(y), family, num(size), weight, fill, anchor, extra, esc(body))
    )


def raw_text(x, y, inner, fill=TEXT, size=11, anchor="start", weight="400", extra="", family=FONT):
    return (
        '<text x="%s" y="%s" font-family="%s" font-size="%s" font-weight="%s" '
        'fill="%s" text-anchor="%s"%s>%s</text>'
        % (num(x), num(y), family, num(size), weight, fill, anchor, extra, inner)
    )


def arch_mark(x, y, size, fill=ARCH):
    return '<g transform="translate(%s %s) scale(%s)"><path d="%s" fill="%s"/></g>' % (
        num(x),
        num(y),
        num(size / 24.0, 4),
        ARCH_PATH,
        fill,
    )


def pill_width(label, size=8.5):
    return len(label) * size * 0.64 + 20


def pill(x, y, label, height=18, fill=CARD, stroke=BORDER, color=MUTED, size=8.5):
    width = pill_width(label, size)
    return (
        '<rect x="%s" y="%s" width="%s" height="%s" rx="%s" fill="%s" stroke="%s" stroke-width="1"/>'
        % (num(x), num(y), num(width), num(height), num(height / 2.0), fill, stroke)
        + text(
            x + width / 2.0,
            y + height / 2.0 + size * 0.36,
            label,
            color,
            size,
            "middle",
            "500",
            ' letter-spacing="0.3"',
        )
    )


def wrap_two_lines(body, max_chars=44):
    words = body.split()
    line1, line2 = [], []
    cur = 0
    for w in words:
        need = len(w) + (1 if line1 else 0)
        if not line2 and cur + need <= max_chars:
            line1.append(w)
            cur += need
        else:
            line2.append(w)
    return " ".join(line1), " ".join(line2)


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


def compute_calendar_telemetry(day_map, weeks):
    if not day_map:
        return {"longest": 0, "current": 0, "peak": 0, "peak_date": "--", "active_weeks_pct": 0, "spark": []}
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
    # Current streak ending today or yesterday
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
    return {
        "longest": longest,
        "current": current,
        "peak": peak,
        "peak_date": peak_date[5:] if len(peak_date) >= 10 else peak_date,
        "active_weeks_pct": active_weeks_pct,
        "spark": weeks[-12:] if weeks else [],
    }


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


def hero_banner_svg(total_contribs, stars, repos, telemetry):
    width, height = 880, 232
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 232" width="880" height="232" role="img" aria-label="BroAmStuck Arch Hyprland Engineering Banner">',
        "<defs>",
        '<linearGradient id="hb-bg" x1="0" y1="0" x2="1" y2="1">',
        '<stop offset="0%" stop-color="#070b14"/>',
        '<stop offset="55%" stop-color="#0c1322"/>',
        '<stop offset="100%" stop-color="#08141a"/>',
        "</linearGradient>",
        '<radialGradient id="hb-glow-em" cx="78%" cy="46%" r="44%">',
        '<stop offset="0%" stop-color="#39d353" stop-opacity="0.16"/>',
        '<stop offset="60%" stop-color="#1793d1" stop-opacity="0.06"/>',
        '<stop offset="100%" stop-color="#070b14" stop-opacity="0"/>',
        "</radialGradient>",
        '<linearGradient id="hb-ridge" x1="0" y1="0" x2="1" y2="0">',
        '<stop offset="0%" stop-color="#1793d1" stop-opacity="0.05"/>',
        '<stop offset="45%" stop-color="#39d353" stop-opacity="0.45"/>',
        '<stop offset="78%" stop-color="#1793d1" stop-opacity="0.55"/>',
        '<stop offset="100%" stop-color="#e3b341" stop-opacity="0.22"/>',
        "</linearGradient>",
        '<pattern id="hb-dots" width="22" height="22" patternUnits="userSpaceOnUse">',
        '<circle cx="1.5" cy="1.5" r="1" fill="#1e293b" fill-opacity="0.65"/>',
        "</pattern>",
        '<clipPath id="hb-clip"><rect x="1" y="1" width="878" height="230" rx="14"/></clipPath>',
        "</defs>",
        REDUCED_MOTION_STYLE,
        '<rect x="0.5" y="0.5" width="879" height="231" rx="14" fill="url(#hb-bg)" stroke="%s" stroke-width="1"/>' % BORDER,
        '<g clip-path="url(#hb-clip)">',
        '<rect x="0" y="0" width="880" height="232" fill="url(#hb-dots)"/>',
        '<rect x="0" y="0" width="880" height="232" fill="url(#hb-glow-em)"/>',
        # Painterly topographic mountain contours (Arch elevation landscape)
        '<path d="M 0 184 C 140 162, 230 202, 390 176 C 530 154, 620 112, 735 126 C 805 134, 845 110, 880 102 L 880 232 L 0 232 Z" fill="#0d1626" fill-opacity="0.72"/>',
        '<path d="M 0 204 C 165 186, 300 214, 465 184 C 600 158, 700 132, 880 148 L 880 232 L 0 232 Z" fill="#09121e" fill-opacity="0.88"/>',
        '<path d="M 0 184 C 140 162, 230 202, 390 176 C 530 154, 620 112, 735 126 C 805 134, 845 110, 880 102" fill="none" stroke="url(#hb-ridge)" stroke-width="1.4"/>',
        '<path d="M 410 198 C 560 170, 675 144, 880 158" fill="none" stroke="#1e293b" stroke-width="1" stroke-dasharray="4 5"/>',
        # Right architectural Hyprland tiling window sculpture
        '<g transform="translate(546, 34)">',
        '<rect x="0" y="0" width="298" height="164" rx="10" fill="#0b111e" fill-opacity="0.88" stroke="#1e293b" stroke-width="1"/>',
        '<rect x="10" y="10" width="166" height="94" rx="7" fill="#0f172a" stroke="#39d353" stroke-width="1.4" stroke-opacity="0.85">'
        '<animate attributeName="stroke-opacity" values="0.55;0.98;0.55" dur="4.2s" repeatCount="indefinite"/></rect>',
        '<rect x="184" y="10" width="104" height="58" rx="7" fill="#0f172a" stroke="#1793d1" stroke-width="1"/>',
        '<rect x="184" y="76" width="104" height="78" rx="7" fill="#0f172a" stroke="#1e293b" stroke-width="1"/>',
        '<rect x="10" y="112" width="166" height="42" rx="7" fill="#0f172a" stroke="#1e293b" stroke-width="1"/>',
        # Inside active Hyprland pane: Arch geometric emblem + live lines
        arch_mark(22, 22, 16, ARCH),
        text(44, 34, "hyprland // active", TERM, 9.5, "start", "600"),
        '<line x1="22" y1="45" x2="162" y2="45" stroke="#1e293b" stroke-width="1"/>',
        text(22, 62, "sys   arch 6.12 LTS", MUTED, 8.8),
        text(22, 78, "ui    7,750+ vault", TEXT, 8.8),
        text(22, 94, "mode  ship sharp", ARCH_SOFT, 8.8),
        '<rect x="132" y="86" width="6" height="10" rx="1" fill="#39d353"><animate attributeName="opacity" values="1;0;1" dur="1.15s" repeatCount="indefinite"/></rect>',
        # Top-right mini pane: live streak & pulse
        text(196, 28, "STREAK", DIM, 7.5, "start", "600", ' letter-spacing="0.9"'),
        text(196, 51, "%dd" % telemetry["longest"], AMBER, 17, "start", "700"),
        text(244, 50, "best", MUTED, 8),
        # Bottom-right mini pane: minimalist orbital vector art
        '<circle cx="236" cy="115" r="24" fill="none" stroke="#1e293b" stroke-width="1"/>',
        '<circle cx="236" cy="115" r="14" fill="none" stroke="#1793d1" stroke-width="1" stroke-dasharray="3 3"/>',
        '<circle cx="236" cy="115" r="3.5" fill="#39d353"/>',
        '<g><circle cx="260" cy="115" r="2.6" fill="#e3b341"/>'
        '<animateTransform attributeName="transform" type="rotate" from="0 236 115" to="360 236 115" dur="9s" repeatCount="indefinite"/></g>',
        # Bottom-left mini pane: 3-pillar tags
        text(22, 130, "WEB CRAFT  ·  REVERSING", MUTED, 8, "start", "600", ' letter-spacing="0.6"'),
        text(22, 144, "OPEN KNOWLEDGE VAULT", TERM, 8, "start", "600", ' letter-spacing="0.6"'),
        "</g>",
        # Subtle moving light pulse along the top hairline
        '<rect x="-120" y="0.5" width="120" height="1.5" fill="url(#hb-ridge)">'
        '<animate attributeName="x" from="-120" to="920" dur="7s" repeatCount="indefinite"/></rect>',
        "</g>",
        # Left Editorial Typographic Lockup
        '<g transform="translate(34, 34)">',
        '<rect x="0" y="0" width="234" height="24" rx="12" fill="#0f172a" stroke="#1e293b" stroke-width="1"/>',
        '<circle cx="13" cy="12" r="3.5" fill="#39d353"><animate attributeName="opacity" values="1;0.35;1" dur="2.4s" repeatCount="indefinite"/></circle>',
        text(24, 15.5, "ARCH / HYPRLAND · SYSTEMS UI", AMBER, 8.8, "start", "600", ' letter-spacing="0.9"'),
        text(0, 68, "BroAmStuck", TEXT, 34, "start", "700", ' letter-spacing="-0.03em"', SANS),
        raw_text(
            0,
            96,
            '<tspan fill="%s">broamstuck-cybr</tspan><tspan fill="%s">  /  </tspan>'
            '<tspan fill="%s">Systems UI · Reversing · Open Vault</tspan>'
            % (ARCH_SOFT, DIM, MUTED),
            MUTED,
            12,
            "start",
            "500",
            "",
            SANS,
        ),
        text(
            0,
            124,
            "Build quiet. Ship sharp. Curate real code, never slop.",
            TEXT,
            11.5,
            "start",
            "400",
            ' fill-opacity="0.88"',
        ),
        # Live KPI chips row (dynamically spaced)
        '<g transform="translate(0, 144)">',
        pill(0, 0, "%d contribs (1y)" % total_contribs, 24, "#0d1a16", "#1f4d35", TERM, 9),
        pill(
            pill_width("%d contribs (1y)" % total_contribs, 9) + 10,
            0,
            "%d stars" % stars,
            24,
            "#1c180e",
            "#4d3c16",
            AMBER,
            9,
        ),
        pill(
            pill_width("%d contribs (1y)" % total_contribs, 9) + 10 + pill_width("%d stars" % stars, 9) + 10,
            0,
            "%d public repos" % repos,
            24,
            "#0e1a26",
            "#1d4261",
            ARCH_SOFT,
            9,
        ),
        "</g>",
        "</g>",
        "</svg>",
    ]
    return "\n".join(parts)


def header_svg(command):
    label = "%s@arch ~ $ %s" % (HANDLE, command)
    size = 12.5
    icon = 14
    gap = 9
    pad = 18
    height = 32
    width = pad * 2 + icon + gap + len(label) * size * 0.61
    x = (880 - width) / 2.0
    y = (42 - height) / 2.0
    inner = (
        '<tspan fill="%s">%s</tspan><tspan fill="%s">@arch</tspan>'
        '<tspan fill="%s"> ~ $ </tspan><tspan fill="%s">%s</tspan>'
    ) % (TERM, esc(HANDLE), ARCH, MUTED, TEXT, esc(command))
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 42" width="880" height="42" role="img">',
        '<line x1="16" y1="21" x2="%s" y2="21" stroke="%s" stroke-width="1" stroke-dasharray="2 5"/>' % (num(x - 14), BORDER),
        '<line x1="%s" y1="21" x2="864" y2="21" stroke="%s" stroke-width="1" stroke-dasharray="2 5"/>' % (num(x + width + 14), BORDER),
        '<rect x="%s" y="%s" width="%s" height="%s" rx="%s" fill="%s" stroke="%s" stroke-width="1"/>'
        % (num(x), num(y), num(width), num(height), num(height / 2.0), CARD, BORDER_HI),
        arch_mark(x + pad, y + (height - icon) / 2.0, icon),
        raw_text(x + pad + icon + gap, y + height / 2.0 + 4.3, inner, TEXT, size),
        "</svg>",
    ]
    return "\n".join(parts)


def contributions_svg(day_map, total, telemetry):
    width, height = 880, 214
    cell = 11.5
    gap = 3.2
    pitch = cell + gap
    grid_x = 68
    grid_y = 34
    month_y = 22
    today = datetime.date.today()
    start = today - datetime.timedelta(days=(today.weekday() + 1) % 7) - datetime.timedelta(weeks=51)
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 214" width="880" height="214" role="img">',
        "<defs>",
        '<linearGradient id="spark-fill" x1="0" y1="0" x2="0" y2="1">',
        '<stop offset="0%" stop-color="#39d353" stop-opacity="0.34"/>',
        '<stop offset="100%" stop-color="#39d353" stop-opacity="0"/>',
        "</linearGradient>",
        "</defs>",
        REDUCED_MOTION_STYLE,
        '<rect x="0.5" y="0.5" width="879" height="213" rx="12" fill="%s" stroke="%s" stroke-width="1"/>' % (CARD, BORDER),
    ]
    previous_month = None
    previous_label = -4
    for column in range(52):
        column_day = start + datetime.timedelta(days=column * 7)
        month = column_day.strftime("%b")
        if month != previous_month and column - previous_label >= 3:
            parts.append(text(grid_x + column * pitch, month_y, month, MUTED, 9.5))
            previous_label = column
        previous_month = month
    for row, label in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        parts.append(text(grid_x - 10, grid_y + row * pitch + cell / 2.0 + 3.4, label, MUTED, 9, "end"))
    for column in range(52):
        for row in range(7):
            day = start + datetime.timedelta(days=column * 7 + row)
            count = day_map.get(day.isoformat(), 0)
            if count <= 0:
                level = 0
            elif count <= 2:
                level = 1
            elif count <= 5:
                level = 2
            elif count <= 9:
                level = 3
            else:
                level = 4
            cx = grid_x + column * pitch
            cy = grid_y + row * pitch
            if level == 4:
                parts.append(
                    '<rect x="%s" y="%s" width="%s" height="%s" rx="3" fill="%s" stroke="#7ee787" stroke-opacity="0.45" stroke-width="0.6"/>'
                    % (num(cx), num(cy), num(cell), num(cell), LEVELS[level])
                )
            else:
                parts.append(
                    '<rect x="%s" y="%s" width="%s" height="%s" rx="3" fill="%s"/>'
                    % (num(cx), num(cy), num(cell), num(cell), LEVELS[level])
                )
    # Divider + Live Telemetry Strip
    parts.append('<line x1="20" y1="150" x2="860" y2="150" stroke="%s" stroke-width="1" stroke-dasharray="3 4"/>' % BORDER)
    kpis = [
        (26, str(total), "contributions (1y)", TERM),
        (210, "%dd" % telemetry["longest"], "longest streak", AMBER),
        (356, "%dd" % telemetry["current"], "current streak", ARCH_SOFT),
        (500, "%d (%s)" % (telemetry["peak"], telemetry["peak_date"]), "peak day", TEXT),
    ]
    for x, val, lbl, col in kpis:
        parts.append(text(x, 179, val, col, 16, "start", "700"))
        parts.append(text(x, 196, lbl, MUTED, 8.8))

    # 12-week velocity sparkline on the right
    spark = telemetry.get("spark") or []
    if spark:
        sx0, sy0, sw, sh = 694.0, 162.0, 158.0, 32.0
        mx = max(spark) or 1
        pts = []
        step = sw / float(max(len(spark) - 1, 1))
        for idx, v in enumerate(spark):
            px = sx0 + idx * step
            py = sy0 + sh - (v / float(mx)) * sh
            pts.append((px, py))
        line_str = " ".join("%s,%s" % (num(px), num(py)) for px, py in pts)
        area_str = "%s,%s %s %s,%s" % (num(sx0), num(sy0 + sh), line_str, num(sx0 + sw), num(sy0 + sh))
        parts.append('<polygon points="%s" fill="url(#spark-fill)"/>' % area_str)
        parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>' % (line_str, TERM))
        lx, ly = pts[-1]
        parts.append('<circle cx="%s" cy="%s" r="3" fill="%s"><animate attributeName="r" values="2.5;4;2.5" dur="2.2s" repeatCount="indefinite"/></circle>' % (num(lx), num(ly), TERM))
        parts.append(text(852, 206, "12w velocity", DIM, 8, "end"))

    parts.append("</svg>")
    return "\n".join(parts)


def window_frame(width, height, script, badge):
    parts = [
        '<rect x="0.5" y="0.5" width="%s" height="%s" rx="12" fill="%s" stroke="%s" stroke-width="1"/>'
        % (num(width - 1), num(height - 1), BG, BORDER),
        '<path d="M13 1 H%s A12 12 0 0 1 %s 13 V34 H1 V13 A12 12 0 0 1 13 1 Z" fill="%s"/>'
        % (num(width - 13), num(width - 1), CARD),
        '<line x1="1" y1="34" x2="%s" y2="34" stroke="%s" stroke-width="1"/>' % (num(width - 1), BORDER),
        arch_mark(14, 10, 14),
        text(34, 22, script, MUTED, 10.5),
    ]
    badge_width = len(badge) * 8 * 0.61 + 18
    parts.append(pill(width - 12 - badge_width, 8.5, badge, 17, CARD_ALT, BORDER_HI, ARCH_SOFT, 8))
    return parts


RAMP = " .:-=+*#%@"
DEPTH = (1.0, 0.58, 0.58, 0.7, 0.7, 0.82, 0.82, 0.93, 0.93, 1.0)


def depth_runs(line):
    runs = []
    buffer = []
    current = None
    for char in line:
        index = RAMP.find(char)
        level = DEPTH[index] if index >= 0 else 1.0
        if current is not None and level != current:
            runs.append((current, "".join(buffer)))
            buffer = []
        current = level
        buffer.append(char)
    if buffer:
        runs.append((current, "".join(buffer)))
    return runs


def portrait_svg(lines):
    width, height = 490, 536
    body_top = 34
    status_line = 504
    body_height = status_line - body_top
    max_len = max([len(line) for line in lines] or [1])
    size = min(
        (width - 42) / (max_len * 0.6),
        (body_height - 28) / (max(len(lines), 1) * 1.16),
        15.0,
    )
    size = max(size, 3.0)
    block_height = len(lines) * size * 1.16
    first = body_top + (body_height - block_height) / 2.0 + size * 0.92
    x0 = (width - max_len * size * 0.6) / 2.0
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 490 536" width="490" height="536" role="img">',
        "<defs>",
        '<linearGradient id="ascii" x1="0" y1="0" x2="0" y2="1">',
        '<stop offset="0" stop-color="%s"/>' % TERM,
        '<stop offset="0.58" stop-color="#26a641"/>',
        '<stop offset="1" stop-color="%s"/>' % ARCH,
        "</linearGradient>",
        '<linearGradient id="scanbeam" x1="0" y1="0" x2="0" y2="1">',
        '<stop offset="0%" stop-color="#39d353" stop-opacity="0"/>',
        '<stop offset="50%" stop-color="#39d353" stop-opacity="0.11"/>',
        '<stop offset="100%" stop-color="#39d353" stop-opacity="0"/>',
        "</linearGradient>",
        '<filter id="bloom" x="-15%" y="-15%" width="130%" height="130%"><feGaussianBlur stdDeviation="1.9"/></filter>',
        '<clipPath id="p-body"><rect x="2" y="35" width="486" height="468"/></clipPath>',
        "</defs>",
        REDUCED_MOTION_STYLE,
    ]
    parts.extend(window_frame(width, height, "./portrait.sh", "hyprland"))
    # Subtle corner HUD registration brackets
    parts.append('<path d="M18 56 V44 H30 M472 56 V44 H460 M18 482 V494 H30 M472 482 V494 H460" fill="none" stroke="#1e293b" stroke-width="1.2"/>')
    art = []
    for index, line in enumerate(lines):
        spans = "".join(
            '<tspan fill-opacity="%s">%s</tspan>' % (num(level), esc(chunk))
            for level, chunk in depth_runs(line)
        )
        art.append(
            raw_text(
                x0,
                first + index * size * 1.16,
                spans,
                "url(#ascii)",
                size,
                "start",
                "500",
                ' xml:space="preserve"',
            )
        )
    parts.append('<g clip-path="url(#p-body)">')
    parts.append('<g filter="url(#bloom)" opacity="0.34">%s</g>' % "".join(art))
    parts.extend(art)
    # Subtle phosphor scanline sweep
    parts.append(
        '<rect x="2" y="-60" width="486" height="60" fill="url(#scanbeam)">'
        '<animateTransform attributeName="transform" type="translate" from="0 0" to="0 570" dur="6.5s" repeatCount="indefinite"/></rect>'
    )
    parts.append("</g>")
    parts.append('<line x1="1" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="1"/>' % (num(status_line), num(width - 1), num(status_line), BORDER))
    parts.append(
        raw_text(
            14,
            status_line + 20,
            '<tspan fill="%s">%s@arch:~$ </tspan><tspan fill="%s" font-weight="700">%s</tspan>'
            % (MUTED, esc(HANDLE), TERM, esc(DISPLAY)),
            MUTED,
            11,
        )
    )
    parts.append(
        '<rect x="228" y="%s" width="6.5" height="11" rx="1" fill="%s">'
        '<animate attributeName="opacity" values="1;0;1" dur="1.1s" repeatCount="indefinite"/></rect>'
        % (num(status_line + 11), TERM)
    )
    parts.append(text(474, status_line + 20, "PTY 01 · LIVE", DIM, 8.5, "end"))
    parts.append("</svg>")
    return "\n".join(parts)


def star_path(cx, cy, outer=6.4, inner=2.7):
    points = []
    for step in range(10):
        angle = math.radians(-90 + step * 36)
        radius = outer if step % 2 == 0 else inner
        points.append("%s,%s" % (num(cx + radius * math.cos(angle)), num(cy + radius * math.sin(angle))))
    return "M" + " L".join(points) + " Z"


def diamond_path(cx, cy, radius=6.2):
    return "M%s %s L%s %s L%s %s L%s %s Z" % (
        num(cx),
        num(cy - radius),
        num(cx + radius),
        num(cy),
        num(cx),
        num(cy + radius),
        num(cx - radius),
        num(cy),
    )


def radar_svg(langs, cx, cy, radius, top):
    parts = []
    for ring in (0.35, 0.68, 1.0):
        points = []
        for axis in range(6):
            angle = math.radians(-90 + axis * 60)
            points.append("%s,%s" % (num(cx + radius * ring * math.cos(angle)), num(cy + radius * ring * math.sin(angle))))
        parts.append('<polygon points="%s" fill="none" stroke="%s" stroke-width="1"/>' % (" ".join(points), BORDER))
    for axis in range(6):
        angle = math.radians(-90 + axis * 60)
        parts.append(
            '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="1"/>'
            % (num(cx), num(cy), num(cx + radius * math.cos(angle)), num(cy + radius * math.sin(angle)), BORDER)
        )
    # Animated radar sweep wedge
    parts.append(
        '<g opacity="0.22">'
        '<path d="M%s %s L%s %s A%s %s 0 0 1 %s %s Z" fill="%s"/>'
        '<animateTransform attributeName="transform" type="rotate" from="0 %s %s" to="360 %s %s" dur="8s" repeatCount="indefinite"/>'
        "</g>"
        % (
            num(cx),
            num(cy),
            num(cx),
            num(cy - radius),
            num(radius),
            num(radius),
            num(cx + radius * math.sin(math.radians(38))),
            num(cy - radius * math.cos(math.radians(38))),
            TERM,
            num(cx),
            num(cy),
            num(cx),
            num(cy),
        )
    )
    plotted = []
    for axis in range(6):
        angle = math.radians(-90 + axis * 60)
        if axis < len(langs):
            ratio = max(math.sqrt(langs[axis][1]) / math.sqrt(top if top else 1), 0.18)
        else:
            ratio = 0.0
        plotted.append(
            (
                cx + radius * ratio * math.cos(angle),
                cy + radius * ratio * math.sin(angle),
                langs[axis][0] if axis < len(langs) else "",
                math.cos(angle),
                math.sin(angle),
            )
        )
    polygon = " ".join("%s,%s" % (num(p[0]), num(p[1])) for p in plotted)
    parts.append('<polygon points="%s" fill="rgba(57, 211, 83, 0.24)" stroke="%s" stroke-width="1.6" stroke-linejoin="round"/>' % (polygon, TERM))
    for px, py, name, cos_value, sin_value in plotted:
        parts.append('<circle cx="%s" cy="%s" r="2.6" fill="%s"/>' % (num(px), num(py), TERM))
        if not name:
            continue
        lx = cx + (radius + 16) * cos_value
        ly = cy + (radius + 16) * sin_value
        anchor = "start" if cos_value > 0.25 else ("end" if cos_value < -0.25 else "middle")
        ly += 3.2 if sin_value > 0 else (-1.2 if sin_value < 0 else 3.2)
        parts.append(text(lx, ly, name, ARCH_SOFT, 8.6, anchor, "600"))
    return parts


def dashboard_svg(langs, stars, repos, commits, events, telemetry):
    width, height = 490, 536
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 490 536" width="490" height="536" role="img">',
        REDUCED_MOTION_STYLE,
    ]
    parts.extend(window_frame(width, height, "./dashboard.sh", "arch-linux"))

    # Top-left: Radar card
    parts.append('<rect x="10.5" y="44.5" width="281" height="258" rx="9" fill="%s" stroke="%s" stroke-width="1"/>' % (CARD, BORDER))
    parts.append(raw_text(22, 64, '<tspan fill="%s">$ </tspan><tspan fill="%s" font-weight="600">lang-radar</tspan>' % (MUTED, TEXT), TEXT, 10))
    top = langs[0][1] if langs else 0
    parts.extend(radar_svg(langs[:6], 151, 188, 86, top))

    # Top-right: Telemetry counters card (4 real metrics)
    parts.append('<rect x="302.5" y="44.5" width="177" height="258" rx="9" fill="%s" stroke="%s" stroke-width="1"/>' % (CARD, BORDER))
    parts.append(raw_text(314, 64, '<tspan fill="%s">$ </tspan><tspan fill="%s" font-weight="600">telemetry</tspan>' % (MUTED, TEXT), TEXT, 10))
    metrics = [
        (98, str(stars), "total stars", AMBER, "star"),
        (149, str(repos), "public repos", ARCH_SOFT, "diamond"),
        (200, str(commits), "commits (1y)", TERM, "chevron"),
        (251, "%d%%" % telemetry["active_weeks_pct"], "active weeks", "#a78bfa", "pulse"),
    ]
    for baseline, value, label, color, icon in metrics:
        if icon == "star":
            parts.append('<path d="%s" fill="%s"/>' % (star_path(322, baseline - 5), color))
        elif icon == "diamond":
            parts.append('<path d="%s" fill="%s" fill-opacity="0.9"/>' % (diamond_path(322, baseline - 5), color))
        elif icon == "pulse":
            parts.append(
                '<polyline points="%s,%s %s,%s %s,%s %s,%s %s,%s" fill="none" stroke="%s" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'
                % (314, baseline - 5, 318, baseline - 5, 321, baseline - 11, 324, baseline + 1, 329, baseline - 5, color)
            )
        else:
            parts.append(
                '<polyline points="%s,%s %s,%s %s,%s" fill="none" stroke="%s" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
                % (317, baseline - 11, 326, baseline - 5, 317, baseline + 1, color)
            )
        parts.append(text(340, baseline, value, TEXT, 19, "start", "700"))
        parts.append(text(314, baseline + 14, label, MUTED, 8.5))

    # Bottom: live git tail log
    parts.append('<rect x="10.5" y="312.5" width="469" height="213" rx="9" fill="%s" stroke="%s" stroke-width="1"/>' % (CARD, BORDER))
    parts.append(
        raw_text(
            22,
            332,
            '<tspan fill="%s">$ </tspan><tspan fill="%s" font-weight="600">tail -n 5 /var/log/github-all.log</tspan>' % (MUTED, TEXT),
            TEXT,
            9.5,
        )
    )
    parts.append('<line x1="11" y1="344" x2="479" y2="344" stroke="%s" stroke-width="1" stroke-dasharray="3 4"/>' % BORDER)
    size = 9
    line_pitch = 29
    first = 367
    plain = ""
    for index in range(5):
        baseline = first + index * line_pitch
        if index < len(events):
            event = events[index]
            repo = event["repo"][:22]
            raw_msg = event["message"]
            message = (raw_msg[:30].rstrip() + "…") if len(raw_msg) > 31 else raw_msg
            inner = (
                '<tspan fill="%s">[%s] </tspan><tspan fill="%s">* </tspan>'
                '<tspan fill="%s">%s </tspan><tspan fill="%s">(%s) </tspan><tspan fill="%s">%s</tspan>'
                % (MUTED, esc(event["time"]), ARCH_SOFT, AMBER, esc(event["sha"]), ARCH_SOFT, esc(repo), TEXT, esc(message))
            )
            plain = "[%s] * %s (%s) %s" % (event["time"], event["sha"], repo, message)
        else:
            inner = '<tspan fill="%s">[--:--] * ------- (—) no recent push events</tspan>' % MUTED
            plain = "[--:--] * ------- (—) no recent push events"
        parts.append(raw_text(22, baseline, inner, TEXT, size, "start", "400", ' xml:space="preserve"'))
    cursor_x = min(464, 22 + len(plain) * size * 0.6 + 3)
    cursor_y = first + 4 * line_pitch - size * 0.82
    parts.append(
        '<text x="%s" y="%s" font-family="%s" font-size="%s" fill="%s">█'
        '<animate attributeName="opacity" values="1;0;1" dur="1.1s" repeatCount="indefinite"/></text>'
        % (num(cursor_x), num(cursor_y), FONT, num(size), TERM)
    )
    parts.append("</svg>")
    return "\n".join(parts)


def ecosystem_mindmap_svg(repo_map):
    width, height = 880, 312
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 312" width="880" height="312" role="img" aria-label="BroAmStuck Repository Ecosystem Mind Map">',
        "<defs>",
        '<radialGradient id="mm-core" cx="50%" cy="50%" r="50%">',
        '<stop offset="0%" stop-color="#39d353" stop-opacity="0.22"/>',
        '<stop offset="100%" stop-color="#080c14" stop-opacity="0"/>',
        "</radialGradient>",
        "</defs>",
        REDUCED_MOTION_STYLE,
    ]
    parts.extend(window_frame(width, height, "./ecosystem-map.sh", "mind-map"))

    cx, cy = 440, 174
    parts.append('<circle cx="%d" cy="%d" r="96" fill="url(#mm-core)"/>' % (cx, cy))

    clusters = [
        {
            "x": 22,
            "y": 54,
            "w": 264,
            "h": 108,
            "color": TERM,
            "title": "01 · WEB CRAFT & FORUMS",
            "sub": "Editorial UI · AI Workspace · Real-time",
            "items": ["f_forumv3", "f-forum", "F-Forum_v2"],
            "path": "M440,174 C354,174 336,108 286,108",
            "dur": "4.6s",
        },
        {
            "x": 594,
            "y": 54,
            "w": 264,
            "h": 108,
            "color": AMBER,
            "title": "02 · OPEN UI/3D VAULT",
            "sub": "Curated 6-library frontend archive",
            "items": ["SOURCEOFKNOWLEDGFORAI", "7,750+ UI"],
            "path": "M440,174 C526,174 544,108 594,108",
            "dur": "5.2s",
        },
        {
            "x": 22,
            "y": 182,
            "w": 264,
            "h": 108,
            "color": ARCH_SOFT,
            "title": "03 · AUTOMATION & REVERSING",
            "sub": "Userscripts · DOM/State Reconstruction",
            "items": ["Edunext_fe", "edunext-legacy", "shoptify"],
            "path": "M440,174 C354,174 336,236 286,236",
            "dur": "5.6s",
        },
        {
            "x": 594,
            "y": 182,
            "w": 264,
            "h": 108,
            "color": "#a78bfa",
            "title": "04 · PROTOTYPES & TUNING",
            "sub": "Web experiments & asset optimization",
            "items": ["Socratic", "resourcepack"],
            "path": "M440,174 C526,174 544,236 594,236",
            "dur": "4.9s",
        },
    ]

    # Cubic Bezier connection tracks + animated packets
    for cl in clusters:
        parts.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.5"/>' % (cl["path"], BORDER_HI))
        parts.append(
            '<path d="%s" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="5 7" stroke-opacity="0.6">'
            '<animate attributeName="stroke-dashoffset" from="24" to="0" dur="2.2s" repeatCount="indefinite"/></path>'
            % (cl["path"], cl["color"])
        )
        parts.append(
            '<circle r="3" fill="%s"><animateMotion dur="%s" repeatCount="indefinite" path="%s"/></circle>'
            % (cl["color"], cl["dur"], cl["path"])
        )

    # Central hub
    parts.append('<circle cx="%d" cy="%d" r="54" fill="%s" stroke="%s" stroke-width="1.5"/>' % (cx, cy, CARD, TERM))
    parts.append(
        '<circle cx="%d" cy="%d" r="62" fill="none" stroke="%s" stroke-width="1" stroke-dasharray="4 6" stroke-opacity="0.5">'
        '<animateTransform attributeName="transform" type="rotate" from="0 %d %d" to="360 %d %d" dur="22s" repeatCount="indefinite"/></circle>'
        % (cx, cy, ARCH_SOFT, cx, cy, cx, cy)
    )
    parts.append(arch_mark(cx - 11, cy - 30, 22, ARCH_SOFT))
    parts.append(text(cx, cy + 8, "CORE", TEXT, 13, "middle", "700", ' letter-spacing="1.4"'))
    parts.append(text(cx, cy + 24, "broamstuck", TERM, 9, "middle", "600"))
    parts.append(text(cx, cy + 37, "%d repos" % max(len(repo_map), 10), MUTED, 8, "middle"))

    # 4 Cluster Cards
    for cl in clusters:
        x, y, w, h, col = cl["x"], cl["y"], cl["w"], cl["h"], cl["color"]
        parts.append('<rect x="%d" y="%d" width="%d" height="%d" rx="10" fill="%s" stroke="%s" stroke-width="1"/>' % (x, y, w, h, CARD, BORDER_HI))
        parts.append('<rect x="%d" y="%d" width="%d" height="3" rx="1.5" fill="%s"/>' % (x + 12, y, w - 24, col))
        parts.append(text(x + 14, y + 24, cl["title"], col, 9.5, "start", "700", ' letter-spacing="0.5"'))
        parts.append(text(x + 14, y + 41, cl["sub"], MUTED, 9, "start", "400", "", SANS))
        px = x + 14
        py = y + 56
        for item in cl["items"]:
            lbl = item[:22]
            pw = pill_width(lbl, 7.8)
            if px + pw > x + w - 12:
                px = x + 14
                py += 24
            parts.append(pill(px, py, lbl, 19, BG, BORDER_HI, TEXT, 7.8))
            px += pw + 6

    parts.append("</svg>")
    return "\n".join(parts)


def featured_gallery_svg(repo_map):
    width, height = 880, 336
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 336" width="880" height="336" role="img" aria-label="Featured Repositories Gallery">',
        REDUCED_MOTION_STYLE,
    ]
    parts.extend(window_frame(width, height, "./gallery.sh --featured", "4 flagships"))

    featured = [
        (
            "f_forumv3",
            "F-Forum v3 · Spatial Studio",
            "AI web workbench, 7,750+ curated free UI/3D specimens, live chat & feed.",
            "fforum3.vercel.app",
            TERM,
            "studio",
        ),
        (
            "SOURCEOFKNOWLEDGFORAI",
            "Source of Knowledge",
            "Agent-ready archive normalizing 6 design & WebGL libraries with verified previews.",
            "6 libraries",
            AMBER,
            "vault",
        ),
        (
            "Edunext_fe",
            "EduNext BAS Engine",
            "Userscript reading prompts, drafting structured answers & tracking submissions.",
            "Tampermonkey",
            ARCH_SOFT,
            "circuit",
        ),
        (
            "shoptify-winter-reverser-engine",
            "Winter '26 Reverser",
            "Offline front-end architecture teardown, asset capture & local mirror reader.",
            "Architecture",
            "#a78bfa",
            "prism",
        ),
    ]

    for idx, (repo_key, title, desc, tag, accent, motif) in enumerate(featured):
        col = idx % 2
        row = idx // 2
        x = 16 + col * 430
        y = 48 + row * 138
        w, h = 418, 126
        meta = repo_map.get(repo_key, {})
        stars = meta.get("stars", 0)
        lang = meta.get("lang", "TypeScript")
        lang_col = LANG_COLORS.get(lang, accent)

        parts.append('<rect x="%d" y="%d" width="%d" height="%d" rx="10" fill="%s" stroke="%s" stroke-width="1"/>' % (x, y, w, h, CARD, BORDER_HI))
        # Left miniature fine-art blueprint plate (84x98)
        mx, my = x + 14, y + 14
        parts.append('<rect x="%d" y="%d" width="86" height="98" rx="8" fill="%s" stroke="%s" stroke-width="1"/>' % (mx, my, BG_DEEP, BORDER))
        if motif == "studio":
            parts.append('<rect x="%d" y="%d" width="58" height="36" rx="4" fill="none" stroke="%s" stroke-width="1.3"/>' % (mx + 14, my + 16, accent))
            parts.append('<rect x="%d" y="%d" width="26" height="24" rx="3" fill="%s" fill-opacity="0.18" stroke="%s" stroke-width="1"/>' % (mx + 14, my + 58, accent, accent))
            parts.append('<rect x="%d" y="%d" width="26" height="24" rx="3" fill="none" stroke="%s" stroke-width="1"/>' % (mx + 46, my + 58, ARCH_SOFT))
        elif motif == "vault":
            for b in range(5):
                bx = mx + 15 + b * 11
                bh = 52 if b != 2 else 62
                by = my + 78 - bh
                bc = accent if b == 2 else BORDER_HI
                parts.append('<rect x="%d" y="%d" width="8" height="%d" rx="2" fill="%s" fill-opacity="%s" stroke="%s" stroke-width="1"/>' % (bx, by, bh, bc, "0.28" if b == 2 else "0.14", bc))
        elif motif == "circuit":
            parts.append('<path d="M%d %d H%d V%d H%d" fill="none" stroke="%s" stroke-width="1.4"/>' % (mx + 14, my + 32, mx + 44, my + 66, mx + 72, accent))
            parts.append('<path d="M%d %d V%d H%d" fill="none" stroke="%s" stroke-width="1.2"/>' % (mx + 28, my + 76, my + 48, mx + 70, TERM))
            parts.append('<circle cx="%d" cy="%d" r="4" fill="%s"/>' % (mx + 44, my + 48, accent))
            parts.append('<circle cx="%d" cy="%d" r="3" fill="%s"/>' % (mx + 72, my + 66, AMBER))
        else:
            parts.append('<polygon points="%d,%d %d,%d %d,%d %d,%d" fill="%s" fill-opacity="0.16" stroke="%s" stroke-width="1.4"/>' % (mx + 43, my + 16, mx + 70, my + 49, mx + 43, my + 82, mx + 16, my + 49, accent, accent))
            parts.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="1"/>' % (mx + 16, my + 49, mx + 70, my + 49, ARCH_SOFT))

        # Right copy block (clean word-boundary wrapping)
        tx = x + 114
        line1, line2 = wrap_two_lines(desc, 44)
        parts.append(text(tx, y + 32, title, TEXT, 13, "start", "700", "", SANS))
        parts.append(text(tx, y + 52, line1, MUTED, 9.6, "start", "400", "", SANS))
        parts.append(text(tx, y + 67, line2, MUTED, 9.6, "start", "400", "", SANS))
        # Footer metadata row
        parts.append('<circle cx="%d" cy="%d" r="3.6" fill="%s"/>' % (tx + 4, y + 101, lang_col))
        parts.append(text(tx + 14, y + 104, lang, TEXT, 9.2, "start", "500"))
        parts.append('<path d="%s" fill="%s"/>' % (star_path(tx + 112, y + 100, 5.2, 2.2), AMBER))
        parts.append(text(tx + 122, y + 104, str(stars), AMBER, 9.5, "start", "700"))
        parts.append(pill(x + w - 12 - pill_width(tag, 8), y + 91, tag, 19, BG, BORDER_HI, accent, 8))

    parts.append("</svg>")
    return "\n".join(parts)


def compact(value):
    for suffix, scale in (("B", 1000000000.0), ("M", 1000000.0), ("K", 1000.0)):
        if value >= scale:
            return "%.1f%s" % (value / scale, suffix)
    return str(int(value))


def specs_svg(langs, chars, disk, repos):
    width, height = 880, 268
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 268" width="880" height="268" role="img">',
        REDUCED_MOTION_STYLE,
    ]
    parts.extend(window_frame(width, height, "./specs.sh", "fastfetch"))
    parts.append(text(26, 58, "[system]", MUTED, 9.5, "start", "600", ' letter-spacing="0.6"'))
    parts.append(text(450, 58, "[stack]", MUTED, 9.5, "start", "600", ' letter-spacing="0.6"'))
    parts.append('<line x1="26" y1="67" x2="854" y2="67" stroke="%s" stroke-width="1" stroke-dasharray="3 4"/>' % BORDER)
    parts.append('<line x1="424" y1="48" x2="424" y2="196" stroke="%s" stroke-width="1" stroke-dasharray="2 5"/>' % BORDER)
    system = [
        ("os", "Arch Linux 6.12 LTS"),
        ("wm", "Hyprland / Wayland"),
        ("shell", "zsh 5.9 / tmux"),
        ("editor", "neovim 0.10"),
        ("terminal", "kitty / jetbrains mono"),
        ("focus", "Systems UI · Reversing"),
    ]
    for index, (key, value) in enumerate(system):
        baseline = 89 + index * 20.5
        parts.append(text(26, baseline, key, MUTED, 10))
        parts.append(text(150, baseline, value, TEXT, 10, "start", "600"))
    total = sum(size for _, size in langs) or 1
    raw = [size * 100.0 / total for _, size in langs]
    counts = [int(value) for value in raw]
    order = sorted(range(len(raw)), key=lambda index: raw[index] - counts[index], reverse=True)
    for index in order[: max(0, 100 - sum(counts))]:
        counts[index] += 1
    shades = (TERM, TERM_MID, ARCH_SOFT, ARCH, AMBER, "#a78bfa")
    for index, (name, size) in enumerate(langs[:6]):
        baseline = 89 + index * 20.5
        share = size / float(total)
        parts.append(text(450, baseline, name, TEXT, 10, "start", "600"))
        parts.append('<rect x="556" y="%s" width="238" height="6.5" rx="3.2" fill="%s"/>' % (num(baseline - 4.8), BORDER))
        parts.append(
            '<rect x="556" y="%s" width="%s" height="6.5" rx="3.2" fill="%s"/>'
            % (num(baseline - 4.8), num(max(6.0, 238 * share)), shades[index])
        )
        parts.append(text(854, baseline, "%d%%" % counts[index] if counts[index] else "<1%", MUTED, 9.5, "end"))
    parts.append('<line x1="1" y1="204" x2="%s" y2="204" stroke="%s" stroke-width="1"/>' % (num(width - 1), BORDER))
    totals = [
        (26, compact(chars), "characters of code", TERM),
        (316, "%.2f GB" % (disk / 1073741824.0), "repository disk", ARCH_SOFT),
        (606, str(repos), "public repos", AMBER),
    ]
    for x, value, label, color in totals:
        parts.append(text(x, 237, value, color, 17.5, "start", "700"))
        parts.append(text(x, 254, label, MUTED, 9))
    parts.append(text(854, 254, "%d languages indexed" % len(langs), MUTED, 9, "end"))
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
    telemetry = compute_calendar_telemetry(data["days"], data["weeks"])
    write("hero-banner.svg", hero_banner_svg(data["total"], data["stars"], data["repos"], telemetry))
    write("header-contributions.svg", header_svg("./contributions.sh"))
    write("contributions.svg", contributions_svg(data["days"], data["total"], telemetry))
    write("header-whoami.svg", header_svg("whoami"))
    write("portrait.svg", portrait_svg(load_portrait()))
    write("dashboard.svg", dashboard_svg(data["langs"], data["stars"], data["repos"], data["commits"], data["events"], telemetry))
    write("header-ecosystem.svg", header_svg("./ecosystem-map.sh"))
    write("ecosystem-mindmap.svg", ecosystem_mindmap_svg(data["repo_map"]))
    write("header-gallery.svg", header_svg("./gallery.sh --featured"))
    write("featured-gallery.svg", featured_gallery_svg(data["repo_map"]))
    write("specs.svg", specs_svg(data["langs"], data["bytes"], data["disk"], data["repos"]))
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
