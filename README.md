# ENCS4380 Dynamic Characteristics Interactive Toolkit — Team T19

ENCS4380 Interfacing Techniques, Birzeit University. Instructor: Dr. Wasel Ghanem.

**[Open the live toolkit](https://khaledbaniodeh.github.io/encs4380-dynamics-t19/)**

A static browser toolkit for understanding sensor dynamics through live controls, response plots, and parameter-estimation challenges.

## Current status

Module 1's first-order time-response features are implemented and published on GitHub Pages: Step and Ramp, K and τ sliders, response markers, ramp tracking metrics, logarithmic error plot, validation table, a Predict, then check exercise, and the optional Forward Euler comparison.

Module 1 has been checked in a desktop browser and at 320 px and 390 px browser viewports; testing on a physical phone is still pending. Module 2 is implemented, linked from the home page, and includes the live sine/Bode plots, dynamic-error design calculator, prediction exercise and on-page checks 2–3. The Module 2 formula benchmarks and JavaScript syntax have been reviewed, and phone-friendly layout and navigation rules are in place. A full browser-interaction check and physical-phone check are still pending; do not treat code inspection as device testing. Modules 3 and 4 remain planned. Team membership, instructor collaborator access and ownership of Modules 2–4 still need confirmation.

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

- [ ] Open the live page on a **physical phone** (e.g., Chrome on Android or Safari on iPhone), and confirm the header links, back link and section links are tappable.
- [ ] Check **Python ready** appears, and both numeric inputs/sliders update the sine and Bode plots without horizontal page overflow.
- [ ] Swipe over the plots to check that vertical page scrolling still works; use the validation table's own horizontal scroll to see every column.
- [ ] Change the dynamic-error calculator inputs and check both a passing and failing design condition.
- [ ] Save a prediction, raise ω without changing τ, check the result, and reset the exercise.
- [ ] Capture a **Module 2 screenshot** after verification and add it under `docs/screenshots/`; then link it here. (Not yet uploaded.)

The responsive rules and static JavaScript checks are in place, but those checks do **not** replace a real mobile browser test.

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

## Files and technology

| File | Responsibility |
| --- | --- |
| `python/first_order.py` | Python exact responses, our scalar Forward Euler solver, error/lag metrics, validation and prediction evaluation |
| `python/First-order frequency response.py` | First-order steady-state frequency response, sine/Bode data, amplitude and phase metrics, cutoff, design calculator and validation checks 2–3 |
| `module-2.html` | Interactive frequency-response page using the Python model through Pyodide and Plotly |
| `index.html` | Lightweight home page: introduction, learning path, module navigation and beginner help |
| `module-1.html` | First-order experiment, guided explanations, responsive controls, Pyodide bridge and Plotly rendering |
| `README.md` | Live link, model assumptions, usage, validation and project status |

Python executes in the visitor's browser through **Pyodide v314.0.7**. **Plotly.js 4.1.1** renders the curves. The CDN versions are pinned in both `module-1.html` and `module-2.html`; the home page loads no Python or plotting runtime. Each module loads its own Python source through Pyodide and passes calculated values to Plotly. Internet access is needed to load CDN libraries.

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
| 2 | Frequency response, sines, Bode plots and dynamic error | [#2](../../issues/2) | Implemented; browser/phone verification pending | To be assigned by the team |
| 3 | Second-order response, poles, state space and phase plane | [#3](../../issues/3) | Not started | To be assigned by the team |
| 4 | Guess the sensor: hidden parameters, noise, hints and scoring | [#4](../../issues/4) | Not started | To be assigned by the team |

Module 1 ownership is confirmed for Khaled Bani Oudeh (@Khaledbaniodeh). The remaining team details and owners for Modules 2–4 will be recorded later. Every member must contribute from their own account and be able to explain their code and equations.

## Delivery checklist

- [x] Create the public repository using the required naming pattern.
- [x] Create one GitHub Issue per module.
- [x] Publish Module 1 on GitHub Pages and verify the live link in a desktop browser.
- [x] Implement K/τ sliders, Step/Ramp plots, markers, ramp metrics and log-error plot.
- [x] Add a Step prediction exercise and on-page validation check 1.
- [x] Document Module 1, its live link and an interface screenshot.
- [ ] Confirm all team members and the instructor have collaborator access.
- [ ] Assign module owners and record who built each module.
- [ ] Verify on a physical phone: Step/Ramp switching, both sliders, number fields, prediction buttons, table scrolling and both plots.
- [x] Implement Module 2: sine input/output, magnitude/phase Bode plots, cutoff marker, dynamic-error calculator, prediction, and lecture checks 2–3.
- [ ] Verify Module 2's full interactions on desktop and physical phone, and add its screenshot to the README.
- [ ] Complete Modules 3–4 and validation checks 4–6.
- [ ] Add the remaining module screenshots and each member's contributions.
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
| 3 | ζ = 0.5: overshoot approximately 16.3% | Not implemented |
| 3 | ζ = 1: no overshoot | Not implemented |
| 3 | m = 1, b = 2, k = 4: eigenvalues/poles −1 ± j1.732; ζ = 0.5; ωn = 2 rad/s | Not implemented |

The brief's reference values will be checked against the lecture formulas when those modules are implemented. Each module needs its own Predict, then check interaction.

## Course references

- ENCS4380 Homework 1: Dynamic Characteristics Interactive Toolkit, released 29 October 2026.
- Static and Dynamic Characteristics lecture slides.
- State-Space Modeling notes, 2026 edition: Example 3, Sections 6 and 7.1; Section 8 for the optional Micromouse simulation bonus. Obtain and confirm this exact reference before reusing its code.

## Checkpoint and versioning

Module 1's reference snapshot is saved at [`checkpoint/module-1`](https://github.com/Khaledbaniodeh/encs4380-dynamics-t19/tree/checkpoint/module-1), pinned to commit `20847b4`. This is a saved branch, not a tag/release. The `checkpoint-1` tag/release is still pending; `v1.0` is reserved for the final four-module submission.

A read-only **Module 1 checkpoint guard** checks that its HTML page, Python model and Euler tests remain unchanged. Later modules should use independent pages and Python files. Any required Module 1 fix must be discussed explicitly and recorded separately. The check detects changes; it does not itself block GitHub Pages deployment.

See [the versioning record](docs/versioning.md) for exact file hashes, limitations and the saved source reference.

## AI Assistance

ChatGPT was used to explain the homework requirements and equations, help debug and review Module 1's Python/HTML/JavaScript integration and optional Forward Euler comparison, and support documentation. For Module 2, ChatGPT generated the initial Python calculation file and interactive HTML/JavaScript page, then made several layout, navigation and explanatory-text revisions. It also helped review mathematical benchmarks, code structure and the README. Team members remain responsible for understanding and independently checking the equations and code, testing the site on real browsers/devices, and explaining their submitted work in the demo.

