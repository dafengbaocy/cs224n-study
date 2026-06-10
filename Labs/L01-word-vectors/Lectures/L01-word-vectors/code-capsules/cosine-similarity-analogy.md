## cosine-similarity-analogy — 余弦相似度与词类比算术 {#cosine-similarity-analogy}

> **[!info] 本 capsule 解释什么概念？]**
> 余弦相似度（cosine similarity）和词类比算术（word analogy arithmetic）。
> A1 Part 2 Q2.2-2.6 要求用 cosine similarity 做类比，但 slides/notes 没有教 cosine similarity 的计算和向量算术的直觉；需要实际跑才能理解。

**对应 waypoint**: WP05/WP06 — [[Lectures/L01-word-vectors/00-concept-glossary#pretrained-word-vectors-cosine-similarity-and-analogies|Pretrained Vectors / Cosine Similarity and Analogies]]

**官方锚点**: A1 Part 2 Q2.2-2.6; Notes §3.1 仅简述

---

### 为什么不能只看文字？

- A1 要求学生计算 cosine similarity、做类比（man : king :: woman : queen）
- Slides/notes 只提了概念，没有教计算公式和向量算术的直觉
- 需要实际跑才能理解：为什么用余弦而不是欧氏距离？类比方向为什么重要？

---

### 第 1 步：余弦相似度公式

$$
\cos(\mathbf{u}, \mathbf{v}) = \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\| \times \|\mathbf{v}\|}
$$

- $\mathbf{u} \cdot \mathbf{v}$ 是[[Lectures/L01-word-vectors/00-concept-glossary#dot-product|点积]]（对应维相乘再求和）
- $\|\mathbf{u}\|$ 是 L2 范数（向量长度）
- 结果范围 $[-1, 1]$：1=方向完全相同，0=正交（无关），-1=方向完全相反

> **[!tip] 为什么用余弦而不是欧氏距离？]**
> 余弦只看方向，不看长度。词向量的"长度"可能受词频影响，不是我们关心的语义信息。

**手算示例**（用本 capsule 的 toy 向量）：

| 词对 | 余弦相似度 | 解释 |
|------|-----------|------|
| king, queen | 0.3725 | 性别维度相反导致方向差异大 |
| king, man | 0.6459 | 同性别，差异只在皇室维度 |
| king, boy | 0.0703 | 同性别，但年龄差异大 |
| king, teacher | 0.2684 | 皇室 vs 职业，方向差异大 |

---

### 第 2 步：词类比算术

经典类比：**man : king :: woman : ?**

公式：$\text{target} = b - a + c$（即 king - man + woman）

直觉：king 比 man 多了"皇室"成分；woman 加上"皇室"应该是 queen。

**本 capsule 实际运行结果**：

| 类比 | 公式 | #1 结果 | cos | 预期 |
|------|------|---------|-----|------|
| man : king :: woman : ? | king - man + woman | queen | 1.0000 | queen ✓ |
| king : man :: woman : ? | man - king + woman | girl | 0.6035 | — (方向反了) |
| boy : girl :: man : ? | girl - boy + man | woman | 1.0000 | woman ✓ |
| prince : princess :: king : ? | princess - prince + king | queen | 1.0000 | queen ✓ |

> **[!warning] 类比方向很重要！]**
> $a:b::c:?$ 的公式是 $b - a + c$，不是 $a - b + c$。
> 类比 2（反向）返回 girl 而不是 queen，说明方向错了结果完全不同。

---

### 第 3 步：余弦相似度热力图

![余弦相似度热力图](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-174112.png)

> **[!info] 读图指南]**
> - **对角线全是 1.0**：自己和自己的余弦 = 1
> - **king-queen = 0.37**：性别维度符号相反，方向差异大
> - **king-man = 0.65**：同性别，只有皇室维度不同
> - **man-boy = 0.53**：同性别，只有年龄维度不同
> - **同性别词之间**的余弦 > **异性别词之间**：性别维度（第 0 维）绝对值最大（0.8），对方向影响最大

---

### 第 4 步：类比的局限性

词类比并不总是成功：

1. **训练数据偏差**：如果语料中 "doctor" 多与男性共现，类比可能返回刻板印象答案
2. **多义词问题**："bank" 可以是河岸也可以是银行，单一向量无法同时编码
3. **Toy 数据局限**：6 维太简单，真实 300 维 GloVe 向量中 king-queen 余弦通常 0.7-0.8

**本 capsule 演示**：teacher : student :: king : ?

| 排名 | 词 | cos | 解释 |
|------|-----|-----|------|
| #1 | prince | 0.7668 | 合理：皇室+年轻+男性 |
| #2 | man | 0.4905 | 成年+男性，但没有"受教"关系 |
| #3 | boy | 0.4777 | 年轻+男性 |

---

### 对应 A1 Part 2 问题

- **Q2.2**: 计算余弦相似度 → 本 capsule 第 1 步
- **Q2.3**: 词类比 → 本 capsule 第 2 步
- **Q2.4-2.6**: 分析类比结果和偏差 → 本 capsule 第 4 步

---

### 运行与复现

**脚本**: `Labs/L01-word-vectors/cosine-similarity-analogy.py`

**Notebook**: `Labs/L01-word-vectors/cosine-similarity-analogy.ipynb`

**Colab**: ⚠️ GitHub 推送失败（TLS 握手错误），Colab 链接暂不可用。本地 notebook 已执行并包含完整输出。

**运行命令**:
```bash
cd /workspace/cs224n-study
.venv/bin/python Labs/L01-word-vectors/cosine-similarity-analogy.py
```

---

### 容易误解的地方

> **[!warning] 常见误区]**
> 1. **king-queen 余弦不高（0.37）不代表它们"不相似"**：toy 向量只有 6 维，性别维度影响被放大。真实 300 维向量中 king-queen 余弦通常 0.7-0.8。
> 2. **类比方向很重要**：man:king::woman:? 和 king:man::woman:? 的结果完全不同。
> 3. **cos=1.0 是因为 toy 数据设计**：真实 GloVe 向量不会这么完美，但类比效果仍然很好。

---

### 相关概念

- [[Lectures/L01-word-vectors/00-concept-glossary#cosine-similarity|cosine-similarity]]
- [[Lectures/L01-word-vectors/00-concept-glossary#analogy|analogy]]
- [[Lectures/L01-word-vectors/00-concept-glossary#dot-product|dot-product]]
- [[Lectures/L01-word-vectors/00-concept-glossary#dense-vector|dense-vector]]
- [[Lectures/L01-word-vectors/00-concept-glossary#pretrained-word-vectors|pretrained-word-vectors]]

---

```yaml
numeric_provenance:
  run_log: Labs/L01-word-vectors/run-log.md#run_id 20260610T094108Z__t_2f043112__cosine-similarity-analogy
  stdout: Labs/L01-word-vectors/outputs/cosine-similarity-analogy-stdout.txt
  checked_values:
    - claim: "cos(king, queen) = 0.3725"
      source: "stdout 第 1 步手算示例输出"
      status: copied_from_output
    - claim: "cos(king, man) = 0.6459"
      source: "stdout 第 1 步手算示例输出"
      status: copied_from_output
    - claim: "man:king::woman:? → #1 queen (cos=1.0000)"
      source: "stdout 第 2 步类比 1 结果"
      status: copied_from_output
    - claim: "boy:girl::man:? → #1 woman (cos=1.0000)"
      source: "stdout 第 2 步类比 3 结果"
      status: copied_from_output
    - claim: "teacher:student::king:? → #1 prince (cos=0.7668)"
      source: "stdout 第 4 步失败案例结果"
      status: copied_from_output
    - claim: "热力图 king-queen = 0.3725, king-man = 0.6459, man-boy = 0.5269"
      source: "stdout 第 3 步相似度矩阵和读图说明"
      status: copied_from_output
```
