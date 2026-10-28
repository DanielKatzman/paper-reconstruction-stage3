# Stage 3 v2 orchestrator interface

Stage 3 release **v2.0.0** composes with Stage 2 **v1.0.2** and Stage 4 **v2.0.5**. The shared SDK package remains0.1.0; its evidence wire schema remains `stage3.assembly-evidence.v2`. Do not confuse a component repository tag, model release, runtime algorithm version, SDK version or wire-schema version.

## Build

Read `compatibility.json` at a selected tag. Resolve compatible releases at image build time, then lock exact Git revisions and model/configuration hashes. The orchestrator can offer automatic latest-compatible selection or a manual selection. Do not follow floating `main`/`latest` independently for each runtime job.

Package the SDK and Stage 3 with Python 3.12 and CPU Torch 2.7.1 by default. The two model files live in `models/`; verify using `tools/verify_release.py` in a source checkout and `paper-stage3 verify --models <models>` in the installed runtime. Core/model/pooling inventories are preserved under `provenance`. Stage 2 and Stage 4 can use separate internal interpreters. No inter-stage HTTP servers are required.

## Input

- Accepted immutable Stage 1 `segmentation_manifest.jsonl`, original piece crops and binary masks.
- Stage 1 `capture_profile.json`: schema `stage1.capture-profile.v1`, `motion_model=rotation_translation`, `shared_native_pixel_scale=true`, `relative_piece_scale=1`, `per_piece_resize=false`, `perspective=false`.
- A completed truth-free Stage 2 `edge_hypotheses_manifest.json`, `pieces/*.json`, NPZ arrays and sealed assets from repository releasev1.0.2/model release1.0.0.
- Explicit model directory and a dedicated per-job output path.

The orchestrator owns capture calibration/review and must honor Stage 1 acceptance flags. Do not falsely relabel predicted masks as exact generator masks. Continuous rotation is allowed; shared scale does not imply an A4 page or known DPI. Arbitrary perspective or independently resized pieces are outside this acquisition model.

## Execution

Invoke the installed `paper-stage3 prepare --stage1 <s1> --stage2 <s2> --models <models> --output <job/stage3> --puzzle-id <stable-job-id>`. CPU is the default; optional CUDA must be selected explicitly. The public Python module is `paper_reconstruction_stage3_release`.

Read progress from stderr and final JSON from stdout. Use the returned `bundle` path, normally `<job/stage3>/bundle`, as Stage 4's input. `native` and `native.work` are retained evidence/checkpoints, not a request to rerun inference after every Stage 4 change. The unchanged pooling policy is `support-pose-strata.v1`.

Separate commands are `infer`, `pool`, `inspect`, and `verify`. Pooling and inspection need no Torch. Interruptions preserve committed native work; repeat identical commands to resume. An existing pooled publication is reused only when input/configuration/interface bindings match. Source, device, model or acquisition changes require a new output context. A stale process lock after a hard crash requires confirming the process is stopped before manual recovery; automatic lock takeover is not implemented.

Return codes:0 published/validated evidence,2 input/runtime failure,130 interrupted. A ready evidence bundle is not a solved reconstruction. Stage 4's assessment determines supported/partial/unresolved outcomes. Run one resource-budgeted job initially; whole-pipeline scheduling, cancellation and durable job state belong to the orchestrator.

## Stage 4 handoff

The immutable folder contains `bundle.json`, working-pool JSON, compressed native hypotheses with all support occurrences, and portable PNG/NPZ assets. Validate with the independent SDK. Transform `transform_b_to_a` maps native pixels of canonical pieceB into pieceA; contours are clockwise in image coordinates, origin is top-left, x right and y down. Never renormalize each piece's scale independently.

Stage 4 v2.0.5 consumes this schema with unchanged source/model banks. Its predicted-mask and exact-mask page profiles differ; select the truthful profile. Its native recovery and independent support/collision/page verification remain essential. Stage 3 does not consume recovery requests automatically in this release, nor does it seed inference from successful saved assemblies.

## Compatibility check

`tools/check_integration.py` accepts explicit Stage 2/Stage 4 checkout paths, interpreters, a small Stage 1 input and a fresh output path. It authenticates the pinned model/configuration and SDK, runs fresh CPU Stage 2 inference/verification, Stage 3 native inference/pooling and cold Stage 4. It accepts no evaluation reference. See `docs/VALIDATION.md` for the recorded check. Full thirty-piece inference is intentionally not required for an integration-only release whose core bytes remain unchanged.

The fourteen-page development cohort and separate six-piece capture result belong to Stage 4's qualification; do not advertise them as unseen reliability or newly measured Stage 3 CPU throughput. Performance and coverage changes will receive distinct source identities and qualifications.
