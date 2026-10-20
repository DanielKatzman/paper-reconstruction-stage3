# Paper reconstruction — Stage 3 alpha

Stage 3 turns a page's accepted Stage 1 pieces and frozen Stage 2 boundary predictions into observable neighbor/pose alternatives for a **separate Stage 4 assembly project**. The handoff is a portable folder of JSON, compressed JSONL, PNG and NPZ files. There is no HTTP service or shared database requirement.

This is alpha **0.1.1**, software **0.9.32**. It preserves the v0.9.31 frozen-core inference recipe while removing research orchestration, dataset dependencies and optimizer state. It contains two frozen models, the runtime, an independently installable contract SDK, tests and a synthetic example. Experimental correction scoring is disabled. Reliable solved-piece capacity is unknown; 20 pieces is the baseline target and 30 the milestone.

## Use the existing Windows environment

From the project root:

```powershell
.\scripts\run_stage3_windows.cmd
```

With no arguments this checks the packaged models and policy. It does not train, reconstruct a page or read a dataset. The existing GTX 1070 environment uses Torch 2.7.1+cu118 and is preserved.

Run the small synthetic example through Stage 3:

```powershell
.\scripts\run_stage3_windows.cmd infer --stage1 examples\synthetic_page\input\stage1 --stage2 examples\synthetic_page\input\stage2 --output outputs\synthetic_page --device cuda --puzzle-id synthetic_page
```

For a real page, replace the two input directories with matching Stage 1/2 exports and use a new output directory. `--device cpu` is explicit; CUDA never silently falls back. Repeating an identical interrupted command reuses committed rankings and physical-pair caches. Source/policy/code changes require a new output directory. New runs report the source and implementation identities.

Inspect the result:

```powershell
.\.venv\Scripts\python.exe scripts\stage3.py inspect --bundle outputs\synthetic_page
```

## Stage 4 boundary

The complete input contract, schemas and independent reader are in [contracts/stage3_to_stage4/v2](contracts/stage3_to_stage4/v2/README.md). Stage 4 receives only the completed evidence folder. It needs numpy, Pillow and jsonschema; it does not import Stage 3 or torch.

```powershell
.\.venv\Scripts\python.exe examples\stage4_consumer.py examples\synthetic_page\evidence
```

This validates and reads the handoff. A full Stage 4 solver is **not** implemented in this repository. The earlier forest control remains in the local research archive. [Stage 4 integration](docs/STAGE4_INTEGRATION.md) specifies how to start its separate project.

## Fresh clone and tests

Use Python 3.12. Create a virtual environment and install `requirements.txt`; it installs the local contract SDK and Stage 3 package. `constraints.txt` records the tested library versions. Install a suitable Torch build for the machine; keep the existing CUDA build when continuing on the GTX 1070.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts\test.py
```

The checkout scripts also work directly with an already compatible environment. See [validation](docs/VALIDATION.md), [development](docs/DEVELOPMENT.md) and [cleanup inventory](docs/CLEANUP_INVENTORY.md).

## Repository contents

| Path | Purpose |
| --- | --- |
| `src/paper_reconstruction_stage3/` | Observable inference, frozen architectures, geometry and export |
| `models/` | Two inference-only checkpoints and sealed policy/model identities |
| `contracts/stage3_to_stage4/v2/` | Versioned file contract, JSON Schemas and independent CPU SDK |
| `scripts/` | CLI, Windows launcher and test runner |
| `examples/` | Synthetic Stage 1/2 input, matching evidence and independent Stage 4 reader |
| `tests/` | Contract/geometry/export tests and v0.9.31 synthetic parity references |

Large experiments, datasets, caches, environments and the local research archive are excluded from Git. They are not needed to run or develop this alpha.
