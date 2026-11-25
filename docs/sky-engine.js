// SPDX-License-Identifier: MIT
// WHY: Synthesizes 60 FPS Van Gogh Starry Night, Arles Sunlit Day, 60s Day-Night lighting cycle, 4 Giant Shooting Stars per 10s, Navier-Stokes cursor flow, and 4-plane parallax.

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
const FLOW_PALETTE_DAY = ["#ffffff", "#fef9c3", "#fde047", "#bae6fd", "#38bdf8", "#fef08a"];

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

export const DAY_NIGHT_CYCLE_SEC = 60.0;
export const METEOR_CYCLE_SEC = 10.0;

const METEOR_SLOTS = [
  {
    slot: 0,
    offsetSec: 0.45,
    x0: 0.12,
    y0: 0.06,
    x1: 0.78,
    y1: 0.55,
    tailPx: 224,
    dur: 1.48,
    coreHex: "#ffffff",
    midHex: "#fde047",
    outerHex: "#38bdf8",
    wakeHex: "rgba(125, 211, 252, 0.22)"
  },
  {
    slot: 1,
    offsetSec: 2.85,
    x0: 0.88,
    y0: 0.07,
    x1: 0.22,
    y1: 0.53,
    tailPx: 198,
    dur: 1.42,
    coreHex: "#ffffff",
    midHex: "#6ee7b7",
    outerHex: "#38bdf8",
    wakeHex: "rgba(110, 231, 183, 0.20)"
  },
  {
    slot: 2,
    offsetSec: 5.35,
    x0: 0.24,
    y0: 0.05,
    x1: 0.90,
    y1: 0.48,
    tailPx: 236,
    dur: 1.54,
    coreHex: "#ffffff",
    midHex: "#fbbf24",
    outerHex: "#fb7185",
    wakeHex: "rgba(253, 224, 71, 0.22)"
  },
  {
    slot: 3,
    offsetSec: 7.85,
    x0: 0.80,
    y0: 0.06,
    x1: 0.15,
    y1: 0.51,
    tailPx: 184,
    dur: 1.38,
    coreHex: "#ffffff",
    midHex: "#fef08a",
    outerHex: "#22d3ee",
    wakeHex: "rgba(56, 189, 248, 0.22)"
  }
];

const COLOR_CACHE = new Map();
const DAY_COLOR_CACHE = new Map();

function smoothstep(a, b, x) {
  const t = Math.max(0, Math.min(1, (x - a) / Math.max(0.0001, b - a)));
  return t * t * (3 - 2 * t);
}

export function evaluateDayNightCycle(cycleTimeSec) {
  const s = ((cycleTimeSec % DAY_NIGHT_CYCLE_SEC) + DAY_NIGHT_CYCLE_SEC) % DAY_NIGHT_CYCLE_SEC;
  let daylight = 0;
  if (s >= 13 && s < 24) {
    daylight = smoothstep(13, 24, s);
  } else if (s >= 24 && s < 40) {
    daylight = 1.0;
  } else if (s >= 40 && s < 53) {
    daylight = 1.0 - smoothstep(40, 53, s);
  }

  const dawn = (s >= 12 && s <= 25)
    ? Math.pow(Math.sin(((s - 12) / 13) * Math.PI), 1.35)
    : 0;
  const sunset = (s >= 39 && s <= 54)
    ? Math.pow(Math.sin(((s - 39) / 15) * Math.PI), 1.35)
    : 0;
  const twilight = (s >= 49 && s <= 59.5)
    ? Math.pow(Math.sin(((s - 49) / 10.5) * Math.PI), 1.3)
    : 0;

  const nightGlow = Math.max(0, Math.min(1, 1.0 - smoothstep(15, 23, s) + smoothstep(44, 53, s)));

  let phase = "midnight";
  if (s >= 14 && s < 23) phase = "dawn";
  else if (s >= 23 && s < 41) phase = "day";
  else if (s >= 41 && s < 51) phase = "sunset";
  else if (s >= 51) phase = "twilight";

  const sunProgress = Math.max(0, Math.min(1, (s - 14) / 36));

  return {
    cycleSec: s,
    phase,
    daylight,
    nightGlow,
    dawn,
    sunset,
    twilight,
    sunProgress
  };
}

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

function getDaylightHex(hex, kind, yNorm, xNorm = 0.5) {
  if (!hex || hex[0] !== "#" || hex.length < 7) return "#38bdf8";
  const bucketY = Math.round(Math.max(0, Math.min(1, yNorm)) * 5);
  const inMoonPocket = kind === "panorama" && xNorm > 0.80 && yNorm < 0.44 ? 1 : 0;
  const cacheKey = `${hex}:${kind}:${bucketY}:${inMoonPocket}`;
  const hit = DAY_COLOR_CACHE.get(cacheKey);
  if (hit) return hit;

  const r = parseInt(hex.slice(1, 3), 16) || 0;
  const g = parseInt(hex.slice(3, 5), 16) || 0;
  const b = parseInt(hex.slice(5, 7), 16) || 0;
  const luma = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
  const yFrac = bucketY / 5;

  let dr;
  let dg;
  let db;

  if (inMoonPocket && r > b && luma > 0.45) {
    dr = Math.min(255, Math.round(168 + luma * 76));
    dg = Math.min(255, Math.round(218 + luma * 34));
    db = Math.min(255, Math.round(244 + luma * 11));
  } else if (kind === "garden" && yFrac >= 0.48 && (g >= b * 0.82 || r >= b)) {
    if (r > g + 20) {
      dr = Math.min(255, Math.round(188 + luma * 67));
      dg = Math.min(255, Math.round(138 + luma * 94));
      db = Math.min(255, Math.round(36 + luma * 58));
    } else {
      dr = Math.min(255, Math.round(34 + luma * 98));
      dg = Math.min(255, Math.round(108 + luma * 116));
      db = Math.min(255, Math.round(52 + luma * 66));
    }
  } else if (luma < 0.20 && yFrac > 0.46) {
    dr = Math.round(24 + luma * 120);
    dg = Math.round(86 + luma * 165);
    db = Math.round(54 + luma * 95);
  } else if (r > b + 22 && luma > 0.34) {
    dr = Math.min(255, Math.round(238 + luma * 17));
    dg = Math.min(255, Math.round(192 + luma * 54));
    db = Math.min(255, Math.round(58 + luma * 90));
  } else {
    const horizonWarmth = Math.max(0, (yFrac - 0.35) / 0.65);
    const skyLift = Math.min(1, 0.38 + luma * 0.85);
    dr = Math.min(255, Math.round(38 + skyLift * 142 + horizonWarmth * 54));
    dg = Math.min(255, Math.round(138 + skyLift * 96 + horizonWarmth * 18));
    db = Math.min(255, Math.round(206 + skyLift * 48 - horizonWarmth * 18));
  }

  const toHex = (n) => Math.max(0, Math.min(255, n)).toString(16).padStart(2, "0");
  const out = `#${toHex(dr)}${toHex(dg)}${toHex(db)}`;
  DAY_COLOR_CACHE.set(cacheKey, out);
  return out;
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
    this.onMeteorLaunch = null;
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
    this.cycleTime = this.reducedMotion ? 4.0 : 0.0;
    this.meteorClock = 0.0;
    this.lastMeteorWindow = -1;
    this.firedSlotsInWindow = new Set();
    this.activeMeteors = [];
    this.meteorEmbers = [];
    this.meteorsLaunched = 0;

    this.gaze = { tx: 0.5, ty: 0.35, x: 0.5, y: 0.35 };
    this.panPtr = { nx: 0.5, ny: 0.5, inside: false };
    this.garPtr = { nx: 0.5, ny: 0.5, inside: false };
    this.wakeGlyphs = [];
    this.garWakeGlyphs = [];
    this.bgWakeGlyphs = [];
    this.bodyScreenPositions = [];
    this.hoveredBody = null;
    this._bgDirty = true;
    this._lastBgDaylight = -1;
    this._lastBgDawn = -1;
    this._lastBgSunset = -1;
    this._bgFrameSkip = 0;
    this._sunflowerSprites = new Map();
    this._looping = false;

    this.panFlow = this._initFlowParticles(72, 0.72);
    this.garFlow = this._initFlowParticles(60, 0.54);

    this.dpr = 1;
    this.bgDpr = 1;
    this.bgW = 1440;
    this.bgH = 1900;
    this.panW = 1120;
    this.panH = 296;
    this.garW = 1120;
    this.garH = 312;

    this.panPlanes = null;
    this.panPlanesDay = null;
    this.garPlanes = null;
    this.garPlanesDay = null;
    this.bgBaked = null;
    this.bgBakedDay = null;

    this._resize();
    this._bindEvents();
    this.renderFrame(0);
    if (!this.reducedMotion) {
      this._startLoop();
    }
  }

  setMeteorListener(fn) {
    this.onMeteorLaunch = typeof fn === "function" ? fn : null;
  }

  getEnvironmentState() {
    const env = evaluateDayNightCycle(this.cycleTime);
    return {
      ...env,
      meteorsLaunched: this.meteorsLaunched,
      activeMeteors: this.activeMeteors.length
    };
  }

  setCycleTime(sec) {
    this.cycleTime = Number(sec) || 0;
    this._bgDirty = true;
    this.renderFrame(0);
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
        dayColor: FLOW_PALETTE_DAY[i % FLOW_PALETTE_DAY.length],
        glyph: glyphs[i % glyphs.length],
        life: rand(),
        speed: 0.65 + rand() * 0.75,
        width: 1.25 + rand() * 1.15
      });
    }
    return arr;
  }

  // WHY: Bakes both nocturnal Starry Night and sunlit Arles Day 4-plane calligraphic buffers once per resize so 60s day-night transitions cost 0 stroke recalculations per frame.
  _bakeCalligraphicPlanes(layerData, w, h, kind = "sky", isDay = false) {
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
    p0.fillStyle = isDay ? "#1d74b8" : "#07142c";
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
      const yNorm = r / Math.max(1, rows);
      for (let k = 0; k < runs.length; k++) {
        const [bCol, bLen] = runs[k];
        const xNorm = (xCur + bLen * 0.5) / cols;
        const mappedHex = isDay ? getDaylightHex(bCol, kind, yNorm, xNorm) : bCol;
        p0.fillStyle = getColorMeta(mappedHex).lifted;
        p0.fillRect(xCur * colStep, ry, bLen * colStep + 0.8, rh);
        xCur += bLen;
      }
    }

    const atmoGrad = p0.createLinearGradient(0, h * 0.04, 0, h * 0.98);
    if (isDay) {
      if (kind === "garden") {
        atmoGrad.addColorStop(0, "rgba(56, 189, 248, 0.24)");
        atmoGrad.addColorStop(0.45, "rgba(186, 230, 253, 0.26)");
        atmoGrad.addColorStop(0.75, "rgba(253, 224, 71, 0.22)");
        atmoGrad.addColorStop(1, "rgba(234, 179, 8, 0.14)");
      } else {
        atmoGrad.addColorStop(0, "rgba(14, 116, 194, 0.22)");
        atmoGrad.addColorStop(0.54, "rgba(125, 211, 252, 0.26)");
        atmoGrad.addColorStop(0.86, "rgba(254, 240, 138, 0.24)");
        atmoGrad.addColorStop(1, "rgba(253, 224, 71, 0.18)");
      }
    } else if (kind === "garden") {
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

    if (kind === "panorama" && !isDay) {
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
      const strokeHex = isDay ? getDaylightHex(scol, kind, ym, xm) : scol;
      drawTaperedImpastoStroke(
        lc,
        x0 * w,
        y0 * h,
        xm * w,
        ym * h,
        x1 * w,
        y1 * h,
        strokeHex,
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
      p.ctx.globalAlpha = isDay ? 0.88 : 0.95;
      p.ctx.font = `700 ${fontSz.toFixed(3)}px ${monoFamily}`;
      p.ctx.textBaseline = "alphabetic";
    });

    for (let r = 0; r < grid.length; r++) {
      const runs = grid[r];
      const mRow = motifs[r] || "";
      const py = (r + 0.82) * rowStep;
      const yNorm = r / Math.max(1, rows);
      let colCur = 0;
      for (let k = 0; k < runs.length; k++) {
        const [colHex, chunk] = runs[k];
        if (colHex) {
          const xNorm = (colCur + chunk.length * 0.5) / cols;
          const mappedHex = isDay ? getDaylightHex(colHex, kind, yNorm, xNorm) : colHex;
          const liftedHex = getColorMeta(mappedHex).lifted;
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

  _bakeSingleFullBackdrop(isDay = false) {
    const w = this.bgW;
    const h = this.bgH;
    const bgDpr = this.bgDpr || 1;
    const c = document.createElement("canvas");
    c.width = Math.max(1, Math.round(w * bgDpr));
    c.height = Math.max(1, Math.round(h * bgDpr));
    const ctx = c.getContext("2d", { alpha: false });
    ctx.setTransform(bgDpr, 0, 0, bgDpr, 0, 0);

    ctx.fillStyle = isDay ? "#1767a8" : "#050b1a";
    ctx.fillRect(0, 0, w, h);

    const gar = this.vgScene.garden;
    const skyOnly = this.vgScene.sky || this.vgScene.panorama;
    if (!skyOnly || !gar) return c;

    const skyTileW = Math.min(w, 1280);
    const skyTileH = Math.max(340, Math.round(skyTileW * 0.36));
    const garTileW = Math.min(w, 1440);
    const garBandH = Math.max(340, Math.round(garTileW * 0.34));
    const skyPlanes = this._bakeCalligraphicPlanes(skyOnly, skyTileW, skyTileH, "sky", isDay);
    const garPlanes = this._bakeCalligraphicPlanes(gar, garTileW, garBandH, "garden", isDay);

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
      zenithGrad.addColorStop(0, isDay ? "rgba(12, 74, 138, 0.42)" : "rgba(4, 9, 22, 0.58)");
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

    return c;
  }

  _bakeFullPageBackdrop() {
    this.bgBaked = this._bakeSingleFullBackdrop(false);
    this.bgBakedDay = this._bakeSingleFullBackdrop(true);
    this._bgDirty = true;
  }

  _resize() {
    if (this._planeCaches) this._planeCaches.clear();
    this.dpr = 1;
    const docEl = document.documentElement;
    this.bgW = Math.max(320, docEl.clientWidth || window.innerWidth || 1440);
    this.bgH = Math.max(window.innerHeight || 900, docEl.scrollHeight || 1400, document.body.offsetHeight || 1400);
    this.bgDpr = 1;
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
      this.panPlanes = this._bakeCalligraphicPlanes(this.vgScene.panorama, this.panW, this.panH, "panorama", false);
      this.panPlanesDay = this._bakeCalligraphicPlanes(this.vgScene.panorama, this.panW, this.panH, "panorama", true);
    }

    if (this.garCanvas && this.garCtx) {
      const rect = this.garCanvas.getBoundingClientRect();
      this.garW = Math.max(280, Math.round(rect.width || 1120));
      this.garH = Math.max(196, Math.round(rect.height || 312));
      this.garCanvas.width = Math.round(this.garW * this.dpr);
      this.garCanvas.height = Math.round(this.garH * this.dpr);
      this.garCtx.setTransform(this.dpr, 0, 0, this.dpr, 0, 0);
      this.garPlanes = this._bakeCalligraphicPlanes(this.vgScene.garden, this.garW, this.garH, "garden", false);
      this.garPlanesDay = this._bakeCalligraphicPlanes(this.vgScene.garden, this.garW, this.garH, "garden", true);
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
      if (this.reducedMotion) {
        this.activeMeteors.length = 0;
        this.meteorEmbers.length = 0;
        this.cycleTime = 4.0;
        this._bgDirty = true;
        this.renderFrame(0);
      } else {
        this._startLoop();
      }
    });

    if (typeof ResizeObserver === "function") {
      const ro = new ResizeObserver(() => {
        const targetH = Math.max(window.innerHeight || 900, document.documentElement.scrollHeight || 1400);
        if (Math.abs(targetH - this.bgH) > 120) {
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
      if (!this.reducedMotion && Math.hypot(ev.movementX || 0, ev.movementY || 0) > 1.2) {
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
        if (!this.reducedMotion && lastX > -900) {
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
        if (!this.reducedMotion) {
          this.injectImpulse(x / Math.max(1, this.panW), y / Math.max(1, this.panH), 12, -8);
          this.triggerSwirlBurst(this.wakeGlyphs, x, y);
        }
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
        if (!this.reducedMotion && gxLast > -900) {
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
        if (this.reducedMotion) return;
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

  // WHY: Launches exactly 4 staggered Giant Shooting Stars per 10-second window across #panorama-canvas, #garden-canvas, and #sky-canvas.
  _stepMeteors(dt) {
    if (this.reducedMotion || dt <= 0) return;

    this.meteorClock += dt;
    const windowIdx = Math.floor(this.meteorClock / METEOR_CYCLE_SEC);
    const localSec = this.meteorClock - windowIdx * METEOR_CYCLE_SEC;

    if (windowIdx !== this.lastMeteorWindow) {
      this.lastMeteorWindow = windowIdx;
      this.firedSlotsInWindow.clear();
    }

    for (let i = 0; i < METEOR_SLOTS.length; i++) {
      const spec = METEOR_SLOTS[i];
      if (localSec >= spec.offsetSec && !this.firedSlotsInWindow.has(spec.slot)) {
        this.firedSlotsInWindow.add(spec.slot);
        const jitter = ((windowIdx * 3 + spec.slot) % 5 - 2) * 0.015;
        const meteor = {
          slot: spec.slot,
          x0: Math.max(0.06, Math.min(0.94, spec.x0 + jitter)),
          y0: spec.y0,
          x1: Math.max(0.08, Math.min(0.92, spec.x1 - jitter)),
          y1: spec.y1,
          tailPx: spec.tailPx,
          dur: spec.dur,
          age: 0,
          emberAccum: 0,
          coreHex: spec.coreHex,
          midHex: spec.midHex,
          outerHex: spec.outerHex,
          wakeHex: spec.wakeHex
        };
        this.activeMeteors.push(meteor);
        this.meteorsLaunched += 1;
        this._bgDirty = true;

        const dx = meteor.x1 - meteor.x0;
        const dy = meteor.y1 - meteor.y0;
        this.injectImpulse((meteor.x0 + meteor.x1) * 0.5, (meteor.y0 + meteor.y1) * 0.5, dx * 14, dy * 12);

        if (this.onMeteorLaunch) {
          this.onMeteorLaunch({
            slot: meteor.slot,
            nx: (meteor.x0 + meteor.x1) * 0.5,
            ny: (meteor.y0 + meteor.y1) * 0.5,
            dirX: dx >= 0 ? 1 : -1,
            tailPx: meteor.tailPx,
            count: this.meteorsLaunched
          });
        }
      }
    }

    for (let i = this.activeMeteors.length - 1; i >= 0; i--) {
      const m = this.activeMeteors[i];
      m.age += dt;
      m.emberAccum += dt;
      const u = Math.min(1, m.age / m.dur);
      if (u < 0.96 && m.emberAccum >= 0.042) {
        m.emberAccum = 0;
        const hx = m.x0 + (m.x1 - m.x0) * u;
        const hy = m.y0 + (m.y1 - m.y0) * u;
        if (this.meteorEmbers.length > 96) this.meteorEmbers.shift();
        this.meteorEmbers.push({
          nx: hx + (Math.random() - 0.5) * 0.012,
          ny: hy + (Math.random() - 0.5) * 0.018,
          vnx: (Math.random() - 0.5) * 0.024,
          vny: 0.012 + Math.random() * 0.025,
          life: 1.0,
          color: Math.random() < 0.55 ? m.midHex : m.outerHex,
          size: 1.8 + Math.random() * 1.8
        });
      }
      if (m.age >= m.dur + 0.42) {
        this.activeMeteors.splice(i, 1);
      }
    }

    for (let i = this.meteorEmbers.length - 1; i >= 0; i--) {
      const e = this.meteorEmbers[i];
      e.nx += e.vnx * dt;
      e.ny += e.vny * dt;
      e.life -= dt * 1.35;
      if (e.life <= 0.02) {
        this.meteorEmbers.splice(i, 1);
      }
    }
  }

  _drawGiantMeteors(ctx, w, h, yScale = 1.0, daylight = 0) {
    if (!this.activeMeteors.length && !this.meteorEmbers.length) return;
    ctx.save();

    for (let i = 0; i < this.activeMeteors.length; i++) {
      const m = this.activeMeteors[i];
      const u = Math.min(1, m.age / m.dur);
      const fadeOut = m.age <= m.dur ? 1.0 : Math.max(0, 1 - (m.age - m.dur) / 0.42);
      const fadeIn = Math.min(1, m.age / 0.12);
      const alpha = fadeIn * fadeOut * (daylight > 0.65 ? 0.90 : 1.0);
      if (alpha <= 0.01) continue;

      const xStart = m.x0 * w;
      const yStart = m.y0 * h * yScale;
      const xEnd = m.x1 * w;
      const yEnd = m.y1 * h * yScale;
      const hx = xStart + (xEnd - xStart) * u;
      const hy = yStart + (yEnd - yStart) * u;

      const dx = xEnd - xStart;
      const dy = yEnd - yStart;
      const pathLen = Math.hypot(dx, dy) || 1;
      const ux = dx / pathLen;
      const uy = dy / pathLen;
      const nx = -uy;
      const ny = ux;

      const maxTail = Math.max(162, Math.min(m.tailPx, w * 0.56));
      const curTail = Math.min(maxTail, Math.max(48, u * pathLen * 0.95));
      const tx = hx - ux * curTail;
      const ty = hy - uy * curTail;

      const cloudGlowR = Math.min(84, curTail * 0.42);
      const cloudX = hx - ux * (curTail * 0.28);
      const cloudY = hy - uy * (curTail * 0.28);
      const cg = ctx.createRadialGradient(cloudX, cloudY, 2, cloudX, cloudY, cloudGlowR);
      cg.addColorStop(0, m.wakeHex);
      cg.addColorStop(1, "rgba(56, 189, 248, 0)");
      ctx.globalAlpha = alpha;
      ctx.fillStyle = cg;
      ctx.beginPath();
      ctx.arc(cloudX, cloudY, cloudGlowR, 0, Math.PI * 2);
      ctx.fill();

      const tailGrad = ctx.createLinearGradient(hx, hy, tx, ty);
      tailGrad.addColorStop(0, m.coreHex);
      tailGrad.addColorStop(0.18, m.midHex);
      tailGrad.addColorStop(0.58, m.outerHex);
      tailGrad.addColorStop(1, "rgba(56, 189, 248, 0)");

      ctx.globalAlpha = alpha * 0.48;
      ctx.fillStyle = tailGrad;
      ctx.beginPath();
      ctx.moveTo(hx + nx * 5.6, hy + ny * 5.6);
      ctx.lineTo(tx, ty);
      ctx.lineTo(hx - nx * 5.6, hy - ny * 5.6);
      ctx.closePath();
      ctx.fill();

      const midX = (hx + tx) * 0.5 + nx * 2.4;
      const midY = (hy + ty) * 0.5 + ny * 2.4;
      drawTaperedImpastoStroke(ctx, tx, ty, midX, midY, hx, hy, m.midHex, 4.4, alpha * 0.86);

      ctx.globalAlpha = alpha * 0.96;
      ctx.strokeStyle = "#ffffff";
      ctx.lineWidth = 2.2;
      ctx.lineCap = "round";
      ctx.beginPath();
      ctx.moveTo(hx, hy);
      ctx.lineTo(hx - ux * (curTail * 0.52), hy - uy * (curTail * 0.52));
      ctx.stroke();

      if (m.age <= m.dur) {
        const comaHalo = ctx.createRadialGradient(hx, hy, 1, hx, hy, 22);
        comaHalo.addColorStop(0, "rgba(255, 255, 255, 0.92)");
        comaHalo.addColorStop(0.38, "rgba(254, 240, 138, 0.55)");
        comaHalo.addColorStop(0.75, "rgba(56, 189, 248, 0.22)");
        comaHalo.addColorStop(1, "rgba(56, 189, 248, 0)");
        ctx.globalAlpha = alpha;
        ctx.fillStyle = comaHalo;
        ctx.beginPath();
        ctx.arc(hx, hy, 22, 0, Math.PI * 2);
        ctx.fill();

        const ang = Math.atan2(uy, ux);
        drawStarPolygon(ctx, hx, hy, 12.2, 3.6, 8, ang + this.time * 2.2);
        ctx.fillStyle = m.midHex;
        ctx.fill();

        drawStarPolygon(ctx, hx, hy, 8.2, 2.4, 4, ang);
        ctx.fillStyle = "#ffffff";
        ctx.fill();
      }
    }

    for (let i = 0; i < this.meteorEmbers.length; i++) {
      const e = this.meteorEmbers[i];
      const ex = e.nx * w;
      const ey = e.ny * h * yScale;
      if (ey > h * 0.92) continue;
      ctx.globalAlpha = Math.max(0, Math.min(1, e.life * 0.88));
      ctx.fillStyle = e.color;
      ctx.beginPath();
      ctx.arc(ex, ey, e.size, 0, Math.PI * 2);
      ctx.fill();
    }

    ctx.restore();
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

  _drawFluidImpastoFlow(ctx, particles, w, h, maxNy, dt, daylight = 0) {
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
      const col = daylight > 0.55 ? p.dayColor : p.color;

      drawTaperedImpastoStroke(
        ctx,
        x - tx,
        y - ty,
        x - ty * 0.24,
        y + tx * 0.24,
        x + tx,
        y + ty,
        col,
        p.width * 1.15,
        env * 0.64
      );
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
      if (!this.reducedMotion) this.triggerSwirlBurst(this.wakeGlyphs, found.x, found.y);
      if (this.onBodyInspect) this.onBodyInspect(found.label);
    }
  }

  _drawWakePool(ctx, pool, w, h, dt) {
    if (!pool.length) return;
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

  _getSunflowerSprite(rad) {
    const key = Math.round(rad);
    const hit = this._sunflowerSprites.get(key);
    if (hit) return hit;

    const span = Math.ceil(key * 2.8);
    const c = document.createElement("canvas");
    c.width = span;
    c.height = span;
    const sc = c.getContext("2d");
    const mid = span * 0.5;
    sc.translate(mid, mid);

    const bloomGlow = sc.createRadialGradient(0, 0, key * 0.12, 0, 0, key * 1.25);
    bloomGlow.addColorStop(0, "rgba(253, 224, 71, 0.30)");
    bloomGlow.addColorStop(0.65, "rgba(245, 158, 11, 0.12)");
    bloomGlow.addColorStop(1, "rgba(245, 158, 11, 0)");
    sc.fillStyle = bloomGlow;
    sc.beginPath();
    sc.arc(0, 0, key * 1.25, 0, Math.PI * 2);
    sc.fill();

    sc.font = "700 8.5px 'JetBrains Mono', ui-monospace, monospace";
    sc.textAlign = "center";
    sc.textBaseline = "middle";
    const petals = 12;
    for (let p = 0; p < petals; p++) {
      const a = (p * Math.PI * 2) / petals;
      const r0 = key * 0.30;
      const rm = key * 0.62;
      const r1 = key * 0.88;
      const px = Math.cos(a) * r1;
      const py = Math.sin(a) * r1;
      drawTaperedImpastoStroke(
        sc,
        Math.cos(a) * r0,
        Math.sin(a) * r0,
        Math.cos(a + 0.15) * rm,
        Math.sin(a + 0.15) * rm,
        px,
        py,
        p % 2 === 0 ? "#fde047" : "#f59e0b",
        2.25,
        0.92
      );
      sc.globalAlpha = 0.90;
      sc.fillStyle = p % 2 === 0 ? "#fef9c3" : "#fcd34d";
      sc.fillText(p % 2 === 0 ? "*" : "~", px, py);
    }

    sc.globalAlpha = 0.95;
    sc.fillStyle = "#78350f";
    sc.beginPath();
    sc.arc(0, 0, key * 0.27, 0, Math.PI * 2);
    sc.fill();
    sc.strokeStyle = "#fbbf24";
    sc.lineWidth = 1.15;
    sc.stroke();
    sc.fillStyle = "#fde047";
    sc.fillText("@", 0, 0);

    this._sunflowerSprites.set(key, c);
    return c;
  }

  _drawHeliotropicSunflowers(ctx, w, h, flowers, targetX, targetY, daylight = 0) {
    ctx.save();
    for (let i = 0; i < flowers.length; i++) {
      const [fx, fy, rad] = flowers[i];
      const cx = fx * w;
      const cy = fy * h;
      const dx = targetX - cx;
      const dy = targetY - cy;
      const gazeAng = Math.atan2(dy, dx);
      const leanX = Math.cos(gazeAng) * Math.min(4.8, Math.hypot(dx, dy) * 0.013);
      const leanY = Math.sin(gazeAng) * Math.min(3.8, Math.hypot(dx, dy) * 0.010);
      const sp = this._getSunflowerSprite(rad);
      const scale = 1 + daylight * 0.05;
      const drawSz = sp.width * scale;

      ctx.save();
      ctx.translate(cx + leanX, cy + leanY);
      ctx.rotate(gazeAng * 0.18 + Math.sin(this.time * 1.1 + i) * 0.04);
      ctx.drawImage(sp, -drawSz * 0.5, -drawSz * 0.5, drawSz, drawSz);
      ctx.restore();
    }
    ctx.restore();
  }

  _getCoronaSprite(r, warm) {
    if (!this._coronaSprites) this._coronaSprites = new Map();
    const key = `${r}:${warm ? 1 : 0}`;
    const hit = this._coronaSprites.get(key);
    if (hit) return hit;

    const span = Math.ceil(r * 3.6);
    const c = document.createElement("canvas");
    c.width = span;
    c.height = span;
    const cc = c.getContext("2d");
    const mid = span * 0.5;
    cc.translate(mid, mid);

    const glowR = r * 1.65;
    const grad = cc.createRadialGradient(0, 0, 1, 0, 0, glowR);
    if (warm) {
      grad.addColorStop(0, "rgba(254, 249, 195, 0.36)");
      grad.addColorStop(0.55, "rgba(253, 224, 71, 0.15)");
      grad.addColorStop(1, "rgba(253, 224, 71, 0)");
    } else {
      grad.addColorStop(0, "rgba(224, 242, 254, 0.32)");
      grad.addColorStop(0.55, "rgba(125, 211, 252, 0.14)");
      grad.addColorStop(1, "rgba(125, 211, 252, 0)");
    }
    cc.fillStyle = grad;
    cc.beginPath();
    cc.arc(0, 0, glowR, 0, Math.PI * 2);
    cc.fill();

    const arcs = 6;
    for (let k = 0; k < arcs; k++) {
      const a0 = (k * Math.PI * 2) / arcs;
      const am = a0 + 0.26;
      const a1 = a0 + 0.52;
      const cr = r * 0.88;
      drawTaperedImpastoStroke(
        cc,
        Math.cos(a0) * cr,
        Math.sin(a0) * cr,
        Math.cos(am) * (cr * 1.06),
        Math.sin(am) * (cr * 1.06),
        Math.cos(a1) * cr,
        Math.sin(a1) * cr,
        warm ? "#fde047" : "#7dd3fc",
        1.55,
        0.72
      );
    }

    cc.font = "700 8px 'JetBrains Mono', ui-monospace, monospace";
    cc.textAlign = "center";
    cc.textBaseline = "middle";
    cc.globalAlpha = 0.90;
    const glyphs = 8;
    for (let g = 0; g < glyphs; g++) {
      const a = (g * Math.PI * 2) / glyphs;
      cc.fillStyle = warm ? "#fef08a" : "#bae6fd";
      cc.fillText(g % 2 === 0 ? "~" : "*", Math.cos(a) * r, Math.sin(a) * r);
    }

    this._coronaSprites.set(key, c);
    return c;
  }

  _drawGazeCoronas(ctx, w, h, targetX, targetY, nightGlow = 1) {
    const starVis = Math.max(0.14, nightGlow);
    ctx.save();
    for (let i = 0; i < PAN_STARS.length; i++) {
      const [nx, ny, r, warm] = PAN_STARS[i];
      const isMoon = i === PAN_STARS.length - 1;
      const bodyVis = isMoon ? Math.max(0.22, nightGlow) : starVis;
      const sx = nx * w + (this.gaze.x - 0.5) * 6;
      const sy = ny * h + (this.gaze.y - 0.35) * 4;
      const lookAng = Math.atan2(targetY - sy, targetX - sx);
      const spin = this.time * (i % 2 === 0 ? 0.28 : -0.22) + lookAng * 0.28;
      const pulse = 0.92 + 0.08 * Math.sin(this.time * 2.1 + i * 1.4);
      const sp = this._getCoronaSprite(r, warm);
      const sz = sp.width * pulse;

      ctx.save();
      ctx.globalAlpha = bodyVis;
      ctx.translate(sx, sy);
      ctx.rotate(spin);
      ctx.drawImage(sp, -sz * 0.5, -sz * 0.5, sz, sz);
      ctx.restore();
    }
    ctx.restore();
  }

  _drawArlesSun(ctx, w, h, env, isGarden = false) {
    const sunAlpha = Math.max(env.daylight, env.dawn * 0.65, env.sunset * 0.65);
    if (sunAlpha <= 0.03) return null;

    const arcU = env.sunProgress;
    const sunNx = 0.18 + arcU * 0.64;
    const sunNy = isGarden
      ? (0.34 - Math.sin(arcU * Math.PI) * 0.20)
      : (0.42 - Math.sin(arcU * Math.PI) * 0.24);
    const sx = sunNx * w + (this.gaze.x - 0.5) * 8;
    const sy = sunNy * h + (this.gaze.y - 0.4) * 5;
    const baseR = isGarden ? 20 : 25;

    ctx.save();
    const bloomR = baseR * 3.4;
    const bloom = ctx.createRadialGradient(sx, sy, baseR * 0.25, sx, sy, bloomR);
    bloom.addColorStop(0, `rgba(255, 251, 235, ${(0.62 * sunAlpha).toFixed(3)})`);
    bloom.addColorStop(0.35, `rgba(253, 224, 71, ${(0.34 * sunAlpha).toFixed(3)})`);
    bloom.addColorStop(0.72, `rgba(251, 146, 60, ${(0.14 * sunAlpha).toFixed(3)})`);
    bloom.addColorStop(1, "rgba(251, 191, 36, 0)");
    ctx.fillStyle = bloom;
    ctx.beginPath();
    ctx.arc(sx, sy, bloomR, 0, Math.PI * 2);
    ctx.fill();

    const rays = 14;
    const rot = this.time * 0.22;
    for (let i = 0; i < rays; i++) {
      const a = rot + (i * Math.PI * 2) / rays;
      const r0 = baseR * 0.85;
      const rm = baseR * 1.45;
      const r1 = baseR * (i % 2 === 0 ? 2.05 : 1.72);
      drawTaperedImpastoStroke(
        ctx,
        sx + Math.cos(a) * r0,
        sy + Math.sin(a) * r0,
        sx + Math.cos(a + 0.14) * rm,
        sy + Math.sin(a + 0.14) * rm,
        sx + Math.cos(a) * r1,
        sy + Math.sin(a) * r1,
        i % 2 === 0 ? "#fef08a" : "#fbbf24",
        2.3,
        sunAlpha * 0.82
      );
    }

    ctx.globalAlpha = Math.min(1, sunAlpha * 0.96);
    ctx.fillStyle = "#fde047";
    ctx.beginPath();
    ctx.arc(sx, sy, baseR * 0.72, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = "#fffbeb";
    ctx.beginPath();
    ctx.arc(sx, sy, baseR * 0.44, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();

    return { x: sx, y: sy };
  }

  _drawAtmosphericPhaseVeil(ctx, w, h, env) {
    if (env.dawn > 0.01) {
      const dg = ctx.createLinearGradient(0, h * 0.08, 0, h);
      dg.addColorStop(0, `rgba(99, 102, 241, ${(0.12 * env.dawn).toFixed(3)})`);
      dg.addColorStop(0.52, `rgba(251, 113, 133, ${(0.24 * env.dawn).toFixed(3)})`);
      dg.addColorStop(1, `rgba(251, 191, 36, ${(0.22 * env.dawn).toFixed(3)})`);
      ctx.fillStyle = dg;
      ctx.fillRect(0, 0, w, h);
    }
    if (env.sunset > 0.01) {
      const sg = ctx.createLinearGradient(0, h * 0.05, 0, h);
      sg.addColorStop(0, `rgba(124, 58, 237, ${(0.18 * env.sunset).toFixed(3)})`);
      sg.addColorStop(0.54, `rgba(249, 115, 22, ${(0.26 * env.sunset).toFixed(3)})`);
      sg.addColorStop(1, `rgba(253, 224, 71, ${(0.20 * env.sunset).toFixed(3)})`);
      ctx.fillStyle = sg;
      ctx.fillRect(0, 0, w, h);
    }
    if (env.twilight > 0.01) {
      const tg = ctx.createLinearGradient(0, 0, 0, h);
      tg.addColorStop(0, `rgba(15, 23, 42, ${(0.22 * env.twilight).toFixed(3)})`);
      tg.addColorStop(0.65, `rgba(49, 46, 129, ${(0.18 * env.twilight).toFixed(3)})`);
      tg.addColorStop(1, `rgba(30, 58, 138, ${(0.12 * env.twilight).toFixed(3)})`);
      ctx.fillStyle = tg;
      ctx.fillRect(0, 0, w, h);
    }
  }

  _getOrUpdatePlaneCache(cacheKey, nightPlanes, dayPlanes, w, h, gxShift, gyShift, env) {
    if (!this._planeCaches) this._planeCaches = new Map();
    let entry = this._planeCaches.get(cacheKey);
    if (!entry || entry.w !== w || entry.h !== h) {
      const c = document.createElement("canvas");
      c.width = w;
      c.height = h;
      entry = { canvas: c, ctx: c.getContext("2d", { alpha: false }), w, h, gx: -99, gy: -99, dl: -99, dw: -99, ss: -99 };
      this._planeCaches.set(cacheKey, entry);
    }
    const needsUpdate =
      Math.abs(gxShift - entry.gx) > 0.002 ||
      Math.abs(gyShift - entry.gy) > 0.002 ||
      Math.abs(env.daylight - entry.dl) > 0.014 ||
      Math.abs(env.dawn - entry.dw) > 0.018 ||
      Math.abs(env.sunset - entry.ss) > 0.018;

    if (needsUpdate) {
      entry.gx = gxShift;
      entry.gy = gyShift;
      entry.dl = env.daylight;
      entry.dw = env.dawn;
      entry.ss = env.sunset;
      const lctx = entry.ctx;
      const mults = [-4.5, 2.5, 6.8, 12.0];
      lctx.globalAlpha = 1;
      lctx.fillStyle = env.daylight > 0.5 ? "#1d74b8" : "#07142c";
      lctx.fillRect(0, 0, w, h);

      if (nightPlanes && env.daylight < 0.995) {
        for (let p = 0; p < nightPlanes.length; p++) {
          const ox = gxShift * mults[p];
          const oy = gyShift * mults[p] * 0.65;
          const pad = Math.abs(mults[p]) + 2;
          lctx.drawImage(nightPlanes[p], -pad + ox, -pad + oy, w + pad * 2, h + pad * 2);
        }
      }
      if (dayPlanes && env.daylight > 0.005) {
        lctx.save();
        lctx.globalAlpha = env.daylight;
        for (let p = 0; p < dayPlanes.length; p++) {
          const ox = gxShift * mults[p];
          const oy = gyShift * mults[p] * 0.65;
          const pad = Math.abs(mults[p]) + 2;
          lctx.drawImage(dayPlanes[p], -pad + ox, -pad + oy, w + pad * 2, h + pad * 2);
        }
        lctx.restore();
      }
      this._drawAtmosphericPhaseVeil(lctx, w, h, env);
    }
    return entry.canvas;
  }

  _drawCompositePlanes(ctx, nightPlanes, dayPlanes, w, h, gxShift, gyShift, env, cacheKey = "pan") {
    if (!nightPlanes) {
      ctx.fillStyle = "#07142c";
      ctx.fillRect(0, 0, w, h);
      return;
    }
    const cached = this._getOrUpdatePlaneCache(cacheKey, nightPlanes, dayPlanes, w, h, gxShift, gyShift, env);
    ctx.globalAlpha = 1;
    ctx.drawImage(cached, 0, 0, w, h);
  }

  _drawSolarOrrery(ctx, w, h, gxShift, gyShift, env) {
    const sunX = w * 0.48 + gxShift * 5.0;
    const sunY = h * 0.50 + gyShift * 3.5;
    const maxRx = Math.min(280, w * 0.29);
    const maxRy = Math.min(62, h * 0.24);
    const tilt = -0.14 + gxShift * 0.04;
    const orreryAlpha = 1.0 - env.daylight * 0.22;

    ctx.save();
    ctx.globalAlpha = orreryAlpha;
    const sunHalo = ctx.createRadialGradient(sunX, sunY, 2, sunX, sunY, 28 + env.daylight * 8);
    sunHalo.addColorStop(0, "rgba(254, 249, 195, 0.62)");
    sunHalo.addColorStop(0.45, "rgba(251, 191, 36, 0.26)");
    sunHalo.addColorStop(1, "rgba(251, 191, 36, 0)");
    ctx.fillStyle = sunHalo;
    ctx.beginPath();
    ctx.arc(sunX, sunY, 28 + env.daylight * 8, 0, Math.PI * 2);
    ctx.fill();

    ctx.strokeStyle = "rgba(254, 240, 138, 0.90)";
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
      label: `Sun · 5,778 K · ${env.phase.toUpperCase()}`
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
      0.86 * orreryAlpha
    );
    ctx.globalAlpha = orreryAlpha;
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
      ctx.strokeStyle = isHov ? "rgba(253, 224, 71, 0.90)" : (env.daylight > 0.55 ? "rgba(255, 255, 255, 0.34)" : "rgba(147, 197, 253, 0.32)");
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
      const dt = Math.min(0.045, Math.max(0.001, (now - last) / 1000));
      last = now;
      this.renderFrame(dt);
      requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }

  renderFrame(dt) {
    if (!this.reducedMotion && dt > 0) {
      this.time += dt;
      this.cycleTime = (this.cycleTime + dt) % DAY_NIGHT_CYCLE_SEC;
      this._stepFluidSolver(dt);
      this._stepMeteors(dt);
    }

    this.gaze.x += (this.gaze.tx - this.gaze.x) * (dt > 0 ? 0.09 : 1);
    this.gaze.y += (this.gaze.ty - this.gaze.y) * (dt > 0 ? 0.09 : 1);

    const env = evaluateDayNightCycle(this.cycleTime);
    const gxShift = this.gaze.x - 0.5;
    const gyShift = this.gaze.y - 0.4;

    this._bgFrameSkip = (this._bgFrameSkip + 1) % 4;
    const bgPhaseChanged =
      this._bgDirty ||
      Math.abs(env.daylight - this._lastBgDaylight) > 0.032 ||
      Math.abs(env.dawn - this._lastBgDawn) > 0.035 ||
      Math.abs(env.sunset - this._lastBgSunset) > 0.035;

    if (this.bgBaked && bgPhaseChanged) {
      this._lastBgDaylight = env.daylight;
      this._lastBgDawn = env.dawn;
      this._lastBgSunset = env.sunset;
      if (!this._bgComp || this._bgComp.width !== this.bgW || this._bgComp.height !== this.bgH) {
        this._bgComp = document.createElement("canvas");
        this._bgComp.width = this.bgW;
        this._bgComp.height = this.bgH;
        this._bgCompCtx = this._bgComp.getContext("2d", { alpha: false });
      }
      const bcc = this._bgCompCtx;
      bcc.globalAlpha = 1;
      if (env.daylight < 0.995) {
        bcc.drawImage(this.bgBaked, 0, 0, this.bgW, this.bgH);
      }
      if (this.bgBakedDay && env.daylight > 0.005) {
        bcc.globalAlpha = env.daylight;
        bcc.drawImage(this.bgBakedDay, 0, 0, this.bgW, this.bgH);
        bcc.globalAlpha = 1;
      }
      this._drawAtmosphericPhaseVeil(bcc, this.bgW, this.bgH, env);
      this.bgCtx.drawImage(this._bgComp, 0, 0, this.bgW, this.bgH);
      this._bgHadOverlay = false;
      this._bgDirty = false;
    }

    const hasBgOverlay = this.activeMeteors.length > 0 || this.meteorEmbers.length > 0 || this.bgWakeGlyphs.length > 0;
    const gutterW = Math.floor((this.bgW - Math.min(this.bgW, 1168)) * 0.5);
    if (gutterW > 20 && this._bgComp && (hasBgOverlay || this._bgHadOverlay) && (dt === 0 || this._bgFrameSkip === 0 || !hasBgOverlay)) {
      const bandH = Math.min(this.bgH, 720);
      this.bgCtx.save();
      this.bgCtx.beginPath();
      this.bgCtx.rect(0, 0, gutterW + 8, bandH);
      this.bgCtx.rect(this.bgW - gutterW - 8, 0, gutterW + 8, bandH);
      this.bgCtx.clip();
      this.bgCtx.drawImage(this._bgComp, 0, 0, this.bgW, bandH, 0, 0, this.bgW, bandH);
      if (hasBgOverlay) {
        this._drawGiantMeteors(this.bgCtx, this.bgW, bandH, 0.85, env.daylight);
        if (this.bgWakeGlyphs.length > 0) {
          this._drawWakePool(this.bgCtx, this.bgWakeGlyphs, this.bgW, this.bgH, dt);
        }
      }
      this.bgCtx.restore();
      this._bgHadOverlay = hasBgOverlay;
    }

    if (this.panCtx && (dt === 0 || isVisible(this.panCanvas))) {
      const w = this.panW;
      const h = this.panH;
      this.bodyScreenPositions = [];
      this._drawCompositePlanes(this.panCtx, this.panPlanes, this.panPlanesDay, w, h, gxShift, gyShift, env, "pan");
      this._drawFluidImpastoFlow(this.panCtx, this.panFlow, w, h, 0.74, dt, env.daylight);
      const sunPt = this._drawArlesSun(this.panCtx, w, h, env, false);
      const tx = this.panPtr.inside ? this.panPtr.nx * w : (sunPt && env.daylight > 0.45 ? sunPt.x : this.gaze.x * w);
      const ty = this.panPtr.inside ? this.panPtr.ny * h : (sunPt && env.daylight > 0.45 ? sunPt.y : this.gaze.y * h);
      this._drawGazeCoronas(this.panCtx, w, h, tx, ty, env.nightGlow);
      this._drawGiantMeteors(this.panCtx, w, h, 1.0, env.daylight);
      this._drawSolarOrrery(this.panCtx, w, h, gxShift, gyShift, env);
      this._drawHeliotropicSunflowers(this.panCtx, w, h, PAN_SUNFLOWERS, tx, ty, env.daylight);
      this._drawWakePool(this.panCtx, this.wakeGlyphs, w, h, dt);
    }

    if (this.garCtx && (dt === 0 || isVisible(this.garCanvas))) {
      const w = this.garW;
      const h = this.garH;
      this._drawCompositePlanes(this.garCtx, this.garPlanes, this.garPlanesDay, w, h, gxShift * 1.12, gyShift * 1.12, env, "gar");
      this._drawFluidImpastoFlow(this.garCtx, this.garFlow, w, h, 0.52, dt, env.daylight);
      const garSunPt = this._drawArlesSun(this.garCtx, w, h, env, true);
      this._drawGiantMeteors(this.garCtx, w, h, 0.78, env.daylight);
      const tx = this.garPtr.inside ? this.garPtr.nx * w : (garSunPt && env.daylight > 0.45 ? garSunPt.x : this.gaze.x * w);
      const ty = this.garPtr.inside ? this.garPtr.ny * h : (garSunPt && env.daylight > 0.45 ? garSunPt.y : this.gaze.y * h);
      this._drawHeliotropicSunflowers(this.garCtx, w, h, GAR_SUNFLOWERS, tx, ty, env.daylight);
      this._drawWakePool(this.garCtx, this.garWakeGlyphs, w, h, dt);
    }
  }
}
