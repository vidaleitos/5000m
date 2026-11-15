---
name: fajir-training-review
description: Use when reviewing Fajir's training data or next block.
---

# FajirXiao 训练复盘工作流

每次"看数据 / 定计划"都走这条流程。不要凭记忆回答，去读真实数据。

## 数据位置（本机，不要猜）

```
D:/running/GarminData/IDEA.md                      # 长期目标
D:/running/GarminData/ATHLETE_MODEL.md             # 运动员模型（活文件，复盘后更新）
D:/running/GarminData/PLAN_*.md                    # 各区块计划
D:/running/GarminData/Data/DI_CONNECT/DI-Connect-Fitness/
    hheu010@gmail.com_1_summarizedActivities.json  # 全量活动（导出日为止，最新到 2026-08-29）
D:/running/GarminData/Data/new_data/<id>/<id>_ACTIVITY.fit_parsed.json   # 最近的逐 lap 明细
D:/running/GarminData/Data/DI_CONNECT/DI-Connect-Metrics/
    MetricsMaxMetData_*.json        # V̇O2max 序列
    RunRacePredictions_*.json       # 5K/10K 预测序列（最好的趋势指标）
    TrainingHistory_*.json          # training status
D:/running/GarminData/Data/DI_CONNECT/DI-Connect-Wellness/
    *_healthStatusData.json         # HRV / 静息HR
    *_sleepData.json                # 睡眠
    130074653_heartRateZones.json   # 心率区间设定
```

## 单位陷阱（踩过）

- `summarizedActivitiesExport[].distance` 是**厘米**（/100000 = km），`duration` 是**毫秒**
- `summarizedActivitiesExport[].startTimeLocal` 已经是"当成 UTC 表达的当地时间"→ `utcfromtimestamp(startTimeLocal/1000)` **不要再加 8 h**
- `new_data/*_ACTIVITY.fit_parsed.json` 的 `session.start_time` 是**真 UTC** → **要 +8 h** 才是本地（本地清晨 05:30 = UTC 前一日 21:30）
- `laps[].total_distance` 是米，`total_timer_time` 是秒
- `avg_step_length` 单位是 **cm**（/10 → m）；`avg_running_cadence` 是**单腿**步频 → ×2 = 总步频
- 两个数据源有重叠：按时间差 <900 s 去重
- 读大目录前先 `os.walk` 限深 + 计时保护。`Data/DI_CONNECT` 直接 `ls -la` 会超时

## 标准分析（每次至少跑这几项）

1. **周量序列**（全史）— `isocalendar()` 分周，看宏观趋势和断点，同时看每周硬课数（maxHR ≥175）
2. **强度分布**（近 8 周 vs 上一个最强区块）— 按会话平均配速分带。会话平均会把间歇课糊掉，所以间歇课要单独看 lap
3. **CS / D′** — 用两个最可靠的计时点解双点模型：`CS = (d2-d1)/(t2-t1)`，`D' = d2 - CS*t2`
4. **%CS 换算** — 所有配速都用 %CS 表达，不用绝对配速区间
5. **生物力学** — 逐 lap 求 corr(速度, 步频) 和 corr(速度, 步幅)、各配速带的触地时间/垂直振幅/垂直比
6. **恢复状态** — HRV / 静息HR（是否 IN_RANGE）、睡眠时长、Garmin training status
7. **温度** — 月度平均最高温。这是最大的混淆项，没有它会把夏天的慢误读成实力下降

## 复盘的判读原则

- 会话命名编码了训练体系：`三/N` 数字体系（2025-08→2026-07）vs 意大利体系 `Rigen/Allunghi/Medio/FL/Special Block/Ripetute`（2026-07 起）。命名变了意味着体系变了，先搞清楚为什么
- 他的调速方式是**步幅**（r≈0.99），步频几乎恒定（CV≈3%）。永远不要建议他改步频
- 他 19 个月零伤停 → 量的天花板是**睡眠和恢复**，不是组织耐受
- 高温（>28 °C 最高温）下 HR 高 5–12 bpm，此时**配速和呼吸优先于 HR**

## 复盘后必须做的

- 更新 `ATHLETE_MODEL.md`（改数字 + 追加更新日志版本条目）
- 如果结论变了，说明**为什么**变，不要偷偷改
- 如果做了测试，重算 CS/D′，更新配速表
- 输出必须带**置信度**和**不确定性**

## 汇报格式

直接、专业、不废话。给他数字和因果链，不给"建议可以考虑"。
中文。允许推翻自己上一次的判断。
