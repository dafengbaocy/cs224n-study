#!/usr/bin/env python3
"""Generate co-occurrence-matrix.ipynb from the .py script."""
import nbformat as nbf
import json

nb = nbf.v4.new_notebook()
nb.metadata = {
    "kernelspec": {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3"
    },
    "language_info": {
        "name": "python",
        "version": "3.13.5"
    }
}

cells = []

# Cell 1: Markdown intro
cells.append(nbf.v4.new_markdown_cell("""# CS224N L01 — Code Capsule: Co-occurrence Matrix + SVD

**Waypoint WP02**: Distributional Semantics  
**Concept**: 从语料构建共现矩阵并做 SVD 降维  
**Official anchor**: Notes §3.1 (co-occurrence matrices); A1 Part 1 Q1.1-1.3

> "You shall know a word by the company it keeps." — J. R. Firth (1957)

本 notebook 演示：
1. 从 toy corpus 构建 [[Lectures/L01-word-vectors/00-concept-glossary#co-occurrence-matrix|共现矩阵]]
2. 应用 log 归一化（Notes §3.1 推荐）
3. 用 [[Lectures/L01-word-vectors/00-concept-glossary#svd|SVD]] 降维到 2D
4. 可视化词向量，观察语义聚类
5. 比较不同窗口大小的效果"""))

# Cell 2: Imports
cells.append(nbf.v4.new_markdown_cell("## 1. 导入库"))
cells.append(nbf.v4.new_code_cell("""import numpy as np
from collections import Counter
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt"""))

# Cell 3: Corpus
cells.append(nbf.v4.new_markdown_cell("""## 2. Toy Corpus

设计两个语义簇：
- **Finance**: banking, money, finance, economy, market, invest
- **Nature**: river, lake, forest, mountain, valley, ocean

> [!tip] 中文扶手
> 分布语义学的核心思想：出现在相似上下文中的词，语义相似。
> 我们通过统计词在滑动窗口内的共现次数来捕捉这种"上下文相似性"。"""))
cells.append(nbf.v4.new_code_cell("""CORPUS = [
    # Finance sentences
    "the banking system manages money and finance",
    "the economy depends on banking and finance",
    "money flows through the banking system",
    "the economy and finance are connected to the market",
    "invest in the banking market and finance",
    "the market economy depends on money and invest",
    # Nature sentences
    "the river flows through the forest and valley",
    "the lake is near the mountain and forest",
    "a mountain rises above the lake and valley",
    "the forest surrounds the lake and river",
    "the river and lake are in the valley",
    "a mountain overlooks the river and ocean",
    # Bridge sentences
    "the river flows like money through the economy",
    "invest in the ocean and the market",
]

def tokenize(text):
    return text.lower().split()

all_tokens = []
for sent in CORPUS:
    all_tokens.extend(tokenize(sent))

vocab_set = sorted(set(all_tokens))
word2idx = {w: i for i, w in enumerate(vocab_set)}
idx2word = {i: w for w, i in word2idx.items()}
V = len(vocab_set)

print(f"Corpus: {len(CORPUS)} sentences, {len(all_tokens)} tokens")
print(f"Vocabulary size |V| = {V}")
print(f"Vocabulary: {vocab_set}")"""))

# Cell 4: Build co-occurrence matrix
cells.append(nbf.v4.new_markdown_cell("""## 3. 构建共现矩阵

> [!info] Notes §3.1 的构建步骤
> 1. 确定词汇表 V
> 2. 建 |V|×|V| 零矩阵
> 3. 遍历文档，在窗口内统计共现
> 4. （可选）行归一化

我们用 `window_size=2`，即中心词左右各 2 个词。"""))
cells.append(nbf.v4.new_code_cell("""def build_cooccurrence(corpus, word2idx, window_size):
    V = len(word2idx)
    cooc = np.zeros((V, V), dtype=int)
    for sent in corpus:
        tokens = tokenize(sent)
        for i, center in enumerate(tokens):
            c_idx = word2idx[center]
            start = max(0, i - window_size)
            end = min(len(tokens), i + window_size + 1)
            for j in range(start, end):
                if i == j:
                    continue
                cooc[c_idx, word2idx[tokens[j]]] += 1
    return cooc

WINDOW = 2
cooc_raw = build_cooccurrence(CORPUS, word2idx, window_size=WINDOW)

print(f"Matrix shape: {cooc_raw.shape}")
print(f"Total count: {cooc_raw.sum()}")
print(f"Nonzero entries: {np.count_nonzero(cooc_raw)}")

# Show content-word sub-matrix
content_words = [w for w in vocab_set if w not in {'the','a','is','in','of','and','to','with'}]
cw_idx = [word2idx[w] for w in content_words]

print("\\nCo-occurrence sub-matrix (content words):")
header = "          " + "".join(f"{w:>10s}" for w in content_words)
print(header)
for i, w in enumerate(content_words):
    row = f"{w:>10s}" + "".join(f"{cooc_raw[cw_idx[i], cw_idx[j]]:10d}" for j in range(len(content_words)))
    print(row)"""))

# Cell 5: Log normalization
cells.append(nbf.v4.new_markdown_cell("""## 4. Log 归一化

> [!tip] Notes §3.1
> "Taking the log token frequency ends up being much more useful"

原始共现次数中，高频词（如 "the"）会主导矩阵。`log(1+x)` 压缩极端值，让 SVD 更好地捕捉语义结构。"""))
cells.append(nbf.v4.new_code_cell("""cooc_log = np.log1p(cooc_raw.astype(float))

print(f"Before log: max = {cooc_raw.max()}, mean(nonzero) = {cooc_raw[cooc_raw > 0].mean():.2f}")
print(f"After log:  max = {cooc_log.max():.4f}, mean(nonzero) = {cooc_log[cooc_log > 0].mean():.4f}")"""))

# Cell 6: SVD
cells.append(nbf.v4.new_markdown_cell("""## 5. SVD 降维

用 [[Lectures/L01-word-vectors/00-concept-glossary#svd|SVD]] 把 |V|×|V| 矩阵压缩到 |V|×2。

> [!info] 直觉
> SVD 找到矩阵中"最重要的两个方向"——共现模式中方差最大的两个轴。
> 语义相似的词在这些轴上的投影会接近。"""))
cells.append(nbf.v4.new_code_cell("""def svd_reduce(matrix, k=2):
    U, S, Vt = np.linalg.svd(matrix, full_matrices=False)
    return U[:, :k] * S[:k], S

k = 2
embeddings, singular_values = svd_reduce(cooc_log, k=k)

print(f"Singular values (top 6): {singular_values[:6].round(3)}")
print(f"Top-{k} explained variance: {(singular_values[:k]**2 / (singular_values**2).sum() * 100).round(1)}%")
print()

print("2D Embeddings (content words):")
for w in content_words:
    i = word2idx[w]
    print(f"  {w:>10s}: [{embeddings[i, 0]:8.4f}, {embeddings[i, 1]:8.4f}]")"""))

# Cell 7: Cosine similarity
cells.append(nbf.v4.new_markdown_cell("""## 6. Cosine Similarity

用 [[Lectures/L01-word-vectors/00-concept-glossary#cosine-similarity|cosine similarity]] 衡量词向量方向相似度。
- 同簇词（如 banking-money）应该相似度高
- 跨簇词（如 banking-river）应该相似度低"""))
cells.append(nbf.v4.new_code_cell("""def cosine_sim(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

pairs = [
    ("banking", "finance",   "same cluster (finance)"),
    ("banking", "money",     "same cluster (finance)"),
    ("river",   "lake",      "same cluster (nature)"),
    ("river",   "forest",    "same cluster (nature)"),
    ("banking", "river",     "CROSS cluster"),
    ("finance", "mountain",  "CROSS cluster"),
]

print("Cosine Similarities (2D SVD):")
for w1, w2, label in pairs:
    sim = cosine_sim(embeddings[word2idx[w1]], embeddings[word2idx[w2]])
    print(f"  sim({w1:>10s}, {w2:>10s}) = {sim:.4f}  [{label}]")"""))

# Cell 8: Window size comparison
cells.append(nbf.v4.new_markdown_cell("""## 7. 窗口大小的影响

> [!tip] Notes §3.1 关键观察
> - **短窗口**（1 词）→ 捕捉**语法**属性（名词旁常出现 the/is）
> - **大窗口**（5+ 词或文档级）→ 捕捉**语义/主题**属性

试试不同窗口大小对相似度的影响："""))
cells.append(nbf.v4.new_code_cell("""print(f"{'Window':>6s}  {'banking-money':>14s}  {'river-lake':>14s}  {'banking-forest':>15s}")
for ws in [1, 2, 3]:
    cooc_ws = np.log1p(build_cooccurrence(CORPUS, word2idx, window_size=ws).astype(float))
    emb_ws, _ = svd_reduce(cooc_ws, k=k)
    sim_bm = cosine_sim(emb_ws[word2idx["banking"]], emb_ws[word2idx["money"]])
    sim_rl = cosine_sim(emb_ws[word2idx["river"]], emb_ws[word2idx["lake"]])
    sim_bf = cosine_sim(emb_ws[word2idx["banking"]], emb_ws[word2idx["forest"]])
    print(f"  {ws:>4d}    {sim_bm:>14.4f}  {sim_rl:>14.4f}  {sim_bf:>15.4f}")"""))

# Cell 9: Visualization
cells.append(nbf.v4.new_markdown_cell("""## 8. 可视化

左：共现矩阵热图 | 中：2D 词向量散点图 | 右：窗口大小对比"""))
cells.append(nbf.v4.new_code_cell("""finance_words = ['banking', 'money', 'finance', 'economy', 'market', 'invest']
nature_words = ['river', 'lake', 'forest', 'mountain', 'valley', 'ocean']

fig, axes = plt.subplots(1, 3, figsize=(20, 6))

# Heatmap
sub_matrix = cooc_raw[np.ix_(cw_idx, cw_idx)]
im = axes[0].imshow(sub_matrix, cmap='YlOrRd', aspect='auto')
axes[0].set_title(f'Co-occurrence Matrix (window={WINDOW})', fontsize=11)
axes[0].set_xticks(range(len(content_words)))
axes[0].set_yticks(range(len(content_words)))
axes[0].set_xticklabels(content_words, rotation=90, fontsize=8)
axes[0].set_yticklabels(content_words, fontsize=8)
plt.colorbar(im, ax=axes[0], fraction=0.046)

# 2D scatter
for w in content_words:
    i = word2idx[w]
    x, y = embeddings[i, 0], embeddings[i, 1]
    if w in finance_words:
        color, marker = '#e74c3c', 'o'
    elif w in nature_words:
        color, marker = '#2ecc71', 's'
    else:
        color, marker = '#f39c12', 'D'
    axes[1].scatter(x, y, c=color, marker=marker, s=100, zorder=5, edgecolors='black', linewidth=0.5)
    axes[1].annotate(w, (x, y), fontsize=9, fontweight='bold', ha='center', va='bottom',
                     xytext=(0, 6), textcoords='offset points')
axes[1].set_title(f'SVD 2D Embeddings (log-normalized, window={WINDOW})', fontsize=11)
axes[1].set_xlabel('SVD Component 1')
axes[1].set_ylabel('SVD Component 2')
axes[1].grid(True, alpha=0.3)
axes[1].axhline(y=0, color='k', linewidth=0.5, linestyle='--')
axes[1].axvline(x=0, color='k', linewidth=0.5, linestyle='--')

# Window comparison
all_sims = {}
for ws in [1, 2, 3]:
    cooc_ws = np.log1p(build_cooccurrence(CORPUS, word2idx, window_size=ws).astype(float))
    emb_ws, _ = svd_reduce(cooc_ws, k=k)
    all_sims[ws] = (
        cosine_sim(emb_ws[word2idx["banking"]], emb_ws[word2idx["money"]]),
        cosine_sim(emb_ws[word2idx["river"]], emb_ws[word2idx["lake"]]),
        cosine_sim(emb_ws[word2idx["banking"]], emb_ws[word2idx["forest"]]),
    )

x_pos = np.arange(3)
width = 0.25
axes[2].bar(x_pos - width, [all_sims[ws][0] for ws in [1,2,3]], width, label='banking-money', color='#e74c3c', alpha=0.8)
axes[2].bar(x_pos, [all_sims[ws][1] for ws in [1,2,3]], width, label='river-lake', color='#2ecc71', alpha=0.8)
axes[2].bar(x_pos + width, [all_sims[ws][2] for ws in [1,2,3]], width, label='banking-forest', color='#3498db', alpha=0.8)
axes[2].set_title('Window Size Effect', fontsize=11)
axes[2].set_xlabel('Window Size')
axes[2].set_ylabel('Cosine Similarity')
axes[2].set_xticks(x_pos)
axes[2].set_xticklabels(['w=1', 'w=2', 'w=3'])
axes[2].legend(fontsize=8)
axes[2].set_ylim(-0.5, 1.1)
axes[2].grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('outputs/co-occurrence-matrix-overview.png', dpi=150, bbox_inches='tight')
plt.show()
print("Saved: outputs/co-occurrence-matrix-overview.png")"""))

# Cell 10: Detailed scatter
cells.append(nbf.v4.new_markdown_cell("## 9. 详细 2D 散点图（带聚类区域）"))
cells.append(nbf.v4.new_code_cell("""from matplotlib.patches import Ellipse

fig2, ax2 = plt.subplots(figsize=(10, 8))

fin_pts = np.array([embeddings[word2idx[w]] for w in finance_words])
fin_center = fin_pts.mean(axis=0)
fin_std = fin_pts.std(axis=0) + 0.3
ax2.add_patch(Ellipse(fin_center, fin_std[0]*4, fin_std[1]*4, alpha=0.12, color='#e74c3c', label='Finance'))

nat_pts = np.array([embeddings[word2idx[w]] for w in nature_words])
nat_center = nat_pts.mean(axis=0)
nat_std = nat_pts.std(axis=0) + 0.3
ax2.add_patch(Ellipse(nat_center, nat_std[0]*4, nat_std[1]*4, alpha=0.12, color='#2ecc71', label='Nature'))

for w in content_words:
    i = word2idx[w]
    x, y = embeddings[i, 0], embeddings[i, 1]
    if w in finance_words:
        color, marker, sz = '#e74c3c', 'o', 120
    elif w in nature_words:
        color, marker, sz = '#2ecc71', 's', 120
    else:
        color, marker, sz = '#f39c12', 'D', 80
    ax2.scatter(x, y, c=color, marker=marker, s=sz, zorder=5, edgecolors='black', linewidth=0.5)
    ax2.annotate(w, (x, y), fontsize=10, fontweight='bold', ha='center', va='bottom',
                 xytext=(0, 8), textcoords='offset points')

ax2.set_title(f'Co-occurrence + SVD: 2D Word Embeddings\\n(log-normalized, window={WINDOW}, k={k})')
ax2.set_xlabel('SVD Component 1')
ax2.set_ylabel('SVD Component 2')
ax2.grid(True, alpha=0.3)
ax2.axhline(y=0, color='k', linewidth=0.5, linestyle='--')
ax2.axvline(x=0, color='k', linewidth=0.5, linestyle='--')
ax2.legend(fontsize=10)
plt.tight_layout()
plt.savefig('outputs/co-occurrence-matrix-2d-embeddings.png', dpi=150, bbox_inches='tight')
plt.show()
print("Saved: outputs/co-occurrence-matrix-2d-embeddings.png")"""))

# Cell 11: Summary
cells.append(nbf.v4.new_markdown_cell("""## 10. 小结

> [!info] 学到了什么
> 1. **共现矩阵**：统计词在窗口内共同出现的次数，捕捉分布语义
> 2. **Log 归一化**：压缩高频词的影响，让 SVD 更有效
> 3. **SVD 降维**：把高维稀疏矩阵压缩到低维密集向量
> 4. **窗口大小**：短窗口捕捉语法，长窗口捕捉语义/主题
> 5. **Cosine similarity**：衡量词向量方向相似度

> [!warning] 局限性
> - Toy corpus 太小（14 句），函数词（the, and）仍然主导共现模式
> - 2D 可视化只保留了 ~58% 的方差，更多信息需要更高维度
> - 实际应用中（如 GloVe），会在更大的语料上用更精细的加权方案

> [!question] 想一想
> - 如果窗口大小设为"整个文档"，共现矩阵会变成什么样？
> - 为什么 Notes §3.1 说 GloVe "works as well as word2vec"？它用了什么不同的技巧？"""))

nb.cells = cells

with open('Labs/L01-word-vectors/co-occurrence-matrix.ipynb', 'w') as f:
    nbf.write(nb, f)

print("Notebook written: Labs/L01-word-vectors/co-occurrence-matrix.ipynb")
