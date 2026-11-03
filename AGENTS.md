# Repository working rules

## Preserve the Module 1 checkpoint

The user has requested a simple structure that lets future modules be added without accidentally changing Module 1.

- Frozen reference commit: `20847b440a8155a036944168de1af0f5aacff641`.
- Saved snapshot branch: `checkpoint/module-1`.
- Preserve `module-1.html`, `python/first_order.py`, and `tests/test_euler.py` when working on other modules.
- Put later modules in their own HTML pages and Python files. Update `index.html` to link to them.
- If a requested change genuinely requires editing Module 1, explain the exact change and obtain the user's agreement before editing those frozen files.
- Do not move the checkpoint reference or change expected blob hashes merely to make the guard pass.
- An intentional approved fix should be a separate, clearly described commit. Keep the original checkpoint available.
- Reserve the release tag `v1.0` for the final four-module submission.
- Do not describe a backup branch as a tag or published release. The current snapshot is a branch; the `checkpoint-1` tag/release has not been created.

The read-only GitHub Actions check detects changes; it is not branch protection and does not itself prevent a GitHub Pages deployment.
