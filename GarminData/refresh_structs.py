# -*- coding: utf-8 -*-
"""并行重算 _act_cache.json 里的「结构」部分（保留已算好的 TRIMP）。
用法：python refresh_structs.py
意义：结构识别的算法改动（STRUCT_VER）只需要这一个脚本，不用重跑整个 build_log.py。
"""
import os, json, sys, time
from concurrent.futures import ProcessPoolExecutor

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
ACACHE = os.path.join(BASE, "_act_cache.json")

import build_log as B          # noqa: E402


def work(item):
    aid, path = item
    if not path or not os.path.exists(path):
        return aid, None
    try:
        laps = B._lap_pass(path)
        return aid, B.structure_from_laps(laps)
    except Exception:
        return aid, None


def main():
    cache = json.load(open(ACACHE, encoding="utf-8")) if os.path.exists(ACACHE) else {}
    # 活动 ID → FIT 路径
    paths = {}
    up = os.path.join(BASE, "_uploaded_index.json")
    if os.path.exists(up):
        for x in json.load(open(up, encoding="utf-8")):
            paths.setdefault(os.path.splitext(os.path.basename(x["file"]))[0], None)
    # 直接从 build_log 的数据源拿 ID→路径
    idx = json.load(open(up, encoding="utf-8")) if os.path.exists(up) else []
    id2path = {}
    for a in B.load_fits():
        id2path[a["id"]] = a.get("path")
    for a in B.load_history(idx):
        if a.get("path"):
            id2path[a["id"]] = a["path"]
    items = [(aid, id2path.get(aid)) for aid in list(cache)]
    t0 = time.time()
    n_ok = 0
    with ProcessPoolExecutor(max_workers=8) as ex:
        for aid, st in ex.map(work, items, chunksize=4):
            if aid in cache and isinstance(cache[aid], dict):
                cache[aid]["struct"] = st
                cache[aid]["sv"] = B.STRUCT_VER
                if st:
                    n_ok += 1
    json.dump(cache, open(ACACHE, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"完成：{len(items)} 条，识别出结构 {n_ok} 条，用时 {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
