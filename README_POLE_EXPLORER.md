# Module 4 — Pole Explorer Bonus

This published version adds the optional *Pole Explorer* to the fully working Module 4 challenge. The Pole Explorer is now part of the GitHub repository.

## Run on Windows

1. Extract the entire ZIP into a new folder (keep `module-4.html`, `js/` and `python/` next to one another).
2. Double-click `START_LOCAL_WINDOWS.bat` (or open CMD in that folder and run `python -m http.server 8000`).
3. Open **http://localhost:8000/module-4.html** in a browser with internet access (Pyodide and Plotly are loaded from CDNs).
4. Click **New Sensor** as desired, enter valid parameters, then click **Submit Guess**.
5. After submission, the independent **Bonus · Pole Explorer** panel appears below **Challenge Result**. Click **Open Pole Explorer**.
6. Drag the teal pole dots directly in the *s-plane*. The chart and values update live. Try it on a phone too.
7. Switch between **Complex conjugate pair** and **Two negative real poles**, or use the sliders for fine control.
8. Click **Reset to start** to restore the initial poles. Click **Close Explorer** to collapse the bonus without losing your score.
9. Click **New Sensor**. The bonus hides until the next submission, and the session total remains unchanged.

**Important:** Do **not** open the HTML with a `file:///` URL. Its Python source is loaded using `fetch`, which requires an HTTP server. Use localhost as above. The links to Modules 1–3 require those files to be present in the same folder; this ZIP intentionally focuses on testing Module 4 without replacing teammates' files.

## What the poles mean

The model is the standard second-order unit-gain system:

`G(s) = wn² / (s² + 2 ζ wn s + wn²)`

Its poles determine the shape of its step response.

- **Conjugate mode:** `p = -a ± j b` where `a > 0` and `b >= 0`. Then `wn = sqrt(a²+b²)` and `ζ = a/wn`. For `b>0`, the poles are underdamped and produce oscillation. When `b=0`, the repeated pole is critically damped.
  - Closed-form unit-step response: `y(t) = 1 - exp(-a t) [cos(b t) + (a/b) sin(b t)]`. At `b=0`, use `y(t)=1-exp(-a t)(1+a t)`.
  - Overshoot: `100 exp(-π a/b)` percent when `b>0`.
- **Two-real-poles mode:** `p1=-a, p2=-b` where `a,b>0`. Then `wn=sqrt(ab)` and `ζ=(a+b)/(2 sqrt(ab))`. If `a != b`, the poles are overdamped; if `a=b`, critically damped.
  - Closed-form unit-step response for `a!=b`: `y(t)=1-[b exp(-a t)-a exp(-b t)]/(b-a)`.
  - For `a=b`, use `y(t)=1-exp(-a t)(1+a t)`.

The **gray dotted curve** is the response at the original starting poles. The **solid teal curve** changes as you drag the poles. The pole positions stay in the **left half-plane**, so the explored systems are stable. Both curves are mathematical simulations with a unit step input, not measured data.

## How the bonus relates to the challenge

The bonus is unlocked **only after Submit Guess**, never while true sensor values are hidden.

- If the completed challenge was **second order**, the explorer starts at the **revealed** sensor's pole locations.
- If the completed challenge was **first order**, the explorer uses an independent example of a second-order system; it is **not** the hidden first-order sensor.
- Moving the bonus poles does **not** change the challenge, guess, revealed result or total score.

## Automated checks

From the project folder:

- `python -m unittest discover -s tests -v` — original Module 4 Python math/scoring and integration tests.
- `node tests/test_pole_explorer.js` — conjugate, critical and real-pole formulas, damping values and reference overshoot.

The new HTML, the external bonus JavaScript, and the original Python math were checked for syntax. A Chromium UI smoke test with simulated Pyodide and Plotly verified unlock/reset, the SVG drag gesture, live state changes, slider controls, lack of score mutations and no horizontal overflow at 320–1280 px. **The CDN-backed browser implementation should still be tried on your own computer and phone**, as requested.

## File locations

- `module-4.html`: existing Module 4 layout and challenge, plus bonus panel markup/styles and unlock hooks.
- `js/pole_explorer.js`: separate, commented math and drag interaction (does not call hidden Python values).
- `python/guess_sensor.py`: **unchanged** existing challenge calculation and scoring.
- `tests/test_pole_explorer.js`: math regression tests for the bonus.