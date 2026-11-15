# -*- coding: utf-8 -*-
"""给 DI-Connect-Uploaded-Files 里的 FIT 文件建索引（活动起止时间 + 距离），
输出 _uploaded_index.json。跑一次就够，之后直接读索引。"""
import os, json, glob, sys
import fitparse

BASE = r"D:/running/GarminData"
UP = os.path.join(BASE, "Data", "DI_CONNECT", "DI-Connect-Uploaded-Files")
OUT = os.path.join(BASE, "_uploaded_index.json")

paths = []
for root, dirs, files in os.walk(UP):
    for f in files:
        if f.lower().endswith(".fit"):
            paths.append(os.path.join(root, f))
print("FIT 文件总数:", len(paths), flush=True)

index = []
bad = 0
for i, p in enumerate(paths):
    try:
        ff = fitparse.FitFile(p)
        got = False
        for m in ff.get_messages("session"):
            a = {x.name: x.value for x in m}
            st = a.get("start_time")
            d = a.get("total_distance")
            if st is None or d is None:
                continue
            index.append({
                "file": os.path.relpath(p, UP),
                "t": st.isoformat() if hasattr(st, "isoformat") else str(st),
                "sport": a.get("sport"),
                "km": round(d / 1000.0, 4),
                "hr": a.get("avg_heart_rate"),
                "dur": a.get("total_timer_time"),
            })
            got = True
            break
        if not got:
            bad += 1
    except Exception:
        bad += 1
    if (i + 1) % 500 == 0:
        print(f"  {i+1}/{len(paths)}  已索引 {len(index)}", flush=True)

json.dump(index, open(OUT, "w", encoding="utf-8"), ensure_ascii=False)
print(f"完成：索引 {len(index)} 条，无 session {bad} 个 → {OUT}", flush=True)
ts = sorted(x["t"] for x in index)
if ts:
    print("时间范围:", ts[0], "→", ts[-1], flush=True)
