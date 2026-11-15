# -*- coding: utf-8 -*-
"""
FajirXiao 跑步训练日志 —— 生成 / 追加脚本
=========================================
用法：   cd D:/running/GarminData && python build_log.py
效果：   把 Garmin 导出数据里"还没有进过日志"的跑步活动，追加到 xlsx 的「训练日志」sheet。
         已存在的行（包括你手填的类型/RPE/备注）永远不会被覆盖。

数据来源：
  1) Data/DI_CONNECT/DI-Connect-Fitness/*_1_summarizedActivities.json   (历史汇总，到导出日)
  2) Data/new_data/<id>/<id>_ACTIVITY.fit                               (近期逐活动)
  3) sessions_weather.csv                                               (历史天气)
  4) Open-Meteo                                                         (近期天气，自动抓并缓存)
"""
import os, glob, json, csv, datetime as dt, urllib.request, shutil, subprocess, importlib.util, sys


def _ensure_deps():
    """缺依赖就自己装 —— 换了解释器也不会再报 ModuleNotFoundError。"""
    need = [p for m, p in (("openpyxl", "openpyxl"), ("fitparse", "fitparse"))
            if importlib.util.find_spec(m) is None]
    if not need:
        return
    print(f"缺少依赖 {need}，正在用当前解释器安装：{sys.executable}")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", *need])
    except Exception as e:
        print("自动安装失败:", e)
        print("改用这个解释器运行（它已经装好）：")
        print(r"   C:\Users\tingz\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe build_log.py")
        sys.exit(1)


import sys
_ensure_deps()
BASE = os.path.dirname(os.path.abspath(__file__))
XLSX = os.path.join(BASE, "FajirXiao_跑步训练日志.xlsx")
NEWDATA = os.path.join(BASE, "Data", "new_data")


def find_export():
    """Garmin 导出包的位置会变（每次导出是一个新的 uuid 文件夹）。
    这里自动找：Data/*/DI_CONNECT 或 Data/DI_CONNECT，取含 DI-Connect-Fitness 的那个。"""
    cands = []
    d = os.path.join(BASE, "Data")
    if os.path.isdir(d):
        for x in sorted(os.listdir(d), reverse=True):
            p = os.path.join(d, x)
            if not os.path.isdir(p):
                continue
            if os.path.isdir(os.path.join(p, "DI_CONNECT")):
                cands.append(os.path.join(p, "DI_CONNECT"))
            elif os.path.isdir(os.path.join(p, "DI-Connect-Fitness")):
                cands.append(p)
    cands.append(os.path.join(d, "DI_CONNECT"))
    for c in cands:
        if os.path.isdir(os.path.join(c, "DI-Connect-Fitness")):
            return c
    return None


DIROOT = find_export()
UP = os.path.join(DIROOT, "DI-Connect-Uploaded-Files") if DIROOT else ""
UPIDX = os.path.join(BASE, "_uploaded_index.json")
WXCSV = os.path.join(BASE, "sessions_weather.csv")
WXCACHE = os.path.join(BASE, "_wx_auto.json")
LAT, LON, TZH = 35.004, 115.183, 8

ACT_CACHE = {}
try:
    ACT_CACHE = json.load(open(os.path.join(BASE, "_act_cache.json"), encoding="utf-8"))
except Exception:
    ACT_CACHE = {}

try:
    import fitparse
except ImportError:
    fitparse = None


# ═══════════════════════════════════════════════════════ 1. 数据采集
def load_history(index):
    """读导出包里所有的 *summarizedActivities*.json（Garmin 一次导出会切成多个文件），
    按 activityId 去重合并。index 用来给历史活动配原始 FIT（可选）。"""
    if not DIROOT:
        print("  ! 找不到 Garmin 导出包（Data/*/DI_CONNECT）")
        return []
    files = sorted(glob.glob(os.path.join(DIROOT, "DI-Connect-Fitness",
                                          "*summarizedActivities*.json")))
    if not files:
        print("  ! 导出包里没有 summarizedActivities.json")
        return []
    # 建立 (UTC 时间, 距离) → FIT 路径 的查找表（索引不存在就留空，不影响主流程）
    pool = []
    if UP and os.path.isdir(UP):
        for x in index:
            try:
                t = dt.datetime.fromisoformat(x["t"])
            except Exception:
                continue
            p = os.path.join(UP, x["file"])
            if os.path.exists(p):
                pool.append((t, x["km"], p))
    elif index:
        print("  ! FIT 索引已失效（导出包换了位置）—— 历史行沿用缓存里的 TRIMP/结构")
    raw_acts = {}
    for f in files:
        try:
            raw = json.load(open(f, encoding="utf-8"))
            arr = (raw[0]["summarizedActivitiesExport"] if isinstance(raw, list)
                   else raw["summarizedActivitiesExport"])
        except Exception as e:
            print("  ! 读取失败", os.path.basename(f), e)
            continue
        for a in arr:
            aid = str(a.get("activityId"))
            raw_acts.setdefault(aid, a)
    print(f"  导出包 {os.path.basename(os.path.dirname(DIROOT)) or DIROOT}："
          f"{len(files)} 个汇总文件 → {len(raw_acts)} 条活动")
    out = []
    for aid, a in raw_acts.items():
        if a.get("activityType") not in ("running", "treadmill_running", "track_running"):
            continue
        ts = a.get("startTimeLocal")
        dist_km = (a.get("distance") or 0) / 100000.0
        dur_s = (a.get("duration") or 0) / 1000.0
        if not ts or dist_km <= 0 or dur_s <= 0:
            continue
        cad = a.get("avgDoubleCadence") or ((a.get("avgRunCadence") or 0) * 2 or None)
        vo = a.get("avgVerticalOscillation")            # 已是 cm
        gain = a.get("elevationGain")                   # 单位 cm
        # 配 FIT：距离最接近、且时间差 < 10 分钟
        path = None
        if a.get("startTimeGmt") and pool:
            utc = dt.datetime.utcfromtimestamp(a["startTimeGmt"] / 1000.0)
            best, bd = None, 1e9
            for pt, pk, pp in pool:
                if abs(pk - dist_km) > 0.05:
                    continue
                dd = abs((pt - utc).total_seconds())
                if dd < bd:
                    best, bd = pp, dd
            if best and bd < 600 and os.path.exists(best):
                path = best
        out.append(dict(id=aid, path=path,
                        dt=dt.datetime.utcfromtimestamp(ts / 1000.0),
                        sport=a.get("activityType"), dist_km=dist_km, dur_s=dur_s,
                        ascent=gain / 100.0 if gain is not None else None,
                        hr=a.get("avgHr"), mx=a.get("maxHr"),
                        cad=cad, stride=a.get("avgStrideLength"), gct=a.get("avgGroundContactTime"),
                        vo=vo, vr=a.get("avgVerticalRatio"),
                        te=a.get("aerobicTrainingEffect"), load=a.get("activityTrainingLoad")))
    return out


def load_fits():
    if fitparse is None:
        return []
    out = []
    for d in sorted(os.listdir(NEWDATA)):
        fp = os.path.join(NEWDATA, d, d + "_ACTIVITY.fit")
        if not os.path.exists(fp):
            g = glob.glob(os.path.join(NEWDATA, d, "*.fit"))
            if not g:
                continue
            fp = g[0]
        try:
            for m in fitparse.FitFile(fp).get_messages("session"):
                a = {f.name: f.value for f in m}
                dist_km = (a.get("total_distance") or 0) / 1000.0
                dur_s = a.get("total_timer_time") or a.get("total_elapsed_time") or 0
                st = a.get("start_time")
                if not st or dist_km <= 0 or dur_s <= 0:
                    continue
                st = st.replace(tzinfo=None) if getattr(st, "tzinfo", None) else st
                stride, vo = a.get("avg_step_length"), a.get("avg_vertical_oscillation")
                out.append(dict(id=d, path=fp,
                                dt=st + dt.timedelta(hours=TZH),
                                sport=a.get("sport") or "running", dist_km=dist_km, dur_s=dur_s,
                                ascent=a.get("total_ascent"), hr=a.get("avg_heart_rate"),
                                mx=a.get("max_heart_rate"),
                                cad=((a.get("avg_running_cadence") or 0) * 2) or None,
                                stride=stride / 10.0 if stride else None,
                                gct=a.get("avg_stance_time"),
                                vo=vo / 10.0 if vo else None,
                                vr=a.get("avg_vertical_ratio"),
                                te=a.get("total_training_effect"),
                                load=(a.get("training_stress_score")
                                      or a.get("activity_training_load"))))
        except Exception as e:
            print("  ! FIT 解析失败", d, e)
    return out


# ═══════════════════════════════════════════════════════ 2. 天气
def load_wx():
    wx = {}
    if os.path.exists(WXCSV):
        for r in csv.DictReader(open(WXCSV, encoding="utf-8")):
            try:
                t = dt.datetime.strptime(r["t"], "%Y-%m-%d %H:%M").replace(minute=0, second=0)
            except Exception:
                continue
            def f(k):
                try:
                    return float(r[k])
                except Exception:
                    return None
            wx[t] = [f("T"), f("DP"), None]
    try:
        for k, v in json.load(open(WXCACHE)).items():
            kk = dt.datetime.strptime(str(k).replace("T", " ")[:16], "%Y-%m-%d %H:%M")
            if v and v[0] is not None:
                wx[kk] = list(v)
    except Exception as e:
        print("  ! 天气缓存读取失败:", e)
    today = dt.date.today()
    need = [dt.datetime.combine(today - dt.timedelta(days=i), dt.time(h))
            for i in range(95) for h in range(4, 12)]
    if any(t not in wx for t in need):
        try:
            url = ("https://api.open-meteo.com/v1/forecast"
                   f"?latitude={LAT}&longitude={LON}"
                   "&hourly=temperature_2m,dewpoint_2m,wind_speed_10m"
                   "&timezone=Asia%2FShanghai&past_days=92&forecast_days=1")
            with urllib.request.urlopen(url, timeout=45) as r:
                h = json.load(r)["hourly"]
            for i, t in enumerate(h["time"]):
                wx[dt.datetime.strptime(t, "%Y-%m-%dT%H:%M")] = [
                    h["temperature_2m"][i], h["dewpoint_2m"][i], h["wind_speed_10m"][i]]
            json.dump({k.strftime("%Y-%m-%d %H:%M"): v for k, v in wx.items()},
                      open(WXCACHE, "w"), ensure_ascii=False)
            print("  · Open-Meteo 天气已更新缓存")
        except Exception as e:
            print("  ! 天气抓取失败（不影响主流程）:", e)
    return wx


def wx_for(wx, t):
    k = t.replace(minute=0, second=0, microsecond=0)
    for off in (0, 1, -1, 2, -2, 3, -3):
        if k + dt.timedelta(hours=off) in wx:
            return wx[k + dt.timedelta(hours=off)]
    return [None, None, None]


# ═══════════════════════════════════════════════════════ 2b. 负荷 / 结构
import math
HRREST, HRMAX = 45.0, 198.0          # TRIMP 用的固定常数，保证 537 行口径一致
MIN_QUALITY_PACE = 310.0             # 「连续」块必须快于此（s/km）= 5:10/km。
#                                      低于它就只是「在跑」而不是一次质量刺激，
#                                      单纯为了挡掉热身/冷身里"跑步 vs 走路"造出来的假结构。
STRUCT_VER = 3                       # 结构识别算法版本；改了它只重算结构（只需读分圈，很快）
CACHE_VER = 3
ACACHE = os.path.join(BASE, "_act_cache.json")


def _lap_pass(path):
    """只读分圈，不碰逐秒记录 —— 比 _one_pass 快一到两个数量级。"""
    laps = []
    for m in fitparse.FitFile(path).get_messages("lap"):
        dist = m.get_value("total_distance") or 0
        t = m.get_value("total_timer_time") or 0
        if dist >= 20 and t >= 3:
            laps.append(dict(dist=dist, t=t, pace=t / (dist / 1000.0)))
    return laps


def _hrr(hr):
    return max(0.0, (hr - HRREST) / (HRMAX - HRREST))


def _one_pass(path):
    """一次遍历 FIT，同时取出分圈和心率流。返回 (laps, hrs)。"""
    laps, hrs = [], []
    for m in fitparse.FitFile(path).get_messages():
        n = m.name
        if n == "record":
            hr = m.get_value("heart_rate")
            if hr:
                hrs.append(hr)
        elif n == "lap":
            dist = m.get_value("total_distance") or 0
            t = m.get_value("total_timer_time") or 0
            if dist >= 20 and t >= 3:
                laps.append(dict(dist=dist, t=t, pace=t / (dist / 1000.0)))
    return laps, hrs


def trimp_from_hrs(hrs):
    if not hrs or len(hrs) < 30:
        return None
    tot = 0.0
    for hr in hrs:
        r = _hrr(hr)
        tot += r * 0.64 * math.exp(1.92 * r) / 60.0
    return round(tot, 1)


def trimp_stream(path):
    """逐秒积分 Banister TRIMP（男 b=1.92）。None = 没读到心率流。"""
    if fitparse is None or not path or not os.path.exists(path):
        return None
    try:
        _l, hrs = _one_pass(path)
    except Exception:
        return None
    return trimp_from_hrs(hrs)


def trimp_avg(dur_s, avg_hr):
    if not dur_s or not avg_hr:
        return None
    r = _hrr(avg_hr)
    return round(dur_s / 60.0 * r * 0.64 * math.exp(1.92 * r), 1)


def analyse_structure(path):
    """从 FIT 分圈识别课的结构。返回 dict 或 None。"""
    if fitparse is None or not path or not os.path.exists(path):
        return None
    try:
        laps, _h = _one_pass(path)
    except Exception:
        return None
    return structure_from_laps(laps)


def structure_from_laps(laps):
    """分圈 → 结构。返回 {"kind","text","work_m","work_s","work_pace","rec_text"} 或 None。"""
    if len(laps) < 3:
        return None
    tot_d = sum(l["dist"] for l in laps)
    tot_t = sum(l["t"] for l in laps)
    if tot_d < 200 or tot_t < 60:
        return None
    avg = tot_t / (tot_d / 1000.0)          # 整堂课的平均配速
    fastest = min(l["pace"] for l in laps)
    if fastest > 400:
        return None
    # 工作段判据：既要比整堂课快 8%，也不能比最快圈慢太多（后者处理间歇里前几组偏慢的情况）
    th = max(avg * 0.92, fastest * 1.30)
    for l in laps:
        l["w"] = l["pace"] <= th
    blocks = []
    for l in laps:
        if blocks and blocks[-1]["w"] == l["w"]:
            blocks[-1]["laps"].append(l)
        else:
            blocks.append({"w": l["w"], "laps": [l]})
    for b in blocks:
        b["dist"] = sum(x["dist"] for x in b["laps"])
        b["t"] = sum(x["t"] for x in b["laps"])
        b["pace"] = b["t"] / (b["dist"] / 1000.0)
    work = [b for b in blocks if b["w"] and b["dist"] >= 20]
    if not work:
        return None
    # 门：工作段整体必须真的比整堂课快 5% 以上，否则这堂课没有结构
    wd = sum(b["dist"] for b in work)
    wt = sum(b["t"] for b in work)
    if wd <= 0 or wt / (wd / 1000.0) > avg * 0.95:
        return None
    work.sort(key=lambda b: -b["dist"])
    main, rest = work[0], work[1:]
    biggest_rest = max([b["dist"] for b in rest], default=0)

    if len(work) == 1 or main["dist"] > 3 * biggest_rest:
        # 单一主块
        if (main["dist"] >= 2500 or main["t"] >= 600) and main["pace"] <= MIN_QUALITY_PACE:
            mm, ss = divmod(int(round(main["t"])), 60)
            return dict(kind="continuous", text=f"连续 {mm}:{ss:02d}",
                        work_m=main["dist"], work_s=main["t"], work_pace=main["pace"],
                        rec_text=None)
        if main["dist"] >= 100 and main["pace"] <= MIN_QUALITY_PACE:
            return dict(kind="surge", text=f"+{main['dist']:.0f}m",
                        work_m=main["dist"], work_s=main["t"], work_pace=main["pace"],
                        rec_text=None)
        return None

    # 间歇：按出现顺序取工作块，恢复块取它们之间的
    order = [b for b in blocks if b in work]
    if len(order) < 2:
        return None
    idxs = [blocks.index(b) for b in order]
    recs = [b for i, b in enumerate(blocks)
            if not b["w"] and min(idxs) < i < max(idxs)]
    n = len(order)
    mean_d = sum(b["dist"] for b in order) / n
    mean_t = sum(b["t"] for b in order) / n
    tot_d = sum(b["dist"] for b in order)
    tot_t = sum(b["t"] for b in order)
    disp = (max(b["dist"] for b in order) - min(b["dist"] for b in order)) / mean_d
    if mean_d < 60:
        text = f"{n}×{mean_t:.0f}秒（约{mean_d:.0f}m）"
    else:
        text = f"{n}×{mean_d:.0f}m" + ("（变距）" if disp > 0.15 else "")
    rec_text = None
    if recs:
        rt = sum(b["t"] for b in recs) / len(recs)
        rd = sum(b["dist"] for b in recs) / len(recs)
        mm, ss = divmod(int(round(rt)), 60)
        rec_text = f"{mm}:{ss:02d} @{rt/(rd/1000.0):.0f}s/km·{rd:.0f}m" if rd > 20 else f"{mm}:{ss:02d}"
    return dict(kind="interval", text=text, work_m=tot_d, work_s=tot_t,
                work_pace=tot_t / (tot_d / 1000.0), rec_text=rec_text)


def act_facts(a):
    """一个活动的派生事实：结构 + TRIMP。带缓存，按活动 ID。
    TRIMP 缓存与结构算法版本分开 —— 改结构算法时不必重算心率流。"""
    c = ACT_CACHE.get(a["id"])
    need_t = (c is None) or (c.get("trimp") is None)
    need_s = (c is None) or (c.get("sv") != STRUCT_VER)
    if not need_t and not need_s:
        return c
    tp = c.get("trimp") if c else None
    st = c.get("struct") if (c and not need_s) else None
    p = a.get("path")
    if p and fitparse is not None and os.path.exists(p):
        try:
            if need_t:
                laps, hrs = _one_pass(p)
                if need_s:
                    st = structure_from_laps(laps)
                tp = trimp_from_hrs(hrs)
            elif need_s:
                st = structure_from_laps(_lap_pass(p))
        except Exception:
            pass
    if tp is None:
        tp = trimp_avg(a["dur_s"], a["hr"])
    c = dict(trimp=tp, struct=st, sv=STRUCT_VER)
    ACT_CACHE[a["id"]] = c
    ACT_CACHE["__dirty__"] = True
    return c


# ═══════════════════════════════════════════════════════ 3. 样式常量
TYPELIST = ["轻松", "恢复", "中等", "长跑", "阈值", "比赛配速", "VO2max", "短冲",
            "坡跑", "台阶", "测试", "比赛", "热身/冷身", "质量课", "其它"]
RPE_LIST = [str(i) for i in range(1, 11)]
LEG_LIST = ["很轻松", "正常", "偏酸", "沉", "抬不动", "无感觉"]

NAVY, BLUE, ORANGE, GREEN, PURPLE, GREY, GOLD, RED = (
    "1F3864", "2E5C8A", "C55A11", "548235", "7030A0", "808080", "7F6000", "C00000")
LNAVY, LBLUE, LORANGE, LGREEN, LPURPLE, LGREY, LGOLD, LRED = (
    "D9E2F3", "DEEBF7", "FCE4D6", "E2EFDA", "E4DFEC", "EDEDED", "FFF2CC", "FCE4E4")

# 训练日志列定义: (表头, 分组主色, 列宽, 数字格式, 是否手填)
LOGFIELDS = [
    ("日期", NAVY, 11, "yyyy-mm-dd", 0), ("星期", NAVY, 5.5, "@", 0),
    ("时段", NAVY, 5.5, "@", 0), ("活动ID", NAVY, 12, "@", 0), ("项目", NAVY, 10, "@", 0),
    ("距离 km", BLUE, 9, "0.000", 0), ("时间", BLUE, 9.5, "[h]:mm:ss", 0),
    ("配速 /km", BLUE, 9.5, "[m]:ss.0", 0), ("爬升 m", BLUE, 7.5, "0", 0),
    ("平均HR", ORANGE, 7.5, "0", 0), ("最大HR", ORANGE, 7.5, "0", 0),
    ("步频 spm", GREEN, 8, "0", 0), ("步幅 cm", GREEN, 8, "0.0", 0),
    ("触地 ms", GREEN, 8, "0", 0), ("垂直振幅 cm", GREEN, 10, "0.0", 0),
    ("垂直比 %", GREEN, 8, "0.0", 0),
    ("气温 ℃", PURPLE, 7.5, "0.0", 0), ("露点 ℃", PURPLE, 7.5, "0.0", 0),
    ("风速 km/h", PURPLE, 9, "0.0", 0),
    ("有氧TE", GREY, 7.5, "0.0", 0), ("训练负荷", GREY, 8.5, "0", 0),
    ("TRIMP 负荷", GREY, 10, "0.0", 0),
    ("类型(初判)", GOLD, 11, "@", 1), ("结构（自动识别，可改）", GOLD, 24, "@", 1),
    ("工作总量", GOLD, 15, "@", 1), ("工作配速 /km", GOLD, 12, "[m]:ss.0", 1),
    ("恢复", GOLD, 20, "@", 1),
    ("RPE", RED, 5.5, "@", 1), ("腿", RED, 9, "@", 1), ("心肺", RED, 9, "@", 1),
    ("症状", RED, 15, "@", 1), ("备注", RED, 38, "@", 1),
]
NCOL = len(LOGFIELDS)
# 关键列号（1 起）
COL_DATE, COL_DIST, COL_TIME, COL_DUR, COL_DEW, COL_TEMP = 1, 6, 7, 7, 18, 17
COL_TE, COL_LOAD, COL_TRIMP = 20, 21, 22
COL_TYPE, COL_STRUCT, COL_WM, COL_WP, COL_REC = 23, 24, 25, 26, 27


def guess_type(a):
    """粗略初判（只为方便筛选）。历史 20 个月里气温/露点跨度极大，配速与心率都被高温抬高过，
    所以任何自动标签都只能当参考 —— 看到判错的直接改，改了脚本不会再覆盖。"""
    d, pace = a["dist_km"], a["dur_s"] / a["dist_km"]
    hr, mx = (a["hr"] or 0), (a["mx"] or 0)
    if d < 3.5 and pace > 330:
        return "热身/冷身"
    if mx >= 178 and hr >= 150 and pace <= 340:   # 课里出现过快速段（pace 条件挡掉"没练过时心跳就很高"） 
        return "质量课"
    if d >= 15:
        return "长跑"
    if pace <= 270:                  # 4:30/km 或更快
        return "质量课"
    if pace <= 330:                  # 4:30–5:30
        return "中等"
    return "轻松"


# ═══════════════════════════════════════════════════════ 4. 写表
def thin():
    from openpyxl.styles import Border, Side
    s = Side(style="thin", color="D0D0D0")
    return Border(left=s, right=s, top=s, bottom=s)


def struct_cells(a):
    """从分圈分析结果生成 TRIMP 与 结构/工作总量/工作配速/恢复 五格"""
    f = act_facts(a)
    st = f.get("struct")
    tp = f.get("trimp")
    if not st:
        return tp, None, None, None, None
    wm, ws, wp = st["work_m"], st["work_s"], st["work_pace"]
    mm, ss = divmod(int(round(ws)), 60)
    return (tp, st["text"], f"{wm:.0f} m / {mm}:{ss:02d}",
            dt.timedelta(seconds=wp), st.get("rec_text"))


def log_row_values(a, wx):
    T, DP, W = wx_for(wx, a["dt"])
    h = a["dt"].hour
    tp, st_text, wm, wp, rec = struct_cells(a)
    return [a["dt"].date(), "周" + "一二三四五六日"[a["dt"].weekday()],
            "早" if h < 12 else ("晚" if h >= 16 else "中"),
            a["id"], {"treadmill_running": "跑步机", "track_running": "跑道"}.get(a["sport"], "跑步"),
            round(a["dist_km"], 3), dt.timedelta(seconds=a["dur_s"]),
            dt.timedelta(seconds=a["dur_s"] / a["dist_km"]) if a["dist_km"] else None,
            a["ascent"], a["hr"], a["mx"], a["cad"], a["stride"], a["gct"], a["vo"], a["vr"],
            T, DP, W, a["te"], round(a["load"]) if a["load"] else None, tp,
            guess_type(a), st_text, wm, wp, rec,
            None, None, None, None, None]


def build_sheets(wb):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    from openpyxl.worksheet.datavalidation import DataValidation

    # ── 训练日志 ─────────────────────────────────────
    ws = wb.create_sheet("训练日志")
    for i, (nm, col, wdt, fmt, man) in enumerate(LOGFIELDS, 1):
        c = ws.cell(1, i, nm)
        c.font = Font(bold=True, color="FFFFFF", size=10, name="微软雅黑")
        c.fill = PatternFill("solid", fgColor=col)
        c.alignment = Alignment("center", "center", wrap_text=True)
        c.border = thin()
        ws.column_dimensions[c.column_letter].width = wdt
    ws.row_dimensions[1].height = 32
    ws.freeze_panes = "F2"
    ws.auto_filter.ref = f"A1:{ws.cell(1, NCOL).column_letter}1"

    dv = DataValidation(type="list", formula1='"' + ",".join(TYPELIST) + '"', allow_blank=True)
    dvr = DataValidation(type="list", formula1='"' + ",".join(RPE_LIST) + '"', allow_blank=True)
    dvl = DataValidation(type="list", formula1='"' + ",".join(LEG_LIST) + '"', allow_blank=True)
    for d in (dv, dvr, dvl):
        ws.add_data_validation(d)
    dv.add(f"W2:W20000")
    dvr.add(f"AB2:AB20000")
    dvl.add(f"AC2:AC20000")
    ws.sheet_view.zoomScale = 90

    # 露点条件格式（唯一真正影响配速可比性的环境变量）
    from openpyxl.formatting.rule import CellIsRule
    ws.conditional_formatting.add(
        f"R2:R20000", CellIsRule(operator="lessThan", formula=["12"],
                                 fill=PatternFill("solid", fgColor="C6EFCE")))
    ws.conditional_formatting.add(
        f"R2:R20000", CellIsRule(operator="between", formula=["12", "18"],
                                 fill=PatternFill("solid", fgColor="FFEB9C")))
    ws.conditional_formatting.add(
        f"R2:R20000", CellIsRule(operator="greaterThan", formula=["18"],
                                 fill=PatternFill("solid", fgColor="FFC7CE")))
    ws.conditional_formatting.add(
        f"W2:W20000", CellIsRule(operator="equal", formula=['"质量课"'],
                                 fill=PatternFill("solid", fgColor="FFF2CC")))

    # ── 日汇总 ───────────────────────────────────────
    ws2 = wb.create_sheet("日汇总")
    day_fields = [("日期", NAVY, 11), ("星期", NAVY, 6), ("次数", BLUE, 6),
                  ("总距离 km", BLUE, 11), ("总时间", BLUE, 10), ("当日 TRIMP", GREY, 11),
                  ("早课 km", GREEN, 9), ("晚课 km", GREEN, 9),
                  ("露点 ℃", PURPLE, 8), ("气温 ℃", PURPLE, 8),
                  ("质量课", GOLD, 9), ("当日备注", RED, 46)]
    for i, (nm, col, wdt) in enumerate(day_fields, 1):
        c = ws2.cell(1, i, nm)
        c.font = Font(bold=True, color="FFFFFF", size=10, name="微软雅黑")
        c.fill = PatternFill("solid", fgColor=col)
        c.alignment = Alignment("center", "center", wrap_text=True)
        c.border = thin()
        ws2.column_dimensions[c.column_letter].width = wdt
    ws2.row_dimensions[1].height = 28
    ws2.freeze_panes = "A2"
    ws2.auto_filter.ref = "A1:L1"

    # ── 周汇总 ───────────────────────────────────────
    ws3 = wb.create_sheet("周汇总")
    wk_fields = [("周起始(周一)", NAVY, 13), ("周次", NAVY, 10), ("训练天数", BLUE, 9),
                 ("训练次数", BLUE, 9), ("总距离 km", BLUE, 11), ("总时间", BLUE, 10),
                 ("总 TRIMP", GREY, 11),
                 ("最长单次 km", GREEN, 11), ("质量课次数", GOLD, 11),
                 ("平均露点 ℃", PURPLE, 11), ("平均心率", ORANGE, 9),
                 ("备注", RED, 50)]
    for i, (nm, col, wdt) in enumerate(wk_fields, 1):
        c = ws3.cell(1, i, nm)
        c.font = Font(bold=True, color="FFFFFF", size=10, name="微软雅黑")
        c.fill = PatternFill("solid", fgColor=col)
        c.alignment = Alignment("center", "center", wrap_text=True)
        c.border = thin()
        ws3.column_dimensions[c.column_letter].width = wdt
    ws3.row_dimensions[1].height = 28
    ws3.freeze_panes = "A2"
    ws3.auto_filter.ref = "A1:L1"

    # ── 测试与PB ─────────────────────────────────────
    ws4 = wb.create_sheet("测试与PB")
    t_fields = [("日期", NAVY, 11), ("项目", BLUE, 12), ("距离 m", BLUE, 9),
                ("成绩", BLUE, 11), ("配速 /km", BLUE, 10),
                ("类型", GOLD, 16), ("气温 ℃", PURPLE, 8), ("露点 ℃", PURPLE, 8),
                ("风速 km/h", PURPLE, 10), ("平均HR", ORANGE, 8), ("最大HR", ORANGE, 8),
                ("触地 ms", GREEN, 9), ("备注", RED, 44)]
    for i, (nm, col, wdt) in enumerate(t_fields, 1):
        c = ws4.cell(1, i, nm)
        c.font = Font(bold=True, color="FFFFFF", size=10, name="微软雅黑")
        c.fill = PatternFill("solid", fgColor=col)
        c.alignment = Alignment("center", "center", wrap_text=True)
        c.border = thin()
        ws4.column_dimensions[c.column_letter].width = wdt
    ws4.row_dimensions[1].height = 28
    ws4.freeze_panes = "A2"

    known = [
        ("2025-04-17", "5000 m", 5000, "18:33.7", "正式比赛", "官方 PB"),
        ("2026-03-10", "5000 m", 5000, "18:45.9", "正式比赛", ""),
        ("2026-06-10", "3000 m", 3000, "10:37.0", "正式比赛", ""),
        ("2026-06-09", "1000 m", 1000, "3:26.4", "训练段", ""),
        ("2026-06-09", "1 mile", 1609, "5:36.8", "训练段", ""),
        ("2025-12-09", "10000 m", 10000, "42:12", "训练段", ""),
        ("2026-10-01", "400 m（疲劳态）", 400, "1:16.2", "训练段·8km 之后",
         "3:10.5/km · 露点 9.4 · HR 184 · 触地 199"),
    ]
    for r, (d, ev, dm, res, tp, note) in enumerate(known, 2):
        ws4.cell(r, 1, d); ws4.cell(r, 2, ev); ws4.cell(r, 3, dm)
        ws4.cell(r, 4, res).alignment = Alignment("center")
        ws4.cell(r, 6, tp); ws4.cell(r, 13, note)

    # ── 力量日志 ─────────────────────────────────────
    ws5 = wb.create_sheet("力量日志")
    s_fields = [("日期", NAVY, 11), ("时段", NAVY, 6), ("模块", BLUE, 14),
                ("动作", BLUE, 22), ("组数×次数 / 保持时间", BLUE, 20),
                ("负荷", BLUE, 12), ("RPE", RED, 6), ("备注", RED, 40)]
    for i, (nm, col, wdt) in enumerate(s_fields, 1):
        c = ws5.cell(1, i, nm)
        c.font = Font(bold=True, color="FFFFFF", size=10, name="微软雅黑")
        c.fill = PatternFill("solid", fgColor=col)
        c.alignment = Alignment("center", "center", wrap_text=True)
        c.border = thin()
        ws5.column_dimensions[c.column_letter].width = wdt
    ws5.row_dimensions[1].height = 28
    ws5.freeze_panes = "A2"
    ws5.auto_filter.ref = "A1:H1"

    # ── 课表模板 ─────────────────────────────────────
    ws6 = wb.create_sheet("课表模板")
    ws6.column_dimensions["A"].width = 13
    for col in "BCDEFGH":
        ws6.column_dimensions[col].width = 21
    ws6.column_dimensions["I"].width = 30

    def put(r, c, v, bold=False, size=10, color="000000", fill=None,
            align="left", wrap=False, border=False):
        cell = ws6.cell(r, c, v)
        cell.font = Font(bold=bold, size=size, color=color, name="微软雅黑")
        if fill:
            cell.fill = PatternFill("solid", fgColor=fill)
        cell.alignment = Alignment(align, "center", wrap_text=wrap)
        if border:
            cell.border = thin()
        return cell

    put(1, 1, "周课表 · 模板", True, 15, NAVY)
    put(2, 1, "整块复制到新的一周使用。计划是「主方案 + 调整逻辑」，不是一张不能改的表。", size=9, color="595959")

    put(4, 1, "周次", True, 10, LNAVY); put(4, 2, None)
    put(4, 4, "日期范围", True, 10, LNAVY); put(4, 5, None)
    put(4, 7, "阶段目标", True, 10, LNAVY); put(4, 8, None)

    put(6, 1, "本周必发生刺激", True, 11, GOLD)
    put(7, 1, "1.", True); put(7, 2, None)
    put(8, 1, "2.", True); put(8, 2, None)
    put(9, 1, "3.", True); put(9, 2, None)
    put(10, 1, "4.", True); put(10, 2, None)

    hdr = ["", "周一", "周二", "周三", "周四", "周五", "周六", "周日", "本周合计/备注"]
    for j, h in enumerate(hdr, 1):
        put(12, j, h, True, 11, "FFFFFF", NAVY if j else None, "center", border=True)

    rows = [("早课", GREEN), ("晚课", GREEN), ("主刺激", GOLD), ("力量 / 辅助", PURPLE),
            ("预估距离", BLUE), ("实际距离", BLUE), ("露点 / 天气", PURPLE)]
    for i, (label, col) in enumerate(rows):
        r = 13 + i
        put(r, 1, label, True, 10, "FFFFFF", col, "center", True, True)
        for j in range(2, 10):
            put(r, j, None, border=True)
        ws6.row_dimensions[r].height = 30

    put(21, 1, "周末复盘", True, 12, RED)
    for i, q in enumerate(["① 计划 vs 实际差在哪",
                           "② 哪个刺激真的发生了 / 哪个没发生",
                           "③ 身体给了什么信号（配速、心率、触地、体感）",
                           "④ 下周改什么（只改一件事）"]):
        r = 22 + i
        put(r, 1, q, False, 10, "595959")
        ws6.merge_cells(start_row=r, start_column=1, end_row=r, end_column=3)
        ws6.merge_cells(start_row=r, start_column=4, end_row=r, end_column=9)
        put(r, 4, None, border=True)
        ws6.row_dimensions[r].height = 24

    # ── 图表 ─────────────────────────────────────────
    from openpyxl.chart import LineChart, Reference
    from openpyxl.chart.shapes import GraphicalProperties
    from openpyxl.drawing.line import LineProperties

    def style_line(chart, color):
        chart.y_axis.majorGridlines = None
        chart.legend = None
        for s in chart.series:
            s.smooth = False
            s.graphicalProperties = GraphicalProperties(
                ln=LineProperties(solidFill=color, w=19050))

    ws7 = wb.create_sheet("图表")
    ws7.column_dimensions["A"].width = 3
    ch = LineChart()
    ch.title = "周跑量 (km)"
    ch.height, ch.width = 9.5, 26
    ch.y_axis.title = "km"
    ch.add_data(Reference(ws3, min_col=5, min_row=1, max_row=320), titles_from_data=True)
    ch.set_categories(Reference(ws3, min_col=1, min_row=2, max_row=320))
    style_line(ch, "1F3864")
    ws7.add_chart(ch, "B2")
    ch2 = LineChart()
    ch2.title = "周平均露点 (℃)"
    ch2.height, ch2.width = 9.5, 26
    ch2.y_axis.title = "℃"
    ch2.add_data(Reference(ws3, min_col=9, min_row=1, max_row=320), titles_from_data=True)
    ch2.set_categories(Reference(ws3, min_col=1, min_row=2, max_row=320))
    style_line(ch2, "C55A11")
    ws7.add_chart(ch2, "B24")

    # ── 说明 ─────────────────────────────────────────
    ws0 = wb.create_sheet("说明", 0)
    ws0.column_dimensions["A"].width = 18
    ws0.column_dimensions["B"].width = 105
    put0 = lambda r, a, b, bold_a=True: (
        setattr(ws0.cell(r, 1, a), "font", Font(bold=bold_a, size=10, name="微软雅黑")),
        setattr(ws0.cell(r, 2, b), "font", Font(size=10, name="微软雅黑")),
        setattr(ws0.cell(r, 2), "alignment", Alignment(None, "center", wrap_text=True)))
    ws0.cell(1, 1, "FajirXiao · 跑步训练日志").font = Font(bold=True, size=16, color=NAVY, name="微软雅黑")
    ws0.cell(2, 1, "每天跑完，把 Garmin 的 FIT 文件放进 Data/new_data/<活动ID>/，然后跑一次 python build_log.py。").font = \
        Font(size=10, color="595959", name="微软雅黑")

    guide = [
        ("训练日志", "每次跑步一行。前 21 列 + TRIMP 全部自动填（来自 Garmin FIT + Open-Meteo）；「结构 / 工作总量 / 工作配速 / 恢复」四列由脚本从分圈自动识别，你可以在上面改；最后一组（RPE/腿/心肺/症状/备注）完全手填。"),
        ("", "「结构」是从 FIT 分圈自动识别的：把所有圈按配速分成工作段和恢复段，连续的工作段合并成一组。连续课写成「连续 30:10」，间歇写成「5×1444m」，收尾写成「+400m」。看到不对的直接改。"),
        ("", "「TRIMP 负荷」= Banister TRIMP，逐秒积分（男 b=1.92，HRrest=45、HRmax=198 固定）。"),
        ("", "为什么不用 Garmin 的「训练负荷」：新版设备导出的 FIT 里没有这个字段，48 行永远是空的。TRIMP 用同一套公式覆盖全部 537 行，跨时期可比。"),
        ("", "露点 ℃ 是配速对比的唯一前提。比不同时期的配速前，先看露点。"),
        ("日汇总", "按天自动汇总。质量课一列手填。"),
        ("周汇总", "按周自动汇总。周起始固定为周一。"),
        ("测试与PB", "只放标准化测量：正式比赛、自造计时、可复现的固定段落。训练里的零散快段不要放进来，它们不是测量。"),
        ("力量日志", "每次力量课把动作和剂量记一行。保持时间类的动作（肩胛后缩保持 / 俯卧 Y 保持）连续记，才看得出是不是在变强。"),
        ("课表模板", "空白周课表。先写“本周必发生刺激”，再往每天里放。"),
        ("", ""),
        ("关于自动初判", "“类型”列历史数据是按规则粗判的：<3.5km 且慢于 5:30/km → 热身/冷身；≥15km → 长跑；≤4:30/km → 质量课；4:30–5:30 → 中等；更慢 → 轻松。"),
        ("", "这只是方便筛选，不是记录。看到判错的直接改，改了就不会被脚本覆盖。历史 20 个月里露点从 -7 到 +23℃，配速和心率都被高温抬高过，所以任何自动标签都只能当参考。"),
        ("数据来源", "Data/new_data/<id>/<id>_ACTIVITY.fit（近期逐活动） + summarizedActivities.json（历史汇总，需重新从 Garmin 导出才会更新）"),
        ("", "sessions_weather.csv（历史天气） + Open-Meteo（近期天气，自动抓，缓存于 _wx_auto.json）"),
        ("注意", "手表温度不可用（常年偏高 3–12℃）。气温/露点一律来自 Open-Meteo。"),
        ("", "心率带与腕表数据不可比。2026-09-27 起为胸带，之前为腕表，分两条序列看。"),
    ]
    r = 4
    for a, b in guide:
        if a:
            c = ws0.cell(r, 1, a); c.font = Font(bold=True, size=10, color=BLUE, name="微软雅黑")
            c.alignment = Alignment(None, "top")
        if b:
            c = ws0.cell(r, 2, b); c.font = Font(size=10, name="微软雅黑")
            c.alignment = Alignment(None, "center", wrap_text=True)
            if len(b) > 75:
                ws0.row_dimensions[r].height = 28
        r += 1
    return wb


# ═══════════════════════════════════════════════════════ 5. 主流程
def desktop_dir():
    """桌面（本机被重定向到了 D:\\fjFiles，从注册表取，取不到就回退）"""
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


def mirror_to_desktop(one_file):
    d = desktop_dir()
    if not d:
        print("  ! 找不到桌面，跳过复制")
        return
    dst = os.path.join(d, os.path.basename(one_file))
    try:
        shutil.copy2(one_file, dst)
        print("已复制到桌面:", dst)
    except Exception as e:
        print("  ! 复制到桌面失败:", e)


def resolve_paths():
    """主文件 = 桌面副本与本地副本里「修改时间较新的那一个」。
    这样你在桌面那份里手填 RPE/备注，脚本读的就是它，不会覆盖你的编辑。"""
    d = desktop_dir()
    local = XLSX
    desk = os.path.join(d, os.path.basename(XLSX)) if d else None
    cands = [p for p in (desk, local) if p and os.path.exists(p)]
    if not cands:
        return local, (desk or local)
    master = max(cands, key=os.path.getmtime)
    other = local if master == desk else (desk or local)
    return master, other


def _colmap(ws):
    """表头名字 → 列号。列的顺序、增删都不会让脚本写错位置。"""
    m = {}
    for c in range(1, ws.max_column + 1):
        h = ws.cell(1, c).value
        if h not in (None, ""):
            m[str(h).strip()] = c
    return m


def _row_activity(ws, cm, r, by_id, by_dk):
    """把一行对回一条活动：优先「活动ID」，没有就用（日期+距离）。"""
    idc = cm.get("活动ID")
    if idc:
        v = ws.cell(r, idc).value
        if v not in (None, ""):
            a = by_id.get(str(v))
            if a:
                return a
    kc = cm.get("距离 km")
    if kc:
        d = ws.cell(r, cm.get("日期", 1)).value
        km = ws.cell(r, kc).value
        if isinstance(d, dt.datetime) and isinstance(km, (int, float)):
            return by_dk.get(f"{d:%Y-%m-%d}|{km:.3f}")
    return None


def backfill_derived(wb, acts):
    """给已存在的行补齐派生列。
    TRIMP：每次重算并覆盖（纯计算列，从不手填）。
    结构/工作总量/工作配速/恢复：只在空白时填 —— 你改过的值不会被覆盖。
    列位置按表头名字查 —— 改了列顺序或删了列也不会写错地方。"""
    from openpyxl.styles import Font, Alignment
    ws = wb["训练日志"]
    cm = _colmap(ws)
    by_id = {a["id"]: a for a in acts}
    by_dk = {f"{a['dt']:%Y-%m-%d}|{a['dist_km']:.3f}": a for a in acts}
    n_tp = n_st = 0
    for r in range(2, ws.max_row + 1):
        a = _row_activity(ws, cm, r, by_id, by_dk)
        if not a:
            continue
        f = act_facts(a)
        tp = f.get("trimp")
        ct = cm.get("TRIMP 负荷")
        if tp is not None and ct and ws.cell(r, ct).value != tp:
            c = ws.cell(r, ct, tp)
            c.number_format = "0.0"
            c.font = Font(size=9.5, name="微软雅黑")
            c.alignment = Alignment(horizontal="center")
            c.border = thin()
            n_tp += 1
        st = f.get("struct")
        if not st:
            continue
        wkm = st["work_m"]
        mm, ss = divmod(int(round(st["work_s"])), 60)
        vals = [("结构（自动识别，可改）", st["text"]),
                ("工作总量", f"{wkm:.0f} m / {mm}:{ss:02d}"),
                ("工作配速 /km", dt.timedelta(seconds=st["work_pace"])),
                ("恢复", st.get("rec_text"))]
        for nm, v in vals:
            col = cm.get(nm)
            if v is None or col is None:
                continue
            cell = ws.cell(r, col)
            if cell.value in (None, ""):
                cell.value = v
                cell.number_format = next((x[3] for x in LOGFIELDS if x[0] == nm), "@")
                cell.font = Font(size=9.5, name="微软雅黑")
                cell.border = thin()
                cell.alignment = Alignment(
                    horizontal=("left" if nm in ("结构（自动识别，可改）", "工作总量", "恢复")
                                else "center"))
                n_st += 1
    return n_tp, n_st


def add_strength_plan(wb):
    """新增（或保留已存在的）「力量计划」sheet —— 力量训练的制订模板。
    幂等：已经有了就只补缺的标题行，不覆盖内容。"""
    from openpyxl.styles import Font, PatternFill, Alignment
    NAME = "力量计划"
    if NAME in wb.sheetnames:
        return wb[NAME], False

    ws = wb.create_sheet(NAME)
    # 排到「力量日志」前面，计划 → 记录，顺序连着
    if "力量日志" in wb.sheetnames:
        wb.move_sheet(NAME, offset=wb.sheetnames.index("力量日志") - wb.sheetnames.index(NAME))
    WID = {"A": 27, "B": 25, "C": 23, "D": 24, "E": 13, "F": 26}
    for c, w in WID.items():
        ws.column_dimensions[c].width = w
    ws.sheet_view.showGridLines = False

    def cell(r, c, v=None, bold=False, size=10, color="000000", fill=None,
             align="left", wrap=False, fmt=None):
        x = ws.cell(r, c, v)
        x.font = Font(bold=bold, size=size, color=color, name="微软雅黑")
        if fill:
            x.fill = PatternFill("solid", fgColor=fill)
        x.alignment = Alignment(horizontal=align, vertical="center", wrap_text=wrap)
        if fmt:
            x.number_format = fmt
        return x

    def section(r, text):
        cell(r, 1, text, True, 12, RED)
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=6)
        ws.row_dimensions[r].height = 22

    def question(r, label, hint=None, h=26):
        cell(r, 1, label, True, 10, BLUE, align="left")
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=2)
        cell(r, 3, hint, size=9, color="808080", align="left", wrap=True)
        ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=6)
        for c in range(1, 7):
            ws.cell(r, c).border = thin()
        ws.row_dimensions[r].height = h

    def table(r, heads, rows, fills):
        for i, h in enumerate(heads, 1):
            x = cell(r, i, h, True, 9.5, "FFFFFF", GOLD, "center", True)
            x.border = thin()
        ws.row_dimensions[r].height = 24
        for j, row in enumerate(rows):
            rr = r + 1 + j
            for i in range(1, 6):
                v = row[i - 1] if i - 1 < len(row) else None
                x = cell(rr, i, v, size=9.5,
                         fill=(fills if j % 2 == 0 else "FFFFFF"),
                         align=("left" if i in (1, 3, 4) else "center"), wrap=(i == 4))
                x.border = thin()
            ws.row_dimensions[rr].height = 20
        return r + len(rows) + 1

    # ── 标题
    cell(1, 1, "力量训练 · 周计划模板", True, 16, NAVY)
    ws.merge_cells("A1:F1")
    cell(2, 1, "复制整块到新的一周用。这里填的是判断，不是菜单 —— "
              "先决定这一周要解决什么，再决定怎么排。", size=9.5, color="595959")
    ws.merge_cells("A2:F2")

    # ── ① 本周判断
    section(4, "① 本周判断")
    question(5, "当前认定的限制因素", "一句话就够。例：65–70 分钟后肩胛后上开始酸（姿态耐力）；或：阈值速度上不去", 30)
    question(6, "这一条还是限制吗？",
             "是 → 只加一个变量（剂量 / 难度 / 频率，挑一个）。    不是 → 容量横向转移，不要给同一个动作继续加难度。")
    question(7, "本周力量排在哪几天", "判据：效果是否取决于「什么时候做」。下肢力量和爆发挑神经新鲜度；上背/核心/活动度不挑，挂钩子。")
    question(8, "本周必须当场讲清的取舍", "如果这周要跳过某一块，把理由和代价写下来 —— 跳过只能是调度妥协，不是价值判断。")

    # ── ② 必须排时间的
    section(10, "② 必须排时间的（效果取决于「什么时候做」）")
    r = table(11,
              ["动作", "位置（周几 · 时段）", "组×次 / 保持", "目标刺激", "实际完成"],
              [["下肢力量（分腿蹲 / 单腿 RDL / 提踵）", "质量课之后 48h 内", "2–3 × 6–12 /侧", "单腿支撑力量与刚度", None],
               ["靠墙静蹲 / 分腿蹲等长", "同上", "2–3 × 20–45 秒", "膝与股四头等长耐力", None],
               ["台阶", "跑后 · 质量课前 48h", "8–10 × 20–30 秒", "上坡力量、触地刚性", None],
               ["pogo / 单腿小跳", "质量课当天或之前", "2–3 × 10–20", "弹性 / 反应力量", None],
               ["深蹲跳 / 反向跳", "神经新鲜时，量很小", "3 × 3–5", "爆发", None],
               [None, None, None, None, None]],
              LGOLD)
    cell(r, 1, "⚠ 这些的 DOMS 会砸在质量课上。排期先让路给硬课，不是反过来。"
               "唯一硬约束：上背 / 核心不到力竭。", size=9, color=ORANGE, wrap=True)
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=6)
    ws.row_dimensions[r].height = 20

    # ── ③ 挂钩子的
    section(r + 2, "③ 挂钩子的（效果不取决于「什么时候做」）")
    r2 = table(r + 3,
               ["动作", "每周目标次数", "剂量", "目标刺激", "实际完成"],
               [["肩胛后缩 + 下沉保持", "每天", "90 秒", "中下斜方 / 菱形肌耐力", None],
                ["俯卧 Y 保持", "每天", "45–60 秒", "中下斜方 / 肩胛上旋", None],
                ["靠墙天使", "每天", "2 × 8–10", "胸椎活动度 + 肩胛控制", None],
                ["胸椎后伸活动度", "每天", "30 秒 × 3", "摆臂后摆空间", None],
                ["胸小肌 / 背阔肌拉伸", "每天", "30 秒 × 2", "前侧紧张 / 后摆受限", None],
                ["站姿摆臂", "每天", "90 秒", "摆臂模式（2kg 可改变惯性）", None],
                ["哑铃直臂上拉（躺地）", "每周 3 次", "2–3 × 15", "背阔肌（伸直手臂＝力臂最长）", None],
                ["肩胛俯卧撑", "每周 3 次", "2 × 8–10", "前锯肌", None],
                ["部分悬挂", "每周 2–3 次", "3 × 20 秒", "牵引耐受（脚支撑、无牵扯感为止）", None],
                ["核心（鸟狗 / 侧平板 / 死虫）", "每周 3 次", "2–3 组", "抗旋 / 抗侧屈 / 抗伸展", None],
                [None, None, None, None, None]],
               LGREEN)
    cell(r2, 1, "这些贴在日常里做，不占训练容量。多对一也行 —— 一个能力的收益可以拆给几个动作。"
                "反式划船无器械时用「哑铃直臂上拉 + 肩胛俯卧撑」补，但那不等于等价。",
         size=9, color=ORANGE, wrap=True)
    ws.merge_cells(start_row=r2, start_column=1, end_row=r2, end_column=6)
    ws.row_dimensions[r2].height = 20

    # ── ④ 环境
    section(r2 + 2, "④ 本周环境")
    question(r2 + 3, "可用的器械 / 场地",
             "楼梯 · 书包 5–15kg · 2kg 哑铃 ×2 · 20lb 小环带（无把手）· 门框 · 稳固椅子 · 公园横杆")
    question(r2 + 4, "这周哪些天时间紧", "时间紧的时候先保 ②，③ 可以拆成碎片。")
    question(r2 + 5, "需要、但还没有的东西", "例：带门锚的长管弹力带 —— 一次性解决拉 / 抗旋 / 外旋三项。")

    # ── ⑤ 复盘
    section(r2 + 7, "⑤ 周末复盘")
    for i, (q, hint) in enumerate([
            ("哪个动作变强了", "必须用同一剂量比 —— 加了难度再说「变强」不算。"),
            ("哪个动作没有任何变化", "先重审顺序：动作 → 剂量 → 假设 → 优先级。不要默认加剂量。"),
            ("哪个能力已经不是限制了", "下一周把容量横向转移过去，而不是给同一个动作继续加难度。"),
            ("哪个动作该退役了", "退役 ≠ 没价值，只是它的功能已经被别的动作覆盖了。"),
            ("下周只改一件事", "改一件，才看得出是哪一件起了作用。")]):
        question(r2 + 8 + i, q, hint)
    return ws, True


def main():
    from openpyxl import load_workbook, Workbook
    from openpyxl.styles import Font, Alignment, PatternFill

    index = []
    if os.path.exists(UPIDX):
        index = json.load(open(UPIDX, encoding="utf-8"))
    acts = load_history(index) + load_fits()
    seen = {}
    for a in sorted(acts, key=lambda x: x["dt"]):
        seen.setdefault(a["id"], a)
    acts = sorted(seen.values(), key=lambda x: x["dt"])
    print(f"共找到 {len(acts)} 条跑步记录  ({acts[0]['dt']:%Y-%m-%d} → {acts[-1]['dt']:%Y-%m-%d})")

    wx = load_wx()

    MASTER, OTHER = resolve_paths()
    if os.path.exists(MASTER):
        wb = load_workbook(MASTER)
        print("追加模式 | 主文件:", MASTER)
    else:
        wb = Workbook()
        wb.remove(wb.active)
        build_sheets(wb)
        print("新建工作簿:", MASTER)

    ws = wb["训练日志"]
    # 列位置一律按表头名字查 —— 列增删/换序都不会再错位
    cm = _colmap(ws)
    want = [f[0] for f in LOGFIELDS]
    missing = [n for n in want if n not in cm]
    odd = [h for h in cm if h not in want]
    if missing:
        print("  · 表里没有这些列，本次跳过不写:", missing)
    if odd:
        print("  · 表里这几列脚本不认识，原样保留:", odd)

    by_id = {a["id"]: a for a in acts}
    by_dk = {f"{a['dt']:%Y-%m-%d}|{a['dist_km']:.3f}": a for a in acts}
    idc = cm.get("活动ID")
    existing = set()
    for r in range(2, ws.max_row + 1):
        if idc:
            v = ws.cell(r, idc).value
            if v not in (None, ""):
                existing.add("id|" + str(v))
                continue
        d = ws.cell(r, cm.get("日期", 1)).value
        kc = cm.get("距离 km")
        km = ws.cell(r, kc).value if kc else None
        if isinstance(d, dt.datetime) and isinstance(km, (int, float)):
            existing.add(f"dk|{d:%Y-%m-%d}|{km:.3f}")

    def akey(a):
        return ("id|" + str(a["id"])) if idc else f"dk|{a['dt']:%Y-%m-%d}|{a['dist_km']:.3f}"

    new = [a for a in acts if akey(a) not in existing]
    print(f"日志里已有 {len(existing)} 条，需要新增 {len(new)} 条")

    # 护栏：整表重导的特征就是「新增数 ≈ 总数」。宁可停，也不写坏。
    if existing and len(new) > max(40, len(existing) * 0.4):
        print(f"!! 拒绝写入：要新增 {len(new)} 条，而已有 {len(existing)} 条 —— 这像是整表重导。")
        print("   常见原因：识别用的列（活动ID / 日期 / 距离 km）被删了或改了名。")
        print("   没有做任何修改。")
        return

    start = ws.max_row + 1 if ws.max_row > 1 else 2
    for i, a in enumerate(new):
        r = start + i
        for j, v in enumerate(log_row_values(a, wx), 1):
            nm, _g, _w, fmt, man = LOGFIELDS[j - 1]
            cidx = cm.get(nm)
            if cidx is None:
                continue
            c = ws.cell(r, cidx, v)
            c.number_format = fmt
            c.font = Font(size=9.5, name="微软雅黑")
            c.border = thin()
            if nm in ("结构（自动识别，可改）", "工作总量", "恢复", "症状", "备注"):
                c.alignment = Alignment(horizontal="left", wrap_text=False)
            else:
                c.alignment = Alignment(horizontal="center")
            if nm in ("星期", "时段", "时间") and not man:
                c.fill = PatternFill("solid", fgColor="F7F7F7")
    print(f"已写入 {len(new)} 行（{start} → {ws.max_row}）")

    # Garmin 补旧活动时会跳出日期顺序，乱序才重排
    n_fix = resort_if_needed(ws)
    if n_fix:
        print(f"检测到日期乱序，已按日期重排 {n_fix} 行（手填列原样跟随）")

    # 补齐既有行的派生列
    n_tp, n_st = backfill_derived(wb, acts)
    if n_tp or n_st:
        print(f"回填：TRIMP {n_tp} 格、结构 {n_st} 格")

    # 力量计划模板（幂等）
    _, created = add_strength_plan(wb)
    if created:
        print("已新增 sheet：力量计划")

    # 日汇总 / 周汇总 行补齐
    fill_day_sheet(wb, acts)
    fill_week_sheet(wb, acts)

    # 结构与 TRIMP 的缓存
    ACT_CACHE.pop("__dirty__", None)
    try:
        json.dump(ACT_CACHE, open(ACACHE, "w", encoding="utf-8"), ensure_ascii=False)
        n_t = sum(1 for k, v in ACT_CACHE.items() if isinstance(v, dict) and v.get("trimp"))
        n_s = sum(1 for k, v in ACT_CACHE.items() if isinstance(v, dict) and v.get("struct"))
        print(f"缓存：{len(ACT_CACHE)} 条活动，其中有 TRIMP {n_t} 条、识别出结构 {n_s} 条")
    except Exception as e:
        print("  ! 缓存写入失败:", e)

    saved = _save_wb(wb, MASTER)
    if saved and os.path.abspath(saved) == os.path.abspath(MASTER) \
            and OTHER and os.path.abspath(OTHER) != os.path.abspath(MASTER):
        try:
            shutil.copy2(MASTER, OTHER)
            print("已同步到:", OTHER)
        except Exception as e:
            print("  ! 同步失败:", e)


def resort_if_needed(ws):
    """数据行按日期排序。只有真的乱序才动（Garmin 补齐旧活动时会插进来）。
    整行搬移，每一格的值原样带走，手填内容不改。"""
    n = ws.max_row
    if n < 3:
        return 0
    keys = [ws.cell(r, 1).value for r in range(2, n + 1)]
    keys = [k for k in keys if isinstance(k, dt.datetime)]
    if len(keys) < 2 or all(keys[i] <= keys[i + 1] for i in range(len(keys) - 1)):
        return 0
    rows = []
    for r in range(2, n + 1):
        d = ws.cell(r, 1).value
        rows.append((d if isinstance(d, dt.datetime) else dt.datetime(1900, 1, 1),
                     [ws.cell(r, c).value for c in range(1, ws.max_column + 1)]))
    rows.sort(key=lambda x: x[0])          # 稳定排序 → 同一天内早/晚顺序不变
    for i, (_, vals) in enumerate(rows):
        for c, v in enumerate(vals, 1):
            ws.cell(2 + i, c).value = v
    return len(rows)


def _save_wb(wb, path, quiet=False):
    """保存。文件被 Excel 占用时不报错崩掉，改存成另一个名字并说清楚。"""
    try:
        wb.save(path)
        if not quiet:
            print("已保存:", path)
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
        print("  ! 原文件被占用（多半是 Excel 还开着它），已另存为：")
        print("   ", alt)
        print("    → 关掉 Excel 里那个表格，把这个文件改名覆盖过去即可。")
        return alt


def _styles():
    from openpyxl.styles import Font, Alignment, PatternFill
    return Font, Alignment, PatternFill


def fill_day_sheet(wb, acts):
    from openpyxl.styles import Font, Alignment
    ws = wb["日汇总"]
    have = set()
    for r in range(2, ws.max_row + 1):
        v = ws.cell(r, 1).value
        if v:
            have.add(v if isinstance(v, str) else v.strftime("%Y-%m-%d"))
    days = sorted({a["dt"].date() for a in acts})
    r = 2
    A = "'训练日志'!$A$2:$A$20000"
    F = "'训练日志'!$F$2:$F$20000"
    for d in days:
        key = d.strftime("%Y-%m-%d")
        if key in have:
            continue
        while ws.cell(r, 1).value not in (None, ""):
            r += 1
        ws.cell(r, 1, d).number_format = "yyyy-mm-dd"
        ws.cell(r, 2, "周" + "一二三四五六日"[d.weekday()])
        ws.cell(r, 3, f'=COUNTIF({A},$A{r})')
        ws.cell(r, 4, f'=ROUND(SUMIF({A},$A{r},{F}),2)')
        ws.cell(r, 5, f'=SUMIF({A},$A{r},\'训练日志\'!$G$2:$G$20000)').number_format = "[h]:mm:ss"
        ws.cell(r, 6, f'=ROUND(SUMIF({A},$A{r},\'训练日志\'!$V$2:$V$20000),1)')
        ws.cell(r, 7, f'=ROUND(SUMIFS({F},{A},$A{r},\'训练日志\'!$C$2:$C$20000,"早"),2)')
        ws.cell(r, 8, f'=ROUND(SUMIFS({F},{A},$A{r},\'训练日志\'!$C$2:$C$20000,"晚"),2)')
        ws.cell(r, 9, f'=IFERROR(ROUND(AVERAGEIFS(\'训练日志\'!$R$2:$R$20000,{A},$A{r}),1),"")')
        ws.cell(r, 10, f'=IFERROR(ROUND(AVERAGEIFS(\'训练日志\'!$Q$2:$Q$20000,{A},$A{r}),1),"")')
        ws.cell(r, 11, f'=COUNTIFS({A},$A{r},\'训练日志\'!$W$2:$W$20000,"质量课")')
        for j in range(1, 13):
            c = ws.cell(r, j)
            c.font = Font(size=9.5, name="微软雅黑"); c.border = thin()
            if j > 2:
                c.alignment = Alignment("center")
        r += 1


def fill_week_sheet(wb, acts):
    from openpyxl.styles import Font, Alignment
    ws = wb["周汇总"]
    have = set()
    for r in range(2, ws.max_row + 1):
        v = ws.cell(r, 1).value
        if v:
            have.add(v if isinstance(v, str) else v.strftime("%Y-%m-%d"))
    weeks = sorted({(a["dt"].date() - dt.timedelta(days=a["dt"].weekday())) for a in acts})
    r = 2
    A = "'训练日志'!$A$2:$A$20000"
    F = "'训练日志'!$F$2:$F$20000"
    G = "'训练日志'!$G$2:$G$20000"
    V = "'训练日志'!$V$2:$V$20000"     # TRIMP
    W = "'训练日志'!$W$2:$W$20000"     # 类型
    R = "'训练日志'!$R$2:$R$20000"     # 露点
    J = "'训练日志'!$J$2:$J$20000"     # 平均HR
    DA = "'日汇总'!$A$2:$A$5000"
    DC = "'日汇总'!$C$2:$C$5000"
    for mon in weeks:
        key = mon.strftime("%Y-%m-%d")
        if key in have:
            continue
        while ws.cell(r, 1).value not in (None, ""):
            r += 1
        iso = dt.date(mon.year, mon.month, mon.day).isocalendar()
        ws.cell(r, 1, mon).number_format = "yyyy-mm-dd"
        ws.cell(r, 2, f"{iso[0]}-W{iso[1]:02d}")
        d1 = f"$A{r}"
        lo, hi = f'">="&$A{r}', f'"<="&$A{r}+6'
        ws.cell(r, 3, f'=COUNTIFS({DA},{lo},{DA},{hi},{DC},">0")')
        ws.cell(r, 4, f'=COUNTIFS({A},{lo},{A},{hi})')
        ws.cell(r, 5, f'=ROUND(SUMIFS({F},{A},{lo},{A},{hi}),2)')
        ws.cell(r, 6, f'=SUMIFS({G},{A},{lo},{A},{hi})').number_format = "[h]:mm:ss"
        ws.cell(r, 7, f'=ROUND(SUMIFS({V},{A},{lo},{A},{hi}),0)')
        ws.cell(r, 8, f'=ROUND(IFERROR(SUMPRODUCT(MAX((({A}>={d1})*({A}<={d1}+6))*{F})),0),2)')
        ws.cell(r, 9, f'=COUNTIFS({A},{lo},{A},{hi},{W},"质量课")')
        ws.cell(r, 10, f'=IFERROR(ROUND(AVERAGEIFS({R},{A},{lo},{A},{hi}),1),"")')
        ws.cell(r, 11, f'=IFERROR(ROUND(AVERAGEIFS({J},{A},{lo},{A},{hi}),1),"")')
        for j in range(1, 13):
            c = ws.cell(r, j)
            c.font = Font(size=9.5, name="微软雅黑"); c.border = thin()
            if j > 2:
                c.alignment = Alignment("center")
        r += 1


if __name__ == "__main__":
    main()
