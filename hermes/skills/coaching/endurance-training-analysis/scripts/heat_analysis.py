#!/usr/bin/env python3
"""Cross-period comparison of running efficiency, with heat controlled and interval
sessions excluded.

Usage:
    python heat_analysis.py                      # reads sessions_weather.csv
    python heat_analysis.py sessions_weather.csv

Input: the CSV produced by fetch_weather.py, with columns
    t, mo, km, min, pace, hr, mx, T, RH, DP, loc

Outputs three tables:
  A. monthly real heat load (dew point decides the band)
  B. ** PRIMARY ** dew-point-matched + HR-band-matched direct comparison (assumption-free)
  C. per-period pace@reference-HR via within-period regression (report n and R2; unstable)

DESIGN CHOICES - do not undo these without a reason:
  * 'steady sessions only' filter: an interval session's whole-session average pace is
    dragged slow by warm-up / cooldown / recovery jogs, so pairing it with avgHR is
    meaningless and reads as fake fitness collapse.
  * Dew-point-matched direct comparison is the PRIMARY judgement. Correction formulas
    disagree with each other; a corrected pace is a sensitivity check, not evidence.
  * Sign convention for normalising pace: pace is SLOWER at higher dew point, so
    P_ref = P + k*(DP_ref - DP).  Getting this backwards silently inverts conclusions.
"""
import csv
import statistics
import sys
from collections import defaultdict

SRC = sys.argv[1] if len(sys.argv) > 1 else "sessions_weather.csv"
MIN_KM = 7.0            # steady-session filter
MAX_HR_SPREAD = 28      # maxHR - avgHR; above this the session contains real intervals
REF_HR = 150            # reference heart rate for the efficiency series
K_DP = 0.41             # s/km per degree C of dew point (literature 0.3-0.7)
DP_BANDS = [(-15, 5), (5, 12), (12, 18), (18, 30)]


def load(path):
    rows = []
    for r in csv.DictReader(open(path, encoding="utf-8")):
        if not r.get("pace") or not r.get("hr") or not r.get("DP"):
            continue
        rows.append(dict(
            t=r["t"], mo=r["mo"], km=float(r["km"]), pace=float(r["pace"]),
            hr=int(float(r["hr"])), mx=int(float(r["mx"])) if r.get("mx") else None,
            T=float(r["T"]), RH=float(r["RH"]), DP=float(r["DP"]),
            loc=r.get("loc"), name=r.get("name"),
        ))
    return rows


def fmt(p):            # minutes per km -> m:ss
    return f"{int(p)}:{int(p % 1 * 60):02d}"


def steady(rows):
    return [r for r in rows
            if r["km"] >= MIN_KM and 3.0 < r["pace"] < 8.0
            and r["mx"] is not None and (r["mx"] - r["hr"]) <= MAX_HR_SPREAD]


def lin(xs, ys):
    n = len(xs)
    if n < 3:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx == 0:
        return None
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    a = my - b * mx
    ss = sum((y - my) ** 2 for y in ys)
    sr = sum((y - (a + b * x)) ** 2 for x, y in zip(xs, ys))
    return a, b, (1 - sr / ss if ss else 0.0)


def norm_pace(p, dp, ref=5.0, k=K_DP):
    """Normalise an observed pace to a reference dew point (minutes/km).
    Higher dew point -> slower pace, so subtracting the excess makes it FASTER."""
    return p + k * (ref - dp) / 60.0


def band(dp):
    for lo, hi in DP_BANDS:
        if lo <= dp < hi:
            return f"DP {lo}..{hi}C"
    return "DP other"


def main():
    rows = load(SRC)
    S = steady(rows)
    print(f"sessions {len(rows)} -> steady sessions {len(S)} "
          f"(km>={MIN_KM}, maxHR-avgHR<={MAX_HR_SPREAD})\n")
    if not S:
        return

    by_month = defaultdict(list)
    for r in S:
        by_month[r["mo"]].append(r)

    print("=== A. monthly real heat load (dew point decides the band) ===")
    print("  month     n   air C   RH %   dew C   band")
    for mo in sorted(by_month):
        v = by_month[mo]
        T = statistics.mean(x["T"] for x in v)
        RH = statistics.mean(x["RH"] for x in v)
        D = statistics.mean(x["DP"] for x in v)
        print(f"  {mo}  {len(v):3d}  {T:6.1f}  {RH:5.0f}  {D:6.1f}   {band(D)}")

    print("\n=== B. PRIMARY: dew-point-matched + HR-band-matched (assumption-free) ===")
    print("  A month is only comparable to another month in the SAME dew-point band.")
    groups = defaultdict(list)
    for mo, v in by_month.items():
        groups[band(statistics.mean(x["DP"] for x in v))].append(
            (mo, len(v), statistics.mean(x["DP"] for x in v)))
    for b in sorted(groups):
        print(f"\n  [{b}]")
        for mo, n, dp in sorted(groups[b]):
            line = f"    {mo}  n={n:2d}  mean DP {dp:5.1f}  "
            for lo, hi in [(135, 145), (145, 155), (150, 160), (155, 165)]:
                sel = [x["pace"] for x in by_month[mo] if lo <= x["hr"] < hi]
                line += f"HR{lo}-{hi}: {fmt(statistics.mean(sel))} (n={len(sel)})  " if len(sel) >= 2 else \
                        f"HR{lo}-{hi}: --   "
            print(line)

    print("\n=== C. efficiency series: pace @ reference HR (regression; n and R2 shown) ===")
    print(f"  reference HR = {REF_HR}; 'norm' = normalised to dew point 5 C via k={K_DP} s/km/C")
    print("  month     n   R2    raw @refHR   dew C   norm@DP5")
    for mo in sorted(by_month):
        v = by_month[mo]
        f = lin([x["hr"] for x in v], [x["pace"] for x in v])
        if not f:
            print(f"  {mo}  {len(v):3d}   --   (too few points)")
            continue
        a, b, r2 = f
        p = a + b * REF_HR
        D = statistics.mean(x["DP"] for x in v)
        print(f"  {mo}  {len(v):3d}  {r2:4.2f}  {fmt(p):>7}/km   {D:5.1f}   {fmt(norm_pace(p, D))}/km")
    print("\n  CAUTION: a within-month fit extrapolated to the reference HR is unstable when that")
    print("  month's sessions cluster at one HR end. Trust table B over table C.")


if __name__ == "__main__":
    main()
