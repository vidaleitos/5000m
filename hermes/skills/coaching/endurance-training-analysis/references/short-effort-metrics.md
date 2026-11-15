# Short efforts, short laps and stairs — worked example and reliability rules

Companion to the SKILL.md section "Short efforts, sprints and stairs".

## Real session (three activities uploaded separately, same morning)

An easy run, then strides, then stair sprints — recorded as three activities, one after another.

### 1. Strides — 4 × ~100 m, GPS-lap triggered

| rep | lap time | peak speed (record-level) | peak cadence (total) | **ground contact at peak** |
|---|---|---|---|---|
| 1 | 21.5 s | 6.58 m/s (2:32/km) | — | — |
| 2 | 17.4 s | 6.28 m/s (2:39/km) | 204 | 178 ms |
| 3 | 16.9 s | 5.94 m/s (2:48/km) | 208 | 173 ms |
| 4 | 17.0 s | 6.07 m/s (2:44/km) | 210 | **156 ms** |

What is trustworthy here: **rep times**, cadence, and GCT. What is not: pace, distance, step length
(the lap-level `avg_step_length` came out at 1495 cm = 15 m/step, which is impossible — the derived
fields collapse on short GPS-triggered laps).

**Why GCT is the interesting number.** Put the same athlete's contact times on one scale:

```
easy pace            ~242 ms
race pace            ~197 ms
stride peak          ~156–178 ms   <- the body's actual floor
```

That gives a concrete mechanical goal — push the *race-pace* contact time down toward a floor the
body has already demonstrated it can reach. A stride session is the cheapest way to measure the floor.

Rep 1 being slowest (21.5 s) is correct behaviour, not a mistake: the first rep doubles as activation.
When prescribing, say so explicitly, otherwise the athlete reads it as a failed rep.

### 2. Stair sprints — 8 reps

| What | Value |
|---|---|
| Rep times | 10.5 / 11.3 / 10.9 / 11.3 / 10.7 / 11.0 / 10.5 / 11.2 s |
| Walk-down recovery | 31–38 s |
| Total ascent (barometer) | 42 m |
| Derived vertical per rep | ~5 m |
| HR during climbs | 111–133 bpm (whole-session max 165) |
| GPS distance for the whole session | 357 m — meaningless |

Two separate findings from the same data:

1. **HR says nothing about intensity here.** 11 s is far too short for HR to rise; the 133 bpm ceiling
during climbs is not evidence the effort was easy. Do not report it as such.
2. **Rep-time spread was only 0.9 s (8 %).** Consistent — but consistency alone cannot distinguish
   "hit every rep at max" from "found a comfortable repeatable rhythm". The only way to tell is to
   calibrate: make rep 1 all-out, then require later reps within +5 %. Without that anchor, "did this
   athlete go hard?" is unanswerable from the file.

**The real defect was segment length, not rep count.** 42 m of ascent over 8 climbs = ~5 m per climb =
reaching the top in roughly 25 m of horizontal travel. A true 10–12 s hill rep covers ~50–60 m and
includes a stable high-force phase. The fix is a longer continuous climb, not more reps.

Per-lap barometer ascent is also unreliable: descent laps in this session were credited with *more*
ascent (28 m) than climb laps (12 m), because the altimeter lags. Only the session total is meaningful.

## Rules to carry forward

1. Grade short-effort data by **lap time**, cadence, and GCT. Everything GPS-derived is suspect.
2. **Never** use peak HR to judge reps under ~15 s.
3. Check **segment length**, not just rep count — a short hill/stair delivers a fraction of the stimulus.
4. When rep times are suspiciously uniform, ask for the calibration rep (rep 1 all-out +5 % gate).
5. Ask the athlete one plain question the file cannot answer: **"did the last one still feel fast?"**
6. On a session recorded as several activities back to back, treat them as one training day for load
   accounting (easy run + strides + stairs = one day, roughly `9.0 + 0.9 + stairs`).
