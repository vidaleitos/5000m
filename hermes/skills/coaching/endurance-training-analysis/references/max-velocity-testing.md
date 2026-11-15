# Max-velocity testing — rep length, field trust, and what the peak actually says

Companion to the "Speed is my weakness" subsection of SKILL.md. The question this answers:
*the athlete believes speed is the limiter — is it, and how do you read the test without over- or
under-calling the result?*

---

## The session that settled it (worked case)

Warm-up 2.6 km + 2 × 150 m, on a 400 m track, light headwind, ~10 °C. The athlete flagged the execution
flaws himself: the first rep was mis-marked and actually 220 m with a late watch-stop; the second had a
mid-rep glance at the watch that cost him a stride.

| | 220 m rep | 150 m rep |
|---|---|---|
| elapsed | 37.77 s | 22.16 s (moving 20 s) |
| average speed | 5.82 m/s | 6.77 m/s |
| **peak speed** | **7.493 m/s** (2:13.5/km) | **7.371 m/s** (2:15.7/km) |
| GCT | 179.5 ms | **156.0 ms** |
| stride | 174.1 cm | **179.5 cm** |
| vertical oscillation | 7.43 cm | **6.14 cm** |
| vertical ratio | 4.66 % | **3.42 %** |
| max cadence | 220 | **234** |
| avg / max power | 342 / 752 W | 333 / 690 W ⚠️ |
| elevation gain | 0 m | **6 m** ⚠️ (impossible) |

### Reading it

1. **The 150 m was the better rep mechanically on every field that survives instrumentation** — shorter
   contact, longer stride, less vertical waste, higher cadence. The athlete's own read was right.
2. **The longer rep had the better peak** — the only advantage it had was runway.
3. **Peak is not the ceiling.** A 150 m from a standing start spends roughly the first 40 m accelerating
   and the last 15 m decelerating. The peak recorded is "fastest sustained for one sample inside 150 m".

### Reserve arithmetic — do it twice, keep both

```
5 K pace              3:45–3:50/km   ->  4.41 m/s
peak 1-s velocity     7.37–7.49 m/s  ->  reserve 1.67–1.70 x
200 m average (same day, fresh)  ~5.95 m/s  ->  reserve 1.35 x
                                  gap       0.32-0.35 x
```

- **The first number says the top gear is fine.** Not a limiter. Close the speed budget; maintenance only
  (strides, an occasional short sprint).
- **The gap says what is actually missing.** Reaching 7.5 m/s and only holding ~6 m/s means the drop-off
  from peak is steep. That is the same construct as a long run fading over the last 3 km — quick to
  recruit, slow to sustain.

**Do not average the two into one reserve figure.** They point at opposite prescriptions.

---

## Field trust for short efforts

| field | reliable? | note |
|---|---|---|
| `maxSpeed` (whole-session) | ✅ | the single most useful field, and usually absent from FIT lap summaries |
| elapsed duration | ✅ | but a late watch-stop adds 1–2 s; cross-check `movingDuration` |
| moving duration | ⚠️ | excludes the closing deceleration, so it is **not** the run time |
| GCT, stride, vertical oscillation, vertical ratio | ✅ | accelerometer; structure-independent |
| cadence (per-rep) | ⚠️ | step counts on a 20 s rep are undercounted; do not derive stride from them |
| running power | ❌ | modelled from speed + grade; inherits GPS-altitude error |
| elevation gain | ❌ | a 150 m rep reporting 6 m (4 %) on a flat track is the altitude fix inventing terrain |
| heart rate | ✅ | but meaningless — HR lags 20–30 s and cannot express a 22 s effort |

**The altitude trap is the one that produces a wrong story fastest.** In this case it simultaneously
reported a 4 % climb and inverted the power-vs-speed relationship (slower rep, higher power). Had the
power numbers been trusted, the conclusion would have been "the second rep cost more" — the opposite of
the mechanics.

---

## Test-design rules

1. **Rep length ≥ 200 m for a max-velocity reading.** Below that the runway is the measurement.
2. **Send the athlete in both directions** and take the better one — a light headwind on 150 m is worth
   more than the difference being measured.
3. **Full recovery between reps** (4–5 min walking). This is a neural test, not a metabolic one; partial
   recovery turns it into a speed-endurance test and changes what the number means.
4. **Measurement before any aerobic volume in the same session.** 15 min easy + activation + strides is
   the warm-up; 50 min of aerobic is a fatigue source.
5. **Read `maxSpeed`, not the average pace.** The average over 150 m from a standing start is mostly a
   statement about acceleration.
6. **Say beforehand which result would change the conclusion.** Otherwise the number gets rationalised
   after the fact — in either direction.

---

## What this test does and does not license

**Licenses:** closing the max-velocity budget; treating speed as a relative strength; redirecting the
remaining training time to the sustained side.

**Does not license:** concluding the athlete is fast *at 5 K* (that is a different measurement), or that
better mechanics means more speed (it means cheaper speed), or a reserve band from the literature
(1.40–1.60 × is folklore unless cited for this event and level).
