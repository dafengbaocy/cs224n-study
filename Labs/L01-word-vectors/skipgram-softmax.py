#!/usr/bin/env python3
"""
Skip-gram Softmax P(o|c) computation demo.
CS224N L01 Word Vectors - Code Capsule: skipgram-softmax

Part A: random init -> nearly uniform probabilities
Part B: hand-designed "trained" vectors -> semantic clusters get higher prob

Official anchors:
  - Slides p27-30: objective function, softmax formula
  - Notes 3.2 Eq.4-5: p(o|c) = exp(u_o^T v_c) / sum_w exp(u_w^T v_c)
"""

import json
import sys
import os

import numpy as np

np.random.seed(42)

# ============================================================
# Vocabulary
# ============================================================
vocab = ["banking", "money", "river", "bank", "stream", "credit", "loan", "water"]
vocab_size = len(vocab)
word_to_idx = {w: i for i, w in enumerate(vocab)}
d = 4

print("=" * 68)
print("Skip-gram Softmax P(o|c)")
print("CS224N L01 - Code Capsule: skipgram-softmax")
print("=" * 68)
print(f"\nVocabulary (|V|={vocab_size}): {vocab}")
print(f"Embedding dim d={d}")
print(f"Clusters: finance=[banking,money,credit,loan]  "
      f"river=[river,stream,water]  ambiguous=[bank]")


def softmax(scores):
    """Numerically stable softmax."""
    shifted = scores - np.max(scores)
    exp_s = np.exp(shifted)
    return exp_s / np.sum(exp_s)


def print_table(center_word, scores, probs, label=""):
    """Print computation table."""
    if label:
        print(f"\n--- {label} ---")
    print(f"\n{'='*76}")
    print(f"  {'Word':<12} {'Dot Score':>12} {'exp(s-max)':>14} {'P(o|c)':>12}  Bar")
    print(f"{'='*76}")
    for i, w in enumerate(vocab):
        bar_len = int(probs[i] * 40)
        bar = "#" * bar_len
        marker = " <- center" if w == center_word else ""
        exp_val = np.exp(scores[i] - np.max(scores))
        print(f"  {w:<10} {scores[i]:>12.6f} {exp_val:>14.6f} {probs[i]:>12.6f}  {bar}{marker}")
    print(f"{'='*76}")
    exp_sum = np.sum(np.exp(scores - np.max(scores)))
    print(f"  {'SUM':<10} {'':>12} {exp_sum:>14.6f} {np.sum(probs):>12.6f}")
    print(f"  Check: sum P(o|c) = {np.sum(probs):.10f}")


# ============================================================
# Part A: Random initialization
# ============================================================
print(f"\n{'#'*68}")
print(f"# Part A: Random initialization (before training)")
print(f"{'#'*68}")

V_rand = np.random.randn(vocab_size, d) * 0.1
U_rand = np.random.randn(vocab_size, d) * 0.1

center_word = "banking"
c_idx = word_to_idx[center_word]
v_c_rand = V_rand[c_idx]

scores_rand = U_rand @ v_c_rand
probs_rand = softmax(scores_rand)

print(f"\nMatrix shapes: V={V_rand.shape}, U={U_rand.shape}, "
      f"total params={V_rand.size + U_rand.size}")
print(f"Center word: '{center_word}', "
      f"v_c = {np.array2string(v_c_rand, precision=4, suppress_small=True)}")

print_table(center_word, scores_rand, probs_rand,
            label="Part A: Random init results")

sorted_idx_rand = np.argsort(-probs_rand)
ratio_rand = probs_rand[sorted_idx_rand[0]] / probs_rand[sorted_idx_rand[-1]]
print(f"\n  Highest: P({vocab[sorted_idx_rand[0]]}|{center_word}) "
      f"= {probs_rand[sorted_idx_rand[0]]:.6f}")
print(f"  Lowest:  P({vocab[sorted_idx_rand[-1]]}|{center_word}) "
      f"= {probs_rand[sorted_idx_rand[-1]]:.6f}")
print(f"  Ratio: {ratio_rand:.2f}x")
print(f"  -> Random init: all probs nearly equal (~ 1/{vocab_size} "
      f"= {1/vocab_size:.4f})")

# ============================================================
# Part B: Hand-designed "trained" vectors
# ============================================================
print(f"\n{'#'*68}")
print(f"# Part B: Hand-designed vectors (simulating trained embeddings)")
print(f"{'#'*68}")
print(f"\nDesign logic:")
print(f"  Finance words (banking/money/credit/loan): high positive on dim 0")
print(f"  River words (river/stream/water): high positive on dim 1")
print(f"  bank: moderate on both dims (ambiguous)")
print(f"  -> banking dot product with money/credit/loan will be larger")

V_train = np.array([
    [1.0, 0.0, 0.2, 0.1],   # banking  - finance
    [0.8, 0.1, 0.1, 0.0],   # money    - finance
    [0.0, 1.0, 0.2, 0.1],   # river    - river
    [0.5, 0.5, 0.1, 0.1],   # bank     - ambiguous
    [0.1, 0.9, 0.1, 0.2],   # stream   - river
    [0.9, 0.0, 0.1, 0.1],   # credit   - finance
    [0.7, 0.1, 0.0, 0.2],   # loan     - finance
    [0.0, 0.8, 0.1, 0.3],   # water    - river
], dtype=np.float64)

U_train = V_train.copy()  # symmetric for clarity

v_c_train = V_train[c_idx]
scores_train = U_train @ v_c_train
probs_train = softmax(scores_train)

print(f"\nCenter word: '{center_word}'")
print(f"  v_{center_word} = {np.array2string(v_c_train, precision=2)}")

# Show detailed dot product for "money"
money_idx = word_to_idx["money"]
u_money = U_train[money_idx]
terms = [f"{u_money[k]:.1f}x{v_c_train[k]:.1f}" for k in range(d)]
print(f"\nDot product detail (money example):")
print(f"  u_money = {np.array2string(u_money, precision=2)}")
print(f"  u_money . v_banking = {' + '.join(terms)}")
dot_detail = sum(u_money[k] * v_c_train[k] for k in range(d))
print(f"                    = {dot_detail:.4f}")

print_table(center_word, scores_train, probs_train,
            label="Part B: Trained vector results")

sorted_idx_train = np.argsort(-probs_train)
ratio_train = probs_train[sorted_idx_train[0]] / probs_train[sorted_idx_train[-1]]
print(f"\n  Highest: P({vocab[sorted_idx_train[0]]}|{center_word}) "
      f"= {probs_train[sorted_idx_train[0]]:.6f}")
print(f"  Lowest:  P({vocab[sorted_idx_train[-1]]}|{center_word}) "
      f"= {probs_train[sorted_idx_train[-1]]:.6f}")
print(f"  Ratio: {ratio_train:.2f}x")
print(f"\n  After training:")
print(f"    Finance words (money/credit/loan/banking): prob increases")
print(f"    River words (river/stream/water): prob decreases")
print(f"    bank (ambiguous): prob in between")

# ============================================================
# Part C: Comparison
# ============================================================
print(f"\n{'#'*68}")
print(f"# Part C: Random vs Trained comparison")
print(f"{'#'*68}")

print(f"\n{'Word':<12} {'P_random':>10} {'P_trained':>10} {'Delta':>10}")
print(f"{'-'*44}")
for i, w in enumerate(vocab):
    diff = probs_train[i] - probs_rand[i]
    arrow = "^" if diff > 0.005 else ("v" if diff < -0.005 else "~")
    print(f"  {w:<10} {probs_rand[i]:>10.4f} {probs_train[i]:>10.4f} "
          f"{diff:>+8.4f} {arrow}")

print(f"\n  Softmax converts dot-product scores into a probability distribution.")
print(f"  Training objective (Notes Eq.5): adjust U,V to maximize P(true context|center).")

# ============================================================
# Save results
# ============================================================
output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
os.makedirs(output_dir, exist_ok=True)

results = {
    "vocab": vocab,
    "center_word": center_word,
    "embedding_dim": d,
    "vocab_size": vocab_size,
    "part_a_random": {
        "scores": {w: round(float(scores_rand[i]), 6)
                   for i, w in enumerate(vocab)},
        "probabilities": {w: round(float(probs_rand[i]), 6)
                         for i, w in enumerate(vocab)},
        "max_min_ratio": round(float(ratio_rand), 2),
    },
    "part_b_trained": {
        "scores": {w: round(float(scores_train[i]), 6)
                   for i, w in enumerate(vocab)},
        "probabilities": {w: round(float(probs_train[i]), 6)
                         for i, w in enumerate(vocab)},
        "max_min_ratio": round(float(ratio_train), 2),
    },
    "sum_probabilities_random": round(float(np.sum(probs_rand)), 10),
    "sum_probabilities_trained": round(float(np.sum(probs_train)), 10),
}

json_path = os.path.join(output_dir, "skipgram-softmax-results.json")
with open(json_path, "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nResults saved: {json_path}")

# ============================================================
# Generate plots (English labels to avoid CJK font issues)
# ============================================================
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mticker
    from matplotlib.patches import Patch

    # Color scheme
    def get_color(w):
        if w == center_word:
            return "#e74c3c"
        elif w in ["banking", "money", "credit", "loan"]:
            return "#3498db"
        elif w in ["river", "stream", "water"]:
            return "#2ecc71"
        else:
            return "#f39c12"

    colors = [get_color(w) for w in vocab]

    # ---- Plot 1: Trained probability bar chart ----
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(vocab, probs_train, color=colors,
                  edgecolor="#2c3e50", linewidth=0.8)
    for bar, prob in zip(bars, probs_train):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.003,
                f"{prob:.3f}", ha="center", va="bottom",
                fontsize=9, fontweight="bold")

    ax.set_xlabel("Context word (o)", fontsize=12)
    ax.set_ylabel("P(o | c)", fontsize=12)
    ax.set_title(f"Skip-gram Softmax: P(o | c='{center_word}') "
                 f"-- Trained Vectors, |V|={vocab_size}, d={d}",
                 fontsize=12)
    ax.set_ylim(0, max(probs_train) * 1.3)
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.3f"))
    ax.axhline(y=1.0/vocab_size, color="gray", linestyle="--",
               linewidth=0.8, alpha=0.7)
    ax.text(vocab_size - 0.5, 1.0/vocab_size + 0.003,
            f"uniform=1/{vocab_size}={1.0/vocab_size:.3f}",
            fontsize=8, color="gray", ha="right")

    legend_elements = [
        Patch(facecolor="#e74c3c", label=f"center ({center_word})"),
        Patch(facecolor="#3498db", label="finance cluster"),
        Patch(facecolor="#2ecc71", label="river cluster"),
        Patch(facecolor="#f39c12", label="ambiguous (bank)"),
    ]
    ax.legend(handles=legend_elements, loc="upper right", fontsize=9)
    plt.tight_layout()
    chart_path = os.path.join(output_dir,
                              "skipgram-softmax-probability-bar.png")
    fig.savefig(chart_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Plot 1 saved: {chart_path}")

    # ---- Plot 2: Dot score vs probability (side by side) ----
    fig2, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    sorted_idx = np.argsort(-scores_train)
    sorted_words = [vocab[i] for i in sorted_idx]
    sorted_scores_list = [scores_train[i] for i in sorted_idx]
    sorted_probs_list = [probs_train[i] for i in sorted_idx]
    colors_sorted = [get_color(w) for w in sorted_words]

    ax1.barh(sorted_words[::-1], sorted_scores_list[::-1],
             color=colors_sorted[::-1], edgecolor="#2c3e50")
    ax1.set_xlabel("Dot product: u_w^T v_c", fontsize=11)
    ax1.set_title(f"Dot products with v_'{center_word}'", fontsize=12)
    for i, (w, s) in enumerate(zip(sorted_words[::-1],
                                    sorted_scores_list[::-1])):
        ax1.text(s + 0.01, i, f"{s:.3f}", va="center", fontsize=8)

    ax2.barh(sorted_words[::-1], sorted_probs_list[::-1],
             color=colors_sorted[::-1], edgecolor="#2c3e50")
    ax2.set_xlabel("P(o | c)", fontsize=11)
    ax2.set_title(f"Softmax P(o | c='{center_word}')", fontsize=12)
    ax2.axvline(x=1.0/vocab_size, color="gray", linestyle="--",
                linewidth=0.8, alpha=0.7)
    for i, (w, p) in enumerate(zip(sorted_words[::-1],
                                    sorted_probs_list[::-1])):
        ax2.text(p + 0.003, i, f"{p:.4f}", va="center", fontsize=8)

    plt.tight_layout()
    compare_path = os.path.join(output_dir,
                                "skipgram-softmax-dotscore-vs-prob.png")
    fig2.savefig(compare_path, dpi=150, bbox_inches="tight")
    plt.close(fig2)
    print(f"Plot 2 saved: {compare_path}")

    # ---- Plot 3: Random vs Trained comparison ----
    fig3, ax3 = plt.subplots(figsize=(11, 5))
    x = np.arange(vocab_size)
    width = 0.35
    ax3.bar(x - width/2, probs_rand, width, label="Random init",
            color="#95a5a6", edgecolor="#2c3e50")
    ax3.bar(x + width/2, probs_train, width, label="Trained (designed)",
            color="#3498db", edgecolor="#2c3e50")

    ax3.set_xlabel("Context word (o)", fontsize=12)
    ax3.set_ylabel("P(o | c)", fontsize=12)
    ax3.set_title(f"Random vs Trained: P(o | c='{center_word}')",
                  fontsize=13)
    ax3.set_xticks(x)
    ax3.set_xticklabels(vocab)
    ax3.legend(fontsize=10)
    ax3.axhline(y=1.0/vocab_size, color="gray", linestyle="--",
                linewidth=0.8, alpha=0.7)
    ax3.set_ylim(0, max(max(probs_rand), max(probs_train)) * 1.3)

    plt.tight_layout()
    compare_ab_path = os.path.join(output_dir,
                                   "skipgram-softmax-random-vs-trained.png")
    fig3.savefig(compare_ab_path, dpi=150, bbox_inches="tight")
    plt.close(fig3)
    print(f"Plot 3 saved: {compare_ab_path}")

except ImportError as e:
    print(f"[WARNING] matplotlib not available: {e}", file=sys.stderr)
    chart_path = None
    compare_path = None
    compare_ab_path = None

print(f"\n{'='*68}")
print("Done. All outputs saved to outputs/ directory.")
print(f"{'='*68}")
