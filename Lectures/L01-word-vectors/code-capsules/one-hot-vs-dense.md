## one-hot-vs-dense — One-hot 向量 vs Dense 向量 {#one-hot-vs-dense}

> [!info] 这个 Capsule 在看什么
> **概念**：[[Lectures/L01-word-vectors/00-concept-glossary#one-hot-encoding|one-hot encoding]] 让每个词成为正交基向量，所有不同词的点积都是 0，无法编码相似度；[[Lectures/L01-word-vectors/00-concept-glossary#dense-vector|dense vector]] 把词映射到低维连续空间，语义相近的词方向接近，可以用[[Lectures/L01-word-vectors/00-concept-glossary#cosine-similarity|余弦相似度]]衡量。
>
> **为什么不能只靠文字**：Slides p19-22 展示了 one-hot 和 dense 的概念，但只有亲手算点积、看矩阵，才能真正理解为什么 one-hot 的 hotel·motel = hotel·apple = 0——这个「所有词等距」的问题有多致命。
>
> **官方锚点**：Slides p19-p22; Notes §2.2 Eq.1-2

### 运行方式

**Colab 打开**（推荐）：[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/dafengbaocy/cs224n-study/blob/main/Labs/L01-word-vectors/one-hot-vs-dense.ipynb)

**本地运行**：
```bash
cd /workspace/cs224n-study
.venv/bin/python Labs/L01-word-vectors/one-hot-vs-dense.py
```

### 这段代码在做什么

1. 用 6 个词（hotel, motel, bank, atm, apple, tea）构建 [[Lectures/L01-word-vectors/00-concept-glossary#one-hot-encoding|one-hot]] 向量
2. 计算 one-hot [[Lectures/L01-word-vectors/00-concept-glossary#dot-product|点积]]矩阵——所有非对角线都是 0
3. 构建 toy [[Lectures/L01-word-vectors/00-concept-glossary#dense-vector|dense vector]]（4 维，模拟训练后结果）
4. 计算 dense 余弦相似度矩阵——同组词（hotel-motel: 0.998）远高于跨组词（hotel-apple: 0.053）

### 运行后先看哪里

> [!tip] 输出解读
> 1. **One-hot 点积矩阵**：对角线 = 1（自身），非对角线全 = 0。无论 hotel 和 motel 多近，点积都是 0。
> 2. **Dense 余弦相似度矩阵**：左上角（hotel-motel = 0.998）、中间（bank-atm = 0.997）、右下（apple-tea = 0.999）明显亮于跨组区域。
> 3. **对比表格**：同组平均 cos_sim = 0.9979，跨组平均 = 0.0899，差值 0.908。

### 关键输出

**One-hot 点积矩阵**（所有不同词对 = 0）：

```
           hotel   motel    bank     atm   apple     tea
   hotel    1.0     0.0     0.0     0.0     0.0     0.0 
   motel    0.0     1.0     0.0     0.0     0.0     0.0 
    bank    0.0     0.0     1.0     0.0     0.0     0.0 
     atm    0.0     0.0     0.0     1.0     0.0     0.0 
   apple    0.0     0.0     0.0     0.0     1.0     0.0 
     tea    0.0     0.0     0.0     0.0     0.0     1.0 
```

**Dense 余弦相似度矩阵**（同组接近 1，跨组接近 0）：

```
           hotel   motel    bank     atm   apple     tea
   hotel  1.000  0.998  0.119  0.105  0.053  0.071
   motel  0.998  1.000  0.107  0.098  0.048  0.069
    bank  0.119  0.107  1.000  0.997  0.045  0.064
     atm  0.105  0.098  0.997  1.000  0.040  0.063
   apple  0.053  0.048  0.045  0.040  1.000  0.999
     tea  0.071  0.069  0.064  0.063  0.999  1.000
```

**关键对比**：

| 词对 | 关系 | One-hot 点积 | Dense cos_sim |
|------|------|-------------|---------------|
| hotel-motel | 同组：住宿 | 0.0 | 0.9980 |
| bank-atm | 同组：金融 | 0.0 | 0.9971 |
| apple-tea | 同组：食物/饮品 | 0.0 | 0.9985 |
| hotel-apple | 跨组：住宿 vs 食物 | 0.0 | 0.0526 |
| hotel-bank | 跨组：住宿 vs 金融 | 0.0 | 0.1191 |
| motel-atm | 跨组：住宿 vs 金融 | 0.0 | 0.0981 |

### 热力图对比

![One-hot vs Dense 热力图对比](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-174129.png)

> [!tip] 读图指南
> - **左图**（One-hot）：只有对角线有值（蓝色），其余全白（= 0）。这意味着任何两个不同词的相似度都是 0。
> - **右图**（Dense）：三个对角线块（左上 hotel-motel、中间 bank-atm、右下 apple-tea）颜色最深（接近 1），跨块区域颜色浅（接近 0）。
> - **关键结论**：dense vector 成功把「语义相近 = 方向接近」编码进了向量空间。

### 柱状图对比

![One-hot vs Dense 柱状图对比](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-174141.png)

> [!tip] 读图指南
> - 蓝色柱（One-hot）：全是 0，无论词对关系如何。
> - 红色柱（Dense）：同组词（前 3 对）接近 1.0，跨组词（后 3 对）接近 0.1。
> - 虚线左边是同组，右边是跨组——差异一目了然。

### 和课堂内容的对应

| 课堂材料 | 对应内容 |
|----------|----------|
| Slides p19 | One-hot 向量展示：`motel = [0 0 0 0 0 0 0 0 0 0 1 0 0 0 0]` |
| Slides p20 | 正交问题："These two vectors are orthogonal. There is no natural notion of similarity for one-hot vectors!" |
| Slides p22 | Dense vector："We will build a dense vector for each word...measuring similarity as the vector dot product" |
| Notes §2.2 Eq.1-2 | 数学论证：$v_{tea}^T v_{coffee} = v_{tea}^T v_{the} = 0$，"all words are equally dissimilar" |

### 容易误解的地方

> [!warning] 注意
> 1. **Dense 向量的值不是手动设计的**——实际中由模型（如 Word2Vec）训练得到。这里的 toy 向量只是为了演示「训练后应该有的效果」。
> 2. **余弦相似度 vs 点积**：点积受向量长度影响；余弦相似度归一化了长度，只看方向。one-hot 向量长度都是 1，所以两者等价。
> 3. **4 维只是演示**。实际词向量通常 100-300 维。维度越高，能编码的语义信息越丰富。
> 4. **One-hot 不是完全没用**。在分类任务的输出层，one-hot 仍然用作标签表示。它的问题是作为**输入表示**时无法编码相似度。

### 数字来源证明

```yaml
numeric_provenance:
  run_log: Labs/L01-word-vectors/run-log.md#run_id 20260610T094123Z__t_2397e6e3__one-hot-vs-dense
  stdout: Labs/L01-word-vectors/outputs/one-hot-vs-dense-stdout.txt
  checked_values:
    - claim: "hotel-motel one-hot dot = 0.0"
      source: "stdout: 'hotel-motel    Same: lodging                     0.0         0.9980'"
      status: copied_from_output
    - claim: "hotel-motel dense cos_sim = 0.9980"
      source: "stdout: same line"
      status: copied_from_output
    - claim: "同组平均 cos_sim = 0.9979"
      source: "stdout: '同组词平均余弦相似度 = 0.9979'"
      status: copied_from_output
    - claim: "跨组平均 cos_sim = 0.0899"
      source: "stdout: '跨组词平均余弦相似度 = 0.0899'"
      status: copied_from_output
    - claim: "差值 = 0.9079"
      source: "stdout: '差值 = 0.9079'"
      status: copied_from_output
```
