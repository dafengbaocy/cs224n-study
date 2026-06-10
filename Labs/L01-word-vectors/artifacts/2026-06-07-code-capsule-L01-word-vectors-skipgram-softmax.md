# Execution Report: Code Capsule skipgram-softmax (WP03)

- **task_id**: t_9a2158c5
- **parent**: t_2daaf65b
- **capsule_slug**: skipgram-softmax
- **waypoint**: WP03 — Word2Vec / Skip-gram / Softmax
- **concept**: Skip-gram softmax 概率计算 P(o|c)
- **status**: review-required
- **ready_for_review**: true
- **downstream_allowed**: false

## Changed files

| File | Action | Notes |
|---|---|---|
| `Labs/L01-word-vectors/skipgram-softmax.py` | write | Main script: Part A (random) + Part B (trained) + Part C (comparison) |
| `Labs/L01-word-vectors/skipgram-softmax.ipynb` | write | 14-cell notebook with Chinese teaching content |
| `Labs/L01-word-vectors/_gen_skipgram_softmax_notebook.py` | write | Notebook generator script |
| `Labs/L01-word-vectors/outputs/skipgram-softmax-stdout.txt` | write | Full stdout from run |
| `Labs/L01-word-vectors/outputs/skipgram-softmax-stderr.txt` | write | Empty (no errors) |
| `Labs/L01-word-vectors/outputs/skipgram-softmax-results.json` | write | Structured numeric results |
| `Labs/L01-word-vectors/outputs/skipgram-softmax-probability-bar.png` | write+upload | Trained probability bar chart |
| `Labs/L01-word-vectors/outputs/skipgram-softmax-dotscore-vs-prob.png` | write+upload | Dot score vs probability comparison |
| `Labs/L01-word-vectors/outputs/skipgram-softmax-random-vs-trained.png` | write+upload | Random vs trained comparison |
| `Labs/L01-word-vectors/run-log.md` | append (flock) | Run entry with run_id 20260610T094936Z__t_9a2158c5__skipgram-softmax |
| `Lectures/L01-word-vectors/code-capsules/skipgram-softmax.md` | write | Capsule partial with Colab link |
| `Lectures/L01-word-vectors/media-registry/code-capsule-skipgram-softmax.json` | write | 3 items, all uploaded |

## Capsule concept

This capsule demonstrates the Skip-gram softmax probability computation P(o|c):
- Part A: Random initialization → uniform probabilities (~0.125 each)
- Part B: Hand-designed "trained" vectors → semantic clustering (finance vs river)
- Part C: Side-by-side comparison showing the effect of training

## Real output summary

- Vocabulary: 8 words (banking, money, river, bank, stream, credit, loan, water)
- Embedding dim: 4
- Random init max/min ratio: 1.05x
- Trained max/min ratio: 2.72x
- Top trained prob: P(banking|banking) = 0.194811
- Bottom trained prob: P(water|banking) = 0.071667
- Sum check: 1.0000000000 for both parts

## Colab link

https://colab.research.google.com/github/dafengbaocy/cs224n-study/blob/main/L01-word-vectors/skipgram-softmax.ipynb

Verified: HTTP 200

## Image uploads

| Image | URL | Status |
|---|---|---|
| probability-bar | https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-174352.png | uploaded (2 attempts: MCP SSL fail → CLI ok) |
| dotscore-vs-prob | https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-174401.png | uploaded (1 attempt) |
| random-vs-trained | https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-174404.png | uploaded (1 attempt) |

## Notebook Chinese teaching checklist

- [x] 这段代码在看什么
- [x] 运行后先看哪里
- [x] 输出怎么解释
- [x] 和本讲哪个 waypoint 对应
- [x] 容易误解的地方
- [x] All Markdown cells in Chinese (with English terms annotated)
- [x] Code comments in Chinese where learner-facing

## Self-check results

- [x] Capsule partial exists at `Lectures/L01-word-vectors/code-capsules/skipgram-softmax.md`
- [x] Heading: `## skipgram-softmax — Skip-gram Softmax 概率计算 P(o|c) {#skipgram-softmax}`
- [x] .py, .ipynb, stdout, outputs, run-log, Colab link all present
- [x] Run-log has unique section with task_id, capsule_slug, run_id, command, exit_code, stdout, outputs
- [x] Key numeric values in partial match stdout (verified via numeric_provenance block)
- [x] Glossary links use vault-root paths: `[[Lectures/L01-word-vectors/00-concept-glossary#...|...]]`
- [x] All glossary headings exist in seed (dot-product, softmax, skip-gram, sgd, negative-sampling)
- [x] No modification to `04-code-capsules.md` or other capsule partials
- [x] No short wikilinks across directories
- [x] All images use remote_url, no local paths in partial
- [x] Media registry uses top-level `items` schema

## Integration risks

None detected. No other capsule partials were modified or found missing.

## Requested glossary terms

None — all needed terms (dot-product, softmax, skip-gram, sgd, negative-sampling) already exist in glossary seed.
