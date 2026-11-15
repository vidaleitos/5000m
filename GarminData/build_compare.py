# -*- coding: utf-8 -*-
"""
同期对照 —— 2025-W41 vs 2026-W40
一年前 / 今年的同一季节、几乎同一露点、几乎同一周量。
输出 FajirXiao_同期对照_2025W41_vs_2026W40.xlsx
"""
import os, json, datetime as dt, statistics as st, shutil
from collections import defaultdict
import fitparse
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

BASE = r"D:/running/GarminData"
UP = os.path.join(BASE, "Data", "DI_CONNECT", "DI-Connect-Uploaded-Files")
ND = os.path.join(BASE, "Data", "new_data")
OUT = os.path.join(BASE, "FajirXiao_同期对照_2025W41_vs_2026W40.xlsx")

NAVY, BLUE, ORANGE, GREEN, PURPLE, GOLD, RED, GREY = (
    "1F3864", "2E5C8A", "C55A11", "548235", "7030A0", "7F6000", "C00000", "808080")
LGREEN, LGOLD, LRED, LBLUE = "E2EFDA", "FFF2CC", "FCE4E4", "DEEBF7"
F = "微软雅黑"


def thin():
    s = Side(style="thin", color="D0D0D0")
    return Border(left=s, right=s, top=s, bottom=s)


def hdr(ws, row, cols, height=30):
    for i, (name, color, width) in enumerate(cols, 1):
        c = ws.cell(row, i, name)
        c.font = Font(bold=True, color="FFFFFF", size=10, name=F)
        c.fill = PatternFill("solid", fgColor=color)
        c.alignment = Alignment("center", "center", wrap_text=True)
        c.border = thin()
        ws.column_dimensions[c.column_letter].width = width
    ws.row_dimensions[row].height = height


def put(ws, r, c, v, fmt=None, bold=False, fill=None, align="center", size=10, color="000000"):
    cell = ws.cell(r, c, v)
    if fmt: cell.number_format = fmt
    cell.font = Font(bold=bold, size=size, color=color, name=F)
    cell.alignment = Alignment(align, "center", wrap_text=True)
    cell.border = thin()
    if fill: cell.fill = PatternFill("solid", fgColor=fill)
    return cell


# ═══════════════════════ 采集
def laps_of(path, min_km=0.5):
    out = []
    for m in fitparse.FitFile(path).get_messages("lap"):
        d = {f.name: f.value for f in m}
        dist = d.get("total_distance") or 0
        t = d.get("total_timer_time") or 0
        if dist > min_km * 1000 and t > 30 and d.get("avg_stance_time"):
            out.append(dict(km=dist / 1000, pace=t / (dist / 1000), gct=d["avg_stance_time"],
                            sl=(d.get("avg_step_length") or 0) / 10,
                            cad=(d.get("avg_running_cadence") or 0) * 2,
                            hr=d.get("avg_heart_rate")))
    return out


def band_pace(path, min_speed=1.4):
    """逐秒数据 → {HR段: [秒数, 米数]}"""
    acc = defaultdict(lambda: [0.0, 0.0])
    for m in fitparse.FitFile(path).get_messages("record"):
        d = {f.name: f.value for f in m}
        hr = d.get("heart_rate")
        sp = d.get("enhanced_speed") or d.get("speed")
        if hr is None or sp is None or sp < min_speed:
            continue
        b = (hr // 10) * 10
        acc[b][0] += 1.0
        acc[b][1] += sp
    return {b: list(v) for b, v in acc.items() if v[0] > 30 and v[1] > 50}


def pace_of(v):      # v = [秒数, 米数] → s/km
    return v[0] / (v[1] / 1000.0)


def read_log():
    """从训练日志读两期的权威口径：活动ID / 日期 / 距离 / 露点 / 类型初判"""
    from openpyxl import load_workbook
    wb = load_workbook(os.path.join(BASE, "FajirXiao_跑步训练日志.xlsx"), read_only=True, data_only=True)
    ws = wb["训练日志"]
    rows = []
    for r in ws.iter_rows(min_row=2, values_only=True):
        d = r[0]
        if d is None:
            continue
        k = d.strftime("%Y-%m-%d") if hasattr(d, "strftime") else str(d)[:10]
        if "2025-10-06" <= k <= "2025-10-12" or "2026-09-28" <= k <= "2026-10-04":
            rows.append(dict(date=k, hhmm=r[2], aid=str(r[3]), km=r[5], dew=r[17], typ=r[22]))
    wb.close()
    return rows


LOG = read_log()
LOG26 = {x["aid"]: x for x in LOG if x["date"] >= "2026-01-01"}
LOG25 = {(x["date"], round(x["km"], 1)): x for x in LOG if x["date"] < "2026-01-01"}

def sess_of(path):
    for m in fitparse.FitFile(path).get_messages("session"):
        a = {f.name: f.value for f in m}
        return dict(gct=a.get("avg_stance_time"),
                    sl=(a.get("avg_step_length") or 0) / 10 or None,
                    cad=(a.get("avg_running_cadence") or 0) * 2 or None,
                    mx=a.get("max_heart_rate"))
    return {}


idx = json.load(open(os.path.join(BASE, "_uploaded_index.json"), encoding="utf-8"))
S25, S26 = [], []
for x in idx:
    t = dt.datetime.fromisoformat(x["t"]) + dt.timedelta(hours=8)
    if not (dt.date(2025, 10, 6) <= t.date() <= dt.date(2025, 10, 12)):
        continue
    meta = LOG25.get((t.strftime("%Y-%m-%d"), round(x["km"], 1)))
    path = os.path.join(UP, x["file"])
    S25.append(dict(path=path, dt=t, km=x["km"],
                    dew=(meta or {}).get("dew"), hr=x["hr"], dur=x["dur"],
                    typ=(meta or {}).get("typ"), aid=(meta or {}).get("aid"),
                    **sess_of(path)))
for aid, meta in LOG26.items():
    p = os.path.join(ND, aid, aid + "_ACTIVITY.fit")
    if not os.path.exists(p):
        continue
    for m in fitparse.FitFile(p).get_messages("session"):
        a = {f.name: f.value for f in m}
        S26.append(dict(path=p, dt=a["start_time"] + dt.timedelta(hours=8),
                        km=a["total_distance"] / 1000, dew=meta["dew"],
                        hr=a.get("avg_heart_rate"), dur=a.get("total_timer_time"),
                        gct=a.get("avg_stance_time"),
                        sl=(a.get("avg_step_length") or 0) / 10,
                        cad=(a.get("avg_running_cadence") or 0) * 2,
                        mx=a.get("max_heart_rate"), typ=meta["typ"], aid=aid))
        break
S25 = [s for s in S25 if s["km"] > 0]
S26 = [s for s in S26 if s["km"] > 0]
S25.sort(key=lambda s: s["dt"]); S26.sort(key=lambda s: s["dt"])
if len(S25) != len([x for x in LOG if x["date"] < "2026-01-01"]):
    print("  ! 2025 期匹配数不符:", len(S25))
if len(S26) != len(LOG26):
    print("  ! 2026 期匹配数不符:", len(S26), "vs", len(LOG26))


def wk_summary(S, label):
    main = [s for s in S if s["km"] > 4]
    return dict(label=label, n=len(S), km=sum(s["km"] for s in S),
                n_main=len(main), km_main=sum(s["km"] for s in main),
                longest=max(s["km"] for s in S),
                dew=st.mean(s["dew"] for s in S if s["dew"] is not None),
                dur=sum((s.get("dur") or 0) for s in S) / 3600.0)


W25, W26 = wk_summary(S25, "2025-W41"), wk_summary(S26, "2026-W40")

# TRIMP（复用 build_log.py 生成的 _act_cache.json）
TRIMP = {}
try:
    TRIMP = {k: v.get("trimp") for k, v in
             json.load(open(os.path.join(BASE, "_act_cache.json"), encoding="utf-8")).items()
             if isinstance(v, dict)}
except Exception:
    pass


def trimp_get(s):
    return TRIMP.get(str(s.get("aid")))


for S in (S25, S26):
    for s in S:
        s["trimp"] = trimp_get(s)
W25["trimp"] = sum(s["trimp"] or 0 for s in S25)
W26["trimp"] = sum(s["trimp"] or 0 for s in S26)

# HR 段
band25, band26 = defaultdict(lambda: [0.0, 0.0]), defaultdict(lambda: [0.0, 0.0])
for s in S25:
    if s["km"] < 4: continue
    for b, (t, m) in band_pace(s["path"]).items():
        band25[b][0] += t; band25[b][1] += m
for s in S26:
    if s["km"] < 4: continue
    for b, (t, m) in band_pace(s["path"]).items():
        band26[b][0] += t; band26[b][1] += m

# 轻松跑连续圈
E25 = []
for s in S25:
    if 11.5 < s["km"] < 12.5:
        for l in laps_of(s["path"]):
            l.update(tag=s["dt"].strftime("%m-%d"), dew=s["dew"]); E25.append(l)
E26 = []
for aid, dew, tag in [("24548054408", 18.9, "09-30"), ("24572696122", 4.0, "10-02")]:
    p = os.path.join(ND, aid, aid + "_ACTIVITY.fit")
    for l in laps_of(p):
        l.update(tag=tag, dew=dew); E26.append(l)


def slope330(L):
    xs = [x["pace"] for x in L]; ys = [x["gct"] for x in L]
    n = len(xs); mx = st.mean(xs); my = st.mean(ys)
    b = sum((xs[i] - mx) * (ys[i] - my) for i in range(n)) / sum((xs[i] - mx) ** 2 for i in range(n))
    return my + b * (330 - mx), b


def easy_stat(L):
    return dict(n=len(L), pace=st.mean(x["pace"] for x in L),
                hr=st.mean(x["hr"] for x in L if x["hr"]),
                gct=st.mean(x["gct"] for x in L), cad=st.mean(x["cad"] for x in L),
                sl=st.mean(x["sl"] for x in L), g330=slope330(L)[0], slope=slope330(L)[1])


E25s, E26s = easy_stat(E25), easy_stat(E26)

# GCT-配速分桶
def buckets(L):
    b = defaultdict(list)
    for l in L: b[int(l["pace"] // 10) * 10].append(l)
    return {k: (st.mean(y["gct"] for y in v), st.mean(y["cad"] for y in v),
                st.mean(y["sl"] for y in v), len(v)) for k, v in b.items() if len(v) >= 2}


# ═══════════════════════ 建表
wb = Workbook(); wb.remove(wb.active)

# ── 1 结论
ws = wb.create_sheet("结论")
ws.column_dimensions["A"].width = 24
ws.column_dimensions["B"].width = 26
ws.column_dimensions["C"].width = 26
ws.column_dimensions["D"].width = 58
ws.cell(1, 1, "同期对照 · 2025-W41 vs 2026-W40").font = Font(bold=True, size=16, color=NAVY, name=F)
ws.cell(2, 1, "2025-10-06→10-12 与 2026-09-28→10-04。同季节、平均露点 12.4 vs 12.1、周量差 −1.3%。"
              "两条最可信的线：① HR 140–149 的配速；② 轻松跑连续圈的触地与步频。").font = Font(size=10, color="595959", name=F)
hdr(ws, 4, [("项目", NAVY, 24), ("2025-W41", BLUE, 26), ("2026-W40", GREEN, 26), ("怎么读", GOLD, 58)])
def fp(s):   # 秒 → m:ss.s
    return f"{int(s//60)}:{s%60:04.1f}"


def fd(s):   # 秒 → m:ss
    return f"{int(s//60)}:{int(s%60):02d}"


b25_140, b26_140 = band25.get(140), band26.get(140)


def agg_ge(bands, lo=180):
    s = [0.0, 0.0]
    for k, v in bands.items():
        if k >= lo:
            s[0] += v[0]; s[1] += v[1]
    return s


g25, g26 = agg_ge(band25), agg_ge(band26)

rows = [
    ("周量", f"{W25['km']:.2f} km", f"{W26['km']:.2f} km", "基本相同（%.1f%%）。这是这次对照成立的前提。" % ((W26['km']/W25['km']-1)*100)),
    ("训练次数 / 主课", f"{W25['n']} 次 / {W25['n_main']} 堂", f"{W26['n']} 次 / {W26['n_main']} 堂",
     "主课（>4km）从 6 堂变 %d 堂；2026 把热身/冷身拆成独立文件，所以次数多不代表练得多。" % W26['n_main']),
    ("最长单次", f"{W25['longest']:.2f} km", f"{W26['longest']:.2f} km",
     "2026 的长跑短了 %.1f km，但把量分散到了更多天。" % (W25['longest']-W26['longest'])),
    ("平均露点", f"{W25['dew']:.1f} ℃", f"{W26['dew']:.1f} ℃",
     "均值几乎相同 —— 所以两边的配速可以直接比，不用做热修正。"),
    ("周总 TRIMP", f"{W25['trimp']:.0f}", f"{W26['trimp']:.0f}",
     "TRIMP 是把强度和时长合在一起的负荷量。这个对比的是「同样的周公里数，身体实际承受了多少」。"),
    ("HR 140–149 配速", fp(pace_of(b25_140)) + " /km", fp(pace_of(b26_140)) + " /km",
     "两期数据最厚、最可比的一段。差 %+.1f s/km。" % (pace_of(b26_140)-pace_of(b25_140))),
    ("HR ≥180 停留时间", fd(g25[0]), fd(g26[0]),
     "2026 在高心率的停留时间是 %.1f 倍，那一段的配速 %s vs %s。" % (g26[0]/max(g25[0],1), fp(pace_of(g26)), fp(pace_of(g25)))),
    ("轻松跑平均 HR", f"{E25s['hr']:.0f}", f"{E26s['hr']:.0f}",
     "⚠ 不可直接比较：2025 是腕表，2026-09-27 起是胸带，已知有 5–10 bpm 系统性偏置。"),
    ("轻松跑连续圈触地（折算到 330 s/km）", f"{E25s['g330']:.1f} ms", f"{E26s['g330']:.1f} ms",
     "同一个配速下，2026 的触地长了 %.1f ms（%+.1f%%）。这是这次对照里最硬的一条机械差异。" % (E26s['g330']-E25s['g330'], (E26s['g330']/E25s['g330']-1)*100)),
    ("轻松跑步频", f"{E25s['cad']:.0f} spm", f"{E26s['cad']:.0f} spm",
     "每一圈都差 %.0f spm，不是噪声。步幅几乎没变（%.1f → %.1f cm）——配速变化来自步频，不是步幅。" % (E25s['cad']-E26s['cad'], E25s['sl'], E26s['sl'])),
]
for i, (a, b, c, dd) in enumerate(rows, 5):
    put(ws, i, 1, a, bold=True, align="left", fill="F7F7F7")
    put(ws, i, 2, b, fill=LBLUE)
    put(ws, i, 3, c, fill=LGREEN)
    put(ws, i, 4, dd, align="left", size=9.5)
    ws.row_dimensions[i].height = 30

ws.cell(17, 1, "三条结论").font = Font(bold=True, size=12, color=RED, name=F)
concl = [
    "① 有氧侧（配速与心率的关系）一年来几乎没有变化。140–149 这一段数据最厚、最可比，两期配速基本相同。",
    "② 变的是结构，不是引擎：2025 是「大量中等强度」（轻松跑就跑到 HR 140–150、周内 86 km 里 22 km 是一堂长跑），2026 是「真的轻松 + 真的快」。",
    "③ 唯一一条朝下的指标：同一配速下触地长了 ~6 ms。它和第 ② 条是一条因果链 —— 轻松跑跑得更松 → 步频降 8 spm → 触地变长。",
    "⚠ 所有涉及心率的结论都受腕表→胸带换代的污染，只作交叉验证，不作单独依据。",
]
for i, t in enumerate(concl, 18):
    ws.cell(i, 1, t).font = Font(size=10.5, name=F)
    ws.merge_cells(start_row=i, start_column=1, end_row=i, end_column=4)
    ws.cell(i, 1).alignment = Alignment(None, "center", wrap_text=True)
    ws.row_dimensions[i].height = 30

# ── 2 逐次课
ws2 = wb.create_sheet("逐次课")
cols = [("日期", NAVY, 11), ("星期", NAVY, 6), ("时段", NAVY, 6), ("距离 km", BLUE, 9),
        ("时间", BLUE, 10), ("配速 /km", BLUE, 10), ("平均HR", ORANGE, 8), ("最大HR", ORANGE, 8),
        ("TRIMP", GREY, 8),
        ("步频", GREEN, 7), ("步幅 cm", GREEN, 8), ("触地 ms", GREEN, 8),
        ("露点 ℃", PURPLE, 8), ("类型（初判）", GREY, 11), ("本周", GOLD, 10)]
hdr(ws2, 1, cols)
r = 2
for lab, S, fill in (("2025-W41", S25, LBLUE), ("2026-W40", S26, LGREEN)):
    for s in S:
        put(ws2, r, 1, s["dt"].date(), "yyyy-mm-dd", fill=fill)
        put(ws2, r, 2, "周" + "一二三四五六日"[s["dt"].weekday()], fill=fill)
        put(ws2, r, 3, "早" if s["dt"].hour < 12 else "晚", fill=fill)
        put(ws2, r, 4, round(s["km"], 3), "0.000", fill=fill)
        if s.get("dur"):
            put(ws2, r, 5, dt.timedelta(seconds=s["dur"]), "[h]:mm:ss", fill=fill)
            put(ws2, r, 6, dt.timedelta(seconds=s["dur"] / s["km"]), "[m]:ss.0", fill=fill)
        put(ws2, r, 7, s.get("hr"), fill=fill)
        put(ws2, r, 8, s.get("mx"), fill=fill)
        put(ws2, r, 9, s.get("trimp"), "0.0", fill=fill)
        put(ws2, r, 10, s.get("cad"), fill=fill)
        put(ws2, r, 11, round(s["sl"], 2) if s.get("sl") else None, "0.00", fill=fill)
        put(ws2, r, 12, s.get("gct"), fill=fill)
        put(ws2, r, 13, s["dew"], fill=fill)
        put(ws2, r, 14, s.get("typ"), fill=fill)
        put(ws2, r, 15, lab, fill=fill)
        r += 1
ws2.freeze_panes = "A2"; ws2.auto_filter.ref = f"A1:O{r-1}"

# ── 3 HR段配速
ws3 = wb.create_sheet("HR段配速")
hdr(ws3, 1, [("HR 段", NAVY, 10), ("2025 停留", BLUE, 11), ("2025 配速 /km", BLUE, 13),
             ("2026 停留", GREEN, 11), ("2026 配速 /km", GREEN, 13), ("配速差", GOLD, 13),
             ("数据量", GREY, 10)])
r = 2
for b in sorted(set(band25) | set(band26)):
    if b < 120 or b > 190: continue
    x = band25.get(b); y = band26.get(b)
    put(ws3, r, 1, f"{b}–{b+9}", bold=True)
    fine = True
    for col, v in ((2, x), (4, y)):
        if v and v[0] > 30:
            put(ws3, r, col, dt.timedelta(seconds=v[0]), "[h]:mm:ss")
            put(ws3, r, col + 1, dt.timedelta(seconds=pace_of(v)), "[m]:ss.0")
        else:
            put(ws3, r, col, "—"); put(ws3, r, col + 1, "—"); fine = False
    if x and y and x[0] > 120 and y[0] > 120:
        d = pace_of(y) - pace_of(x)
        put(ws3, r, 6, f"{d:+.1f} s/km",
            fill=(LRED if d > 3 else (LGREEN if d < -3 else LGOLD)), bold=True)
    else:
        put(ws3, r, 6, "样本不足")
    put(ws3, r, 7, "可比" if (x and y and x[0] > 120 and y[0] > 120) else "偏少", size=9)
    r += 1
ws3.cell(r + 1, 1, "⚠ 2025 用腕表心率，2026-09-27 起用胸带，已知存在 5–10 bpm 系统偏置。"
                   "所以「同一 HR 段的配速」这一列本身仍有传感器误差，它只用来交叉验证，不作单独结论。"
                   "  绿=2026 更快，红=2026 更慢，黄=差异在噪声内。").font = \
    Font(size=9.5, color=RED, name=F)
ws3.merge_cells(start_row=r + 1, start_column=1, end_row=r + 1, end_column=7)
ws3.cell(r + 1, 1).alignment = Alignment(None, "center", wrap_text=True)

# ── 4 轻松跑机械
ws4 = wb.create_sheet("轻松跑机械")
hdr(ws4, 1, [("", NAVY, 16), ("圈数", NAVY, 8), ("配速 s/km", BLUE, 10), ("平均HR", ORANGE, 9),
             ("触地 ms", GREEN, 9), ("步频 spm", GREEN, 9), ("步幅 cm", GREEN, 9),
             ("折算到 330 s/km 的触地", GOLD, 16), ("触地–配速斜率", GREY, 13)])
for i, (lab, e, fill) in enumerate((("2025 主轻松跑（3 堂 12 km）", E25s, LBLUE),
                                    ("2026 主轻松跑（2 堂 8–9 km）", E26s, LGREEN))):
    r = 2 + i
    put(ws4, r, 1, lab, align="left", fill=fill, bold=True)
    put(ws4, r, 2, e["n"], fill=fill)
    put(ws4, r, 3, round(e["pace"], 1), "0.0", fill=fill)
    put(ws4, r, 4, round(e["hr"]), fill=fill)
    put(ws4, r, 5, round(e["gct"], 1), "0.0", fill=fill)
    put(ws4, r, 6, round(e["cad"]), fill=fill)
    put(ws4, r, 7, round(e["sl"], 2), "0.00", fill=fill)
    put(ws4, r, 8, round(e["g330"], 1), "0.0", fill=fill, bold=True)
    put(ws4, r, 9, round(e["slope"], 2), "0.00", fill=fill)
put(ws4, 4, 1, "差（2026 − 2025）", bold=True, align="left", fill=LGOLD)
put(ws4, 4, 3, round(E26s["pace"] - E25s["pace"], 1), "0.0", fill=LGOLD)
put(ws4, 4, 5, round(E26s["gct"] - E25s["gct"], 1), "0.0", fill=LGOLD)
put(ws4, 4, 6, round(E26s["cad"] - E25s["cad"]), fill=LGOLD)
put(ws4, 4, 7, round(E26s["sl"] - E25s["sl"], 2), "0.00", fill=LGOLD)
put(ws4, 4, 8, round(E26s["g330"] - E25s["g330"], 1), "0.0", fill=LGOLD, bold=True)

r = 7
put(ws4, r, 1, "逐圈明细", bold=True, size=11, color=RED, align="left"); r += 1
hdr(ws4, r, [("来源", NAVY, 10), ("距离 km", BLUE, 9), ("配速 s/km", BLUE, 10), ("HR", ORANGE, 6),
             ("触地 ms", GREEN, 9), ("步频", GREEN, 7), ("步幅 cm", GREEN, 9), ("露点 ℃", PURPLE, 8)])
r += 1
for lab, L, fill in (("2025", E25, LBLUE), ("2026", E26, LGREEN)):
    for l in sorted(L, key=lambda z: z["pace"]):
        put(ws4, r, 1, lab, fill=fill); put(ws4, r, 2, round(l["km"], 3), "0.000", fill=fill)
        put(ws4, r, 3, round(l["pace"], 1), "0.0", fill=fill)
        put(ws4, r, 4, l["hr"], fill=fill); put(ws4, r, 5, round(l["gct"], 1), "0.0", fill=fill)
        put(ws4, r, 6, round(l["cad"]), fill=fill); put(ws4, r, 7, round(l["sl"], 2), "0.00", fill=fill)
        put(ws4, r, 8, l["dew"], fill=fill)
        r += 1

# ── 5 触地–配速曲线
ws5 = wb.create_sheet("触地-配速曲线")
hdr(ws5, 1, [("配速段 s/km", NAVY, 12), ("2025 触地", BLUE, 11), ("2025 步频", BLUE, 10),
             ("2025 步幅 cm", BLUE, 12), ("2026 触地", GREEN, 11), ("2026 步频", GREEN, 10),
             ("2026 步幅 cm", GREEN, 12), ("触地差", GOLD, 10)])
b25, b26 = buckets(E25), buckets(E26)
L25all, L26all = [], []
for s in S25:
    if s["km"] >= 4:
        for l in laps_of(s["path"]): l["dew"] = s["dew"]; L25all.append(l)
for s in S26:
    if s["km"] >= 4:
        for l in laps_of(s["path"]): l["dew"] = s["dew"]; L26all.append(l)
B25, B26 = buckets(L25all), buckets(L26all)
r = 2
for k in sorted(set(B25) | set(B26)):
    x = B25.get(k); y = B26.get(k)
    put(ws5, r, 1, f"{k}–{k+9}")
    if x: put(ws5, r, 2, round(x[0], 1), "0.0"); put(ws5, r, 3, round(x[1])); put(ws5, r, 4, round(x[2], 1), "0.0")
    else:
        for c in (2, 3, 4): put(ws5, r, c, "—")
    if y: put(ws5, r, 5, round(y[0], 1), "0.0"); put(ws5, r, 6, round(y[1])); put(ws5, r, 7, round(y[2], 1), "0.0")
    else:
        for c in (5, 6, 7): put(ws5, r, c, "—")
    if x and y:
        d = y[0] - x[0]
        put(ws5, r, 8, f"{d:+.1f}", fill=(LRED if d > 3 else (LGREEN if d < -3 else LGOLD)))
    else:
        put(ws5, r, 8, "—")
    r += 1

# ── 6 数据来源
ws6 = wb.create_sheet("数据来源与口径")
ws6.column_dimensions["A"].width = 22; ws6.column_dimensions["B"].width = 100
def kv(r, k, v, bold=True):
    c = ws6.cell(r, 1, k); c.font = Font(bold=bold, size=10, color=BLUE, name=F)
    c.alignment = Alignment(None, "top")
    d = ws6.cell(r, 2, v); d.font = Font(size=10, name=F)
    d.alignment = Alignment(None, "center", wrap_text=True)
    if len(v) > 70: ws6.row_dimensions[r].height = 28
ws6.cell(1, 1, "数据来源与口径").font = Font(bold=True, size=14, color=NAVY, name=F)
src = [
    ("2025-W41 原始数据", "Data/DI_CONNECT/DI-Connect-Uploaded-Files/UploadedFiles_20250094-_Part1 里的 FIT（由 _uploaded_index.json 索引，491 条）"),
    ("2026-W40 原始数据", "Data/new_data/<活动ID>/<活动ID>_ACTIVITY.fit"),
    ("索引脚本", "_uploaded_index.json 由 index_uploaded.py 生成；9834 个 FIT 里 491 个含运动 session"),
    ("露点", "Open-Meteo（_wx_auto.json 缓存）。2025 与 2026 的露点均按活动开始的小时取值"),
    ("触地 / 步频 / 步幅", "FIT lap 的 avg_stance_time / avg_running_cadence×2 / avg_step_length"),
    ("单位换算", "FIT 的 avg_step_length 是 mm（已 /10）；summarizedActivities.json 的是 cm"),
    ("⚠ 心率口径", "2025-W41 = 腕表光电心率；2026-W40 = 胸带（2026-09-27 起换）。已知 5–10 bpm 系统偏置 → HR 相关的结论全部降级为交叉验证"),
    ("⚠ 数据量", "各一周。周量、结构、方向性差异是可信的；绝对差值不要当成精确值"),
    ("⚠ 自动初判", "「类型（初判）」直接取自训练日志，是按距离/配速/心率的粗判标签，只用于快速筛选，本文件的所有结论都不依赖它"),
]
for i, (k, v) in enumerate(src, 3): kv(i, k, v)

def desktop_dir():
    try:
        import winreg
        k = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                           r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
        v, _ = winreg.QueryValueEx(k, "Desktop")
        if os.path.isdir(v):
            return v
    except Exception:
        pass
    for c in (r"D:\fjFiles", os.path.join(os.path.expanduser("~"), "Desktop")):
        if os.path.isdir(c):
            return c
    return None


wb.save(OUT)
print("已保存:", OUT)
_d = desktop_dir()
if _d:
    try:
        shutil.copy2(OUT, os.path.join(_d, os.path.basename(OUT)))
        print("已复制到桌面:", os.path.join(_d, os.path.basename(OUT)))
    except Exception as e:
        print("  ! 复制到桌面失败:", e)
print(f"2025-W41: {W25['km']:.2f}km / {W25['n']}次  2026-W40: {W26['km']:.2f}km / {W26['n']}次")
print(f"轻松跑 G330: {E25s['g330']:.1f} → {E26s['g330']:.1f} ms | 步频 {E25s['cad']:.0f} → {E26s['cad']:.0f}")
