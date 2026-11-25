// SPDX-License-Identifier: MIT
// WHY: Coordinates the calligraphic Van Gogh sky/garden engine, sculpted contribution constellation, 4K portrait, stack crystal, 4-state console, and Blender 3D stages.

import { LiquidStarrySky } from "./sky-engine.js";
import { PortraitStage, Radar5DStage, Forum3DStage } from "./models-3d.js";

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

function drawStarPolygon(ctx, cx, cy, outerR, innerR, points = 6, rot = -Math.PI * 0.5) {
  ctx.beginPath();
  const total = points * 2;
  for (let i = 0; i < total; i++) {
    const a = rot + (i * Math.PI) / points;
    const r = i % 2 === 0 ? outerR : innerR;
    const px = cx + Math.cos(a) * r;
    const py = cy + Math.sin(a) * r;
    if (i === 0) ctx.moveTo(px, py);
    else ctx.lineTo(px, py);
  }
  ctx.closePath();
}

class CelestialMatrixStage {
  constructor(canvas, telemetry, vgSky, onDayHover) {
    this.canvas = canvas;
    this.ctx = canvas.getContext("2d", { alpha: false });
    this.daysMap = telemetry.days || {};
    this.weeks52 = (telemetry.streaks && telemetry.streaks.weeks52) || [];
    this.vgSky = vgSky;
    this.onDayHover = onDayHover;
    this.pointerX = 560;
    this.selectedIdx = -1;
    this.cells = [];
    this.time = 0;
    this.mqReduced = window.matchMedia("(prefers-reduced-motion: reduce)");
    this.reducedMotion = this.mqReduced.matches;
    this._looping = false;

    this.w = 1120;
    this.h = 206;
    this.dpr = Math.min(window.devicePixelRatio || 1, 2);
    this.canvas.width = Math.round(this.w * this.dpr);
    this.canvas.height = Math.round(this.h * this.dpr);
    this.ctx.setTransform(this.dpr, 0, 0, this.dpr, 0, 0);

    this._bakeUnderlay();
    this._buildCells();
    this._bindEvents();
    this.render();
    if (!this.reducedMotion) {
      this._loop();
    }
  }

  // WHY: Renders full 3-layer calligraphic Starry Night impasto (oil bg + structure-tensor strokes + glyph weave) beneath a nocturnal glaze so zero hollow scribble loops appear while preserving star contrast.
  _bakeUnderlay() {
    const c = document.createElement("canvas");
    c.width = Math.max(1, Math.round(this.w * this.dpr));
    c.height = Math.max(1, Math.round(this.h * this.dpr));
    const lc = c.getContext("2d", { alpha: false });
    lc.setTransform(this.dpr, 0, 0, this.dpr, 0, 0);
    lc.fillStyle = "#040916";
    lc.fillRect(0, 0, this.w, this.h);

    if (this.vgSky) {
      const cols = Math.max(1, this.vgSky.cols || 160);
      const rows = Math.max(1, this.vgSky.rows || 56);
      const rowStep = this.h / rows;
      const colStep = this.w / cols;

      const bgRows = this.vgSky.bg || [];
      lc.globalAlpha = 0.72;
      for (let r = 0; r < bgRows.length; r++) {
        let xCur = 0;
        const runs = bgRows[r];
        const ry = r * rowStep;
        const rh = rowStep + 0.8;
        for (let k = 0; k < runs.length; k++) {
          const [bCol, bLen] = runs[k];
          lc.fillStyle = bCol;
          lc.fillRect(xCur * colStep, ry, bLen * colStep + 0.8, rh);
          xCur += bLen;
        }
      }

      const strokes = this.vgSky.strokes || [];
      lc.lineCap = "round";
      lc.globalAlpha = 0.76;
      for (let i = 0; i < strokes.length; i++) {
        const [x0, y0, xm, ym, x1, y1, col, sw] = strokes[i];
        lc.strokeStyle = col;
        lc.lineWidth = sw * 1.45;
        lc.beginPath();
        lc.moveTo(x0 * this.w, y0 * this.h);
        lc.quadraticCurveTo(xm * this.w, ym * this.h, x1 * this.w, y1 * this.h);
        lc.stroke();
      }

      const grid = this.vgSky.grid || [];
      const monoFamily = "'JetBrains Mono', ui-monospace, monospace";
      lc.font = `700 20px ${monoFamily}`;
      const unitAdv = (lc.measureText("MMMMMMMMMM").width / 200) || 0.6;
      const fontSz = Math.max(1.8, colStep / unitAdv);
      lc.font = `700 ${fontSz.toFixed(3)}px ${monoFamily}`;
      lc.textBaseline = "alphabetic";
      lc.globalAlpha = 0.78;
      for (let r = 0; r < grid.length; r++) {
        let cur = 0;
        const runs = grid[r];
        const py = (r + 0.82) * rowStep;
        for (let k = 0; k < runs.length; k++) {
          const [colHex, chunk] = runs[k];
          if (colHex) {
            lc.fillStyle = colHex;
            lc.fillText(chunk, cur * colStep, py);
          }
          cur += chunk.length;
        }
      }

      lc.globalAlpha = 1;
      lc.fillStyle = "rgba(4, 9, 22, 0.56)";
      lc.fillRect(0, 0, this.w, this.h);

      const topScrim = lc.createLinearGradient(0, 0, 0, 28);
      topScrim.addColorStop(0, "rgba(4, 9, 22, 0.62)");
      topScrim.addColorStop(1, "rgba(4, 9, 22, 0)");
      lc.fillStyle = topScrim;
      lc.fillRect(0, 0, this.w, 28);

      const leftScrim = lc.createLinearGradient(0, 0, 56, 0);
      leftScrim.addColorStop(0, "rgba(4, 9, 22, 0.64)");
      leftScrim.addColorStop(1, "rgba(4, 9, 22, 0)");
      lc.fillStyle = leftScrim;
      lc.fillRect(0, 0, 56, this.h);
    }
    this.underlay = c;
  }

  _buildCells() {
    const dates = Object.keys(this.daysMap).sort();
    const lastIso = dates.length ? dates[dates.length - 1] : "2026-11-25";
    const endDay = new Date(lastIso + "T00:00:00Z");
    const dow = endDay.getUTCDay();
    const endSunday = new Date(endDay.getTime() - dow * 86400000);
    const startSunday = new Date(endSunday.getTime() - 51 * 7 * 86400000);

    const gx = 54;
    const gy = 34;
    const px = 20.1;
    const py = 18.8;

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
          count
        });
      }
    }
    let activeIdx = this.cells.length - 1;
    for (let i = this.cells.length - 1; i >= 0; i--) {
      if (this.cells[i].count > 0) {
        activeIdx = i;
        break;
      }
    }
    this.selectedIdx = activeIdx;
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

    this.mqReduced.addEventListener("change", (e) => {
      this.reducedMotion = e.matches;
      if (!this.reducedMotion) this._loop();
      else this.render();
    });
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
    if (this._looping) return;
    this._looping = true;
    const step = () => {
      if (this.reducedMotion) {
        this._looping = false;
        return;
      }
      const r = this.canvas.getBoundingClientRect();
      if (r.width > 0 && r.bottom >= -80 && r.top <= (window.innerHeight || 900) + 80) {
        this.time += 0.02;
        this.render();
      }
      requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }

  render() {
    const ctx = this.ctx;
    ctx.drawImage(this.underlay, 0, 0, this.w, this.h);

    ctx.font = "600 10.5px 'Inter', system-ui, sans-serif";
    ctx.fillStyle = "#c5d4ea";
    ctx.textAlign = "center";
    for (let i = 0; i < this.monthLabels.length; i++) {
      ctx.fillText(this.monthLabels[i].text, this.monthLabels[i].x, 16);
    }

    ctx.font = "500 10px 'JetBrains Mono', ui-monospace, monospace";
    ctx.fillStyle = "#8fa5c4";
    ctx.textAlign = "right";
    const rowDays = [[1, "Mon"], [3, "Wed"], [5, "Fri"]];
    for (let i = 0; i < rowDays.length; i++) {
      ctx.fillText(rowDays[i][1], 38, 38 + rowDays[i][0] * 18.8);
    }

    const coordKey = new Map();
    for (let i = 0; i < this.cells.length; i++) {
      const c = this.cells[i];
      coordKey.set(`${c.w}:${c.r}`, c);
    }

    for (let i = 0; i < this.cells.length; i++) {
      const c = this.cells[i];
      if (c.count < 2) continue;
      const down = coordKey.get(`${c.w}:${c.r + 1}`);
      if (down && down.count >= 2) {
        ctx.strokeStyle = (c.count + down.count) >= 22 ? "rgba(253, 224, 71, 0.50)" : "rgba(125, 211, 252, 0.36)";
        ctx.lineWidth = 1.1;
        ctx.beginPath();
        ctx.moveTo(c.x, c.y);
        ctx.lineTo(down.x, down.y);
        ctx.stroke();
      }
      const right = coordKey.get(`${c.w + 1}:${c.r}`);
      if (right && right.count >= 4 && c.count >= 4) {
        ctx.strokeStyle = "rgba(94, 234, 212, 0.36)";
        ctx.lineWidth = 1.0;
        ctx.beginPath();
        ctx.moveTo(c.x, c.y);
        ctx.lineTo(right.x, right.y);
        ctx.stroke();
      }
    }

    for (let i = 0; i < this.cells.length; i++) {
      const c = this.cells[i];
      if (c.count === 0) {
        ctx.strokeStyle = "#243b63";
        ctx.lineWidth = 0.85;
        ctx.beginPath();
        ctx.moveTo(c.x - 1.7, c.y);
        ctx.lineTo(c.x + 1.7, c.y);
        ctx.moveTo(c.x, c.y - 1.7);
        ctx.lineTo(c.x, c.y + 1.7);
        ctx.stroke();
      } else if (c.count <= 4) {
        drawStarPolygon(ctx, c.x, c.y, 4.2, 1.5, 4);
        ctx.fillStyle = "#7dd3fc";
        ctx.fill();
      } else if (c.count <= 19) {
        drawStarPolygon(ctx, c.x, c.y, 5.4, 2.0, 6, this.time * 0.25 + i);
        ctx.fillStyle = "#34d399";
        ctx.fill();
      } else {
        ctx.save();
        ctx.translate(c.x, c.y);
        ctx.rotate(this.time * 0.35 + i);
        ctx.strokeStyle = "rgba(253, 224, 71, 0.82)";
        ctx.lineWidth = 1.05;
        ctx.setLineDash([3, 2.2]);
        ctx.beginPath();
        ctx.arc(0, 0, 7.6, 0, Math.PI * 2);
        ctx.stroke();
        ctx.restore();
        drawStarPolygon(ctx, c.x, c.y, 6.6, 2.4, 8, -this.time * 0.25);
        ctx.fillStyle = "#fde047";
        ctx.fill();
      }
    }

    if (this.selectedIdx >= 0 && this.cells[this.selectedIdx]) {
      const sel = this.cells[this.selectedIdx];
      ctx.strokeStyle = "#fde047";
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.arc(sel.x, sel.y, 8.8, 0, Math.PI * 2);
      ctx.stroke();
    }

    const waterY = 169;
    ctx.strokeStyle = "rgba(125, 211, 252, 0.34)";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(36, waterY);
    ctx.lineTo(this.w - 24, waterY);
    ctx.stroke();

    ctx.font = "700 9.5px 'JetBrains Mono', ui-monospace, monospace";
    ctx.textAlign = "center";
    const maxW = Math.max(1, ...this.weeks52);
    for (let w = 0; w < 52; w++) {
      const val = this.weeks52[w] || 0;
      if (val <= 0) continue;
      const norm = Math.pow(val / maxW, 0.62);
      const wx = 54 + w * 20.1;
      const cursorBoost = Math.exp(-Math.pow((wx - this.pointerX) / 90, 2)) * 0.35;
      const shift = Math.sin(this.time * 1.6 + w * 0.5) * 2.2;
      ctx.globalAlpha = Math.min(0.95, 0.36 + norm * 0.48 + cursorBoost);
      ctx.fillStyle = norm > 0.45 ? "#fde047" : "#7dd3fc";
      ctx.fillText(norm > 0.55 ? "≈~≈" : "~~", wx + shift, waterY + 17 + (w % 2) * 6);
    }
    ctx.globalAlpha = 1;
  }
}

async function fetchJson(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

async function initObservatory() {
  let telemetry;
  let portraitData;
  let vgScene;
  let modelsBundle;

  try {
    [telemetry, portraitData, vgScene, modelsBundle] = await Promise.all([
      fetchJson("assets/telemetry.json"),
      fetchJson("assets/portrait_hd.json"),
      fetchJson("assets/vangogh_scene.json"),
      fetchJson("assets/models_3d.json")
    ]);
  } catch (err) {
    const list = document.getElementById("console-list");
    list.innerHTML = "";
    const panel = document.createElement("div");
    panel.className = "state-panel";
    panel.innerHTML = `<strong>Observatory data bundle unavailable (${err.message}).</strong><span>Verify assets/*.json or retry loading.</span>`;
    const retry = document.createElement("button");
    retry.type = "button";
    retry.className = "chip-btn is-active";
    retry.textContent = "Retry";
    retry.addEventListener("click", () => window.location.reload());
    panel.appendChild(retry);
    list.appendChild(panel);
    return;
  }

  const skyHud = document.getElementById("sky-hud");
  const skyReadout = document.getElementById("sky-readout");
  const sky = new LiquidStarrySky(
    document.getElementById("sky-canvas"),
    document.getElementById("panorama-canvas"),
    document.getElementById("garden-canvas"),
    vgScene,
    (bodyText) => {
      skyReadout.textContent = bodyText;
      if (skyHud) skyHud.hidden = !bodyText;
    }
  );

  document.getElementById("mat-total").textContent = Number(telemetry.metrics.contributions).toLocaleString("en-US");
  document.getElementById("mat-streak").textContent = `${telemetry.streaks.longest}d`;
  document.getElementById("val-chars").textContent = telemetry.metrics.bytesCompact;
  document.getElementById("val-commits").textContent = Number(telemetry.metrics.commits).toLocaleString("en-US");
  document.getElementById("val-stars").textContent = String(telemetry.metrics.stars);
  document.getElementById("val-contribs").textContent = Number(telemetry.metrics.contributions).toLocaleString("en-US");

  const matInspector = document.getElementById("matrix-inspector");
  const matrixStage = new CelestialMatrixStage(
    document.getElementById("matrix-canvas"),
    telemetry,
    vgScene.sky || vgScene.panorama,
    (cell) => {
      matInspector.textContent = `${cell.iso} · ${cell.count}`;
    }
  );
  matrixStage._emitSelected();
  const matScroll = document.querySelector(".matrix-scroll");
  if (matScroll) {
    matScroll.scrollLeft = matScroll.scrollWidth;
  }

  new PortraitStage(document.getElementById("portrait-canvas"), portraitData);

  const radarReadout = document.getElementById("radar-readout");
  const updateRadarReadout = (selectedName) => {
    if (!selectedName) {
      radarReadout.innerHTML = `${telemetry.metrics.repos} repos &middot; ${telemetry.metrics.bytesCompact}`;
      return;
    }
    const found = telemetry.langs5d.find((l) => l.name === selectedName);
    if (found) {
      radarReadout.innerHTML = `<strong>${found.name}</strong> &middot; ${found.bytesCompact} (${found.percentExact}%) &middot; ${found.repos} repos`;
    }
  };

  const radarStage = new Radar5DStage(document.getElementById("radar-canvas"), telemetry.langs5d, updateRadarReadout);
  updateRadarReadout(null);

  const metricCards = document.querySelectorAll(".metric-card");
  metricCards.forEach((card) => {
    card.addEventListener("click", () => {
      metricCards.forEach((c) => c.classList.toggle("is-active", c === card));
      const key = card.dataset.metric;
      if (key === "chars") radarStage.setSelected("HTML");
      else if (key === "stars") sky.focusBody("sun");
      else radarStage.setSelected(null);
    });
  });

  const snapshotEvents = Array.isArray(telemetry.events) ? [...telemetry.events] : [];
  let eventsPool = [...snapshotEvents];
  let consoleState = eventsPool.length ? "populated" : "empty";
  const consoleList = document.getElementById("console-list");

  const restoreSnapshot = () => {
    eventsPool = [...snapshotEvents];
    consoleState = eventsPool.length ? "populated" : "empty";
    renderConsole();
  };

  const renderConsole = () => {
    consoleList.innerHTML = "";
    if (consoleState === "loading") {
      for (let i = 0; i < 4; i++) {
        const sk = document.createElement("div");
        sk.className = "skeleton-line";
        consoleList.appendChild(sk);
      }
      const note = document.createElement("span");
      note.className = "radar-readout";
      note.textContent = "Syncing public GitHub events…";
      consoleList.appendChild(note);
      return;
    }

    if (consoleState === "error") {
      const errPanel = document.createElement("div");
      errPanel.className = "state-panel";
      errPanel.innerHTML = "<strong>GitHub API rate-limited or offline.</strong><span>Restore verified local snapshot.</span>";
      const restoreBtn = document.createElement("button");
      restoreBtn.type = "button";
      restoreBtn.className = "chip-btn is-active";
      restoreBtn.textContent = "Restore Snapshot";
      restoreBtn.addEventListener("click", restoreSnapshot);
      errPanel.appendChild(restoreBtn);
      consoleList.appendChild(errPanel);
      return;
    }

    if (consoleState === "empty" || !eventsPool.length) {
      const emptyPanel = document.createElement("div");
      emptyPanel.className = "state-panel";
      emptyPanel.innerHTML = "<strong>No recent public push events.</strong><span>Restore verified local snapshot or sync again.</span>";
      const resetBtn = document.createElement("button");
      resetBtn.type = "button";
      resetBtn.className = "chip-btn is-active";
      resetBtn.textContent = "Restore Snapshot";
      resetBtn.addEventListener("click", restoreSnapshot);
      emptyPanel.appendChild(resetBtn);
      consoleList.appendChild(emptyPanel);
      return;
    }

    eventsPool.slice(0, 5).forEach((ev) => {
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
        if (ev.type !== "PushEvent" || !ev.payload) continue;
        const repoShort = ((ev.repo && ev.repo.name) || "").split("/").pop();
        const commitsArr = Array.isArray(ev.payload.commits) && ev.payload.commits.length
          ? [...ev.payload.commits].reverse()
          : (ev.payload.head ? [{ sha: ev.payload.head, message: `push to ${(ev.payload.ref || "main").replace("refs/heads/", "")}` }] : []);
        for (const c of commitsArr) {
          const sha = (c.sha || "").slice(0, 7);
          if (!sha || seen.has(sha)) continue;
          seen.add(sha);
          fresh.push({
            sha,
            repo: repoShort,
            message: (c.message || "").split("\n")[0],
            time: (ev.created_at || "").slice(11, 16) || "--:--",
            url: `https://github.com/${telemetry.username}/${repoShort}/commit/${c.sha}`
          });
        }
      }
      eventsPool = fresh;
      consoleState = fresh.length ? "populated" : "empty";
      renderConsole();
    } catch {
      consoleState = "error";
      renderConsole();
    }
  });

  renderConsole();

  const cardSky = vgScene.sky || vgScene.panorama;
  new Forum3DStage(document.getElementById("stage-v3"), "v3", modelsBundle, cardSky, { yaw: 0.50 });
  new Forum3DStage(document.getElementById("stage-v2"), "v2", modelsBundle, cardSky, { yaw: 0.43 });
  new Forum3DStage(document.getElementById("stage-v1"), "v1", modelsBundle, cardSky, { yaw: 0.40, pitch: 0.38 });

  const modal = document.getElementById("stage-modal");
  const modalTitle = document.getElementById("modal-title");
  const modalDesc = document.getElementById("modal-desc");
  const modalLiveLink = document.getElementById("modal-live-link");
  const modalExplodeRange = document.getElementById("modal-explode-range");
  const modalVariantBtns = document.querySelectorAll("[data-modal-variant]");
  const modalStage = new Forum3DStage(
    document.getElementById("modal-3d-canvas"),
    "v3",
    modelsBundle,
    cardSky,
    { width: 880, height: 495, zoom: 1.12 }
  );

  const openModalVariant = (id) => {
    const meta = (telemetry.forums || []).find((f) => f.id === id) || telemetry.forums[0];
    modalTitle.textContent = `${meta.title} — 360° Stage`;
    modalDesc.textContent = meta.summary;
    modalLiveLink.href = meta.liveUrl;
    modalLiveLink.textContent = meta.domain ? `Open ${meta.domain}` : "Open Repository";
    modalExplodeRange.value = "0";
    modalStage.setExplode(0);
    modalStage.setVariant(id);
    modalVariantBtns.forEach((b) => b.classList.toggle("is-active", b.dataset.modalVariant === id));
  };

  document.querySelectorAll("[data-expand-3d]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const id = btn.getAttribute("data-expand-3d");
      if (typeof modal.showModal === "function") modal.showModal();
      else modal.setAttribute("open", "");
      openModalVariant(id);
    });
  });

  modalVariantBtns.forEach((btn) => {
    btn.addEventListener("click", () => openModalVariant(btn.dataset.modalVariant));
  });

  modalExplodeRange.addEventListener("input", () => {
    modalStage.setExplode(Number(modalExplodeRange.value));
  });

  document.getElementById("modal-wire-btn").addEventListener("click", (ev) => {
    const w = modalStage.toggleWireframe();
    ev.currentTarget.classList.toggle("is-active", w);
    ev.currentTarget.textContent = w ? "Solid" : "Wire";
  });

  document.getElementById("modal-close-btn").addEventListener("click", () => {
    if (typeof modal.close === "function") modal.close();
    else modal.removeAttribute("open");
  });

  modal.addEventListener("click", (ev) => {
    if (ev.target === modal) {
      if (typeof modal.close === "function") modal.close();
      else modal.removeAttribute("open");
    }
  });
}

initObservatory();
