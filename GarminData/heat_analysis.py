import csv, statistics, json
from collections import defaultdict

P = "D:/running/GarminData/sessions_weather.csv"
R = list(csv.DictReader(open(P, encoding="utf-8")))
for r in R:
    r["pace"] = float(r["pace"]) if r["pace"] else None
    r["hr"] = int(float(r["hr"])) if r["hr"] else None
    r["km"] = float(r["km"]); r["T"] = float(r["T"]); r["DP"] = float(r["DP"]); r["RH"] = float(r["RH"])
print("sessions:", len(R))

print("\n=== A. 真实热负荷（训练时刻，露点为准）===")
bym = defaultdict(list)
for r in R: bym[r["mo"]].append(r)
print("  月份      n    气温°C  露点°C  RH%   热负荷档")
for k in sorted(bym):
    v = bym[k]
    T = statistics.mean(x["T"] for x in v); DP = statistics.mean(x["DP"] for x in v); RH = statistics.mean(x["RH"] for x in v)
    if DP < 12: tag = "理想（<12）"
    elif DP < 18: tag = "轻微（12-18）"
    elif DP < 21: tag = "明显（18-21）"
    elif DP < 24: tag = "严重（21-24）"
    else: tag = "极端（>24）"
    print(f"  {k}  {len(v):3d}   {T:5.1f}  {DP:5.1f}  {RH:4.0f}   {tag}")

print("\n=== B. 固定 HR 带内的配速（热中性对比，这才是正确的跨时期比较）===")
BANDS = [(135,145), (145,155), (155,165), (165,175)]
def era(r):
    if r["mo"] in ("2025-12","2026-01"): return "2025-12→2026-01 (80km/w, 露点-6)"
    if r["mo"] in ("2026-05","2026-06"): return "2026-05→06 (67km/w, 露点~16)"
    if r["mo"] in ("2026-07","2026-08"): return "2026-07→08 (45km/w, 露点~23)"
    if r["mo"] == "2026-09": return "2026-09 (50km/w, 露点15)"
    return None
print(f'  {"HR带":10s} {"时期":34s} n   平均配速      露点')
for lo,hi in BANDS:
    for e in ["2025-12→2026-01 (80km/w, 露点-6)","2026-05→06 (67km/w, 露点~16)",
              "2026-07→08 (45km/w, 露点~23)","2026-09 (50km/w, 露点15)"]:
        sel = [r for r in R if lo <= (r["hr"] or 0) < hi and r["pace"] and era(r) == e and r["km"] >= 6]
        if len(sel) < 3: continue
        p = statistics.mean(x["pace"] for x in sel)
        print(f'  {lo}-{hi:<6} {e:34s} {len(sel):2d}   {int(p)}:{int(p%1*60):02d}/km    {statistics.mean(x["DP"] for x in sel):5.1f}')
    print()

print("=== C. 热修正后的配速（露点修正 + T+DP 修正）===")
def adjust(p, T, DP):
    dpf = DP*9/5+32; tf = T*9/5+32
    a1 = (dpf-60)*0.025*60/1.609 if dpf > 60 else 0          # 秒/km
    a2 = p*(1 - 1/(1+0.01*max(0,(tf+dpf-130))/10)) if (tf+dpf) > 130 else 0
    return max(a1, a2)
for e in ["2025-12→2026-01 (80km/w, 露点-6)","2026-05→06 (67km/w, 露点~16)",
          "2026-07→08 (45km/w, 露点~23)","2026-09 (50km/w, 露点15)"]:
    sel = [r for r in R if era(r) == e and r["pace"] and r["hr"] and 140 <= r["hr"] < 165 and r["km"] >= 6]
    if not sel: continue
    raw = statistics.mean(x["pace"] for x in sel)
    adj = statistics.mean(x["pace"] - adjust(x["pace"], x["T"], x["DP"]) for x in sel)
    print(f'  {e:34s} n={len(sel):2d} 实测 {int(raw)}:{int(raw%1*60):02d}/km  →  热修正 {int(adj)}:{int(adj%1*60):02d}/km  (HR 140-165)')
