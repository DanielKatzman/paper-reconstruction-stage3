# Stage 3 v2 release validation

Validated 28 October 2026 against Stage 2 v1.0.2 and Stage 4 v2.0.5. This is an integration release of the qualified unit-scale-v5 core. The original 36 core source files, 8 SDK source/schema files, pooling implementation and 3 model/config files match the preserved 48-file inventory byte-for-byte. Model weights and numerical inference/search policies are unchanged.

## Local checks

- 31 tests pass: native/support/coordinate contracts, immutable publications, tamper/path rejection, frozen feature/model-score parity, independent CPU reader, release CPU defaults, pooled publication/resume and continuous shared-scale acquisition.
- `tools/verify_release.py` authenticates the release metadata and qualified inventory.
- Both the Stage 3 v2.0.0 wheel and SDK 0.1.0 wheel were built without dependency/environment replacement, extracted outside the source path, imported independently, and used to load JSON cache policy and both frozen rankers with CPU-only Torch 2.7.1+cpu.
- Windows/Linux CPU CI is configured. Local checks do not by themselves establish a passing Linux job; inspect the published workflow results.

## Fresh cross-stage CPU check

A fresh four-piece generator Stage 1 input was processed by production Stage 2 inference and its standalone verifier, then the released Stage 3 `prepare` interface, then cold Stage 4 v2.0.5. No saved rankings, native-pair caches or previous assembly were reused. No reference/evaluation files were supplied. SDK bytes were compared against the current consumer, and its actual implementation fingerprint matched `6000dccca2004995b02a6b76f21791e5a85b1daabfd235cb755be4761fb69c37`.

| Phase | Seconds |
| --- | ---: |
| Stage 2 CPU inference |11.38 |
| Stage 2 independent verification |0.97 |
| Stage 3 CPU native inference and pooling |139.88 |
| Stage 4 cold solve/assessment |6.84 |

The consumer produced one supported connected four-piece assembly. This establishes fresh interoperability, not new reconstruction reliability or thirty-piece throughput. Timings are a single workstation observation; they are not optimization claims. The exact generator-mask case does not independently qualify real-photo segmentation.

Receipts: [integration](../provenance/INTEGRATION_VALIDATION_2026-10-28.json), [installed wheels](../provenance/WHEEL_VALIDATION_2026-10-28.json), [qualified sources](../provenance/qualified_sources.json).

To repeat with compatible source checkouts and explicit interpreters:

```text
python -B tools/check_integration.py --stage2-source <stage2-v1.0.2> --stage4-source <stage4-v2.0.5> --stage2-python <stage2-python> --stage4-python <stage4-python> --stage1 <small-stage1-with-capture-profile> --output <new-check-directory>
```

Use the CPU-only Stage 3 interpreter for this command. The tool accepts no evaluation reference. Existing Stage 4 fourteen-page and six-piece real-capture results retain their original scope/receipts and were not rerun as new upstream qualifications here. Performance improvements, new coverage policies, model training, and automatic recovery-request handling are outside this release.
