// SPDX-License-Identifier: MIT
// WHY: Coordinates the hydrodynamic sky, 52-week celestial matrix, 5D astrolabe, HD glyph portrait, 4-state console, and 360-degree 3D F-Forum stages.

import { LiquidStarrySky } from "./sky-engine.js";
import { PortraitStage, Radar5DStage, Forum3DStage } from "./models-3d.js";

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

class CelestialMatrixStage {
  constructor(canvas, telemetry, onDayHover) {
    this.canvas = canvas;
    this.ctx = canvas.getContext("2d");
    this.daysMap = telemetry.days || {};
    this.weeks52 = (telemetry.streaks && telemetry.streaks.weeks52) || [];
    this.onDayHover = onDayHover;
    this.filter = "all";
    this.pointerX = 560;
    this.selectedIdx = -1;
    this.cells = [];
    this.time = 0;
    this.reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    this.w = 1120;
    this.h = 214;
    this.canvas.width = this.w;
    this.canvas.height = this.h;

    this._buildCells();
    this._bindEvents();
    this.render();
    if (!this.reducedMotion) {
      this._loop();
    }
  }

  setFilter(mode) {
    this.filter = mode;
    this.render();
  }

  _matchesFilter(count) {
    if (this.filter === "supernova") return count >= 20;
    if (this.filter === "radiant") return count >= 5 && count < 20;
    if (this.filter === "spark") return count >= 1 && count < 5;
    return true;
  }

  _buildCells() {
    const dates = Object.keys(this.daysMap).sort();
    const lastIso = dates.length ? dates[dates.length - 1] : "2026-11-24";
    const endDay = new Date(lastIso + "T00:00:00Z");
    const dow = endDay.getUTCDay();
    const endSunday = new Date(endDay.getTime() - dow * 86400000);
    const startSunday = new Date(endSunday.getTime() - 51 * 7 * 86400000);

    const gx = 54;
    const gy = 34;
    const px = 20.1;
    const py = 19.2;

    this.monthLabels = [];
    let lastMonth = -1;
    let lastW = -9;

    for (let w = 0; w < 52; w++) {
      const ws = new Date(startSunday.getTime() + w * 7 * 86400000);
      const m = ws.getUTCMonth();
      if (m !== lastMonth) {
        if (!(w === 0 && ws.getUTCDate() > 16)) {
          lastMonth = m;
          if (w - lastW >= 3) {
            this.monthLabels.push({ x: gx + w * px, text: MONTHS[m] });
            lastW = w;
          }
        } else {
          lastMonth = m;
        }
      }
      for (let r = 0; r < 7; r++) {
        const d = new Date(startSunday.getTime() + (w * 7 + r) * 86400000);
        if (d > endDay) continue;
        const iso = d.toISOString().slice(0, 10);
        const count = Number(this.daysMap[iso] || 0);
        this.cells.push({
          w,
          r,
          x: gx + w * px,
          y: gy + r * py,
          iso,
          count,
          weekSum: this.weeks52[w] || 0
        });
      }
    }
    this.selectedIdx = this.cells.length - 1;
  }

  _bindEvents() {
    const pick = (ev) => {
      const rect = this.canvas.getBoundingClientRect();
      const sx = ((ev.clientX - rect.left) / Math.max(1, rect.width)) * this.w;
      const sy = ((ev.clientY - rect.top) / Math.max(1, rect.height)) * this.h;
      this.pointerX = sx;

      let best = -1;
      let bestDist = 18;
      for (let i = 0; i < this.cells.length; i++) {
        const c = this.cells[i];
        const d = Math.hypot(sx - c.x, sy - c.y);
        if (d < bestDist) {
          bestDist = d;
          best = i;
        }
      }
      if (best >= 0 && best !== this.selectedIdx) {
        this.selectedIdx = best;
        this._emitSelected();
      }
      if (this.reducedMotion) this.render();
    };

    this.canvas.addEventListener("pointermove", pick);
    this.canvas.addEventListener("pointerdown", pick);
    this.canvas.addEventListener("keydown", (ev) => {
      if (!this.cells.length) return;
      if (ev.key === "ArrowLeft") {
        this.selectedIdx = Math.max(0, this.selectedIdx - 1);
        this._emitSelected();
        this.render();
        ev.preventDefault();
      } else if (ev.key === "ArrowRight") {
        this.selectedIdx = Math.min(this.cells.length - 1, this.selectedIdx + 1);
        this._emitSelected();
        this.render();
        ev.preventDefault();
      }
    });
  }

  _emitSelected() {
    if (this.onDayHover && this.selectedIdx >= 0 && this.cells[this.selectedIdx]) {
      this.onDayHover(this.cells[this.selectedIdx]);
    }
  }

  _loop() {
    const step = () => {
      this.time += 0.02;
      this.render();
      requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }

  render() {
    const ctx = this.ctx;
    ctx.clearRect(0, 0, this.w, this.h);

    const sky = ctx.createLinearGradient(0, 0, this.w, this.h);
    sky.addColorStop(0, "#050b19");
    sky.addColorStop(0.55, "#091731");
    sky.addColorStop(1, "#040915");
    ctx.fillStyle = sky;
    ctx.fillRect(0, 0, this.w, this.h);

    ctx.font = "600 10.5px 'Inter', system-ui, sans-serif";
    ctx.fillStyle = "#8ea4c2";
    ctx.textAlign = "center";
    for (let i = 0; i < this.monthLabels.length; i++) {
      ctx.fillText(this.monthLabels[i].text, this.monthLabels[i].x, 16);
    }

    ctx.font = "500 10px 'JetBrains Mono', ui-monospace, monospace";
    ctx.textAlign = "right";
    const rowDays = [[1, "Mon"], [3, "Wed"], [5, "Fri"]];
    for (let i = 0; i < rowDays.length; i++) {
      ctx.fillText(rowDays[i][1], 38, 38 + rowDays[i][0] * 19.2);
    }

    const coordKey = new Map();
    for (let i = 0; i < this.cells.length; i++) {
      const c = this.cells[i];
      coordKey.set(`${c.w}:${c.r}`, c);
    }

    for (let i = 0; i < this.cells.length; i++) {
      const c = this.cells[i];
      if (c.count < 2 || !this._matchesFilter(c.count)) continue;
      const down = coordKey.get(`${c.w}:${c.r + 1}`);
      if (down && down.count >= 2 && this._matchesFilter(down.count)) {
        ctx.strokeStyle = (c.count + down.count) >= 22 ? "rgba(253, 224, 71, 0.42)" : "rgba(125, 211, 252, 0.30)";
        ctx.lineWidth = 1.05;
        ctx.beginPath();
        ctx.moveTo(c.x, c.y);
        ctx.lineTo(down.x, down.y);
        ctx.stroke();
      }
      const right = coordKey.get(`${c.w + 1}:${c.r}`);
      if (right && right.count >= 4 && c.count >= 4 && this._matchesFilter(right.count)) {
        ctx.strokeStyle = "rgba(94, 234, 212, 0.30)";
        ctx.lineWidth = 0.95;
        ctx.beginPath();
        ctx.moveTo(c.x, c.y);
        ctx.lineTo(right.x, right.y);
        ctx.stroke();
      }
    }

    for (let i = 0; i < this.cells.length; i++) {
      const c = this.cells[i];
      const vis = this._matchesFilter(c.count);
      ctx.globalAlpha = vis ? 1 : 0.16;

      if (c.count === 0) {
        ctx.fillStyle = "#1a2d4d";
        ctx.beginPath();
        ctx.arc(c.x, c.y, 2.1, 0, Math.PI * 2);
        ctx.fill();
      } else if (c.count <= 4) {
        ctx.fillStyle = "#60a5fa";
        ctx.beginPath();
        ctx.arc(c.x, c.y, 3.1, 0, Math.PI * 2);
        ctx.fill();
      } else if (c.count <= 19) {
        ctx.fillStyle = "rgba(52, 211, 153, 0.22)";
        ctx.beginPath();
        ctx.arc(c.x, c.y, 6.4, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = "#34d399";
        ctx.beginPath();
        ctx.arc(c.x, c.y, 3.8, 0, Math.PI * 2);
        ctx.fill();
      } else {
        const g = ctx.createRadialGradient(c.x, c.y, 1, c.x, c.y, 11.5);
        g.addColorStop(0, "rgba(255, 255, 255, 0.95)");
        g.addColorStop(0.35, "rgba(253, 224, 71, 0.72)");
        g.addColorStop(1, "rgba(251, 191, 36, 0)");
        ctx.fillStyle = g;
        ctx.beginPath();
        ctx.arc(c.x, c.y, 11.5, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = "#fde047";
        ctx.beginPath();
        ctx.arc(c.x, c.y, 4.6, 0, Math.PI * 2);
        ctx.fill();
      }
    }
    ctx.globalAlpha = 1;

    if (this.selectedIdx >= 0 && this.cells[this.selectedIdx]) {
      const sel = this.cells[this.selectedIdx];
      ctx.strokeStyle = "#fde047";
      ctx.lineWidth = 1.6;
      ctx.beginPath();
      ctx.arc(sel.x, sel.y, 8.2, 0, Math.PI * 2);
      ctx.stroke();
    }

    const waterY = 174;
    ctx.strokeStyle = "rgba(125, 211, 252, 0.36)";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(36, waterY);
    ctx.lineTo(this.w - 24, waterY);
    ctx.stroke();

    const maxW = Math.max(1, ...this.weeks52);
    for (let w = 0; w < 52; w++) {
      const val = this.weeks52[w] || 0;
      if (val <= 0) continue;
      const norm = Math.pow(val / maxW, 0.62);
      const wx = 54 + w * 20.1;
      const cursorBoost = Math.exp(-Math.pow((wx - this.pointerX) / 95, 2)) * 4.5;
      for (let r = 1; r <= 3; r++) {
        const half = (3.8 + norm * 11 + cursorBoost) * (1 - r * 0.18);
        const shift = Math.sin(this.time * 1.8 + w * 0.5 + r) * 2.2;
        const ry = waterY + r * 8.4;
        ctx.strokeStyle = norm > 0.45 ? `rgba(253, 224, 71, ${(0.46 - r * 0.1).toFixed(2)})` : `rgba(125, 211, 252, ${(0.42 - r * 0.09).toFixed(2)})`;
        ctx.lineWidth = 1.25;
        ctx.beginPath();
        ctx.moveTo(wx - half + shift, ry);
        ctx.lineTo(wx + half + shift, ry);
        ctx.stroke();
      }
    }
  }
}

async function fetchJson(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

function tierLabel(count) {
  if (count >= 20) return "Supernova Tier";
  if (count >= 5) return "Radiant Corona";
  if (count >= 1) return "Starlight Spark";
  return "Quiet Night";
}

async function initObservatory() {
  const skyReadout = document.getElementById("sky-readout");
  const sky = new LiquidStarrySky(
    document.getElementById("sky-canvas"),
    document.getElementById("panorama-canvas"),
    (bodyText) => {
      skyReadout.textContent = bodyText;
    }
  );

  const turbBtns = document.querySelectorAll("[data-turbulence]");
  turbBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      const lv = Number(btn.dataset.turbulence);
      sky.setTurbulence(lv);
      turbBtns.forEach((b) => b.setAttribute("aria-pressed", String(b === btn)));
    });
  });

  let speedCycle = 0;
  const orbitBtn = document.getElementById("orbit-speed-btn");
  orbitBtn.addEventListener("click", () => {
    const modes = [
      { mult: 1, label: "Orbits: 1x" },
      { mult: 5, label: "Orbits: 5x" },
      { mult: 0, label: "Orbits: Pause" }
    ];
    speedCycle = (speedCycle + 1) % modes.length;
    sky.setOrbitSpeed(modes[speedCycle].mult);
    orbitBtn.textContent = modes[speedCycle].label;
  });

  document.getElementById("stir-sky-btn").addEventListener("click", () => {
    sky.triggerWave(0.35 + Math.random() * 0.3, 0.5);
    skyReadout.textContent = "Impasto wavefront injected across Milky Way & Solar Orrery";
  });

  let telemetry;
  let portraitData;
  try {
    [telemetry, portraitData] = await Promise.all([
      fetchJson("assets/telemetry.json"),
      fetchJson("assets/portrait_hd.json")
    ]);
  } catch (err) {
    const list = document.getElementById("console-list");
    list.innerHTML = "";
    const panel = document.createElement("div");
    panel.className = "state-panel";
    panel.innerHTML = `<strong>Telemetry bundle unavailable (${err.message}).</strong><span>Verify local assets/telemetry.json or retry loading.</span>`;
    const retry = document.createElement("button");
    retry.type = "button";
    retry.className = "chip-btn";
    retry.textContent = "Retry Load";
    retry.addEventListener("click", () => window.location.reload());
    panel.appendChild(retry);
    list.appendChild(panel);
    return;
  }

  document.getElementById("mat-total").textContent = String(telemetry.metrics.contributions);
  document.getElementById("mat-streak").textContent = `${telemetry.streaks.longest}-day`;
  document.getElementById("val-chars").textContent = telemetry.metrics.bytesCompact;
  document.getElementById("val-commits").textContent = String(telemetry.metrics.commits);
  document.getElementById("val-stars").textContent = String(telemetry.metrics.stars);
  document.getElementById("val-contribs").textContent = String(telemetry.metrics.contributions);

  const matInspector = document.getElementById("matrix-inspector");
  const matrixStage = new CelestialMatrixStage(document.getElementById("matrix-canvas"), telemetry, (cell) => {
    matInspector.textContent = `${cell.iso} · ${cell.count} contribution${cell.count === 1 ? "" : "s"} · ${tierLabel(cell.count)} · Weekly pulse: ${cell.weekSum}`;
  });
  matrixStage._emitSelected();
  const matScroll = document.querySelector(".matrix-scroll");
  if (matScroll) {
    matScroll.scrollLeft = matScroll.scrollWidth;
  }

  const matFilterBtns = document.querySelectorAll("[data-mat-filter]");
  matFilterBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      matrixStage.setFilter(btn.dataset.matFilter);
      matFilterBtns.forEach((b) => b.classList.toggle("is-active", b === btn));
    });
  });

  const portraitStage = new PortraitStage(document.getElementById("portrait-canvas"), portraitData);
  const portraitBtns = document.querySelectorAll("[data-portrait-mode]");
  portraitBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      portraitStage.setMode(btn.dataset.portraitMode);
      portraitBtns.forEach((b) => b.classList.toggle("is-active", b === btn));
    });
  });

  const radarReadout = document.getElementById("radar-readout");
  const langPillsWrap = document.getElementById("lang-pills");

  const updateRadarReadout = (selectedName) => {
    if (!selectedName) {
      radarReadout.innerHTML = `<span><strong>All 6 Domains</strong> · Drag 360° or select a language</span><span>${telemetry.metrics.repos} public repos · ${telemetry.metrics.bytesCompact} source bytes</span>`;
      return;
    }
    const found = telemetry.langs5d.find((l) => l.name === selectedName);
    if (found) {
      radarReadout.innerHTML = `<span><strong>${found.name}</strong> · ${found.bytesCompact} (${found.percentExact}%) · ${found.repos} repo${found.repos === 1 ? "" : "s"}</span><span>D4 Gravity ${found.d4Gravity.toFixed(2)} · D5 Phase ${found.d5Velocity.toFixed(2)}</span>`;
    }
  };

  const radarStage = new Radar5DStage(document.getElementById("radar-canvas"), telemetry.langs5d, (sel) => {
    updateRadarReadout(sel);
    langPillsWrap.querySelectorAll("button").forEach((b) => {
      b.classList.toggle("is-active", (b.dataset.lang || null) === sel || (!sel && b.dataset.lang === ""));
    });
  });
  updateRadarReadout(null);

  const allBtn = document.createElement("button");
  allBtn.type = "button";
  allBtn.className = "chip-btn is-active";
  allBtn.dataset.lang = "";
  allBtn.textContent = "All 6";
  allBtn.addEventListener("click", () => radarStage.setSelected(null));
  langPillsWrap.appendChild(allBtn);

  telemetry.langs5d.forEach((l) => {
    const b = document.createElement("button");
    b.type = "button";
    b.className = "chip-btn";
    b.dataset.lang = l.name;
    b.textContent = l.name;
    b.addEventListener("click", () => radarStage.setSelected(l.name));
    langPillsWrap.appendChild(b);
  });

  const wSlider = document.getElementById("w-fold-range");
  wSlider.addEventListener("input", () => {
    radarStage.setWFold(Number(wSlider.value));
  });

  const orbitToggle = document.getElementById("radar-orbit-btn");
  orbitToggle.addEventListener("click", () => {
    const on = radarStage.toggleOrbit();
    orbitToggle.setAttribute("aria-pressed", String(on));
    orbitToggle.textContent = on ? "5D Orbit: On" : "5D Orbit: Hold";
  });

  const metricCards = document.querySelectorAll(".metric-card");
  metricCards.forEach((card) => {
    card.addEventListener("click", () => {
      metricCards.forEach((c) => c.classList.toggle("is-active", c === card));
      const key = card.dataset.metric;
      if (key === "chars") radarStage.setSelected("HTML");
      else if (key === "commits") matrixStage.setFilter("radiant");
      else if (key === "stars") sky.triggerWave(0.68, 0.52);
      else matrixStage.setFilter("all");
    });
  });

  let eventsPool = telemetry.events || [];
  let activeRepoFilter = "all";
  let consoleState = "populated";
  const consoleList = document.getElementById("console-list");
  const repoFiltersWrap = document.getElementById("console-filters");

  const renderConsole = () => {
    consoleList.innerHTML = "";
    if (consoleState === "loading") {
      for (let i = 0; i < 4; i++) {
        const sk = document.createElement("div");
        sk.className = "skeleton-line";
        consoleList.appendChild(sk);
      }
      const note = document.createElement("span");
      note.className = "radar-subtitle";
      note.textContent = "Querying public GitHub push events for broamstuck-cybr…";
      consoleList.appendChild(note);
      return;
    }

    if (consoleState === "error") {
      const errPanel = document.createElement("div");
      errPanel.className = "state-panel";
      errPanel.innerHTML = "<strong>Live GitHub API rate-limited or unreachable.</strong><span>Cached snapshot remains intact; retry live fetch or restore snapshot.</span>";
      const restoreBtn = document.createElement("button");
      restoreBtn.type = "button";
      restoreBtn.className = "chip-btn is-active";
      restoreBtn.textContent = "Restore Verified Snapshot";
      restoreBtn.addEventListener("click", () => {
        consoleState = "populated";
        renderConsole();
      });
      errPanel.appendChild(restoreBtn);
      consoleList.appendChild(errPanel);
      return;
    }

    const filtered = activeRepoFilter === "all"
      ? eventsPool
      : eventsPool.filter((ev) => ev.repo.toLowerCase() === activeRepoFilter.toLowerCase());

    if (!filtered.length) {
      const emptyPanel = document.createElement("div");
      emptyPanel.className = "state-panel";
      emptyPanel.innerHTML = `<strong>No recent commits match repository filter "${activeRepoFilter}".</strong><span>Reset the filter to view all verified public push events.</span>`;
      const resetBtn = document.createElement("button");
      resetBtn.type = "button";
      resetBtn.className = "chip-btn is-active";
      resetBtn.textContent = "Show All Commits";
      resetBtn.addEventListener("click", () => {
        activeRepoFilter = "all";
        repoFiltersWrap.querySelectorAll("button[data-repo]").forEach((b) => {
          b.classList.toggle("is-active", b.dataset.repo === "all");
        });
        renderConsole();
      });
      emptyPanel.appendChild(resetBtn);
      consoleList.appendChild(emptyPanel);
      return;
    }

    filtered.slice(0, 5).forEach((ev) => {
      const row = document.createElement("a");
      row.className = "console-row";
      row.href = ev.url || `https://github.com/${telemetry.username}/${ev.repo}`;
      row.target = "_blank";
      row.rel = "noopener noreferrer";

      const tSpan = document.createElement("span");
      tSpan.className = "console-time";
      tSpan.textContent = ev.time;

      const sSpan = document.createElement("span");
      sSpan.className = "console-sha";
      sSpan.textContent = ev.sha;

      const rSpan = document.createElement("span");
      rSpan.className = "console-repo";
      rSpan.textContent = ev.repo;

      const mSpan = document.createElement("span");
      mSpan.className = "console-msg";
      mSpan.textContent = ev.message;

      row.append(tSpan, sSpan, rSpan, mSpan);
      consoleList.appendChild(row);
    });
  };

  const repoNames = ["all", "broamstuck-cybr", "f_forumv3", "resourcepack", "Socratic"];
  repoNames.forEach((rName) => {
    const b = document.createElement("button");
    b.type = "button";
    b.className = `chip-btn${rName === "all" ? " is-active" : ""}`;
    b.dataset.repo = rName;
    b.textContent = rName === "all" ? "All Repos" : rName;
    b.addEventListener("click", () => {
      activeRepoFilter = rName;
      consoleState = "populated";
      repoFiltersWrap.querySelectorAll("button[data-repo]").forEach((btn) => {
        btn.classList.toggle("is-active", btn === b);
      });
      renderConsole();
    });
    repoFiltersWrap.appendChild(b);
  });

  document.getElementById("console-sync-btn").addEventListener("click", async () => {
    consoleState = "loading";
    renderConsole();
    try {
      const res = await fetch(`https://api.github.com/users/${telemetry.username}/events/public?per_page=30`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const rawEvents = await res.json();
      const fresh = [];
      const seen = new Set();
      for (const ev of rawEvents) {
        if (ev.type !== "PushEvent" || !ev.payload || !ev.payload.commits) continue;
        for (const c of [...ev.payload.commits].reverse()) {
          const sha = (c.sha || "").slice(0, 7);
          if (!sha || seen.has(sha)) continue;
          seen.add(sha);
          const repoShort = ((ev.repo && ev.repo.name) || "").split("/").pop();
          fresh.push({
            sha,
            repo: repoShort,
            message: (c.message || "").split("\n")[0],
            time: (ev.created_at || "").slice(11, 16) || "--:--",
            url: `https://github.com/${telemetry.username}/${repoShort}/commit/${c.sha}`
          });
        }
      }
      if (fresh.length) eventsPool = fresh;
      consoleState = "populated";
      renderConsole();
    } catch {
      consoleState = "error";
      renderConsole();
    }
  });

  renderConsole();

  const cardStages = {
    v3: new Forum3DStage(document.getElementById("stage-v3"), "v3"),
    v2: new Forum3DStage(document.getElementById("stage-v2"), "v2"),
    v1: new Forum3DStage(document.getElementById("stage-v1"), "v1")
  };

  document.querySelectorAll("[data-wire-toggle]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const id = btn.dataset.wireToggle;
      const isWire = cardStages[id].toggleWireframe();
      btn.textContent = isWire ? "Solid" : "Wire";
    });
  });

  const modal = document.getElementById("stage-modal");
  const modalTitle = document.getElementById("modal-title");
  const modalDesc = document.getElementById("modal-desc");
  const modalLiveLink = document.getElementById("modal-live-link");
  const modalStage = new Forum3DStage(document.getElementById("modal-3d-canvas"), "v3", { width: 880, height: 495, zoom: 1.12 });

  document.querySelectorAll("[data-expand-3d]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const id = btn.getAttribute("data-expand-3d");
      const meta = (telemetry.forums || []).find((f) => f.id === id) || telemetry.forums[0];
      modalTitle.textContent = `${meta.title} — 360° Architectural Model`;
      modalDesc.textContent = meta.summary;
      modalLiveLink.href = meta.liveUrl;
      modalLiveLink.textContent = meta.id === "v2" ? "Open Bridge Repository" : `Open ${meta.domain}`;
      modalStage.setVariant(id);
      if (typeof modal.showModal === "function") {
        modal.showModal();
      } else {
        modal.setAttribute("open", "");
      }
    });
  });

  document.querySelectorAll("[data-cam-preset]").forEach((btn) => {
    btn.addEventListener("click", () => {
      modalStage.setCameraPreset(btn.dataset.camPreset);
    });
  });

  document.getElementById("modal-wire-btn").addEventListener("click", (ev) => {
    const w = modalStage.toggleWireframe();
    ev.currentTarget.textContent = w ? "Sculpted Mode" : "Blueprint Wire";
  });

  document.getElementById("modal-close-btn").addEventListener("click", () => {
    if (typeof modal.close === "function") modal.close();
    else modal.removeAttribute("open");
  });
}

initObservatory();
