// SPDX-License-Identifier: MIT
// WHY: Coordinates the calligraphic Van Gogh sky/garden engine, sculpted contribution constellation, 4K portrait, stack crystal, 4-state console, and Blender 3D stages.

import { LiquidStarrySky, drawTaperedImpastoStroke } from "./sky-engine.js";
import { PortraitStage as LegacyPortraitStage, Radar5DStage, Forum3DStage } from "./models-3d.js";
import { StarlightPixelDog } from "./pixel-dog.js";

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

// WHY: Bakes the 4-plane pure-vector painterly portrait (sky, Guan Yu meadow, railing, subject) onto offscreen canvases at dpr<=2 for 60 FPS parallax.
class PortraitStage {
  constructor(canvas, portraitData) {
    if (!portraitData || !portraitData.vector_layers) {
      return new LegacyPortraitStage(canvas, portraitData);
    }
    this.canvas = canvas;
    this.ctx = canvas.getContext("2d");
    this.data = portraitData;
    this.mqReduced = window.matchMedia("(prefers-reduced-motion: reduce)");
    this.reducedMotion = this.mqReduced.matches;
    this.pointer = { nx: 0.5, ny: 0.5, inside: false };
    this.gaze = { tx: 0, ty: 0, x: 0, y: 0 };
    this.angle = 0;
    this._visible = true;
    this._looping = false;

    this.dpr = Math.min(window.devicePixelRatio || 1, 2);
    const baseCss = Math.max(200, Math.min(460, Math.round(canvas.clientWidth || 324)));
    this.size = Math.round(baseCss * this.dpr);
    this.canvas.width = this.size;
    this.canvas.height = this.size;

    this.layers = [0, 1, 2, 3].map(() => {
      const c = document.createElement("canvas");
      c.width = this.size;
      c.height = this.size;
      return c;
    });
    this.composite = document.createElement("canvas");
    this.composite.width = this.size;
    this.composite.height = this.size;

    this._bakeLayers();
    this._bindEvents();
    this.render();
    if (!this.reducedMotion) {
      this._animate();
    }
  }

  _bakeLayers() {
    const sz = this.size;
    const cx = sz * 0.5;
    const cy = sz * 0.5;
    const r = sz * 0.464;
    const diam = r * 2;
    const x0 = cx - r;
    const y0 = cy - r;

    const ctxs = this.layers.map((c) => {
      const lc = c.getContext("2d");
      lc.clearRect(0, 0, sz, sz);
      return lc;
    });

    const coordSz = this.data.coord_size || 2000;
    const scale = diam / coordSz;
    ctxs[0].fillStyle = this.data.bg_fill || "#081833";
    ctxs[0].fillRect(0, 0, sz, sz);

    const vl = this.data.vector_layers || {};
    const specs = [
      ["sky_polys", false],
      ["sky_strokes", true],
      ["meadow_polys", false],
      ["meadow_strokes", true],
      ["rail_polys", false],
      ["subject_polys", false],
      ["subject_strokes", true]
    ];

    for (let s = 0; s < specs.length; s++) {
      const [lname, isStroke] = specs[s];
      const arr = vl[lname] || [];
      for (let i = 0; i < arr.length; i++) {
        const it = arr[i];
        const lc = ctxs[Math.min(3, Math.max(0, Number(it.plane || 0)))];
        lc.save();
        lc.translate(x0, y0);
        lc.scale(scale, scale);
        const p2d = new Path2D(it.d);
        if (!isStroke) {
          lc.globalAlpha = it.opacity ?? 1;
          lc.fillStyle = it.fill;
          lc.fill(p2d, it.rule || "nonzero");
          if (it.seam) {
            lc.strokeStyle = it.fill;
            lc.lineWidth = it.seam;
            lc.lineJoin = "round";
            lc.stroke(p2d);
          }
        } else {
          lc.globalAlpha = it.opacity ?? 0.84;
          lc.strokeStyle = it.stroke;
          lc.lineWidth = it.width || 3;
          lc.lineCap = it.cap || "round";
          lc.lineJoin = "round";
          lc.stroke(p2d);
        }
        lc.restore();
      }
    }
    ctxs.forEach((lc) => { lc.globalAlpha = 1; });
  }

  _bindEvents() {
    this.mqReduced.addEventListener("change", (e) => {
      this.reducedMotion = e.matches;
      if (!this.reducedMotion) this._animate();
      else this.render();
    });

    if (typeof IntersectionObserver === "function") {
      const io = new IntersectionObserver((entries) => {
        if (entries[0]) this._visible = entries[0].isIntersecting;
      }, { rootMargin: "90px 0px" });
      io.observe(this.canvas);
    }

    window.addEventListener("pointermove", (ev) => {
      const rect = this.canvas.getBoundingClientRect();
      const cx = rect.left + rect.width * 0.5;
      const cy = rect.top + rect.height * 0.5;
      this.gaze.tx = Math.max(-1, Math.min(1, (ev.clientX - cx) / 380));
      this.gaze.ty = Math.max(-1, Math.min(1, (ev.clientY - cy) / 380));
      if (this.reducedMotion) {
        this.gaze.x = this.gaze.tx;
        this.gaze.y = this.gaze.ty;
        this.render();
      }
    }, { passive: true });

    const updateLocal = (ev) => {
      const rect = this.canvas.getBoundingClientRect();
      const nx = (ev.clientX - rect.left) / Math.max(1, rect.width);
      const ny = (ev.clientY - rect.top) / Math.max(1, rect.height);
      const dist = Math.hypot(nx - 0.5, ny - 0.5);
      this.pointer = { nx, ny, inside: dist <= 0.455 };
      if (this.reducedMotion) this.render();
    };
    this.canvas.addEventListener("pointermove", updateLocal);
    this.canvas.addEventListener("pointerdown", updateLocal);
    this.canvas.addEventListener("pointerleave", () => {
      this.pointer.inside = false;
      if (this.reducedMotion) this.render();
    });
  }

  _animate() {
    if (this._looping) return;
    this._looping = true;
    let last = performance.now();
    const step = (now) => {
      if (this.reducedMotion) {
        this._looping = false;
        return;
      }
      const dt = Math.min(0.05, Math.max(0.001, (now - last) / 1000));
      last = now;
      if (this._visible) {
        this.angle += dt * 0.24;
        const k = Math.min(1, dt * 6.5);
        this.gaze.x += (this.gaze.tx - this.gaze.x) * k;
        this.gaze.y += (this.gaze.ty - this.gaze.y) * k;
        this.render();
      }
      requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }

  render() {
    const ctx = this.ctx;
    const sz = this.size;
    const cx = sz * 0.5;
    const cy = sz * 0.5;
    const r = sz * 0.464;
    const u = sz / 1240;

    ctx.clearRect(0, 0, sz, sz);

    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(this.angle * 0.30);
    for (let deg = 0; deg < 360; deg += 15) {
      const rad = (deg * Math.PI) / 180;
      const r0 = r + 9 * u;
      const r1 = r + (deg % 45 === 0 ? 25 : 15) * u;
      ctx.strokeStyle = deg % 90 === 0 ? "rgba(254, 240, 138, 0.90)" : "rgba(125, 211, 252, 0.44)";
      ctx.lineWidth = (deg % 45 === 0 ? 2.7 : 1.5) * u;
      ctx.beginPath();
      ctx.moveTo(Math.cos(rad) * r0, Math.sin(rad) * r0);
      ctx.lineTo(Math.cos(rad) * r1, Math.sin(rad) * r1);
      ctx.stroke();
    }
    const satA = this.angle * 1.4;
    drawStarPolygon(ctx, Math.cos(satA) * (r + 20 * u), Math.sin(satA) * (r + 20 * u), 10.0 * u, 3.6 * u, 4, satA);
    ctx.fillStyle = "#fde047";
    ctx.fill();
    ctx.restore();

    const dxNorm = this.pointer.inside ? (this.pointer.nx - 0.5) * 1.35 : this.gaze.x * 0.62;
    const dyNorm = this.pointer.inside ? (this.pointer.ny - 0.5) * 1.35 : this.gaze.y * 0.52;

    if (
      this._compDx === undefined ||
      Math.hypot(dxNorm - this._compDx, dyNorm - this._compDy) > 0.002
    ) {
      this._compDx = dxNorm;
      this._compDy = dyNorm;
      const compCtx = this.composite.getContext("2d");
      compCtx.clearRect(0, 0, sz, sz);
      compCtx.save();
      compCtx.beginPath();
      compCtx.arc(cx, cy, r, 0, Math.PI * 2);
      compCtx.clip();
      const shifts = [-7.0 * u, 2.5 * u, 8.5 * u, 14.5 * u];
      for (let p = 0; p < 4; p++) {
        compCtx.drawImage(this.layers[p], dxNorm * shifts[p], dyNorm * shifts[p]);
      }
      compCtx.restore();
    }

    ctx.drawImage(this.composite, 0, 0);

    if (this.pointer.inside) {
      const loupeR = 162 * u;
      const zoom = 2.25;
      const rawLx = this.pointer.nx * sz;
      const rawLy = this.pointer.ny * sz;
      const offX = rawLx - cx;
      const offY = rawLy - cy;
      const offDist = Math.hypot(offX, offY);
      const maxCenterDist = Math.max(0, r - loupeR - 8 * u);
      const clampedLx = offDist > maxCenterDist && offDist > 0 ? cx + (offX / offDist) * maxCenterDist : rawLx;
      const clampedLy = offDist > maxCenterDist && offDist > 0 ? cy + (offY / offDist) * maxCenterDist : rawLy;

      ctx.save();
      ctx.beginPath();
      ctx.arc(cx, cy, r - 2 * u, 0, Math.PI * 2);
      ctx.clip();

      ctx.beginPath();
      ctx.arc(clampedLx, clampedLy, loupeR, 0, Math.PI * 2);
      ctx.clip();
      ctx.fillStyle = "#081833";
      ctx.fillRect(clampedLx - loupeR, clampedLy - loupeR, loupeR * 2, loupeR * 2);
      ctx.drawImage(
        this.composite,
        rawLx - loupeR / zoom,
        rawLy - loupeR / zoom,
        (loupeR * 2) / zoom,
        (loupeR * 2) / zoom,
        clampedLx - loupeR,
        clampedLy - loupeR,
        loupeR * 2,
        loupeR * 2
      );
      ctx.restore();

      ctx.strokeStyle = "#fde047";
      ctx.lineWidth = 4.2 * u;
      ctx.beginPath();
      ctx.arc(clampedLx, clampedLy, loupeR, 0, Math.PI * 2);
      ctx.stroke();

      ctx.strokeStyle = "rgba(255, 255, 255, 0.55)";
      ctx.lineWidth = 1.6 * u;
      ctx.beginPath();
      ctx.arc(clampedLx, clampedLy, loupeR - 3 * u, -Math.PI * 0.85, -Math.PI * 0.25);
      ctx.stroke();
    }

    ctx.strokeStyle = "rgba(253, 230, 138, 0.78)";
    ctx.lineWidth = 4.0 * u;
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.stroke();

    ctx.strokeStyle = "rgba(254, 249, 195, 0.52)";
    ctx.lineWidth = 1.8 * u;
    ctx.beginPath();
    ctx.arc(cx, cy, r - 2.5 * u, -Math.PI * 0.86, -Math.PI * 0.18);
    ctx.stroke();
  }
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
    this.dpr = 1;
    this.canvas.width = this.w;
    this.canvas.height = this.h;
    this.ctx.setTransform(1, 0, 0, 1, 0, 0);

    this._buildCells();
    this._bakeUnderlay();
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
      for (let i = 0; i < strokes.length; i++) {
        const [x0, y0, xm, ym, x1, y1, col, sw] = strokes[i];
        drawTaperedImpastoStroke(
          lc,
          x0 * this.w,
          y0 * this.h,
          xm * this.w,
          ym * this.h,
          x1 * this.w,
          y1 * this.h,
          col,
          sw * 1.50,
          0.80
        );
      }

      const grid = this.vgSky.grid || [];
      const monoFamily = "'JetBrains Mono', ui-monospace, monospace";
      lc.font = `700 20px ${monoFamily}`;
      const unitAdv = (lc.measureText("MMMMMMMMMM").width / 200) || 0.6;
      const fontSz = Math.max(1.8, colStep / unitAdv);
      lc.font = `700 ${fontSz.toFixed(3)}px ${monoFamily}`;
      lc.textBaseline = "alphabetic";
      lc.globalAlpha = 0.80;
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
      lc.fillStyle = "rgba(4, 9, 22, 0.48)";
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

    lc.font = "600 10.5px 'Inter', system-ui, sans-serif";
    lc.fillStyle = "#c5d4ea";
    lc.textAlign = "center";
    for (let i = 0; i < this.monthLabels.length; i++) {
      lc.fillText(this.monthLabels[i].text, this.monthLabels[i].x, 16);
    }

    lc.font = "500 10px 'JetBrains Mono', ui-monospace, monospace";
    lc.fillStyle = "#8fa5c4";
    lc.textAlign = "right";
    const rowDays = [[1, "Mon"], [3, "Wed"], [5, "Fri"]];
    for (let i = 0; i < rowDays.length; i++) {
      lc.fillText(rowDays[i][1], 38, 38 + rowDays[i][0] * 18.8);
    }

    const coordKey = new Map();
    for (let i = 0; i < this.cells.length; i++) {
      const cell = this.cells[i];
      coordKey.set(`${cell.w}:${cell.r}`, cell);
    }
    for (let i = 0; i < this.cells.length; i++) {
      const cell = this.cells[i];
      if (cell.count < 2) continue;
      const down = coordKey.get(`${cell.w}:${cell.r + 1}`);
      if (down && down.count >= 2) {
        lc.strokeStyle = (cell.count + down.count) >= 22 ? "rgba(253, 224, 71, 0.50)" : "rgba(125, 211, 252, 0.36)";
        lc.lineWidth = 1.1;
        lc.beginPath();
        lc.moveTo(cell.x, cell.y);
        lc.lineTo(down.x, down.y);
        lc.stroke();
      }
      const right = coordKey.get(`${cell.w + 1}:${cell.r}`);
      if (right && right.count >= 4 && cell.count >= 4) {
        lc.strokeStyle = "rgba(94, 234, 212, 0.36)";
        lc.lineWidth = 1.0;
        lc.beginPath();
        lc.moveTo(cell.x, cell.y);
        lc.lineTo(right.x, right.y);
        lc.stroke();
      }
    }

    this.dynamicCells = [];
    for (let i = 0; i < this.cells.length; i++) {
      const cell = this.cells[i];
      if (cell.count === 0) {
        lc.strokeStyle = "#243b63";
        lc.lineWidth = 0.85;
        lc.beginPath();
        lc.moveTo(cell.x - 1.7, cell.y);
        lc.lineTo(cell.x + 1.7, cell.y);
        lc.moveTo(cell.x, cell.y - 1.7);
        lc.lineTo(cell.x, cell.y + 1.7);
        lc.stroke();
      } else if (cell.count <= 4) {
        drawStarPolygon(lc, cell.x, cell.y, 4.2, 1.5, 4);
        lc.fillStyle = "#7dd3fc";
        lc.fill();
      } else {
        this.dynamicCells.push({ cell, idx: i });
      }
    }

    lc.strokeStyle = "rgba(125, 211, 252, 0.34)";
    lc.lineWidth = 1;
    lc.beginPath();
    lc.moveTo(36, 169);
    lc.lineTo(this.w - 24, 169);
    lc.stroke();

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
    this._visible = true;
    if (typeof IntersectionObserver === "function") {
      const io = new IntersectionObserver((entries) => {
        if (entries[0]) this._visible = entries[0].isIntersecting;
      }, { rootMargin: "90px 0px" });
      io.observe(this.canvas);
    }
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
    this._frameTick = 0;
    const step = () => {
      if (this.reducedMotion) {
        this._looping = false;
        return;
      }
      if (this._visible) {
        this.time += 0.02;
        this._frameTick = (this._frameTick + 1) % 3;
        if (this._frameTick === 0) {
          this.render();
        }
      }
      requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }

  render() {
    const ctx = this.ctx;
    ctx.drawImage(this.underlay, 0, 0, this.w, this.h);

    if (!this._starSprites) {
      const mkStar = (sz, outR, inR, pts, col, ring) => {
        const sc = document.createElement("canvas");
        sc.width = sz;
        sc.height = sz;
        const sctx = sc.getContext("2d");
        const mid = sz * 0.5;
        if (ring) {
          sctx.strokeStyle = "rgba(253, 224, 71, 0.82)";
          sctx.lineWidth = 1.05;
          sctx.setLineDash([3, 2.2]);
          sctx.beginPath();
          sctx.arc(mid, mid, 7.6, 0, Math.PI * 2);
          sctx.stroke();
          sctx.setLineDash([]);
        }
        drawStarPolygon(sctx, mid, mid, outR, inR, pts, -Math.PI * 0.5);
        sctx.fillStyle = col;
        sctx.fill();
        return sc;
      };
      this._starSprites = {
        emerald: mkStar(14, 5.4, 2.0, 6, "#34d399", false),
        gold: mkStar(18, 6.6, 2.4, 8, "#fde047", true)
      };
    }

    for (let k = 0; k < this.dynamicCells.length; k++) {
      const { cell: c, idx: i } = this.dynamicCells[k];
      ctx.save();
      ctx.translate(c.x, c.y);
      if (c.count <= 19) {
        ctx.rotate(this.time * 0.25 + i);
        ctx.drawImage(this._starSprites.emerald, -7, -7);
      } else {
        ctx.rotate(this.time * 0.30 + i);
        ctx.drawImage(this._starSprites.gold, -9, -9);
      }
      ctx.restore();
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
    if (!this._waterSprites) {
      const mk = (txt, col) => {
        const wc = document.createElement("canvas");
        wc.width = 26;
        wc.height = 14;
        const wctx = wc.getContext("2d");
        wctx.font = "700 9.5px 'JetBrains Mono', ui-monospace, monospace";
        wctx.textAlign = "center";
        wctx.textBaseline = "middle";
        wctx.fillStyle = col;
        wctx.fillText(txt, 13, 7);
        return wc;
      };
      this._waterSprites = {
        goldHi: mk("≈~≈", "#fde047"),
        goldLo: mk("~~", "#fde047"),
        skyLo: mk("~~", "#7dd3fc")
      };
    }
    const maxW = Math.max(1, ...this.weeks52);
    for (let w = 0; w < 52; w++) {
      const val = this.weeks52[w] || 0;
      if (val <= 0) continue;
      const norm = Math.pow(val / maxW, 0.62);
      const wx = 54 + w * 20.1;
      const cursorBoost = Math.exp(-Math.pow((wx - this.pointerX) / 90, 2)) * 0.35;
      const shift = Math.sin(this.time * 1.6 + w * 0.5) * 2.2;
      ctx.globalAlpha = Math.min(0.95, 0.36 + norm * 0.48 + cursorBoost);
      const sp = norm > 0.55 ? this._waterSprites.goldHi : (norm > 0.45 ? this._waterSprites.goldLo : this._waterSprites.skyLo);
      ctx.drawImage(sp, Math.round(wx + shift - 13), waterY + 10 + (w % 2) * 6);
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

  const portraitStage = new PortraitStage(document.getElementById("portrait-canvas"), portraitData);
  const rawPortraitRender = portraitStage.render.bind(portraitStage);
  let portraitIdleTick = 0;
  let portW = portraitStage.canvas.width;
  let portH = portraitStage.canvas.height;
  portraitStage.render = () => {
    if (portraitStage.canvas.width !== portW || portraitStage.canvas.height !== portH) {
      portW = portraitStage.canvas.width;
      portH = portraitStage.canvas.height;
      rawPortraitRender();
      return;
    }
    if (
      !portraitStage.reducedMotion &&
      !portraitStage.pointer.inside &&
      Math.hypot(portraitStage.gaze.tx - portraitStage.gaze.x, portraitStage.gaze.ty - portraitStage.gaze.y) < 0.004
    ) {
      portraitIdleTick = (portraitIdleTick + 1) % 4;
      if (portraitIdleTick !== 0) return;
    }
    rawPortraitRender();
  };

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
  const rawRadarResize = radarStage._resize.bind(radarStage);
  const rawRadarRender = radarStage.render.bind(radarStage);
  let radarTick = 0;
  let radarForce = true;
  radarStage._resize = () => {
    radarForce = true;
    rawRadarResize();
  };
  radarStage.render = () => {
    if (radarForce || radarStage.reducedMotion || radarStage.dragging || radarStage.hovered) {
      radarForce = false;
      rawRadarRender();
      return;
    }
    radarTick = (radarTick + 1) % 3;
    if (radarTick !== 1) return;
    rawRadarRender();
  };
  const rawSetSel = radarStage.setSelected.bind(radarStage);
  radarStage.setSelected = (name) => {
    radarForce = true;
    rawSetSel(name);
  };
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
      const rlRes = await fetch("https://api.github.com/rate_limit");
      if (!rlRes.ok) throw new Error(`HTTP ${rlRes.status}`);
      const rlData = await rlRes.json();
      const remaining = rlData && rlData.resources && rlData.resources.core
        ? Number(rlData.resources.core.remaining)
        : 1;
      if (remaining < 1) {
        consoleState = "error";
        renderConsole();
        return;
      }
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
  const forumStages = [
    new Forum3DStage(document.getElementById("stage-v3"), "v3", modelsBundle, cardSky, { yaw: 0.50 }),
    new Forum3DStage(document.getElementById("stage-v2"), "v2", modelsBundle, cardSky, { yaw: 0.43 }),
    new Forum3DStage(document.getElementById("stage-v1"), "v1", modelsBundle, cardSky, { yaw: 0.40, pitch: 0.38 })
  ];
  forumStages.forEach((st, idx) => {
    const rawResize = st._resize.bind(st);
    const rawRender = st.render.bind(st);
    let tick = idx;
    let needsPaint = true;
    st._resize = () => {
      needsPaint = true;
      rawResize();
    };
    st.render = () => {
      if (needsPaint || st.reducedMotion || st.dragging) {
        needsPaint = false;
        rawRender();
        return;
      }
      tick = (tick + 1) % 3;
      if (tick !== 0) return;
      rawRender();
    };
    rawRender();
  });

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

  let pup = null;
  const dogLayer = document.getElementById("pixel-dog-layer");
  const dogCanvas = document.getElementById("pixel-dog-canvas");
  const dogHitbox = document.getElementById("pixel-dog-hitbox");
  if (dogLayer && dogCanvas && dogHitbox) {
    pup = new StarlightPixelDog(
      dogLayer,
      dogCanvas,
      dogHitbox,
      (nx, ny, fx = 7, fy = -6) => {
        sky.injectImpulse(nx, ny, fx, fy);
      },
      () => sky.getEnvironmentState()
    );
    sky.setMeteorListener((meteorInfo) => {
      if (pup) pup.notifyMeteor(meteorInfo);
    });
  }

  window.__observatoryEcosystem = {
    setCycleTime: (sec) => {
      sky.setCycleTime(sec);
      if (pup) {
        pup._syncHitbox(true);
        pup.render();
      }
    },
    getState: () => sky.getEnvironmentState()
  };

  document.querySelectorAll("[data-expand-3d]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const id = btn.getAttribute("data-expand-3d");
      if (typeof modal.showModal === "function") modal.showModal();
      else modal.setAttribute("open", "");
      if (pup) pup._syncHitbox();
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
    if (pup) pup._syncHitbox();
  });

  modal.addEventListener("click", (ev) => {
    if (ev.target === modal) {
      if (typeof modal.close === "function") modal.close();
      else modal.removeAttribute("open");
      if (pup) pup._syncHitbox();
    }
  });

  modal.addEventListener("close", () => {
    if (pup) pup._syncHitbox();
  });
}

initObservatory();
