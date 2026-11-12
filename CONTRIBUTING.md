# Team contribution guide

This guide reflects the live ENCS4380 Dynamic Characteristics Interactive Toolkit as of **12 November 2026**. See [README.md](README.md) for the current module status and [docs/versioning.md](docs/versioning.md) for checkpoint details.

## Team coordination

1. The repository owner should confirm that all four members and the instructor have the required access. The homework specifies inviting the instructor at `ghanem@staff.birzeit.edu`; an invitation is not confirmation that access was accepted.
2. Use issues [#1](../../issues/1)–[#4](../../issues/4) to track requirements, review and ownership. The README records **Khaled Bani Oudeh** for Module 1 and **Jibreel Haddar** for Module 2. Module 3 was implemented by **Waad Melhem**; Module 4 ownership still needs confirmation.
3. Contributions should be made from each member's own GitHub account so individual work is represented accurately. Do not claim another teammate's commits as your own.
4. Keep this public coursework repository separate from the Micromouse firmware repository. Use the course's *Static and Dynamic Characteristics* lectures and the specified 2026 State-Space Modeling notes for equations and Module 3 references.

## How to contribute

1. Pick an issue and agree on the scope with the other team members. For parallel work, create a short branch (for example, `module-3-second-order`) and open a pull request against `main`.
2. Read [AGENTS.md](AGENTS.md) and [docs/versioning.md](docs/versioning.md) before editing an existing module. Keep each new module in separate files; don't change an earlier module just to share a layout or helper.
3. Use descriptive commits, review the changed files before merging, and associate work with the relevant issue. Update README for material changes to functionality, ownership, validation or screenshots.
4. Keep numerical models in **Python**, running in the browser through **Pyodide**. Use HTML/CSS/JavaScript for the interface, controls and Plotly visualizations. Keep pinned CDN versions and do not require a backend, login or server.
5. For required response plots, follow the lecture's closed-form formulas. Document the units, initial conditions, input amplitude and gain assumptions. Show benchmark expected/computed values, their tolerances, and Pass/Fail.
6. Keep the code understandable for the course demo. Accurately disclose AI assistance in README, never commit passwords/tokens, and don't mark an item complete before its behavior has been checked.

## Current repository layout

These paths **already exist** on `main`:

| Path | Purpose |
| --- | --- |
| `index.html` | Published home page and navigation between modules |
| `module-1.html` | First-order **time** response: Step, Ramp, error and optional Euler comparison |
| `python/first_order.py` | Module 1 calculations |
| `tests/test_euler.py` | Python regression tests for the optional numerical solver |
| `module-2.html` | **Module 2 v2**: sine/Bode plots, dynamic error, prediction, validations, and the Superposition of Sine Waves extra-credit section |
| `python/First-order frequency response.py` | Module 2 calculations including the v2 two-sine Superposition model (filename contains spaces) |
| `tests/test_superposition.py` | Seven numerical regression cases for Module 2 v2 Superposition |
| `.github/workflows/python-regression.yml` | Automated regression checks for Euler and Superposition; not a checkpoint guard |
| `module-3.html`, `python/second_order.py` | Implemented Module 3 response and state-space views |
| `docs/screenshots/` | Module screenshots; existing Module 2 PNGs predate the v2 section |
| `docs/versioning.md` | Saved checkpoint, file hashes, release and workflow status |
| `README.md` | Live link, usage, module owners, testing status and documentation |

Styles and browser JavaScript are currently embedded in the module HTML pages. The previous proposed `assets/css/` and `assets/js/` structure is **not** the current layout. Only add shared assets if the team agrees and verifies they don't affect finished modules.

## Verify changes before merging

- Open the GitHub Pages site on a desktop browser and check that controls actually update values and plots. Also test on a physical phone if you change layout, inputs, chart touch handling or navigation.
- Test the module's **Predict, then check** flow, the reset button, error handling and its validation results.
- Check whether any table scrolls correctly and whether labels, navigation and controls work on narrow screens.
- Run the Python regression tests from the repository root:
  ```sh
  python -m unittest discover -s tests -v
  ```
- For Module 2, verify that `omega` is in rad/s in the sine/Bode and Superposition models, but the design calculator's `f` is in Hz (`omega = 2*pi*f`). Both sine experiments show **steady-state**, not the start-up transient.
- For **Module 2 v2**, verify the new navigation link, both frequency sliders and number fields, A₂ = 0, equal frequencies, the Reset button, the shared τ, the combined Plotly graph and the 260px README screenshot layout. Capture a new v2 screenshot after the update is tested on a phone.
- Recheck course benchmarks with independent calculations and document test limitations honestly. Screenshots should show real app output, not be treated as evidence for unpictured controls.
- Update any related issue, README section and screenshots after verification.

**Current validation/testing status (12 November):** Modules 1–3 are implemented; Module 4 remains pending. Jibreel Haddar reported physical-phone testing of the original Module 2 and supplied PNG screenshots; the **new v2 Superposition UI still needs its own phone check**. The Python regression workflow, including the new Superposition tests, passed on 12 November. These checks do not replace real-browser testing.

## Checkpoints and protecting Module 1

- The reference Module 1 source is stored at commit `20847b4` and on branch [`checkpoint/module-1`](https://github.com/Khaledbaniodeh/encs4380-dynamics-t19/tree/checkpoint/module-1). Don't rewrite this saved branch.
- `module-1.html` on current `main` includes a small documented change to Step error explanation/default-view markup relative to the snapshot. The Module 1 Python and Euler test files still match the snapshot.
- The previously described automatic **Module 1 checkpoint guard is not currently installed** on `main`. A separate Python numerical regression workflow was added on 12 November 2026, but it does not compare baseline file hashes. Do not assume GitHub Actions will detect a changed baseline automatically; compare against [docs/versioning.md](docs/versioning.md) when necessary.
- Ask the team before deliberately modifying saved Module 1 files. Record approved changes in a separate descriptive commit; do not change stored baseline hashes to hide differences.
- Do not call a saved branch a release or claim the instructor accepted a checkpoint unless that has been confirmed.

## GitHub Pages and delivery

The static site is already published from `main` at **[Dynamics Lab](https://khaledbaniodeh.github.io/encs4380-dynamics-t19/)**. `.nojekyll` is present. Browser-based Python and Plotly depend on CDN access; there's no backend service.

| Date (2026) | Course milestone | Status as of 5 November |
| --- | --- | --- |
| 3 November | Checkpoint 1: live Module 1 | Saved reference branch; instructor acceptance not confirmed here |
| 9 November | Checkpoint 2: Modules 2 and 3 working | **Pending:** Module 2 implemented; Module 3 not yet ready |
| 12 November | Four modules, final `v1.0` release and Pages link submission | **Pending** |
| 15–16 November | Group demos | Upcoming |

Create the `v1.0` release only after the final four-module work is complete. The `checkpoint-1` tag/release and final `v1.0` release have not been created as of this review.
