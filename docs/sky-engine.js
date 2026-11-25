// SPDX-License-Identifier: MIT
// WHY: Synthesizes Van Gogh Starry Night, Sunflowers, and Provence Cypresses with tapered dual-tone impasto brushwork, lifted celestial radiance, Navier-Stokes cursor flow, and 4-plane parallax.

const PLANETS = [
  { key: "mercury", name: "Mercury", period: "88d", rf: 0.17, r: 2.6, color: "#e2e8f0", speed: 1.62, phase: 0.4 },
  { key: "venus", name: "Venus", period: "225d", rf: 0.26, r: 3.5, color: "#fef08a", speed: 1.18, phase: 1.9 },
  { key: "earth", name: "Earth", period: "365d", rf: 0.36, r: 3.9, color: "#38bdf8", speed: 0.88, phase: 3.5 },
  { key: "mars", name: "Mars", period: "687d", rf: 0.47, r: 3.1, color: "#fb7185", speed: 0.68, phase: 5.1 },
  { key: "jupiter", name: "Jupiter", period: "11.9y", rf: 0.61, r: 5.4, color: "#fbbf24", speed: 0.45, phase: 0.9 },
  { key: "saturn", name: "Saturn", period: "29.5y", rf: 0.76, r: 4.6, color: "#fde047", speed: 0.32, phase: 2.8, ring: true },
  { key: "uranus", name: "Uranus", period: "84y", rf: 0.88, r: 3.6, color: "#67e8f9", speed: 0.23, phase: 4.4, tiltRing: true },
  { key: "neptune", name: "Neptune", period: "165y", rf: 0.99, r: 3.5, color: "#60a5fa", speed: 0.17, phase: 5.8 }
];

const WAKE_GLYPHS = ["*", "~", "+", "@", "/", "\\", "(", ")", "%", "#"];
const WAKE_COLORS = ["#fde047", "#fbbf24", "#7dd3fc", "#93c5fd", "#fef08a", "#34d399"];
const FLOW_PALETTE = ["#60a5fa", "#93c5fd", "#e0f2fe", "#38bdf8", "#fde68a", "#fde047"];

const PAN_STARS = [
  [0.09, 0.09, 13, true],
  [0.23, 0.25, 15, true],
  [0.34, 0.56, 22, true],
  [0.56, 0.17, 14, false],
  [0.71, 0.30, 15, true],
  [0.895, 0.255, 30, true]
];

const PAN_SUNFLOWERS = [
  [0.036, 0.81, 21],
  [0.088, 0.88, 18],
  [0.964, 0.82, 20],
  [0.914, 0.89, 17]
];

const GAR_SUNFLOWERS = [
  [0.044, 0.57, 25],
  [0.114, 0.67, 27],
  [0.058, 0.83, 24],
  [0.176, 0.79, 23],
  [0.242, 0.88, 19],
  [0.956, 0.57, 25],
  [0.886, 0.67, 27],
  [0.942, 0.83, 24],
  [0.824, 0.79, 23],
  [0.758, 0.88, 19]
];

const COLOR_CACHE = new Map();

function getColorMeta(hex) {
  if (!hex || hex[0] !== "#" || hex.length < 7) {
    return { r: 125, g: 211, b: 252, luma: 0.72, lifted: hex || "#7dd3fc", filament: "#f8fafc" };
  }
  const cached = COLOR_CACHE.get(hex);
  if (cached) return cached;
  const r = parseInt(hex.slice(1, 3), 16) || 0;
  const g = parseInt(hex.slice(3, 5), 16) || 0;
  const b = parseInt(hex.slice(5, 7), 16) || 0;
  const luma = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
  const warm = r >= b;
  const liftAmt = luma < 0.18 ? 0.08 : 0.14;
  const lr = Math.min(255, Math.round(r + (255 - r) * liftAmt + (warm ? 4 : 1)));
  const lg = Math.min(255, Math.round(g + (255 - g) * liftAmt + 3));
  const lb = Math.min(255, Math.round(b + (255 - b) * (warm ? liftAmt * 0.78 : liftAmt * 1.08)));
  const fr = Math.min(255, Math.round(lr + (255 - lr) * (warm ? 0.44 : 0.36)));
  const fg = Math.min(255, Math.round(lg + (255 - lg) * 0.42));
  const fb = Math.min(255, Math.round(lb + (255 - lb) * (warm ? 0.28 : 0.46)));
  const meta = {
    r,
    g,
    b,
    luma,
    lifted: `rgb(${lr}, ${lg}, ${lb})`,
    filament: `rgb(${fr}, ${fg}, ${fb})`
  };
  COLOR_CACHE.set(hex, meta);
  return meta;
}

// WHY: Renders each brushstroke as a feathered, belly-tapered quadratic ribbon with an upper sunlit impasto ridge filament instead of a flat uniform cylinder.
export function drawTaperedImpastoStroke(ctx, x0, y0, xm, ym, x1, y1, hexCol, widthPx, baseAlpha = 0.90) {
  const meta = getColorMeta(hexCol);
  const hw = Math.max(0.45, widthPx * 0.54);

  let tx0 = xm - x0;
  let ty0 = ym - y0;
  let l0 = Math.hypot(tx0, ty0);
  if (l0 < 0.001) {
    tx0 = x1 - x0;
    ty0 = y1 - y0;
    l0 = Math.hypot(tx0, ty0) || 1;
  }
  const nx0 = -ty0 / l0;
  const ny0 = tx0 / l0;

  const txm = x1 - x0;
  const tym = y1 - y0;
  const lm = Math.hypot(txm, tym) || 1;
  const nxm = -tym / lm;
  const nym = txm / lm;

  let tx1 = x1 - xm;
  let ty1 = y1 - ym;
  let l1 = Math.hypot(tx1, ty1);
  if (l1 < 0.001) {
    tx1 = txm;
    ty1 = tym;
    l1 = lm;
  }
  const nx1 = -ty1 / l1;
  const ny1 = tx1 / l1;

  const wStart = hw * 0.18;
  const wMid = hw * 1.12;
  const wEnd = hw * 0.12;

  ctx.fillStyle = meta.lifted;
  ctx.globalAlpha = baseAlpha;
  ctx.beginPath();
  ctx.moveTo(x0 - (tx0 / l0) * hw * 0.28 + nx0 * wStart, y0 - (ty0 / l0) * hw * 0.28 + ny0 * wStart);
  ctx.quadraticCurveTo(xm + nxm * wMid, ym + nym * wMid, x1 + (tx1 / l1) * hw * 0.32 + nx1 * wEnd, y1 + (ty1 / l1) * hw * 0.32 + ny1 * wEnd);
  ctx.quadraticCurveTo(xm - nxm * wMid * 0.92, ym - nym * wMid * 0.92, x0 - (tx0 / l0) * hw * 0.28 - nx0 * wStart, y0 - (ty0 / l0) * hw * 0.28 - ny0 * wStart);
  ctx.closePath();
  ctx.fill();

  if (meta.luma > 0.30 && widthPx >= 1.05) {
    const evalX = (t) => (1 - t) * (1 - t) * x0 + 2 * (1 - t) * t * xm + t * t * x1;
    const evalY = (t) => (1 - t) * (1 - t) * y0 + 2 * (1 - t) * t * ym + t * t * y1;
    const off = hw * 0.22;
    const sx = evalX(0.18) + nx0 * off;
    const sy = evalY(0.18) + ny0 * off;
    const mx = evalX(0.50) + nxm * off * 1.35;
    const my = evalY(0.50) + nym * off * 1.35;
    const ex = evalX(0.82) + nx1 * off * 0.6;
    const ey = evalY(0.82) + ny1 * off * 0.6;
    const cx = 2 * mx - 0.5 * (sx + ex);
    const cy = 2 * my - 0.5 * (sy + ey);

    ctx.strokeStyle = meta.filament;
    ctx.lineWidth = Math.max(0.55, widthPx * 0.24);
    ctx.globalAlpha = baseAlpha * (meta.luma > 0.58 ? 0.68 : 0.46);
    ctx.beginPath();
    ctx.moveTo(sx, sy);
    ctx.quadraticCurveTo(cx, cy, ex, ey);
    ctx.stroke();
  }
}

function isVisible(canvas) {
  if (!canvas) return false;
  const r = canvas.getBoundingClientRect();
  if (r.width === 0 || r.height === 0) return false;
  return r.bottom >= -100 && r.top <= (window.innerHeight || 900) + 100;
}

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

export class LiquidStarrySky {
  constructor(bgCanvas, panoramaCanvas, gardenCanvas, vgScene, onBodyInspect) {
    this.bgCanvas = bgCanvas;
    this.bgCtx = bgCanvas.getContext("2d", { alpha: false });
    this.panCanvas = panoramaCanvas;
    this.panCtx = panoramaCanvas ? panoramaCanvas.getContext("2d", { alpha: false }) : null;
    this.garCanvas = gardenCanvas;
    this.garCtx = gardenCanvas ? gardenCanvas.getContext("2d", { alpha: false }) : null;
    this.vgScene = vgScene || {};
    this.onBodyInspect = onBodyInspect;
    this.mqReduced = window.matchMedia("(prefers-reduced-motion: reduce)");
    this.reducedMotion = this.mqReduced.matches;

    this.cols = 64;
    this.rows = 32;
    const cells = this.cols * this.rows;
    this.vx = new Float32Array(cells);
    this.vy = new Float32Array(cells);
    this.vx0 = new Float32Array(cells);
    this.vy0 = new Float32Array(cells);
    this.div = new Float32Array(cells);
    this.press = new Float32Array(cells);

    this.time = 12.0;
    this.gaze = { tx: 0.5, ty: 0.35, x: 0.5, y: 0.35 };
    this.panPtr = { nx: 0.5, ny: 0.5, inside: false };
    this.garPtr = { nx: 0.5, ny: 0.5, inside: false };
    this.wakeGlyphs = [];
    this.garWakeGlyphs = [];
    this.bgWakeGlyphs = [];
    this.bodyScreenPositions = [];
    this.hoveredBody = null;
    this._bgDirty = true;
    this._looping = false;

    this.panFlow = this._initFlowParticles(136, 0.72);
    this.garFlow = this._initFlowParticles(112, 0.54);

    this.dpr = Math.min(window.devicePixelRatio || 1, 1.5);
    this.bgW = 1440;
    this.bgH = 1900;
    this.panW = 1120;
    this.panH = 296;
    this.garW = 1120;
    this.garH = 312;

    this.panPlanes = null;
    this.garPlanes = null;
    this.bgBaked = null;

    this._resize();
    this._bindEvents();
    this.renderFrame(0.016);
    if (!this.reducedMotion) {
      this._startLoop();
    }
  }

  _initFlowParticles(count, maxNy) {
    const arr = [];
    let seed = 918273;
    const rand = () => {
      seed = (1664525 * seed + 1013904223) >>> 0;
      return (seed & 0xffff) / 65535;
    };
    const glyphs = ["~", "/", "\\", "(", ")", "*", "="];
    for (let i = 0; i < count; i++) {
      const nx = 0.04 + rand() * 0.92;
      const ny = 0.05 + rand() * (maxNy - 0.05);
      arr.push({
        nx,
        ny,
        px: nx,
        py: ny,
        color: FLOW_PALETTE[i % FLOW_PALETTE.length],
        glyph: glyphs[i % glyphs.length],
        life: rand(),
        speed: 0.65 + rand() * 0.75,
        width: 1.25 + rand() * 1.15
      });
    }
    return arr;
  }

  // WHY: Paints continuous lifted oil pigments + atmospheric horizon glow on plane 0 beneath tapered multi-plane impasto strokes so 2.5D parallax never tears dark gaps.
  _bakeCalligraphicPlanes(layerData, w, h, kind = "sky") {
    if (!layerData || !w || !h) return null;
    const dpr = this.dpr;
    const planes = [0, 1, 2, 3].map(() => {
      const c = document.createElement("canvas");
      c.width = Math.max(1, Math.round(w * dpr));
      c.height = Math.max(1, Math.round(h * dpr));
      const lc = c.getContext("2d");
      lc.setTransform(dpr, 0, 0, dpr, 0, 0);
      return { canvas: c, ctx: lc };
    });

    const p0 = planes[0].ctx;
    p0.fillStyle = "#07142c";
    p0.fillRect(0, 0, w, h);

    const cols = Math.max(1, layerData.cols || 204);
    const rows = Math.max(1, layerData.rows || 60);
    const rowStep = h / rows;
    const colStep = w / cols;

    const bgRows = layerData.bg || [];
    for (let r = 0; r < bgRows.length; r++) {
      let xCur = 0;
      const runs = bgRows[r];
      const ry = r * rowStep;
      const rh = rowStep + 0.9;
      for (let k = 0; k < runs.length; k++) {
        const [bCol, bLen] = runs[k];
        p0.fillStyle = getColorMeta(bCol).lifted;
        p0.fillRect(xCur * colStep, ry, bLen * colStep + 0.8, rh);
        xCur += bLen;
      }
    }

    const atmoGrad = p0.createLinearGradient(0, h * 0.08, 0, h * 0.96);
    if (kind === "garden") {
      atmoGrad.addColorStop(0, "rgba(56, 189, 248, 0.12)");
      atmoGrad.addColorStop(0.46, "rgba(125, 211, 252, 0.16)");
      atmoGrad.addColorStop(0.76, "rgba(251, 191, 36, 0.14)");
      atmoGrad.addColorStop(1, "rgba(180, 83, 9, 0.08)");
    } else {
      atmoGrad.addColorStop(0, "rgba(30, 64, 175, 0.10)");
      atmoGrad.addColorStop(0.52, "rgba(56, 189, 248, 0.15)");
      atmoGrad.addColorStop(0.84, "rgba(253, 224, 71, 0.12)");
      atmoGrad.addColorStop(1, "rgba(14, 116, 144, 0.10)");
    }
    p0.fillStyle = atmoGrad;
    p0.fillRect(0, 0, w, h);

    if (kind === "panorama") {
      const p1 = planes[1].ctx;
      for (let s = 0; s < PAN_STARS.length; s++) {
        const [sxN, syN, sr, warm] = PAN_STARS[s];
        const sx = sxN * w;
        const sy = syN * h;
        const haloR = sr * (s === PAN_STARS.length - 1 ? 2.45 : 1.95);
        const rg = p1.createRadialGradient(sx, sy, 1, sx, sy, haloR);
        if (warm) {
          rg.addColorStop(0, "rgba(254, 249, 195, 0.36)");
          rg.addColorStop(0.42, "rgba(253, 224, 71, 0.18)");
          rg.addColorStop(1, "rgba(251, 191, 36, 0)");
        } else {
          rg.addColorStop(0, "rgba(224, 242, 254, 0.32)");
          rg.addColorStop(0.45, "rgba(125, 211, 252, 0.16)");
          rg.addColorStop(1, "rgba(56, 189, 248, 0)");
        }
        p1.fillStyle = rg;
        p1.beginPath();
        p1.arc(sx, sy, haloR, 0, Math.PI * 2);
        p1.fill();
      }
    }

    const motifToPlane = (m) => {
      if (m >= 3) return 3;
      if (m === 2) return 2;
      if (m === 1) return 1;
      return 0;
    };

    const strokes = layerData.strokes || [];
    planes.forEach((p) => { p.ctx.lineCap = "round"; });
    const strokeScale = w / 640;
    for (let i = 0; i < strokes.length; i++) {
      const [x0, y0, xm, ym, x1, y1, scol, sw, motif] = strokes[i];
      const pl = motifToPlane(Number(motif || 0));
      const lc = planes[pl].ctx;
      drawTaperedImpastoStroke(
        lc,
        x0 * w,
        y0 * h,
        xm * w,
        ym * h,
        x1 * w,
        y1 * h,
        scol,
        sw * strokeScale,
        0.90
      );
    }

    const grid = layerData.grid || [];
    const motifs = layerData.motifs || [];
    const monoFamily = "'JetBrains Mono', ui-monospace, monospace";
    planes[0].ctx.font = `700 20px ${monoFamily}`;
    const unitAdv = (planes[0].ctx.measureText("MMMMMMMMMM").width / 200) || 0.6;
    const fontSz = Math.max(1.8, colStep / unitAdv);

    planes.forEach((p) => {
      p.ctx.globalAlpha = 0.95;
      p.ctx.font = `700 ${fontSz.toFixed(3)}px ${monoFamily}`;
      p.ctx.textBaseline = "alphabetic";
    });

    for (let r = 0; r < grid.length; r++) {
      const runs = grid[r];
      const mRow = motifs[r] || "";
      const py = (r + 0.82) * rowStep;
      let colCur = 0;
      for (let k = 0; k < runs.length; k++) {
        const [colHex, chunk] = runs[k];
        if (colHex) {
          const liftedHex = getColorMeta(colHex).lifted;
          let segStart = 0;
          let segPl = -1;
          let segText = "";
          for (let c = 0; c <= chunk.length; c++) {
            const ch = c < chunk.length ? chunk[c] : "";
            const pl = c < chunk.length ? motifToPlane(Number(mRow[colCur + c] || 0)) : -1;
            if (pl === segPl && pl >= 0) {
              segText += ch;
            } else {
              if (segPl >= 0 && segText) {
                const lc = planes[segPl].ctx;
                lc.fillStyle = liftedHex;
                lc.fillText(segText, (colCur + segStart) * colStep, py);
              }
              segPl = pl;
              segStart = c;
              segText = pl >= 0 ? ch : "";
            }
          }
        }
        colCur += chunk.length;
      }
    }
    planes.forEach((p) => { p.ctx.globalAlpha = 1; });
    return planes.map((p) => p.canvas);
  }

  // WHY: Composes one seamless full-page Starry Night sky flowing down to the grounded Sunflowers & Provence bottom garden without tile seams or duplicate margin moons.
  _bakeFullPageBackdrop() {
    const w = this.bgW;
    const h = this.bgH;
    const bgDpr = this.bgDpr || this.dpr;
    const c = document.createElement("canvas");
    c.width = Math.max(1, Math.round(w * bgDpr));
    c.height = Math.max(1, Math.round(h * bgDpr));
    const ctx = c.getContext("2d", { alpha: false });
    ctx.setTransform(bgDpr, 0, 0, bgDpr, 0, 0);

    ctx.fillStyle = "#050b1a";
    ctx.fillRect(0, 0, w, h);

    const gar = this.vgScene.garden;
    const skyOnly = this.vgScene.sky || this.vgScene.panorama;
    if (!skyOnly || !gar) {
      this.bgBaked = c;
      this._bgDirty = true;
      return;
    }

    const skyTileW = Math.min(w, 1280);
    const skyTileH = Math.max(340, Math.round(skyTileW * 0.36));
    const garTileW = Math.min(w, 1440);
    const garBandH = Math.max(340, Math.round(garTileW * 0.34));
    const skyPlanes = this._bakeCalligraphicPlanes(skyOnly, skyTileW, skyTileH, "sky");
    const garPlanes = this._bakeCalligraphicPlanes(gar, garTileW, garBandH, "garden");

    if (skyPlanes) {
      const skyTile = document.createElement("canvas");
      skyTile.width = Math.max(1, Math.round(skyTileW * bgDpr));
      skyTile.height = Math.max(1, Math.round(skyTileH * bgDpr));
      const stc = skyTile.getContext("2d", { alpha: false });
      stc.setTransform(bgDpr, 0, 0, bgDpr, 0, 0);
      for (let p = 0; p < skyPlanes.length; p++) {
        stc.drawImage(skyPlanes[p], 0, 0, skyTileW, skyTileH);
      }

      const overlap = Math.round(skyTileH * 0.32);
      const step = Math.max(120, skyTileH - overlap);
      const skyFeather = document.createElement("canvas");
      skyFeather.width = skyTile.width;
      skyFeather.height = skyTile.height;
      const sfc = skyFeather.getContext("2d");
      sfc.setTransform(bgDpr, 0, 0, bgDpr, 0, 0);
      sfc.drawImage(skyTile, 0, 0, skyTileW, skyTileH);
      sfc.globalCompositeOperation = "destination-in";
      const fMask = sfc.createLinearGradient(0, 0, 0, overlap);
      fMask.addColorStop(0, "rgba(0,0,0,0)");
      fMask.addColorStop(1, "rgba(0,0,0,1)");
      sfc.fillStyle = fMask;
      sfc.fillRect(0, 0, skyTileW, skyTileH);

      for (let x = 0; x < w; x += skyTileW) {
        ctx.drawImage(skyTile, x, 0, skyTileW, skyTileH);
      }
      let tileIdx = 1;
      for (let y = step; y < h; y += step) {
        const shiftX = Math.round(((tileIdx * 0.381966) % 1) * skyTileW);
        for (let x = -shiftX; x < w; x += skyTileW) {
          ctx.drawImage(skyFeather, x, y, skyTileW, skyTileH);
        }
        tileIdx++;
      }

      const zenithGrad = ctx.createLinearGradient(0, 0, 0, 36);
      zenithGrad.addColorStop(0, "rgba(4, 9, 22, 0.58)");
      zenithGrad.addColorStop(1, "rgba(4, 9, 22, 0)");
      ctx.fillStyle = zenithGrad;
      ctx.fillRect(0, 0, w, 36);
    }

    if (garPlanes) {
      const gy = Math.max(0, h - garBandH);
      const garComp = document.createElement("canvas");
      garComp.width = Math.max(1, Math.round(garTileW * bgDpr));
      garComp.height = Math.max(1, Math.round(garBandH * bgDpr));
      const gc = garComp.getContext("2d");
      gc.setTransform(bgDpr, 0, 0, bgDpr, 0, 0);
      for (let p = 0; p < garPlanes.length; p++) {
        gc.drawImage(garPlanes[p], 0, 0, garTileW, garBandH);
      }
      gc.globalCompositeOperation = "destination-in";
      const gMask = gc.createLinearGradient(0, 0, 0, garBandH);
      gMask.addColorStop(0, "rgba(0,0,0,0)");
      gMask.addColorStop(0.28, "rgba(0,0,0,0.92)");
      gMask.addColorStop(1, "rgba(0,0,0,1)");
      gc.fillStyle = gMask;
      gc.fillRect(0, 0, garTileW, garBandH);
      if (w <= garTileW) {
        ctx.drawImage(garComp, 0, gy, garTileW, garBandH);
      } else {
        const rem = w % garTileW;
        const startX = rem > 0 ? -Math.round((garTileW - rem) * 0.5) : 0;
        let gIdx = 0;
        for (let x = startX; x < w; x += garTileW) {
          if (gIdx % 2 === 1) {
            ctx.save();
            ctx.translate(x + garTileW, gy);
            ctx.scale(-1, 1);
            ctx.drawImage(garComp, 0, 0, garTileW, garBandH);
            ctx.restore();
          } else {
            ctx.drawImage(garComp, x, gy, garTileW, garBandH);
          }
          gIdx++;
        }
      }
    }

    this.bgBaked = c;
    this._bgDirty = true;
  }

  _resize() {
    this.dpr = Math.min(window.devicePixelRatio || 1, 1.5);
    const docEl = document.documentElement;
    this.bgW = Math.max(320, docEl.clientWidth || window.innerWidth || 1440);
    this.bgH = Math.max(window.innerHeight || 900, docEl.scrollHeight || 1400, document.body.offsetHeight || 1400);
    this.bgDpr = (this.bgW * this.bgH > 2200000) ? 1 : this.dpr;
    this.bgCanvas.width = Math.round(this.bgW * this.bgDpr);
    this.bgCanvas.height = Math.round(this.bgH * this.bgDpr);
    this.bgCtx.setTransform(this.bgDpr, 0, 0, this.bgDpr, 0, 0);

    if (this.panCanvas && this.panCtx) {
      const rect = this.panCanvas.getBoundingClientRect();
      this.panW = Math.max(280, Math.round(rect.width || 1120));
      this.panH = Math.max(188, Math.round(rect.height || 296));
      this.panCanvas.width = Math.round(this.panW * this.dpr);
      this.panCanvas.height = Math.round(this.panH * this.dpr);
      this.panCtx.setTransform(this.dpr, 0, 0, this.dpr, 0, 0);
      this.panPlanes = this._bakeCalligraphicPlanes(this.vgScene.panorama, this.panW, this.panH, "panorama");
    }

    if (this.garCanvas && this.garCtx) {
      const rect = this.garCanvas.getBoundingClientRect();
      this.garW = Math.max(280, Math.round(rect.width || 1120));
      this.garH = Math.max(196, Math.round(rect.height || 312));
      this.garCanvas.width = Math.round(this.garW * this.dpr);
      this.garCanvas.height = Math.round(this.garH * this.dpr);
      this.garCtx.setTransform(this.dpr, 0, 0, this.dpr, 0, 0);
      this.garPlanes = this._bakeCalligraphicPlanes(this.vgScene.garden, this.garW, this.garH, "garden");
    }

    this._bakeFullPageBackdrop();
  }

  _spawnWake(pool, x, y, vx, vy, count = 3) {
    const speed = Math.hypot(vx, vy);
    if (speed < 0.4) return;
    const baseAng = Math.atan2(vy, vx);
    for (let i = 0; i < count; i++) {
      if (pool.length > 120) pool.shift();
      const spread = (Math.random() - 0.5) * 18;
      const perp = baseAng + Math.PI * 0.5;
      pool.push({
        x: x + Math.cos(perp) * spread,
        y: y + Math.sin(perp) * spread,
        vx: vx * (0.24 + Math.random() * 0.22) + (Math.random() - 0.5) * 0.8,
        vy: vy * (0.24 + Math.random() * 0.22) + (Math.random() - 0.5) * 0.8,
        ang: baseAng,
        glyph: WAKE_GLYPHS[(Math.random() * WAKE_GLYPHS.length) | 0],
        color: WAKE_COLORS[(Math.random() * WAKE_COLORS.length) | 0],
        life: 1.0,
        size: 10 + Math.random() * 4.2
      });
    }
  }

  _bindEvents() {
    let resizeTimer = 0;
    const scheduleResize = () => {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(() => {
        this._resize();
        this.renderFrame(0);
      }, 90);
    };
    window.addEventListener("resize", scheduleResize);

    this.mqReduced.addEventListener("change", (e) => {
      this.reducedMotion = e.matches;
      if (!this.reducedMotion) this._startLoop();
      else this.renderFrame(0);
    });

    if (typeof ResizeObserver === "function") {
      const ro = new ResizeObserver(() => {
        const targetH = Math.max(window.innerHeight || 900, document.documentElement.scrollHeight || 1400);
        if (Math.abs(targetH - this.bgH) > 16) {
          scheduleResize();
        }
      });
      ro.observe(document.body);
    }

    window.addEventListener("pointermove", (ev) => {
      this.gaze.tx = ev.clientX / Math.max(1, window.innerWidth || 1440);
      this.gaze.ty = ev.clientY / Math.max(1, window.innerHeight || 900);
      const pageX = ev.pageX ?? ev.clientX;
      const pageY = ev.pageY ?? (ev.clientY + window.scrollY);
      this.injectImpulse(this.gaze.tx, this.gaze.ty, (ev.movementX || 0) * 0.30, (ev.movementY || 0) * 0.30);
      if (Math.hypot(ev.movementX || 0, ev.movementY || 0) > 1.2) {
        this._spawnWake(this.bgWakeGlyphs, pageX, pageY, ev.movementX || 0, ev.movementY || 0, 2);
        this._bgDirty = true;
      }
      if (this.reducedMotion) {
        this.gaze.x = this.gaze.tx;
        this.gaze.y = this.gaze.ty;
        this.renderFrame(0);
      }
    }, { passive: true });

    if (this.panCanvas) {
      let lastX = -999;
      let lastY = -999;
      this.panCanvas.addEventListener("pointermove", (ev) => {
        const rect = this.panCanvas.getBoundingClientRect();
        const x = ev.clientX - rect.left;
        const y = ev.clientY - rect.top;
        this.panPtr = { nx: x / Math.max(1, this.panW), ny: y / Math.max(1, this.panH), inside: true };
        if (lastX > -900) {
          const dx = x - lastX;
          const dy = y - lastY;
          this.injectImpulse(this.panPtr.nx, this.panPtr.ny, dx * 0.55, dy * 0.55);
          this._spawnWake(this.wakeGlyphs, x, y, dx, dy, 4);
        }
        lastX = x;
        lastY = y;
        this._checkBodyHover(x, y);
      }, { passive: true });

      this.panCanvas.addEventListener("pointerleave", () => {
        lastX = -999;
        this.panPtr.inside = false;
        this.hoveredBody = null;
        if (this.onBodyInspect) this.onBodyInspect("");
      });

      this.panCanvas.addEventListener("pointerdown", (ev) => {
        const rect = this.panCanvas.getBoundingClientRect();
        const x = ev.clientX - rect.left;
        const y = ev.clientY - rect.top;
        this.injectImpulse(x / Math.max(1, this.panW), y / Math.max(1, this.panH), 12, -8);
        this.triggerSwirlBurst(this.wakeGlyphs, x, y);
        this._checkBodyHover(x, y, true);
      }, { passive: true });
    }

    if (this.garCanvas) {
      let gxLast = -999;
      let gyLast = -999;
      this.garCanvas.addEventListener("pointermove", (ev) => {
        const rect = this.garCanvas.getBoundingClientRect();
        const x = ev.clientX - rect.left;
        const y = ev.clientY - rect.top;
        this.garPtr = { nx: x / Math.max(1, this.garW), ny: y / Math.max(1, this.garH), inside: true };
        if (gxLast > -900) {
          const dx = x - gxLast;
          const dy = y - gyLast;
          this.injectImpulse(this.garPtr.nx, this.garPtr.ny, dx * 0.50, dy * 0.50);
          this._spawnWake(this.garWakeGlyphs, x, y, dx, dy, 4);
        }
        gxLast = x;
        gyLast = y;
      }, { passive: true });

      this.garCanvas.addEventListener("pointerleave", () => {
        gxLast = -999;
        this.garPtr.inside = false;
      });

      this.garCanvas.addEventListener("pointerdown", (ev) => {
        const rect = this.garCanvas.getBoundingClientRect();
        const x = ev.clientX - rect.left;
        const y = ev.clientY - rect.top;
        this.injectImpulse(x / Math.max(1, this.garW), y / Math.max(1, this.garH), 10, -8);
        this.triggerSwirlBurst(this.garWakeGlyphs, x, y);
      }, { passive: true });
    }
  }

  triggerSwirlBurst(pool, cx, cy) {
    for (let i = 0; i < 18; i++) {
      const a = (i * Math.PI * 2) / 18;
      const spd = 2.6 + (i % 3) * 0.9;
      pool.push({
        x: cx + Math.cos(a) * 6,
        y: cy + Math.sin(a) * 6,
        vx: Math.cos(a + 0.9) * spd,
        vy: Math.sin(a + 0.9) * spd,
        ang: a + 1.57,
        glyph: WAKE_GLYPHS[i % WAKE_GLYPHS.length],
        color: WAKE_COLORS[i % WAKE_COLORS.length],
        life: 1.0,
        size: 11.5 + (i % 3) * 1.8
      });
    }
    if (this.reducedMotion) this.renderFrame(0.016);
  }

  injectImpulse(nx, ny, fx, fy) {
    const gxCenter = Math.max(1, Math.min(this.cols - 2, nx * this.cols));
    const gyCenter = Math.max(1, Math.min(this.rows - 2, ny * this.rows));
    for (let gy = 1; gy < this.rows - 1; gy++) {
      const dy = gy - gyCenter;
      if (Math.abs(dy) > 4.5) continue;
      for (let gx = 1; gx < this.cols - 1; gx++) {
        const dx = gx - gxCenter;
        const d2 = dx * dx + dy * dy;
        if (d2 < 20) {
          const w = Math.exp(-d2 / 5.5);
          const idx = gy * this.cols + gx;
          this.vx[idx] = Math.max(-24, Math.min(24, this.vx[idx] + fx * w));
          this.vy[idx] = Math.max(-24, Math.min(24, this.vy[idx] + fy * w));
        }
      }
    }
  }

  _sampleFluidVelocity(nx, ny) {
    const W = this.cols;
    const H = this.rows;
    const cx = Math.max(0.5, Math.min(W - 1.5, nx * W));
    const cy = Math.max(0.5, Math.min(H - 1.5, ny * H));
    const x0 = Math.floor(cx);
    const y0 = Math.floor(cy);
    const tx = cx - x0;
    const ty = cy - y0;
    const i00 = y0 * W + x0;
    const fx =
      this.vx[i00] * (1 - tx) * (1 - ty) +
      this.vx[i00 + 1] * tx * (1 - ty) +
      this.vx[i00 + W] * (1 - tx) * ty +
      this.vx[i00 + W + 1] * tx * ty;
    const fy =
      this.vy[i00] * (1 - tx) * (1 - ty) +
      this.vy[i00 + 1] * tx * (1 - ty) +
      this.vy[i00 + W] * (1 - tx) * ty +
      this.vy[i00 + W + 1] * tx * ty;
    return [fx, fy];
  }

  // WHY: Analytical Starry Night double-vortex + Crescent Moon corona tangent field coupled with solved Navier-Stokes cursor velocity.
  _starryVortexVelocity(nx, ny) {
    let ux = 0.022 + 0.012 * Math.cos(ny * 8.5 + this.time * 0.25);
    let uy = -0.008 * Math.sin(nx * 9.2 - this.time * 0.20);
    const vortices = [
      [0.39, 0.42, 0.055, 0.028],
      [0.57, 0.56, -0.044, 0.018],
      [0.895, 0.255, 0.048, 0.016]
    ];
    for (let i = 0; i < vortices.length; i++) {
      const [vx, vy, strength, sigma2] = vortices[i];
      const dx = nx - vx;
      const dy = (ny - vy) * 0.55;
      const r2 = dx * dx + dy * dy;
      const falloff = Math.exp(-r2 / sigma2);
      ux += (-dy / Math.max(0.04, Math.sqrt(r2))) * strength * falloff;
      uy += (dx / Math.max(0.04, Math.sqrt(r2))) * strength * falloff * 1.45;
    }
    const [fx, fy] = this._sampleFluidVelocity(nx, ny);
    return [ux + fx * 0.022, uy + fy * 0.048];
  }

  _drawFluidImpastoFlow(ctx, particles, w, h, maxNy, dt) {
    ctx.save();
    ctx.lineCap = "round";
    ctx.font = "700 8.5px 'JetBrains Mono', ui-monospace, monospace";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";

    for (let i = 0; i < particles.length; i++) {
      const p = particles[i];
      const [vx, vy] = this._starryVortexVelocity(p.nx, p.ny);
      if (dt > 0) {
        p.px = p.nx;
        p.py = p.ny;
        p.nx += vx * dt * p.speed;
        p.ny += vy * dt * p.speed;
        p.life += dt * 0.26;
        if (p.life >= 1 || p.nx < 0.02 || p.nx > 0.98 || p.ny < 0.03 || p.ny > maxNy) {
          p.nx = 0.04 + ((i * 0.618034 + this.time * 0.03) % 0.92);
          p.ny = 0.05 + ((i * 0.381966 + this.time * 0.02) % (maxNy - 0.06));
          p.px = p.nx;
          p.py = p.ny;
          p.life = 0.04;
        }
      }
      const env = Math.sin(Math.min(1, p.life) * Math.PI);
      const x = p.nx * w;
      const y = p.ny * h;
      const ang = Math.atan2(vy * h, vx * w);
      const len = 8.2 + Math.min(11, Math.hypot(vx * w, vy * h) * 0.13);
      const tx = Math.cos(ang) * len;
      const ty = Math.sin(ang) * len;

      drawTaperedImpastoStroke(
        ctx,
        x - tx,
        y - ty,
        x - ty * 0.24,
        y + tx * 0.24,
        x + tx,
        y + ty,
        p.color,
        p.width * 1.15,
        env * 0.64
      );

      if (i % 2 === 0) {
        ctx.globalAlpha = env * 0.76;
        ctx.fillStyle = getColorMeta(p.color).filament;
        ctx.fillText(p.glyph, x, y);
      }
    }
    ctx.restore();
  }

  _stepFluidSolver(dt) {
    const W = this.cols;
    const H = this.rows;
    this.vx0.set(this.vx);
    this.vy0.set(this.vy);

    const sampleBilinear = (arr, x, y) => {
      const cx = Math.max(0.5, Math.min(W - 1.5, x));
      const cy = Math.max(0.5, Math.min(H - 1.5, y));
      const x0 = Math.floor(cx);
      const y0 = Math.floor(cy);
      const tx = cx - x0;
      const ty = cy - y0;
      const i00 = y0 * W + x0;
      return (
        arr[i00] * (1 - tx) * (1 - ty) +
        arr[i00 + 1] * tx * (1 - ty) +
        arr[i00 + W] * (1 - tx) * ty +
        arr[i00 + W + 1] * tx * ty
      );
    };

    const adv = dt * 13.5;
    for (let y = 1; y < H - 1; y++) {
      for (let x = 1; x < W - 1; x++) {
        const idx = y * W + x;
        const bx = x - this.vx0[idx] * adv;
        const by = y - this.vy0[idx] * adv;
        this.vx[idx] = sampleBilinear(this.vx0, bx, by) * 0.962;
        this.vy[idx] = sampleBilinear(this.vy0, bx, by) * 0.962;
      }
    }

    for (let y = 1; y < H - 1; y++) {
      for (let x = 1; x < W - 1; x++) {
        const idx = y * W + x;
        this.div[idx] = -0.5 * (this.vx[idx + 1] - this.vx[idx - 1] + this.vy[idx + W] - this.vy[idx - W]);
        this.press[idx] = 0;
      }
    }

    for (let iter = 0; iter < 5; iter++) {
      for (let y = 1; y < H - 1; y++) {
        for (let x = 1; x < W - 1; x++) {
          const idx = y * W + x;
          this.press[idx] = (this.div[idx] + this.press[idx - 1] + this.press[idx + 1] + this.press[idx - W] + this.press[idx + W]) * 0.25;
        }
      }
    }

    for (let y = 1; y < H - 1; y++) {
      for (let x = 1; x < W - 1; x++) {
        const idx = y * W + x;
        this.vx[idx] -= 0.5 * (this.press[idx + 1] - this.press[idx - 1]);
        this.vy[idx] -= 0.5 * (this.press[idx + W] - this.press[idx - W]);
      }
    }
  }

  _checkBodyHover(x, y, force = false) {
    let hit = null;
    let best = 22;
    for (let i = 0; i < this.bodyScreenPositions.length; i++) {
      const b = this.bodyScreenPositions[i];
      const d = Math.hypot(x - b.x, y - b.y);
      if (d < Math.max(16, b.r + 8) && d < best) {
        best = d;
        hit = b;
      }
    }
    if (hit && (hit !== this.hoveredBody || force)) {
      this.hoveredBody = hit;
      if (this.onBodyInspect) this.onBodyInspect(hit.label);
    } else if (!hit && this.hoveredBody) {
      this.hoveredBody = null;
      if (this.onBodyInspect) this.onBodyInspect("");
    }
  }

  focusBody(key) {
    const found = this.bodyScreenPositions.find((b) => b.key === key);
    if (found) {
      this.hoveredBody = found;
      this.triggerSwirlBurst(this.wakeGlyphs, found.x, found.y);
      if (this.onBodyInspect) this.onBodyInspect(found.label);
    }
  }

  _drawWakePool(ctx, pool, w, h, dt) {
    ctx.save();
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    for (let i = pool.length - 1; i >= 0; i--) {
      const p = pool[i];
      if (dt > 0) {
        const [fx, fy] = this._sampleFluidVelocity(p.x / Math.max(1, w), p.y / Math.max(1, h));
        p.vx = p.vx * 0.93 + fx * 0.14;
        p.vy = p.vy * 0.93 + fy * 0.14;
        p.x += p.vx;
        p.y += p.vy;
        p.ang = Math.atan2(p.vy, p.vx);
        p.life -= 0.024;
      }
      if (p.life <= 0.02) {
        pool.splice(i, 1);
        continue;
      }
      ctx.save();
      ctx.translate(p.x, p.y);
      ctx.rotate(p.ang);
      drawTaperedImpastoStroke(ctx, -8, 0, 0, -3.4, 8, 0, p.color, 1.8, p.life * 0.92);
      ctx.globalAlpha = p.life * 0.92;
      ctx.font = `700 ${p.size.toFixed(1)}px 'JetBrains Mono', ui-monospace, monospace`;
      ctx.fillStyle = getColorMeta(p.color).filament;
      ctx.fillText(p.glyph, 0, 0);
      ctx.restore();
    }
    ctx.restore();
  }

  _drawHeliotropicSunflowers(ctx, w, h, flowers, targetX, targetY) {
    ctx.save();
    ctx.font = "700 8.5px 'JetBrains Mono', ui-monospace, monospace";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    for (let i = 0; i < flowers.length; i++) {
      const [fx, fy, rad] = flowers[i];
      const cx = fx * w;
      const cy = fy * h;
      const dx = targetX - cx;
      const dy = targetY - cy;
      const gazeAng = Math.atan2(dy, dx);
      const leanX = Math.cos(gazeAng) * Math.min(4.5, Math.hypot(dx, dy) * 0.012);
      const leanY = Math.sin(gazeAng) * Math.min(3.5, Math.hypot(dx, dy) * 0.010);

      ctx.save();
      ctx.translate(cx + leanX, cy + leanY);

      const bloomGlow = ctx.createRadialGradient(0, 0, rad * 0.12, 0, 0, rad * 1.15);
      bloomGlow.addColorStop(0, "rgba(253, 224, 71, 0.24)");
      bloomGlow.addColorStop(0.65, "rgba(245, 158, 11, 0.10)");
      bloomGlow.addColorStop(1, "rgba(245, 158, 11, 0)");
      ctx.fillStyle = bloomGlow;
      ctx.beginPath();
      ctx.arc(0, 0, rad * 1.15, 0, Math.PI * 2);
      ctx.fill();

      ctx.rotate(gazeAng * 0.16 + Math.sin(this.time * 1.1 + i) * 0.04);
      const petals = 12;
      for (let p = 0; p < petals; p++) {
        const a = (p * Math.PI * 2) / petals;
        const r0 = rad * 0.30;
        const rm = rad * 0.62;
        const r1 = rad * 0.86;
        const px = Math.cos(a) * r1;
        const py = Math.sin(a) * r1;
        drawTaperedImpastoStroke(
          ctx,
          Math.cos(a) * r0,
          Math.sin(a) * r0,
          Math.cos(a + 0.15) * rm,
          Math.sin(a + 0.15) * rm,
          px,
          py,
          p % 2 === 0 ? "#fde047" : "#f59e0b",
          2.2,
          0.88
        );
        ctx.globalAlpha = 0.88;
        ctx.fillStyle = p % 2 === 0 ? "#fef9c3" : "#fcd34d";
        ctx.fillText(p % 2 === 0 ? "*" : "~", px, py);
      }

      ctx.globalAlpha = 0.94;
      ctx.fillStyle = "#78350f";
      ctx.beginPath();
      ctx.arc(0, 0, rad * 0.27, 0, Math.PI * 2);
      ctx.fill();
      ctx.strokeStyle = "#fbbf24";
      ctx.lineWidth = 1.15;
      ctx.stroke();
      ctx.fillStyle = "#fde047";
      ctx.fillText("@", 0, 0);
      ctx.restore();
    }
    ctx.restore();
  }

  _drawGazeCoronas(ctx, w, h, targetX, targetY) {
    ctx.save();
    ctx.font = "700 8px 'JetBrains Mono', ui-monospace, monospace";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    for (let i = 0; i < PAN_STARS.length; i++) {
      const [nx, ny, r, warm] = PAN_STARS[i];
      const sx = nx * w + (this.gaze.x - 0.5) * 6;
      const sy = ny * h + (this.gaze.y - 0.35) * 4;
      const lookAng = Math.atan2(targetY - sy, targetX - sx);
      const spin = this.time * (i % 2 === 0 ? 0.28 : -0.22) + lookAng * 0.28;
      const pulse = 0.86 + 0.14 * Math.sin(this.time * 2.1 + i * 1.4);

      const glowR = r * 1.55 * pulse;
      const grad = ctx.createRadialGradient(sx, sy, 1, sx, sy, glowR);
      if (warm) {
        grad.addColorStop(0, "rgba(254, 249, 195, 0.34)");
        grad.addColorStop(0.55, "rgba(253, 224, 71, 0.14)");
        grad.addColorStop(1, "rgba(253, 224, 71, 0)");
      } else {
        grad.addColorStop(0, "rgba(224, 242, 254, 0.30)");
        grad.addColorStop(0.55, "rgba(125, 211, 252, 0.13)");
        grad.addColorStop(1, "rgba(125, 211, 252, 0)");
      }
      ctx.globalAlpha = 1;
      ctx.fillStyle = grad;
      ctx.beginPath();
      ctx.arc(sx, sy, glowR, 0, Math.PI * 2);
      ctx.fill();

      const arcs = 6;
      for (let k = 0; k < arcs; k++) {
        const a0 = spin + (k * Math.PI * 2) / arcs;
        const am = a0 + 0.26;
        const a1 = a0 + 0.52;
        const cr = r * 0.88;
        drawTaperedImpastoStroke(
          ctx,
          sx + Math.cos(a0) * cr,
          sy + Math.sin(a0) * cr,
          sx + Math.cos(am) * (cr * 1.06),
          sy + Math.sin(am) * (cr * 1.06),
          sx + Math.cos(a1) * cr,
          sy + Math.sin(a1) * cr,
          warm ? "#fde047" : "#7dd3fc",
          1.55,
          0.72
        );
      }

      const glyphs = 8;
      ctx.globalAlpha = 0.90;
      for (let g = 0; g < glyphs; g++) {
        const a = spin + (g * Math.PI * 2) / glyphs;
        const gx = sx + Math.cos(a) * r;
        const gy = sy + Math.sin(a) * r;
        ctx.fillStyle = warm ? "#fef08a" : "#bae6fd";
        ctx.fillText(g % 2 === 0 ? "~" : "*", gx, gy);
      }
    }
    ctx.restore();
  }

  _drawCompositePlanes(ctx, planes, w, h, gxShift, gyShift) {
    if (!planes) {
      ctx.fillStyle = "#07142c";
      ctx.fillRect(0, 0, w, h);
      return;
    }
    const mults = [-4.5, 2.5, 6.8, 12.0];
    ctx.fillStyle = "#07142c";
    ctx.fillRect(0, 0, w, h);
    for (let p = 0; p < planes.length; p++) {
      const ox = gxShift * mults[p];
      const oy = gyShift * mults[p] * 0.65;
      const pad = Math.abs(mults[p]) + 2;
      ctx.drawImage(planes[p], -pad + ox, -pad + oy, w + pad * 2, h + pad * 2);
    }
  }

  _drawSolarOrrery(ctx, w, h, gxShift, gyShift) {
    const sunX = w * 0.48 + gxShift * 5.0;
    const sunY = h * 0.50 + gyShift * 3.5;
    const maxRx = Math.min(280, w * 0.29);
    const maxRy = Math.min(62, h * 0.24);
    const tilt = -0.14 + gxShift * 0.04;

    ctx.save();
    const sunHalo = ctx.createRadialGradient(sunX, sunY, 2, sunX, sunY, 28);
    sunHalo.addColorStop(0, "rgba(254, 249, 195, 0.56)");
    sunHalo.addColorStop(0.45, "rgba(251, 191, 36, 0.22)");
    sunHalo.addColorStop(1, "rgba(251, 191, 36, 0)");
    ctx.fillStyle = sunHalo;
    ctx.beginPath();
    ctx.arc(sunX, sunY, 28, 0, Math.PI * 2);
    ctx.fill();

    ctx.strokeStyle = "rgba(254, 240, 138, 0.88)";
    ctx.lineWidth = 1.2;
    drawStarPolygon(ctx, sunX, sunY, 11.2, 4.1, 8, this.time * 0.35);
    ctx.fillStyle = "#fbbf24";
    ctx.fill();
    ctx.stroke();
    drawStarPolygon(ctx, sunX, sunY, 5.2, 2.0, 4, -this.time * 0.5);
    ctx.fillStyle = "#ffffff";
    ctx.fill();
    ctx.restore();

    this.bodyScreenPositions.push({
      key: "sun",
      x: sunX,
      y: sunY,
      r: 12,
      label: "Sun · 5,778 K"
    });

    const cometAng = this.time * 0.26 + 1.1;
    const cRx = maxRx * 0.84;
    const cRy = maxRy * 0.42;
    const cTilt = 0.25;
    const clx = Math.cos(cometAng) * cRx;
    const cly = Math.sin(cometAng) * cRy;
    const comX = sunX + maxRx * 0.14 + clx * Math.cos(cTilt) - cly * Math.sin(cTilt);
    const comY = sunY - 4 + clx * Math.sin(cTilt) + cly * Math.cos(cTilt);
    const away = Math.atan2(comY - sunY, comX - sunX);

    ctx.save();
    drawTaperedImpastoStroke(
      ctx,
      comX,
      comY,
      comX + Math.cos(away + 0.08) * 12,
      comY + Math.sin(away + 0.08) * 12,
      comX + Math.cos(away) * 25,
      comY + Math.sin(away) * 25,
      "#7dd3fc",
      2.2,
      0.86
    );
    ctx.globalAlpha = 1;
    drawStarPolygon(ctx, comX, comY, 4.3, 1.5, 4, away);
    ctx.fillStyle = "#ffffff";
    ctx.fill();
    ctx.restore();

    this.bodyScreenPositions.push({
      key: "comet",
      x: comX,
      y: comY,
      r: 8,
      label: "Halley's Comet · 76y"
    });

    const cosT = Math.cos(tilt);
    const sinT = Math.sin(tilt);
    for (let i = 0; i < PLANETS.length; i++) {
      const pl = PLANETS[i];
      const rx = maxRx * pl.rf;
      const ry = maxRy * pl.rf;
      const isHov = this.hoveredBody && this.hoveredBody.key === pl.key;

      ctx.save();
      ctx.translate(sunX, sunY);
      ctx.rotate(tilt);
      ctx.strokeStyle = isHov ? "rgba(253, 224, 71, 0.88)" : "rgba(147, 197, 253, 0.32)";
      ctx.lineWidth = isHov ? 1.4 : 0.85;
      ctx.beginPath();
      ctx.ellipse(0, 0, rx, ry, 0, 0, Math.PI * 2);
      ctx.stroke();
      ctx.restore();

      const ang = pl.phase + this.time * 0.32 * pl.speed;
      const lx = Math.cos(ang) * rx;
      const ly = Math.sin(ang) * ry;
      const px = sunX + lx * cosT - ly * sinT;
      const py = sunY + lx * sinT + ly * cosT;

      if (pl.ring || pl.tiltRing) {
        ctx.save();
        ctx.translate(px, py);
        ctx.rotate(pl.tiltRing ? 1.18 : -0.32);
        ctx.strokeStyle = pl.tiltRing ? "#67e8f9" : "#fde68a";
        ctx.lineWidth = 1.45;
        ctx.beginPath();
        ctx.ellipse(0, 0, pl.r * 2.25, pl.r * 0.84, 0, 0, Math.PI * 2);
        ctx.stroke();
        ctx.restore();
      }

      drawStarPolygon(ctx, px, py, pl.r * 1.40, pl.r * 0.68, 6, this.time * 0.4 + i);
      ctx.fillStyle = pl.color;
      ctx.fill();
      ctx.fillStyle = "#ffffff";
      ctx.beginPath();
      ctx.arc(px - pl.r * 0.18, py - pl.r * 0.18, Math.max(0.9, pl.r * 0.24), 0, Math.PI * 2);
      ctx.fill();

      this.bodyScreenPositions.push({
        key: pl.key,
        x: px,
        y: py,
        r: pl.r + 2,
        label: `${pl.name} · ${pl.period}`
      });
    }

    this.bodyScreenPositions.push({
      key: "moon",
      x: w * 0.895,
      y: h * 0.255,
      r: 30,
      label: "Crescent Moon"
    });
  }

  _startLoop() {
    if (this._looping) return;
    this._looping = true;
    let last = performance.now();
    const tick = (now) => {
      if (this.reducedMotion) {
        this._looping = false;
        return;
      }
      const dt = Math.min(0.045, (now - last) / 1000);
      last = now;
      this.renderFrame(dt);
      requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }

  renderFrame(dt) {
    this.time += dt;
    this.gaze.x += (this.gaze.tx - this.gaze.x) * 0.09;
    this.gaze.y += (this.gaze.ty - this.gaze.y) * 0.09;
    if (dt > 0) {
      this._stepFluidSolver(dt);
    }

    const gxShift = this.gaze.x - 0.5;
    const gyShift = this.gaze.y - 0.4;

    if (this.bgBaked && (this._bgDirty || this.bgWakeGlyphs.length > 0)) {
      this.bgCtx.drawImage(this.bgBaked, 0, 0, this.bgW, this.bgH);
      if (this.bgWakeGlyphs.length > 0) {
        this._drawWakePool(this.bgCtx, this.bgWakeGlyphs, this.bgW, this.bgH, dt);
      }
      this._bgDirty = this.bgWakeGlyphs.length > 0;
    }

    if (this.panCtx && (dt === 0 || isVisible(this.panCanvas))) {
      const w = this.panW;
      const h = this.panH;
      this.bodyScreenPositions = [];
      this._drawCompositePlanes(this.panCtx, this.panPlanes, w, h, gxShift, gyShift);
      this._drawFluidImpastoFlow(this.panCtx, this.panFlow, w, h, 0.74, dt);
      const tx = this.panPtr.inside ? this.panPtr.nx * w : this.gaze.x * w;
      const ty = this.panPtr.inside ? this.panPtr.ny * h : this.gaze.y * h;
      this._drawGazeCoronas(this.panCtx, w, h, tx, ty);
      this._drawSolarOrrery(this.panCtx, w, h, gxShift, gyShift);
      this._drawHeliotropicSunflowers(this.panCtx, w, h, PAN_SUNFLOWERS, tx, ty);
      this._drawWakePool(this.panCtx, this.wakeGlyphs, w, h, dt);
    }

    if (this.garCtx && (dt === 0 || isVisible(this.garCanvas))) {
      const w = this.garW;
      const h = this.garH;
      this._drawCompositePlanes(this.garCtx, this.garPlanes, w, h, gxShift * 1.12, gyShift * 1.12);
      this._drawFluidImpastoFlow(this.garCtx, this.garFlow, w, h, 0.52, dt);
      const tx = this.garPtr.inside ? this.garPtr.nx * w : this.gaze.x * w;
      const ty = this.garPtr.inside ? this.garPtr.ny * h : this.gaze.y * h;
      this._drawHeliotropicSunflowers(this.garCtx, w, h, GAR_SUNFLOWERS, tx, ty);
      this._drawWakePool(this.garCtx, this.garWakeGlyphs, w, h, dt);
    }
  }
}
