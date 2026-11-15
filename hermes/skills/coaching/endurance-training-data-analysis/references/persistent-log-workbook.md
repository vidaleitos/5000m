# 持久化训练日志工作簿（Excel）

分析只活在聊天里就会死。**交付物之一是一个运动员能自己天天维护、并从中读出趋势的日志。**
这份文件记录怎么做出来、以及那些会静默毁掉它的坑。

---

## 1. 架构：追加式生成器 + 活公式工作簿

不要手搓表格。**一个脚本 + 一个工作簿**：

```
build_log.py                  生成器（幂等、只追加）
<Athlete>_训练日志.xlsx       工作簿（活公式，跑一次脚本刷新）
```

**核心契约：脚本只追加"还没有进过日志"的活动，永不触碰已有行。**
运动员手填的列（类型 / 结构 / RPE / 备注 / 主观感受）**必须活过一次又一次重跑** ——
否则他填三天就会放弃。

```python
# 列位置一律按表头名字查 —— 绝不写死列号（见 §1a）
cm = {}
for c in range(1, ws.max_column + 1):
    h = ws.cell(1, c).value
    if h not in (None, ""):
        cm[str(h).strip()] = c

idc = cm.get("活动ID")                        # 身份列在就优先用它
def key_of_row(r):
    if idc:
        v = ws.cell(r, idc).value
        if v not in (None, ""):
            return "id|" + str(v)
    d  = ws.cell(r, cm.get("日期", 1)).value   # 退路：日期 + 距离
    km = ws.cell(r, cm.get("距离 km")).value if cm.get("距离 km") else None
    if isinstance(d, dt.datetime) and isinstance(km, (int, float)):
        return f"dk|{d:%Y-%m-%d}|{km:.3f}"
    return None

existing = {k for r in range(2, ws.max_row + 1) if (k := key_of_row(r))}

def akey(a):
    return ("id|" + str(a["id"])) if idc else f"dk|{a['dt']:%Y-%m-%d}|{a['dist_km']:.3f}"

new = [a for a in acts if akey(a) not in existing]

# 护栏：整表重导的特征就是「新增数 ≈ 总数」。宁可停，也不写坏。
if existing and len(new) > max(40, len(existing) * 0.4):
    print(f"!! 拒绝写入：要新增 {len(new)} 条，而已有 {len(existing)} 条 —— 这像是整表重导。")
    print("   常见原因：识别用的列（活动ID / 日期 / 距离 km）被删了或改了名。没有做任何修改。")
    return

start = ws.max_row + 1 if ws.max_row > 1 else 2
for i, a in enumerate(new):
    for j, v in enumerate(log_row_values(a, wx), 1):
        col = cm.get(LOGFIELDS[j - 1][0])      # 按名字取列号
        if col is None:
            continue                            # 表里没有这一列 → 跳过，不写错地方
        ws.cell(start + i, col, v)
```

### 1a. 列的位置会变 —— 按名字查，永不写死列号

**这是本案付出过真实代价的一条。** §1 上面那段代码的第一版写死了「活动ID 在第 4 列」。
运动员后来在 Excel 里把 `训练日志` 从 32 列精简到 15 列，第 4 列变成了「距离 km」。于是：

```
日志里已有 429 条，需要新增 544 条       ← 429 是「不同距离值」的个数，不是活动数
已写入 544 行（543 → 1086）              ← 整份历史被重新追加了一遍
```

**它对不上任何一条已有记录，于是判定 544 条全部是新的 —— 静默地写了一整份重复。**
541 行变 1086 行，而输出看起来只是"数字有点大"。

三条规矩：

1. **列号只从表头文字解析，不从位置。** 增删、换序、改名都不再会让脚本写错地方；
   表里没有的列就跳过（打印出来让运动员知道），**不要回退到"第 N 列"**。
2. **身份键要有退路。** 活动ID 没了就用 **（日期 + 距离，三位小数）** —— 足够唯一。
   不要因为身份列消失就放弃匹配、更不要因此整份重写。
3. **必须有一个"这像是整表重导"的护栏，宁可停也不写。**
   判据：`新增数 > max(40, 已有数 × 0.4)`。护栏触发时**一个字节都不动**并说明最可能的原因。
   最常见的成因就是「识别用的列被删/改名了」—— 而那是一个**合法**的改动，不该被当成故障。

**两个附带教训：**

- **怎么判断布局是被人在 Excel 里改的，而不是脚本写坏的：去看汇总页的公式。**
  Excel 删列时会**自动重写引用它的公式**，所以 `日汇总`/`周汇总` 的引用会跟着平移到
  新布局里正确的列上、数字仍然对（本案引用落在 `A/C/D/E/F/J` = 日期/时段/距离/时间/气温/TRIMP）。
  脚本改布局不会有这个行为。本案就是这样确认「这是一次有意的精简」，从而没有去"修复"它。
- **`shutil.copy2` 会保留 mtime**（§1b 用的就是它）。所以追查"布局是哪一次改的"时
  **mtime 不可信** —— 两个内容不同的文件可以有同一个时间戳。证据要看内容
  （`<dimension ref>`、`<cols>`、第 1 行的单元格集合），不要看时间。

**布局是运动员的选择，不是故障。** 精简/重排列是他表达"我关心哪些字段"的方式。
脚本要做的是**适应任何布局**，而不是要求他改回来 —— 那会让他觉得这份交付物不是他的。

**必须验证这个契约**（不然第一次重跑才发现就晚了）：
1. 往某个手填格里写一个哨兵值（例如 `手填内容请勿覆盖`）
2. 重跑脚本
3. 读回：哨兵还在吗？行数是不是没变？

追加模式下正确输出形如 `日志里已有 537 条，需要新增 0 条`。

### 1b. 交付物同时存在于两处时 —— 直接 `cp` 一份是数据丢失陷阱

生成器目录不是他日常打开的地方。你会很自然地把工作簿复制到桌面（他真正会打开的地方），
**然后他就在那一份里填 RPE 和备注，而下一次跑脚本读的是生成器目录那份** ——
他填的东西被一个旧版本覆盖，不报错、不提示，三天后才发现。

**正确做法：主文件 = 两份里「修改时间较新的那一份」，保存后同步到另一份。**

```python
def resolve_paths():
    cands = [p for p in (desk, local) if p and os.path.exists(p)]
    if not cands:
        return local, (desk or local)
    master = max(cands, key=os.path.getmtime)
    other  = local if master == desk else (desk or local)
    return master, other

MASTER, OTHER = resolve_paths()
wb = load_workbook(MASTER)        # 读他刚才编辑过的那份
...
wb.save(MASTER)
shutil.copy2(MASTER, OTHER)       # 同步回去，两边始终一致
```

**脚本必须打印它选定的主文件**（形如 `追加模式 | 主文件: D:\...\xxx.xlsx`）——
否则下一次你或他都会怀疑到底改的是哪一份。

**桌面路径不要硬编码。** 本机桌面被重定向到了 `D:\fjFiles`（**不是** `C:\Users\<user>\Desktop`），
从注册表读，取不到再回退：

```python
import winreg
k = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
desk = winreg.QueryValueEx(k, "Desktop")[0]
```

**这个契约和 §1 那个一样，必须实测，而且要在*另一份*上测**：
往**桌面那份**写哨兵值 → 重跑 → 确认 (a) 脚本报的主文件是桌面那份、
(b) 哨兵还在、(c) 两份 MD5 一致。只测生成器目录那份等于没测 —— 会出问题的正是另一份。

**验收也要在他会打开的那一份上做**：公式错误扫描、`CalculateFullRebuild` 重算验证，
对着两份里他实际用的那一份再跑一遍。

---

## 1c. 「只追加」的盲点：新加的列在旧行上是空的

§1 的契约（**永不触碰已存在的行**）保护了手填内容，但它有一个直接后果：

> **你后来加的任何一个派生列，在已有几百行上全部是空白。**

而且是静默的 —— 追加模式输出 `需要新增 0 条`，看起来一切正常，
他只能自己发现右半边全是空的。

**必须配一个回填 pass，并且把列分成两类：**

```python
# 纯计算列（从不手填）→ 每次重算并覆盖
if tp is not None and ws.cell(r, COL_TRIMP).value != tp:
    ws.cell(r, COL_TRIMP).value = tp

# 可编辑的自动列（结构 / 工作总量 / 工作配速 / 恢复）→ 只在空白时填
if cell.value in (None, ""):
    cell.value = v
```

**分界线是"运动员能不能改它"，不是"它是不是算出来的"。**
结构列是算出来的，但列名写了"可改"，所以他改过的值必须活下来；
TRIMP 没有任何手改的理由，覆盖它是唯一不产生陈旧数据的做法。

### 派生指标的缓存要带版本号

这些算法你会改三五次。没版本号的话，每次改动都只能删缓存全量重算。

**关键技巧：把不同派生量的版本号分开。** 结构识别算法改了，
TRIMP 不需要重算（它不依赖结构算法），而重算 TRIMP 要读逐秒心率流、
比重算结构贵一到两个数量级：

```python
need_t = (c is None) or (c.get("trimp") is None)          # 心率流，贵
need_s = (c is None) or (c.get("sv") != STRUCT_VER)       # 分圈，便宜
if need_t:
    laps, hrs = _one_pass(p); st = structure_from_laps(laps); tp = trimp_from_hrs(hrs)
elif need_s:
    st = structure_from_laps(_lap_pass(p))                 # 只走便宜那条
```

**并写一个独立的并行重算脚本**（`refresh_structs.py`），不要每次都重跑整个生成器。
注：`get_messages("lap")` 仍然解析整份文件，"只读分圈"并不真正更快 —— 
真正的加速来自多进程（537 文件：单线程 10 min → 8 进程 165 s）。

### 结构列怎么算出来的

见 **`references/session-structure-inference.md`**（含判别式、必须有的速度下限、
正负例验收法、以及 TRIMP 负荷列）。

---

## 2. 表结构

按"回答什么问题"拆，不要一张大表：

| Sheet | 一行是 | 谁填 |
|---|---|---|
| **说明** | 每个 sheet 是什么、哪些列自动、初判规则、数据源、导出边界 | 你 |
| **训练日志** | 一次活动 | 左 21 列自动，右 10 列手填 |
| **日汇总** | 一个自然日 | 活公式 |
| **周汇总** | 一周（周一为周起始） | 活公式 |
| **测试与PB** | 一次标准化测量 | 手填（预填已知 PB） |
| **力量日志** | 一次力量课的某个动作 | 手填 |
| **课表模板** | — | 空白模板 |
| **图表** | — | 从周汇总取数 |

### 训练日志的列分组

用表头底色把三十来列分组，运动员扫一眼就知道哪些是机器给的、哪些要自己写：

```
基本（日期/星期/时段/活动ID/项目）       深蓝
距离与配速（距离/时间/配速/爬升）         中蓝
心率（平均/最大）                        橙
机械（步频/步幅/触地/垂直振幅/垂直比）    绿
环境（气温/露点/风速）                   紫
负荷（有氧TE/设备负荷/TRIMP）          灰
质量课（类型/结构/工作总量/工作配速/恢复）金  ← 可编辑的到这里
主观（RPE/腿/心肺/症状/备注）            红
```

**手填列必须集中在右侧并单独上色。** 混在自动列中间 = 他每次都要找。

### 几个刻意的设计

- **露点列加条件格式**（<12 绿 / 12–18 黄 / >18 红）。理由：露点是配速能不能横向比较的
  **唯一前提**，让它一眼可见比写十行说明有用。
- **"结构"列**（`4×2000m rec 2:01`）和"工作总量 / 工作配速 / 恢复"是要认真填的 ——
  那对应**工作/恢复比**，比会话平均配速有用得多。
- **冻结窗格放在第一个手填列**（`F2`）而不是 `A2`，这样横向滚动时日期和距离一直在。
- 加自动筛选、加下拉校验（类型 / RPE / 腿感）。

### 记录页 vs 计划页 —— 运动员自己订计划时，后者才是交付物

当运动员开始自己订计划（本案 2026-10 起），交付物从"我写一份计划给他"变成
**"一个他往里写计划的模板"**。差别很大：计划是我给的，**模板是逼他做出我会做的那些判断**。

**计划页必须把判断放在动作表前面。** 那几段的顺序不是分类，是决策顺序：

| 段 | 内容 | 作用 |
|---|---|---|
| ① 本周判断 | 当前认定的限制因素 / **这一条还是限制吗？** / 本周排在哪几天 / 取舍 | 整页的核心，见下 |
| ② 必须排时间的 | 动作 ｜ **位置（规则，不是星期）** ｜ 组×次 ｜ 目标刺激 ｜ 实际 | — |
| ③ 挂钩子的 | 动作 ｜ **频率**（每天 / 每周 3 次） ｜ 剂量 | — |
| ④ 本周环境 | 器械 / 时间紧的天 / 缺什么 | 让"条件"是可见的变量，而不是藏在动作表里 |
| ⑤ 周末复盘 | 五个问题，见下 | — |

**① 的第二行是整页的核心。** 它把"该不该加量"变成一个**必须先回答**的问题，
而且答案只有两支 —— **"不是限制了"那一支明确指向横向转移，不是加难度。**
它把 `training-block-design` §13 的 stop-loss 规则做成了一个空行：不填，就不能往下走。

**② 的"位置"栏写排期规则、不写星期**：星期会变（换课、天气、作息），
"质量课之后 48 小时"不会变。这是 `training-block-design` §7 那个
「效果是否取决于什么时候做」判据的可填版本。

**⑤ 的问题必须逐个对应已知的失败模式**，不能是"这周怎么样"：

| 问题 | 挡住的错 |
|---|---|
| 哪个动作变强了 | 改了难度再说"变强"不算 —— 要**同一剂量**下比 |
| 哪个动作没有任何变化 | **不要默认加剂量**，先重审：动作 → 剂量 → 假设 → 优先级 |
| 哪个能力已经不是限制了 | 横向转移容量，不是给同一个动作继续加难度 |
| 哪个动作该退役了 | 退役 ≠ 没价值 |
| 下周只改一件事 | 改一件才看得出是哪一件起作用 |

**使用契约：整块复制到新的一周，不要在原来的上面改。**
往回翻的时候，**那一周当时的判断比那一周的动作更有价值** —— 动作到处都查得到，
"我当时认为限制因素是什么、后来为什么改了"查不到。
这和 §1 的追加式契约是同一个原则：**历史不能被下一次编辑抹掉。**

---

## 3. Excel 公式陷阱（这些是踩过的）

### `SUMPRODUCT` 的第二个参数不能是裸布尔数组

```excel
=SUMPRODUCT((A:A>=d)*(A:A<=d+6), (V:V="质量课"))      → 恒为 0   ❌
=SUMPRODUCT((A:A>=d)*(A:A<=d+6), (V:V="质量课")*1)    → 正确     ✅
```

**更稳的写法是根本不碰 SUMPRODUCT**，改用：

```excel
计数      =COUNTIFS(A, ">="&$A2, A, "<="&$A2+6)
条件计数  =COUNTIFS(A, ">="&$A2, A, "<="&$A2+6, V, "质量课")
求和      =SUMIFS(F, A, ">="&$A2, A, "<="&$A2+6)
求平均    =AVERAGEIFS(R, A, ">="&$A2, A, "<="&$A2+6)
```

`AVERAGEIFS` 比 `SUM/COUNT` 好，因为它**自动忽略空单元格** —— 缺天气的日子不会把均值稀释成 0
（踩过：整月缺露点的周显示 "平均露点 0.0"，而不是空白）。

### 求"最大单次"时可以留 SUMPRODUCT

```excel
=ROUND(SUMPRODUCT(MAX(((A>=$A2)*(A<=$A2+6))*F)), 2)
```
这是**普通公式**，不需要 CSE 数组输入 —— 比 `MAX(IF(...))` 安全。

### 公式写错的代价是延迟的

它不会在生成时失败。它会以 `#VALUE!` 或恒为 0 的形式**出现在他的 Excel 里**，
而你可能几周后才发现。所以下面第 5 节不是可选项。

---

## 4. openpyxl：时长与配速

配速（`4:09.6`）和时长（`1:00:08`）**必须存成真时长**，不能存字符串 —— 否则没法排序、没法算。

```python
import datetime as dt
ws["H2"] = dt.timedelta(seconds=249.6)
ws["H2"].number_format = "[m]:ss.0"        # 显示 4:09.6
ws["G2"] = dt.timedelta(seconds=3608.45)
ws["G2"].number_format = "[h]:mm:ss"       # 显示 1:00:08
```

`timedelta` 能正确 round-trip（`load_workbook` 读回来还是 `timedelta`）。
方括号很重要：`[m]` 表示**累计分钟**，超过 60 分钟不会回绕成小时。

---

## 5. 验证：openpyxl 不算公式

**`openpyxl` 读回的公式单元格是公式字符串，不是值。** 所以"文件能打开"证明不了任何事。

**唯一可靠的验证：真的开一次 Excel，强制全量重算，再读值。**

```python
import pythoncom, win32com.client as w32, time
pythoncom.CoInitialize()          # 必须；否则 DispatchEx 报 CoInitialize has not been called
                                  # （execute_code 的 kernel 是常驻的，上一次 CoUninitialize 之后必须重新初始化）
xl = w32.DispatchEx("Excel.Application")
xl.Visible = False
xl.DisplayAlerts = False
try:
    wb = xl.Workbooks.Open(r"D:\...\xxx.xlsx")
    xl.CalculateFullRebuild(); time.sleep(2)
    w = wb.Worksheets("周汇总")
    print(w.Cells(88, 5).Value)                # 值，不是公式
    err = 0                                    # 错误扫描
    for sh in wb.Worksheets:
        ur = sh.UsedRange
        for row in range(1, min(ur.Rows.Count, 4000) + 1):
            for col in range(1, min(ur.Columns.Count, 40) + 1):
                v = sh.Cells(row, col).Value
                if isinstance(v, int) and v <= -2147483000:
                    err += 1
    print("公式错误:", err)                     # 验收标准 = 0
    wb.Close(SaveChanges=False)
finally:
    xl.Quit(); del xl; pythoncom.CoUninitialize()
```

**排查具体某个公式时**，往空白列写几个候选公式、重算、读 `.Text` —— 比猜快得多。
就是这么定位到 `SUMPRODUCT` 那条的。

### 非侵入式截图：验证"好不好看"

`Range.CopyPicture` + 剪贴板，**不会抢焦点、不会弹窗**：

```python
ws.Range("A1:M16").CopyPicture(Format=2)      # 2 = xlBitmap
time.sleep(0.8)
from PIL import ImageGrab
im = ImageGrab.grabclipboard()
im.save(path)
```

**截图必须自己看**（`vision_analyze`）。只做这一步才发现的问题：复盘问题的标签被相邻合并单元格截断、
单序列折线图的图例把所有分类日期都列成了条目（`chart.legend = None` 解决）、
Excel 默认的平滑多色折线要显式设成单色直线。

### COM 的收尾：孤儿进程与锁文件（代价是延迟的）

§5 那段 `finally: xl.Quit()` 不是礼貌，是**必须**。少一次干净退出就留下一个
**无窗口的 `EXCEL.EXE` 后台进程**；验证跑得多它就会累积（本案一次发现 **6 个**）。

**它的失败形态是延迟的、而且指向错误的文件**：进程还占着工作簿 → 留下一个
`~$<文件名>.xlsx` 锁文件 → 下一次 `wb.save()` 报 `PermissionError`，或者生成器跑不完。
而你会去查生成器的代码 —— 真正的原因在几小时前那次"成功"的验证里。

```bash
# 先数一下有没有累积
MSYS_NO_PATHCONV=1 tasklist /FI "IMAGENAME eq EXCEL.EXE"
```

**清理前必须先确认用户没有正在编辑的表格。** `taskkill /IM EXCEL.EXE /F` 会把他没保存的东西
一起关掉，**不可逆**。顺序不能反：

1. **先列窗口**（`computer_use list_windows`）—— 用户打开的 Excel 一定**有窗口**；
   孤儿是你自己 COM 起来的、`Visible=False`、没有窗口的。
2. 确认只有孤儿之后，**再杀进程**：

```bash
MSYS_NO_PATHCONV=1 taskkill /F /IM EXCEL.EXE
rm -f "$DIR/~\$"*.xlsx          # 锁文件也要删，否则下次照样 PermissionError
```

**`MSYS_NO_PATHCONV=1` 是必须的** —— git-bash 会把 `/F`、`/IM` 当路径翻译，
`taskkill /F` 变成 `taskkill F:\...`，报的错和真实原因毫无关系。（`//F` 也行，前缀变量更稳。）

**最省事的做法是每次验证自己收尾**，而不是攒着清理；但无论怎样，
**跑过几轮 win32com 验证之后都要数一次进程**，因为漏掉一次是静默的。

#### 孤儿可能同时开着*他的*文件 —— 那就不能杀进程

本案那个孤儿（`Visible=False`、无窗口、`CreationDate` 正好是我截图那一刻）
**不只开着日志工作簿，还开着运动员自己的 `W1.xlsx`。**
`taskkill /F /IM EXCEL.EXE` 会把他那份一起带走、且不可逆。

所以顺序是 **先取证 → 能只关工作簿就不杀进程**。

**① 取证：这个进程是谁、什么时候起来的、开的什么文件**

```bash
MSYS_NO_PATHCONV=1 powershell -NoProfile -Command \
  "Get-CimInstance Win32_Process -Filter \"Name='EXCEL.EXE'\" | Select-Object ProcessId,CreationDate,CommandLine | Format-List"
```

`CreationDate` 对上你自己那次 COM 调用的时刻 + `CommandLine` 指向你操作过的工作簿
→ 两条独立证据都有了，基本可以确定是孤儿。（**无窗口 + 是你自己起的**，缺一不可。）

**② 先直接问文件能不能写** —— 比看锁文件可靠，而且是一行：

```python
try:
    open(path, "r+b").close(); print("可写")
except PermissionError:
    print("被占用")
```

**③ 只关那一个工作簿，不动进程**（推荐路线）：

```python
import pythoncom, win32com.client as w32
pythoncom.CoInitialize()
xl = w32.GetActiveObject("Excel.Application")     # 连到*正在运行*的实例，不是新起一个
xl.DisplayAlerts = False
for wb in list(xl.Workbooks):
    print("它打开着:", wb.Name)                   # 先看清楚，再决定
for wb in list(xl.Workbooks):
    if "训练日志" in wb.Name:                      # 只关目标
        wb.Close(SaveChanges=False)
```

四条注意：

- **`SaveChanges=False` 是有意的**：盘上那份才是你要的，Excel 内存里那份是旧的。
  让它"保存"会把陈旧的版本写回去。
- **`GetActiveObject` 可能抛 `The object invoked has disconnected from its clients`** ——
  这**不代表失败**。它通常在 COM 拆解时抛出，而实例已经跟着退出了。
  **抛完立刻重新探一次文件可写性**，本案就是这样确认已经解开、
  且 `W1.xlsx` 的 mtime 和大小一字未变。
- **别用 `DispatchEx`** —— 那是新起一个实例，对已有的孤儿无效。
- **每一步之后都要验证"他的文件没被动过"**：操作前记下他的文件 mtime + 大小，操作后比对。

---

## 6. 导出边界：历史表有个硬终点

Garmin 的 `summarizedActivities.json` 是**一次快照**，只覆盖到"导出那一天"。
之后的新数据只存在于逐活动 FIT 里。两条路径都要接：

1. **历史** —— JSON（一次导入几百条）
2. **日常** —— `new_data/<activityId>/<activityId>_ACTIVITY.fit`（每天一两个）

**并在说明页写清"历史表需要隔几个月从 Garmin 重新导出一次"** ——
否则半年后会有人（包括未来的你）以为那段时间没跑。

同理，合并两个源时要按活动 ID（或时间邻近）去重，并说明每个源各自覆盖到哪一天。

### 6b. 生成器是在**他的** shell 里跑的 —— 解释器不一定对

本案真实报错：`ModuleNotFoundError: No module named 'openpyxl'`，**位置在 `main()` 快结束时**
（数据已经读完，只在写表那一步炸）。原因：同一条 `python` 命令在他的 shell 里解析到另一个解释器
（`D:\apps\python`）——那个装了 `fitparse`、没装 `openpyxl`。
我的 shell 里 `python` 指向 Hermes 的 venv，两个包都有，**所以我永远测不出这个问题。**

**不要靠"告诉他用哪个解释器"解决。** 两条一起上：

1. **脚本在 import 阶段自愈**（放在最前面，别等到 `main()` 里才 import）：

```python
import importlib.util, subprocess, sys

def _ensure_deps():
    need = [p for m, p in (("openpyxl", "openpyxl"), ("fitparse", "fitparse"))
            if importlib.util.find_spec(m) is None]
    if not need:
        return
    print(f"缺少依赖 {need}，正在用当前解释器安装：{sys.executable}")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", *need])
    except Exception as e:
        print("自动安装失败:", e)
        print(r"改用这个解释器运行：C:\...\venv\Scripts\python.exe build_log.py")
        sys.exit(1)

_ensure_deps()
```

2. **给一个双击就能跑的 `.bat`**，它自己挨个试解释器，挑第一个 `import openpyxl, fitparse` 通过的：

```bat
@echo off
cd /d "%~dp0"
set "PYEXE="
call :try "C:\...\venv\Scripts\python.exe"
call :try "D:\apps\python\python.exe"
call :try "python"
if "%PYEXE%"=="" set "PYEXE=python"
echo [interpreter] %PYEXE%
"%PYEXE%" build_log.py
pause
exit /b

:try
if "%~1"=="" exit /b
"%~1" -c "import openpyxl, fitparse" >nul 2>&1
if errorlevel 1 exit /b
if not "%PYEXE%"=="" exit /b
set "PYEXE=%~1"
exit /b
```

**用 `if errorlevel 1`（运行时求值），不要用 `if %errorlevel%==0`** —— 后者在批处理里被解析期展开，块内失效。`:try` 里**不要写括号块**，逐行解析才安全。

**并且：交付之前从*他的*那条命令测一次。** 「我这能跑」是最容易漏的验收项 ——
他在用的形态是 `cd D:\running\GarminData && python build_log.py`。

### 6c. 文件被他自己开着 → 不能崩，要另存

§5 讲的是**孤儿 EXCEL.EXE**（我自己 COM 验证漏的收尾）。另一半是**他合法地开着这个表格**
—— 他天天看，这一定会发生，而且会撞在下一次保存上。

```python
def _save_wb(wb, path, quiet=False):
    try:
        wb.save(path)
        return path
    except PermissionError:
        alt = os.path.join(os.path.dirname(path),
                           os.path.splitext(os.path.basename(path))[0] + "_新.xlsx")
        try:
            wb.save(alt)
        except Exception as e:
            print("  ! 保存失败（文件被占用）:", e)
            print("    → 请先关掉 Excel 里打开的这个表格，再跑一次。")
            return None
        print("  ! 原文件被占用，已另存为：", alt)
        return alt
```

**不要因为一次锁就失败退出** —— 他刚跑完的一大堆解析会全白费。也不要在 `except` 里静默 `pass`：
**必须把另存的文件名和"关掉 Excel 再改回来"说清楚**，否则他会以为生成器坏了。

### 6d. 追加式契约的第三个后果：补进来的旧活动会跳出日期顺序

§1 的契约（新活动追加在末尾）有一个不容易想到的副作用：
**Garmin 会在后续导出里补上以前漏掉的活动**（本案补了一条 2026-09-23 的 7.0 km），
它以"新活动"的身份被追加到末尾 —— 而它的日期在**两个月前**。

结果是一行错位的记录。日汇总/周汇总按日期聚合，所以**数字对**，
但他翻开表格看到的是一行 9 月的记录夹在 10 月中间。

**修法：每次追加后检查一次日期是否单调，乱了才重排（稳定排序，整行搬走）。**

```python
def resort_if_needed(ws):
    n = ws.max_row
    if n < 3:
        return 0
    keys = [ws.cell(r, 1).value for r in range(2, n + 1)]
    keys = [k for k in keys if isinstance(k, dt.datetime)]
    if len(keys) < 2 or all(keys[i] <= keys[i + 1] for i in range(len(keys) - 1)):
        return 0                                   # 已经有序：什么都不做
    rows = [(ws.cell(r, 1).value or dt.datetime(1900, 1, 1),
             [ws.cell(r, c).value for c in range(1, ws.max_column + 1)])
            for r in range(2, n + 1)]
    rows.sort(key=lambda x: x[0])                  # 稳定排序 → 同一天内早/晚顺序不变
    for i, (_, vals) in enumerate(rows):
        for c, v in enumerate(vals, 1):
            ws.cell(2 + i, c).value = v
    return len(rows)
```

三个必须注意的点：

- **只在真的乱序时才动**（先扫一遍单调性）。正常跑就是 no-op，不会累积风险。
- **稳定排序 + 整行搬移**：同一天内的早/晚顺序靠稳定性保住（表里只有日期和时段，
  没有开始时间列）。所以排序键用日期即可，**不要**再加活动ID 之类的二级键，
  它会把同日顺序打乱。
- **它不违反 §1 的契约**：每一格的值原样跟随，手填内容一个字都不改，只是换了个位置。
  但它仍然是唯一会移动已有行的操作，所以**重排之后要再跑一次哨兵测试**。

---

## 7. 自动初判列：只能当提示，不能当测量

"类型"这种自动打的标签很方便筛选，但它会**变成一条被引用的记录** ——
和那个被撤回的"6.4%"是同一类错误。

规矩：
- 列名就叫 **`类型(初判)`**，让"这是猜的"写在标题里
- 初判规则**写进说明页**，让人知道它在什么条件下会错
- 规则要能解释自己：本案是
  `长<3.5 km 且慢于 5:30/km → 热身/冷身`；`maxHR≥178 且 avgHR≥150 且快于 5:40/km → 质量课`；
  `≥15 km → 长跑`；`≤4:30/km → 质量课`；`≤5:30/km → 中等`；否则 `轻松`
- **用 avgHR 挡掉腕表心率伪影，用配速挡掉"没练过时心跳本来就高"** ——
  第一版规则把 2025 年初那些 6:50/km、maxHR 188 的慢跑全判成质量课（一周 6 节）；
  加上配速条件后降到 1 节。**跨二十个月的历史，任何一个自动规则都会在某个时期系统性出错。**
- 手改之后脚本不再覆盖（靠第 1 节那个追加式契约）

---

## 8. 交付前的验收清单

- [ ] Excel 全量重算后 **公式错误 = 0**
- [ ] 哨兵测试：手填值活过一次重跑，行数不变
- [ ] **回填测试**：新加的派生列在旧行上真的填上了；且**手填哨兵没被回填覆盖**
      （两个方向都要测 —— 回填最大的风险是它把可编辑列一起刷了）
- [ ] 抽查 3–4 行：距离 / 配速 / 时长 / 露点 与原始文件对得上
- [ ] 露点条件格式在正确的位置上（<12 绿）
- [ ] 图表有数据、坐标轴可读、没有多余图例
- [ ] 截图自己看过：没有截断的标签、没有裸露的小数
- [ ] 说明页写清：哪些列自动、初判规则、数据源、导出边界
