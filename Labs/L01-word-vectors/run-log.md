## run_id 20260610T080902Z__t_a3b87099__one-hot-vs-dense

task_id: t_a3b87099
capsule_slug: one-hot-vs-dense
timestamp: 2026-06-10T08:09:02Z
hostname: 0d61b5cf12fa
command: /workspace/cs224n-study/.venv/bin/python Labs/L01-word-vectors/one-hot-vs-dense.py
exit_code: 0
stdout: Labs/L01-word-vectors/outputs/one-hot-vs-dense-stdout.txt
stderr: Labs/L01-word-vectors/outputs/one-hot-vs-dense-stderr.txt (empty — no errors, no warnings)
outputs:
  - Labs/L01-word-vectors/outputs/one-hot-vs-dense-comparison.png
  - Labs/L01-word-vectors/outputs/one-hot-vs-dense-results.json
  - Labs/L01-word-vectors/outputs/one-hot-vs-dense-stdout.txt
notebook: Labs/L01-word-vectors/one-hot-vs-dense.ipynb
notes: Script ran cleanly with no errors. Uses numpy+matplotlib (pre-installed in Colab). No cells skipped. No cache used.

## run_id 20260610T080907Z__t_832bffea__skipgram-softmax

task_id: t_832bffea
capsule_slug: skipgram-softmax
timestamp: 2026-06-10T08:09:07Z
hostname: 0d61b5cf12fa
command: .venv/bin/python Labs/L01-word-vectors/skipgram-softmax.py
exit_code: 0
stdout: Labs/L01-word-vectors/outputs/skipgram-softmax-stdout.txt
stderr: Labs/L01-word-vectors/outputs/skipgram-softmax-stderr.txt (empty — no errors)
outputs:
  - Labs/L01-word-vectors/outputs/skipgram-softmax-prob-distribution.png
  - Labs/L01-word-vectors/outputs/skipgram-softmax-three-steps.png
  - Labs/L01-word-vectors/outputs/skipgram-softmax-computation-cost.png
  - Labs/L01-word-vectors/outputs/skipgram-softmax-output.json
notebook: Labs/L01-word-vectors/skipgram-softmax.ipynb
notes: |
  Script ran cleanly with exit code 0. No errors or warnings.
  numpy seed=42 for reproducibility. Mini vocabulary of 6 words, d=4.
  All three plots generated successfully.
  Key output values: P(money|banking)=0.251396, P(river|banking)=0.091563, ratio=2.75x.
  Partition function Z=10.388761 for center word 'banking'.


## run_id 20260610T081059Z__t_64256cc7__co-occurrence-matrix

task_id: t_64256cc7
capsule_slug: co-occurrence-matrix
timestamp: 2026-06-10T08:10:59Z
hostname: 0d61b5cf12fa
environment: Python 3.13.5, venv /workspace/cs224n-study/.venv, numpy 2.4.6, matplotlib 3.10.9, scipy 1.17.1
command: .venv/bin/python Labs/L01-word-vectors/co-occurrence-matrix.py
workdir: /workspace/cs224n-study
exit_code: 0
stderr: Labs/L01-word-vectors/outputs/co-occurrence-matrix-stderr.txt (empty — no errors)
stdout: Labs/L01-word-vectors/outputs/co-occurrence-matrix-stdout.txt
outputs:
  - Labs/L01-word-vectors/outputs/co-occurrence-matrix-heatmap.png (105431 bytes)
  - Labs/L01-word-vectors/outputs/co-occurrence-matrix-2d-embeddings.png (90590 bytes)
  - Labs/L01-word-vectors/outputs/co-occurrence-matrix-window-comparison.png (105025 bytes)
  - Labs/L01-word-vectors/outputs/co-occurrence-matrix-svd-coordinates.json (2094 bytes)
notebook: Labs/L01-word-vectors/co-occurrence-matrix.ipynb
notes: |
  No errors. Script ran once, all cells executed.
  Corpus: 14 sentences (6 finance + 6 nature + 2 bridge), 15 words vocabulary.
  Window size = 2 (default), compared with 1, 2, 4.
  Matrix: 15×15, 64.4% sparse, 140 total co-occurrence count.
  SVD k=2 explained variance: 75.3%.
  Within-cluster cosine mean: 0.9932, cross-cluster: 0.1508 — clear separation.
  No cells skipped. No cache used.
