# 设备导出解析（以 Garmin 为例）

---

## 1. Garmin 单位陷阱（都踩过）

| 字段 | 单位 | 换算 |
|---|---|---|
| `summarizedActivitiesExport[].distance` | **厘米** | / 100000 = km |
| `summarizedActivitiesExport[].duration` | **毫秒** | / 60000 = min |
| `summarizedActivitiesExport[].elevationGain` | **厘米** | / 100 = m |
| `summarizedActivitiesExport[].avgVerticalOscillation` | **厘米（已经是）** | 不要再除 |
| `summarizedActivitiesExport[].avgStrideLength` | 厘米 | — |
| `summarizedActivitiesExport[].avgRunCadence` | **单腿**步频 | × 2 = 总步频 |
| `summarizedActivitiesExport[].avgDoubleCadence` | 双腿（总）步频 | — |
| `laps[].total_distance` | 米 | / 1000 = km |
| `laps[].total_timer_time` | 秒 | — |
| `avg_stance_time` | 毫秒（触地时间）| — |

### 同一个字段名，两种导出格式，单位不同（最贵的一类坑）

| 字段名 | 汇总 JSON | 逐活动 FIT |
|---|---|---|
| 步幅 | `avgStrideLength` = **厘米** | `avg_step_length` = **毫米**（/10 → cm）|
| 垂直振幅 | `avgVerticalOscillation` = **厘米** | `avg_vertical_oscillation` = **毫米**（/10 → cm）|
| 爬升 | `elevationGain` = **厘米**（/100 → m）| `total_ascent` = **米** |
| 训练负荷 | `activityTrainingLoad` | `training_stress_score`（FIT 里没有前者）|

**自检恒等式（用来给垂直振幅的单位定性）**：

```
avgVerticalOscillation / avgStrideLength × 100  ==  avgVerticalRatio
```

两边单位一致时才成立。实测：`7.17 / 84.68 × 100 = 8.47`，而 `avgVerticalRatio` 正好是 `8.47` ——
所以汇总 JSON 里垂直振幅**已经是厘米**，再除 10 就错了（7.17 cm 会变成 0.717 cm，
看起来像"这个跑者垂直振幅极小"，不会报错）。

**任何"看起来像单位问题"的字段，先找一个包含它的恒等式去验证，不要靠猜。**
导出的字段之间通常有冗余恒等关系（速度 = 步频 × 步幅；垂直比 = 振幅 / 步幅），
它们是免费的验证器。

## 2. 时区陷阱

**同一个导出里，不同来源的时间字段时区规则不同。**

| 来源 | 字段 | 处理 |
|---|---|---|
| `summarizedActivities` | `startTimeLocal` | 已经是"当成 UTC 表达的当地时间" → `utcfromtimestamp(v/1000)`，**不要再加 8 h** |
| `summarizedActivities` | `startTimeGmt` | 真 UTC |
| 逐活动 FIT（`session.start_time`）| ISO 字符串 | **真 UTC → 要 +8 h 才是本地** |

**验证方法**：用一次已知的清晨训练反推。如果算出来是 13:00 或 22:00，时区错了。
（本地清晨 05:30 = UTC 前一日 21:30。）

**两个数据源会重叠**：按时间差 < 900 s 去重。

## 3. 解析 FIT 文件

```bash
pip install fitparse
```

目录结构有两种，脚本要都覆盖：
```
new_data/*.fit                  # 直接放
new_data/<activityId>/*.fit     # 按活动 ID 分目录（更常见）
```

Glob 写法：
```python
fits = sorted(glob.glob(os.path.join(DATA_DIR, "*.fit"))) + \
       sorted(glob.glob(os.path.join(DATA_DIR, "*", "*.fit")))
```

**解析器要点**：
- `fitparse.FitFile(fp)` → 遍历 `ff.get_messages()`
- 要提取的消息类型：`session` / `lap` / `record` / `event` / `workout_step`
- 跳过 `bytes` 类型的字段（无法 JSON 序列化）
- 有 `isoformat()` 的转字符串
- **已解析的跳过**（`if os.path.exists(outp): continue`），所以可以在新 FIT 到达后重跑
- 逐秒 `record` 数据很大（单次课 2000–3000 条），**只保留需要的字段**

保留字段建议：
```python
RECORD_KEEP = ['timestamp','heart_rate','enhanced_speed','speed','cadence','temperature',
               'enhanced_altitude','distance','power','stance_time','vertical_oscillation',
               'vertical_ratio']
```

## 4. 目录扫描的注意事项

- 完整导出目录可能上万文件 → **先 `os.walk` 限深（depth ≤ 4）+ 计时保护**，
  超时就 break 并报告扫到哪里
- 某些目录 `ls -la` 会超时（文件数太多）→ 用 Python 遍历代替
- 找文件用 `os.walk` 按扩展名归类，先看**每类的数量和样例路径**，再决定读哪些

## 4b. 完整导出里藏着「你以为没有的」历史原始数据

完整 Garmin 导出（“Export Your Data”）里有一个目录：

```
Data/DI_CONNECT/DI-Connect-Uploaded-Files/UploadedFiles_*_Part1|Part2/
```

**里面是逐活动原始 FIT，时间范围和 `summarizedActivities.json` 一样** ——
也就是**你以为只有汇总、没有逐秒记录的那段历史**。
本案：9834 个 FIT 里只有 **491** 个含运动 session，范围 2025-02-11 → 2026-08-28。

**这决定了你能不能对一年前做逐秒分析（心率分档、逐圈触地、逐秒配速），
还是只能用汇总里的会话平均值。**

### 坑：随机抽样会让你得出「没有这种文件」

抽查 20 个文件、`get_messages("session")` 全空 → 很容易得出「这些不是活动文件，旧数据没逐秒」。
**结论是错的** —— 只是 ~95% 的文件是监控/健康类，随机抽样几乎必然抽不到活动文件。

**正确做法：全量建一次索引，落到 JSON，之后都读索引。**

```python
index = []
for p in all_fit_paths:                      # os.walk 收全部 *.fit
    for m in fitparse.FitFile(p).get_messages("session"):
        a = {x.name: x.value for x in m}
        if a.get("start_time") and a.get("total_distance"):
            index.append({"file": os.path.relpath(p, UP),
                          "t": a["start_time"].isoformat(),      # 真 UTC！
                          "sport": a.get("sport"),
                          "km": a["total_distance"] / 1000,
                          "hr": a.get("avg_heart_rate"),
                          "dur": a.get("total_timer_time")})
        break                                # 一个文件只取第一个 session
json.dump(index, open("_uploaded_index.json", "w", encoding="utf-8"))
```

9834 个文件全量扫约 **3 分钟**，产出 491 条索引。**跑一次就够，之后读索引是毫秒级。**

**建完先打印「条数 + 时间范围」再决定能不能做逐秒分析** ——
不要写完分析脚本才发现数据不在。

**索引里的 `t` 是真 UTC（FIT `start_time`）**，匹配日期时要 +8 h（见 §2）。
**旧数据匹配日志时用「日期 + 距离（保留一位小数）」，不要只用日期** —— 一天两练会撞车。

### 索引要存够字段，否则你还要回去重开 FIT

本案索引只存了 `km / hr / dur / t`。结果做「逐次课」对照表时，触地 / 步频 / 步幅
**整列是空的** —— 那三个字段在 `session` 消息里，只能再扫一遍 491 个文件补上。

**索引时就把会用到的一次抽全**：`avg_stance_time` / `avg_running_cadence` /
`avg_step_length` / `max_heart_rate` / `total_ascent`。多存几列的成本接近零，
漏存的成本是一次全量重扫。

（另一个细节：同一份导出里，一个文件可能有多条 `session`（多活动文件），
**只取第一条**并 `break`，和主索引保持一致。）

## 4c. 导出包的位置会变 —— 绝不要硬编码路径

每次从 Garmin 重新导出，都会得到一个 **uuid 命名的文件夹**：

```
Data/81e54d86-a8a9-415e-9db8-9c0176b2948f_1/DI_CONNECT/DI-Connect-Fitness/...
Data/DI_CONNECT/...                    ← 上一次导出的位置，这次会被删掉
```

**硬编码旧路径的失败形态是最坏的一种：静默。**
脚本找不到 JSON → 返回空列表 → 照样跑完、照样写日志、照样"成功"，
只是**历史一条都没进来**。没有任何报错指向真正的原因。

**做法：启动时自动探测，不要写死。**

```python
def find_export():
    """取 Data/*/DI_CONNECT 或 Data/DI_CONNECT 里含 DI-Connect-Fitness 的那个。"""
    cands = []
    d = os.path.join(BASE, "Data")
    for x in sorted(os.listdir(d), reverse=True):      # 新的 uuid 目录排在前面
        p = os.path.join(d, x)
        if not os.path.isdir(p):
            continue
        if os.path.isdir(os.path.join(p, "DI_CONNECT")):
            cands.append(os.path.join(p, "DI_CONNECT"))
        elif os.path.isdir(os.path.join(p, "DI-Connect-Fitness")):
            cands.append(p)
    cands.append(os.path.join(d, "DI_CONNECT"))        # 老布局兜底
    for c in cands:
        if os.path.isdir(os.path.join(c, "DI-Connect-Fitness")):
            return c
    return None                                        # 找不到就要报出来
```

**找不到时打印一句，不要静默返回空。** 并在每次跑的时候把选中的导出包和它覆盖的时间范围打出来。

## 4d. 历史被切成好几个 `summarizedActivities` 文件

**一次导出里的汇总历史可能分成多个文件，必须全部读并去重。** 实测：

| 文件 | 条数 | 覆盖 |
|---|---|---|
| `hheu..._301_summarizedActivities.json` | 241 | 2025-02-12 → 2025-11-05 |
| `hheu..._1_summarizedActivities.json` | 300 | 2025-11-07 → 2026-10-10 |

只读 `_1_` 那个（旧版脚本的写法）会**丢掉前面 9 个月**，而且同样不报错。

```python
files = sorted(glob.glob(os.path.join(DIROOT, "DI-Connect-Fitness",
                                      "*summarizedActivities*.json")))
raw_acts = {}
for f in files:
    raw = json.load(open(f, encoding="utf-8"))
    arr = raw[0]["summarizedActivitiesExport"] if isinstance(raw, list) \
          else raw["summarizedActivitiesExport"]
    for a in arr:
        raw_acts.setdefault(str(a.get("activityId")), a)     # 按 activityId 去重
print(f"{len(files)} 个汇总文件 → {len(raw_acts)} 条活动")
```

**把"读了几个文件、共多少条"打出来** —— 这是唯一能一眼看出"少读了一个文件"的地方。

## 4e. 换了导出包 → 你的 FIT 索引会整体失效

`_uploaded_index.json` 里存的是**相对旧导出包的路径**。新导出落地后旧目录被删，
索引里**每一条都指不到文件**。

**这不一定致命 —— 前提是你的派生值有缓存。** 本案 `_act_cache.json` 里已经存了
全部 541 条的 TRIMP 与结构，所以历史行照常显示；
如果每次都必须回读 FIT 才能算，重新导出一次历史就全空了。

两条规矩：

1. **建索引的池子要先过 `os.path.exists`**，路径死了就跳过，不要让它把主流程拖垮：

```python
pool = []
if UP and os.path.isdir(UP):
    for x in index:
        p = os.path.join(UP, x["file"])
        if os.path.exists(p):                 # 死掉的路径直接丢
            pool.append((t, x["km"], p))
elif index:
    print("  ! FIT 索引已失效（导出包换了位置）—— 历史行沿用缓存里的派生值")
```

2. **派生值要缓存到本地 JSON，并带版本号**（见 `persistent-log-workbook.md` §1c）。
   缓存是重导之后历史的唯一依靠。

**想恢复历史的逐秒分析能力，就对新导出包重跑一次全量索引**（§4b）—— 不重跑就只能读缓存。

## 5. 长时抓取/解析任务

用 `terminal(background=True, notify=True)` 跑，不要占 foreground timeout。
进度写到 stdout 并 `flush=True`，这样 `process(action='poll')` 能看到进展。

## 6. 从逐秒 record 里找"段"

设备不会把间歇段标清楚，但可以用速度阈值切分：

```python
# 例：找加速跑段（速度 > 4 m/s 且连续 >= 5 秒）
segs = []
cur, inrun = [], False
for i, r in enumerate(records):
    sp = r.get("enhanced_speed") or r.get("speed") or 0
    if sp > 4.0:
        inrun = True; cur.append((i, sp, r.get("cadence"), r.get("stance_time")))
    else:
        if inrun and len(cur) >= 5: segs.append(cur)
        inrun = False; cur = []
```

**这个切分在有 GPS 漂移的场景（爬楼梯）会失败** —— 那时速度字段本身是噪声。
爬楼梯只能靠 `laps` 的分段时间（如果用了手动分段）。

## 7. 复现脚本的位置约定

把可复跑的脚本放在数据目录里，不要每次手敲：
- `fetch_weather.py` —— 气象抓取 + 缓存
- `parse_all.py` —— FIT 批量解析（覆盖子目录）
- `heat_analysis.py` —— 露点匹配比较

**脚本要幂等**（已处理就跳过），这样在新数据到达后直接重跑即可。
