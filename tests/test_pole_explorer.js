"use strict";
const assert = require("node:assert/strict");
global.window = {};
require("../js/pole_explorer.js");
const m = window.PoleExplorer.math;

const close = (a, b, tol = 1e-8) => assert.ok(Math.abs(a - b) <= tol, `${a} != ${b}`);

// All models have a zero initial step response and a unit DC gain.
for (const [mode, a, b] of [
  ["complex", 1, 2],
  ["complex", 2, 0],
  ["real", 1, 3],
  ["real", 2, 2],
]) {
  close(m.response(mode, 0, a, b), 0);
  close(m.response(mode, 100, a, b), 1);
}

// Conjugate poles p = -1 +/- j*sqrt(3) correspond to zeta=0.5, wn=2.
const p = m.parameters("complex", 1, Math.sqrt(3));
close(p.dampingRatio, 0.5);
close(p.naturalFrequency, 2);
close(p.overshoot, 16.303353482, 0.00001);
assert.equal(p.dampingCase, "Underdamped");
const peakTime = Math.PI / Math.sqrt(3);
close(m.response("complex", peakTime, 1, Math.sqrt(3)), 1 + p.overshoot / 100, 1e-8);

// Two real poles -1 and -4: wn=2 and zeta=1.25 (overdamped).
const real = m.parameters("real", 1, 4);
close(real.naturalFrequency, 2);
close(real.dampingRatio, 1.25);
close(real.overshoot, 0);
assert.equal(real.dampingCase, "Overdamped");
for (let t = 0; t <= 12; t += 0.2) {
  const y = m.response("real", t, 1, 4);
  assert.ok(y >= -1e-10 && y <= 1 + 1e-10, `overdamped response outside [0,1] at t=${t}: ${y}`);
}

// Both critical representations match the analytical repeated-pole formula.
for (const t of [0, 0.3, 1, 3, 10]) {
  close(m.response("real", t, 2, 2), m.response("complex", t, 2, 0));
}
console.log("Pole Explorer math: all assertions passed.");
