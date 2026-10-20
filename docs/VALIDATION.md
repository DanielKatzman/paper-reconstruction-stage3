# Alpha cleanup validation — v0.9.32

This is a packaging/runtime extraction of the v0.9.31 frozen-core recipe. It does not change the selected model tensors, launch real inference/assembly experiments or establish a solved-piece capacity.

## Passed checks

- **21/21 lean-repository tests**, including frozen model/tensor parity, complete occurrence support/evidence, reverse direction, isolated/zero-candidate pieces, interrupted/immutable exports, relocation, asset tampering, path escape, schema/closed-truth rejection and projective composition/division.
- The original v0.9.31 and cleaned runtime produce **exactly equal complete prediction archives and working pools** on the same synthetic production handoff: 69 geometry groups, 134 occurrences, 24 working edges. Both runs use the existing CUDA environment. See `PARITY.json` for archive/pool hashes and scope.
- Synthetic observable model inputs are array-equal to the original runtime. CPU frozen pair scores agree to six decimal places; the CUDA run also passes the existing first-batch CPU/CUDA parity checks.
- Two original checkpoint contexts/tensor digests are preserved in inference-only artifacts. Removing optimizer state reduces the combined model files from 11,774,296 to **3,133,722 bytes**. No weights are trained or selected during cleanup.
- The contract reader imports independently of Stage 3 and torch. The example Stage 4 process validates the complete synthetic bundle without Stage 3/model/data dependencies.
- Stage 3 and the contract SDK both build wheels with `--no-index --no-deps --no-build-isolation`. No package is installed, upgraded or downloaded during validation. The SDK wheel includes all three schemas and has no Stage 3/torch dependency.
- A staging scan finds no private machine paths or credential strings in source/docs/examples and no unexpected large source files. Real documents and datasets are excluded.

## Commands

```powershell
.\.venv\Scripts\python.exe scripts\test.py
.\.venv\Scripts\python.exe scripts\stage3.py verify
.\.venv\Scripts\python.exe examples\stage4_consumer.py examples\synthetic_page\evidence
```

The validated Windows environment is Python 3.12, NumPy 2.5.3, Pillow 12.3.0, Torch 2.7.1+cu118, threadpoolctl 3.7.0 and jsonschema 4.26.0. The existing environment is retained.

## Limits

The synthetic fixture proves preservation/interoperability, not real reconstruction accuracy. Stage 4 is still a separate solver project to implement and benchmark. The real 4/8-piece pilot and subsequent 12/16/20 progression remain future work. General CPU throughput and Docker runtime have not been profiled.

The old broad research suite is archived rather than folded into the alpha tests. Its Windows SQLite-fixture cleanup errors reproduce on the original v0.9.30 control, as documented in the local v0.9.31 review; no old scientific source/test is edited to hide them. The active runtime no longer depends on those research databases/coordinators.
