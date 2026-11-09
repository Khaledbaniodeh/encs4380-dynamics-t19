# Repository working rules for coding assistants and contributors

Read [README.md](README.md), [CONTRIBUTING.md](CONTRIBUTING.md), and [docs/versioning.md](docs/versioning.md) before editing. This is a static ENCS4380 coursework site published from `main` through GitHub Pages. Preserve students' ability to explain every calculation, control and submitted code change.

## Keep completed modules separate

- **Module 1 (time domain)** uses `module-1.html`, `python/first_order.py`, and `tests/test_euler.py`; its owner is Khaled Bani Oudeh. It includes the optional Forward Euler comparison.
- **Module 2 (frequency domain)** uses `module-2.html` and `python/First-order frequency response.py`; its owner is Jibreel Haddar. Keep the exact Python filename (including spaces) unless an explicitly agreed rename updates all references.
- Module 3 is implemented and tested in `module-3.html` and `python/second_order.py`. Module 4 remains pending. Keep later modules separate and update `index.html` and README links when ready.
- Do not silently rewrite existing module logic or visuals to implement a new module. Obtain the team's agreement before making unrelated changes to a completed module.
- Python performs numerical calculations in the browser via Pyodide; browser JavaScript integrates controls and Plotly. No server or login should be required. Required response curves use lecture closed-form formulas, with explicitly documented gain, units and initial conditions.
- Module 2 uses **angular frequency in rad/s** in its main model and **Hz** in its design calculator. `omega=2*pi*f` is required for conversions; its sine output is steady-state (not the switch-on transient).

## Preserve the Module 1 checkpoint

- Saved reference commit: `20847b440a8155a036944168de1af0f5aacff641`.
- Snapshot branch: [`checkpoint/module-1`](https://github.com/Khaledbaniodeh/encs4380-dynamics-t19/tree/checkpoint/module-1). Do not rewrite or move it.
- Baseline tracked paths: `module-1.html`, `python/first_order.py`, `tests/test_euler.py`.
- On `main`, `module-1.html` has three documented text/default-view differences from the saved snapshot; the Python model and Euler tests still match. Do not describe `main` as byte-for-byte identical to the snapshot.
- If a necessary fix changes Module 1, explain the scope, obtain the user's approval, use a clearly described separate commit, and preserve the original reference. Do not alter stored blob hashes simply to make comparisons pass.

**Important (verified 5 November 2026):** the previously described read-only **Module 1 checkpoint guard is not installed** in `.github/workflows/` on `main`. There is no confirmed automated guard, branch-protection rule or deployment gate. Use the snapshot hashes in [docs/versioning.md](docs/versioning.md) for manual verification until an explicitly configured check exists.

## Testing and documentation expectations

- Verify each affected page after editing: Python loads, controls respond, plots update, mobile navigation works, and validation checks display expected/computed/tolerance/Pass or Fail.
- Run `python -m unittest discover -s tests -v` for the existing Euler tests; do not imply these tests cover every module.
- Test on desktop and phone for interface changes, and distinguish team-reported testing from independent browser verification. Module 2 phone testing was reported successful by Jibreel Haddar; its desktop and mobile PNG screenshots are saved in `docs/screenshots/`.
- Keep `README.md` accurate for modules, owners, known limitations, screenshots and AI assistance. Keep `docs/versioning.md` accurate for snapshots, differences and release status.
- Each teammate should contribute via their own GitHub account. Do not claim tests, authorship, approval, deployed results or checkpoint acceptance that have not actually occurred. Never commit credentials or secrets.

## Releases and course milestones

- Checkpoint 1 (3 Nov 2026): Module 1 code preserved on a reference branch; a saved branch does **not** prove instructor sign-off.
- Checkpoint 2 (9 Nov 2026): **Modules 2 and 3** must work. Modules 2 and 3 are implemented and ready for Checkpoint 2.
- Final submission (12 Nov 2026): all four modules and a GitHub release tagged **`v1.0`**, with the live Pages link submitted according to the brief.
- The `checkpoint-1` tag/release and `v1.0` release were not created at the last check. Do not represent a branch as a tag or publish a final release early.
