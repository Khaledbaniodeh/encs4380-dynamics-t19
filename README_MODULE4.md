# Module 4 — Guess the Sensor (ENCS4380, Team T19)

A complete, static, browser-based **Module 4** for the Dynamic Characteristics Toolkit. The interface matches the team's navy/teal/white visual theme and adapts to mobile screens.

## Quick start (Windows / macOS / Linux)

1. Unzip all files, keeping `module-4.html` and `python/guess_sensor.py` in their folders.
2. Open a terminal in this folder and run `python -m http.server 8000` (or `py -m http.server 8000` on Windows).
3. Open `http://localhost:8000/module-4.html` in Chrome or Edge.
4. Keep the terminal open. Internet is required **only** to download the Pyodide and Plotly browser libraries; there is **no Python web server needed once deployed on GitHub Pages**.
5. Do **not** open the HTML file via `file://`; browsers may block loading the local Python code.

## How to play

1. **New Sensor** chooses random hidden parameters and a first-order step, first-order **steady-state sine**, or second-order step challenge.
2. The plot shows noisy sensor output. Sine challenges also show the **unit-amplitude input sine** and the known angular frequency in **rad/s**. The true parameters and noiseless output remain hidden until submission.
3. **Get Hint** offers the 63.2% step method, the sine amplitude/phase method, or the second-order overshoot/peak-time method. **Hide Hint** closes the help panel.
4. Enter estimates, then click **Submit Guess** (the **Predict, then check** step). Your model is compared with the true curve and noisy output.
5. The result section shows true and guessed parameters, per-parameter errors and score out of 100. It appears **only after submitting**.
6. **New Sensor** resets only the current challenge. Total Points, Average Score and Rounds persist until the page is reloaded. Multiple submits cannot count the same round twice.

## Equations used

All challenges use an input amplitude of **1**.

**First-order unit-step (zero initial state)**

`y(t) = K * (1 - exp(-t/tau))`

At `t = tau`, `y = 0.63212 K`. At `t = 3 tau`, `y = 0.95021 K`.

**First-order steady-state sine**

Input: `x(t) = sin(omega*t)`.

`M = 1/sqrt(1+(omega*tau)^2)`, `phi = -atan(omega*tau)`.

Output: `y(t) = K*M*sin(omega*t + phi)`.

The student can estimate `tau = tan(abs(phi))/omega` from phase lag; `K = (B/A)*sqrt(1+(omega*tau)^2)` from output/input amplitudes (`A=1`). The initial transient is **not** plotted: this is deliberately the steady-state sine taught in Module 2. Four input cycles are shown so phase and amplitude can be estimated.

**Second-order underdamped unit-step**

`omega_d = omega_n*sqrt(1-zeta^2)`.

`y(t) = 1 - exp(-zeta*omega_n*t)*(cos(omega_d*t) + zeta/sqrt(1-zeta^2)*sin(omega_d*t))`

For `0 < zeta < 1`, overshoot `Mp = exp(-pi*zeta/sqrt(1-zeta^2))` and peak time `Tp = pi/(omega_n*sqrt(1-zeta^2))`. Recover `zeta = -ln(Mp)/sqrt(pi^2+ln(Mp)^2)` and `omega_n = pi/(Tp*sqrt(1-zeta^2))`.

## Scoring policy (explicit implementation choice)

The handout gives **full credit within 10%** but does not prescribe partial credit. Our scoring rule awards equal weight to each of the two hidden parameters:

`error_percent = abs(guess - actual) / actual * 100`

- At `error <= 10%`: parameter score = 100.
- From `10% < error < 100%`: parameter score = `100*(100-error_percent)/90`.
- At `error >= 100%`: parameter score = 0.
- Round score = arithmetic mean of the two parameter scores. Each round is out of 100.
- Session total = sum of round scores. Session average = total / completed rounds.

The random generator deliberately uses strictly positive true parameters (`K`, `tau`, `zeta`, `omega_n`), avoiding division by zero. To ensure second-order parameters are estimable using the lecture's overshoot method, random second-order cases are underdamped only.

## Technical architecture

- **HTML/CSS**: responsive layout and matching site theme.
- **JavaScript**: input validation, plots, hint visibility, round and session state, presentation.
- **Python in Pyodide** (`python/guess_sensor.py`): random sensor generation, mathematical closed-form curves, simulated Gaussian measurement noise, parameter scoring, reveal computation.
- **Plotly.js**: public response, then true/predicted overlay after submit.
- **No backend or login**. The user must have an internet connection for the external library CDNs.

## Verification

Run `python -m unittest discover -s tests -v`. Tests cover the 63.2% rule, second-order overshoot, sine amplitude/phase formulas, all three generator modes, estimable time windows, perfect-guess overlays, score thresholds, and invalid inputs.

Browser checklist: desktop + 375 px mobile; no horizontal overflow; random new sensor; first-order step, sine, and second-order step; show/hide hint; invalid guesses; submission overlay; prevent duplicate submissions; reset only the current round; correct session total and average. The ZIP includes a `tools/integrate_module4.py` helper for the existing repository and `docs/module4_demo.md` for presenting the work.

## Local integration with Modules 1–3 (NO GitHub changes)

This ZIP deliberately does not replace your team's completed Modules 1–3. Put the extracted Module 4 package beside a **local copy** of the original repository and run:

```
python tools/integrate_module4.py --repo "C:\\path\\to\\encs4380-dynamics-t19"
```

This first command only **previews changes**. To apply the modifications **locally**, add `--apply`:

```
python tools/integrate_module4.py --repo "C:\\path\\to\\encs4380-dynamics-t19" --apply
```

It copies Module 4 and its tests/docs, adds Module 4 navigation to the existing pages, and activates its card on `index.html`. It makes backups of overwritten files in `.module4-backups/`. **It does not commit, push, publish, or create any release.** Review results, then decide separately whether to upload them.

## Submission notes

Before team submission, fill in the owner's name in the project README, capture fresh desktop/mobile screenshots of the working page, run the full site from the local repo, and create GitHub Issue/commit history and release `v1.0` **manually when approved**. Document any AI assistance in the team's README, and be prepared to explain code and equations in the demo.


## Optional Pole Explorer Bonus

After submitting a guess, **Open Pole Explorer** lets you drag s-plane poles, switch between underdamped conjugate and negative-real pole configurations, and compare second-order closed-form step responses. The experiment does not change the score. For mathematical derivations and test instructions see [README_POLE_EXPLORER.md](README_POLE_EXPLORER.md).
