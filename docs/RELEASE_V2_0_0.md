# Stage 3 v2.0.0

Integration release for the single-container paper reconstruction orchestrator. Compatible with **Stage 2 v1.0.2** and **Stage 4 v2.0.5**.

- Qualified unit-scale-v5 core and both frozen rankers preserved byte-for-byte.
- CPU-default installed `paper-stage3` interface, with explicit optional CUDA.
- `prepare` composes native inference and unchanged support-pose-strata.v1 pooling; Stage 4 receives its `bundle/` directory.
- Authenticated resume, independent SDK, installed JSON resources and machine-readable compatibility/source inventories.
- 31 tests pass locally. Fresh CPU Stage 2 → Stage 3 → Stage 4 four-piece integration returns a supported connected assembly; both built wheels load independently with CPU-only Torch.

The release tag/distribution is2.0.0; the frozen core keeps software0.9.32/model/algorithm provenance. Input remains Stage 2 model release1.0.0 inside repository releasev1.0.2. Output remains `stage3.assembly-evidence.v2`, with unchanged native coordinates and support occurrences.

Install from this tag using Python 3.12 and `python -B tools/setup.py`. Two model files are included in Git. Read `README.md`, `compatibility.json`, `docs/ORCHESTRATOR.md` and `docs/VALIDATION.md`.

This release does not retrain models, optimize runtime, introduce new pose/parent policies, or claim a new full thirty-piece CPU benchmark. Stage 4 remains responsible for global reconstruction, recovery and independent physical/support/page checks.
