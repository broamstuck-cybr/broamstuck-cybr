// SPDX-License-Identifier: MIT
// WHY: Self-contained 3D perspective mesh renderer, 5D Schlegel projector, and Retina glyph-portrait engine with zero external CDN risk.

export class PortraitStage {
  constructor(canvas, portraitData) {
    this.canvas = canvas;
    this.ctx = canvas.getContext("2d");
    this.data = portraitData;
    this.mode = "weave";
    this.reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    this.pointer = { nx: 0.5, ny: 0.5, inside: false };
    this.angle = 0;

    this.size = 560;
    this.canvas.width = this.size;
    this.canvas.height = this.size;

    this.offscreen = document.createElement("canvas");
    this.offscreen.width = this.size;
    this.offscreen.height = this.size;
    this._bakeBase();
    this._bindEvents();
    this.render();
    if (!this.reducedMotion) {
      this._animate();
    }
  }

  setMode(mode) {
    this.mode = mode;
    this._bakeBase();
    this.render();
  }

  _bakeBase() {
    const oc = this.offscreen.getContext("2d");
    const sz = this.size;
    const cx = sz / 2;
    const cy = sz / 2;
    const r = sz * 0.455;
    const diam = r * 2;
    const x0 = cx - r;
    const y0 = cy - r;

    oc.clearRect(0, 0, sz, sz);
    oc.save();
    oc.beginPath();
    oc.arc(cx, cy, r, 0, Math.PI * 2);
    oc.clip();

    oc.fillStyle = "#060c1a";
    oc.fillRect(x0, y0, diam, diam);

    const atmosN = Math.max(1, this.data.atmos_n || 48);
    const atmos = this.data.atmos || [];
    const cellStep = diam / atmosN;
    oc.save();
    oc.globalAlpha = this.mode === "relief" ? 0.84 : 0.62;
    for (let i = 0; i < atmos.length; i++) {
      const [ax, ay, col] = atmos[i];
      const px = x0 + (ax + 0.5) * cellStep;
      const py = y0 + (ay + 0.5) * cellStep;
      const g = oc.createRadialGradient(px, py, 0, px, py, cellStep * 1.35);
      g.addColorStop(0, col);
      g.addColorStop(1, "rgba(6, 12, 26, 0)");
      oc.fillStyle = g;
      oc.beginPath();
      oc.arc(px, py, cellStep * 1.35, 0, Math.PI * 2);
      oc.fill();
    }
    oc.restore();

    if (this.mode === "impasto") {
      oc.save();
      oc.lineCap = "round";
      for (let i = 0; i < 110; i++) {
        const u = (i * 0.6180339) % 1;
        const v = ((i * 0.381966) % 1) * 0.46;
        if (u > 0.36 && u < 0.61 && v > 0.41) continue;
        const sx = x0 + u * diam;
        const sy = y0 + v * diam;
        const ang = Math.sin(u * 8.5) * 0.45 - 0.12;
        oc.strokeStyle = i % 3 === 0 ? "rgba(253, 224, 71, 0.34)" : "rgba(96, 165, 250, 0.30)";
        oc.lineWidth = 2.4;
        oc.beginPath();
        oc.moveTo(sx - Math.cos(ang) * 11, sy - Math.sin(ang) * 11);
        oc.quadraticCurveTo(sx, sy - 4, sx + Math.cos(ang) * 11, sy + Math.sin(ang) * 11);
        oc.stroke();
      }
      oc.restore();
    }

    const cols = Math.max(1, this.data.cols || 156);
    const rows = Math.max(1, this.data.rows || 86);
    const grid = this.data.grid || [];
    const rowStep = diam / rows;
    const colStep = diam / cols;
    const fontSz = Math.max(3.2, diam / (cols * 0.595));

    oc.font = `700 ${fontSz.toFixed(2)}px 'JetBrains Mono', ui-monospace, monospace`;
    oc.textBaseline = "alphabetic";
    oc.globalAlpha = this.mode === "relief" ? 0.80 : 0.98;

    for (let rIdx = 0; rIdx < grid.length; rIdx++) {
      const runs = grid[rIdx];
      const py = y0 + (rIdx + 0.82) * rowStep;
      let colCursor = 0;
      for (let k = 0; k < runs.length; k++) {
        const [colHex, chunk] = runs[k];
        if (colHex) {
          oc.fillStyle = colHex;
          for (let c = 0; c < chunk.length; c++) {
            const ch = chunk[c];
            if (ch !== " ") {
              oc.fillText(ch, x0 + (colCursor + c) * colStep, py);
            }
          }
        }
        colCursor += chunk.length;
      }
    }
    oc.globalAlpha = 1;

    const contours = this.data.contours || [];
    oc.lineCap = "round";
    for (let i = 0; i < contours.length; i++) {
      const [cx0, cy0, cx1, cy1, scol, sop] = contours[i];
      oc.strokeStyle = scol;
      oc.globalAlpha = this.mode === "relief" ? Math.min(0.92, sop * 1.35) : sop;
      oc.lineWidth = this.mode === "relief" ? 1.45 : 1.05;
      oc.beginPath();
      oc.moveTo(x0 + cx0 * diam, y0 + cy0 * diam);
      oc.lineTo(x0 + cx1 * diam, y0 + cy1 * diam);
      oc.stroke();
    }
    oc.restore();
  }

  _bindEvents() {
    const updatePointer = (ev) => {
      const rect = this.canvas.getBoundingClientRect();
      const nx = (ev.clientX - rect.left) / Math.max(1, rect.width);
      const ny = (ev.clientY - rect.top) / Math.max(1, rect.height);
      const dist = Math.hypot(nx - 0.5, ny - 0.5);
      this.pointer = { nx, ny, inside: dist <= 0.48 };
      if (this.reducedMotion) this.render();
    };
    this.canvas.addEventListener("pointermove", updatePointer);
    this.canvas.addEventListener("pointerdown", updatePointer);
    this.canvas.addEventListener("pointerleave", () => {
      this.pointer.inside = false;
      if (this.reducedMotion) this.render();
    });
  }

  _animate() {
    const step = () => {
      this.angle += 0.0045;
      this.render();
      requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }

  render() {
    const ctx = this.ctx;
    const sz = this.size;
    const cx = sz / 2;
    const cy = sz / 2;
    const r = sz * 0.455;

    ctx.clearRect(0, 0, sz, sz);

    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(this.angle * 0.35);
    ctx.strokeStyle = "rgba(125, 211, 252, 0.32)";
    ctx.lineWidth = 1.4;
    ctx.setLineDash([5, 7]);
    ctx.beginPath();
    ctx.arc(0, 0, r + 17, 0, Math.PI * 2);
    ctx.stroke();
    ctx.setLineDash([]);

    for (let deg = 0; deg < 360; deg += 10) {
      const rad = (deg * Math.PI) / 180;
      const r0 = r + 5;
      const r1 = r + (deg % 30 === 0 ? 14 : 9);
      ctx.strokeStyle = deg % 90 === 0 ? "rgba(253, 230, 138, 0.85)" : "rgba(125, 211, 252, 0.38)";
      ctx.lineWidth = deg % 30 === 0 ? 1.5 : 0.9;
      ctx.beginPath();
      ctx.moveTo(Math.cos(rad) * r0, Math.sin(rad) * r0);
      ctx.lineTo(Math.cos(rad) * r1, Math.sin(rad) * r1);
      ctx.stroke();
    }

    const satX = Math.cos(this.angle * 1.4) * (r + 14);
    const satY = Math.sin(this.angle * 1.4) * (r + 14);
    ctx.fillStyle = "#fde047";
    ctx.beginPath();
    ctx.arc(satX, satY, 3.6, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();

    const tiltX = this.pointer.inside ? (this.pointer.nx - 0.5) * 8 : 0;
    const tiltY = this.pointer.inside ? (this.pointer.ny - 0.5) * 8 : 0;
    ctx.save();
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.clip();
    ctx.drawImage(this.offscreen, tiltX, tiltY);
    ctx.restore();

    ctx.strokeStyle = "rgba(253, 230, 138, 0.58)";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.stroke();

    if (this.pointer.inside) {
      const lx = this.pointer.nx * sz;
      const ly = this.pointer.ny * sz;
      const loupeR = 76;
      const zoom = 2.85;

      ctx.save();
      ctx.beginPath();
      ctx.arc(lx, ly, loupeR, 0, Math.PI * 2);
      ctx.clip();
      ctx.fillStyle = "#050b18";
      ctx.fillRect(lx - loupeR, ly - loupeR, loupeR * 2, loupeR * 2);
      ctx.drawImage(
        this.offscreen,
        lx - loupeR / zoom,
        ly - loupeR / zoom,
        (loupeR * 2) / zoom,
        (loupeR * 2) / zoom,
        lx - loupeR,
        ly - loupeR,
        loupeR * 2,
        loupeR * 2
      );
      ctx.restore();

      ctx.strokeStyle = "#fde047";
      ctx.lineWidth = 2.4;
      ctx.beginPath();
      ctx.arc(lx, ly, loupeR, 0, Math.PI * 2);
      ctx.stroke();

      ctx.strokeStyle = "rgba(125, 211, 252, 0.55)";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.arc(lx, ly, loupeR - 4, 0, Math.PI * 2);
      ctx.stroke();
    }
  }
}

export class Radar5DStage {
  constructor(canvas, langs5d, onSelect) {
    this.canvas = canvas;
    this.ctx = canvas.getContext("2d");
    this.langs = langs5d || [];
    this.onSelect = onSelect;
    this.reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    this.yaw = -0.38;
    this.pitch = 0.96;
    this.wFold = -0.45;
    this.autoOrbit = !this.reducedMotion;
    this.selected = null;
    this.time = 0;
    this.dragging = false;
    this.lastPt = { x: 0, y: 0 };
    this.hitNodes = [];

    this.w = 640;
    this.h = 314;
    this.canvas.width = this.w;
    this.canvas.height = this.h;

    this._bindEvents();
    this.render();
    if (!this.reducedMotion) {
      this._loop();
    }
  }

  setWFold(val) {
    this.wFold = val;
    this.render();
  }

  setSelected(name) {
    this.selected = name;
    this.render();
    if (this.onSelect) this.onSelect(this.selected);
  }

  toggleOrbit() {
    this.autoOrbit = !this.autoOrbit;
    if (this.autoOrbit && this.reducedMotion) {
      this.reducedMotion = false;
      this._loop();
    }
    return this.autoOrbit;
  }

  _project5D(x, y, z, wCoord) {
    const cx = this.w * 0.5;
    const cy = this.h * 0.57;
    const wScale = 1 / (1 + 0.28 * (1 - wCoord));
    const xw = x * wScale;
    const yw = y * wScale;
    const zw = z * wScale + wCoord * 14;

    const cyaw = Math.cos(this.yaw);
    const syaw = Math.sin(this.yaw);
    const rx = xw * cyaw - yw * syaw;
    const ry = xw * syaw + yw * cyaw;

    const sx = cx + rx;
    const sy = cy + ry * Math.cos(this.pitch) - zw * Math.sin(this.pitch);
    return { sx, sy, depth: ry };
  }

  _bindEvents() {
    this.canvas.addEventListener("pointerdown", (ev) => {
      this.dragging = true;
      this.moved = false;
      this.lastPt = { x: ev.clientX, y: ev.clientY };
      this.canvas.setPointerCapture(ev.pointerId);
    });

    this.canvas.addEventListener("pointermove", (ev) => {
      if (!this.dragging) return;
      const dx = ev.clientX - this.lastPt.x;
      const dy = ev.clientY - this.lastPt.y;
      if (Math.hypot(dx, dy) > 2) this.moved = true;
      this.yaw += dx * 0.011;
      this.pitch = Math.max(0.42, Math.min(1.32, this.pitch + dy * 0.008));
      this.lastPt = { x: ev.clientX, y: ev.clientY };
      this.render();
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
          if (Math.hypot(px - hn.x, py - hn.y) < 24) {
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
      if (ev.key === "ArrowDown") { this.pitch = Math.min(1.32, this.pitch + 0.08); this.render(); ev.preventDefault(); }
    });
  }

  _loop() {
    if (this._loopRunning) return;
    this._loopRunning = true;
    const step = () => {
      this.time += 0.016;
      if (this.autoOrbit && !this.dragging) {
        this.yaw += 0.0038;
      }
      if (this.autoOrbit || !this.reducedMotion) {
        this.render();
      }
      requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }

  render() {
    const ctx = this.ctx;
    const rMax = 130;
    const crownZ = 78;
    const apexZ = 96;
    ctx.clearRect(0, 0, this.w, this.h);

    const glow = ctx.createRadialGradient(this.w * 0.5, this.h * 0.52, 10, this.w * 0.5, this.h * 0.52, 210);
    glow.addColorStop(0, "rgba(56, 189, 248, 0.13)");
    glow.addColorStop(0.55, "rgba(251, 191, 36, 0.06)");
    glow.addColorStop(1, "rgba(5, 10, 22, 0)");
    ctx.fillStyle = glow;
    ctx.fillRect(0, 0, this.w, this.h);

    ctx.beginPath();
    for (let deg = 0; deg <= 360; deg += 6) {
      const rad = (deg * Math.PI) / 180;
      const p = this._project5D(Math.cos(rad) * rMax * 1.08, Math.sin(rad) * rMax * 1.08, 0, 1);
      if (deg === 0) ctx.moveTo(p.sx, p.sy);
      else ctx.lineTo(p.sx, p.sy);
    }
    ctx.fillStyle = "rgba(7, 16, 33, 0.78)";
    ctx.fill();
    ctx.strokeStyle = "rgba(62, 95, 148, 0.72)";
    ctx.lineWidth = 1.2;
    ctx.stroke();

    for (const rf of [0.32, 0.58, 0.84]) {
      ctx.beginPath();
      for (let i = 0; i <= 6; i++) {
        const ang = -Math.PI / 2 + (i % 6) * (Math.PI / 3);
        const p = this._project5D(Math.cos(ang) * rMax * rf, Math.sin(ang) * rMax * rf, 0, 1);
        if (i === 0) ctx.moveTo(p.sx, p.sy);
        else ctx.lineTo(p.sx, p.sy);
      }
      ctx.strokeStyle = "rgba(46, 70, 110, 0.55)";
      ctx.lineWidth = 0.9;
      ctx.stroke();
    }

    for (let m = 0; m < 2; m++) {
      const zAmp = m === 0 ? 34 : -28;
      ctx.save();
      ctx.beginPath();
      for (let deg = 0; deg <= 360; deg += 10) {
        const rad = (deg * Math.PI) / 180;
        const p = this._project5D(
          Math.cos(rad) * rMax * 0.96,
          Math.sin(rad) * rMax * 0.96,
          28 + Math.sin(rad + m * 1.2) * zAmp,
          1
        );
        if (deg === 0) ctx.moveTo(p.sx, p.sy);
        else ctx.lineTo(p.sx, p.sy);
      }
      ctx.setLineDash([4, 4]);
      ctx.strokeStyle = m === 0 ? "rgba(125, 211, 252, 0.30)" : "rgba(253, 224, 71, 0.28)";
      ctx.lineWidth = 1;
      ctx.stroke();
      ctx.restore();

      const oAng = this.time * (m === 0 ? 0.65 : -0.48) + m * 2.1;
      const op = this._project5D(
        Math.cos(oAng) * rMax * 0.96,
        Math.sin(oAng) * rMax * 0.96,
        28 + Math.sin(oAng + m * 1.2) * zAmp,
        1
      );
      ctx.fillStyle = m === 0 ? "#7dd3fc" : "#fde047";
      ctx.beginPath();
      ctx.arc(op.sx, op.sy, 3.0, 0, Math.PI * 2);
      ctx.fill();
    }

    const origin = this._project5D(0, 0, 0, 1);
    const zenith = this._project5D(0, 0, apexZ, 1);
    const innerZenith = this._project5D(0, 0, apexZ * 0.56, this.wFold);

    const n = this.langs.length || 6;
    const outerV = [];
    const innerV = [];
    const labelAnchors = [];

    for (let i = 0; i < n; i++) {
      const item = this.langs[i];
      const ang = -Math.PI / 2 + (i * Math.PI * 2) / n;
      const reach = 0.28 + 0.72 * Math.min(1, item.d2Volume);
      const elev = 14 + crownZ * (0.45 * Math.min(1, item.d2Volume) + 0.55 * item.d3Breadth);
      const wx = Math.cos(ang) * rMax * reach;
      const wy = Math.sin(ang) * rMax * reach;

      const ov = this._project5D(wx, wy, elev, 1);
      const bv = this._project5D(wx, wy, 0, 1);
      const iv = this._project5D(
        Math.cos(ang) * rMax * (reach * 0.54 * (0.65 + 0.35 * item.d4Gravity)),
        Math.sin(ang) * rMax * (reach * 0.54 * (0.65 + 0.35 * item.d4Gravity)),
        elev * 0.54 + 8,
        this.wFold
      );
      const axisOuter = this._project5D(Math.cos(ang) * rMax * 1.18, Math.sin(ang) * rMax * 1.18, crownZ * 0.45, 1);

      ctx.strokeStyle = "rgba(46, 70, 110, 0.52)";
      ctx.lineWidth = 0.85;
      ctx.beginPath();
      ctx.moveTo(origin.sx, origin.sy);
      ctx.lineTo(bv.sx, bv.sy);
      ctx.stroke();

      outerV.push({ ...ov, bx: bv.sx, by: bv.sy, bdepth: bv.depth, item });
      innerV.push({ ...iv, item });
      labelAnchors.push(axisOuter);
    }

    const facets = [];
    for (let i = 0; i < n; i++) {
      const j = (i + 1) % n;
      const vi = outerV[i];
      const vj = outerV[j];
      const ii = innerV[i];
      const ij = innerV[j];

      facets.push({
        depth: (innerZenith.depth + ii.depth + ij.depth) / 3 - 4,
        pts: [innerZenith, ii, ij],
        fill: i % 2 === 0 ? "rgba(96, 165, 250, 0.32)" : "rgba(253, 224, 71, 0.28)",
        stroke: "rgba(219, 234, 254, 0.78)",
        lw: 1.0
      });

      facets.push({
        depth: (vi.bdepth + vj.bdepth + vi.depth + vj.depth) / 4 - 2,
        pts: [{ sx: vi.bx, sy: vi.by }, { sx: vj.bx, sy: vj.by }, vj, vi],
        fill: "rgba(14, 41, 75, 0.34)",
        stroke: "rgba(94, 234, 212, 0.45)",
        lw: 0.85
      });

      facets.push({
        depth: (zenith.depth + vi.depth + vj.depth) / 3,
        pts: [zenith, vi, vj],
        fill: vi.item.color + "38",
        stroke: "rgba(253, 230, 138, 0.78)",
        lw: 1.15
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
    }

    for (let i = 0; i < n; i++) {
      ctx.strokeStyle = i % 2 === 0 ? "rgba(253, 224, 71, 0.82)" : "rgba(94, 234, 212, 0.82)";
      ctx.lineWidth = 1.15;
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
    ctx.strokeStyle = "#fde68a";
    ctx.lineWidth = 1.75;
    ctx.stroke();

    this.hitNodes = [];
    ctx.font = "600 12px 'JetBrains Mono', ui-monospace, monospace";
    ctx.textBaseline = "middle";

    for (let i = 0; i < n; i++) {
      const ov = outerV[i];
      const it = ov.item;
      const isSel = this.selected === it.name;

      ctx.fillStyle = isSel ? "#ffffff" : it.highlight;
      ctx.beginPath();
      ctx.arc(ov.sx, ov.sy, isSel ? 6.2 : 4.2, 0, Math.PI * 2);
      ctx.fill();
      ctx.strokeStyle = it.color;
      ctx.lineWidth = 2;
      ctx.stroke();

      const la = labelAnchors[i];
      const pctStr = it.percent > 0 ? `${it.percent}%` : "<1%";
      const label = `${it.name} ${pctStr}`;
      const alignLeft = la.sx < this.w * 0.46;
      const alignRight = la.sx > this.w * 0.54;
      ctx.textAlign = alignLeft ? "right" : (alignRight ? "left" : "center");
      const lx = Math.max(12, Math.min(this.w - 12, la.sx + (alignLeft ? -6 : (alignRight ? 6 : 0))));
      const ly = Math.max(18, Math.min(this.h - 16, la.sy + (la.sy < this.h * 0.35 ? -8 : 6)));

      ctx.fillStyle = isSel ? "#fde047" : it.color;
      ctx.fillText(label, lx, ly);

      this.hitNodes.push({ name: it.name, x: ov.sx, y: ov.sy });
      this.hitNodes.push({ name: it.name, x: lx, y: ly });
    }
  }
}

function buildCitadelModel() {
  const faces = [];
  const lines = [];

  const tiers = [
    [56, -26, -19, "#0d2136", "#081523", "#2c466e"],
    [41, -19, -12, "#123047", "#0a1e2e", "#5eead4"],
    [26, -12, -6, "#163e56", "#0d283a", "#6ee7b7"]
  ];
  for (let t = 0; t < tiers.length; t++) {
    const [rad, yb, yt, ft, fs, strk] = tiers[t];
    const topPts = [];
    const botPts = [];
    for (let k = 0; k < 8; k++) {
      const a = (k * Math.PI) / 4 + Math.PI / 8;
      topPts.push([Math.cos(a) * rad, yt, Math.sin(a) * rad]);
      botPts.push([Math.cos(a) * rad, yb, Math.sin(a) * rad]);
    }
    faces.push({ pts: topPts, fill: ft, stroke: strk, alpha: 0.90 });
    for (let k = 0; k < 8; k++) {
      const nk = (k + 1) % 8;
      faces.push({ pts: [botPts[k], botPts[nk], topPts[nk], topPts[k]], fill: fs, stroke: strk, alpha: 0.92 });
    }
  }

  for (let i = 0; i < 6; i++) {
    const a = (i * Math.PI) / 3 + 0.3;
    const dist = 37;
    const px = Math.cos(a) * dist;
    const pz = Math.sin(a) * dist;
    const tx = -Math.sin(a) * 10.5;
    const tz = Math.cos(a) * 10.5;
    const col = i % 2 === 0 ? "#6ee7b7" : "#7dd3fc";
    faces.push({
      pts: [[px - tx, 2, pz - tz], [px + tx, 2, pz + tz], [px + tx, 16, pz + tz], [px - tx, 16, pz - tz]],
      fill: "#112b45",
      stroke: col,
      alpha: 0.68
    });
    lines.push({ p0: [px, -6, pz], p1: [px, 2, pz], stroke: col, width: 1.0 });
  }

  const apexTop = [0, 34, 0];
  const apexBot = [0, -2, 0];
  const ring = [];
  for (let k = 0; k < 6; k++) {
    const a = (k * Math.PI) / 3;
    ring.push([Math.cos(a) * 15, 15, Math.sin(a) * 15]);
  }
  for (let k = 0; k < 6; k++) {
    const nk = (k + 1) % 6;
    faces.push({ pts: [apexTop, ring[k], ring[nk]], fill: k % 2 === 0 ? "#34d399" : "#38bdf8", stroke: "#fde68a", alpha: 0.44 });
    faces.push({ pts: [apexBot, ring[nk], ring[k]], fill: "#134e4a", stroke: "#6ee7b7", alpha: 0.52 });
  }

  const rings = [[0.36, -0.22, 49, "#fde68a"], [-0.30, 0.32, 45, "#7dd3fc"]];
  for (let r = 0; r < rings.length; r++) {
    const [tx, tz, rad, col] = rings[r];
    let prev = null;
    for (let s = 0; s <= 28; s++) {
      const a = (s * Math.PI * 2) / 28;
      const ox = Math.cos(a) * rad;
      const oz = Math.sin(a) * rad;
      const cur = [ox, 11 + ox * tx + oz * tz, oz];
      if (prev) lines.push({ p0: prev, p1: cur, stroke: col, width: 1.2 });
      prev = cur;
    }
  }

  return { faces, lines, beacon: [0, 34, 0] };
}

function addBox(faces, x0, x1, y0, y1, z0, z1, topFill, sideFill, stroke, alpha = 0.90) {
  faces.push({ pts: [[x0, y1, z0], [x1, y1, z0], [x1, y1, z1], [x0, y1, z1]], fill: topFill, stroke, alpha });
  faces.push({ pts: [[x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0]], fill: sideFill, stroke, alpha });
  faces.push({ pts: [[x1, y0, z0], [x1, y0, z1], [x1, y1, z1], [x1, y1, z0]], fill: sideFill, stroke, alpha });
  faces.push({ pts: [[x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]], fill: sideFill, stroke, alpha });
  faces.push({ pts: [[x0, y0, z0], [x0, y0, z1], [x0, y1, z1], [x0, y1, z0]], fill: sideFill, stroke, alpha });
}

function buildViaductModel() {
  const faces = [];
  const lines = [];

  for (let gz = -24; gz <= 24; gz += 12) {
    lines.push({ p0: [-76, -25, gz], p1: [76, -25, gz], stroke: "rgba(96, 165, 250, 0.28)", width: 0.9 });
  }
  for (const px of [-42, 42]) {
    addBox(faces, px - 9, px + 9, -25, -16, -12, 12, "#152e4f", "#0b192e", "#7dd3fc", 0.92);
  }
  addBox(faces, -78, 78, -8.5, -4.2, -9, 9, "#142c4c", "#0a172b", "#7dd3fc", 0.92);
  lines.push({ p0: [-76, -3.9, 0], p1: [76, -3.9, 0], stroke: "#fde047", width: 1.6 });

  for (const tx of [-42, 42]) {
    for (const sz of [-8, 8]) {
      lines.push({ p0: [tx - 3.2, -16, sz], p1: [tx - 1.0, 34, sz * 0.42], stroke: "#fde68a", width: 2.0 });
      lines.push({ p0: [tx + 3.2, -16, sz], p1: [tx + 1.0, 34, sz * 0.42], stroke: "#fde68a", width: 2.0 });
    }
    for (const [py, zScale] of [[5, 0.78], [19, 0.58], [33, 0.44]]) {
      lines.push({ p0: [tx, py, -8 * zScale], p1: [tx, py, 8 * zScale], stroke: "#fbbf24", width: 1.5 });
    }
    lines.push({ p0: [tx, 5, -6.2], p1: [tx, 19, 4.6], stroke: "#7dd3fc", width: 1.0 });
    lines.push({ p0: [tx, 5, 6.2], p1: [tx, 19, -4.6], stroke: "#7dd3fc", width: 1.0 });
  }

  const cableY = (xVal) => {
    if (Math.abs(xVal) <= 42) {
      const u = xVal / 42;
      return 3 + 31 * u * u;
    }
    const u = (Math.abs(xVal) - 42) / 36;
    return 34 * Math.pow(1 - u, 1.35) - 4 * u;
  };

  for (const [zp, col] of [[-7.6, "#7dd3fc"], [7.6, "#fde047"]]) {
    let prev = null;
    for (let x = -78; x <= 78; x += 6) {
      const cy = cableY(x);
      const cur = [x, cy, zp * (0.45 + 0.55 * (1 - cy / 36))];
      if (prev) lines.push({ p0: prev, p1: cur, stroke: col, width: 1.5 });
      prev = cur;
      if (x % 12 === 0 && Math.abs(x) !== 42 && Math.abs(x) !== 78) {
        lines.push({ p0: [x, -4, zp * 0.85], p1: cur, stroke: "rgba(253, 230, 138, 0.55)", width: 0.9 });
      }
    }
  }

  return { faces, lines, transit: true };
}

function buildRotundaModel() {
  const faces = [];
  const lines = [];

  for (const [rad, yb, yt, ft, fs, strk] of [
    [54, -26, -20, "#15223b", "#0b1324", "#2c466e"],
    [44, -20, -14.5, "#1b2c4b", "#0e192d", "#fbbf24"]
  ]) {
    const topPts = [];
    const botPts = [];
    for (let k = 0; k < 14; k++) {
      const a = (k * Math.PI * 2) / 14;
      topPts.push([Math.cos(a) * rad, yt, Math.sin(a) * rad]);
      botPts.push([Math.cos(a) * rad, yb, Math.sin(a) * rad]);
    }
    faces.push({ pts: topPts, fill: ft, stroke: strk, alpha: 0.90 });
    for (let k = 0; k < 14; k++) {
      const nk = (k + 1) % 14;
      faces.push({ pts: [botPts[k], botPts[nk], topPts[nk], topPts[k]], fill: fs, stroke: strk, alpha: 0.92 });
    }
  }

  const colR = 37;
  for (let k = 0; k < 20; k++) {
    const a0 = (k * Math.PI * 2) / 20;
    const a1 = ((k + 1) * Math.PI * 2) / 20;
    lines.push({
      p0: [Math.cos(a0) * colR, 16, Math.sin(a0) * colR],
      p1: [Math.cos(a1) * colR, 16, Math.sin(a1) * colR],
      stroke: "#fde68a",
      width: 1.5
    });
  }

  for (let k = 0; k < 10; k++) {
    const a = (k * Math.PI * 2) / 10 + 0.2;
    const cx = Math.cos(a) * colR;
    const cz = Math.sin(a) * colR;
    lines.push({ p0: [cx, -14.5, cz], p1: [cx, 16, cz], stroke: "#fefce8", width: 2.1 });
    let prev = [cx, 16, cz];
    for (let s = 1; s <= 5; s++) {
      const u = s / 5;
      const dr = colR * Math.cos(u * Math.PI * 0.44);
      const dy = 16 + Math.sin(u * Math.PI * 0.44) * 19;
      const cur = [Math.cos(a) * dr, dy, Math.sin(a) * dr];
      lines.push({ p0: prev, p1: cur, stroke: k % 2 === 0 ? "#fbbf24" : "#7dd3fc", width: 1.05 });
      prev = cur;
    }
  }

  addBox(faces, -6.5, 6.5, -14.5, -6.5, -5.5, 5.5, "#263757", "#131d33", "#fde68a", 0.94);
  faces.push({ pts: [[-1, -5.5, -10.5], [-20, 0, -9.5], [-20, 0, 10], [-1, -5.5, 11]], fill: "#1e3050", stroke: "#fde047", alpha: 0.96 });
  faces.push({ pts: [[1, -5.5, -10.5], [20, 0, -9.5], [20, 0, 10], [1, -5.5, 11]], fill: "#24395e", stroke: "#fde047", alpha: 0.96 });

  return { faces, lines, beacon: [0, 35, 0], lanterns: true };
}

const MODEL_BUILDERS = {
  v3: buildCitadelModel,
  v2: buildViaductModel,
  v1: buildRotundaModel
};

export class Forum3DStage {
  constructor(canvas, variant = "v3", options = {}) {
    this.canvas = canvas;
    this.ctx = canvas.getContext("2d");
    this.variant = variant;
    this.model = (MODEL_BUILDERS[variant] || buildCitadelModel)();
    this.reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    this.yaw = options.yaw ?? -0.56;
    this.pitch = options.pitch ?? 0.40;
    this.zoom = options.zoom ?? 1.0;
    this.wireOnly = false;
    this.autoSpin = !this.reducedMotion;
    this.time = 0;
    this.dragging = false;
    this.lastPt = { x: 0, y: 0 };

    this.w = options.width || 480;
    this.h = options.height || 246;
    this.canvas.width = this.w;
    this.canvas.height = this.h;

    this._bindEvents();
    this.render();
    if (!this.reducedMotion) {
      this._loop();
    }
  }

  setVariant(variant) {
    this.variant = variant;
    this.model = (MODEL_BUILDERS[variant] || buildCitadelModel)();
    this.yaw = -0.56;
    this.pitch = 0.40;
    this.zoom = 1.05;
    this.render();
  }

  setCameraPreset(preset) {
    if (preset === "top") { this.yaw = -0.4; this.pitch = 1.18; }
    else if (preset === "front") { this.yaw = 0.0; this.pitch = 0.14; }
    else { this.yaw = -0.56; this.pitch = 0.40; }
    this.render();
  }

  toggleWireframe() {
    this.wireOnly = !this.wireOnly;
    this.render();
    return this.wireOnly;
  }

  _project(pt) {
    const [vx, vy, vz] = pt;
    const cyaw = Math.cos(this.yaw);
    const syaw = Math.sin(this.yaw);
    const cpitch = Math.cos(this.pitch);
    const spitch = Math.sin(this.pitch);

    const x1 = vx * cyaw - vz * syaw;
    const z1 = vx * syaw + vz * cyaw;
    const y2 = vy * cpitch - z1 * spitch;
    const z2 = vy * spitch + z1 * cpitch;

    const fov = Math.min(this.w, this.h * 1.65) * 1.12 * this.zoom;
    const camDist = 195;
    const scale = fov / Math.max(55, camDist + z2);
    return {
      sx: this.w * 0.5 + x1 * scale,
      sy: this.h * 0.56 - y2 * scale,
      z: z2
    };
  }

  _bindEvents() {
    this.canvas.addEventListener("pointerdown", (ev) => {
      this.dragging = true;
      this.lastPt = { x: ev.clientX, y: ev.clientY };
      this.canvas.setPointerCapture(ev.pointerId);
    });

    this.canvas.addEventListener("pointermove", (ev) => {
      if (!this.dragging) return;
      const dx = ev.clientX - this.lastPt.x;
      const dy = ev.clientY - this.lastPt.y;
      this.yaw += dx * 0.012;
      this.pitch = Math.max(-0.55, Math.min(1.28, this.pitch + dy * 0.010));
      this.lastPt = { x: ev.clientX, y: ev.clientY };
      this.render();
    });

    const stop = () => { this.dragging = false; };
    this.canvas.addEventListener("pointerup", stop);
    this.canvas.addEventListener("pointercancel", stop);

    this.canvas.addEventListener("wheel", (ev) => {
      ev.preventDefault();
      this.zoom = Math.max(0.72, Math.min(1.80, this.zoom - ev.deltaY * 0.001));
      this.render();
    }, { passive: false });

    this.canvas.addEventListener("keydown", (ev) => {
      if (ev.key === "ArrowLeft") { this.yaw -= 0.14; this.render(); ev.preventDefault(); }
      if (ev.key === "ArrowRight") { this.yaw += 0.14; this.render(); ev.preventDefault(); }
      if (ev.key === "ArrowUp") { this.pitch = Math.min(1.25, this.pitch + 0.10); this.render(); ev.preventDefault(); }
      if (ev.key === "ArrowDown") { this.pitch = Math.max(-0.45, this.pitch - 0.10); this.render(); ev.preventDefault(); }
    });
  }

  _loop() {
    if (this._running) return;
    this._running = true;
    const step = () => {
      this.time += 0.016;
      if (this.autoSpin && !this.dragging) {
        this.yaw += 0.0055;
      }
      if (this.autoSpin || !this.reducedMotion) {
        this.render();
      }
      requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }

  render() {
    const ctx = this.ctx;
    ctx.clearRect(0, 0, this.w, this.h);

    const bg = ctx.createRadialGradient(this.w * 0.5, this.h * 0.48, 8, this.w * 0.5, this.h * 0.48, this.w * 0.62);
    bg.addColorStop(0, "rgba(30, 64, 128, 0.28)");
    bg.addColorStop(0.55, "rgba(10, 20, 42, 0.45)");
    bg.addColorStop(1, "rgba(5, 10, 22, 0.92)");
    ctx.fillStyle = bg;
    ctx.fillRect(0, 0, this.w, this.h);

    for (let i = 0; i < 28; i++) {
      const sx = ((i * 73) % 97) * 0.0103 * this.w;
      const sy = ((i * 41) % 89) * 0.0112 * this.h;
      ctx.fillStyle = i % 3 === 0 ? "rgba(253, 224, 71, 0.55)" : "rgba(186, 230, 253, 0.45)";
      ctx.beginPath();
      ctx.arc(sx, sy, i % 5 === 0 ? 1.4 : 0.85, 0, Math.PI * 2);
      ctx.fill();
    }

    const drawList = [];
    for (let i = 0; i < this.model.faces.length; i++) {
      const f = this.model.faces[i];
      const proj = f.pts.map((p) => this._project(p));
      const avgZ = proj.reduce((acc, p) => acc + p.z, 0) / proj.length;
      drawList.push({ z: avgZ, type: "face", proj, f });
    }
    for (let i = 0; i < this.model.lines.length; i++) {
      const ln = this.model.lines[i];
      const a = this._project(ln.p0);
      const b = this._project(ln.p1);
      drawList.push({ z: (a.z + b.z) * 0.5 - 0.6, type: "line", a, b, ln });
    }

    drawList.sort((a, b) => b.z - a.z);

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
          ctx.globalAlpha = item.f.alpha;
          ctx.fillStyle = item.f.fill;
          ctx.fill();
        }
        ctx.globalAlpha = 0.88;
        ctx.strokeStyle = item.f.stroke;
        ctx.lineWidth = 1.05;
        ctx.stroke();
      } else {
        ctx.globalAlpha = 0.92;
        ctx.strokeStyle = item.ln.stroke;
        ctx.lineWidth = item.ln.width;
        ctx.beginPath();
        ctx.moveTo(item.a.sx, item.a.sy);
        ctx.lineTo(item.b.sx, item.b.sy);
        ctx.stroke();
      }
    }
    ctx.globalAlpha = 1;

    if (this.model.beacon) {
      const bp = this._project(this.model.beacon);
      const g = ctx.createRadialGradient(bp.sx, bp.sy, 1, bp.sx, bp.sy, 15);
      g.addColorStop(0, "rgba(255, 255, 255, 0.98)");
      g.addColorStop(0.35, "rgba(253, 224, 71, 0.65)");
      g.addColorStop(1, "rgba(253, 224, 71, 0)");
      ctx.fillStyle = g;
      ctx.beginPath();
      ctx.arc(bp.sx, bp.sy, 15, 0, Math.PI * 2);
      ctx.fill();
    }

    if (this.model.transit) {
      const u = (this.time * 0.24) % 1;
      const px = -74 + u * 148;
      const tp = this._project([px, -3.6, 0]);
      ctx.fillStyle = "#fde047";
      ctx.beginPath();
      ctx.arc(tp.sx, tp.sy, 3.4, 0, Math.PI * 2);
      ctx.fill();
    }

    if (this.model.lanterns) {
      for (let k = 0; k < 3; k++) {
        const a = this.time * 0.7 + (k * Math.PI * 2) / 3;
        const lp = this._project([Math.cos(a) * 26, 8 + Math.sin(a * 2) * 2.5, Math.sin(a) * 26]);
        ctx.fillStyle = k === 0 ? "#fde047" : (k === 1 ? "#7dd3fc" : "#6ee7b7");
        ctx.beginPath();
        ctx.arc(lp.sx, lp.sy, 2.8, 0, Math.PI * 2);
        ctx.fill();
      }
    }
  }
}
