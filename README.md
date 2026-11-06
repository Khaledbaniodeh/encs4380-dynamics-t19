# ENCS4380 Dynamic Characteristics Interactive Toolkit — Team T19

ENCS4380 Interfacing Techniques, Birzeit University. Instructor: Dr. Wasel Ghanem.

**[Open the live toolkit](https://khaledbaniodeh.github.io/encs4380-dynamics-t19/)**

A static browser toolkit for understanding sensor dynamics through live controls, response plots, and parameter-estimation challenges.

## Current status

Module 1's first-order time-response features are implemented and published on GitHub Pages: Step and Ramp, K and τ sliders, response markers, ramp tracking metrics, logarithmic error plot, validation table, a Predict, then check exercise, and the optional Forward Euler comparison.

Module 1 has been checked in a desktop browser and at 320 px and 390 px browser viewports; testing on a physical phone is still pending. Module 2 is implemented, linked from the home page, and includes the live sine/Bode plots, dynamic-error design calculator, prediction exercise and on-page checks 2–3. The Module 2 formula benchmarks and JavaScript syntax have been reviewed, and phone-friendly layout and navigation rules are in place. A team member (Jibreel Haddar) confirmed that Module 2 interactions work on a physical phone and supplied desktop and phone screenshots of the page header. This is team-reported testing, not an independently reproduced cross-device test. Modules 3 and 4 remain planned. Instructor collaborator access, ownership of Modules 3–4, and any unconfirmed team administration details still need confirmation.

## Module 1: using the time-response experiment

1. Open the live link to see the toolkit introduction and learning path. Choose **Start with Module 1** or **Open module**. Module 1 has its own page at [module-1.html](https://khaledbaniodeh.github.io/encs4380-dynamics-t19/module-1.html). Wait for Python to load inside the module. Internet access is required for its CDN libraries.
2. Choose **Step** or **Ramp** using the input buttons in the Parameters panel.
3. Move the **K** and **τ** sliders, or type values in their number fields. Typed valid values can extend the initial slider ranges.
4. Set the Step amplitude A or Ramp slope r, then choose a time t to read the output at that instant.
5. Read the response plot and the mode-specific results. The plot covers 0 to 5τ; the selected-time output can also be evaluated outside that window.
6. Use **Reset example** to restore the default values. On narrow screens, **Edit parameters** and **View response** provide quick navigation; the Parameters panel can be collapsed.
7. In **Euler comparison**, change Δt to compare the numerical orange curve with the exact blue curve. Use its checkbox to hide the approximation; **How does this work?** explains the update and stability.
8. For **Predict, then check**, choose a nonzero Step, save a prediction, increase τ without changing K or A, then press **Check**. **New prediction** starts another attempt.

K, A and r may be positive, negative or zero. τ must be finite and strictly positive; t must be finite and nonnegative. Nonfinite inputs and results outside the supported numeric range produce an error message. For KA = 0, the normalized Step percentages, log-error plot and prediction exercise are not applicable.

### Module 1: try it on your phone

Open the live link in Chrome or Safari, or press **Open on phone** in the page header and scan its QR code with your phone camera. The dialog also includes the website link and a copy button; if clipboard access is unavailable, copy the visible link manually.

Wait for **Python ready**, then test both input modes, the sliders and number fields, the prediction exercise and horizontal scrolling in the validation table. Browser viewport checks do not replace testing on a real phone.

## Module 1 model and outputs

The model is a linear first-order sensor:

```text
τ dy/dt + y = Kx,     y(0) = 0
```

| Input | Closed-form output |
| --- | --- |
| Step from zero to A | y(t) = KA(1 − exp(−t/τ)) |
| Ramp x(t) = rt | y(t) = Kr[t − τ(1 − exp(−t/τ))] |

This is the zero-initial-condition model. It applies to sensors that can reasonably be represented as first-order linear systems; it is not a model of every sensor.

The page shows:

- Step markers at τ (63.2% of the final change) and 3τ (approximately 95%).
- Step error fraction E(t) = (KA − y(t))/KA = exp(−t/τ), on a logarithmic vertical axis.
- The explanation ln(E) = −t/τ and its slope −1/τ. The remaining-error section offers a base-10 logarithmic axis for E(t), plus a **Natural log · understand the slope** view (selected by default) that plots Python-computed ln(E) on linear axes, so the visible slope is exactly −1/τ. Beginner explanations distinguish sensor response error from numerical calculation error.
- Ramp input x(t), sensor output y(t), and ideal instantaneous output Kx(t). When K = 1, input and ideal output share one trace.
- Ramp current signed tracking error Kx(t) − y(t), steady-state signed error Krτ, and asymptotic time lag τ relative to Kx(t). This lag describes long-time tracking, not a pure delay. If the ideal output is constant (K = 0 or r = 0), that lag is not applicable.

τ and t use seconds. A uses input units, r uses input units per second, and K maps input units to output units.

### Validation check 1

Expected values are rounded lecture benchmarks. The page compares normalized fractions with tolerance 0.0005, equivalent to 0.05 percentage points, and displays expected output, computed output, percentages and Pass/Fail.

With K = 1, A = 10 and τ = 2 s:

| Time | Expected y | Computed y | Computed percentage | Result |
| --- | --- | --- | --- | --- |
| τ = 2 s | 6.3200 | 6.3212 | 63.2121% | Pass |
| 3τ = 6 s | 9.5000 | 9.5021 | 95.0213% | Pass |

For the default Ramp (K = 1, r = 2, τ = 2 s), y(2) = 1.4715, current tracking error = 2.5285, steady-state error = 4, and asymptotic lag = 2 s.

Checks performed during development include signed and zero K/A/r values, invalid time constants, slider/number synchronization, mode switching, and correct/incorrect predictions. These are development checks, not a claim of complete cross-device testing.

### Screenshot

Module 1 experiment dashboard with its parameter panel, live summary and response plot:

![Module 1 controls and validation](docs/screenshots/module1-interface.png)

## Module 2: first-order frequency response

**[Open Module 2](https://khaledbaniodeh.github.io/encs4380-dynamics-t19/module-2.html)**

### How to use Module 2

1. From the home page, choose **Open Module 2**, or use **Home / Module 1 / Module 2** in the header of the module page. **← All modules** also returns to the home page.
2. Wait for **Python ready**, then change the time constant **τ** (seconds) and angular frequency **ω** (rad/s) using the linked sliders or number fields. **Reset example** restores τ = 0.2 s and ω = 2 rad/s.
3. Compare the blue input sine with the green steady-state output. Read amplitude ratio **M**, phase lag **φ**, signed amplitude-based dynamic error **δ**, and cutoff angular frequency **ωc** in the metric cards.
4. Scroll to the two **Bode plots**. Their logarithmic frequency axes show magnitude in dB and phase in degrees. The orange cutoff marker is at ωc = 1/τ, and the point at your selected ω is highlighted.
5. In the **Dynamic-error calculator**, enter the *highest required frequency in Hz* and *maximum allowed amplitude error in percent*. Read the calculated maximum allowed τ, phase at half that frequency using τmax, and whether your currently selected sensor τ meets the limit.
6. For **Predict, then check**, first choose and save a prediction for M. Increase **ω** while keeping **τ** fixed, then press **Check**. Use **New prediction** to try again. The expandable explanation provides a worked example.
7. Review **Validation checks 2 and 3**: expected, computed, tolerance and Pass/Fail are shown for fixed lecture cases. They do not change with your sliders.

### Module 2 phone / browser verification checklist

- [x] Team member Jibreel Haddar opened Module 2 on a physical phone and confirmed its features work (team report, 5 November 2026).
- [x] **Python ready** appears on the phone and desktop screenshots. The team reports that the remaining interactions work; individual slider and plot states were not separately captured.
- [x] Team confirmed Module 2 works on the phone, including its interactive controls; dedicated plot/table screenshots are still useful as additional evidence.
- [x] Team reports the dynamic-error calculator works on the phone; a saved pass/fail comparison screenshot is optional additional evidence.
- [x] Team reports the prediction exercise works on the phone.
- [x] Desktop and mobile page-header screenshots uploaded to `docs/screenshots/` and linked below. Screenshots of lower-page charts and validation results can be added later if desired.

The responsive rules and static JavaScript checks are in place. The phone test above is confirmed by the team, rather than independently reproduced by the documentation reviewer.

### Module 2 screenshots

**Desktop view** — the navigation, introduction, parameters and live result cards:

![Module 2 desktop view](docs/screenshots/module2-desktop.png)

**Phone view** — the responsive header, module links, introduction and single-column learning steps:

<img src="docs/screenshots/module2-mobile.png" alt="Module 2 mobile view" width="260">

Screenshots provided by **Jibreel Haddar** on 5 November 2026 after testing Module 2 on his phone. They show the upper part of the interface; chart, calculator and validation interactions were tested by the team but are not pictured here. The screenshots are stored as PNG files, with the phone screenshot displayed at a compact width in this README. Click or open the image file to view it at its stored resolution.

Module 2 reuses the first-order sensor, now with a sinusoidal input. This implementation deliberately uses unit static gain and input amplitude, K = A = 1, to make the frequency-dependent ratio M clear. Its output sine is the **steady-state** part, not the initial switch-on transient.

- **Model:** G(s) = 1/(τs+1), M = 1/sqrt(1+(ωτ)^2), φ = −atan(ωτ). Angular frequency ω is always in rad/s, while the design calculator accepts f in Hz and converts with ω = 2πf.
- **Interactive inputs:** positive τ (seconds) and ω (rad/s), with linked slider and numeric controls. The sine plot shows input x(t) = sin(ωt) and output yss(t) = M sin(ωt+φ) across three cycles.
- **Metrics:** amplitude ratio, phase shift in degrees, signed amplitude-based dynamic error 100(M−1)%, and cutoff ωc = 1/τ. Equivalent sine-peak delay |φ|/ω is provided in seconds.
- **Bode:** logarithmic angular-frequency axes for 20log10(M) and φ (degrees), with highlighted current frequency and the cutoff at −3.01 dB / −45°.
- **Design calculator:** for a chosen maximum input frequency and permitted amplitude error, solve τmax = sqrt(1/(1−e)^2−1)/(2πfmax), where e is the allowed fractional error. Compare current τ with the limit. The displayed phase at half fmax is computed using τmax, not the current τ.
- **Predict, then check:** make a prediction about the amplitude ratio when ω rises and τ stays fixed; save it, change ω, and check the result.
- **Validation:** the page reports fixed course checks 2 and 3 with expected, computed, tolerance, and Pass/Fail. These tests do not depend on current sliders.
- **Architecture:** `module-2.html` loads `python/First-order frequency response.py` using Pyodide, then renders the returned Python-computed samples with Plotly. The URL uses percent-encoded spaces.
- **Limitations/testing:** the waveform is steady state, not the start-up transient; the first-order model assumes τ > 0, the input amplitude and gain are fixed at one, and ω > 0 is required for the logarithmic axis. The calculator's δ is an amplitude-ratio error, not instantaneous input-output difference or phase error. Full browser-interaction and physical-phone testing remain to be performed.

### Module 2 lecture benchmark calculations

| Check | Expected (rounded) | Calculated from formulas |
| --- | ---: | ---: |
| τ = 0.2 s, ω = 2 rad/s: M | 0.93 | 0.9284767 |
| τ = 0.2 s, ω = 2 rad/s: phase lag | 21.8° | 21.8014° |
| fmax = 100 Hz, allowed error = 5%: τmax | 0.52 ms | approximately 0.523 ms |
| Phase at 50 Hz using that τmax | 9.3° | approximately 9.33° |

The provided rounded benchmarks use tolerances of 0.01 for M, 0.2° for phase, and 0.02 ms for τmax. These values are independently calculated in the module; the page reports a Pass/Fail result for each.

## Module 3: second-order response

**[Open Module 3](https://khaledbaniodeh.github.io/encs4380-dynamics-t19/module-3.html)**

Module 3 uses the standard second-order model

```text
G(s) = ωn² / (s² + 2ζωn s + ωn²)
```

with live controls for damping ratio ζ and natural frequency ωn. The page classifies the response as underdamped, critically damped or overdamped and reports rise time, peak time, overshoot and 2% settling time from the simulated curve.

The same page also includes:

- A live s-plane pole plot.
- A mass–spring–damper state-space model with adjustable m, b and k.
- Live A and B matrices, derived ωn and ζ, eigenvalues of A and matching poles.
- A phase-plane plot of displacement x1 versus velocity x2.
- A Predict-then-check exercise for the effect of increasing ζ on overshoot.
- Validation checks for the three Module 3 lecture benchmarks.

The physical model uses

```text
A = [[0, 1], [-k/m, -b/m]]
B = [[0], [1/m]]
y = [1 0]x
```

The step response is simulated in Python with RK4. Rise time uses the 10–90% convention and settling time uses a ±2% band.

### Module 3 validation

| Check | Expected | Calculated | Result |
| --- | --- | --- | --- |
| ζ = 0.5 overshoot | 16.3% | 16.3029% | Pass |
| ζ = 1 overshoot | 0% | 0% | Pass |
| m = 1, b = 2, k = 4 | ωn = 2 rad/s, ζ = 0.5, poles/eigenvalues = −1 ± j1.732 | Matching values | Pass |

Module 3 was tested with underdamped, critically damped and overdamped examples on desktop, and its responsive layout and controls were also checked on a physical phone.

## Files and technology

| File | Responsibility |
| --- | --- |
| `python/first_order.py` | Python exact responses, our scalar Forward Euler solver, error/lag metrics, validation and prediction evaluation |
| `python/First-order frequency response.py` | First-order steady-state frequency response, sine/Bode data, amplitude and phase metrics, cutoff, design calculator and validation checks 2–3 |
| `module-2.html` | Interactive frequency-response page using the Python model through Pyodide and Plotly |
| `python/second_order.py` | Second-order RK4 simulation, curve-based metrics, poles, state-space calculations, eigenvalues, phase-plane data and Module 3 validation |
| `module-3.html` | Interactive second-order response page with damping controls, poles, state space, phase plane, prediction and validation |
| `index.html` | Lightweight home page: introduction, learning path, module navigation and beginner help |
| `module-1.html` | First-order experiment, guided explanations, responsive controls, Pyodide bridge and Plotly rendering |
| `README.md` | Live link, model assumptions, usage, validation and project status |

Python executes in the visitor's browser through **Pyodide v314.0.7**. **Plotly.js 4.1.1** renders the curves. The CDN versions are pinned in the interactive module pages; the home page loads no Python or plotting runtime. Each module loads its own Python source through Pyodide and passes calculated values to Plotly. Internet access is needed to load CDN libraries.

GitHub Pages publishes the repository root from `main`. The deployed site needs no backend server, Binder or login. Numerical models remain in Python; Flask and Django are not used.

Required plots use the lecture's closed-form formulas. An optional **Forward Euler comparison** is implemented in Module 1. The default comparison is enabled with Δt = 0.5 s. It can be switched off without changing the exact response.

The solver uses our own Python loop:

```text
y[n+1] = y[n] + h * f(t[n], y[n])
f(t,y) = (K*x(t) - y)/τ
```

Step uses x(t) = A; Ramp uses x(t) = rt evaluated at the beginning of each step. Both start at y(0) = 0. The requested step is Δt, with a shorter last step if necessary to finish at 5τ. The solver does not evaluate the exponential formula to advance the numerical solution; the exact formula is evaluated separately for comparison.

Orange dashed lines and nodes overlay the exact blue response. Hovering an Euler node shows its approximate value, exact reference and absolute error. The comparison reports the maximum absolute error **at Euler nodes**, the final error at 5τ, and the number of steps. Errors use output units, so signed and zero inputs are supported without undefined percentage errors.

For the default Step (K = 1, A = 10, τ = 2 s), Δt = 0.5 s gives 20 steps, maximum node error approximately 0.51473 and final error approximately 0.035667. At Δt = 0.1 s, the maximum node error drops to approximately 0.093935.

The page explains the homogeneous Euler stability condition: every applied step must be less than 2τ. A coarse or unstable step gets an explicit message; stability does not guarantee accuracy. Invalid or overly small Δt values affect only the optional comparison. A 2,000-step limit keeps the browser responsive.

Development checks cover hand-calculated Step/Ramp updates, convergence when Δt is reduced, negative and zero signals, a final partial step, the stability boundary and unstable case, and invalid/excessive runs. RK4 has not been implemented.

Run the numerical regression checks from the repository root with standard Python:

```sh
python -m unittest discover -s tests -v
```

## Modules and ownership

| Module | Scope | Tracking issue | Implementation | Owner |
| --- | --- | --- | --- | --- |
| 1 | First-order time response | [#1](../../issues/1) | Implemented; phone check pending | Khaled Bani Oudeh ([@Khaledbaniodeh](https://github.com/Khaledbaniodeh)) |
| 2 | Frequency response, sines, Bode plots and dynamic error | [#2](../../issues/2) | Implemented; phone functionality confirmed by team | Jibreel Haddar |
| 3 | Second-order response, poles, state space and phase plane | [#3](../../issues/3) | Implemented and tested on desktop and phone | To be assigned by the team |
| 4 | Guess the sensor: hidden parameters, noise, hints and scoring | [#4](../../issues/4) | Not started | To be assigned by the team |

Module 1 ownership is confirmed for Khaled Bani Oudeh (@Khaledbaniodeh). Module 2 is recorded under Jibreel Haddar, who confirmed the phone test and provided screenshots. Owners of Modules 3–4 and any additional contributor information remain to be recorded. Every member must contribute from their own account and be able to explain their code and equations.

## Delivery checklist

- [x] Create the public repository using the required naming pattern.
- [x] Create one GitHub Issue per module.
- [x] Publish Module 1 on GitHub Pages and verify the live link in a desktop browser.
- [x] Implement K/τ sliders, Step/Ramp plots, markers, ramp metrics and log-error plot.
- [x] Add a Step prediction exercise and on-page validation check 1.
- [x] Document Module 1, its live link and an interface screenshot.
- [ ] Confirm all team members and the instructor have collaborator access.
- [ ] Confirm owners for Modules 3 and 4; Modules 1 and 2 have named owners.
- [ ] Verify on a physical phone: Step/Ramp switching, both sliders, number fields, prediction buttons, table scrolling and both plots.
- [x] Implement Module 2: sine input/output, magnitude/phase Bode plots, cutoff marker, dynamic-error calculator, prediction, and lecture checks 2–3.
- [x] Module 2 physical-phone functionality confirmed by Jibreel Haddar; desktop and mobile screenshots supplied for README documentation.
- [x] Implement Module 3: second-order response, poles, state space, phase plane, prediction, and validation checks 4–6.
- [ ] Complete Module 4.
- [ ] Add screenshots for Modules 3–4, optionally add Module 2 charts/results screenshots, and complete contributor records.
- [ ] Create the final release tagged `v1.0` and submit the Pages link on the course page.

Instructor invitation: repository Settings → Collaborators → Add people → `ghanem@staff.birzeit.edu`.

## Schedule

| Date (2026) | Deliverable |
| --- | --- |
| 3 November | Checkpoint 1: GitHub Pages live and Module 1 working |
| 9 November | Checkpoint 2: Modules 2 and 3 working |
| 12 November | All four modules; release tagged `v1.0`; submit the Pages link |
| 15–16 November | Group demos: 10 minutes plus questions |

Each checkpoint is a five-minute check in the lab. The brief specifies a five-point deduction for each missed checkpoint.

## Validation checks 2–6

| Module | Expected result from the brief | Status |
| --- | --- | --- |
| 2 | τ = 0.2 s, input sin(2t): amplitude ratio approximately 0.93; phase lag 21.8° | Implemented in validation table |
| 2 | Up to 100 Hz, at most 5% dynamic error: τmax approximately 0.52 ms; phase lag approximately 9.3° at 50 Hz | Implemented in validation table |
| 3 | ζ = 0.5: overshoot approximately 16.3% | Implemented; calculated 16.3029%, Pass |
| 3 | ζ = 1: no overshoot | Implemented; calculated 0%, Pass |
| 3 | m = 1, b = 2, k = 4: eigenvalues/poles −1 ± j1.732; ζ = 0.5; ωn = 2 rad/s | Implemented; values match, Pass |

Module 3 checks are calculated by the page and shown with expected, calculated and Pass/Fail results. Each implemented module includes its own Predict, then check interaction.

## Course references

- ENCS4380 Homework 1: Dynamic Characteristics Interactive Toolkit, released 29 October 2026.
- Static and Dynamic Characteristics lecture slides.
- State-Space Modeling notes, 2026 edition: Example 3, Sections 6 and 7.1; Section 8 for the optional Micromouse simulation bonus. Obtain and confirm this exact reference before reusing its code.

## Checkpoint and versioning

| Milestone | Date | Current status |
| --- | --- | --- |
| Checkpoint 1 — Module 1 | 3 November 2026 | A reference snapshot was saved in the `checkpoint/module-1` branch at [`20847b4`](https://github.com/Khaledbaniodeh/encs4380-dynamics-t19/commit/20847b440a8155a036944168de1af0f5aacff641). This preserves the code; it does **not** by itself confirm instructor acceptance. |
| Module 2 — First-order frequency response | 5 November 2026 | Implemented on `main` with Python calculations, interactive plots, validation checks 2–3, documentation and PNG desktop/mobile screenshots. Jibreel Haddar reported successful testing on a physical phone. |
| Checkpoint 2 — Modules 2 **and** 3 | 9 November 2026 | **Ready for presentation.** Modules 2 and 3 are implemented; Module 3 has been tested on desktop and phone and all three required validation checks pass. |
| Final submission — All four modules | 12 November 2026 | **Pending.** Create the `v1.0` release only after Modules 1–4 and the final submission checks are ready. |

**Branches and releases:** `main` contains the ongoing work, while [`checkpoint/module-1`](https://github.com/Khaledbaniodeh/encs4380-dynamics-t19/tree/checkpoint/module-1) preserves the Module 1 baseline. As checked on 5 November, the `checkpoint-1` tag/release and `v1.0` release have not been created. There is no separate Module 2 or Checkpoint 2 snapshot yet.

**Protecting earlier work:** Module 1's Python model and Euler tests still match the stored checkpoint hashes, but `module-1.html` has three explanation/default-view edits compared with the saved branch. The checkpoint copy is unchanged. The previously documented **Module 1 checkpoint guard** is **not currently installed** under `.github/workflows/` on `main`, so no active automated guard should be assumed. Keep future modules in separate pages and Python files; review any Module 1 change against the saved snapshot.

See [`docs/versioning.md`](docs/versioning.md) for the saved commit, Git blob hashes, differences from the snapshot, and release/guard status.

## AI Assistance

ChatGPT was used to explain the homework requirements and equations, help debug and review Module 1's Python/HTML/JavaScript integration and optional Forward Euler comparison, and support documentation. For Module 2, ChatGPT generated the initial Python calculation file and interactive HTML/JavaScript page, then made several layout, navigation and explanatory-text revisions. It also helped review mathematical benchmarks, code structure and the README. Team members remain responsible for understanding and independently checking the equations and code, testing the site on real browsers/devices, and explaining their submitted work in the demo.

