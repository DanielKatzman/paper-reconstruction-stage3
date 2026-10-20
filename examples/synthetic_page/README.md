# Synthetic interoperability example

`input/stage1` and `input/stage2` are producer-shaped synthetic exports for one page. There are three physical pieces, two candidate-bearing observations and one zero-candidate piece. All images are generated white rectangles, not real documents. The short input is meant for interface/abstention tests.

`evidence` is the cleaned alpha's validated file handoff: 69 geometry groups, 134 source occurrences and a bounded 24-edge pool. Equal shapes and white content are ambiguous; this is not a solved-page example. The zero-candidate piece remains in its own candidate-graph component.

To read the precomputed handoff independently of Stage 3/torch:

```powershell
.\.venv\Scripts\python.exe examples\stage4_consumer.py examples\synthetic_page\evidence
```

To generate it afresh, use the inference command in the root README and a new output directory. Stage 4 must receive the whole completed evidence folder, including `assets/`.
