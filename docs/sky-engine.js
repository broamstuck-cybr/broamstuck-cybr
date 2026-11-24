// SPDX-License-Identifier: MIT
// WHY: Drives both the full-document seamless Starry Night sky and the interactive panoramic Solar Orrery & Milky Way window.

const PLANETS = [
  { name: "Mercury", au: "0.39 AU", period: "88 days", rf: 0.17, r: 2.5, color: "#cbd5e1", speed: 1.55, phase: 0.4, note: "Swift innermost rocky world" },
  { name: "Venus", au: "0.72 AU", period: "225 days", rf: 0.26, r: 3.3, color: "#fde68a", speed: 1.12, phase: 1.9, note: "Brilliant evening star cloud deck" },
  { name: "Earth & Moon", au: "1.00 AU", period: "365.25 days", rf: 0.36, r: 3.7, color: "#38bdf8", speed: 0.86, phase: 3.5, moon: true, note: "Blue marble with lunar satellite" },
  { name: "Mars", au: "1.52 AU", period: "687 days", rf: 0.47, r: 3.0, color: "#fb7185", speed: 0.66, phase: 5.1, note: "Iron-oxide desert world" },
  { name: "Jupiter", au: "5.20 AU", period: "11.86 years", rf: 0.61, r: 5.4, color: "#fbbf24", speed: 0.44, phase: 0.9, note: "Gas giant with banded equatorial jets" },
  { name: "Saturn", au: "9.58 AU", period: "29.45 years", rf: 0.76, r: 4.6, color: "#fcd34d", speed: 0.31, phase: 2.8, ring: true, note: "Crowned by icy Cassini ring system" },
  { name: "Uranus", au: "19.2 AU", period: "84.0 years", rf: 0.88, r: 3.6, color: "#67e8f9", speed: 0.22, phase: 4.4, note: "Axial-tilted ice giant" },
  { name: "Neptune", au: "30.1 AU", period: "164.8 years", rf: 0.99, r: 3.5, color: "#60a5fa", speed: 0.16, phase: 5.8, note: "Supersonic cobalt outer giant" }
];

const IMPASTO_COLORS = [
  "#132c54",
  "#1d437a",
  "#2d5fa8",
  "#4c84cc",
  "#5eead4",
  "#93c5fd",
  "#fde047",
  "#fbbf24"
];

export class LiquidStarrySky {
  constructor(bgCanvas, panoramaCanvas, onBodyInspect) {
    this.bgCanvas = bgCanvas;
    this.bgCtx = bgCanvas.getContext("2d", { alpha: false });
    this.panCanvas = panoramaCanvas;
    this.panCtx = panoramaCanvas ? panoramaCanvas.getContext("2d", { alpha: false }) : null;
    this.onBodyInspect = onBodyInspect;
    this.reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    this.cols = 36;
    this.rows = 16;
    this.vx = new Float32Array(this.cols * this.rows);
    this.vy = new Float32Array(this.cols * this.rows);

    this.turbulenceMode = 1;
    this.orbitSpeed = 1;
    this.time = 14.2;
    this.pointer = { px: -999, py: -999 };
    this.hoveredBody = null;
    this.ripples = [];
    this.meteors = [];
    this.bodyScreenPositions = [];

    this.bgW = 1440;
    this.bgH = 1800;
    this.panW = 1100;
    this.panH = 172;
    this.dpr = Math.min(window.devicePixelRatio || 1, 2);

    this._seedParticles();
    this._resize();
    this._bindEvents();
    this.renderFrame(0.016);
    if (!this.reducedMotion) {
      this._startLoop();
    }
  }

  _seedParticles() {
    let s = 18890619;
    const rand = () => {
      s = (1664525 * s + 1013904223) >>> 0;
      return (s >>> 8) / 16777215;
    };

    this.bgStrokes = [];
    for (let i = 0; i < 420; i++) {
      this.bgStrokes.push({
        nx: rand(),
        ny: rand(),
        len: 12 + rand() * 20,
        width: 1.3 + rand() * 2.4,
        color: IMPASTO_COLORS[Math.floor(rand() * IMPASTO_COLORS.length)],
        alpha: 0.18 + rand() * 0.34,
        speed: 0.35 + rand() * 0.7
      });
    }

    this.panStrokes = [];
    for (let i = 0; i < 290; i++) {
      this.panStrokes.push({
        nx: rand(),
        ny: rand(),
        len: 10 + rand() * 17,
        width: 1.3 + rand() * 2.3,
        color: IMPASTO_COLORS[Math.floor(rand() * IMPASTO_COLORS.length)],
        alpha: 0.24 + rand() * 0.42,
        speed: 0.45 + rand() * 0.85
      });
    }

    this.bgStars = [];
    for (let i = 0; i < 340; i++) {
      const onMw = rand() < 0.65;
      const t = rand();
      const spread = (rand() - 0.5) * (onMw ? 0.24 : 1.0);
      this.bgStars.push({
        nx: onMw ? t : rand(),
        ny: onMw ? Math.min(0.99, Math.max(0.01, 0.88 * (1 - t) + 0.08 * t + spread)) : rand(),
        r: 0.55 + rand() * 1.45,
        phase: rand() * Math.PI * 2,
        twinkle: 0.8 + rand() * 2.2,
        color: rand() > 0.32 ? "#dbeafe" : "#fef08a"
      });
    }

    this.panStars = [];
    for (let i = 0; i < 190; i++) {
      const onMw = rand() < 0.72;
      const t = rand();
      const spread = (rand() - 0.5) * (onMw ? 0.34 : 1.0);
      this.panStars.push({
        nx: onMw ? t : rand(),
        ny: onMw ? Math.min(0.96, Math.max(0.04, 0.84 * (1 - t) + 0.14 * t + spread)) : rand(),
        r: 0.6 + rand() * 1.5,
        phase: rand() * Math.PI * 2,
        twinkle: 0.9 + rand() * 2.5,
        color: rand() > 0.30 ? "#e0f2fe" : "#fef08a"
      });
    }

    this.panAureoles = [
      { nx: 0.19, ny: 0.24, r: 12, warm: true },
      { nx: 0.33, ny: 0.18, r: 10, warm: false },
      { nx: 0.50, ny: 0.32, r: 15, warm: true },
      { nx: 0.64, ny: 0.64, r: 13, warm: true },
      { nx: 0.75, ny: 0.26, r: 11, warm: false }
    ];
  }

  _resize() {
    this.dpr = Math.min(window.devicePixelRatio || 1, 2);
    this.bgW = Math.max(320, document.documentElement.clientWidth || window.innerWidth);
    this.bgH = Math.max(window.innerHeight, document.documentElement.scrollHeight);
    this.bgCanvas.width = Math.round(this.bgW * this.dpr);
    this.bgCanvas.height = Math.round(this.bgH * this.dpr);
    this.bgCtx.setTransform(this.dpr, 0, 0, this.dpr, 0, 0);

    if (this.panCanvas && this.panCtx) {
      const rect = this.panCanvas.getBoundingClientRect();
      this.panW = Math.max(280, rect.width || 1100);
      this.panH = Math.max(148, rect.height || 172);
      this.panCanvas.width = Math.round(this.panW * this.dpr);
      this.panCanvas.height = Math.round(this.panH * this.dpr);
      this.panCtx.setTransform(this.dpr, 0, 0, this.dpr, 0, 0);
    }
  }

  _bindEvents() {
    const onResize = () => {
      this._resize();
      this.renderFrame(0);
    };
    window.addEventListener("resize", onResize);
    if (typeof ResizeObserver === "function") {
      const ro = new ResizeObserver(() => {
        const targetH = Math.max(window.innerHeight, document.documentElement.scrollHeight);
        if (Math.abs(targetH - this.bgH) > 8) {
          this._resize();
          this.renderFrame(0);
        }
      });
      ro.observe(document.body);
    }

    if (this.panCanvas) {
      this.panCanvas.addEventListener("pointermove", (ev) => {
        const rect = this.panCanvas.getBoundingClientRect();
        const x = ev.clientX - rect.left;
        const y = ev.clientY - rect.top;
        if (this.pointer.px > -900) {
          this.injectImpulse(x / this.panW, y / this.panH, (x - this.pointer.px) * 0.35, (y - this.pointer.py) * 0.35);
        }
        this.pointer.px = x;
        this.pointer.py = y;
        this._checkBodyHover(x, y);
        if (this.reducedMotion) this.renderFrame(0.016);
      }, { passive: true });

      this.panCanvas.addEventListener("pointerleave", () => {
        this.pointer.px = -999;
      });

      this.panCanvas.addEventListener("pointerdown", (ev) => {
        const rect = this.panCanvas.getBoundingClientRect();
        const x = ev.clientX - rect.left;
        const y = ev.clientY - rect.top;
        this.triggerWave(x / this.panW, y / this.panH);
        this._checkBodyHover(x, y, true);
      }, { passive: true });
    }

    window.addEventListener("pointermove", (ev) => {
      const nx = ev.clientX / Math.max(1, window.innerWidth);
      const ny = ev.clientY / Math.max(1, window.innerHeight);
      this.injectImpulse(nx, ny, (ev.movementX || 0) * 0.16, (ev.movementY || 0) * 0.16);
    }, { passive: true });
  }

  injectImpulse(nx, ny, fx, fy) {
    const gxCenter = nx * this.cols;
    const gyCenter = ny * this.rows;
    const gRad = 4.2;
    for (let gy = 0; gy < this.rows; gy++) {
      for (let gx = 0; gx < this.cols; gx++) {
        const dx = gx - gxCenter;
        const dy = gy - gyCenter;
        const d2 = dx * dx + dy * dy;
        if (d2 < gRad * gRad) {
          const w = Math.exp(-d2 / 5.5);
          const idx = gy * this.cols + gx;
          this.vx[idx] = Math.max(-16, Math.min(16, this.vx[idx] + fx * w));
          this.vy[idx] = Math.max(-16, Math.min(16, this.vy[idx] + fy * w));
        }
      }
    }
  }

  triggerWave(nx = 0.52, ny = 0.48) {
    this.ripples.push({ nx, ny, r: 6, maxR: 210, alpha: 0.82 });
    for (let a = 0; a < Math.PI * 2; a += Math.PI / 6) {
      this.injectImpulse(nx + Math.cos(a) * 0.03, ny + Math.sin(a) * 0.08, Math.cos(a + 1.1) * 8, Math.sin(a + 1.1) * 8);
    }
    this.meteors.push({ nx: Math.max(0.08, nx - 0.14), ny: Math.max(0.12, ny - 0.22), vx: 0.011, vy: 0.022, life: 1.0 });
    if (this.reducedMotion) this.renderFrame(0.016);
  }

  setTurbulence(level) {
    this.turbulenceMode = level;
    this.triggerWave(0.5, 0.5);
  }

  setOrbitSpeed(mult) {
    this.orbitSpeed = mult;
    if (this.reducedMotion) this.renderFrame(0);
  }

  _sampleFluidNorm(nx, ny) {
    const gx = Math.max(0, Math.min(this.cols - 1, Math.floor(nx * this.cols)));
    const gy = Math.max(0, Math.min(this.rows - 1, Math.floor(ny * this.rows)));
    const idx = gy * this.cols + gx;
    return [this.vx[idx], this.vy[idx]];
  }

  _curlField(nx, ny) {
    const t = this.time * 0.22;
    const amp = this.turbulenceMode === 0 ? 0.45 : (this.turbulenceMode === 2 ? 1.6 : 1.05);
    let ux = 0.58;
    let uy = -0.08 + 0.24 * Math.sin(nx * 7.5 + t);

    const vortices = [
      [0.48, 0.46, 1.55 * amp, 0.20],
      [0.64, 0.62, -1.25 * amp, 0.16],
      [0.24, 0.36, 0.95 * amp, 0.17],
      [0.82, 0.40, 0.78 * amp, 0.15]
    ];
    for (let i = 0; i < vortices.length; i++) {
      const [vx0, vy0, str, rad] = vortices[i];
      const dx = nx - vx0;
      const dy = ny - vy0;
      const d2 = dx * dx + dy * dy + 0.004;
      const fall = Math.exp(-d2 / (2 * rad * rad));
      const inv = 1 / Math.sqrt(d2);
      ux += (-dy * inv) * str * fall;
      uy += (dx * inv) * str * fall;
    }
    return [ux, uy];
  }

  _checkBodyHover(x, y, forceNotify = false) {
    let hit = null;
    for (let i = 0; i < this.bodyScreenPositions.length; i++) {
      const b = this.bodyScreenPositions[i];
      if (Math.hypot(x - b.x, y - b.y) <= Math.max(16, b.r + 10)) {
        hit = b;
        break;
      }
    }
    if (hit !== this.hoveredBody || forceNotify) {
      this.hoveredBody = hit;
      if (this.onBodyInspect && hit) {
        this.onBodyInspect(hit.label);
      }
    }
  }

  _startLoop() {
    let last = performance.now();
    const tick = (now) => {
      const dt = Math.min(0.05, (now - last) / 1000);
      last = now;
      this.renderFrame(dt);
      requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }

  _renderSkySurface(ctx, w, h, stars, strokes, dt, isPanorama) {
    const bgGrad = ctx.createLinearGradient(0, 0, w * 0.3, h);
    bgGrad.addColorStop(0, "#040a18");
    bgGrad.addColorStop(0.5, "#091835");
    bgGrad.addColorStop(1, "#040814");
    ctx.fillStyle = bgGrad;
    ctx.fillRect(0, 0, w, h);

    ctx.save();
    ctx.translate(w * 0.52, h * 0.48);
    ctx.rotate(isPanorama ? -0.22 : -0.48);
    const mwGrad = ctx.createRadialGradient(0, 0, 8, 0, 0, Math.max(w, h) * 0.58);
    mwGrad.addColorStop(0, isPanorama ? "rgba(186, 230, 253, 0.26)" : "rgba(186, 230, 253, 0.18)");
    mwGrad.addColorStop(0.36, "rgba(96, 165, 250, 0.14)");
    mwGrad.addColorStop(0.7, "rgba(30, 64, 138, 0.06)");
    mwGrad.addColorStop(1, "rgba(4, 9, 23, 0)");
    ctx.scale(1.65, isPanorama ? 0.42 : 0.32);
    ctx.fillStyle = mwGrad;
    ctx.beginPath();
    ctx.arc(0, 0, Math.max(w, h) * 0.58, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();

    for (let i = 0; i < stars.length; i++) {
      const st = stars[i];
      const [fx, fy] = this._sampleFluidNorm(st.nx, st.ny);
      const sx = st.nx * w + fx * 1.8;
      const sy = st.ny * h + fy * 1.8;
      const tw = 0.45 + 0.55 * (0.5 + 0.5 * Math.sin(this.time * st.twinkle + st.phase));
      ctx.globalAlpha = tw * 0.88;
      ctx.fillStyle = st.color;
      ctx.beginPath();
      ctx.arc(sx, sy, st.r, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.globalAlpha = 1;

    ctx.lineCap = "round";
    for (let i = 0; i < strokes.length; i++) {
      const p = strokes[i];
      const px = p.nx * w;
      const py = p.ny * h;
      const [cx, cy] = this._curlField(p.nx, p.ny);
      const [fx, fy] = this._sampleFluidNorm(p.nx, p.ny);
      const ux = cx * 1.25 + fx * 0.26;
      const uy = cy * 1.25 + fy * 0.26;
      const mag = Math.hypot(ux, uy) || 1;
      const dx = (ux / mag) * p.len;
      const dy = (uy / mag) * p.len;

      ctx.strokeStyle = p.color;
      ctx.globalAlpha = p.alpha;
      ctx.lineWidth = p.width;
      ctx.beginPath();
      ctx.moveTo(px - dx * 0.5, py - dy * 0.5);
      ctx.quadraticCurveTo(px - dy * 0.22, py + dx * 0.22, px + dx * 0.5, py + dy * 0.5);
      ctx.stroke();

      if (!this.reducedMotion && dt > 0) {
        p.nx += ux * (isPanorama ? 0.00065 : 0.00032) * p.speed;
        p.ny += uy * (isPanorama ? 0.00095 : 0.00032) * p.speed;
        if (p.nx > 1.03) p.nx = -0.03;
        if (p.nx < -0.03) p.nx = 1.03;
        if (p.ny > 1.03) p.ny = -0.03;
        if (p.ny < -0.03) p.ny = 1.03;
      }
    }
    ctx.globalAlpha = 1;
  }

  renderFrame(dt) {
    this.time += dt;
    for (let i = 0; i < this.vx.length; i++) {
      this.vx[i] *= 0.94;
      this.vy[i] *= 0.94;
    }

    this._renderSkySurface(this.bgCtx, this.bgW, this.bgH, this.bgStars, this.bgStrokes, dt, false);

    if (!this.panCtx) return;
    const ctx = this.panCtx;
    const w = this.panW;
    const h = this.panH;

    this._renderSkySurface(ctx, w, h, this.panStars, this.panStrokes, dt, true);
    this.bodyScreenPositions = [];

    for (let i = 0; i < this.panAureoles.length; i++) {
      const au = this.panAureoles[i];
      const [fx, fy] = this._sampleFluidNorm(au.nx, au.ny);
      const sx = au.nx * w + fx * 1.6;
      const sy = au.ny * h + fy * 1.6;
      const glow = ctx.createRadialGradient(sx, sy, 1, sx, sy, au.r * 2.1);
      glow.addColorStop(0, au.warm ? "rgba(254, 240, 138, 0.78)" : "rgba(186, 230, 253, 0.72)");
      glow.addColorStop(0.45, au.warm ? "rgba(251, 191, 36, 0.22)" : "rgba(96, 165, 250, 0.20)");
      glow.addColorStop(1, "rgba(4, 9, 23, 0)");
      ctx.fillStyle = glow;
      ctx.beginPath();
      ctx.arc(sx, sy, au.r * 2.1, 0, Math.PI * 2);
      ctx.fill();

      ctx.save();
      ctx.translate(sx, sy);
      ctx.rotate(this.time * (i % 2 === 0 ? 0.22 : -0.18));
      ctx.strokeStyle = au.warm ? "rgba(253, 224, 71, 0.62)" : "rgba(125, 211, 252, 0.56)";
      ctx.lineWidth = 1.15;
      ctx.setLineDash([4, 3]);
      ctx.beginPath();
      ctx.arc(0, 0, au.r * 0.86, 0, Math.PI * 2);
      ctx.stroke();
      ctx.restore();

      ctx.fillStyle = "#ffffff";
      ctx.beginPath();
      ctx.arc(sx, sy, 1.9, 0, Math.PI * 2);
      ctx.fill();
    }

    const moonX = w - Math.min(74, w * 0.09);
    const moonY = h * 0.56;
    const moonR = Math.min(20, Math.max(14, w * 0.019));
    const mHalo = ctx.createRadialGradient(moonX, moonY, moonR * 0.35, moonX, moonY, moonR * 3.1);
    mHalo.addColorStop(0, "rgba(253, 224, 71, 0.56)");
    mHalo.addColorStop(0.42, "rgba(251, 191, 36, 0.22)");
    mHalo.addColorStop(1, "rgba(4, 9, 23, 0)");
    ctx.fillStyle = mHalo;
    ctx.beginPath();
    ctx.arc(moonX, moonY, moonR * 3.1, 0, Math.PI * 2);
    ctx.fill();

    ctx.save();
    ctx.translate(moonX, moonY);
    for (const rk of [1.35, 1.78, 2.2]) {
      ctx.save();
      ctx.rotate(this.time * (rk > 1.7 ? -0.14 : 0.18));
      ctx.strokeStyle = rk < 1.8 ? "rgba(253, 224, 71, 0.64)" : "rgba(125, 211, 252, 0.38)";
      ctx.lineWidth = 1.25;
      ctx.setLineDash([5, 3.5]);
      ctx.beginPath();
      ctx.arc(0, 0, moonR * rk, 0, Math.PI * 2);
      ctx.stroke();
      ctx.restore();
    }
    ctx.rotate(-0.42);
    ctx.fillStyle = "#fb923c";
    ctx.beginPath();
    ctx.arc(0, 0, moonR, -Math.PI * 0.5, Math.PI * 0.5, false);
    ctx.arc(-moonR * 0.36, 0, moonR * 0.84, Math.PI * 0.5, -Math.PI * 0.5, true);
    ctx.closePath();
    ctx.fill();
    ctx.restore();

    this.bodyScreenPositions.push({
      x: moonX,
      y: moonY,
      r: moonR * 1.4,
      label: "Saint-Remy Waning Crescent Moon · Impasto Corona Vortex"
    });

    const sunX = w * 0.38;
    const sunY = h * 0.56;
    const maxRx = Math.min(260, w * 0.28);
    const maxRy = Math.min(54, h * 0.32);
    const tilt = -0.14;

    const sunGlow = ctx.createRadialGradient(sunX, sunY, 1.5, sunX, sunY, 26);
    sunGlow.addColorStop(0, "rgba(255, 255, 255, 0.98)");
    sunGlow.addColorStop(0.28, "rgba(253, 224, 71, 0.82)");
    sunGlow.addColorStop(0.66, "rgba(245, 158, 11, 0.25)");
    sunGlow.addColorStop(1, "rgba(4, 9, 23, 0)");
    ctx.fillStyle = sunGlow;
    ctx.beginPath();
    ctx.arc(sunX, sunY, 26, 0, Math.PI * 2);
    ctx.fill();
    this.bodyScreenPositions.push({
      x: sunX,
      y: sunY,
      r: 12,
      label: "Heliocentric Sun · G2V Star · 8-Planet Keplerian Solar System"
    });

    const cosT = Math.cos(tilt);
    const sinT = Math.sin(tilt);
    for (let i = 0; i < PLANETS.length; i++) {
      const pl = PLANETS[i];
      const rx = maxRx * pl.rf;
      const ry = maxRy * pl.rf;
      const isHov = this.hoveredBody && this.hoveredBody.name === pl.name;

      ctx.save();
      ctx.translate(sunX, sunY);
      ctx.rotate(tilt);
      ctx.strokeStyle = isHov ? "rgba(253, 224, 71, 0.78)" : "rgba(147, 197, 253, 0.26)";
      ctx.lineWidth = isHov ? 1.35 : 0.85;
      ctx.beginPath();
      ctx.ellipse(0, 0, rx, ry, 0, 0, Math.PI * 2);
      ctx.stroke();
      ctx.restore();

      const ang = pl.phase + this.time * 0.34 * pl.speed * this.orbitSpeed;
      const lx = Math.cos(ang) * rx;
      const ly = Math.sin(ang) * ry;
      const px = sunX + lx * cosT - ly * sinT;
      const py = sunY + lx * sinT + ly * cosT;

      if (pl.ring) {
        ctx.save();
        ctx.translate(px, py);
        ctx.rotate(-0.32);
        ctx.strokeStyle = "rgba(253, 230, 138, 0.90)";
        ctx.lineWidth = 1.35;
        ctx.beginPath();
        ctx.ellipse(0, 0, pl.r * 2.25, pl.r * 0.82, 0, 0, Math.PI * 2);
        ctx.stroke();
        ctx.restore();
      }

      ctx.fillStyle = pl.color;
      ctx.beginPath();
      ctx.arc(px, py, pl.r, 0, Math.PI * 2);
      ctx.fill();

      if (pl.moon) {
        const mAng = this.time * 2.4 * this.orbitSpeed;
        ctx.fillStyle = "#f8fafc";
        ctx.beginPath();
        ctx.arc(px + Math.cos(mAng) * (pl.r + 3.2), py + Math.sin(mAng) * (pl.r + 3.2), 1.15, 0, Math.PI * 2);
        ctx.fill();
      }

      this.bodyScreenPositions.push({
        name: pl.name,
        x: px,
        y: py,
        r: pl.r,
        label: `${pl.name} · ${pl.au} · Orbit ${pl.period} — ${pl.note}`
      });
    }

    for (let i = this.ripples.length - 1; i >= 0; i--) {
      const rp = this.ripples[i];
      rp.r += 3.2;
      rp.alpha *= 0.958;
      ctx.strokeStyle = `rgba(125, 211, 252, ${rp.alpha.toFixed(3)})`;
      ctx.lineWidth = 1.4;
      ctx.beginPath();
      ctx.arc(rp.nx * w, rp.ny * h, rp.r, 0, Math.PI * 2);
      ctx.stroke();
      if (rp.alpha < 0.03 || rp.r > rp.maxR) {
        this.ripples.splice(i, 1);
      }
    }

    for (let i = this.meteors.length - 1; i >= 0; i--) {
      const m = this.meteors[i];
      m.nx += m.vx;
      m.ny += m.vy;
      m.life -= 0.028;
      if (m.life <= 0) {
        this.meteors.splice(i, 1);
        continue;
      }
      const mx = m.nx * w;
      const my = m.ny * h;
      const tail = ctx.createLinearGradient(mx, my, mx - m.vx * w * 0.09, my - m.vy * h * 0.25);
      tail.addColorStop(0, `rgba(255, 255, 255, ${m.life.toFixed(2)})`);
      tail.addColorStop(1, "rgba(125, 211, 252, 0)");
      ctx.strokeStyle = tail;
      ctx.lineWidth = 2.0;
      ctx.beginPath();
      ctx.moveTo(mx, my);
      ctx.lineTo(mx - m.vx * w * 0.09, my - m.vy * h * 0.25);
      ctx.stroke();
    }
  }
}
