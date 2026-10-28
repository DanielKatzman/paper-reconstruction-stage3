> Historical alpha documentation. For the v2 release use README.md, compatibility.json and docs/ORCHESTRATOR.md.

# Stage 4 is a separate project

Stage 3 owns evidence generation. Stage 4 owns global assembly, layout selection and its own versioned output. The Stage 3 repository provides the outgoing file contract and an independent reader, not a complete Stage 4 service.

For a new chat, read the [Stage 4 development handoff](../STAGE4_DEVELOPMENT_HANDOFF.md). It records the frozen baseline, historical findings, local data/code locations, contract details and proposed first implementation/pilot, and includes a starter prompt.

## Install only the contract in Stage 4

From a checkout of this repository, install `contracts/stage3_to_stage4/v2/sdk` into Stage 4's environment. That is a separate Python distribution named `paper-reconstruction-contracts`. Its source imports no Stage 3 modules and requires no torch, models, datasets or databases.

```python
from paper_reconstruction_contracts import load_bundle, map_points, compose

data = load_bundle("/inputs/page_001", full=True)
entries = data.entries
working_edges = data.edges
for geometry in data.hypotheses():
    occurrences = geometry["occurrences"]
```

An implementation in another language may use the same JSON Schemas and documented coordinate/hash conventions instead. Shared contract libraries do not require shared service processes or a shared database.

## File orchestration

1. Stage 1 writes its accepted pieces and `segmentation_manifest.jsonl`.
2. Stage 2 writes the matching frozen `edge_hypotheses_manifest.json` and records.
3. Stage 3 reads those two directories and publishes a completed evidence directory.
4. Stage 4 receives that directory read-only, validates it and writes its own predictions to a different directory.

When containers are introduced, mount the same inputs read-only and a separate output path. The CLI already accepts paths explicitly. An HTTP wrapper is optional and must not change the artifact contract. GPU/CPU runtime and container profiling are still separate deployment work; no Docker runtime is claimed here.

## Start Stage 4 deliberately

Port the archived collision/cycle-aware forest as the first control in Stage 4's own repository. Keep its join-count-first objective identified as a baseline, preserve partial components and compare a separately declared abstention objective. Enforce complete homogeneous transforms, mask non-overlap, physical-piece uniqueness and support conflicts. Do not add a learned global scorer before the baseline's failure breakdown identifies a missing signal.

Publish immutable predictions before opening evaluation maps. Record component gauges, selected geometry/occurrence IDs, unresolved pieces, feasibility diagnostics, search truncation and runtime. Define Stage 4's output schema in its own project when implementing that producer; the normative contract here is **Stage 3 output / Stage 4 input**.

The synthetic example checks interoperability and coordinate handling. It does not establish real 4/8/20-piece reconstruction success.
