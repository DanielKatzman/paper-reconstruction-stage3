# Paper Reconstruction — Stage 3 v2.0

CPU-default pair-placement evidence for the modular paper reconstruction pipeline.

**Release v2.0.0 is compatible with Stage 2 v1.0.2 and Stage 4 v2.0.5.** It packages the qualified `unit-scale-v5` runtime used by Stage 4, the same two frozen rankers, and the unchanged `stage3.assembly-evidence.v2` file contract. No retraining, retrieval changes, numerical acceleration, or new pose policy is included.

Stage 3 reads accepted Stage 1 pieces/masks and Stage 2 boundary observations. It proposes relative rigid placements; Stage 4 owns global reconstruction and independent support/page verification. The qualified core keeps its original software version `0.9.32` and algorithm/model identities. The public distribution and interface version is `2.0.0`.

[Compatibility manifest](compatibility.json) · [Orchestrator contract](docs/ORCHESTRATOR.md) · [Release validation](docs/VALIDATION.md) · [Stage 4 handoff](https://github.com/DanielKatzman/paper-reconstruction-stage4/blob/v2.0.5/docs/STAGE3_HANDOFF.md)

## Install

Use Python 3.12. The two small model weights are included in Git; no research dataset, sibling checkout, GPU, or Git LFS download is required to use this component.

```powershell
git clone --branch v2.0.0 https://github.com/DanielKatzman/paper-reconstruction-stage3.git
cd paper-reconstruction-stage3
py -3.12 -B tools/setup.py
.\.venv\Scripts\python.exe -B tools/verify_release.py
.\.venv\Scripts\python.exe -B scripts/stage3.py verify
```

On Linux use `python3.12 -B tools/setup.py` and `.venv/bin/python`. Setup creates a **new CPU-only** environment and refuses to replace an existing one. CUDA is an explicit opt-in (`--device cuda` at setup and inference); it never silently replaces CPU execution. macOS installation has not been qualified by this release.

For an orchestrator-managed environment, install CPU Torch first, then the standalone SDK and package:

```text
python -m pip install torch==2.7.1+cpu --index-url https://download.pytorch.org/whl/cpu
python -m pip install -e ./contracts/stage3_to_stage4/v2/sdk -e .[test] -c constraints.txt
```

The first command targets Windows/Linux. Dependency versions are pinned in `constraints.txt`. Do not replace an existing development GPU environment just to install the CPU release.

## Produce the Stage 4 input

From the repository root, run one page through native inference and unchanged observable pooling:

```powershell
.\.venv\Scripts\python.exe -B scripts/stage3.py prepare `
  --stage1 path/to/stage1 --stage2 path/to/stage2 `
  --output outputs/my_page/stage3 --puzzle-id my_page
```

No device option is needed: **CPU is the default**. Pass `--device cuda` only when explicitly wanted.

`prepare` writes:

- `native/`: the qualified native archive and initial working pool.
- `native.work/`: authenticated resumable rankings and physical-pair caches.
- `bundle/`: the final immutable `support-pose-strata.v1` publication for Stage 4.

**Give Stage 4 the `bundle/` directory.** Progress goes to stderr; stdout ends in JSON containing the bundle path and release version. Exit code zero means evidence was published, not that a page was solved. Interrupted native work resumes by repeating the identical command. An already published pooled bundle is reused only after validating its source, policy and interface identity. Changed code, inputs, device or configuration require a new job directory.

The installed `paper-stage3` console command and `python -m paper_reconstruction_stage3_release` expose the same interface. Use `--models <directory>` when running outside a checkout whose working directory contains `models/`.

Individual phases remain available:

```text
paper-stage3 infer --stage1 <stage1> --stage2 <stage2> --models <models> --output <native>
paper-stage3 pool --input <native> --output <consumer_bundle>
paper-stage3 inspect --bundle <consumer_bundle>
```

`pool`, `inspect` and `verify` do not import Torch. Stage 4 needs only the SDK and its own runtime.

## Acquisition and contracts

Every Stage 1 input must include a truthful `capture_profile.json` declaring common native pixel scale, rotation/translation, scale1, no independent resizing and no perspective. Continuous rigid rotations and predicted/reviewed masks are supported inputs; exact masks and quarter turns are not general requirements of Stage 3. See [the predicted-mask profile](profiles/shared_scale_predicted_capture_v1.json). A declaration describes the acquisition assumptions; it does not calibrate a camera.

Stage 2 v1.0.2 contains boundary **model release1.0.0**. These are separate versions. The adapter authenticates that model/configuration, `stage2.edge-hypotheses-manifest.v1`, per-piece arrays, accepted piece inventory and Stage 1 lineage. No synthetic contract is substituted for real Stage 2 output.

Output coordinates remain native crop pixels, clockwise contours and canonical transforms from piece B to piece A. Preserve stable physical-piece IDs and every support occurrence. The SDK/schema bytes match Stage 4 v2.0.5. Page dimensions, aspect ratio and DPI are not guessed; page completeness/geometry profiles belong to Stage 4.

## Tests and synthetic example

```powershell
.\.venv\Scripts\python.exe -B scripts/test.py
.\.venv\Scripts\python.exe -B scripts/stage3.py prepare `
  --stage1 examples/synthetic_page/input/stage1 `
  --stage2 examples/synthetic_page/input/stage2 `
  --output outputs/synthetic_page
```

The synthetic example checks interchange and inventory, not reconstruction accuracy. [Validation](docs/VALIDATION.md) records the fresh small-case CPU Stage 2 → Stage 3 → Stage 4 check and its limits. Existing Stage 4 development results through30 pieces are not a new full-pipeline CPU performance or held-out reliability claim for this release.

## Orchestrator integration

Each teammate can release a stage independently. The application repository should resolve compatible releases, pin commits/model/configuration hashes, and build one container with each stage as an internal process. It can select the latest **compatible** release or an explicit manual version; runtime jobs must use the resulting fixed manifest. This component does not add an HTTP service or a container of its own.

Use [docs/ORCHESTRATOR.md](docs/ORCHESTRATOR.md) for the exact entry points, input/output paths, status handling and dependency pins. The known expensive pose preparation remains unchanged; optimization is separate follow-up work.

## Contents

| Path | Purpose |
| --- | --- |
| `src/paper_reconstruction_stage3/` | Byte-preserved qualified unit-scale core; original provenance versions |
| `src/paper_reconstruction_stage3_release/` | CPU-default CLI and unchanged pooling implementation |
| `models/` | Two frozen inference-only checkpoints and sealed model/config manifest |
| `contracts/stage3_to_stage4/v2/sdk/` | Independent Stage 3→4 file SDK and schemas |
| `compatibility.json`, `provenance/` | Version compatibility, source inventories and qualification receipts |
| `tools/`, `tests/`, `examples/` | Setup, release verification, integration check and portable fixtures |

Datasets, local environments, experiments and generated outputs are excluded from Git. Historical alpha design documents remain background; this README and compatibility manifest define the v2 interface.
