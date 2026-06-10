# L01 Word Vectors — Readings Map

> Reading Triage for CS224N Winter 2025, Lecture 1: Introduction and Word Vectors.
> 本文件只做 readings map：把官方 schedule / slides / notes / assignment 里出现的 readings 分层，把 core readings 映射到 waypoint 概念锚点，并为下游 Paper Tutor / Code Capsules / DeepResearch / Lecture Weaver 提供唯一配置来源。
> 禁止在本阶段写 paper note、改 `00-课堂入口.md`、跑代码或执行 DeepResearch。

## Official anchors read

| Source | Evidence path | Key content used for triage |
|---|---|---|
| Schedule row | `recovered/evidence/l01/l01-schedule-row.txt` | Week 1 Tue Jan 7 Word Vectors；Suggested Readings 明确列出 "Efficient Estimation…"（original word2vec paper）和 "Distributed Representations…"（negative sampling paper）；Assignment 1 out |
| Slides PDF (36 pages) | `recovered/assets/official/l01/cs224n-2025-lecture01-wordvecs1.pdf`; extracted text `recovered/evidence/l01/slides-extracted-text.txt` | p1-p15：course intro / lecture plan / NLP applications；p16-p23：word meaning / WordNet / one-hot / distributional semantics / dense vectors；p24-p30：Word2Vec skip-gram、center/context、two vectors、softmax；p31-p35：loss optimization、GD/SGD；p9 lecture plan item 6 "Looking at word vectors (10 mins or less)" 但 slides 无对应正文内容 |
| Notes PDF (13 pages) | `recovered/assets/official/l01/cs224n-2025-lecture01-notes.pdf`; extracted text `recovered/evidence/l01/notes-extracted-text.txt` | §1：NLP intro / motivation；§2：signifier/signified、one-hot、WordNet/UniMorph contrast；§3.1：co-occurrence and GloVe；§3.2：skipgram model and Eq.4-Eq.5；§3.3-3.4：empirical loss and gradient；§3.5：negative sampling；Appendix A.1 CBOW / A.2 SVD (headings only) |
| A1 notebook | `recovered/evidence/l01/a1-notebook-extracted-text.txt` | Part 1：co-occurrence matrix + SVD；Part 2：GloVe, cosine similarity, analogies, bias exploration |
| Canonical lock | `Sources/readings-canonical-lock.yaml` | Canonical URLs, PDF URLs, local evidence, URL probe paths and source role decisions |

Schedule row exact reading evidence:

```text
Week 1 Tue Jan 7 Word Vectors [ slides ] [ notes ] Suggested Readings: Efficient Estimation of Word Representations in Vector Space (original word2vec paper) Distributed Representations of Words and Phrases and their Compositionality (negative sampling paper) Assignment 1 out [ code ]
```

## Waypoints

| WP | Title | One-sentence concept | Official anchor | est. time |
|---|---|---|---|---|
| WP01 | Course Intro & NLP Landscape | 先知道 CS224N 要解决什么 NLP 问题，以及为什么"表示"是这门课的入口。 | slides p1-p15; notes §1 | 10 min |
| WP02 | One-hot vs Dense Vectors | 从离散符号和 one-hot 的正交问题，走到 distributional semantics 与 dense vector 的动机。 | slides p16-p23; notes §2.1-§3.1; A1 Part 1 | 15 min |
| WP03 | Word2Vec / Skip-gram / Softmax | 用 center word 预测 context word：每个词两套向量，点积打分，再经 softmax 得到概率。 | slides p24-p30; notes §3.2 Eq.4-Eq.5 | 15 min |
| WP04 | Objective / Gradients / Negative Sampling | 把 Word2Vec 写成经验损失并用 SGD 训练；理解 full softmax 梯度与 negative sampling 的效率替代。 | slides p31-p35; notes §3.3-§3.5 Eq.6-Eq.15; R02 | 25 min |
| WP05 | Pretrained Vectors / Analogy / Visualization | 用 A1 里的 GloVe / analogy / visualization 把"学到的向量空间"变成可观察对象。 | slides p9 plan item "Looking at word vectors"; A1 Part 2; R02 compositionality examples | 10 min |

## Reading roles

| role | id | reading | why this role / evidence |
|---|---|---|---|
| **core** | L01-R01 | Mikolov et al. 2013, "Efficient Estimation of Word Representations in Vector Space" | Schedule row explicitly labels it "original word2vec paper"；slides p24 cite Mikolov et al. 2013 for Word2Vec / Skip-gram；notes references lines 813-814 cite CoRR abs/1301.3781；core for WP03-WP04. |
| **core** | L01-R02 | Mikolov et al. 2013, "Distributed Representations of Words and Phrases and their Compositionality" | Schedule row explicitly labels it "negative sampling paper"；notes §3.5 introduces SGNS as replacement for the expensive softmax partition function；A1 Part 2 asks vector relationship questions that align with the compositionality/analogy part；core for WP04-WP05. |
| support | L01-R03 | Pennington et al. 2014, "GloVe: Global Vectors for Word Representation" | Notes §3.1 cites GloVe as a co-occurrence-based method comparable to word2vec；A1 Part 2 links the Stanford GloVe PDF and loads GloVe vectors；support for WP02/WP05 and assignment bridge, not schedule-core. |
| support | L01-R04 | Rong 2014, "word2vec Parameter Learning Explained" | Notes references lines 817-818 cite it；useful support for WP04 gradient intuition, but not a schedule suggested reading. |
| support | L01-R05 | Firth 1957, "Applications of General Linguistics" | Notes §3 cites "You shall know a word by the company it keeps"；A1 cell 3 repeats the quote；canonical primary URL remains unresolved in lock file, so use as conceptual support with caveat. |
| optional | L01-R06 | Miller 1995, "WordNet: A Lexical Database for English" | Notes §2.3 cites WordNet as annotated semantic relation resource；only needed as contrast against learned dense representations. |
| optional | L01-R07 | Batsuren et al. 2022, "UniMorph 4.0" | Notes §2.3 cites UniMorph for morphology annotation；background only. |
| optional | L01-R08 | Manning 2022, "Human Language Understanding & Reasoning" | Notes §1.1 cites it for language/intelligence motivation；course framing only. |
| optional | L01-R09 | Bengio et al. 2003, "A Neural Probabilistic Language Model" | Notes references lines 804-805；historical neural LM background. |
| optional | L01-R10 | Collobert et al. 2011, "Natural Language Processing (Almost) from Scratch" | Notes references lines 806-808；historical neural NLP background. |
| optional | L01-R11 | Baum & Petrie 1966 | Notes references lines 801-803；extra probabilistic modeling background; no direct L01 waypoint anchor. |
| optional | L01-R12 | Rumelhart et al. 1986/1988, "Learning representations by back-propagating errors" | Notes references lines 819-820；optimization/backprop historical background only. |

## Configuration Fields (YAML)

### core_readings

```yaml
core_readings:
  - slug: L01-R01
    title: "Efficient Estimation of Word Representations in Vector Space"
    role: core
    canonical_url: "https://arxiv.org/abs/1301.3781"
    paper_url: "https://arxiv.org/pdf/1301.3781"
    local_pdf: "recovered/assets/papers/l01/L01-R01-mikolov-efficient-estimation-1301.3781.pdf"
    official_anchor: "Schedule row (original word2vec paper); slides p24-p30; notes §3.2-§3.4; notes references lines 813-814"
    waypoint_focus: [WP03, WP04]
    paper_tutor_focus: "Skip-gram/CBOW setup, center/context prediction, two vector matrices, softmax objective, and how the original word2vec paper maps onto slides p24-p35 and notes §3.2-§3.4"
  - slug: L01-R02
    title: "Distributed Representations of Words and Phrases and their Compositionality"
    role: core
    canonical_url: "https://papers.nips.cc/paper_files/paper/2013/hash/9aa42b31882ec039965f3c4923ce901b-Abstract.html"
    paper_url: "https://papers.nips.cc/paper_files/paper/2013/file/9aa42b31882ec039965f3c4923ce901b-Paper.pdf"
    local_pdf: "recovered/assets/papers/l01/L01-R02-mikolov-distributed-representations-neurips2013.pdf"
    official_anchor: "Schedule row (negative sampling paper); notes §3.5 Eq.14-Eq.15; A1 Part 2 vector relationship exploration"
    waypoint_focus: [WP04, WP05]
    paper_tutor_focus: "Negative sampling mechanism, full-softmax efficiency bridge, p_neg/noise distribution context, phrase/compositionality evidence, and analogy/vector-space relationship examples"
```

### code_capsules

```yaml
code_capsules:
  - slug: one-hot-vs-dense
    waypoint: WP02
    concept: "One-hot orthogonality vs dense similarity"
    why_not_text: "Students need to see numerically that one-hot vectors make unrelated and semantically related words equally dissimilar (off-diagonal dot products are 0), while dense toy embeddings can give similar words larger similarity."
    official_anchor: "slides p19-p20 (one-hot and orthogonality problem); slides p22-p23 (dense vectors and dot product similarity); notes §2.2 Eq.1-Eq.2"
    expected_output:
      - "Table comparing one-hot dot products with dense cosine/dot similarities"
      - "Heatmap showing one-hot similarity vs toy dense similarity"
  - slug: cooccurrence-svd-mini
    waypoint: WP02
    concept: "Co-occurrence matrix and low-dimensional projection"
    why_not_text: "A1 Part 1 asks students to build co-occurrence vectors and apply SVD; a tiny runnable example makes the count matrix, sparsity, and dimensionality reduction visible before assignment work."
    official_anchor: "notes §3.1 (co-occurrence matrix construction and window size); A1 Part 1 cells on co-occurrence matrix and SVD"
    expected_output:
      - "Toy co-occurrence matrix for a 2-sentence corpus"
      - "2D SVD coordinates table and scatter plot"
  - slug: softmax-probability
    waypoint: WP03
    concept: "Softmax probability computation"
    why_not_text: "The denominator over the whole vocabulary is easy to gloss over in formulas; running it on a tiny vocabulary shows dot product scores, exponentials, normalization, and probability mass."
    official_anchor: "slides p28-p30 (P(o|c)=exp(u_o^T v_c)/sum exp(u_w^T v_c)); notes §3.2 Eq.4-Eq.5"
    expected_output:
      - "Table: candidate outside word, dot score, exp(score), normalized probability"
      - "Bar chart of P(o|c) over a tiny vocabulary"
  - slug: skip-gram-shapes
    waypoint: WP03
    concept: "Skip-gram data flow: center/context pairs and U/V matrix shapes"
    why_not_text: "Students often mix up center vectors v_w, context vectors u_w, and matrix shapes. Printing pairs and dimensions forces the notation to line up with code."
    official_anchor: "slides p25-p26 (window example); slides p28 (two vectors per word); notes §3.2 (U,V in R^{|V| x d})"
    expected_output:
      - "List of center-context training pairs from a toy corpus with window=2"
      - "Shape table for vocabulary size, embedding dimension, U, V, scores, and probability vector"
  - slug: negative-sampling-demo
    waypoint: WP04
    concept: "Negative sampling vs full softmax"
    why_not_text: "Full softmax pushes down every vocabulary item, while SGNS samples k negatives. A toy comparison makes the computational and gradient-direction difference concrete."
    official_anchor: "notes §3.5 Eq.14-Eq.15 (softmax partition function and SGNS); slides p35 (SGD cost motivation); R02 negative sampling paper"
    expected_output:
      - "Cost comparison table: full softmax O(|V|) vs SGNS O(k)"
      - "Toy positive/negative sample table and binary logistic losses"
      - "Gradient-direction sketch showing positive pair pulled closer and negative pairs pushed apart"
  - slug: pretrained-analogy
    waypoint: WP05
    concept: "Pretrained word vectors, cosine similarity, and analogies"
    why_not_text: "Analogy claims such as king - man + woman ≈ queen are not trustworthy as prose alone; they need real nearest-neighbor queries and visible failure cases."
    official_anchor: "A1 Part 2 (GloVe vectors, cosine similarity, analogy and bias questions); slides p9 plan item 'Looking at word vectors'; R02 compositionality examples"
    expected_output:
      - "Nearest-neighbor table for several analogy queries plus at least one failure/bias case"
      - "Cosine similarity heatmap for selected word pairs"
      - "2D PCA/t-SNE visualization with caveat about projection artifacts"
```

### deepresearch_waypoints

```yaml
deepresearch_waypoints:
  - waypoint: WP01
    title: "Course Intro & NLP Landscape"
    needs_deepresearch: false
    official_anchor: "slides p1-p15; notes §1"
    research_question: ""
    reason: "Official materials are sufficient. Slides p1-p15 cover course logistics, lecture plan, NLP applications (MT, QA, sentiment), and motivation. Notes §1.1-§1.3 cover human language, machines, and NLP uses. This is introductory framing with no formulas, no concept jumps, and no external-paper dependency. Students can proceed without supplemental research."
  - waypoint: WP02
    title: "One-hot vs Dense Vectors"
    needs_deepresearch: false
    official_anchor: "slides p16-p23; notes §2.1-§3.1; A1 Part 1"
    research_question: ""
    reason: "Official materials are sufficient at L01 depth. Slides p19-p20 explicitly show one-hot vectors and the orthogonality/no-similarity problem; slides p21-p23 introduce distributional semantics and dense vectors with dot-product similarity. Notes §2.2 gives the mathematical one-hot dot-product argument, §2.3 explains why WordNet/annotated feature resources are incomplete, and §3.1 gives a concrete co-occurrence matrix construction plus window-size intuition. A1 Part 1 then operationalizes co-occurrence and SVD. No formula black box or external-paper handoff is required for this waypoint."
  - waypoint: WP03
    title: "Word2Vec / Skip-gram / Softmax"
    needs_deepresearch: false
    official_anchor: "slides p24-p30; notes §3.2 Eq.4-Eq.5"
    research_question: ""
    reason: "Official materials are sufficient at L01 depth. Slides p24-p30 walk through Word2Vec: corpus positions, center word, outside/context words, two vectors per word, dot products, exponentiation, and normalization over the vocabulary. Notes §3.2 formalizes the same model with random variables C/O and matrices U,V in R^{|V| x d}, then states the cross-entropy objective. The softmax probability computation itself is decomposed on slide p30, so there is no concept jump that requires DeepResearch before downstream teaching."
  - waypoint: WP04
    title: "Objective / Gradients / Negative Sampling"
    needs_deepresearch: true
    official_anchor: "slides p31-p35; notes §3.3-§3.5 Eq.6-Eq.15; R02 negative sampling paper"
    research_question: "How does the observed-minus-expected gradient update connect to efficient word2vec training, why does SGNS use a logistic objective with sampled negatives rather than a simple full-softmax denominator approximation, and how should p_neg/noise distribution choices be explained to students?"
    reason: "The objective and gradient pieces are partly covered: notes §3.3-Eq.6 turns the expectation into an empirical corpus/window loss; notes §3.4-Eq.9-Eq.13 derives the gradient and gives the observed-minus-expected intuition; slides p31-p35 introduce GD/SGD. But negative sampling remains under-explained. Slides do not mention negative sampling at all; notes §3.5 states that the partition function pushes down all other words and that SGNS samples k negatives, but it explicitly says p_neg is undefined ('a distribution we haven't defined, called p_neg. Think of this for now like the uniform distribution over V'). The actual practice-relevant noise distribution, logistic-loss form, and relationship to R02/NCE are external-paper-dependent and need DeepResearch before a robust teaching script."
  - waypoint: WP05
    title: "Pretrained Vectors / Analogy / Visualization"
    needs_deepresearch: true
    official_anchor: "slides p9 plan item 'Looking at word vectors'; A1 Part 2; R02 compositionality/analogy evidence"
    research_question: "How do pretrained vector analogies and compositional relationships work geometrically, when do they fail, how should cosine/PCA/t-SNE visualizations be interpreted, and what bias/failure cases should be surfaced before A1 Part 2?"
    reason: "Official slides/notes do not teach this waypoint in distributed material. Slides p9 lists 'Looking at word vectors (10 mins or less)' in the lecture plan, but the extracted slides end at p36 with optimization/SGD and contain no dedicated analogy or visualization section. Notes appendices list CBOW and SVD headings (A.1, A.2) but no substantive content, and there is no notes section on analogies, PCA/t-SNE interpretation, or embedding bias. A1 Part 2 requires students to load GloVe vectors, compute similarities, analyze plots, answer analogy questions, and inspect bias, so this waypoint needs external explanation and evidence before Lecture Weaver can responsibly guide students."
```

## Verification notes

- `core_readings`: 2 entries, both schedule-core and both with canonical URL, PDF URL, local PDF path, official anchor, `waypoint_focus`, and `paper_tutor_focus`.
- `code_capsules`: 6 entries covering WP02-WP05. WP02 has both one-hot/dense and co-occurrence/SVD because A1 Part 1 depends on the count-based path as well as the one-hot contrast.
- `deepresearch_waypoints`: 5 entries for WP01-WP05 (all waypoints covered). WP01/WP02/WP03 are false because slides+notes cover them at intro depth; WP04/WP05 are true because negative sampling and vector analogy/visualization require external-paper/support explanation.
- Three YAML blocks are independently fenced as `yaml`, closed, and contain no YAML document separator line.
- No paper note, `00-课堂入口.md`, code capsule implementation, DeepResearch report, or Obsidian publish was written in this Reading Triage stage.
