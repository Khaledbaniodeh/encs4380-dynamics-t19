# ENCS4380 Dynamic Characteristics Interactive Toolkit — Team T19

ENCS4380 Interfacing Techniques, Birzeit University. Instructor: Dr. Wasel Ghanem.

**[Open the live toolkit](https://khaledbaniodeh.github.io/encs4380-dynamics-t19/)**

A static browser toolkit for understanding sensor dynamics through live controls, response plots, and parameter-estimation challenges.

## Current status

Module 1's first-order time-response features are implemented and published on GitHub Pages: Step and Ramp, K and τ sliders, response markers, ramp tracking metrics, logarithmic error plot, validation table, a Predict, then check exercise, and the optional Forward Euler comparison.

The interface has been checked in a desktop browser and at 320 px and 390 px browser viewports. A physical-phone check is still pending. Modules 2–4 are planned and are not available on the page yet. Team membership, collaborator invitations and module ownership still need confirmation.

## Use the toolkit

1. Open the live link to see the toolkit introduction and learning path. Choose **Start with Module 1** or **Open module**. Module 1 has its own page at [module-1.html](https://khaledbaniodeh.github.io/encs4380-dynamics-t19/module-1.html). Wait for Python to load inside the module. Internet access is required for its CDN libraries.
2. Choose **Step** or **Ramp** using the input buttons in the Parameters panel.
3. Move the **K** and **τ** sliders, or type values in their number fields. Typed valid values can extend the initial slider ranges.
4. Set the Step amplitude A or Ramp slope r, then choose a time t to read the output at that instant.
5. Read the response plot and the mode-specific results. The plot covers 0 to 5τ; the selected-time output can also be evaluated outside that window.
6. Use **Reset example** to restore the default values. On narrow screens, **Edit parameters** and **View response** provide quick navigation; the Parameters panel can be collapsed.
7. In **Euler comparison**, change Δt to compare the numerical orange curve with the exact blue curve. Use its checkbox to hide the approximation; **How does this work?** explains the update and stability.
8. For **Predict, then check**, choose a nonzero Step, save a prediction, increase τ without changing K or A, then press **Check**. **New prediction** starts another attempt.

K, A and r may be positive, negative or zero. τ must be finite and strictly positive; t must be finite and nonnegative. Nonfinite inputs and results outside the supported numeric range produce an error message. For KA = 0, the normalized Step percentages, log-error plot and prediction exercise are not applicable.

### Try it on your phone

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
- The explanation ln(E) = −t/τ and its slope −1/τ. The default remaining-error view uses a base-10 logarithmic axis. A separate **Natural log · understand the slope** view plots Python-computed ln(E) on linear axes, so the visible slope is exactly −1/τ. Beginner explanations distinguish sensor response error from numerical calculation error.
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
| `index.html` | Lightweight home page: introduction, learning path, module navigation and beginner help |
| `module-1.html` | First-order experiment, guided explanations, responsive controls, Pyodide bridge and Plotly rendering |
| `README.md` | Live link, model assumptions, usage, validation and project status |

Python executes in the visitor's browser through **Pyodide v314.0.7**. **Plotly.js 4.1.1** renders the curves. Both CDN URLs are pinned in `module-1.html`; the home page loads no Python or plotting runtime. JavaScript connects controls to Python and passes the returned values to Plotly.

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
| 1 | First-order time response | [#1](../../issues/1) | Implemented; phone check pending | To be assigned by the team |
| 2 | Frequency response, sines, Bode plots and dynamic error | [#2](../../issues/2) | Not started | To be assigned by the team |
| 3 | Second-order response, poles, state space and phase plane | [#3](../../issues/3) | Not started | To be assigned by the team |
| 4 | Guess the sensor: hidden parameters, noise, hints and scoring | [#4](../../issues/4) | Not started | To be assigned by the team |

The four-member roster, GitHub usernames and agreed module owners will be recorded once confirmed. Every member must contribute from their own account and be able to explain their code and equations.

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
- [ ] Complete Modules 2–4 and validation checks 2–6.
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

## Remaining validation checks

| Module | Expected result from the brief | Status |
| --- | --- | --- |
| 2 | τ = 0.2 s, input sin(2t): amplitude ratio approximately 0.93; phase lag 21.8° | Not implemented |
| 2 | Up to 100 Hz, at most 5% dynamic error: τmax approximately 0.52 ms; phase lag approximately 9.3° at 50 Hz | Not implemented |
| 3 | ζ = 0.5: overshoot approximately 16.3% | Not implemented |
| 3 | ζ = 1: no overshoot | Not implemented |
| 3 | m = 1, b = 2, k = 4: eigenvalues/poles −1 ± j1.732; ζ = 0.5; ωn = 2 rad/s | Not implemented |

The brief's reference values will be checked against the lecture formulas when those modules are implemented. Each module needs its own Predict, then check interaction.

## Course references

- ENCS4380 Homework 1: Dynamic Characteristics Interactive Toolkit, released 29 October 2026.
- Static and Dynamic Characteristics lecture slides.
- State-Space Modeling notes, 2026 edition: Example 3, Sections 6 and 7.1; Section 8 for the optional Micromouse simulation bonus. Obtain and confirm this exact reference before reusing its code.

## AI Assistance

ChatGPT was used to provide guidance throughout the assignment by explaining the homework requirements, clarifying mathematical concepts, and suggesting possible approaches to solving problems. It also assisted with identifying and fixing errors in the Python code and the HTML/CSS/JavaScript integration, reviewing the plots and prediction/validation features, and checking the optional Forward Euler implementation. Additionally, it helped improve the repository documentation and provided suggestions for testing and verifying the results.

