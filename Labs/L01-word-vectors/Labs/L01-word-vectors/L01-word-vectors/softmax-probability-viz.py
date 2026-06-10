#!/usr/bin/env python3
"""Generate softmax probability bar chart for code capsule softmax-probability."""
import json
import os
import sys

# Try matplotlib; fall back to ASCII if unavailable
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       '..', '..', 'Labs', 'L01-word-vectors', 'outputs')
os.makedirs(out_dir, exist_ok=True)

# Load results
json_path = os.path.join(out_dir, 'softmax-probability-results.json')
with open(json_path) as f:
    data = json.load(f)

vocab = data['vocab']
results_bank = data['results']['bank']
results_ocean = data['results']['ocean']

if HAS_MPL:
    # ── Bar chart: P(o|c) for bank and ocean ──────────────────────────
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    words = [r['word'] for r in results_bank]
    probs_bank = [r['probability'] for r in results_bank]
    probs_ocean = [r['probability'] for r in results_ocean]

    colors_bank = ['#2196F3' if r['probability'] == max(probs_bank) else '#90CAF9'
                   for r in results_bank]
    colors_ocean = ['#FF9800' if r['probability'] == max(probs_ocean) else '#FFE0B2'
                    for r in results_ocean]

    # Left: bank
    bars1 = axes[0].bar(words, probs_bank, color=colors_bank, edgecolor='white', linewidth=0.5)
    axes[0].set_title("P(o | center='bank')", fontsize=13, fontweight='bold')
    axes[0].set_ylabel('Probability', fontsize=11)
    axes[0].set_ylim(0, 0.35)
    for bar, p in zip(bars1, probs_bank):
        axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
                     f'{p:.4f}', ha='center', va='bottom', fontsize=9)
    axes[0].axhline(y=1/len(vocab), color='gray', linestyle='--', alpha=0.5, label=f'Uniform (1/{len(vocab)}={1/len(vocab):.3f})')
    axes[0].legend(fontsize=9)

    # Right: ocean
    bars2 = axes[1].bar(words, probs_ocean, color=colors_ocean, edgecolor='white', linewidth=0.5)
    axes[1].set_title("P(o | center='ocean')", fontsize=13, fontweight='bold')
    axes[1].set_ylabel('Probability', fontsize=11)
    axes[1].set_ylim(0, 0.35)
    for bar, p in zip(bars2, probs_ocean):
        axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
                     f'{p:.4f}', ha='center', va='bottom', fontsize=9)
    axes[1].axhline(y=1/len(vocab), color='gray', linestyle='--', alpha=0.5, label=f'Uniform (1/{len(vocab)}={1/len(vocab):.3f})')
    axes[1].legend(fontsize=9)

    fig.suptitle('Softmax Probability P(o|c) — Tiny Vocabulary Demo\n'
                 'slides p28-30: P(o|c) = exp(u_oᵀv_c) / Σ_w exp(u_wᵀv_c)',
                 fontsize=12, y=1.02)
    plt.tight_layout()
    chart_path = os.path.join(out_dir, 'softmax-probability-bar-chart.png')
    fig.savefig(chart_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f'Chart saved to {chart_path}')

    # ── Step-by-step breakdown chart ──────────────────────────────────
    fig2, axes2 = plt.subplots(1, 3, figsize=(15, 4.5))

    # Step 1: dot product scores
    scores_bank = [r['dot_score'] for r in results_bank]
    axes2[0].bar(words, scores_bank, color='#4CAF50', edgecolor='white')
    axes2[0].set_title('Step 1: Dot Products u_wᵀv_c', fontsize=11, fontweight='bold')
    axes2[0].set_ylabel('Score')
    for i, s in enumerate(scores_bank):
        axes2[0].text(i, s + 0.01, f'{s:.3f}', ha='center', fontsize=9)

    # Step 2: exp scores (stable)
    exps_bank = [r['exp_score'] for r in results_bank]
    axes2[1].bar(words, exps_bank, color='#FF5722', edgecolor='white')
    axes2[1].set_title('Step 2: exp(score - max)', fontsize=11, fontweight='bold')
    axes2[1].set_ylabel('exp value')
    for i, e in enumerate(exps_bank):
        axes2[1].text(i, e + 0.01, f'{e:.3f}', ha='center', fontsize=9)

    # Step 3: normalized probabilities
    axes2[2].bar(words, probs_bank, color=colors_bank, edgecolor='white')
    axes2[2].set_title('Step 3: P(o|c) = exp / Z', fontsize=11, fontweight='bold')
    axes2[2].set_ylabel('Probability')
    for i, p in enumerate(probs_bank):
        axes2[2].text(i, p + 0.005, f'{p:.4f}', ha='center', fontsize=9)
    axes2[2].axhline(y=1/len(vocab), color='gray', linestyle='--', alpha=0.5)

    fig2.suptitle("Softmax Decomposition (center='bank') — slides p30 breakdown",
                  fontsize=12, y=1.02)
    plt.tight_layout()
    steps_path = os.path.join(out_dir, 'softmax-probability-step-decomposition.png')
    fig2.savefig(steps_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f'Steps chart saved to {steps_path}')
else:
    print('matplotlib not available, generating ASCII chart instead')
    # ASCII fallback
    ascii_path = os.path.join(out_dir, 'softmax-probability-bar-chart.txt')
    with open(ascii_path, 'w') as f:
        f.write("P(o|'bank'):\n")
        for r in results_bank:
            bar = '█' * int(r['probability'] * 50)
            f.write(f"  {r['word']:<10} {bar} {r['probability']:.4f}\n")
        f.write("\nP(o|'ocean'):\n")
        for r in results_ocean:
            bar = '█' * int(r['probability'] * 50)
            f.write(f"  {r['word']:<10} {bar} {r['probability']:.4f}\n")
    print(f'ASCII chart saved to {ascii_path}')
