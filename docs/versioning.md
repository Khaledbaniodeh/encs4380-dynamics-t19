# Checkpoints and versioning

This record distinguishes the saved source snapshots, current `main`, and actual course checkpoint/release status (reviewed on **5 November 2026**).

## Checkpoint 1 — Module 1 reference snapshot

- Course checkpoint date: **3 November 2026**.
- Saved source commit: [`20847b440a8155a036944168de1af0f5aacff641`](https://github.com/Khaledbaniodeh/encs4380-dynamics-t19/commit/20847b440a8155a036944168de1af0f5aacff641).
- Snapshot branch: [`checkpoint/module-1`](https://github.com/Khaledbaniodeh/encs4380-dynamics-t19/tree/checkpoint/module-1).
- This is a saved **branch**, not a tag or a GitHub Release; it does not establish instructor acceptance. The `checkpoint-1` tag/release is **not created**.

The saved baseline Git blob hashes are:

| File | Snapshot blob SHA | Current `main` comparison |
| --- | --- | --- |
| `module-1.html` | `20ce7df8bd2a7087499af983430b7aefcfe9bd33` | **Changed**: `4171e771a992afd19c02c5386e25fd211c53992d` |
| `python/first_order.py` | `e095d0d876b405dab1d122b70714a6bd29547ea3` | Identical |
| `tests/test_euler.py` | `3bde45d74fbb1d6644aedc201bfbd196dba598d6` | Identical |

The `module-1.html` change is limited to three lines of text/default-view markup in the Step error section (the default now selects the natural-log view). The saved checkpoint branch still contains the earlier version.

## Module 2 implementation — 5 November 2026

Module 2 lives on `main`, separate from Module 1, in:

- [`module-2.html`](../module-2.html) — live sine/Bode interface, cutoff markers, dynamic-error calculator, prediction, validation and responsive navigation.
- [`python/First-order frequency response.py`](../python/First-order%20frequency%20response.py) — the first-order frequency-response calculations and lecture checks 2–3.
- [`docs/screenshots/module2-desktop.png`](screenshots/module2-desktop.png) and [`docs/screenshots/module2-mobile.png`](screenshots/module2-mobile.png) — supplied desktop and mobile screenshots.

Jibreel Haddar is recorded as Module 2 owner and reported successful testing on a physical phone. This is a team report, not a claim of independently repeated device testing. No separate `checkpoint/module-2` branch or `checkpoint-2` tag/release has been created.

## Module 3 implementation — 9 November 2026

Module 3 is implemented on `main` in:

- [`module-3.html`](../module-3.html) — interactive second-order response, pole plots, state-space view, phase plane, prediction exercise and validation.
- [`python/second_order.py`](../python/second_order.py) — closed-form second-order responses, optional RK4 comparison, curve-based metrics, poles, state-space calculations, eigenvalues and validation.

The state-space view plots poles and eigenvalues together on the same s-plane so their matching locations are visible. The Module 3 update was committed as `0636193` on 9 November 2026. The required Module 3 validation checks pass.

## Checkpoint 2 and final release

| Milestone | Deadline | Status |
| --- | --- | --- |
| Checkpoint 2: Modules 2 and 3 working | **9 November 2026** | **Ready**: Modules 2 and 3 are implemented and tested |
| Final delivery: Modules 1–4, version `v1.0` | **12 November 2026** | **Pending**: Module 4 and release/submission requirements remain |

The `v1.0` GitHub Release has **not** been published. Preserve existing snapshots and avoid representing an in-progress module as a completed course checkpoint.

## Change detection and safeguarding earlier modules

The earlier documentation said that a read-only **Module 1 checkpoint guard** runs on pushes and pull requests. However, the `.github/workflows/` directory was **absent from `main` when checked on 5 November 2026**. Therefore, that automated guard must **not** be treated as currently active.

The table above is a *manual snapshot comparison*, not an automatically enforced GitHub status check. No branch-protection or deployment gate was verified. GitHub Pages serves the current `main` files, while the checkpoint branch preserves Module 1's historical version.

Keep later modules in separate HTML and Python files. If a Module 1 fix is necessary, review and document the difference separately and retain the original checkpoint reference.
