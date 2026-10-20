# Developing the alpha

Run `scripts/test.py` first. It checks the file boundary, native coordinate math, occurrence preservation, isolated pieces, tampering, relocation and exact observable tensors/frozen scores against the v0.9.31 synthetic control. Use the existing environment; no research database or training data is needed.

The inference entry point is `alpha_inference.infer`; the export is `alpha_bundle.export_bundle`. `models/alpha.json` declares the recipe and resource caps. Frozen checkpoint selection/context/tensor hashes are retained, while optimizer state is omitted. New training or policy selection is a separate experiment and must not silently overwrite these controls.

For ordinary source edits, use a new output path. The run identity includes the model/policy manifest, Stage 1/2 receipts and hashes of executable Stage 3/contract code and schemas. A changed implementation cannot reuse old ranking/pose caches. Completed bundles are immutable; the consumer reads them after `bundle.json` commits.

The alpha supports one native observation per physical piece. A zero-candidate piece remains in the inventory. Scores are uncalibrated. A finite search budget or a connected candidate graph does not establish solvability. The complete archive preserves every support/evidence occurrence; the solver pool is bounded separately.

The input producer validates the frozen Stage 2 ONNX identity, accepted Stage 1 provenance, file hashes and crop/source coordinate maps. It never opens a matching or label database. Stage 4 chooses consistent placements; Stage 3 does not solve global layouts.

The next measured step is an independent 4/8-piece assembly pilot, then 12/16/20 as justified. Register document families, inputs, solver budgets and the existing 4 px placement criterion before reading outcomes. Report whole-page success, false/missing joins, largest correct component, unplaced pieces, collisions, runtime and memory. Separate candidate availability, shortlist retention and global selection failures. Keep the 30-piece milestone and reliable capacity field distinct.

The original research tree is retained locally under `research_archive/v0.9.31`; generated experiments stay under ignored `generated/`. Its source release manifests and completed review provide historical replay evidence. Do not copy that history into the alpha's Git tree or use inspected development cases as independent capacity confirmation.
