# Heat & climate matching for training-data comparison

Condensed reference. Everything here is either a literature threshold, a formula, or a transferable
methodology lesson.

## 1. Why body-worn temperature is unusable

A wrist optical/thermistor temperature channel reads skin-adjacent air, warmed by the body and by
sunlight. Measured against reanalysis weather at the same hour and location:

| Month | Watch reported | Actual air temp | Error |
|---|---|---|---|
| December | 23.6 °C | 0.6 °C | +23 °C |
| January | 22.4 °C | −1.7 °C | +24 °C |

In summer the error is small (watch 31.1 vs actual ~25), so the channel *looks* plausible if you only
ever look at summer — and it is roughly monotone within a season, which is exactly why it silently
corrupts cross-season comparison.

**Rule: never use a watch temperature field for anything spanning more than a few days.
Fetch real weather instead.**

## 2. Real climate table (worked example)

Location 35.004 N, 115.183 E — early-morning sessions (05:00–06:30), Open-Meteo historical reanalysis.

| Month | Air °C | RH % | Dew point °C | Load band |
|---|---|---|---|---|
| 03 | 7.5 | 53 | −3.5 | ideal |
| 04 | 12.5 | 82 | 9.2 | ideal |
| 05 | 18.2 | 82 | 15.0 | mild |
| 06 | 22.0 | 72 | 16.4 | mild |
| 07 | 25.2 | **90** | **23.4** | **severe** |
| 08 | 24.0 | **92** | **22.5** | **severe** |
| 09 | 19.3 | 79 | 15.4 | mild |
| 10 | 12.5 | 87 | 10.4 | ideal |
| 11 | 6.2 | 76 | 1.9 | ideal |
| 12 | **0.6** | 74 | **−3.9** | ideal |
| 01 | **−1.7** | 69 | **−7.1** | ideal |

**Seasonal implication worth stating to any athlete in this climate:** there is one contiguous
4-month window (Oct–Jan) with dew point below 12 °C. Training done in it sets the ceiling for the
following summer; the hot months are structurally unable to absorb high volume or hard sessions.

## 3. Dew-point thresholds for training

| Dew point | Effect |
|---|---|
| `< 12 °C` | ideal. Pace targets fully valid. |
| `12–18 °C` | easy running largely unaffected; hard sessions feel harder. Add tolerance. |
| `18–21 °C` | adjust pace; run quality sessions by effort / HR rather than pace. |
| `21–24 °C` | uncomfortable; quality drops. Move the session in the day or downgrade it. |
| `> 24 °C` | safety first — cancel or relocate hard sessions. |

## 4. Pace-adjustment formulas and their limits

- **Dew-point rule:** `adjusted = base + (DP°F − 60) × 0.025 min/mile`
- **Combined rule:** when `T + DP` (both °F) exceeds 130, penalty ≈ `1 % per 10 points above`

These two disagree with each other, and heat-index-based methods are derived from sedentary data and
are less accurate for running. **Prefer dew point directly.**

Sign convention, spelled out because it is easy to invert:

```python
# A higher dew point means a slower pace.
# P_observed = P_base + k * (DP - DP_ref),  k > 0
# therefore, normalising an observation to a reference dew point:
def norm_pace(p_min_per_km, dp_c, dp_ref_c=5.0, k=0.41/60):
    return p_min_per_km + k * (dp_ref_c - dp_c)
# A run at DP 23 °C normalises to DP 5 °C by becoming ~7 s/km FASTER.
```

Coefficient `k` is uncertain — roughly `0.3–0.7 s/km per °C` in the literature; the data-driven
regression in a real dataset gave ~`0.4 s/km per °C`. **Never present a corrected pace as if it were
measured.** The corrected value is a sensitivity check, not evidence.

## 5. The comparison method that actually works

Do NOT compare era-mean pace. Do this instead:

1. Filter to steady sessions: `km >= 6` and `maxHR - avgHR <= 28`.
2. For each period, get pace at a **fixed reference HR** — either by band-matching directly or by a
   within-period linear fit. Direct band-matching is assumption-free and preferred.
3. Group periods by **dew-point band** (e.g. `14–17 °C`, `22–24 °C`) and compare only within band.
4. Report the year-on-year matched pair. This is usually the strongest single statement.
5. Name what heat does NOT explain.

Known weaknesses to declare when you use them:
- A within-period regression extrapolated to a reference HR is unstable when that period's sessions
  cluster at one HR end (report `n` and `R²`).
- Band-matched samples for a single month can be very small (`n = 2`). Say so.

## 6. Worked example: a conclusion that had to be retracted

**First conclusion (wrong):** "Volume fell from 80 to 45 km/week, therefore aerobic fitness
collapsed." Supported by a race-prediction widget trending from 17:26 to 17:59.

**What climate matching showed:**

- The volume collapse coincided exactly with dew point peaking at 22.5–23.4 °C **at 90 % humidity**.
  High volume in those conditions is physiologically unavailable, not a failure of discipline.
  The "collapsed base" verdict had to be **half-retracted**.
- Dew-point-matched, HR-matched comparison, dew point 14–17 °C:

  | Period | @HR150 |
  |---|---|
  | 2026-05 | 4:57 |
  | 2026-06 | 4:58 |
  | 2026-09 (now) | **5:21** |

  Same dew point, same HR → **23 s/km slower**. Heat cannot explain September. This is the real,
  heat-proof finding — and it pointed at a different corrective action than the first conclusion did.
- Dew-point-matched year-on-year, dew point 22–24 °C: `5:44 → 4:52` at HR 155–165. Same conditions,
  a year apart — genuine large progress.

**Method lessons:**
1. The instrument being bad did not justify dropping the confound; fetching better data resolved it.
2. The watch race prediction was ~60–70 s optimistic and drifted when hard efforts stopped — a trend
   indicator, not a measurement.
3. Filtering out interval sessions changed a month's apparent efficiency by ~25 s/km.
4. The corrected conclusion was *still* actionable, and more precise than the wrong one.
