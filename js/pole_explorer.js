/*
 * Bonus — interactive second-order pole explorer.
 *
 * For G(s)=wn^2/(s^2+2*zeta*wn*s+wn^2), the poles are
 *    p1,p2 = -zeta*wn +/- j*wn*sqrt(1-zeta^2)   (0<zeta<1)
 * or two negative real values when zeta>1.
 *
 * The interactive chart is intentionally an INDEPENDENT sandbox, unlocked
 * only after Submit Guess. It never changes the hidden sensor or session score.
 */
(function () {
  "use strict";

  const EPS = 0.15;
  const MAX_RATE = 6;
  const MAX_IM = 5;
  const SVG_NS = "http://www.w3.org/2000/svg";
  const VIEW = { width: 640, height: 320, left: 65, right: 584, top: 25, bottom: 290 };

  const math = {
    // p = -a +/- j*b. Works at b=0 (repeated real pole) too.
    conjugateStep(t, a, b) {
      if (Math.abs(b) < 1e-6) return 1 - Math.exp(-a * t) * (1 + a * t);
      return 1 - Math.exp(-a * t) * (Math.cos(b * t) + a * Math.sin(b * t) / b);
    },
    // p1=-a, p2=-b. Use the repeated-pole limit for a approx b.
    realStep(t, a, b) {
      if (Math.abs(a - b) < 1e-5) return 1 - Math.exp(-a * t) * (1 + a * t);
      return 1 - (b * Math.exp(-a * t) - a * Math.exp(-b * t)) / (b - a);
    },
    parameters(mode, a, b) {
      const naturalFrequency = mode === "complex" ? Math.hypot(a, b) : Math.sqrt(a * b);
      const dampingRatio = mode === "complex" ? a / naturalFrequency : (a + b) / (2 * naturalFrequency);
      const overshoot = mode === "complex" && b > 1e-6 ? 100 * Math.exp(-Math.PI * a / b) : 0;
      const dampingCase = mode === "complex"
        ? (b > 1e-6 ? "Underdamped" : "Critically damped")
        : (Math.abs(a - b) < 1e-5 ? "Critically damped" : "Overdamped");
      return { naturalFrequency, dampingRatio, overshoot, dampingCase };
    },
    response(mode, t, a, b) {
      return mode === "complex" ? this.conjugateStep(t, a, b) : this.realStep(t, a, b);
    }
  };

  let initialized = false;
  let isUnlocked = false;
  let isOpen = false;
  let mode = "complex";
  let states = { complex: { a: 1.2, b: 2.3 }, real: { a: 1.1, b: 3.4 } };
  let baseline = { mode: "complex", a: 1.2, b: 2.3 };
  let activeHandle = null;
  let framePending = false;
  let nodes = {};
  let handles = {};

  function byId(id) { return document.getElementById(id); }
  function clamp(x, min, max) { return Math.max(min, Math.min(max, x)); }
  function rounded(x) { return Math.round(x * 100) / 100; }
  function fmt(x) { return x.toFixed(2); }
  function xPixel(real) { return VIEW.left + (real + MAX_RATE) * (VIEW.right - VIEW.left) / MAX_RATE; }
  function yPixel(imag) { return VIEW.top + (MAX_IM - imag) * (VIEW.bottom - VIEW.top) / (2 * MAX_IM); }
  function toReal(pixel) { return clamp((pixel - VIEW.left) * MAX_RATE / (VIEW.right - VIEW.left) - MAX_RATE, -MAX_RATE, -EPS); }
  function toImag(pixel) { return clamp(MAX_IM - (pixel - VIEW.top) * 2 * MAX_IM / (VIEW.bottom - VIEW.top), -MAX_IM, MAX_IM); }

  function svgNode(name, attrs, text) {
    const el = document.createElementNS(SVG_NS, name);
    for (const [key, value] of Object.entries(attrs || {})) el.setAttribute(key, String(value));
    if (text !== undefined) el.textContent = text;
    return el;
  }

  function setupPlane() {
    const svg = nodes.plane;
    svg.replaceChildren();
    svg.setAttribute("viewBox", `0 0 ${VIEW.width} ${VIEW.height}`);
    const grid = svgNode("g", { "aria-hidden": "true" });
    for (let n = -6; n <= 0; n += 1) {
      const x = xPixel(n);
      grid.append(svgNode("line", { x1: x, x2: x, y1: VIEW.top, y2: VIEW.bottom,
        stroke: n === 0 ? "#718299" : "#e6edf3", "stroke-width": n === 0 ? 1.5 : 1 }));
      grid.append(svgNode("text", { x, y: 309, "text-anchor": "middle", fill: "#67788b", "font-size": 12 }, String(n)));
    }
    for (let n = -4; n <= 4; n += 2) {
      const y = yPixel(n);
      grid.append(svgNode("line", { x1: VIEW.left, x2: VIEW.right, y1: y, y2: y,
        stroke: n === 0 ? "#718299" : "#e6edf3", "stroke-width": n === 0 ? 1.5 : 1 }));
      grid.append(svgNode("text", { x: 49, y: y + 4, "text-anchor": "end", fill: "#67788b", "font-size": 12 }, String(n)));
    }
    grid.append(svgNode("text", { x: 605, y: yPixel(0) - 8, "text-anchor": "middle", fill: "#52647a", "font-size": 12 }, "Re"));
    grid.append(svgNode("text", { x: xPixel(0) - 12, y: 14, "text-anchor": "end", fill: "#52647a", "font-size": 12 }, "Im"));
    svg.append(grid);

    for (const key of ["first", "second"]) {
      const g = svgNode("g", { "data-pole": key, style: "cursor:grab;touch-action:none" });
      const hit = svgNode("circle", { r: 20, fill: "transparent", "pointer-events": "all" });
      const dot = svgNode("circle", { r: 8.5, fill: "#087f72", stroke: "#fff", "stroke-width": 3, "pointer-events": "none" });
      const label = svgNode("text", { y: -19, "text-anchor": "middle", fill: "#087f72", "font-size": 14,
        "font-weight": 700, "pointer-events": "none" }, key === "first" ? "p₁" : "p₂");
      g.append(hit, dot, label);
      svg.append(g);
      handles[key] = g;
    }

    svg.addEventListener("pointerdown", event => {
      if (!isOpen) return;
      const target = event.target.closest("[data-pole]");
      if (!target) return;
      activeHandle = target.getAttribute("data-pole");
      if (svg.setPointerCapture) svg.setPointerCapture(event.pointerId);
      event.preventDefault();
    });
    svg.addEventListener("pointermove", event => {
      if (!activeHandle || !isOpen) return;
      const box = svg.getBoundingClientRect();
      if (!box.width || !box.height) return;
      // The SVG has a fixed aspect ratio, so the viewBox maps directly to its pixels.
      const xp = (event.clientX - box.left) * VIEW.width / box.width;
      const yp = (event.clientY - box.top) * VIEW.height / box.height;
      const p = states[mode];
      const a = -toReal(xp);
      if (mode === "complex") {
        p.a = rounded(a);
        p.b = rounded(Math.abs(toImag(yp)));
      } else {
        p[activeHandle === "first" ? "a" : "b"] = rounded(a);
      }
      updateUI();
      event.preventDefault();
    });
    const endDrag = () => { activeHandle = null; };
    svg.addEventListener("pointerup", endDrag);
    svg.addEventListener("pointercancel", endDrag);
    svg.addEventListener("lostpointercapture", endDrag);
  }

  function updateHandles() {
    const p = states[mode];
    const points = mode === "complex"
      ? [{ x: xPixel(-p.a), y: yPixel(p.b) }, { x: xPixel(-p.a), y: yPixel(-p.b) }]
      : [{ x: xPixel(-p.a), y: yPixel(0) }, { x: xPixel(-p.b), y: yPixel(0) }];
    for (const [index, key] of ["first", "second"].entries()) {
      handles[key].setAttribute("transform", `translate(${points[index].x} ${points[index].y})`);
      handles[key].setAttribute("aria-label", key === "first" ? "Pole 1: drag to move" : "Pole 2: drag to move");
    }
  }

  function updateUI() {
    if (!isUnlocked) return;
    const p = states[mode];
    const m = math.parameters(mode, p.a, p.b);
    nodes.firstLabel.textContent = mode === "complex" ? "Decay rate α = −Re(p)" : "Pole 1 magnitude |p₁|";
    nodes.secondLabel.textContent = mode === "complex" ? "Oscillation frequency β = |Im(p)|" : "Pole 2 magnitude |p₂|";
    nodes.first.value = String(p.a);
    nodes.second.min = mode === "complex" ? "0" : String(EPS);
    nodes.second.max = String(mode === "complex" ? MAX_IM : MAX_RATE);
    nodes.second.value = String(p.b);
    nodes.firstNumber.textContent = fmt(p.a);
    nodes.secondNumber.textContent = fmt(p.b);
    nodes.poles.textContent = mode === "complex"
      ? `p₁ = −${fmt(p.a)} + j${fmt(p.b)}, p₂ = −${fmt(p.a)} − j${fmt(p.b)}`
      : `p₁ = −${fmt(p.a)}, p₂ = −${fmt(p.b)}`;
    nodes.wn.textContent = fmt(m.naturalFrequency) + " rad/s";
    nodes.zeta.textContent = fmt(m.dampingRatio);
    nodes.case.textContent = m.dampingCase;
    nodes.overshoot.textContent = fmt(m.overshoot) + "%";
    updateHandles();
    schedulePlot();
  }

  function drawPlot() {
    framePending = false;
    if (!isUnlocked || !isOpen || typeof Plotly === "undefined") return;
    const p = states[mode];
    const rate = mode === "complex" ? p.a : Math.min(p.a, p.b);
    const baseRate = baseline.mode === "complex" ? baseline.a : Math.min(baseline.a, baseline.b);
    const maxT = clamp(6 / Math.min(rate, baseRate), 3.5, 22);
    const time = Array.from({ length: 360 }, (_, i) => maxT * i / 359);
    const reference = time.map(t => math.response(baseline.mode, t, baseline.a, baseline.b));
    const edited = time.map(t => math.response(mode, t, p.a, p.b));
    Plotly.react(nodes.plot, [
      { x: time, y: reference, type: "scatter", mode: "lines", name: "Initial response",
        line: { color: "#95a7b4", width: 2.5, dash: "dot" } },
      { x: time, y: edited, type: "scatter", mode: "lines", name: "Dragged poles",
        line: { color: "#087f72", width: 3 } },
    ], {
      margin: { l: 45, r: 12, t: 16, b: 75 }, autosize: true,
      xaxis: { title: "Time (s)", gridcolor: "#edf0f4", zeroline: false },
      yaxis: { title: "Step response", gridcolor: "#edf0f4", zeroline: false, automargin: true },
      paper_bgcolor: "#fff", plot_bgcolor: "#fff",
      font: { family: "Segoe UI, sans-serif", color: "#17263b", size: 12 },
      showlegend: true, legend: { orientation: "h", x: 0, y: -0.30, font: { size: 10 } },
    }, { responsive: true, displaylogo: false, displayModeBar: false, scrollZoom: false });
  }

  function schedulePlot() {
    if (framePending || !isOpen) return;
    framePending = true;
    if (typeof requestAnimationFrame === "function") requestAnimationFrame(drawPlot);
    else drawPlot();
  }

  function init() {
    if (initialized) return;
    initialized = true;
    nodes = {
      section: byId("pole-section"), toggle: byId("pole-toggle"), body: byId("pole-body"),
      mode: byId("pole-mode"), plane: byId("pole-plane"), plot: byId("pole-response-plot"),
      first: byId("pole-first"), second: byId("pole-second"),
      firstLabel: byId("pole-first-label"), secondLabel: byId("pole-second-label"),
      firstNumber: byId("pole-first-number"), secondNumber: byId("pole-second-number"),
      poles: byId("pole-values"), wn: byId("pole-wn"), zeta: byId("pole-zeta"),
      case: byId("pole-case"), overshoot: byId("pole-overshoot"),
      context: byId("pole-context"), reset: byId("pole-reset"),
    };
    if (Object.values(nodes).some(element => !element)) throw new Error("Pole Explorer HTML is incomplete.");
    setupPlane();
    nodes.toggle.addEventListener("click", () => {
      if (!isUnlocked) return;
      isOpen = !isOpen;
      nodes.body.hidden = !isOpen;
      nodes.toggle.textContent = isOpen ? "Close Explorer" : "Open Pole Explorer";
      nodes.toggle.setAttribute("aria-expanded", String(isOpen));
      if (isOpen) updateUI();
    });
    nodes.mode.addEventListener("change", () => {
      mode = nodes.mode.value;
      updateUI();
    });
    nodes.first.addEventListener("input", () => {
      states[mode].a = Number(nodes.first.value);
      updateUI();
    });
    nodes.second.addEventListener("input", () => {
      states[mode].b = Number(nodes.second.value);
      updateUI();
    });
    nodes.reset.addEventListener("click", () => {
      if (baseline.mode === "complex") {
        states.complex = { a: baseline.a, b: baseline.b };
      } else {
        states.real = { a: baseline.a, b: baseline.b };
      }
      mode = baseline.mode;
      nodes.mode.value = mode;
      updateUI();
    });
  }

  function unlock(parameters) {
    if (!initialized) init();
    // The calling code passes revealed second-order parameters ONLY after Submit.
    // A completed first-order challenge starts an independent example instead.
    if (parameters && Number.isFinite(parameters.zeta) && Number.isFinite(parameters.omega_n)) {
      const z = parameters.zeta;
      const wn = parameters.omega_n;
      const a = clamp(rounded(z * wn), EPS, MAX_RATE);
      const b = clamp(rounded(wn * Math.sqrt(Math.max(0, 1 - z * z))), 0, MAX_IM);
      states.complex = { a, b };
      nodes.context.textContent = "Starting from the revealed second-order sensor. Move its poles to explore a different response; the original challenge remains unchanged.";
    } else {
      states.complex = { a: 1.2, b: 2.3 };
      nodes.context.textContent = "Independent second-order demonstration. This is not the hidden first-order sensor from your completed round.";
    }
    states.real = { a: 1.1, b: 3.4 };
    mode = "complex";
    nodes.mode.value = mode;
    baseline = { mode, ...states.complex };
    isUnlocked = true;
    isOpen = false;
    nodes.section.hidden = false;
    nodes.body.hidden = true;
    nodes.toggle.textContent = "Open Pole Explorer";
    nodes.toggle.setAttribute("aria-expanded", "false");
    updateUI();
  }

  function reset() {
    if (!initialized) init();
    activeHandle = null;
    isUnlocked = false;
    isOpen = false;
    nodes.body.hidden = true;
    nodes.section.hidden = true;
    nodes.toggle.textContent = "Open Pole Explorer";
    nodes.toggle.setAttribute("aria-expanded", "false");
  }

  function resize() {
    if (isUnlocked && isOpen && typeof Plotly !== "undefined") Plotly.Plots.resize(nodes.plot);
  }

  window.PoleExplorer = { init, unlock, reset, resize, math };
})();

