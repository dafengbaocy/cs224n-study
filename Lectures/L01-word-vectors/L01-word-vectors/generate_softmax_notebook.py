#!/usr/bin/env python3
"""Generate softmax-probability.ipynb from the .py source."""
import json
import os

script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'softmax-probability.py')
with open(script_path) as f:
    py_source = f.read()

viz_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'softmax-probability-viz.py')
with open(viz_path) as f:
    viz_source = f.read()

# Read stdout
stdout_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           '..', '..', 'Labs', 'L01-word-vectors', 'outputs',
                           'softmax-probability-stdout.txt')
with open(stdout_path) as f:
    stdout_text = f.read()

nb = {
    "nbformat": 4,
    "nbformat_minor": 0,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.11.0"
        },
        "colab": {
            "provenance": [],
            "name": "softmax-probability.ipynb"
        }
    },
    "cells": [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# CS224N L01 — Code Capsule: Softmax Probability Computation (WP03)\n",
                "\n",
                "**Concept**: Softmax probability computation for skip-gram Word2Vec  \n",
                "**Formula**: $P(o|c) = \\frac{\\exp(u_o^\\top v_c)}{\\sum_w \\exp(u_w^\\top v_c)}$  \n",
                "**Official anchor**: slides p28-p30; notes §3.2 Eq.4-Eq.5\n",
                "\n",
                "## Why this capsule matters\n",
                "\n",
                "The denominator (partition function Z) sums over the **entire vocabulary**.\n",
                "In formulas it's easy to gloss over, but running it on a tiny vocabulary\n",
                "makes the computation concrete:\n",
                "\n",
                "1. **Dot product scores** → how similar is each outside word to the center?\n",
                "2. **Exponentials** → make all scores positive\n",
                "3. **Normalization** → divide by Z to get a probability distribution\n",
                "\n",
                "This also shows why full softmax is expensive (→ WP04 negative sampling)."
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## Setup: Tiny vocabulary with hand-picked vectors\n",
                "\n",
                "5 words, 3-dimensional vectors. Semantically related words (bank/river/money/finance)\n",
                "have higher dot-product scores than unrelated pairs."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "import math\n",
                "import json\n",
                "\n",
                "vocab = ['bank', 'river', 'money', 'finance', 'ocean']\n",
                "vocab_size = len(vocab)\n",
                "\n",
                "# Center-word vectors v_c (rows of the V matrix)\n",
                "V = {\n",
                "    'bank':    [0.8,  0.3,  0.1],\n",
                "    'river':   [0.7,  0.5,  0.2],\n",
                "    'money':   [0.1,  0.9,  0.7],\n",
                "    'finance': [0.2,  0.8,  0.6],\n",
                "    'ocean':   [0.6,  0.4, -0.1],\n",
                "}\n",
                "\n",
                "# Outside-word vectors u_o (rows of the U matrix)\n",
                "U = {\n",
                "    'bank':    [0.7,  0.4,  0.2],\n",
                "    'river':   [0.8,  0.6,  0.3],\n",
                "    'money':   [0.2,  0.8,  0.9],\n",
                "    'finance': [0.3,  0.7,  0.5],\n",
                "    'ocean':   [0.5,  0.3, -0.2],\n",
                "}\n",
                "\n",
                "def dot(a, b):\n",
                "    return sum(ai * bi for ai, bi in zip(a, b))\n",
                "\n",
                "print(f'Vocabulary: {vocab}')\n",
                "print(f'|V| = {vocab_size}, embedding dim d = 3')\n",
                "print(f'V matrix (center vectors): {len(V)} words × {len(V[\"bank\"])} dims')\n",
                "print(f'U matrix (outside vectors): {len(U)} words × {len(U[\"bank\"])} dims')"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## Softmax computation step by step\n",
                "\n",
                "For center word `c`, we compute P(o|c) for every word o in the vocabulary."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "def compute_softmax_prob(center_word, vocab, V, U):\n",
                "    \"\"\"Compute P(o | center_word) for every o in vocab.\"\"\"\n",
                "    v_c = V[center_word]\n",
                "    print('=' * 70)\n",
                "    print(f\"Center word: {center_word!r}\")\n",
                "    print(f\"Center vector v_c = {v_c}\")\n",
                "    print(f\"Vocabulary size |V| = {len(vocab)}\")\n",
                "    print('=' * 70)\n",
                "    print()\n",
                "\n",
                "    # Step 1: Dot product scores\n",
                "    print('--- Step 1: Dot product scores  u_w^T v_c ---')\n",
                "    scores = []\n",
                "    for w in vocab:\n",
                "        score = dot(U[w], v_c)\n",
                "        scores.append(score)\n",
                "        print(f'  u_{w:<8}^T v_{center_word:<8} = {U[w]} . {v_c} = {score:.6f}')\n",
                "    print()\n",
                "\n",
                "    # Step 2: Exponentials (with max-subtraction for numerical stability)\n",
                "    print('--- Step 2: Exponentials  exp(u_w^T v_c) ---')\n",
                "    max_score = max(scores)\n",
                "    print(f'  Max score = {max_score:.6f}  (subtracting for numerical stability)')\n",
                "    exps_stable = []\n",
                "    for w, s in zip(vocab, scores):\n",
                "        exp_val = math.exp(s - max_score)\n",
                "        exps_stable.append(exp_val)\n",
                "        print(f'  exp({s:.6f} - {max_score:.6f}) = exp({s - max_score:.6f}) = {exp_val:.6f}')\n",
                "    Z = sum(exps_stable)\n",
                "    print()\n",
                "\n",
                "    # Step 3: Partition function Z\n",
                "    print('--- Step 3: Partition function Z (denominator) ---')\n",
                "    print(f'  Z = sum_w exp(u_w^T v_c) = {Z:.6f}')\n",
                "    print(f'  (This sum runs over ALL |V|={len(vocab)} words — expensive for real vocabularies!)')\n",
                "    print()\n",
                "\n",
                "    # Step 4: Normalized probabilities\n",
                "    print('--- Step 4: Normalized probabilities  P(o|c) = exp / Z ---')\n",
                "    probs = []\n",
                "    results = []\n",
                "    for w, exp_val, score in zip(vocab, exps_stable, scores):\n",
                "        p = exp_val / Z\n",
                "        probs.append(p)\n",
                "        results.append({'word': w, 'dot_score': round(score, 6),\n",
                "                        'exp_score': round(exp_val, 6), 'probability': round(p, 6)})\n",
                "        bar = '#' * int(p * 50)\n",
                "        print(f'  P({w:<8}|{center_word:<8}) = {exp_val:.6f} / {Z:.6f} = {p:.6f}  {bar}')\n",
                "    prob_sum = sum(probs)\n",
                "    print(f'  Sum of all P(o|c) = {prob_sum:.10f}  (should be 1.0)')\n",
                "    print()\n",
                "\n",
                "    # Key Insight\n",
                "    print('--- Key Insight ---')\n",
                "    sorted_results = sorted(results, key=lambda x: x['probability'], reverse=True)\n",
                "    print(f\"  Ranking by P(o|{center_word!r}):\")\n",
                "    for i, r in enumerate(sorted_results, 1):\n",
                "        print(f\"    {i}. {r['word']:<10} P = {r['probability']:.6f}  \"\n",
                "              f\"(dot score = {r['dot_score']:.4f})\")\n",
                "    return results\n",
                "\n",
                "# Run for center word 'bank'\n",
                "results_bank = compute_softmax_prob('bank', vocab, V, U)"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## Different center words → different distributions\n",
                "\n",
                "The same vocabulary, but with 'ocean' as center word, produces a different probability distribution."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Run for center word 'ocean'\n",
                "results_ocean = compute_softmax_prob('ocean', vocab, V, U)"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## Comparison table"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "print('=' * 70)\n",
                "print('COMPARISON: How different center words produce different distributions')\n",
                "print('=' * 70)\n",
                "print()\n",
                "print(f\"{'Word':<12} | {'P(o|bank)':<12} | {'P(o|ocean)':<12} | Difference\")\n",
                "print('-' * 55)\n",
                "for w in vocab:\n",
                "    p_bank = next(r['probability'] for r in results_bank if r['word'] == w)\n",
                "    p_ocean = next(r['probability'] for r in results_ocean if r['word'] == w)\n",
                "    diff = p_bank - p_ocean\n",
                "    marker = ' <- same word' if w in ['bank', 'ocean'] else ''\n",
                "    print(f'{w:<12} | {p_bank:<12.6f} | {p_ocean:<12.6f} | {diff:>+10.6f}{marker}')"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## Visualization\n",
                "\n",
                "Bar charts showing the softmax probability distributions for both center words."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "import matplotlib\n",
                "matplotlib.use('Agg')\n",
                "import matplotlib.pyplot as plt\n",
                "\n",
                "fig, axes = plt.subplots(1, 2, figsize=(12, 5))\n",
                "\n",
                "words = [r['word'] for r in results_bank]\n",
                "probs_bank = [r['probability'] for r in results_bank]\n",
                "probs_ocean = [r['probability'] for r in results_ocean]\n",
                "\n",
                "colors_bank = ['#2196F3' if p == max(probs_bank) else '#90CAF9' for p in probs_bank]\n",
                "colors_ocean = ['#FF9800' if p == max(probs_ocean) else '#FFE0B2' for p in probs_ocean]\n",
                "\n",
                "bars1 = axes[0].bar(words, probs_bank, color=colors_bank, edgecolor='white')\n",
                "axes[0].set_title(\"P(o | center='bank')\", fontsize=13, fontweight='bold')\n",
                "axes[0].set_ylabel('Probability')\n",
                "axes[0].set_ylim(0, 0.35)\n",
                "for bar, p in zip(bars1, probs_bank):\n",
                "    axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,\n",
                "                 f'{p:.4f}', ha='center', va='bottom', fontsize=9)\n",
                "axes[0].axhline(y=1/len(vocab), color='gray', linestyle='--', alpha=0.5,\n",
                "                label=f'Uniform (1/{len(vocab)}={1/len(vocab):.3f})')\n",
                "axes[0].legend(fontsize=9)\n",
                "\n",
                "bars2 = axes[1].bar(words, probs_ocean, color=colors_ocean, edgecolor='white')\n",
                "axes[1].set_title(\"P(o | center='ocean')\", fontsize=13, fontweight='bold')\n",
                "axes[1].set_ylabel('Probability')\n",
                "axes[1].set_ylim(0, 0.35)\n",
                "for bar, p in zip(bars2, probs_ocean):\n",
                "    axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,\n",
                "                 f'{p:.4f}', ha='center', va='bottom', fontsize=9)\n",
                "axes[1].axhline(y=1/len(vocab), color='gray', linestyle='--', alpha=0.5,\n",
                "                label=f'Uniform (1/{len(vocab)}={1/len(vocab):.3f})')\n",
                "axes[1].legend(fontsize=9)\n",
                "\n",
                "fig.suptitle('Softmax Probability P(o|c) — Tiny Vocabulary Demo\\n'\n",
                "             'slides p28-30: P(o|c) = exp(u_oᵀv_c) / Σ_w exp(u_wᵀv_c)',\n",
                "             fontsize=12, y=1.02)\n",
                "plt.tight_layout()\n",
                "plt.show()"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## Key takeaways\n",
                "\n",
                "1. **Softmax decomposes into 3 steps** (slides p30):\n",
                "   - Dot product → similarity score\n",
                "   - Exponential → make positive, amplify differences\n",
                "   - Normalize by Z → valid probability distribution\n",
                "\n",
                "2. **Z sums over the entire vocabulary** — with |V| = 500,000 this is extremely expensive.\n",
                "   This is the motivation for **negative sampling** (WP04).\n",
                "\n",
                "3. **Different center words produce different distributions** — the model learns\n",
                "   that 'bank' as center word assigns higher probability to 'river' (related context)\n",
                "   than to 'money'."
            ]
        }
    ]
}

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        '..', '..', 'Labs', 'L01-word-vectors', 'softmax-probability.ipynb')
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, 'w') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)
print(f'Notebook written to {out_path}')
