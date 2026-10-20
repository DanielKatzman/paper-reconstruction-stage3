# Stage 4 development handoff

Prepared **2026-10-20** for a new development chat. This document records the current state and recommended next work; the Stage 4 implementation and experiments below have **not** been completed.

Stage 3 repository: [DanielKatzman/paper-reconstruction-stage3](https://github.com/DanielKatzman/paper-reconstruction-stage3). Frozen runtime baseline: commit `ae06b96556458c13468e53c336ac3d682b671c52`, software **0.9.32**, alpha **0.1.1**, algorithm `stage3.alpha-evidence.v0931`, recipe `frozen-core-composition-v1`.

## 1. Start here

The user wants to see actual global reconstruction before investing in another Stage 3 scorer. **Build Stage 4 as a separate project**, consuming immutable Stage 3 evidence folders through the released contract. Establish an honest assembly baseline, diagnose its failures, then decide which stage needs improvement.

Read these in order; paths are relative to this Stage 3 checkout:

1. This handoff, then [README.md](README.md).
2. [The normative Stage 3 output / Stage 4 input contract](contracts/stage3_to_stage4/v2/README.md), its three JSON Schemas and independent SDK.
3. [Stage 4 integration](docs/STAGE4_INTEGRATION.md) and [the example consumer](examples/stage4_consumer.py).
4. [Validation](docs/VALIDATION.md), [parity scope](docs/PARITY.json) and [development notes](docs/DEVELOPMENT.md).
5. For the first solver control, inspect the local archived `pose_solver.py` described in section 7. For historical scientific conclusions, read the local v0.9.30 completed review described in section 3.

The older `research_archive/v0.9.31/STAGE3_CODEX_CONTINUATION_HANDOFF.md` describes an earlier research state. Its immediate sequence is superseded by this document and the current alpha documentation.

## 2. Architecture, ownership and actual status

```text
Stage 1: accepted piece segmentation and cropped RGB/masks
    -> Stage 2: frozen boundary roles and candidate predictions
    -> Stage 3: observable neighbor / relative-pose alternatives
    -> Stage 4: globally consistent components, poses and unresolved pieces
```

Each stage is intended to be a separate project, eventually runnable in its own container. File contracts connect them. A shared database, HTTP server and Docker deployment are unnecessary for the first Stage 4 baseline.

| Area | Current state |
| --- | --- |
| Stages 1 and 2 | Complete/frozen for this work; do not modify or retrain as a side effect |
| Stage 3 alpha | Cleaned, tested and published; frozen inference and evidence export |
| Stage 4 input | Released `stage3.assembly-evidence.v2`, SDK 0.1.0, portable sealed assets |
| Independent consumer | Implemented; validates/reads evidence, does not assemble it |
| Historical forest solver | Local archived control; not a finished independent Stage 4 product |
| New Stage 4 project, CLI and output contract | Still to implement in its own workspace/repository |
| Real 4/8-piece assembly pilot | Still to design and run |
| Reliable solved-piece capacity | **Unknown**, represented as `null` |
| Targets | Reliable 20-piece baseline would be useful; 30 pieces remains the milestone |

A connected candidate graph, many pose alternatives, passing integrity checks, or individually accurate contacts do not establish a correct whole-page reconstruction. Do not report an established 2-, 3-, 4-, 20- or 30-piece capacity from the current evidence.

## 3. Why we are moving downstream now

The Stage 3 research explored shape retrieval, learned pair ranking, local windows, similarity and projective fitting, sliding alignment, RGB continuation, ordered correspondence, learned corrections and context/choice scoring. The user also proposed using whole-piece content and line/word continuation. More context remains a plausible signal, but the reviewed experiments did not qualify a new correction/choice scorer for the alpha.

The completed v0.9.30 experiment was technically valid: 322 prepared blocks, six epochs, 1,074 optimizer updates, 11,440 fit draws and 68,640 exposures. The correction expert and backbone received zero updates. All seven retained checkpoints failed the predeclared **calibration** gates; selection fell back to step zero and there were **zero internal confirmations**. The old `model_failed_internal_gate` readiness text was generic and must not be described as a failed internal evaluation. Sources remained unchanged and predictions committed before closed evaluation.

The unqualified scorer added no accepted poses. On two already inspected development cases, source contact coverage remained **3/5** under **p95 <= 4 native piece-A pixels**:

- Two-piece case: no source alternative passes the single contact; best error **6.6484 px**.
- Four-piece case: passing alternatives exist among pieces 1/2/3, but contact 2/4 is absent at the criterion; best error **7.2518 px**. The individually passing alternatives do not certify a compatible three-piece assembly.
- Previously saved complete assemblies fail their complete saved-reference checks. That review did not run a new global solver.

One family supplied 423/503 valid calibration anchors, and 266/503 anchors had no admissible move in the frozen trial set. These findings do not justify assuming that a larger encoder alone will solve the problem. These cases are useful debugging controls, not independent confirmation data. Failure on a small ambiguous case also does not establish that larger, more constrained pages cannot work.

The review found a concrete export problem: equal-transform grouping could discard distinct candidate/support and per-variant evidence. This was repaired in v0.9.31 with complete `occurrences[]`, stable candidate/observation keys and native assets. Serving was separated from training/teacher dependencies. The v0.9.32 cleanup extracted the runtime and independent contract SDK.

**Current recommendation:** hold Stage 3 fixed, measure global selection with the available alternatives, and separate missing evidence from solver mistakes. Do not resume the historical scorer-training sequence by default.

Local authoritative historical review: `generated/review_checks_v0930/REVIEW.md`; detailed proof: `native_review_result.json` and `review_result.json` in the same directory. The native review replayed production preparation, retained checkpoints, policy decisions, handoffs and closed metrics without training. Repeating that expensive audit is unnecessary for starting Stage 4.

## 4. What was published, and what exists only locally

The active repository contains 30 Stage 3 runtime modules, two frozen inference-only models (3,133,722 bytes combined), the model/policy manifest, independent CPU contract SDK, small scripts, lean tests and a synthetic example. Optimizer state and research orchestration are omitted. See [cleanup inventory](docs/CLEANUP_INVENTORY.md).

The recorded validation passed **21/21 lean tests**. Original v0.9.31 and cleaned v0.9.32 new-input runtimes produced exactly equal complete archives and working pools on the synthetic production fixture: **69 geometries, 134 occurrences, 24 working edges**. Model-input tensors and frozen scores also match within the documented checks. This establishes preservation and interoperability on that fixture, **not real assembly accuracy**.

Two distinctions matter:

- New inputs use the declared **frozen-core-composition-v1** recipe. The manifest explicitly says it does not exactly replay every historical research branch on arbitrary new inputs.
- The richer historical real source-only exports preserve previously computed evidence. Their existence does not prove that every historical score/branch is reproduced by new-input serving.

| Location | Availability and purpose |
| --- | --- |
| `contracts/stage3_to_stage4/v2/` | In Git; normative contract, schemas, hash vector and independent SDK |
| `examples/synthetic_page/` | In Git; Stage 1/2-shaped inputs and matching precomputed evidence |
| `models/alpha.json` | In Git; authoritative frozen policy, recipe, caps and model identities |
| `research_archive/v0.9.31/` | Local only, ignored; preserved original source/tests/configs/release manifests |
| `generated/` | Local only, ignored; approximately 85.96 GiB of historical results/caches/data at cleanup time |
| `.venv/` | Local only, ignored; existing working Windows/CUDA environment |
| `generated/stage3_alpha_v0931/examples/` | Local only; two real source-only evidence bundles listed below |

Local real example directories:

```text
generated/stage3_alpha_v0931/examples/puzzle_000371_d5b710a03018/
generated/stage3_alpha_v0931/examples/puzzle_000461_ffe5e308e9ad/
```

The reviewed two-/four-piece exports contain respectively 538/5,226 geometries, 1,785/17,700 occurrences and 24/144 working edges. They are already inspected development material. Do not advertise their results as held-out performance.

Original generated data was retained, not deleted. The archived source release was verified byte-identical to its release manifest. A fresh GitHub clone does **not** contain the archive, real documents, full datasets or historical experiment outputs.

On the original Windows machine, discover upstream data relative to the user profile:

```powershell
$stage3Root = Join-Path $env:USERPROFILE 'Desktop\paper-reconstruction-stage3'
$stage1DataRoot = Join-Path $env:USERPROFILE 'Desktop\universal-paper-segmenter\data'
$stage2DataRoot = Join-Path $env:USERPROFILE 'Desktop\paper_reconstruction_stage3_inputs_v1'
```

The Stage 1 root contains the user's complete dataset v1. Inspect manifests, family identities, splits and eligible single-page piece counts; do not guess a child path or assume every file is eligible. The 162 Stage 1 jobs used in earlier studies contain **4–8 pieces**, not 20. Deliberately construct larger eligible single-page cases; do not combine unrelated pages. The Stage 2 root contains historical observable native predictions/assets. Keep closed evaluation maps out of the serving/search process.

## 5. Stage 4 input contract: details that must survive implementation

The normative specification is [contract v2](contracts/stage3_to_stage4/v2/README.md). This section highlights common implementation errors; the schemas and SDK remain the source of truth.

### Publication and independence

```text
<evidence-directory>/
  bundle.json
  working_pool.json
  hypotheses.jsonl.gz
  assets/<sha256>.png
  assets/<sha256>.npz
```

`bundle.json` is written last and is the readiness barrier. Validate the whole artifact before solving. Inputs are immutable; Stage 4 writes elsewhere. Ignore unfinished directories, `*.tmp` and the optional producer `export_request.json` marker. Invalid input is an explicit failure, never an empty puzzle.

Schema IDs: `stage3.assembly-evidence.v2` and `stage3.working-pool.v1`. SDK distribution: **paper-reconstruction-contracts 0.1.0**, independently installable from `contracts/stage3_to_stage4/v2/sdk`. Dependencies: NumPy, Pillow and jsonschema. **Stage 4 must not import the Stage 3 runtime or require its Torch/models/databases.** Install the SDK into Stage 4's own environment when setting up that project; do not upgrade the existing Stage 3 environment.

```python
from paper_reconstruction_contracts import (
    ContractError, compose, load_bundle, map_points, relative_file,
)

data = load_bundle(evidence_directory, full=True)
entries = data.entries
edges = data.edges
```

`entries` is keyed by physical piece ID and exposes `piece_id`, `observation_key`, resolved `image_path`/`mask_path`, and `size_hw`. `edges` preserves working-pool fields and provides aliases **`id`, `a`, `b`, `transform`**, plus `weight`, `pose`, score method/variant and occurrence links. This matches the old solver's edge shape, but does not make that solver a complete support-aware consumer.

`data.manifest`, `data.pool` and `data.root` expose the other validated metadata. For a contour, resolve `data.manifest['pieces'][piece_id]['contour']` through `relative_file(data.root, ...)`; do not assume `entries` contains contour arrays. `data.hypotheses()` lazily yields full geometry groups. Archive count/membership checks finish only on exhaustion; `full=True` already exhausts it once for validation. Avoid loading all groups into memory without a declared budget/indexing plan.

### Coordinates and composition

One physical piece has one registered native observation in this alpha. Preserve all physical pieces, including isolated and zero-candidate pieces. Coordinates are native cropped pixels: origin top-left, x right, y down. Canonical physical pairs use Python Unicode code-point order, `a < b`.

`H_b_to_a` maps **B native crop into A native crop**, using column homogeneous coordinates:

```text
[u, v, w]^T = H_b_to_a @ [x_b, y_b, 1]^T
(x_a, y_a) = (u/w, v/w)
H_c_to_a = H_b_to_a @ H_c_to_b
H_a_to_b = inverse(H_b_to_a)

G_i maps piece i into its component's coordinate frame.
G_b = G_a @ H_b_to_a
move_for_B_component = G_a @ H_b_to_a @ inverse(G_b)
```

Matrices may be proper similarity or guarded projective transforms. Preserve the complete 3x3 matrix and homogeneous division. Check projective denominator/poles and local Jacobians over the whole crop, reflection/orientation and scale, plus physical mask overlap. A locally good edge fit can still warp the rest of a piece badly. The SDK validates contract geometry; it does not certify a globally feasible assembly.

Use a deterministic component gauge, e.g. the lexicographically smallest physical piece at identity. Separate components have independent gauges. A visualization may pack them on a canvas, but those display offsets are not measured inter-component poses.

### Alternatives, support and scores

The full archive groups exact normalized transforms without rounding. Each geometry retains **every `occurrences[]` record**, with stable candidate keys, physical/observation identities, original query/target direction, full pose/support spans/windows/fractions, original matrix and method evidence. Duplicate historical record aliases remain distinct occurrences.

The working pool is a bounded portfolio, default **24 geometries per physical pair**, with links to the full archive and explicit retained/available counts. Do not rebuild a lossy grouped map. A selected geometry can have multiple possible support occurrences: record which compatible occurrence assignment supports the selected joins. Do not treat all correlated occurrences as simultaneous independent evidence. Support exclusivity across chosen joins is Stage 4's responsibility and is not implemented by the reader.

Weights are **uncalibrated heuristics**, not probabilities. Method/variant scope matters. Correlated variants must not be added as independent votes. Historical method name `reference` is an observable baseline, not a truth-fitted teacher. Blank/insufficient RGB content can abstain; absence is not zero error. Any abstention objective, score normalization or threshold needs an explicit version/configuration and development-only selection.

At 24 alternatives/pair, all-pairs upper bounds are 4,560 working edges for 20 pieces and 10,440 for 30; actual counts depend on evidence availability. Neither bound establishes runtime or solvability. Start from the bounded pool and report truncation; inspect the full archive under a separate declared budget when diagnosing pruning.

### Integrity and evaluation separation

Relative POSIX paths, file sizes/SHA-256, schema checks and cross-file ownership are enforced by the SDK. No absolute/escaping paths or pickle arrays. The NPZ whitelist is `points_xy`, `arc_length_px`, `tangent_xy`, `inward_normal_xy`, `curvature_per_px`, `corner_strength`, `inward_thickness_px`, `role_probabilities`, `transition_probabilities`.

Canonical digests use UTF-8 Python JSON, sorted keys, compact separators, `ensure_ascii=True`, `allow_nan=False`; see `hash_test_vector.json`. Preserve numeric encoding and artifact bytes/line endings. The repository's `.gitattributes` disables automatic text conversion for this reason. Unknown contract versions must fail; breaking semantics require a new contract version.

Evidence contains no teacher transforms, labels, saved reference anchors or opened protected evaluation. Publish immutable Stage 4 predictions **before** opening evaluation maps. Put evaluation in a separate command/process and output directory. Integrity validation is not an accuracy evaluation.

## 6. Frozen Stage 3 behavior and commands

The recipe combines frozen shape retrieval, symmetric MLP/CNN pair ranking, gated fitting windows, similarity fits, sliding overlap, guarded projective fitting, broader geometric support and RGB continuation. The correction scorer is **disabled**. Manifest `models/alpha.json` is authoritative; its manifest identity is `86d547731a0b3b629647d01d657c19170859e47264a79ed1e947c2c1e0b6e59e`.

Recipe caps include 1,024 candidates (explicit failure above the cap), retrieval pool 80/query, 20 parents/query, four parents/physical pair, 16 local windows and 24 working geometries/pair. Do not confuse these with older `pose_configuration` alternatives/beam fields or assume every historical policy field is active in every branch. Do not edit the frozen policy to make a downstream benchmark pass.

From the **Stage 3 root**, using the existing environment:

```powershell
# Model/policy verification only; no inference, training or assembly.
.\scripts\run_stage3_windows.cmd

# Small existing checks, not research experiments.
.\.venv\Scripts\python.exe scripts\test.py
.\.venv\Scripts\python.exe examples\stage4_consumer.py examples\synthetic_page\evidence

# Read an existing evidence folder.
.\.venv\Scripts\python.exe scripts\stage3.py inspect --bundle examples\synthetic_page\evidence
```

To produce a fresh synthetic handoff, if needed, the user can run:

```powershell
.\scripts\run_stage3_windows.cmd infer --stage1 examples\synthetic_page\input\stage1 --stage2 examples\synthetic_page\input\stage2 --output outputs\synthetic_page --device cuda --puzzle-id synthetic_page
```

This is inference, not an assembly test. The fixture has three physical pieces, two candidate-bearing observations and one zero-candidate piece. White rectangles deliberately expose ambiguity/RGB abstention; do not use it to claim reconstruction capacity.

For a real page, supply matching Stage 1 `segmentation_manifest.jsonl` exports and frozen Stage 2 `edge_hypotheses_manifest.json` exports, plus a new output path. The producer checks lineage, native crop/source maps and frozen Stage 2 identity. CUDA is default; CPU requires `--device cpu`, with no silent fallback. Interrupted identical runs can reuse `<output>.work` caches. Changed source/policy/executable code/schema requires a new output directory. Publication is atomic at the ready manifest. CLI exits are 0 success, 2 failure, 130 interruption.

The tested local setup is Python 3.12, GTX 1070 8 GB, Torch 2.7.1+cu118, NumPy 2.5.3, Pillow 12.3.0, threadpoolctl 3.7.0 and jsonschema 4.26.0. Preserve it. Stage 4 can begin on CPU with its own minimal environment. General CPU serving throughput and Docker/GPU deployment are not yet profiled.

## 7. First Stage 4 solver control: reuse the math, identify the limitations

Local archived starting points:

```text
research_archive/v0.9.31/src/paper_reconstruction_stage3/pose_solver.py
research_archive/v0.9.31/src/paper_reconstruction_stage3/alignment.py
research_archive/v0.9.31/src/paper_reconstruction_stage3/projective.py
```

Inspect `State`, `merge`, `retain_states`, `cycle_summary` and `solve` in `pose_solver.py`; `apply_transform`, `mask_samples`, `collision_fraction` in `alignment.py`; and `warp_check` in `projective.py`. Port the small necessary control/math into Stage 4 with documented origin and tests. Do not add the archived package to Stage 4's runtime imports, restore the entire research tree, or rebuild its candidate edges: consume the contract's working edges.

The archived control:

- Starts with singleton components and considers both skipping and merging edges in a deterministic bounded beam.
- Moves all pieces in one component using the relation in section 5, checks sampled cross-component mask collisions and some warp/scale guards, then regauges to the smallest piece.
- Erodes masks with `MinFilter(3)` and uses sampled collision checks. This is an approximate historical control, not exact pixel-level physical proof.
- Prioritizes **number of tree joins before evidence score** in beam/final selection. It retains some partial tiers, but still favors more feasible joins.
- Uses cycle compatibility as **final reranking/diagnostics**, not a hard rejection of every inconsistent cycle. Positive heuristic evidence can reinforce a bad join.
- Does not implement full occurrence-support exclusivity, calibrated abstention, a global k-best output guarantee or continuous global refinement.

Keep an identified legacy control result rather than silently changing its objective. In the separately named improved baseline, allow unresolved pieces/partial components and explicit feasibility/support handling. Pin objective, ordering, beam, budgets and seed. Use the same input and evaluation protocol for comparisons. If the control accepts something the improved feasibility layer rejects, retain the reason in diagnostics.

Historical defaults include collision grid 24, maximum assembly collision 0.08 and cycle tolerance 8 px. These are control settings, **not** the evaluation rule: the inherited contact criterion is p95 <= 4 native piece-A pixels. Projective safety needs its full policy, not only these three numbers. Inspect the actual configuration and record which guards are approximate. Do not claim that simply porting this control makes the new solver fully safe or correct.

The old `pose_choice_handoff.py` is a historical lossy exporter; it is not the released v2 contract and must not replace the current SDK/export semantics. On a remote clone without the local archive, explicitly report that the legacy source is unavailable; build a documented independent control from the contract, without claiming exact historical solver parity.

## 8. Recommended first implementation iteration

These are proposed deliverables, not completed work or preselected experimental results.

1. **Create a separate Stage 4 project in its authorized workspace.** Inspect existing files/environment first. No Stage 4 remote has been chosen. A sibling `paper-reconstruction-stage4` folder is a suggested location, not an existing project. Use only the contract SDK across the boundary; input is read-only and outputs are separate.
2. **Implement a minimal vertical slice:** validate one bundle, preserve every physical piece, run the bounded forest control, write versioned predictions/diagnostics and a simple layout preview. Add a separately identified partial/abstaining objective with explicit support/feasibility policy. Avoid training, a web service or a learned global model in this iteration.
3. **Define Stage 4's own output contract with the producer.** There is a complete Stage 3-output/Stage 4-input contract already. There is not yet a Stage 4-output contract; do not imply the incoming schema defines its predictions.
4. **Use targeted solver tests before real experiments.** Cover transform inversion/composition and projective division; known compatible chains; mutually exclusive alternatives and conflicting cycles; collision, reflection and pole rejection; zero-candidate/isolated pieces; and a case where leaving a piece unresolved beats a wrong join. Test deterministic output and partial/failure publication. The existing white-rectangle fixture is only an interoperability smoke test; construct explicit known-layout solver fixtures too.
5. **Provide user-run commands for the pilot.** Small deterministic tests/smokes can be run during implementation. The user will launch long inference/benchmark jobs. No full dataset crawl, model training, large evidence regeneration or benchmark should start implicitly.

The proposed Stage 4 output should record:

- Schema/solver/code/SDK versions; input manifest and artifact identities; config, seed, deterministic ordering and resource budgets.
- One physical-piece inventory with component IDs and native-to-component transforms; deterministic gauges; unresolved/isolated status and explicit abstentions.
- Selected geometry IDs and supporting occurrence IDs/assignments, with traceable evidence and rejection/selection reasons. Alternative layouts may be bounded, but do not claim k-best completeness without implementing it.
- Objective terms and score semantics; collision/warp/support/cycle diagnostics; confidence explicitly uncalibrated unless independently established.
- Search termination, examined/pruned counts, caps/truncation, elapsed time, peak memory and failure/interruption state.
- Atomic immutable prediction publication before evaluation; resumability keyed to input/code/config identities. Keep display packing transforms separate from reconstruction poses.

Use an explicit proposed output version such as `stage4.assembly-result.v1` only when implementing/documenting it in Stage 4. No such released schema exists today.

## 9. Pilot and capacity assessment

Begin with **4- and 8-piece single-page cases**, then expand to 12/16/20 as the results justify. Thirty remains the milestone. A useful starting pilot proposal is at least ten puzzles per size spanning at least five document families where data permits; these counts are a planning suggestion, not a previously agreed reliability gate or a statistically established capacity claim.

Before running, register the eligible families/splits, page inventories, Stage 3 recipe, solver variants, search budget and scoring rules. Reserve uninspected families or collect fresh confirmation data. Separate development tuning from confirmation. Existing inspected real bundles and synthetic toy chains are regression/debugging material. Follow known-map development with scanner/phone captures before claiming capture robustness.

Keep the **p95 <= 4 native piece-A-pixel contact criterion** for continuity. Independently specify gauge-invariant component/global placement evaluation, treatment of scale/projective gauge and the whole-puzzle pass rule. Do not silently substitute an 8 px cycle threshold, relax the 4 px rule, or equate a correct join count with a solved page. State the expected-contact denominator, including missing alternatives.

Report whole-puzzle success, correct placements, false/missing joins, largest correct component, unresolved pieces, collision/cycle/pose errors, runtime, peak memory and truncation. Pair comparisons on the same puzzles and describe uncertainty across families. Do not define reliable capacity from one successful page; predeclare the acceptance rule and confirmation set before promoting a piece count.

For each failure, distinguish:

| Diagnosis | Likely next work |
| --- | --- |
| True neighbor absent from candidate retrieval | Stage 3 retrieval/candidate coverage |
| Neighbor exists, no accurate relative pose in complete archive | Stage 3 pose generation / relevant observable content |
| Accurate pose exists in archive, lost from working pool | Stage 3 portfolio/pruning or declared Stage 4 archive expansion |
| Compatible accurate alternatives exist but are not selected | Stage 4 objective, support assignment or search |
| Good local selections accumulate drift or break global feasibility | Stage 4 consistency/refinement, with local errors measured |
| Strong ambiguity/insufficient observable information | Partial layout/abstention; assess additional capture/content evidence |

An evaluation-only oracle can estimate candidate/pose availability after prediction commitment. Never feed its truth-based selections back into the serving solver or present an oracle result as observable performance. More beam width or a larger encoder is a hypothesis to test after this breakdown, not the default explanation.

## 10. Working preferences and boundaries for the new chat

- The user wants useful action and clear recommendations, not repeated confirmations for routine authorized work. Inspect the Stage 4 workspace, summarize the first slice briefly and implement it when asked. Explain any actual permission/workspace blocker specifically.
- The user runs long scripts. Provide exact **PowerShell-compatible** commands, expected artifacts, resume behavior and the next review step. Do not use cmd.exe `^` continuations in a PowerShell command block.
- Preserve the frozen Stage 3 alpha, existing CUDA environment, datasets, archived evidence and evaluation split boundaries. Do not install/upgrade packages, retrain models, alter upstream stages or launch heavy jobs as an incidental setup step.
- No Stage 4 repository, output schema, Docker deployment or real assembly capacity is already established. Treat these as explicit future deliverables. A shared file-contract SDK is compatible with separate microservices.
- Prefer a small interpretable baseline with visible layouts and failure attribution. Further Stage 3 context/whole-piece learning becomes sensible when measured downstream failures identify what signal is missing.

## 11. Starter prompt for the new chat

Open the new chat in the intended **Stage 4 workspace**, with read access to the Stage 3 checkout. Paste:

> Read `STAGE4_DEVELOPMENT_HANDOFF.md` in my `paper-reconstruction-stage3` checkout and the current contract/docs it references. This is the handoff from our completed Stage 3 alpha, software 0.9.32 / alpha 0.1.1. Inspect the current Stage 4 workspace before changing anything. I want Stage 4 as a separate project connected by immutable file artifacts, using only the independent contract SDK from Stage 3. Start implementing the first iteration in section 8: independent loader/CLI, documented legacy forest control, a separately identified partial/abstaining baseline with feasibility/support handling, a versioned output contract, diagnostics, layout preview and focused synthetic tests. Preserve the Stage 3 alpha, datasets, closed evaluation maps and existing CUDA environment. Summarize the first slice and assumptions briefly, then proceed with authorized implementation here. Do not train or launch full inference/benchmarks; give me the commands and I will run the long jobs. Reliable piece capacity is unknown: plan an independent 4/8-piece pilot, then 12/16/20, with 30 as the milestone. If historical/local files are unavailable, identify that limitation and continue from the published contract without inventing prior results.
