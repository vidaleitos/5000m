# Standardized Time-Trial Protocol

When to use: the athlete has no race on the calendar, but the block needs a measurement point.
Also when a race exists but you need reproducible numbers between races.

**The protocol matters more than the result.** An unstandardized test is not a data point — it cannot
be compared to the next one, and it cannot be used to recompute critical speed / D′.

## Rules

1. **Identical every time.** Same venue type, same time of day, same warm-up, same pacing rule.
2. **Deload into it.** ~25 % volume reduction across the 2 days before. Last quality session at least
   4 days out.
3. **Day before:** easy 6–8 km + 4 × 100 m strides.
4. **Test day warm-up:** 3 km easy → dynamic mobility → 4 × 60 m strides → 3–4 min rest → start.
5. **Conditions:** check the dew point (see `endurance-training-analysis`). Target a dew point below
   ~18 °C. Record the actual temperature and dew point with the result — a time trial without
   conditions attached is only half a data point.
6. **Venue:** a 400 m track is best (readable per-lap splits). Otherwise a flat, straight, low-traffic
   stretch.
7. **Record:** per-km (or per-400 m) splits, total time, avg HR, max HR, cadence, stride length,
   ground contact time, temperature and dew point. Without the splits the effort cannot be diagnosed.

## Pacing rule (protects the data point)

The most common failure is going out too hard and blowing up, which produces a number that measures
neither fitness nor pacing.

- First 1 km **3–4 s/km slower than target** — deliberately, and it should feel too easy.
- kms 2–4 steady.
- Last 400 m flat out.
- Per-lap check is *"is this lap more than ~4 s slower than the previous one?"* — not cumulative time.

**Set the target from current data, not from the athlete's goal.** Derive it from their recent
efficiency at a reference HR, and say so. Frame the target as a range and label it as a sanity check,
not an objective. Then state the actual objective in one line: *the requirement is a clean data point,
not a fast one.*

## Executing a maximal effort alone (no pacer, no competitors)

- Set the watch to **auto-lap every 400 m**.
- Use the watch's **virtual partner / pacing feature** at the target pace. The watch is the rabbit.
- Glance at the watch only on the straightaways, never through the turns.
- Write the splits down immediately after finishing — not after getting home.

## Honest limits — state these to the athlete

A solo time trial yields a valid model data point. It does **not** provide competition pressure,
pack tactics, or the experience of hurting with others. Say this once, plainly, when the athlete
confirms they will not race. Repeat it every block and it becomes nagging; say it once and design
around it.

## After the test

1. Recompute critical speed / D′ if you have two reliable points at different distances.
2. Recompute efficiency at the reference HR and compare with the **dew-point-matched** prior value.
3. Rewrite the pace table from the new parameters.
4. Update the athlete model file, including which prior judgement was overturned.
