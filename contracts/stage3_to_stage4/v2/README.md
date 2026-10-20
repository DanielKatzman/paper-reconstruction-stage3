# Stage 3 → Stage 4 file contract v2

Status: released alpha input interface. Schema ID: `stage3.assembly-evidence.v2`. CPU reader distribution: `paper-reconstruction-contracts` 0.1.0. The solver itself is a separate project.

## Artifact layout and publication

```text
page_001/
  bundle.json
  working_pool.json
  hypotheses.jsonl.gz
  assets/<content-sha256>.png
  assets/<content-sha256>.npz
```

`bundle.json` is the publication barrier and is written last. Stage 4 must ignore an unfinished directory without that file, then fully verify it before solving. The producer may leave an `export_request.json` resume marker; it is not solver input. `*.tmp` files are never inputs. Do not edit a published bundle. Put Stage 4's outputs elsewhere.

All required assets are within the artifact. Paths use relative POSIX separators; absolute paths, drive letters, traversal and symlink escapes are rejected. Moving the complete folder does not require the original Stage 1/2 dataset or machine paths. Preserve artifact bytes exactly, including JSON/JSONL line endings; the repository's `.gitattributes` prevents checkout conversion from breaking file receipts.

## Normative schemas

The shipped files in [sdk/src/paper_reconstruction_contracts/schemas](sdk/src/paper_reconstruction_contracts/schemas) are JSON Schema Draft 2020-12:

- `bundle.schema.json`: inventories, file receipts, identity, policy and coordinate/provenance metadata.
- `working_pool.schema.json`: bounded search edges and per-pair truncation counts.
- `hypothesis.schema.json`: one archived geometry group with all exact support/evidence occurrences.

Unknown schema versions must fail explicitly. Breaking field/frame/score semantics require a new schema version. The reference SDK validates schemas offline and checks cross-file identities, counts, candidate ownership, transforms and native assets. Consumers in other languages must implement equivalent semantic checks, not only JSON syntax validation.

## Coordinates and identity

Physical IDs identify pieces within one page; observation IDs identify native captures. This alpha requires one registered observation per physical piece. Preserve isolated and zero-candidate pieces. The candidate array order is authoritative for legacy `pose.query`/`pose.target` indices; stable candidate keys and observation/physical IDs are also retained.

Coordinates are native cropped-image pixels, origin top-left, x right, y down. Canonical pairs have `piece_a < piece_b` using Unicode code-point order. A homogeneous matrix `H_b_to_a` maps **piece B into piece A**:

```text
[u, v, w]^T = H_b_to_a [x_b, y_b, 1]^T
(x_a, y_a) = (u/w, v/w)
H_c_to_a = H_b_to_a @ H_c_to_b
H_a_to_b = inverse(H_b_to_a)
```

Matrices can be proper similarity or guarded projective transforms. Never drop the last row. The SDK's `map_points` performs homogeneous division; `compose` follows the order above. Each occurrence retains the original query/target direction, source matrix, spans, window IDs and overlap fractions. Support endpoints/fractions name that occurrence's native candidate, not another grouped occurrence.

## Complete archive and bounded search pool

`hypotheses.jsonl.gz` has one exact normalized transform group per line. Grouping never rounds a matrix and never replaces distinct occurrence support. An occurrence ID includes variant, original row position and record ID, so duplicate record aliases remain separate. Method metadata, learned/visual/geometric evidence and explicit abstention flags stay attached to their occurrences.

`working_pool.json` contains at most the declared cap (default 24) per physical pair, with links to the complete archive and a representative occurrence. It is a resource-limited portfolio, not proof that a correct pose exists or that the search exhausted every possibility. Per-pair available/retained counts and truncation are explicit. Stage 4 may inspect the archive under its own declared budget.

Weights are **uncalibrated heuristic evidence**, with method/branch scope preserved. Correlated variants are provenance and must not be summed as independent votes. The historical method name `reference` denotes an observable baseline, not a teacher-fitted pose. Missing RGB support can explicitly abstain; it is not fabricated zero-error evidence. Graph connectivity is not assembly correctness.

## Observable data and integrity

NPZ loading uses `allow_pickle=False`. Per-observation arrays are restricted to `points_xy`, `arc_length_px`, `tangent_xy`, `inward_normal_xy`, `curvature_per_px`, `corner_strength`, `inward_thickness_px`, `role_probabilities` and `transition_probabilities`. Raw boundary archives, labels, saved reference anchors and teacher transforms are forbidden. Metadata must keep protected/evaluation-open flags false.

Receipts store byte length and SHA-256 for assets, archive and working pool. `manifest_sha256` hashes the manifest without that field, using UTF-8 JSON with sorted keys, compact separators, ASCII escaping for non-ASCII characters (`ensure_ascii=True`), and nonfinite numbers forbidden. Geometry/occurrence IDs use the same canonical JSON digest rule. SHA-256 values are lowercase hex. The SDK is the reference for this legacy canonicalization; `hash_test_vector.json` gives concrete bytes and a digest. Preserve original numeric values and their Python JSON float encoding when re-encoding in another language.

The alpha correction scorer is disabled. Reliable solved-piece capacity is null. These fields cannot be interpreted as a calibrated confidence or a demonstrated 20-piece success rate.

## Independent reader and errors

```text
python -m pip install ./contracts/stage3_to_stage4/v2/sdk
```

```python
from paper_reconstruction_contracts import load_bundle
data = load_bundle("path/to/page_001", full=True)
print(data.summary())
```

Stage 4 needs only this SDK and its numpy/Pillow/jsonschema dependencies. No Stage 3 installation or torch import is required. The example consumer demonstrates this in a separate process.

Producer CLI exit codes: 0 for success, 2 for invalid input/runtime failure, 130 for interruption. Failed/interrupted work does not publish a ready manifest; repeat the identical command to resume. The reader raises `ContractError` for an invalid contract/integrity condition; malformed files are errors and must not be treated as empty evidence. Stage 4 owns its own failure/output protocol.
