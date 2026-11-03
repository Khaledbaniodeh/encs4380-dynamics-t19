# Checkpoints and versioning

## Module 1 reference snapshot

- Source commit: [`20847b440a8155a036944168de1af0f5aacff641`](https://github.com/Khaledbaniodeh/encs4380-dynamics-t19/commit/20847b440a8155a036944168de1af0f5aacff641).
- Snapshot branch: [`checkpoint/module-1`](https://github.com/Khaledbaniodeh/encs4380-dynamics-t19/tree/checkpoint/module-1).
- This records the code available on 3 November 2026. It is not an assertion that the instructor accepted the checkpoint or that all administrative/device checks are complete.
- The snapshot is currently a saved **branch**, not a tag/release. The requested `checkpoint-1` tag/release has not been created.
- The final homework release will be tagged `v1.0` after all four modules are complete.

## Keep future modules separate

Home/navigation lives in `index.html`. Module 1 lives in `module-1.html` and `python/first_order.py`, with its Euler regression tests in `tests/test_euler.py`.

Add future modules as separate pages and Python files. A home-page link can be added without editing Module 1. Review and agree on any necessary Module 1 fix explicitly, then use a separate commit; retain the original snapshot.

## Change detection

`Module 1 checkpoint guard` runs on pushes and pull requests to `main`. It uses read-only access to compare the current Git blob hashes with the saved values:

| File | Baseline Git blob SHA |
| --- | --- |
| `module-1.html` | `20ce7df8bd2a7087499af983430b7aefcfe9bd33` |
| `python/first_order.py` | `e095d0d876b405dab1d122b70714a6bd29547ea3` |
| `tests/test_euler.py` | `3bde45d74fbb1d6644aedc201bfbd196dba598d6` |

If one of these files is changed, deleted or cannot be verified, the check fails. Do not change the stored hashes solely to obtain a passing result.

This check reports changes; it is **not** a branch-protection rule or a deployment gate. The GitHub Pages URL continues to show the current `main` version. Use the saved commit/branch to inspect the checkpoint.

## Release creation status

The saved branch and the read-only guard are the completed safeguards. The `checkpoint-1` tag/release remains pending. No `v1.0` release has been published.
