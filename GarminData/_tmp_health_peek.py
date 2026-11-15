import json, os

d = r"D:\running\GarminData\Data\DI_CONNECT\DI-Connect-Wellness"

def peek(name, n=6):
    p = os.path.join(d, name)
    j = json.load(open(p, encoding="utf-8"))
    print("=" * 70)
    print(name, "entries:", len(j))
    print("first entry:", json.dumps(j[0], ensure_ascii=False)[:400])
    for e in j[-n:]:
        print("  ", json.dumps(e, ensure_ascii=False)[:400])

peek("2026-05-21_2026-08-29_130074653_healthStatusData.json")
peek("2026-05-23_2026-08-31_130074653_sleepData.json", 4)
print("=" * 70)
print("bioMetrics_latest:", json.dumps(json.load(open(os.path.join(d, "130074653_bioMetrics_latest.json"), encoding="utf-8")), ensure_ascii=False)[:400])
