# Stage 3 v2 development

The public release is2.0.0. The preserved qualified core remains unit-scale-v5/software0.9.32 with unchanged weights, search, ranking and pooling policy. Use the CPU-default interface in `paper_reconstruction_stage3_release`; original core entry points retain historical implementation details for provenance.

Start with `README.md`, `compatibility.json`, `docs/ORCHESTRATOR.md`, and `provenance/qualified_sources.json`. Run `python -B tools/verify_release.py` and `python -B scripts/test.py`. Source JSON package data is required in wheels; the SDK installs independently. CI covers Windows/Linux Python 3.12 and CPU Torch.

Do not edit frozen inventories or model manifests to disguise an algorithm change. Qualified-core/model/pooling changes require new provenance and downstream checks. Keep execution optimizations separate from retrieval/pose coverage experiments. Do not mutate old outputs or use evaluation references in serving code.

The speed research, broader candidate coverage, recovery-request consumption, ONNX ranker export and container/API orchestration are future work, not part of the v2 integration release. The application repository owns image composition and durable jobs; stage repositories remain independently maintained.
