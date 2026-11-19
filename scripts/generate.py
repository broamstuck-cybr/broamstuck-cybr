import datetime
import json
import math
import os
import urllib.request

FONT = "'JetBrains Mono', 'Fira Code', monospace"
USERNAME = os.environ.get("GH_PROFILE_USERNAME", "broamstuck-cybr")
HANDLE = os.environ.get("GH_PROFILE_HANDLE", "broamstuck")
DISPLAY = os.environ.get("GH_PROFILE_DISPLAY", "Bro Am Stuck")
TOKEN = os.environ.get("GITHUB_TOKEN", "") or os.environ.get("GH_TOKEN", "")
API = (os.environ.get("GITHUB_API_URL", "") or "https://api.github.com").rstrip("/")
GQL = (os.environ.get("GITHUB_GRAPHQL_URL", "") or "https://api.github.com/graphql").rstrip("/")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")

BG = "#090d16"
CARD = "#111622"
BORDER = "#1e293b"
ARCH = "#1793d1"
TERM = "#39d353"
AMBER = "#e3b341"
TEXT = "#f8fafc"
MUTED = "#8b949e"
LEVELS = ["#1b2233", "#0e4429", "#006d32", "#26a641", "#39d353"]

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


def num(value, places=2):
    text = ("%." + str(places) + "f") % float(value)
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    if text in ("", "-0"):
        text = "0"
    return text


def esc(value):
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def text(x, y, body, fill=TEXT, size=11, anchor="start", weight="400", extra=""):
    return (
        '<text x="%s" y="%s" font-family="%s" font-size="%s" font-weight="%s" '
        'fill="%s" text-anchor="%s"%s>%s</text>'
        % (num(x), num(y), FONT, num(size), weight, fill, anchor, extra, esc(body))
    )


def raw_text(x, y, inner, fill=TEXT, size=11, anchor="start", weight="400", extra=""):
    return (
        '<text x="%s" y="%s" font-family="%s" font-size="%s" font-weight="%s" '
        'fill="%s" text-anchor="%s"%s>%s</text>'
        % (num(x), num(y), FONT, num(size), weight, fill, anchor, extra, inner)
    )


def arch_mark(x, y, size, fill=ARCH):
    return '<g transform="translate(%s %s) scale(%s)"><path d="%s" fill="%s"/></g>' % (
        num(x),
        num(y),
        num(size / 24.0, 4),
        ARCH_PATH,
        fill,
    )


def pill(x, y, label, height=18, fill=CARD, stroke=BORDER, color=MUTED, size=8.5):
    width = len(label) * size * 0.6 + 17
    return (
        '<rect x="%s" y="%s" width="%s" height="%s" rx="%s" fill="%s" stroke="%s" stroke-width="1"/>'
        % (num(x), num(y), num(width), num(height), num(height / 2.0), fill, stroke)
        + text(x + width / 2.0, y + height / 2.0 + size * 0.36, label, color, size, "middle", "500", ' letter-spacing="0.4"')
    )


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
        "total": 0,
        "commits": 0,
        "stars": 0,
        "repos": 0,
        "langs": [],
        "events": [],
    }
    query = (
        "query($login:String!){user(login:$login){"
        "contributionsCollection{totalCommitContributions "
        "contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}"
        "repositories(first:100,ownerAffiliations:OWNER,isFork:false,privacy:PUBLIC){totalCount "
        "nodes{stargazerCount languages(first:10,orderBy:{field:SIZE,direction:DESC})"
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
            for day in week.get("contributionDays") or []:
                data["days"][day.get("date")] = int(day.get("contributionCount") or 0)
        repos = user.get("repositories") or {}
        data["repos"] = int(repos.get("totalCount") or 0)
        sizes = {}
        for node in repos.get("nodes") or []:
            data["stars"] += int(node.get("stargazerCount") or 0)
            for edge in (node.get("languages") or {}).get("edges") or []:
                name = ((edge.get("node") or {}).get("name")) or ""
                if name:
                    sizes[name] = sizes.get(name, 0) + int(edge.get("size") or 0)
        data["langs"] = sorted(sizes.items(), key=lambda item: item[1], reverse=True)
    data["events"] = collect_events()
    return data


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


def header_svg(command):
    label = "%s@arch ~ $ %s" % (HANDLE, command)
    size = 13
    icon = 15
    gap = 9
    pad = 18
    height = 33
    width = pad * 2 + icon + gap + len(label) * size * 0.6
    x = (800 - width) / 2.0
    y = (44 - height) / 2.0
    inner = (
        '<tspan fill="%s">%s</tspan><tspan fill="%s">@arch</tspan>'
        '<tspan fill="%s"> ~ $ </tspan><tspan fill="%s">%s</tspan>'
    ) % (TERM, esc(HANDLE), ARCH, MUTED, TEXT, esc(command))
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 44" width="800" height="44" role="img">',
        '<rect x="%s" y="%s" width="%s" height="%s" rx="%s" fill="%s" stroke="%s" stroke-width="1"/>'
        % (num(x), num(y), num(width), num(height), num(height / 2.0), CARD, BORDER),
        arch_mark(x + pad, y + (height - icon) / 2.0, icon),
        raw_text(x + pad + icon + gap, y + height / 2.0 + 4.5, inner, TEXT, size),
        "</svg>",
    ]
    return "\n".join(parts)


def contributions_svg(day_map, total):
    cell = 11
    gap = 3
    pitch = cell + gap
    grid_x = 72
    grid_y = 34
    month_y = 24
    footer_y = 151
    today = datetime.date.today()
    start = today - datetime.timedelta(days=(today.weekday() + 1) % 7) - datetime.timedelta(weeks=51)
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 840 165" width="840" height="165" role="img">',
        '<rect x="0.5" y="0.5" width="839" height="164" rx="10" fill="%s" stroke="%s" stroke-width="1"/>' % (CARD, BORDER),
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
        parts.append(text(grid_x - 9, grid_y + row * pitch + cell / 2.0 + 3.4, label, MUTED, 9, "end"))
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
            parts.append(
                '<rect x="%s" y="%s" width="%s" height="%s" rx="3" fill="%s"/>'
                % (num(grid_x + column * pitch), num(grid_y + row * pitch), cell, cell, LEVELS[level])
            )
    parts.append(
        raw_text(
            grid_x,
            footer_y,
            '<tspan fill="%s" font-weight="700">%s</tspan><tspan fill="%s"> contributions in the last year</tspan>'
            % (TERM, esc(str(total)), MUTED),
            MUTED,
            11.5,
        )
    )
    parts.append("</svg>")
    return "\n".join(parts)


def window_frame(width, height, script, badge, gradient_stops=None):
    parts = [
        '<rect x="0.5" y="0.5" width="%s" height="%s" rx="10" fill="%s" stroke="%s" stroke-width="1"/>'
        % (num(width - 1), num(height - 1), BG, BORDER),
        '<path d="M11 1 H%s A10 10 0 0 1 %s 11 V33 H1 V11 A10 10 0 0 1 11 1 Z" fill="%s"/>'
        % (num(width - 11), num(width - 1), CARD),
        '<line x1="1" y1="33" x2="%s" y2="33" stroke="%s" stroke-width="1"/>' % (num(width - 1), BORDER),
        arch_mark(13, 9.5, 14),
        text(33, 21.5, script, MUTED, 10.5),
    ]
    badge_width = len(badge) * 8 * 0.6 + 17
    parts.append(pill(width - 12 - badge_width, 8, badge, 17, CARD, BORDER, MUTED, 8))
    return parts


def portrait_svg(lines):
    width = 490
    height = 520
    body_top = 33
    status_line = 490
    body_height = status_line - body_top
    max_len = max([len(line) for line in lines] or [1])
    size = min(
        (width - 40) / (max_len * 0.6),
        (body_height - 26) / (max(len(lines), 1) * 1.16),
        15.0,
    )
    size = max(size, 3.0)
    block_height = len(lines) * size * 1.16
    first = body_top + (body_height - block_height) / 2.0 + size * 0.92
    x0 = (width - max_len * size * 0.6) / 2.0
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 490 520" width="490" height="520" role="img">',
        "<defs>",
        '<linearGradient id="ascii" x1="0" y1="0" x2="0" y2="1">',
        '<stop offset="0" stop-color="%s"/>' % TERM,
        '<stop offset="0.55" stop-color="#26a641"/>',
        '<stop offset="1" stop-color="%s"/>' % ARCH,
        "</linearGradient>",
        "</defs>",
    ]
    parts.extend(window_frame(width, height, "./portrait.sh", "hyprland"))
    for index, line in enumerate(lines):
        parts.append(
            text(
                x0,
                first + index * size * 1.16,
                line,
                "url(#ascii)",
                size,
                "start",
                "500",
                ' xml:space="preserve"',
            )
        )
    parts.append(
        '<line x1="1" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="1"/>'
        % (num(status_line), num(width - 1), num(status_line), BORDER)
    )
    parts.append(
        raw_text(
            14,
            status_line + 19,
            '<tspan fill="%s">%s@arch:~$ </tspan><tspan fill="%s" font-weight="700">%s</tspan>'
            % (MUTED, esc(HANDLE), TERM, esc(DISPLAY)),
            MUTED,
            11,
        )
    )
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


def radar_svg(langs, cx, cy, radius, top, bottom):
    parts = []
    for ring in (0.36, 0.68, 1.0):
        points = []
        for axis in range(6):
            angle = math.radians(-90 + axis * 60)
            points.append(
                "%s,%s"
                % (num(cx + radius * ring * math.cos(angle)), num(cy + radius * ring * math.sin(angle)))
            )
        parts.append(
            '<polygon points="%s" fill="none" stroke="%s" stroke-width="1"/>' % (" ".join(points), BORDER)
        )
    for axis in range(6):
        angle = math.radians(-90 + axis * 60)
        parts.append(
            '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="1"/>'
            % (
                num(cx),
                num(cy),
                num(cx + radius * math.cos(angle)),
                num(cy + radius * math.sin(angle)),
                BORDER,
            )
        )
    plotted = []
    for axis in range(6):
        angle = math.radians(-90 + axis * 60)
        if axis < len(langs):
            ratio = math.sqrt(langs[axis][1]) / math.sqrt(top if top else 1)
            ratio = max(ratio, 0.17)
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
    parts.append(
        '<polygon points="%s" fill="rgba(57, 211, 83, 0.25)" stroke="%s" stroke-width="1.5" stroke-linejoin="round"/>'
        % (polygon, TERM)
    )
    for px, py, name, cos_value, sin_value in plotted:
        parts.append('<circle cx="%s" cy="%s" r="2.2" fill="%s"/>' % (num(px), num(py), TERM))
        if not name:
            continue
        lx = cx + (radius + 15) * cos_value
        ly = cy + (radius + 15) * sin_value
        anchor = "middle"
        if cos_value > 0.25:
            anchor = "start"
        elif cos_value < -0.25:
            anchor = "end"
        ly += 3.2 if sin_value > 0 else (-1.0 if sin_value < 0 else 3.2)
        parts.append(text(lx, ly, name, ARCH, 8.5, anchor, "500"))
    return parts


def dashboard_svg(langs, stars, repos, commits, events):
    width = 490
    height = 520
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 490 520" width="490" height="520" role="img">',
    ]
    parts.extend(window_frame(width, height, "./dashboard.sh", "arch-linux"))

    parts.append(
        '<rect x="10.5" y="42.5" width="281" height="251" rx="8" fill="%s" stroke="%s" stroke-width="1"/>'
        % (CARD, BORDER)
    )
    parts.append(
        raw_text(
            22,
            62,
            '<tspan fill="%s">$ </tspan><tspan fill="%s" font-weight="600">lang-radar</tspan>' % (MUTED, TEXT),
            TEXT,
            10,
        )
    )
    top = langs[0][1] if langs else 0
    parts.extend(radar_svg(langs[:6], 151, 184, 86, top, 0))

    parts.append(
        '<rect x="302.5" y="42.5" width="177" height="251" rx="8" fill="%s" stroke="%s" stroke-width="1"/>'
        % (CARD, BORDER)
    )
    parts.append(
        raw_text(
            314,
            62,
            '<tspan fill="%s">$ </tspan><tspan fill="%s" font-weight="600">star-counter</tspan>' % (MUTED, TEXT),
            TEXT,
            10,
        )
    )
    metrics = [
        (98, str(stars), "total stars", AMBER, "star"),
        (154, str(repos), "public repos", ARCH, "diamond"),
        (210, str(commits), "commits (1y)", TERM, "chevron"),
    ]
    for baseline, value, label, color, icon in metrics:
        if icon == "star":
            parts.append('<path d="%s" fill="%s"/>' % (star_path(322, baseline - 5), color))
        elif icon == "diamond":
            parts.append('<path d="%s" fill="%s" fill-opacity="0.85"/>' % (diamond_path(322, baseline - 5), color))
        else:
            parts.append(
                '<polyline points="%s" fill="none" stroke="%s" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
                % (
                    " ".join(
                        [
                            "%s,%s" % (num(317), num(baseline - 11)),
                            "%s,%s" % (num(326), num(baseline - 5)),
                            "%s,%s" % (num(317), num(baseline + 1)),
                        ]
                    ),
                    color,
                )
            )
        parts.append(text(340, baseline, value, TEXT, 20, "start", "700"))
        parts.append(text(314, baseline + 15, label, MUTED, 8.5, "start", "400"))

    parts.append(
        '<rect x="10.5" y="302.5" width="469" height="207" rx="8" fill="%s" stroke="%s" stroke-width="1"/>'
        % (CARD, BORDER)
    )
    parts.append(
        raw_text(
            22,
            321,
            '<tspan fill="%s">$ </tspan><tspan fill="%s" font-weight="600">tail -n 5 /var/log/github-all.log</tspan>'
            % (MUTED, TEXT),
            TEXT,
            9.5,
        )
    )
    parts.append(
        '<line x1="11" y1="333" x2="479" y2="333" stroke="%s" stroke-width="1" stroke-dasharray="3 4"/>' % BORDER
    )
    size = 9
    line_pitch = 27
    first = 354
    plain = ""
    for index in range(5):
        baseline = first + index * line_pitch
        if index < len(events):
            event = events[index]
            repo = event["repo"][:26]
            message = event["message"][:34]
            inner = (
                '<tspan fill="%s">[%s] </tspan><tspan fill="%s">* </tspan>'
                '<tspan fill="%s">%s </tspan><tspan fill="%s">(%s) </tspan><tspan fill="%s">%s</tspan>'
                % (MUTED, esc(event["time"]), ARCH, AMBER, esc(event["sha"]), ARCH, esc(repo), TEXT, esc(message))
            )
            plain = "[%s] * %s (%s) %s" % (event["time"], event["sha"], repo, message)
        else:
            inner = '<tspan fill="%s">[--:--] * ------- (—) no recent push events</tspan>' % MUTED
            plain = "[--:--] * ------- (—) no recent push events"
        parts.append(raw_text(22, baseline, inner, TEXT, size, "start", "400", ' xml:space="preserve"'))
    cursor_x = 22 + len(plain) * size * 0.6 + 3
    cursor_y = first + 4 * line_pitch - size * 0.82
    parts.append(
        '<text x="%s" y="%s" font-family="%s" font-size="%s" fill="%s" opacity="1">█'
        '<animate attributeName="opacity" values="1;0;1" dur="1.1s" repeatCount="indefinite"/></text>'
        % (num(cursor_x), num(cursor_y), FONT, num(size), TERM)
    )
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
    write("header-contributions.svg", header_svg("./contributions.sh"))
    write("contributions.svg", contributions_svg(data["days"], data["total"]))
    write("header-whoami.svg", header_svg("whoami"))
    write("portrait.svg", portrait_svg(load_portrait()))
    write("dashboard.svg", dashboard_svg(data["langs"], data["stars"], data["repos"], data["commits"], data["events"]))
    print(
        "synced %s: %d contributions, %d commits, %d stars, %d repos, %d languages, %d events"
        % (
            USERNAME,
            data["total"],
            data["commits"],
            data["stars"],
            data["repos"],
            len(data["langs"]),
            len(data["events"]),
        )
    )


if __name__ == "__main__":
    main()
