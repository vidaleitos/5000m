HRMAX = 197
print("RHR | 60%HRR上限(<136基准) | 56%HRR Rigen均值目标 | 74% | 78%")
for r in range(40, 53, 2):
    f = lambda p: round((HRMAX - r) * p + r)
    print(f"{r:3d} | {f(0.60):3d} | {f(0.56):3d} | {f(0.74):3d} | {f(0.78):3d}")

# 今日/明日配速参考核对
print()
print("9/13 实测: 5.01km / 30:04 ->", round(30*60+4), "s ;", round((30*60+4)/5.01), "s/km =",
      f"{(30*60+4)/5.01/60:.2f} min/km")
for pace in ["5:45", "6:00", "6:15", "5:30"]:
    m, s = pace.split(":")
    spp = int(m)*60+int(s)
    print(f"  {pace}/km -> 5km {spp*5//60}:{spp*5%60:02d} · 6km {spp*6//60}:{spp*6%60:02d}")
