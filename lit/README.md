# 5000m 文献库

**用途**：把这个项目的每一个训练决定，挂到可核实的证据上 —— 并且**同时挂上反对它的证据**。

## 三条硬规则

1. **每条文献必须带 `confidence`（证据强度）和 `applicability`（对 Fajir 的适用性）** —— 一篇 n=15 的业余跑者研究，不能和一个 n=43 研究的 meta 一样重。
2. **必须有 `contradicting-evidence.md`** —— 只有支持性证据的文献库，是宣传材料，不是证据库。
3. **`verified: false` 的条目不许用来做决定** —— 只能作为“待查线索”。

## 分类

| 域 | 回答什么问题 | 当前是否限制因素 |
|---|---|---|
| `aerobic-capacity` | 有氧底座够不够 | 待定（**很可能不是**） |
| `threshold` | LT1/LT2 与 MLSS 的时间剂量 | 待定 |
| `intervals-vo2max` | 间歇的段落、间歇、结构 | **主要是** |
| `running-economy` | 同速度下的耗氧与触地 | **主要是** |
| `strength-concurrent` | 力量与同期训练 | 是（执行层） |
| `periodization` | 块与波的结构 | 是 |
| `recovery-overtraining` | 过度训练信号与单调性 | 是（防错） |
| `psychology` | 动机、精神疲劳、自主性 | 是（防错） |
| `biomechanics` | 步频步幅、触地、肌腱 | 是 |
| `climate-environment` | 热、冷、污染、海拔 | 是（地区约束） |

## 文件

| 文件 | 内容 |
|---|---|
| `bibliography.yaml` | 结构化条目：出处、设计、样本、结论、效应量、适用性、置信度 |
| `00-methods/evidence-rules.md` | 怎么读、怎么分级、怎么把文献落到一次训练上 |
| `01-analysis/competing-hypotheses.md` | **竞争假设**：把“为什么会停”写成可被证伪的几条，逐条用他的数据打分 |
| `01-analysis/contradicting-evidence.md` | **反证清单**：与当前计划矛盾的证据，以及它推翻什么 |

## 更新纪律

- 新增一条 → 必须在 `contradicting-evidence.md` 里问一次：“有没有反例？”
- 每条结论 → 必须写“如果这条错了，训练会改成什么”
- 不做“文献综述”式堆砌：**只收能改变决定的文献**
