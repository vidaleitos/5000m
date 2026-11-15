# Prescribing a block

Companion to the prescription section of SKILL.md. Analysis tells you *what limits the athlete*;
this is how to turn that into sessions without turning it into a table of targets.

## Start from the limitation, not from the event

Work out what actually bounds performance before choosing any workout.

```
race pace / CS ratio:
  ~5–6%   -> sustainable ceiling (CS / threshold) IS the limit -> volume + threshold work
  8–12%   -> normal for a trained 5 K runner
  >12%    -> speed reserve is short -> VO2max intervals and short reps
```

Also compare the athlete's **speed reserve** against their **sustainable ratio**. Someone who can
hold 3:24/km for 400 m reps but whose 5 K pace is only 6 % above CS does not need more speed.
Giving them more VO2max work because it looks "harder" is the classic mis-prescription.

## Stimulus set (per week)

| Stimulus | Dose | Develops |
|---|---|---|
| **Threshold / sub-threshold** | 30–45 min of work | critical speed — the usual limiter |
| **Race-pace** | 4–6 km of work | converting CS into race performance |
| **Long run** | 1×, easy to steady | aerobic base, late-race durability |
| **Neuromuscular** | strides 2–3×, hills/stairs 1× | ground contact time, economy |
| Easy aerobic | fills the rest | raises the ceiling on absorbable threshold work |

**Volume is what these sum to.** Never state a kilometre target; state the set and report the sum.

## Continuous vs interval threshold

Both work. They are not interchangeable, and the default is usually wrong in the same direction:
people reach for intervals because they look more like "real training".

- **Continuous is the default.** One 10–14 km run at 93–99 %%CS = *40–60 min* at that intensity.
  3×10 min gives 30 min of work with two interruptions. Continuous also spends far more time in the
  mechanical state you are trying to adapt (ground contact time at speed).
- **Intervals are a dose controller**, not a substitute: use them when you want **40–50 min** of
  threshold work in one session but continuous running would break down; or when you need to sit
  precisely at the top of the band.

Progression for a continuous threshold session: **20 → 25 → 30 → 35 min**, then graduate to a
12–14 km medium-long run. Split it if you must (2×12, 3×10, 3×14) — **total time matters more than
how it is divided.**

## %%CS pace table

Derive the athlete's own table; do not import one.

```
pace_s_per_km = 1000 / ( %%CS * CS_m_s )
```

Worked example at CS = 4.196 m/s (3:58/km):

| %%CS | pace | role |
|---|---|---|
| 88–92 %% | ~4:20–4:30 | medium / steady |
| 95 %% | 4:11 | threshold, lower edge |
| 97 %% | 4:05 | threshold, upper edge |
| 100 %% | 3:58 | critical speed |
| 106–108 %% | 3:40–3:45 | race pace (special block) |
| 112–118 %% | 3:25–3:35 | VO2max reps |

**State the *window*, not just the target** — the stimulus is defined by the band. A threshold session
is bounded: faster than the top edge stops being threshold work (and costs reps 2 and 3); slower than
the bottom edge becomes a different session entirely.

## Target arithmetic

To go from a current CS to a goal time (holding D' constant):

```
required_CS = (distance - D') / target_time
```

This is how to decide whether a goal is a 6-month or a 2-year project, and what the intermediate
checkpoints are. Report it as arithmetic, not as a promise.

## Double threshold

**Principle that transfers:** lower the per-session intensity and raise the frequency → a large
increase in threshold volume without a proportional increase in fatigue.

**Form that does not transfer, for two reasons:**

1. It is built on **120–180 km/week** of total volume. Below that, copying it displaces strength and
   mechanical work.
2. **It depends on real-time lactate control** (2.0–3.5 mmol/L). Without a lactate meter, "sub-threshold"
   is guessed by pace, both sessions drift above threshold, and the result is **two hard sessions in one
   day — the worst possible outcome**, not two sustainable ones.

**Usable intermediate:** one full threshold session + one sub-threshold continuous day on an adjacent
day + one long run. Three distinct intensities, accumulating to a large dose, requiring no meter.

A portable lactate meter is the one purchase that converts LT1/LT2 from an inference into a
measurement. Offer it as an option; never present current threshold paces as measured values.

## Hill and stair sprints

| Grade | Length | Duration | Use |
|---|---|---|---|
| **5–8 %%** | **60–100 m** | **10–15 s** | preferred — force and speed, mechanics preserved |
| 8–12 %% | 40–70 m | 8–12 s | more force-biased; stairs land here |
| 3–5 %% | 100–150 m | 15–20 s | drifts toward speed-endurance / aerobic |
| >15 %% | <40 m | <8 s | excessive trunk lean, stride collapses — avoid |

5 %% is 5 m of rise per 100 m — **a bridge approach or embankment ramp qualifies; you do not need a
hill.** Calibrate by running one rep and marking where 10 s lands.

Calibration rule: **rep 1 all-out, record the time, every later rep within +5 %.** This gives an
objective anchor that needs no sensor (see the short-effort section of SKILL.md for why HR cannot
serve this role).

Feel check: finishing gassed and unable to speak = too steep/long (it became an aerobic session);
immediately able to speak but the legs feel heavy and force-production is obvious = correct.

**If stairs are short** (total vertical gain ÷ reps below ~8 m), the athlete tops out before reaching a
stable high-force phase. Fix by finding a longer continuous climb, not by adding reps.

## Plyometrics and strength without a gym

Evidence: body-weight plyometrics (hops, bounds, depth jumps) 2–3×/week for 6–12 weeks improves
running economy by roughly **3–5 %** at submaximal speeds — via tendon stiffness and rate of force
development, **with no change in VO2max**. Heavy resistance produces a *larger* effect but needs load;
when that is unavailable the substitute ladder is:

1. **Single-leg loaded work** — split squats / step-ups / single-leg RDL with a loaded backpack
2. **Plyometrics** — pogo hops, box/step jumps, bounding, single-leg hops, skipping rope
3. **Hill/stair sprints** — the closest no-load substitute for heavy lifting
4. **Mini-bands** — activation only (glute medius, ankle dorsiflexion). **Too short and too light for
   resisted sprinting; do not prescribe them for that.** A band for resisted sprints needs a fixed
   anchor and ~10–20 kg of tension; without a partner or anchor, stairs are the better answer.

Most effective protocol shape: 2–4 lower-body movements at 40–70 %% 1RM, **not to failure**, plus
plyometrics, 2–3×/week, 8–12 weeks.

## Things *not* to add

- **Nordic hamstring curls** when knee/ankle fixation is unavailable and the athlete has no injury
  history. Their evidence base is *injury prevention* (one 409-player RCT: 51 %% reduction in ACL
  injury). With no such gap, the movement only adds execution friction. Substitute single-leg RDL for
  the posterior chain. (If the injury history justifies it: a towel threaded under a closed door
  anchors the ankles.)
- **Cross-training volume.** Cycling time is not running volume — it supplies cardiovascular stimulus
  but not the sport-specific musculoskeletal, tendon-stiffness or economy adaptations. Only running
  kilometres buy those.
- **Extra easy kilometres as an end in themselves.** Volume exists to raise the ceiling on how much
  threshold work the athlete can absorb. It is the means, not the goal.

## Race-pace / special block

Sustained work at or just above goal race pace, recovered at an aerobic intensity:

- 5×1000 m at 100–103 %% race pace, 2:30 jog
- 3×2000 m at 98–99 %%, 3–4 min jog
- 6×1000 m at 100–103 %%, 2–3 min jog

The point is to extend time at race speed while keeping each rep aerobic enough to preserve quality.
**Scale the volume, not the intensity** — the reps are already at or above CS, so adding more of them
is what changes the stimulus character.
