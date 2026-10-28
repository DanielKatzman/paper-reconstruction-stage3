> Historical alpha documentation. For the v2 release use README.md, compatibility.json and docs/ORCHESTRATOR.md.

# Alpha cleanup inventory

## Keep in GitHub

- The observable Stage 3 runtime and its fixed neural architectures/geometry helpers: 30 Python modules, with research and training coordination removed.
- Two inference-only checkpoints: `pair_mlp_small.pt` and `paired_strip_cnn_small.pt`, 3,133,722 bytes combined. Their context IDs and tensor digests match the selected original checkpoints. Optimizer state is omitted; upstream checkpoint hashes remain in the model manifest.
- The sealed model/policy manifest, validated dependency constraints, short CLI/Windows/test scripts, current documentation and development plan.
- The independently installable Stage 3-to-Stage 4 contract SDK, normative JSON Schemas and a concrete hash test vector.
- A small synthetic Stage 1/2 input and matching evidence bundle, CPU Stage 4 example consumer, lean tests and synthetic v0.9.31 parity references. No real page imagery or real dataset is included.

## Retain locally, exclude from Git

| Local path | Reason |
| --- | --- |
| `research_archive/v0.9.31/` | Original source, old experiment scripts/tests/configurations, historical documents and release manifests; preserves the work leading to this alpha |
| `generated/` | Approximately 85.96 GiB and 1.41 million generated experiment/index/cache/checkpoint files in the audited project; old absolute evidence paths remain valid |
| `.venv/` | Existing 5.45 GiB Windows/CUDA environment; unchanged and reproducible through dependency metadata |
| `.idea/` | Local editor state |
| `outputs/`, `data/`, `datasets/`, `runs/` | Machine-local future inputs/results, not source dependencies |

This cleanup makes the active source and Git history small. **It does not delete the large research data from the disk.** No external Stage 1/2 dataset, original checkpoint or completed experiment is removed. Deleting the historical generated tree is a separate storage decision after any desired backup.

## Deliberately omitted from the active alpha

Old model screens, reranker training/selection, teacher/label construction, study-specific v0.9.x launchers, duplicate source snapshots, SQLite indexes, failed correction models, full training checkpoints/optimizer state and historical release/review bundles. None is needed for fresh production inference.

The old forest diagnostic also belongs to the local research history. Stage 4 can port that control into its own project, using the independently released file contract. Stage 3 does not take ownership of global assembly as part of this cleanup.

## Verification before publishing

The extraction is checked against the prior observable runtime, not accepted merely because imports succeed. `PARITY.json` records exact full-archive and working-pool equality on the synthetic production handoff. The test suite checks original observable tensors/frozen scores and independent contract loading. Both distributions build wheels without installing or downloading packages. File receipts and source preservation checks protect the local archive; the staged Git files are checked for private machine paths, credentials and unexpected large files.
