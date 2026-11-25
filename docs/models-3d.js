// SPDX-License-Identifier: MIT
// WHY: Renders the 1240px occlusion-free 4-plane calligraphic portrait, specular-lit 360-degree Stack Architecture crystal, and Blender 360-degree 3D F-Forum stages.

import { drawTaperedImpastoStroke } from "./sky-engine.js";

function isCanvasVisible(canvas) {
  if (!canvas) return false;
  const dlg = canvas.closest("dialog");
  if (dlg && !dlg.open) return false;
  const rect = canvas.getBoundingClientRect();
  if (rect.width === 0 || rect.height === 0) return false;
  return rect.bottom >= -80 && rect.top <= (window.innerHeight || 900) + 80;
}

function shadeHex(hexCol, factor, warmBoost = 0, specBoost = 0, coolRim = 0) {
  const clean = (hexCol || "#60a5fa").replace("#", "");
  const r = parseInt(clean.slice(0, 2), 16) || 96;
  const g = parseInt(clean.slice(2, 4), 16) || 165;
  const b = parseInt(clean.slice(4, 6), 16) || 250;
  const nr = Math.min(255, Math.max(0, Math.round(r * factor + warmBoost * 46 + specBoost * 118 + coolRim * 18)));
  const ng = Math.min(255, Math.max(0, Math.round(g * factor + warmBoost * 32 + specBoost * 114 + coolRim * 46)));
  const nb = Math.min(255, Math.max(0, Math.round(b * factor + warmBoost * 10 + specBoost * 96 + coolRim * 74)));
  return `rgb(${nr}, ${ng}, ${nb})`;
}

function shadeHexAlpha(hexCol, factor, alpha, specBoost = 0) {
  const clean = (hexCol || "#60a5fa").replace("#", "");
  const r = parseInt(clean.slice(0, 2), 16) || 96;
  const g = parseInt(clean.slice(2, 4), 16) || 165;
  const b = parseInt(clean.slice(4, 6), 16) || 250;
  const nr = Math.min(255, Math.max(0, Math.round(r * factor + specBoost * 110)));
  const ng = Math.min(255, Math.max(0, Math.round(g * factor + specBoost * 108)));
  const nb = Math.min(255, Math.max(0, Math.round(b * factor + specBoost * 96)));
  return `rgba(${nr}, ${ng}, ${nb}, ${alpha.toFixed(3)})`;
}

function computeNormal(pts) {
  if (pts.length < 3) return [0, 1, 0];
  const ax = pts[1][0] - pts[0][0];
  const ay = pts[1][1] - pts[0][1];
  const az = pts[1][2] - pts[0][2];
  const bx = pts[2][0] - pts[0][0];
  const by = pts[2][1] - pts[0][1];
  const bz = pts[2][2] - pts[0][2];
  const nx = ay * bz - az * by;
  const ny = az * bx - ax * bz;
  const nz = ax * by - ay * bx;
  const len = Math.hypot(nx, ny, nz) || 1;
  return [nx / len, ny / len, nz / len];
}

function drawStarReticle(ctx, cx, cy, outerR, innerR, points = 4, rot = -Math.PI * 0.5) {
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

export class PortraitStage {
  constructor(canvas, portraitData) {
    this.canvas = canvas;
    this.ctx = canvas.getContext("2d");
    this.data = portraitData;
    this.mqReduced = window.matchMedia("(prefers-reduced-motion: reduce)");
    this.reducedMotion = this.mqReduced.matches;
    this.pointer = { nx: 0.5, ny: 0.5, inside: false };
    this.gaze = { tx: 0, ty: 0, x: 0, y: 0 };
    this.angle = 0;
    this._looping = false;

    this.size = 1240;
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

  // WHY: Paints occluded sky/field/railing inpainting (bg_under) beneath tapered multi-plane strokes so 2.5D parallax never tears black gaps.
  _bakeLayers() {
    const sz = this.size;
    const cx = sz / 2;
    const cy = sz / 2;
    const r = sz * 0.464;
    const diam = r * 2;
    const x0 = cx - r;
    const y0 = cy - r;

    const ctxs = this.layers.map((c) => {
      const lc = c.getContext("2d");
      lc.clearRect(0, 0, sz, sz);
      return lc;
    });

    ctxs[0].fillStyle = "#0b2042";
    ctxs[0].fillRect(0, 0, sz, sz);

    const hatchN = Math.max(1, this.data.hatch_n || 76);
    const hStep = diam / hatchN;
    ctxs.forEach((lc) => { lc.lineCap = "round"; });

    const bgUnder = this.data.bg_under || [];
    for (let i = 0; i < bgUnder.length; i++) {
      const [ax, ay, bcol, bpl] = bgUnder[i];
      const pl = Math.min(2, Math.max(0, Number(bpl || 0)));
      const lc = ctxs[pl];
      const px = x0 + ax * hStep - hStep * 0.22;
      const py = y0 + ay * hStep - hStep * 0.22;
      lc.fillStyle = shadeHex(bcol, 1.08, 0.03);
      lc.fillRect(px, py, hStep * 1.48, hStep * 1.48);
    }

    const skyHalo = ctxs[0].createRadialGradient(cx + r * 0.22, cy - r * 0.34, r * 0.06, cx, cy, r * 1.05);
    skyHalo.addColorStop(0, "rgba(254, 240, 138, 0.20)");
    skyHalo.addColorStop(0.45, "rgba(56, 189, 248, 0.14)");
    skyHalo.addColorStop(1, "rgba(10, 28, 58, 0)");
    ctxs[0].fillStyle = skyHalo;
    ctxs[0].fillRect(0, 0, sz, sz);

    const underStrokes = this.data.under_strokes || [];
    for (let i = 0; i < underStrokes.length; i++) {
      const [ax, ay, hcol, planeRaw, angDeg] = underStrokes[i];
      const pl = Math.min(3, Math.max(0, Number(planeRaw || 0)));
      const lc = ctxs[pl];
      const px = x0 + (ax + 0.5) * hStep;
      const py = y0 + (ay + 0.5) * hStep;
      const rad = (angDeg * Math.PI) / 180;
      const dx = Math.cos(rad) * hStep * 0.82;
      const dy = Math.sin(rad) * hStep * 0.82;
      const nx = -Math.sin(rad) * hStep * 0.14;
      const ny = Math.cos(rad) * hStep * 0.14;
      drawTaperedImpastoStroke(lc, px - dx, py - dy, px + nx, py + ny, px + dx, py + dy, hcol, hStep * 1.04, 0.94);
    }

    const skyStrokes = this.data.sky_strokes || [];
    ctxs[0].save();
    for (let i = 0; i < skyStrokes.length; i++) {
      const [sx0, sy0, smx, smy, sx1, sy1, scol, sop] = skyStrokes[i];
      drawTaperedImpastoStroke(
        ctxs[0],
        x0 + sx0 * diam,
        y0 + sy0 * diam,
        x0 + smx * diam,
        y0 + smy * diam,
        x0 + sx1 * diam,
        y0 + sy1 * diam,
        scol,
        3.2,
        Math.min(1, sop * 1.08)
      );
    }
    ctxs[0].restore();

    const cols = Math.max(1, this.data.cols || 208);
    const rows = Math.max(1, this.data.rows || 122);
    const grid = this.data.grid || [];
    const planes = this.data.planes || [];
    const rowStep = diam / rows;
    const colStep = diam / cols;
    const monoFamily = "'JetBrains Mono', ui-monospace, monospace";
    ctxs[0].font = `700 20px ${monoFamily}`;
    const unitAdv = (ctxs[0].measureText("MMMMMMMMMM").width / 200) || 0.6;
    const fontSz = Math.max(2.0, colStep / unitAdv);

    ctxs.forEach((lc) => {
      lc.font = `700 ${fontSz.toFixed(3)}px ${monoFamily}`;
      lc.textBaseline = "alphabetic";
      lc.globalAlpha = 0.98;
    });

    for (let rIdx = 0; rIdx < grid.length; rIdx++) {
      const runs = grid[rIdx];
      const planeRow = planes[rIdx] || "";
      const py = y0 + (rIdx + 0.82) * rowStep;
      let colCursor = 0;
      for (let k = 0; k < runs.length; k++) {
        const [colHex, chunk] = runs[k];
        if (colHex) {
          const liftedCol = shadeHex(colHex, 1.06, 0.02);
          let segStart = 0;
          let segPlane = -1;
          let segChars = "";
          for (let c = 0; c <= chunk.length; c++) {
            const ch = c < chunk.length ? chunk[c] : " ";
            const pCode = ch !== " " ? Number(planeRow[colCursor + c] ?? 1) : -1;
            if (pCode === segPlane && pCode >= 0) {
              segChars += ch;
            } else {
              if (segPlane >= 0 && segChars) {
                const lc = ctxs[Math.min(3, Math.max(0, segPlane))];
                lc.fillStyle = liftedCol;
                lc.fillText(segChars, x0 + (colCursor + segStart) * colStep, py);
              }
              segPlane = pCode;
              segStart = c;
              segChars = pCode >= 0 ? ch : "";
            }
          }
        }
        colCursor += chunk.length;
      }
    }

    const contours = this.data.contours || [];
    for (let i = 0; i < contours.length; i++) {
      const [cx0, cy0, cx1, cy1, scol, sop, pRaw] = contours[i];
      const pIdx = Math.min(3, Math.max(0, Number(pRaw ?? 1)));
      const lc = ctxs[pIdx];
      const px0 = x0 + cx0 * diam;
      const py0 = y0 + cy0 * diam;
      const px1 = x0 + cx1 * diam;
      const py1 = y0 + cy1 * diam;
      drawTaperedImpastoStroke(
        lc,
        px0,
        py0,
        (px0 + px1) * 0.5,
        (py0 + py1) * 0.5,
        px1,
        py1,
        scol,
        1.95,
        sop
      );
    }
    ctxs.forEach((lc) => { lc.globalAlpha = 1; });
  }

  _bindEvents() {
    this.mqReduced.addEventListener("change", (e) => {
      this.reducedMotion = e.matches;
      if (!this.reducedMotion) this._animate();
      else this.render();
    });

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
    const step = () => {
      if (this.reducedMotion) {
        this._looping = false;
        return;
      }
      if (isCanvasVisible(this.canvas)) {
        this.angle += 0.004;
        this.gaze.x += (this.gaze.tx - this.gaze.x) * 0.10;
        this.gaze.y += (this.gaze.ty - this.gaze.y) * 0.10;
        this.render();
      }
      requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }

  render() {
    const ctx = this.ctx;
    const sz = this.size;
    const cx = sz / 2;
    const cy = sz / 2;
    const r = sz * 0.464;

    ctx.clearRect(0, 0, sz, sz);

    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(this.angle * 0.30);
    for (let deg = 0; deg < 360; deg += 15) {
      const rad = (deg * Math.PI) / 180;
      const r0 = r + 9;
      const r1 = r + (deg % 45 === 0 ? 25 : 15);
      ctx.strokeStyle = deg % 90 === 0 ? "rgba(254, 240, 138, 0.90)" : "rgba(125, 211, 252, 0.44)";
      ctx.lineWidth = deg % 45 === 0 ? 2.7 : 1.5;
      ctx.beginPath();
      ctx.moveTo(Math.cos(rad) * r0, Math.sin(rad) * r0);
      ctx.lineTo(Math.cos(rad) * r1, Math.sin(rad) * r1);
      ctx.stroke();
    }
    const satA = this.angle * 1.4;
    drawStarReticle(ctx, Math.cos(satA) * (r + 20), Math.sin(satA) * (r + 20), 10.0, 3.6, 4, satA);
    ctx.fillStyle = "#fde047";
    ctx.fill();
    ctx.restore();

    const dxNorm = this.pointer.inside ? (this.pointer.nx - 0.5) * 1.35 : this.gaze.x * 0.62;
    const dyNorm = this.pointer.inside ? (this.pointer.ny - 0.5) * 1.35 : this.gaze.y * 0.52;

    const compCtx = this.composite.getContext("2d");
    compCtx.clearRect(0, 0, sz, sz);
    compCtx.save();
    compCtx.beginPath();
    compCtx.arc(cx, cy, r, 0, Math.PI * 2);
    compCtx.clip();
    const shifts = [-7.0, 2.5, 8.5, 14.5];
    for (let p = 0; p < 4; p++) {
      compCtx.drawImage(this.layers[p], dxNorm * shifts[p], dyNorm * shifts[p]);
    }
    compCtx.restore();

    ctx.drawImage(this.composite, 0, 0);

    // WHY: Clamps and clips the optical loupe strictly inside the circular medallion so CSS border-radius never slices it into a D-shape.
    if (this.pointer.inside) {
      const loupeR = 162;
      const zoom = 2.35;
      const rawLx = this.pointer.nx * sz;
      const rawLy = this.pointer.ny * sz;
      const offX = rawLx - cx;
      const offY = rawLy - cy;
      const offDist = Math.hypot(offX, offY);
      const maxCenterDist = Math.max(0, r - loupeR - 8);
      const clampedLx = offDist > maxCenterDist && offDist > 0 ? cx + (offX / offDist) * maxCenterDist : rawLx;
      const clampedLy = offDist > maxCenterDist && offDist > 0 ? cy + (offY / offDist) * maxCenterDist : rawLy;

      ctx.save();
      ctx.beginPath();
      ctx.arc(cx, cy, r - 2, 0, Math.PI * 2);
      ctx.clip();

      ctx.beginPath();
      ctx.arc(clampedLx, clampedLy, loupeR, 0, Math.PI * 2);
      ctx.clip();
      ctx.fillStyle = "#07142c";
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
      ctx.lineWidth = 4.2;
      ctx.beginPath();
      ctx.arc(clampedLx, clampedLy, loupeR, 0, Math.PI * 2);
      ctx.stroke();

      ctx.strokeStyle = "rgba(255, 255, 255, 0.55)";
      ctx.lineWidth = 1.6;
      ctx.beginPath();
      ctx.arc(clampedLx, clampedLy, loupeR - 3, -Math.PI * 0.85, -Math.PI * 0.25);
      ctx.stroke();
    }

    ctx.strokeStyle = "rgba(253, 230, 138, 0.78)";
    ctx.lineWidth = 4.0;
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.stroke();

    ctx.strokeStyle = "rgba(254, 249, 195, 0.52)";
    ctx.lineWidth = 1.8;
    ctx.beginPath();
    ctx.arc(cx, cy, r - 2.5, -Math.PI * 0.86, -Math.PI * 0.18);
    ctx.stroke();
  }
}

export class Radar5DStage {
  constructor(canvas, langs5d, onSelect) {
    this.canvas = canvas;
    this.ctx = canvas.getContext("2d");
    this.langs = langs5d || [];
    this.onSelect = onSelect;
    this.mqReduced = window.matchMedia("(prefers-reduced-motion: reduce)");
    this.reducedMotion = this.mqReduced.matches;

    this.yaw = -0.40;
    this.pitch = 0.98;
    this.hyperAngle = 0.45;
    this.gazeOffset = { x: 0, y: 0 };
    this.selected = null;
    this.hovered = null;
    this.time = 0;
    this.dragging = false;
    this.lastPt = { x: 0, y: 0 };
    this.hitNodes = [];
    this._looping = false;

    this.w = 620;
    this.h = 310;
    this.dpr = Math.min(window.devicePixelRatio || 1, 2);
    this._resize();
    this._bindEvents();
    this.render();
    if (!this.reducedMotion) {
      this._loop();
    }
  }

  _resize() {
    this.dpr = Math.min(window.devicePixelRatio || 1, 2);
    const rect = this.canvas.getBoundingClientRect();
    this.w = Math.max(300, Math.round(rect.width || 620));
    const ratio = this.w < 460 ? 0.59 : 0.50;
    this.h = Math.max(216, Math.round(this.w * ratio));
    this.canvas.width = Math.round(this.w * this.dpr);
    this.canvas.height = Math.round(this.h * this.dpr);
    this.ctx.setTransform(this.dpr, 0, 0, this.dpr, 0, 0);
  }

  setSelected(name) {
    this.selected = name;
    this.render();
    if (this.onSelect) this.onSelect(this.selected);
  }

  _project5D(x, y, z, wCoord) {
    const cx = this.w * 0.5;
    const cy = this.h * 0.55;
    const ha = this.hyperAngle;
    const ca = Math.cos(ha);
    const sa = Math.sin(ha);

    const x4 = x * ca - wCoord * 16 * sa;
    const w4 = (x / 120) * sa + wCoord * ca;
    const z4 = z * Math.cos(ha * 0.5) + wCoord * 12 * Math.sin(ha * 0.5);

    const wScale = 1 / Math.max(0.55, 1.34 - 0.28 * w4);
    const xw = x4 * wScale;
    const yw = y * wScale;
    const zw = z4 * wScale;

    const effYaw = this.yaw + this.gazeOffset.x * 0.14;
    const effPitch = Math.max(0.42, Math.min(1.42, this.pitch + this.gazeOffset.y * 0.10));
    const cyaw = Math.cos(effYaw);
    const syaw = Math.sin(effYaw);
    const rx = xw * cyaw - yw * syaw;
    const ry = xw * syaw + yw * cyaw;

    const cp = Math.cos(effPitch);
    const sp = Math.sin(effPitch);
    const vy = ry * cp - zw * sp;
    const vz = ry * sp + zw * cp;

    const sx = cx + rx;
    const sy = cy + vy;
    return { sx, sy, depth: ry, vx: rx, vy: -vy, vz: -vz };
  }

  _bindEvents() {
    this.mqReduced.addEventListener("change", (e) => {
      this.reducedMotion = e.matches;
      if (!this.reducedMotion) this._loop();
      else this.render();
    });

    window.addEventListener("resize", () => {
      this._resize();
      this.render();
    });

    window.addEventListener("pointermove", (ev) => {
      if (this.dragging) return;
      const rect = this.canvas.getBoundingClientRect();
      this.gazeOffset.x = Math.max(-1, Math.min(1, (ev.clientX - (rect.left + rect.width * 0.5)) / 500));
      this.gazeOffset.y = Math.max(-1, Math.min(1, (ev.clientY - (rect.top + rect.height * 0.5)) / 500));
      if (this.reducedMotion) this.render();
    }, { passive: true });

    this.canvas.addEventListener("pointerdown", (ev) => {
      this.dragging = true;
      this.moved = false;
      this.lastPt = { x: ev.clientX, y: ev.clientY };
      this.canvas.setPointerCapture(ev.pointerId);
    });

    this.canvas.addEventListener("pointermove", (ev) => {
      const rect = this.canvas.getBoundingClientRect();
      const px = ((ev.clientX - rect.left) / Math.max(1, rect.width)) * this.w;
      const py = ((ev.clientY - rect.top) / Math.max(1, rect.height)) * this.h;

      if (this.dragging) {
        const dx = ev.clientX - this.lastPt.x;
        const dy = ev.clientY - this.lastPt.y;
        if (Math.hypot(dx, dy) > 2) this.moved = true;
        this.yaw += dx * 0.011;
        this.pitch = Math.max(0.42, Math.min(1.42, this.pitch + dy * 0.008));
        this.lastPt = { x: ev.clientX, y: ev.clientY };
        this.render();
        return;
      }

      let found = null;
      for (let i = 0; i < this.hitNodes.length; i++) {
        const hn = this.hitNodes[i];
        if (Math.hypot(px - hn.x, py - hn.y) < 22) {
          found = hn.name;
          break;
        }
      }
      if (found !== this.hovered) {
        this.hovered = found;
        if (!this.selected && this.onSelect) this.onSelect(found);
        if (this.reducedMotion) this.render();
      }
    });

    this.canvas.addEventListener("pointerleave", () => {
      this.hovered = null;
      if (!this.selected && this.onSelect) this.onSelect(null);
      if (this.reducedMotion) this.render();
    });

    const endDrag = (ev) => {
      if (!this.dragging) return;
      this.dragging = false;
      if (!this.moved) {
        const rect = this.canvas.getBoundingClientRect();
        const px = ((ev.clientX - rect.left) / Math.max(1, rect.width)) * this.w;
        const py = ((ev.clientY - rect.top) / Math.max(1, rect.height)) * this.h;
        let found = null;
        for (let i = 0; i < this.hitNodes.length; i++) {
          const hn = this.hitNodes[i];
          if (Math.hypot(px - hn.x, py - hn.y) < 26) {
            found = hn.name;
            break;
          }
        }
        this.setSelected(found === this.selected ? null : found);
      }
    };
    this.canvas.addEventListener("pointerup", endDrag);
    this.canvas.addEventListener("pointercancel", () => { this.dragging = false; });

    this.canvas.addEventListener("keydown", (ev) => {
      if (ev.key === "ArrowLeft") { this.yaw -= 0.12; this.render(); ev.preventDefault(); }
      if (ev.key === "ArrowRight") { this.yaw += 0.12; this.render(); ev.preventDefault(); }
      if (ev.key === "ArrowUp") { this.pitch = Math.max(0.42, this.pitch - 0.08); this.render(); ev.preventDefault(); }
      if (ev.key === "ArrowDown") { this.pitch = Math.min(1.42, this.pitch + 0.08); this.render(); ev.preventDefault(); }
    });
  }

  _loop() {
    if (this._looping) return;
    this._looping = true;
    const step = () => {
      if (this.reducedMotion) {
        this._looping = false;
        return;
      }
      if (isCanvasVisible(this.canvas)) {
        this.time += 0.016;
        if (!this.dragging) {
          this.yaw += 0.0036;
        }
        this.render();
      }
      requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }

  render() {
    const ctx = this.ctx;
    const scale = Math.min(this.w / 620, this.h / 306);
    const compactFactor = this.w < 460 ? 0.84 : 1.0;
    const rMax = 122 * scale * compactFactor;
    const crownZ = 74 * scale * compactFactor;
    const apexZ = 90 * scale * compactFactor;
    ctx.clearRect(0, 0, this.w, this.h);

    const origin = this._project5D(0, 0, 0, 1);

    ctx.beginPath();
    for (let deg = 0; deg <= 360; deg += 6) {
      const rad = (deg * Math.PI) / 180;
      const p = this._project5D(Math.cos(rad) * rMax * 1.10, Math.sin(rad) * rMax * 1.10, 0, 1);
      if (deg === 0) ctx.moveTo(p.sx, p.sy);
      else ctx.lineTo(p.sx, p.sy);
    }
    const baseGrad = ctx.createRadialGradient(origin.sx, origin.sy, rMax * 0.06, origin.sx, origin.sy, rMax * 1.18);
    baseGrad.addColorStop(0, "rgba(18, 44, 88, 0.94)");
    baseGrad.addColorStop(0.56, "rgba(9, 22, 48, 0.92)");
    baseGrad.addColorStop(1, "rgba(5, 13, 28, 0.90)");
    ctx.fillStyle = baseGrad;
    ctx.fill();
    ctx.strokeStyle = "rgba(96, 165, 250, 0.68)";
    ctx.lineWidth = 1.35;
    ctx.stroke();

    for (let deg = 0; deg < 360; deg += 15) {
      const rad = (deg * Math.PI) / 180;
      const inF = deg % 60 === 0 ? 1.00 : 1.05;
      const p0 = this._project5D(Math.cos(rad) * rMax * inF, Math.sin(rad) * rMax * inF, 0, 1);
      const p1 = this._project5D(Math.cos(rad) * rMax * 1.10, Math.sin(rad) * rMax * 1.10, 0, 1);
      ctx.strokeStyle = deg % 60 === 0 ? "rgba(254, 240, 138, 0.86)" : "rgba(125, 211, 252, 0.42)";
      ctx.lineWidth = deg % 60 === 0 ? 1.25 : 0.8;
      ctx.beginPath();
      ctx.moveTo(p0.sx, p0.sy);
      ctx.lineTo(p1.sx, p1.sy);
      ctx.stroke();
    }

    for (const rf of [0.32, 0.56, 0.80, 1.00]) {
      ctx.beginPath();
      for (let i = 0; i <= 6; i++) {
        const ang = -Math.PI / 2 + (i % 6) * (Math.PI / 3);
        const p = this._project5D(Math.cos(ang) * rMax * rf, Math.sin(ang) * rMax * rf, 0, 1);
        if (i === 0) ctx.moveTo(p.sx, p.sy);
        else ctx.lineTo(p.sx, p.sy);
      }
      ctx.strokeStyle = rf >= 0.8 ? "rgba(96, 165, 250, 0.58)" : "rgba(56, 88, 138, 0.48)";
      ctx.lineWidth = 0.9;
      ctx.stroke();
    }

    const zenith = this._project5D(0, 0, apexZ, 1);
    const innerZenith = this._project5D(0, 0, apexZ * 0.58, -0.75);

    const n = this.langs.length || 6;
    const outerV = [];
    const baseV = [];
    const innerV = [];
    const labelAnchors = [];

    for (let i = 0; i < n; i++) {
      const item = this.langs[i];
      const ang = -Math.PI / 2 + (i * Math.PI * 2) / n;
      const reach = 0.36 + 0.62 * Math.min(1, item.d2Volume);
      const elev = 14 * scale + crownZ * (0.42 * Math.min(1, item.d2Volume) + 0.58 * item.d3Breadth);
      const wx = Math.cos(ang) * rMax * reach;
      const wy = Math.sin(ang) * rMax * reach;

      const ov = this._project5D(wx, wy, elev, 1);
      const bv = this._project5D(wx, wy, 0, 1);
      const iv = this._project5D(
        wx * (0.58 * (0.68 + 0.32 * item.d4Gravity)),
        wy * (0.58 * (0.68 + 0.32 * item.d4Gravity)),
        elev * 0.56 + 8 * scale,
        -0.75
      );
      const labelZ = i === 0 ? crownZ * 0.74 : (i === 3 ? -18 * scale : Math.max(elev * 0.88, crownZ * 0.38));
      const labelRad = i === 3 ? rMax * 1.28 : rMax * (this.w < 460 ? 1.36 : 1.30);
      const axisOuter = this._project5D(Math.cos(ang) * labelRad, Math.sin(ang) * labelRad, labelZ, 1);

      ctx.strokeStyle = "rgba(59, 92, 146, 0.56)";
      ctx.lineWidth = 0.9;
      ctx.beginPath();
      ctx.moveTo(origin.sx, origin.sy);
      ctx.lineTo(bv.sx, bv.sy);
      ctx.stroke();

      outerV.push({ ...ov, item });
      baseV.push(bv);
      innerV.push({ ...iv, item });
      labelAnchors.push(axisOuter);
    }

    ctx.beginPath();
    for (let i = 0; i < n; i++) {
      if (i === 0) ctx.moveTo(baseV[i].sx, baseV[i].sy);
      else ctx.lineTo(baseV[i].sx, baseV[i].sy);
    }
    ctx.closePath();
    ctx.fillStyle = "rgba(2, 6, 16, 0.42)";
    ctx.fill();

    const coreGlow = ctx.createRadialGradient(innerZenith.sx, innerZenith.sy, 2, origin.sx, origin.sy, rMax * 0.68);
    coreGlow.addColorStop(0, "rgba(254, 240, 138, 0.26)");
    coreGlow.addColorStop(0.52, "rgba(56, 189, 248, 0.14)");
    coreGlow.addColorStop(1, "rgba(56, 189, 248, 0)");
    ctx.fillStyle = coreGlow;
    ctx.beginPath();
    ctx.arc(origin.sx, origin.sy, rMax * 0.68, 0, Math.PI * 2);
    ctx.fill();

    const activeDomain = this.selected || this.hovered;
    const facets = [];
    const lx = -0.38;
    const ly = 0.64;
    const lz = 0.66;

    for (let i = 0; i < n; i++) {
      const j = (i + 1) % n;
      const vi = outerV[i];
      const vj = outerV[j];
      const bi = baseV[i];
      const bj = baseV[j];
      const ii = innerV[i];
      const ij = innerV[j];
      const highlighted = activeDomain && (vi.item.name === activeDomain || vj.item.name === activeDomain);

      const coreNorm = computeNormal([
        [innerZenith.vx, innerZenith.vy, innerZenith.vz],
        [ii.vx, ii.vy, ii.vz],
        [ij.vx, ij.vy, ij.vz]
      ]);
      const coreDot = Math.abs(coreNorm[0] * lx + coreNorm[1] * ly + coreNorm[2] * lz);
      const coreSpec = Math.pow(coreDot, 8);

      facets.push({
        depth: (innerZenith.depth + ii.depth + ij.depth) / 3 - 4,
        pts: [innerZenith, ii, ij],
        fill: highlighted
          ? "rgba(253, 224, 71, 0.56)"
          : shadeHexAlpha(i % 2 === 0 ? "#60a5fa" : "#fbbf24", 0.90 + coreDot * 0.45, 0.38, coreSpec * 0.35),
        stroke: coreSpec > 0.38 ? "rgba(254, 249, 195, 0.92)" : "rgba(224, 242, 254, 0.84)",
        lw: highlighted ? 1.55 : 1.05,
        spec: coreSpec
      });

      const waistNorm = computeNormal([
        [bi.vx, bi.vy, bi.vz],
        [bj.vx, bj.vy, bj.vz],
        [vj.vx, vj.vy, vj.vz]
      ]);
      const waistDot = Math.abs(waistNorm[0] * lx + waistNorm[1] * ly + waistNorm[2] * lz);
      const waistSpec = Math.pow(waistDot, 10);

      facets.push({
        depth: (bi.depth + bj.depth + vi.depth + vj.depth) / 4 - 2,
        pts: [bi, bj, vj, vi],
        fill: shadeHexAlpha("#1d4ed8", 0.52 + waistDot * 0.62, highlighted ? 0.56 : 0.40, waistSpec * 0.28),
        stroke: waistSpec > 0.42 ? "rgba(186, 230, 253, 0.85)" : "rgba(94, 234, 212, 0.56)",
        lw: highlighted ? 1.25 : 0.95,
        spec: waistSpec
      });

      const crownNorm = computeNormal([
        [zenith.vx, zenith.vy, zenith.vz],
        [vi.vx, vi.vy, vi.vz],
        [vj.vx, vj.vy, vj.vz]
      ]);
      const crownDot = Math.abs(crownNorm[0] * lx + crownNorm[1] * ly + crownNorm[2] * lz);
      const crownSpec = Math.pow(crownDot, 9);

      facets.push({
        depth: (zenith.depth + vi.depth + vj.depth) / 3,
        pts: [zenith, vi, vj],
        fill: shadeHexAlpha(vi.item.color, 0.78 + crownDot * 0.54, highlighted ? 0.54 : 0.34, crownSpec * 0.42),
        stroke: highlighted ? "#ffffff" : (crownSpec > 0.36 ? "#fef9c3" : "rgba(253, 230, 138, 0.84)"),
        lw: highlighted ? 1.75 : (crownSpec > 0.36 ? 1.35 : 1.15),
        spec: crownSpec
      });
    }

    facets.sort((a, b) => a.depth - b.depth);
    for (let i = 0; i < facets.length; i++) {
      const f = facets[i];
      ctx.beginPath();
      ctx.moveTo(f.pts[0].sx, f.pts[0].sy);
      for (let k = 1; k < f.pts.length; k++) {
        ctx.lineTo(f.pts[k].sx, f.pts[k].sy);
      }
      ctx.closePath();
      ctx.fillStyle = f.fill;
      ctx.fill();
      ctx.strokeStyle = f.stroke;
      ctx.lineWidth = f.lw;
      ctx.stroke();

      if (f.spec > 0.44 && f.pts.length >= 3) {
        ctx.strokeStyle = `rgba(255, 255, 255, ${(f.spec * 0.62).toFixed(2)})`;
        ctx.lineWidth = 1.4;
        ctx.beginPath();
        ctx.moveTo(f.pts[0].sx, f.pts[0].sy);
        ctx.lineTo(f.pts[1].sx, f.pts[1].sy);
        ctx.stroke();
      }
    }

    for (let i = 0; i < n; i++) {
      const isHi = activeDomain === outerV[i].item.name;
      ctx.strokeStyle = isHi ? "#ffffff" : (i % 2 === 0 ? "rgba(254, 240, 138, 0.90)" : "rgba(110, 231, 183, 0.88)");
      ctx.lineWidth = isHi ? 1.95 : 1.2;
      ctx.beginPath();
      ctx.moveTo(innerV[i].sx, innerV[i].sy);
      ctx.lineTo(outerV[i].sx, outerV[i].sy);
      ctx.stroke();
    }

    ctx.beginPath();
    for (let i = 0; i < n; i++) {
      if (i === 0) ctx.moveTo(outerV[i].sx, outerV[i].sy);
      else ctx.lineTo(outerV[i].sx, outerV[i].sy);
    }
    ctx.closePath();
    ctx.strokeStyle = "#fef08a";
    ctx.lineWidth = 1.85;
    ctx.stroke();

    const zenGlow = ctx.createRadialGradient(zenith.sx, zenith.sy, 1, zenith.sx, zenith.sy, 16);
    zenGlow.addColorStop(0, "rgba(255, 255, 255, 0.65)");
    zenGlow.addColorStop(0.5, "rgba(253, 224, 71, 0.28)");
    zenGlow.addColorStop(1, "rgba(253, 224, 71, 0)");
    ctx.fillStyle = zenGlow;
    ctx.beginPath();
    ctx.arc(zenith.sx, zenith.sy, 16, 0, Math.PI * 2);
    ctx.fill();

    drawStarReticle(ctx, zenith.sx, zenith.sy, 7.6, 2.7, 8, this.time * 0.4);
    ctx.fillStyle = "#fde047";
    ctx.fill();

    this.hitNodes = [];
    const fontPx = Math.max(9.5, Math.min(12.2, this.w * 0.024));
    ctx.font = `700 ${fontPx.toFixed(1)}px 'JetBrains Mono', ui-monospace, monospace`;
    ctx.textBaseline = "middle";

    for (let i = 0; i < n; i++) {
      const ov = outerV[i];
      const it = ov.item;
      const isSel = activeDomain === it.name;

      drawStarReticle(ctx, ov.sx, ov.sy, isSel ? 8.4 : 6.0, isSel ? 3.2 : 2.2, 4, this.time * 0.35 + i);
      ctx.fillStyle = isSel ? "#ffffff" : it.highlight;
      ctx.fill();
      ctx.strokeStyle = it.color;
      ctx.lineWidth = 1.45;
      ctx.stroke();

      const la = labelAnchors[i];
      const pctStr = it.percent > 0 ? `${it.percent}%` : "<1%";
      const label = `${it.name} ${pctStr}`;
      const alignLeft = la.sx < this.w * 0.45;
      const alignRight = la.sx > this.w * 0.55;
      ctx.textAlign = alignLeft ? "right" : (alignRight ? "left" : "center");
      const lxPos = Math.max(10, Math.min(this.w - 10, la.sx + (alignLeft ? -6 : (alignRight ? 6 : 0))));
      const lyPos = Math.max(16, Math.min(this.h - 16, la.sy + (la.sy < this.h * 0.35 ? -7 : 6)));

      ctx.fillStyle = isSel ? "#fde047" : it.color;
      ctx.fillText(label, lxPos, lyPos);

      this.hitNodes.push({ name: it.name, x: ov.sx, y: ov.sy });
      this.hitNodes.push({ name: it.name, x: lxPos, y: lyPos });
    }
  }
}

export class Forum3DStage {
  constructor(canvas, variant = "v3", modelsBundle = {}, vgSky = null, options = {}) {
    this.canvas = canvas;
    this.ctx = canvas.getContext("2d");
    this.modelsBundle = modelsBundle || {};
    this.vgSky = vgSky;
    this.variant = variant;
    this.model = this.modelsBundle[variant] || { faces: [], lines: [] };
    this.mqReduced = window.matchMedia("(prefers-reduced-motion: reduce)");
    this.reducedMotion = this.mqReduced.matches;

    this.yaw = options.yaw ?? 0.46;
    this.pitch = options.pitch ?? 0.36;
    this.zoom = options.zoom ?? 1.04;
    this.explode = 0;
    this.wireOnly = false;
    this.autoSpin = !this.reducedMotion;
    this.time = 0;
    this.dragging = false;
    this.lastPt = { x: 0, y: 0 };

    this.dpr = Math.min(window.devicePixelRatio || 1, 2);
    this.w = options.width || 480;
    this.h = options.height || 246;
    this.bgSky = null;
    this._resize();
    this._bindEvents();
    this.render();
    if (!this.reducedMotion) {
      this._loop();
    }
  }

  _bakeCardSky() {
    const c = document.createElement("canvas");
    c.width = Math.max(1, Math.round(this.w * this.dpr));
    c.height = Math.max(1, Math.round(this.h * this.dpr));
    const lc = c.getContext("2d", { alpha: false });
    lc.setTransform(this.dpr, 0, 0, this.dpr, 0, 0);
    lc.fillStyle = "#061128";
    lc.fillRect(0, 0, this.w, this.h);

    if (this.vgSky) {
      const cols = Math.max(1, this.vgSky.cols || 160);
      const rows = Math.max(1, this.vgSky.rows || 56);
      const rStep = this.h / rows;
      const cStep = this.w / cols;

      const bgRows = this.vgSky.bg || [];
      lc.globalAlpha = 0.64;
      for (let r = 0; r < bgRows.length; r++) {
        let xCur = 0;
        const runs = bgRows[r];
        const ry = r * rStep;
        const rh = rStep + 0.8;
        for (let k = 0; k < runs.length; k++) {
          const [bCol, bLen] = runs[k];
          lc.fillStyle = shadeHex(bCol, 1.12, 0.02);
          lc.fillRect(xCur * cStep, ry, bLen * cStep + 0.8, rh);
          xCur += bLen;
        }
      }

      const horzGlow = lc.createLinearGradient(0, this.h * 0.12, 0, this.h);
      horzGlow.addColorStop(0, "rgba(56, 189, 248, 0.12)");
      horzGlow.addColorStop(0.62, "rgba(125, 211, 252, 0.14)");
      horzGlow.addColorStop(1, "rgba(251, 191, 36, 0.10)");
      lc.globalAlpha = 1;
      lc.fillStyle = horzGlow;
      lc.fillRect(0, 0, this.w, this.h);

      const strokes = this.vgSky.strokes || [];
      for (let i = 0; i < Math.min(760, strokes.length); i++) {
        const [x0, y0, xm, ym, x1, y1, scol, sw] = strokes[i];
        drawTaperedImpastoStroke(
          lc,
          x0 * this.w,
          y0 * this.h,
          xm * this.w,
          ym * this.h,
          x1 * this.w,
          y1 * this.h,
          scol,
          sw * 1.18,
          0.66
        );
      }
      const grid = this.vgSky.grid || [];
      const monoFamily = "'JetBrains Mono', ui-monospace, monospace";
      lc.font = `700 20px ${monoFamily}`;
      const unitAdv = (lc.measureText("MMMMMMMMMM").width / 200) || 0.6;
      const fSz = Math.max(1.6, cStep / unitAdv);
      lc.font = `700 ${fSz.toFixed(3)}px ${monoFamily}`;
      lc.globalAlpha = 0.56;
      for (let r = 0; r < grid.length; r++) {
        let cur = 0;
        const runs = grid[r];
        for (let k = 0; k < runs.length; k++) {
          const [col, chunk] = runs[k];
          if (col) {
            lc.fillStyle = shadeHex(col, 1.10);
            lc.fillText(chunk, cur * cStep, (r + 0.82) * rStep);
          }
          cur += chunk.length;
        }
      }
      lc.globalAlpha = 1;
      lc.fillStyle = "rgba(4, 10, 24, 0.24)";
      lc.fillRect(0, 0, this.w, this.h);
    }
    this.bgSky = c;
  }

  _resize() {
    this.dpr = Math.min(window.devicePixelRatio || 1, 2);
    const rect = this.canvas.getBoundingClientRect();
    if (rect.width > 40 && rect.height > 40) {
      this.w = Math.round(rect.width);
      this.h = Math.round(rect.height);
    }
    this.canvas.width = Math.round(this.w * this.dpr);
    this.canvas.height = Math.round(this.h * this.dpr);
    this.ctx.setTransform(this.dpr, 0, 0, this.dpr, 0, 0);
    this._bakeCardSky();
  }

  setVariant(variant) {
    this.variant = variant;
    this.model = this.modelsBundle[variant] || { faces: [], lines: [] };
    this.yaw = 0.46;
    this.pitch = 0.36;
    this.zoom = 1.08;
    this._resize();
    this.render();
  }

  setExplode(val) {
    this.explode = Math.max(0, Math.min(1, val));
    this.render();
  }

  toggleWireframe() {
    this.wireOnly = !this.wireOnly;
    this.render();
    return this.wireOnly;
  }

  _displace(pt, part = 0) {
    if (this.explode <= 0.001) return pt;
    const lift = (part - 0.5) * 14 * this.explode;
    return [pt[0], pt[1] + lift, pt[2]];
  }

  // WHY: Right-handed front-above perspective (camDist - z2) ensures +Z forecourt elements (Open Codex, mullions, pools) face the viewer from above.
  _project(pt, part = 0) {
    const [vx, vy, vz] = this._displace(pt, part);
    const cyaw = Math.cos(this.yaw);
    const syaw = Math.sin(this.yaw);
    const cpitch = Math.cos(this.pitch);
    const spitch = Math.sin(this.pitch);

    const x1 = vx * cyaw + vz * syaw;
    const z1 = -vx * syaw + vz * cyaw;
    const y2 = vy * cpitch - z1 * spitch;
    const z2 = vy * spitch + z1 * cpitch;

    const fov = Math.min(this.w, this.h * 1.72) * 1.16 * this.zoom;
    const camDist = 204;
    const scale = fov / Math.max(60, camDist - z2);
    return {
      sx: this.w * 0.5 + x1 * scale,
      sy: this.h * 0.58 - y2 * scale,
      z: z2
    };
  }

  _rotateNormal(nx, ny, nz) {
    const cyaw = Math.cos(this.yaw);
    const syaw = Math.sin(this.yaw);
    const cpitch = Math.cos(this.pitch);
    const spitch = Math.sin(this.pitch);
    const nx1 = nx * cyaw + nz * syaw;
    const nz1 = -nx * syaw + nz * cyaw;
    const ny2 = ny * cpitch - nz1 * spitch;
    const nz2 = ny * spitch + nz1 * cpitch;
    return [nx1, ny2, nz2];
  }

  _bindEvents() {
    this.mqReduced.addEventListener("change", (e) => {
      this.reducedMotion = e.matches;
      this.autoSpin = !this.reducedMotion;
      if (!this.reducedMotion) this._loop();
      else this.render();
    });

    window.addEventListener("resize", () => {
      this._resize();
      this.render();
    });

    this.canvas.addEventListener("pointerdown", (ev) => {
      this.dragging = true;
      this.lastPt = { x: ev.clientX, y: ev.clientY };
      this.canvas.setPointerCapture(ev.pointerId);
    });

    this.canvas.addEventListener("pointermove", (ev) => {
      if (!this.dragging) return;
      const dx = ev.clientX - this.lastPt.x;
      const dy = ev.clientY - this.lastPt.y;
      this.yaw -= dx * 0.012;
      this.pitch = Math.max(-0.42, Math.min(1.24, this.pitch + dy * 0.010));
      this.lastPt = { x: ev.clientX, y: ev.clientY };
      this.render();
    });

    const stop = () => { this.dragging = false; };
    this.canvas.addEventListener("pointerup", stop);
    this.canvas.addEventListener("pointercancel", stop);

    this.canvas.addEventListener("wheel", (ev) => {
      ev.preventDefault();
      this.zoom = Math.max(0.74, Math.min(1.85, this.zoom - ev.deltaY * 0.001));
      this.render();
    }, { passive: false });

    this.canvas.addEventListener("keydown", (ev) => {
      if (ev.key === "ArrowLeft") { this.yaw += 0.14; this.render(); ev.preventDefault(); }
      if (ev.key === "ArrowRight") { this.yaw -= 0.14; this.render(); ev.preventDefault(); }
      if (ev.key === "ArrowUp") { this.pitch = Math.min(1.24, this.pitch + 0.10); this.render(); ev.preventDefault(); }
      if (ev.key === "ArrowDown") { this.pitch = Math.max(-0.42, this.pitch - 0.10); this.render(); ev.preventDefault(); }
    });
  }

  _loop() {
    if (this._running) return;
    this._running = true;
    const step = () => {
      if (this.reducedMotion) {
        this._running = false;
        return;
      }
      if (isCanvasVisible(this.canvas)) {
        this.time += 0.016;
        if (this.autoSpin && !this.dragging) {
          this.yaw += 0.0046;
        }
        this.render();
      }
      requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }

  render() {
    const ctx = this.ctx;
    if (this.bgSky) {
      ctx.drawImage(this.bgSky, 0, 0, this.w, this.h);
    } else {
      ctx.fillStyle = "#061128";
      ctx.fillRect(0, 0, this.w, this.h);
    }

    const plinthGlow = ctx.createRadialGradient(this.w * 0.5, this.h * 0.64, 6, this.w * 0.5, this.h * 0.64, Math.min(this.w, this.h) * 0.62);
    plinthGlow.addColorStop(0, "rgba(56, 189, 248, 0.22)");
    plinthGlow.addColorStop(0.55, "rgba(251, 191, 36, 0.08)");
    plinthGlow.addColorStop(1, "rgba(6, 17, 40, 0)");
    ctx.fillStyle = plinthGlow;
    ctx.fillRect(0, 0, this.w, this.h);

    const kLx = -0.42;
    const kLy = 0.74;
    const kLz = 0.52;
    const rLx = 0.58;
    const rLy = 0.34;
    const rLz = -0.74;
    const hx = -0.24;
    const hy = 0.43;
    const hz = 0.87;

    const drawList = [];
    const faces = this.model.faces || [];
    const lines = this.model.lines || [];

    for (let i = 0; i < faces.length; i++) {
      const f = faces[i];
      const proj = f.pts.map((p) => this._project(p, f.part || 0));
      const avgZ = proj.reduce((acc, p) => acc + p.z, 0) / proj.length;
      const [onx, ony, onz] = computeNormal(f.pts);
      const [vnx, vny, vnz] = this._rotateNormal(onx, ony, onz);

      const keyDot = Math.abs(vnx * kLx + vny * kLy + vnz * kLz);
      const rimDot = Math.max(0, vnx * rLx + vny * rLy + vnz * rLz);
      const specDot = Math.abs(vnx * hx + vny * hy + vnz * hz);
      const spec = Math.pow(specDot, 14);
      const depthCue = Math.max(-0.12, Math.min(0.16, avgZ / 210));

      const shade = 0.64 + 0.56 * keyDot + depthCue + (f.emissive ? 0.32 : 0);
      const litFill = shadeHex(
        f.fill,
        shade,
        f.emissive ? 0.28 : 0.06,
        spec * (f.emissive ? 0.52 : 0.34),
        rimDot * 0.28
      );
      drawList.push({ z: avgZ, type: "face", proj, f, litFill, spec, rimDot });
    }

    for (let i = 0; i < lines.length; i++) {
      const ln = lines[i];
      const a = this._project(ln.p0, ln.part || 0);
      const b = this._project(ln.p1, ln.part || 0);
      drawList.push({ z: (a.z + b.z) * 0.5 + 0.6, type: "line", a, b, ln });
    }

    drawList.sort((a, b) => a.z - b.z);

    for (let i = 0; i < drawList.length; i++) {
      const item = drawList[i];
      if (item.type === "face") {
        ctx.beginPath();
        ctx.moveTo(item.proj[0].sx, item.proj[0].sy);
        for (let k = 1; k < item.proj.length; k++) {
          ctx.lineTo(item.proj[k].sx, item.proj[k].sy);
        }
        ctx.closePath();
        if (!this.wireOnly) {
          ctx.globalAlpha = Math.min(1, item.f.alpha + item.spec * 0.08);
          ctx.fillStyle = item.litFill;
          ctx.fill();
        }
        const hiEdge = item.spec > 0.42 || item.f.emissive;
        ctx.globalAlpha = this.wireOnly ? 0.95 : (hiEdge ? 0.92 : 0.80);
        ctx.strokeStyle = hiEdge && !this.wireOnly
          ? shadeHex(item.f.stroke, 1.18, 0.08, item.spec * 0.42)
          : item.f.stroke;
        ctx.lineWidth = this.wireOnly ? 1.08 : (hiEdge ? 1.02 : 0.84);
        ctx.stroke();

        if (!this.wireOnly && item.spec > 0.50 && item.proj.length >= 2) {
          ctx.globalAlpha = Math.min(0.76, item.spec * 0.72);
          ctx.strokeStyle = "#fef9c3";
          ctx.lineWidth = 1.25;
          ctx.beginPath();
          ctx.moveTo(item.proj[0].sx, item.proj[0].sy);
          ctx.lineTo(item.proj[1].sx, item.proj[1].sy);
          ctx.stroke();
        }
      } else {
        ctx.globalAlpha = 0.95;
        ctx.strokeStyle = shadeHex(item.ln.stroke, 1.12, 0.04);
        ctx.lineWidth = (item.ln.width || 1.0) * 1.06;
        ctx.beginPath();
        ctx.moveTo(item.a.sx, item.a.sy);
        ctx.lineTo(item.b.sx, item.b.sy);
        ctx.stroke();
      }
    }
    ctx.globalAlpha = 1;

    if (this.model.transit) {
      for (const dir of [0, 0.5]) {
        const u = (this.time * 0.22 + dir) % 1;
        const px = dir === 0 ? -66 + u * 132 : 66 - u * 132;
        const camber = 1.8 * (1 - (px / 68) ** 2);
        const tp = this._project([px, -3.5 + camber, dir === 0 ? -2.8 : 2.8], 1);
        drawStarReticle(ctx, tp.sx, tp.sy, 5.2, 2.0, 4, this.time);
        ctx.fillStyle = dir === 0 ? "#fde047" : "#7dd3fc";
        ctx.fill();
      }
    }
  }
}
