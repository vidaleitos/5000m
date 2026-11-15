---
name: endurance-training-analysis
description: Use when analyzing or prescribing endurance training.
---

# Endurance Training Analysis

How to compare a runner's training and performance **across time periods** without fooling yourself.
The whole point of this skill: the most common analysis error is not a wrong formula, it is an
**uncontrolled confound**. Heat is the biggest one.

## Two hard rules (violate either and the conclusion is void)

### Rule 1 — Only compare like sessions
For any pace-vs-heart-rate analysis, keep **steady sessions only**:

```
km >= 6–7  and  (maxHR - avgHR) <= 28
```

An interval session's "average pace" is dragged slow by warm-up, cooldowns and recovery jogs, so
pairing it with `avgHR` is meaningless — and it biases in a nasty direction: the session *looks*
slow at a moderate HR, which reads as "fitness collapsed" when nothing happened.
Real example: an 8x400 m session whose whole-session average was 5:43/km at avgHR 155 — it was
correctly a hard session (reps at 3:24/km, HR to 193). Unfiltered, it corrupted a whole month.

**It is not only the session average — per-rep HR is not comparable to steady-state HR either.**
HR approaches plateau with a time constant of roughly 30–60 s and needs **2–4 min** to get there.
A 6-minute rep starting from a partial recovery never reaches plateau: its trace is the first six
minutes of a rising curve. Worked case, same athlete, five days apart, similar climate:

```
continuous 30:10 @ 4:12.4   ->  HR plateau 181
5 x 6:00    @ 4:09.6        ->  per-rep peak 178-179; first km of each rep only 164-170
```

Read naively that says "faster pace at *lower* HR" — an improvement. It is arithmetic across two
different physiological states. The interval number is low **because of the structure**, not because
the effort was easier.

So HR is comparable **only within the same structure**. Across structures, compare only:

1. **Ground-contact time at matched pace** — mechanical, structure-independent, and the field that
   actually survives the change of session type
2. **Rep-to-rep dispersion** — a last rep that is the fastest is a pacing story, not a fitness story
3. **Movement quality at the end of the set**

Pace is also only comparable within a structure. Report the raw numbers ("4:09.6 for 30:00 of work")
and explicitly refuse the cross-structure comparison rather than making it and hedging.

#### What *can* cross structures: the work-to-recovery ratio

If HR cannot cross structures and pace cannot either, the thing that does is the session's
**work : recovery ratio**. Two sessions inside the same nominal pace band are not the same session:

```
5 x 6:00   @ 4:09.6   rec 2:02   ->  360 s work / 122 s recovery  =  2.95
4 x 2000 m @ 4:07.0   rec 2:01   ->  494 s work / 121 s recovery  =  4.08
```

Nearly identical nominal pace and nearly identical recovery *duration* — but the second gives every
rep ~39 % more accumulated work before the same rest, so each rep starts with lactate higher and HR
less recovered. It converges toward continuous running. **Check the ratio before calling one session
harder than the other on pace alone** — and report it alongside the pace when the athlete will want to
compare sessions weeks later.

#### The recovery interval is a training variable, not dead time

Slowing the recovery makes the next rep start "cleaner", buying pace at the cost of total time near
threshold. So the athlete gets two legitimate ways to run the comparison, and should pick one
deliberately:

- **Fix the recovery** → the work pace becomes a directly comparable score and repeated sessions are
  interchangeable; in-session adjustment is given up.
- **Let the recovery float** → the work pace is only half a result; **"how much recovery was needed to
  hold this pace" becomes the metric.** Closer to a real adaptation signal, and it preserves the
  athlete's own in-session judgement.

Do not silently mix them. And when the athlete says *"I slowed the recovery on purpose"*, that is a
session-management decision to respect — **not a fatigue signal to interpret.** The tempting read
("the recoveries got progressively slower, so there is accumulating fatigue") is arithmetically the
same and causally different. Ask *why*: breathing not down / leg feel / protecting the later reps.
The three answers mean different things, and the third is deliberate intra-session periodisation —
a more advanced behaviour than the prescription asked for.

**Corollary — this is also why a flat HR–pace curve shows up.** If a threshold effort plateaus at 181
while race-pace reps peak at 179, the tempting conclusion is "the athlete's HR cannot separate
threshold from race pace". Usually the gap is this structural artifact first; only claim a genuinely
compressed HR response after matching the session structures.

### Rule 2 — Match the climate before comparing eras
Dew point across seasons can differ by **28 °C**, which is worth **20–30 s/km**. That is larger than
most real training gains. Compare unmatched and you will "discover" progress that is weather.

**A bad instrument is not a reason to drop the variable — it is a reason to get a better instrument.**
This is the key lesson. Body-worn temperature sensors are contaminated by skin heat; a watch can
report 23 °C for a run that was actually 0 °C. The wrong fix is to declare temperature an
unmeasurable confound and move on. The right fix is to fetch real meteorological data.

## Heat / climate matching method

1. Get the session list with **local** timestamps and coordinates (see units traps below).
2. Fetch real weather at the training hour: `scripts/fetch_weather.py` (Open-Meteo historical
   reanalysis, free, no key). It matches each session to the nearest hour and writes
   `sessions_weather.csv` with real temp / RH / dew point **and** the watch's own temperature field,
   so you can demonstrate the watch value is unusable.
3. Run `scripts/heat_analysis.py` for three tables: monthly real heat load, dew-point-matched
   comparison, and the steady-session HR-band check.
4. **Primary judgement = dew-point-matched AND HR-band-matched direct comparison.** No model, no
   assumption. Only fall back to a regression when the matched sample is too thin, and then report
   `n` and `R²` and say the fit is unstable.

### Fetching the weather — implementation notes that cost time

Open-Meteo historical reanalysis (`archive-api.open-meteo.com/v1/archive`) is free and needs no key,
but three things bite:

- **`end_date` in the future returns HTTP 400.** Cap it at yesterday before building the URL.
- **One large request over many months fails.** Fetch in chunks of roughly one to two months
  (~55 days is a safe size) and cache every response to a JSON file on disk. **Two different failure
  shapes, and the quiet one is worse:** a timeout is obvious, but a long request can also return
  **HTTP 200 with `null` in every field** for part of the range. A chunk that is too long therefore
  poisons the cache with "no data" instead of raising — and you find out months later, when sessions
  from those weeks have no weather and a monthly average silently reads `0.0` instead of blank.
  Chunk it, and treat "the API answered" as no evidence at all about whether the values are there.
- **The forecast endpoint and the archive endpoint disagree about coverage.** `past_days=92` on the
  forecast endpoint carried `null` holes in the *middle* of its own window (a run of weeks ~3 months
  back) while the archive endpoint had the same days fine. Use forecast for freshness, archive for
  anything older, and merge with a **never-overwrite-good-with-null** rule — not a plain
  last-writer-wins assignment, which is what turns one good merge order into permanent data loss.
- **Normalise cache keys before you trust the cache.** API timestamps come back as
  `2026-07-20T06:00`; lookups get written naturally as `2026-07-20 06:00`. A
  `strptime(k, "%Y-%m-%d %H:%M")` sitting inside a bare `except: pass` loader will swallow the mismatch,
  load **zero** usable rows, and look exactly like "that month has no weather data". A silent except
  around a cache load is a data-loss bug waiting to be blamed on the weather.
- **Verify a cache by asking it for a date you already know the answer to.** Any one known session's
  temperature/dew point is enough to prove the loader actually populated anything.
- **Re-fetch after the endpoint has had time to fill in.** A range that returned `null` last week is
  often complete this week, so the backfill is cheap to retry — just make the merge non-destructive
  (above) so retrying can only add.
- **TLS handshakes are intermittently flaky on this host.** Wrap each fetch in ~4 retries with a short
  sleep. Retrying works; do not conclude the endpoint is unreachable.
- Also request `temperature_2m, relative_humidity_2m, dew_point_2m` **per hour** and index by the
  session's local hour (rounded down). Fetching a whole period and matching afterwards is far simpler
  than trying to request exactly the right hour.

Useful side effect: also carry the watch's own temperature field into the output CSV. Printing the two
side by side (watch says 23 °C, reanalysis says 0.6 °C) is the fastest way to settle any future
argument about whether the sensor can be trusted — and to stop a later session re-introducing the
uncontrolled confound.

Fetch by **location**, not by athlete: if the athlete moved cities, split the location table by date
range and fetch each location separately.

### Dew point thresholds (literature)

| Dew point | Meaning |
|---|---|
| `< 12 °C` | ideal — pace targets are valid |
| `12–18 °C` | hard sessions start to suffer; add ~3–5 s/km tolerance |
| `18–21 °C` | run quality sessions by feel/HR; pace is a weak guide |
| `> 21 °C` | move or cancel hard sessions; **do not chase paces** |

### Pace-correction formulas — use with care

Two published rules exist and **they disagree**, so never present a corrected pace as a measurement:

- Dew-point rule: `adjusted = base + (DP°F − 60) × 0.025 min/mile`
- Combined rule: when `T + DP` (both °F) exceeds 130, the penalty grows ~1 % per 10 points above

Sign convention (this is easy to get backwards — it was gotten backwards once):

```
# pace is SLOWER at higher dew point
# P = P0 + k*(D - Dref)   with k > 0
# so normalising an observed pace at dew point D to reference Dref:
def norm_pace(p_min_per_km, dp_c, ref_c=5.0, k=0.41/60):
    return p_min_per_km + k*(ref_c - dp_c)   # hot run -> adjusts FASTER
```

Sanity check before trusting it: a July run at `k=0.41` should normalise only ~7 s/km, while the
observed same-HR deficit across seasons is often 20–30 s/km. If the correction cannot explain the
gap, the remainder is real — or your `k` is too small for humidity-dominated heat.

## Cross-period comparison recipe

Produce, in this order:

1. **Real climate table by month** — temp, RH, dew point at the training hour. Establishes which
   months are even comparable.
2. **Monthly efficiency series** — for each month, fit or band-match pace at a fixed reference HR
   (e.g. `@HR150`). Plot this next to the dew-point series. Where the two lines move together you
   have heat; where they diverge you have a real fitness change.
3. **Dew-point-matched pairs** — e.g. all months whose mean dew point falls in 14–17 °C, compared
   directly. This is the table you actually draw conclusions from.
4. **Year-on-year matched pairs** — same dew-point band, same HR band, 12 months apart. Usually the
   single most honest statement of real progress — but it is fragile in a specific way: the
   HR-band method's own scatter is ~±10 s/km, so **when the sign flips from band to band the finding
   is "no resolvable change", not "pick the band that agrees with my prior"**. The hard line in this
   comparison is ground-contact time on steady laps, normalised to a common pace — it does not depend
   on the heart-rate sensor at all. Build it, state the resolution limit next to the conclusion, and
   reconcile both periods' totals against the athlete's own log before analysing anything.
   → full recipe, worked numbers and the code in **`references/period-comparison.md`**
5. Attribute the residual. State explicitly what heat does **not** explain.

### Cheap daily recovery check: same pace, same sensor, two different days

The most reliable read on "did yesterday's session leave a mark" is a matched-pace comparison between
consecutive sessions on the same sensor:

```
long run, final 6 km       4:55/km -> HR 159
next day, mid-session      4:55/km -> HR 154
-> essentially identical after pace correction -> the session was absorbed
```

Four things keep it honest:

- **Rule out the climate confound FIRST.** Before attributing a matched-pace HR rise to fatigue, check
  both days' dew point. Worked case: easy run four days earlier at dew 19.6 °C → 5:21/km @ avgHR 133;
  today at dew 18.9 °C → **5:29/km @ avgHR 140**. *Slower pace, same climate, +13 bpm* — so heat
  cannot explain it. Had today's dew point been the higher one, the identical arithmetic would have
  been worth nothing. **Do not skip this step; it is the step that makes the read admissible.**
- **Control for elapsed duration.** HR drifts ~5–10 bpm over an hour, so a *late-run* segment and a
  *mid-run* segment are not directly comparable. Prefer comparing segments at a similar elapsed time,
  or compare the drift slopes rather than single points.
- **Corroborate with a mechanical metric, in the same direction.** In the case above, ground-contact
  time came back 247.8 ms where the athlete's own pace curve predicts 245–246 ms — only ~2 ms high, but
  pointing the same way as the HR. Supportive, not decisive; never let it carry the conclusion alone.
- **One matched pair is not a verdict** — it says "no obvious residual", not "recovered".

**The accumulation case — the same read across a loaded microcycle, not just day-to-day.** The +13 bpm
above appeared on the fourth consecutive running day, after a threshold session, a long run and a
medium-long run (27 km in the last two days). That is a **normal response to productive training, not a
problem** — and the correct use of it is a **scheduling decision**, not a reason to cut the block. What
it licenses is moving a hard session off the next day and onto the best-condition day of the coming
week (see the forecast-placement section in `training-block-design`), if a better day exists.

**Direction of the error matters here more than in most reads.** Misreading accumulation as *fitness
loss* shrinks the block; misreading it as *nothing* stacks a quality session onto a body that is
already carrying one. The confound-first rule is what keeps those two apart.

This beats both "how do you feel" and a single-day HRV reading, and it needs no extra equipment.

### Also do not trust
- **Race-prediction / VO2max widgets on consumer watches.** They can be systematically optimistic
  (60–70 s over 5 km in the case studied) — and they drift when no hard efforts are logged, which
  manufactures a fake "decline". Use them as a **trend indicator only**, never as an absolute.
- **Session names change when the training system changes.** A rename is evidence that the
  methodology changed — find out why before interpreting the load.

## Prescribing a block — intents, not numbers

The analysis above is worthless if the prescription that follows is a table of targets. Three
corrections were needed on this, and all three are the same error in different clothes: a
**description** of how training usually unfolds, turned into a **target** and handed over as
something to hit.

| What was given | What came back |
|---|---|
| A "48 h / 72 h between sessions" table | *"Don't use intervals to rigidly limit yourself when there are no concrete numbers"* |
| "Target 82–88 km/week", "don't go above 100" | *"Volume is an outcome — even 100 in a week is an outcome"* |
| Total volume and stimulus volume used interchangeably | *"Warm-up and cool-down — do those count as volume? They shouldn't, right?"* |

### The rule

**Specify the stimuli that must occur. Never specify kilometres, hour-gaps, or ceilings.**
Every number is written as an *expected outcome*, labelled as such. **No number is a target to hit.**

The weekly intent set:

1. one **threshold** stimulus (30–45 min of work)
2. one **race-pace** stimulus (4–6 km of work)
3. one **long run**
4. **neuromuscular** work 2–3× (strides / hill or stair sprints)
5. easy aerobic running fills the rest — **whatever it sums to, it sums to**

Volume is the sum of those five. Whether it lands at 65 or 100 this month depends on how those five
look and how the athlete absorbs them — **not the other way around.**

### Total volume and stimulus volume are two numbers — always separate

| | **Total** (incl. warm-up/cool-down) | **Stimulus** (main-session work) |
|---|---|---|
| Answers | recovery demand, aerobic base | did the adaptation happen |
| Counts warm-up/cool-down | **yes** | **no** |

- "72 km this week" = total (comparable to their history, because the historical numbers were counted
  the same way)
- "30 min threshold / 4 km at race pace" = **work distance**
- **Strides and stair/hill sprints count toward neither** — they are neuromuscular stimuli, logged separately
- Never pad total volume by stretching the warm-up. That is manufacturing a number, not training.
- Magnitude of the error: a session reported as 13.99 km contained **7.16 km** of actual stimulus.

### When something has to be cut, the order matters more than the amount

Cutting a kilometre from the long run and a kilometre from an aerobic run are not the same subtraction.
Rank by what the session **uniquely** carries:

1. **Cut last — the session carrying the athlete's only measured deficit.** Here the long run, because
   durability is the diagnosed limiter and it is the only session that attacks it.
2. **Cut next — quality sessions**, which have a minimum effective dose below which they stop being that
   stimulus at all.
3. **Cut first — filler aerobic running**: cheap, repeatable, replaceable next week.

Worked case: the athlete balanced a planned 80 km week by **dropping a Friday aerobic run** and holding
Saturday at 18 km. Volume reconciled; **stimulus did not** — and the athlete had made the swap for a
perfectly reasonable reason (hitting the weekly number). The correction is not "train more", it is
"swap the same kilometres from the cheap session to the expensive one": long run 20 km, recovering day
10 km, total unchanged.

**Say it as a rule the athlete can reuse at the next decision**, not as a correction to this week:
*"equal volume is not equal stimulus — the long run is the last thing you cut."*

### When is it too much? Signals, not a number

- first rep of a quality session goes flat, or drops >6 s/km across the set
- the warm-up never comes alive
- morning resting HR +5 for two consecutive days
- a single-point pain (not muscular soreness)

Any of these → reduce. None of them → **no ceiling.**
And the only test of a volume ramp: **did the quality sessions get faster at the same perceived cost?**

### Every default comes from the athlete's own history

Ignoring this meant proposing generic "what an 18:30 5K runner should do" parameters to an athlete who
had already run **106.6 km in a week, 87.5 km/week for a month, and 80 km/week for two months — all
injury-free.** Check their history first; use the template only to correct it.

It applies to session *type*, not just dose. Before prescribing intervals for a threshold session,
check what their best block actually consisted of: in the case studied it was almost entirely
**continuous** running, so continuous became the default and intervals were demoted to a dose
controller. Same for recovery and sleep — do not keep offering "you need to sleep more" as a
constraint once the data has ruled it out.

**But "the data" means measured data — not the athlete's report.** A standing note read *"sleep
5.1–5.7 h, not a constraint"*, built entirely on *"I wake up naturally and I'm not tired."* When a
wearable export was finally available, the same nights read:

| night | score | duration | REM |
|---|---|---|---|
| 1 | 44 | 4.87 h | **0** |
| 2 | 41 | 4.45 h | **0** |
| 3 | 40 | 4.18 h | 0.32 |
| 4 | 69 | 5.93 h | — |
| 5 | 44 | 5.52 h | **0** |

Median ~5.2 h and REM 0–0.58 h against a normal ~1.5 h — chronic restriction, not a short-sleeper
trait. **Absence of daytime sleepiness is not evidence of adequate sleep.** This caps how fast volume
may rise, because adaptation happens in sleep. Treat self-report as a placeholder: usable until
measured, never a finding.

Three operational consequences:

1. **Short time-in-bed is usually the cause, not insomnia.** 4.18 h asleep + 1.82 h awake ≈ 6 h in
   bed, so 7 h asleep needs ~8 h in bed. That is a concrete instruction, not "sleep more".
2. **Keep the autonomic marker separate from sleep architecture.** The same week's HRV was
   baseline-balanced. The right summary is *"autonomic load is being handled; recovery depth is
   not"* — not "recovery is broken". Report both, and let sleep set the ceiling on the ramp.
3. **When measured recovery contradicts an assumed one, the assumption loses — and the standing note
   must be retired in writing** (see Reporting). A note that accepted the self-report silently keeps
   licensing load the data says cannot be absorbed.

**But measured recovery is still not a veto.** A Garmin sleep score of 44 on the night before a
max-velocity test was used to **cancel the test**; it was run the next day anyway and produced the best
short-effort data of the block. Two separate errors were in that loop: (a) the score and the sleep
staging are unreliable fields, and (b) **a recovery metric may move a session; it may not delete one.**

| what a recovery metric may do | what it may not do |
|---|---|
| influence *placement* (which day) | cancel a session outright |
| influence *dose* (how much) | override the session's own output as evidence |
| raise a question to ask the athlete | become the finding |

The arbiter of whether a session was affordable is **the session's output**, not the night before it.
State the rule to the athlete once — *"wearable data is a weak prior; actual performance is the judge"* —
because otherwise every later analysis has to re-litigate it, and the athlete will be right every time.

### Answer execution questions with criteria, not slogans

When the athlete asks something operational (what counts as a warm-up, is a cool-down required, pace
or heart rate, which day does strength go), give **purpose → dose → the check that tells them it was
enough**. "Listen to your body" comes straight back as another question.

See `references/prescribing-a-block.md`.

## Metrics that look like intensity but are not

### Peak training HR reflects the training, not the heart

A rising peak HR across months is usually read as "cardiac fitness improved". It is not. Peak HR in
training is bounded by **whether the programme contains short efforts above critical speed** — a block
of nothing but continuous running tops out near threshold HR however fit the athlete becomes.

Worked case: four months of continuous-only running peaked at **179–184** bpm in every hard session;
months containing 400–1000 m reps reached **189–195**. Same athlete, same heart. The tell is that the
"peak HR rise" appeared in exactly the month the rep distances got shorter.

### HR and local muscle acidosis decouple — and the athlete's old yardstick dies with them

Heart rate tracks *cardiovascular output demand* (central drive, heat, dehydration, arousal).
"Legs burning" tracks *local muscle metabolic state* (H⁺/Pi accumulation, fibre recruitment).
They correlate in most training, which is why athletes learn to use soreness as an intensity gauge —
and why the gauge silently breaks when the two decouple.

Observed: at similar paces and the same HR band the athlete used to report burning legs and being
unable to speak; now reports the same or higher HR as controllable and conversational.

1. **Fibre recruitment differs by session type.** Short fast reps recruit type II fibres → fast
   glycolysis → H⁺ → burn. Sustained sub-threshold running is oxidative and stays near lactate
   balance. *The same HR means different things in a 400 m rep and in minute 8 of a threshold run.*
2. **Local adaptation** — capillary and mitochondrial density, MCT transporters: same power, less H⁺.
3. **Cardiac adaptation shifts the HR↔output curve**, so a given HR now corresponds to a larger
   absolute output and a smaller fraction of capacity.
4. **The muscular limiter can uncouple from the ceiling.** If the legs used to fail first, the heart
   never expressed its true maximum, so peak HR was truncated. Removing the muscular limiter raises
   achievable peak HR *and* lowers perceived effort.

**Say the consequence out loud:** the athlete's "soreness = hard enough" instinct is now wrong, and
keeping it will make them over-run threshold sessions (failure signature: a fast third rep and a
collapsed fourth). Replace it explicitly, per session type:

| Session | Control variable | Never use |
|---|---|---|
| Easy | pace | leg feel, HR |
| Threshold | breathing (3–5 word sentences, not conversational) + rep-to-rep consistency | leg soreness, a single HR reading |
| Short reps (400–1000 m) | target pace + quality of the last rep | HR |
| Strides / hills / stairs | rep times + ground-contact feel | HR (any use) |

**Keep the warning symmetric:** legs *should* stay fresh in threshold work, and legs *should* burn in
short maximal reps. If short reps stop producing any local burn, that side of the stimulus has been
dropped — keep strides, hills and a little rep work in the programme.

### Ground-contact time proves the limb *can* do it — never that it can *sustain* it

A retracted inference, and a subtle one. Reading GCT of **179–186 ms** during 3:01–3:13/km strides and
short reps, the conclusion drawn was *"mechanically he is already a 16-minute 5K runner, so the limiter
must be aerobic."*

**That does not follow.** GCT is an *instantaneous* mechanical measurement. It says the leg can recycle
fast enough **for one contact** at that speed. It says nothing about the metabolic cost of **holding**
that speed — a different system, and the one that decides a 5000 m.

| What GCT at a fast pace supports | What it does not |
|---|---|
| the limb can produce contacts at that rate | that the athlete can sustain the output |
| mechanics are not *structurally* blocking that speed | that aerobic supply is the only remaining limit |

**Corollary — say "the mechanics are not blocking it", not "the limiter is aerobic".** They are not the
same claim, and only the first one is supported. When a judgement like this is retracted, retract it in
writing (see Reporting).

### A training segment is not a performance — do not extrapolate across the two

Riegel-style extrapolation (`t2 = t1 × (d2/d1)^1.06`) needs **maximal** inputs. Mid-session splits are
not maximal, so mixing them with real performances manufactures a fake profile.

Worked case, one athlete:

| Mark | Nature | Riegel → 5 K | vs actual 18:33.7 |
|---|---|---|---|
| 1 km 3:26.4 | **training segment** | 18:56.6 | 23 s slower than the PB |
| 1 mile 5:36.8 | **training segment** | 18:40.0 | 6 s slower |
| 3 km 10:37.0 | **performance** | 18:14.7 | 19 s faster |

Read naively, the two segments say "his 5 K is better than his speed" and the performance says the
opposite — so the table *looks* like evidence of a speed deficit. **It is mostly evidence that two of the
three numbers were not maximal efforts.** Rules:

1. **Label every mark by nature before using it in arithmetic** — race / time trial / training segment.
2. **Only compare like with like.** A performance against a performance; a segment against another
   segment from comparable conditions.
3. **When the marks disagree, the disagreement is the finding** — it usually means the inputs differ in
   effort, not that the athlete has an imbalance.
4. **A mark from a different period is confounded too** — a June 3 km says nothing precise about an April
   5 km, because the athlete was fitter in June.

### Capability and level are two different objects — never answer one with the other

The athlete's objection, and it invalidates a whole class of answer: *"you're just listing historical
bests — 运动表现能力 and 运动水平 are not the same thing."*

| | answers | contaminated by |
|---|---|---|
| **level** (PB / result) | what you produced on one particular day | the date, the weather, the tactics, whether it was maximal |
| **capability** | what you can express **now** | current state only |

So "what am I capable of, from 50 m to the marathon" is answered in **two layers**, never one:

1. **Parameters** — built only from current measurements, each tagged with a confidence level: peak
   velocity; reserve against **two** references (peak *and* the 200 m average — they answer different
   questions, see the pull-back section); critical speed; LT1; LT2; vVO2max; economy proxies (GCT and
   vertical ratio at matched pace); D′; durability.
2. **Expression** — per distance: what those parameters project **and which one limits that distance**.
   Label every projection as a projection, and keep "unknown" as an allowed answer (D′, durability and
   anything past 10 km usually are).

**Never put a PB in layer 1.** Two ways a recorded mark corrupts the profile, in opposite directions:

- a **training segment** (a mid-session 1 km, an unraced mile) is a **lower bound** → understates capability
- an **unraced long-distance mark** is not comparable to a Riegel projection from a 5 K → it reads as a
  durability deficit when it may only be evidence that nobody raced it

This framing also produces the honest headline the athlete is actually asking for: *"your parameters
point at a number faster than your PB — the gap is expression, not capability."* That sentence is worth
more than any table, because it names the work that remains (put the dose in) instead of implying a
physiological defect.

### "Speed is my weakness" — measure it instead of arguing about it

When the athlete asserts a limiter the data cannot resolve, the answer is **neither to agree nor to
out-argue**. It is to say *why* it cannot be resolved and to propose the cheapest measurement.

Here every fast number on file was either a submaximal training segment or taken in a fatigued state
(the fastest 200 m was the **second** rep of a set, after a race-pace session had already been run), so
maximum velocity had never actually been measured. Apparent speed reserve came out low (1.08–1.30 × 5 K
pace) — but reserve computed from non-maximal efforts is not a measurement.

The cheap resolution:

```
2-3 x 60 m all-out, 3-4 min full walking recovery, + 1 x 150 m all-out
```

Twenty minutes, almost no fatigue cost, and it separates **absolute speed** from **speed endurance** —
which have different prescriptions. Say which number would change the conclusion *before* the test, so
the result cannot be rationalised afterwards.

**Do not quote a population "normal reserve" band as a criterion.** A figure like 1.40–1.60 × is a
literature-flavoured guess unless you can cite it for this event and level; presenting it as a threshold
invites the athlete to treat a soft number as a measurement. **If a later session output quotes
1.40–1.60 × as if it were a criterion, that is this error happening again.**

#### Peak velocity and sustained velocity are two measurements — the gap between them is the finding

The test above resolves at one distance, and the distance bounds what it can report. Same session, two
reps, second one mechanically better on every running-dynamics field:

```
150 m rep   GCT 156 ms   stride 179.5 cm   vO 6.14 cm   vert ratio 3.42 %   peak 7.371 m/s
220 m rep   GCT 179 ms   stride 174.1 cm   vO 7.43 cm   vert ratio 4.66 %   peak 7.493 m/s
```

1. **A short rep bounds the reading; it does not measure maximum velocity.** From a standing start the
   first ~40 m is acceleration and the last ~15 m is deceleration, so the peak sits below the ceiling.
   The 220 m had the *better* peak **because it had the runway**, despite worse mechanics. Give a
   max-velocity rep **≥ 200 m**, or report the answer as "≥ this value".
2. **Report peak and sustained separately, and name the gap.** Reserve against peak was **1.69 ×** 5 K
   pace; against the same athlete's 200 m average it was **1.35 ×**. That 0.34 × is the **pull-back**:
   a high top gear that cannot be held. It is the *same mechanism* as a fading long run — so "fast
   peak" and "fades late" are not contradictory findings, they are one finding measured twice.
3. **Mechanics can improve while peak speed falls.** The better-mechanics rep could not beat the other
   one's peak. Do not read better GCT / stride / vertical ratio as *more speed* — read it as **more
   efficient production of the speed actually reached.**

And keep the two reserves apart in the model file. Collapsing them into one "speed reserve" number is
how a strength (top gear) and a weakness (pull-back) get averaged into a bland and useless middle.

## A failed time trial is usually a pacing error — read HR against pace to tell them apart

When an athlete aborts a TT, the temptation is to file it as "could not hold it" and downgrade the
fitness estimate. **Check the shape of the failure first.** Two causes look identical in the summary
line and mean opposite things:

```
aborted 4 km TT, 1.42 km total, 5:03, avgHR 186 / maxHR 191

400 m   81.8 s   3:24.5/km   HR 177 -> 187
400 m   85.3 s   3:33.2/km   HR 188 -> 191
400 m   87.8 s   3:39.5/km   HR 189 -> 191
220 m   48.2 s   3:38.9/km   HR 190 -> 191
```

- **HR still climbing while pace decays = started above the sustainable intensity.** The system was
  never at steady state; it was above it from the first 400 m. This is a **pacing error**, and it
  measures nothing about the ceiling.
- **HR pinned from the start = a genuine wall at that distance.** That is a fitness reading.

So: **if HR is rising as pace falls, the trial is inconclusive, not negative.** Say exactly that —
and do not let the aborted number into the model file as evidence about current capability. It is
very easy to write "could not hold 3:40 for 4 km" out of a session where 3:40 was never attempted.

### Set the opening pace with arithmetic, not with feel

The athlete opened at **3:24.5/km** — faster than their own 3 km PB pace (3:32.4) and essentially
their 1 km PB pace (3:26.4). A 4 km cannot be run at 1 km pace, so the outcome was decided inside the
first lap. Anchor the target before the attempt:

```
5 K PB 18:33.7   ->  Riegel to 4 km:  1113.7 * (4/5)**1.06  =  14:39.1   ->  3:39.8/km
opening 400 m actually run                                                  3:24.5/km
                                                                            --------
                                                                            +15.3 s/km
```

**The durable point is that the athlete's untutored opening pace is their 1 km pace.** That is a real
pacing-calibration gap, not carelessness, and it is fixable with one stated ceiling: *first 800 m no
faster than 3:40*. Give the ceiling, not a target pace — the athlete should stay free to negative-split.

#### …but a ceiling becomes an anchor. Continuous efforts need a band, not a wall

The ceiling rule above is right for **rep sessions**, where the failure mode is opening too fast and
collapsing the set. It is **wrong for a continuous maximal effort**, where the failure mode is the
opposite — and it produced exactly that failure on the next attempt.

Prescription given: *"first 5 min no faster than 4:15"* for a 30-min test. What the athlete did:

```
400 m laps  4:17.0  4:10.2  4:09.7  4:07.6  4:06.2  4:05.5 ... 3:52.4  3:53.8  3:54.5
avg 4:00.9 for 30:02    avgHR 172 / maxHR 183    LTHR ~181    finished with reserve
```

He treated **4:15 as the anchor** and built from it, so the ceiling became the floor and the
"measurement" produced a **lower bound instead of a measurement**. His words: *"I didn't dare go faster
in case I blew up."* That is the instruction's fault, not a discipline failure — say so plainly.

| effort type | failure mode | give |
|---|---|---|
| reps / intervals | opens too fast, set collapses | a **ceiling** |
| **continuous maximal (TT, threshold test)** | **opens too slow, finishes with reserve** | **a band + a mid-point checkpoint** |

The checkpoint is what makes it self-correcting:

```
first 5 min   4:04–4:08        (a BAND, both ends stated)
minute 10     if it still feels "very easy, no pressure" -> add 5 s/km IMMEDIATELY
last 5 min    whatever is left; fading here means the start was too fast
```

**How to tell afterwards that it was under-paced** — any two of these is enough:

1. **Average HR well below LTHR** (172 vs 181 here). A truly maximal continuous effort averages ≈ LTHR.
2. **The last laps are the fastest** (3:53.8, 3:54.5 to finish).
3. **The athlete says there was something left.**

**A lower bound is not a measurement — do not feed it into the threshold conversion.** Applying
`LT2 ≈ 30-min pace + 5–10 s/km` to a *submaximal* 30-min average double-discounts: it treats a pace that
already had reserve as if it were the 30-min ceiling, so LT2 comes out too slow. Worked case: 4:00.9 + 9
→ 4:10, when the evidence pointed at ~4:03. **Check the reserve signs before converting, not after.**

### A speed-defined target licenses pace feedback — say so explicitly

This athlete deliberately does not look at HR during sessions, and that rule should hold. It does
**not** extend to a time trial's pace, because in a TT pace *is* the control variable and HR is the
post-hoc verification variable (see the control-variable table above). State the division out loud,
or the no-watch rule gets smuggled into the one session type where it destroys the measurement.

### And treat the aborted session's remainder as the real data

He went on to do 5x400 m and 2x200 m. Those are unaffected by the pacing failure, and they were the
best numbers of the day:

```
5 x 400 m   83.3 / 84.8 / 83.8 / 84.6 / 85.3 s   ->  2.0 s spread across five reps, rec 1:26
2 x 200 m   36.6 / 36.0 s   stride 167.3 / 169.7 cm   GCT 178.9 / 175.2 ms
```

A 2.0 s spread over five 400 m reps is race-grade consistency — report it as the session's finding,
not as a consolation. **And note that one session can retire an earlier instrument judgement:** the
same data carried **HR 191**, which overturned a standing "this athlete's HR does not go high" note.
Reaching 191 bpm at 1.4 km is the evidence that the ceiling was never the problem — the *training*
never went there. When a note like that is retired, retire it in writing (see Reporting).

## An athlete's zone label is a claim — verify it against measured anchors

When an athlete says *"I'll do two LT1 runs a week"*, **do not design around the label.** Work out what
their measured data says that zone is, then check the two agree.

Worked case. The athlete had been running **4:07–4:12/km with a heart-rate plateau of 181** — and 181 is
his measured **LTHR**. So the work he was calling threshold was **LT2 (MLSS), not LT1**. His LT1, read off
his own easy-run HR–pace curve, sits near **HR 162–168 ≈ 4:55–5:05/km**.

| | blood lactate | his HR | his pace | sustainable frequency |
|---|---|---|---|---|
| **LT1** (aerobic threshold) | ~2 mmol | **~162–168** | **~4:55–5:05** | **3–4×/week** |
| **LT2** (MLSS) | ~4 mmol | **181** (measured) | **4:11** (measured) | **1×/week is already a lot** |

Two reasons this is not pedantry:

1. **The recovery cost differs by a whole multiple.** Mistaking LT2 for LT1 turns a planned two-a-week
   aerobic stimulus into two threshold sessions — a much heavier week, arrived at without anyone
   deciding it.
2. **"Comfortably hard" slides.** For this athlete the felt boundary between LT1 and LT2 is around
   4:20/km, so "just run it by feel" lands on LT2 essentially always. **The base-phase failure mode is
   not too little training — it is calling threshold work aerobic work.**

An estimate read off their own curves is legitimate here, but label it as an estimate. Threshold pace
derived from feel is not a measured value, and a portable lactate meter is the one purchase that
converts LT1/LT2 from an inference into a measurement.

### Do not schedule LT1 as its own session when the athlete trains once a day

The athlete's correction, and it is right: **LT1 is a by-product of the easy and long runs.** Any
sustained running in the HR 145–165 band *is* LT1 work, so a separate "LT1 session" double-counts the
same stimulus and occupies a slot a genuinely different stimulus could use.

A dedicated LT1 session only earns its place in a **double-threshold (twice-a-day) model**, where the
easy volume is compressed and can no longer deliver it. Training once a day: put the *easy run* on the
LT1 band and the zone fills itself.

The consequence is bigger than it sounds — **moving 30 km of easy running from HR ≤ 135 up into HR
145–155 is a larger lever than adding any session, and it costs no extra time.** Which also means the
empty-zone histogram below is a statement about *easy runs*, not a case for a new session.

### Locate the empty zone by histogramming the athlete's own sessions

The same data answers a second question: **which intensity band does this athlete structurally
under-use?** Band their *easy and steady* sessions by average HR and count sessions per band. Repeat per
era if the training has changed shape. (This is a different use of HR banding from the cross-period
method above — there the bands compare two eras; here they locate a hole in one.)

Worked case — 78 easy sessions over four months, quality sessions excluded:

| HR band | sessions | mean pace | %HRmax |
|---|---|---|---|
| 110–119 | 4 | 6:19.4 | 58 % |
| 120–129 | 17 | 6:17.4 | 63 % |
| 130–139 | 14 | 5:44.3 | 68 % |
| 140–149 | 22 | 5:16.4 | 73 % |
| **150–159** | **15** | **5:03.6** | **78 %** |
| **160–169** | **6** | **4:55.7** | **84 %** |

**45 % of sessions sat at HR ≤ 139 (recovery), while the LT1 band he intended to train held 27 %.** The
zone he wanted to build was the thinnest part of his own distribution. That is a far more useful
statement than "add LT1 work", because it says where the work is missing *and* what he has been doing
instead.

Two consequences worth stating:

- **This is a volume-in-zone question, not a distance question.** 6–8 km at HR 125–139 and the same
  6–8 km at HR 158–165 cost the same clock time; the second buys materially more aerobic stimulus. When
  time is the binding constraint, intensity-within-zone is the lever.
- **Do not let the band table become a weekly quota.** It is a picture of a hole, not a prescription.
  The finding is *"this band is empty"*, not *"run 4 × 45 min at 158"*.
- **The watch's own load split is an independent corroboration.** Garmin's training-load balance
  reported `aerobicLow 1216` against `aerobicHigh 1933` — high-aerobic load dominating low-aerobic.
  Different mechanism, same diagnosis as the empty band: quality-heavy, easy-thin. **When two unrelated
  sources say the same thing, say so** — it moves the finding from "my analysis" to "the data".

### Check whether the profile is internally consistent before naming a weakness

Before writing "his limiter is X", test whether the pieces agree with each other:

```
measured threshold (LT2)   4:11/km
5K PB                      3:42.7/km     ->  28 s/km apart
```

A ~28 s/km threshold-to-5K gap is unremarkable at this level — **the two anchors imply the same fitness,
so there is no broken component to patch.** The limiter is the overall level, and the answer is broad
aerobic development rather than closing a specific gap.

**The failure this prevents:** declaring a limiter from a single gap, then designing a whole block
around closing it. When the anchors agree with each other, the honest conclusion is that nothing is
broken — a harder answer to give and a more useful one.

### Durability is intensity-specific — and a duration is not a measurement

"Durability" is not one number. It is a **function of intensity**, and the three layers answer
different questions:

| intensity | what a test there tells you | relevance to a 5 000 m |
|---|---|---|
| aerobic (easy / long-run pace) | can easy pace be held 90+ min without drift | indirect |
| LT1 | how fast the aerobic curve decays | moderate |
| **5 K pace** | **can target pace still be produced in the last fifth** | **decisive** |

**A 20 km long run is not a 5 K durability test.** It is an aerobic-capacity, structural-tolerance and
glycogen-management session. The 5 K-relevant durability question is a **17-minute** question, and the
cheapest existing test is one the athlete already runs — **a rep set whose last rep is the fastest:**

```
6 x 1000 m   last rep 3:40.2, fastest of the set  ->  5 K-intensity durability: PASSED
```

So before proposing a durability test, ask **which intensity layer the deficit would actually live in**.
Prescribing more long runs against a 5 K-layer problem puts volume in the wrong bucket.

### Decoupling needs constant pace — a progressive run cannot produce one

The efficiency-factor read (`speed ÷ HR`, first third vs last third) assumes both windows are at **the
same pace**. A long run prescribed as three ascending pace stages violates that by construction:

```
km 2-6    5:03.4   HR 130.0   -> EF 0.02533
km 14-18  4:56.1   HR 142.5   -> EF 0.02369      -6.5 %
```

Part of that 6.5 % is the pace change, and **the two cannot be separated after the fact.** Either
prescribe a constant-pace long run, or give up the decoupling number and use ratio metrics instead.

**Two things this is NOT.** (a) Not "the intensity was too low" — HR drift is measurable at aerobic
intensities too. (b) Not "the athlete was not fatigued" — 98 min of running produces glycogen depletion,
eccentric damage and neuromuscular fatigue however easy it felt. **Fatigue existing and decoupling being
measurable are different claims**, and the athlete will say so if you merge them.

### "Slower at matched conditions" is capability, not durability

The two get conflated because both arrive as a number going the wrong way:

| observation | what it is |
|---|---|
| same pace, HR climbing through the session | **durability** |
| same HR, pace falling through the session | **durability** |
| GCT up / stride down / vertical ratio up at constant pace | **mechanical durability** |
| **slower at matched dew point than two months ago** | **capability** — no within-session decay |
| opened too fast and blew up | **pacing** |
| high peak velocity but low 200 m average | **speed endurance** |
| 5 K pace ~18 s/km faster than the 30-min TT | **normal** |

Only the first three are durability. Writing "durability is his only deficit" off a matched-conditions
pace comparison is exactly the error this table exists to stop — and it collides with the
internal-consistency check above. **"Unknown" is a legitimate result**; say that instead.

### "Supplementary / remedial training" must attach to a measured deficit

When the athlete asks what 补强 / supplementary training is (or proposes adding accessory work): the term
is **not technical** — it is practice shorthand for three different things (fixing a *tested* weakness,
supporting the main quality, rehabilitating a diagnosed dysfunction). Say that first, or the
conversation silently becomes "add things".

The filter that keeps it honest:

> **"If I drop this, which capability I have already measured will fall?"**

- An answer exists → keep it, and treat it as **maintenance** — it does not need progressive overload.
- No answer → it is an added part, not a supplement. Parts do not become capability.

Worked case: every measured deficit sat **inside running** (durability, 5K-pace volume, easy-run
intensity, unmeasured speed), so none could be fixed by accessory work. The single supplement that
survived the filter was **heavy strength + plyometrics**, and only because the resilience literature
ties it to durability — the one measured weakness. → `references/durability-and-race-readiness.md`

**Give the athlete the corollary:** a supplement with no named deficit is not neutral; it dilutes the
session that would have moved the number.

### A strength programme needs a next progression, or it is not a base

The athlete's objection is correct: *"general physical qualities also need developing, it is just
gradual specialisation."* General preparation is real periodisation. The error is not being general —
it is prescribing general work that **cannot be specialised later**:

```
cul-de-sac    bodyweight -> 20 reps -> 2 kg dumbbell        (the end of the road)
real base     bodyweight -> loaded backpack -> 5-6 reps -> more load -> stronger
```

20 reps trains local endurance, and no amount of "20 reps" becomes a strength stimulus without
changing the exercise. **Ask "what is the next progression of this exercise?" — if the answer is "the
same thing with more reps", it is not a base.**

Two dose facts settle most of these arguments:

- **1x/week at real intensity maintains** most acquired strength; **3x/week is a development dose**. When
  the stated goal is "keep it while mileage rises", 3x/week is training for a target never set.
- **The time budget resolves "strength or miles" arithmetically.** 87 -> 105 km/week needs ~+1.5 h;
  cutting non-running work from a development dose (~2.5 h/week) to a maintenance dose (~1.1 h) frees
  ~1.4 h. The athlete never had to choose — the dose was the constraint, not the clock. Say it as
  *"you are not training too much, you are spending a development dose on a maintenance goal."*

→ zero-transfer list, the no-gym load substitutions, eccentric gap and placement rules:
  `references/strength-and-gpp.md`

### Which session costs the most is not which session is longest

Recovery cost tracks **intensity**, not duration. Same athlete, two adjacent cases:

```
Sat   20.03 km / 98 min / 4:54 / avgHR 138                              -> the long run
Mon   6 x 1000 / 22 min of work / avgHR 174, max 188, anaerobic TE 2.8  -> the quality session
Tue   next-day aerobic run, vs the post-long-run one:
        GCT 241 vs 237 ms | cadence 186 vs 190 | HR 141 vs 137 at the same pace
```

**The 22-minute quality session left the bigger mark.** Two consequences:

1. **The day after the hardest session is a *recovery* day, not an aerobic day** — keep the volume, drop
   the band (5:15-5:25 / HR <=138 instead of 5:05-5:15 / HR 140-148). An aerobic band there turns the
   week into "two hard days plus one half-hard day".
2. **Do not put strength in that morning** — it is the second-cheapest place in the week to add stress,
   and it lands inside the worst recovery window.

**The mechanical fields are the tell.** GCT and cadence at matched pace degrade before HR does — a
4-5 ms GCT rise plus a 4-5 spm cadence drop with HR up only 4 bpm is residual fatigue, and it is a
cleaner signal than the heart rate. Self-reported effort ("felt easy") does not overrule it.

### Say what a session stimulated, not what you called it

A session is named by its intention and paid out at whatever the pace actually was. Worked case: a
design called "5K-pace volume" was run at **3:42.5**, against a measured LT2 of ~3:59 and vVO2max of
~3:32 — i.e. **between LT2 and vVO2max**, 7.4 % above LT2 and 2.1 % below 5K pace, at HR 186-188
(94-96 % HRmax).

What that actually bought:

- ~110-130 s per rep above 90 % VO2max, ~12 min per session — **a VO2max stimulus**
- lactate buffering (anaerobic TE 2.8)
- neuromuscular rehearsal of race-speed mechanics
- pacing execution

What it did **not** buy: no MLSS shift, no durability, no aerobic base.

**Name the category out loud: an "expression" session, not a "construction" session.** It converts
capacity into performance; it does not enlarge capacity. That distinction is what justifies its dose
(1x/week, 36-48 h recovery) and what stops the athlete reading a good 6x1000 as proof the engine is
growing. The building happens in the threshold session and the long run.

**The watch separates the two categories for you — check the training-effect pair before arguing.**
Same athlete, same week:

```
6 x 1000 @ 3:42.5   aerobic TE 3.8 / anaerobic TE 2.8   -> VO2max + lactate buffering
6 x 6:00 @ 4:00.0   aerobic TE 4.3 / anaerobic TE 0.5   -> threshold, essentially no anaerobic cost
```

An anaerobic TE near zero next to a high aerobic TE is the signature of a **construction** session; a
substantial anaerobic component means the pace left the MLSS band, whatever the session was called.
Two numbers, no interpretation, and it corroborates the pace-vs-threshold arithmetic independently —
worth quoting whenever the athlete asks "what did today actually do?"

## Changing sensors breaks the series — treat it as data, not as a detail

A longitudinal HR metric (a monthly `@HR150` pace, any efficiency series) is only valid **within one
sensor**. Chest straps (ECG) and wrist optical do not agree, and the disagreement is not a constant you
can eyeball away.

Observed on a same-pace, adjacent-day pair:

```
wrist optical   @ 5:19/km  ->  HR 125–133
chest strap     @ 5:17/km  ->  HR 137
```

Roughly **+5 to +10 bpm**, in the direction theory predicts (optical under-reads at higher intensity).
But this is **one pair of sessions, so it is not calibrated** — and the competing explanations (residual
fatigue, cumulative load, a different pace structure that day) cannot be separated from it. Say so
rather than quoting the offset as a number.

Rules:

1. **A sensor change is a series break.** Start a new series; do not join the two.
2. **Do not over-retract.** Findings from *within* the old sensor's series stay valid. In the case
   studied, three consecutive days on the same wrist sensor showed a consistent 7–15 bpm drop at
   matched pace — that survives the break. Only cross-sensor comparisons die.
3. **Ask before the athlete switches**, or at minimum record the switch date, so a later session is not
   silently comparing two instruments.
4. **Arrange an overlap if you want a real number.** Same pace, two consecutive days, one sensor each.
   Without an overlap the offset stays an estimate forever.
5. **Performance is sensor-independent.** Time trials and races remain the ground truth — losing HR
   series continuity does not cost you the ability to judge.
6. Prefer the **better** instrument even though it breaks the series: high-intensity short-effort data
   is exactly where optical is least trustworthy, and that is where the coaching decisions are.

### Even a chest strap produces impossible values — screen for it before trusting

A strap with dry electrodes (no sweat yet, poor placement) can **lock onto noise for the first
2–3 km**. The tell is a value that is physiologically impossible for the pace:

```
easy run, km 1-3      5:59 / 5:39 / 5:35  ->  avgHR 125 / 181 / 178  (max 181 / 186 / 186)
from km 4 onward      5:28-5:35           ->  avgHR 128-142
```

An 181 bpm **average** across a conversational 5:39 km is not a fatigue reading — the athlete's LTHR
*is* 181. It also contaminates the reported whole-session average (142 here, against ~138 from the
clean segments), and that whole-session average is exactly what a naive pipeline feeds to a
regression.

Rules:
1. **Screen every session**: a lap whose `avgHR` is implausible for its pace is an artifact. Cheap
   test — easy pace with `avgHR` above the athlete's threshold HR.
2. **Read segments, not the session average**, whenever the opening laps are suspect — and say which
   laps you used.
3. **Fix the instrument, not the analysis**: wet the electrode strip first, or start recording a few
   minutes in, or reseat the strap.
4. **Teach the athlete the signature** so they flag it ("the first few km of HR today are fake") rather
   than you silently comparing a corrupted number.

## Short efforts, sprints and stairs — what the watch can and cannot measure

Strides, hill/stair sprints and accelerations are a normal weekly component, and their data is
*partly* usable. Do not discard the session; do not trust it whole either.

| Metric | Usable? | Why |
|---|---|---|
| Lap time per rep | ✅ | The only reliable performance number — use it as the entire measurement |
| HR recovery after the effort (e.g. +60 s of walking) | ✅ | For short reps this *is* the physiological signal |
| Cadence | ✅ (mostly) | Accelerometer-based. But do **not** compare it to flat-running cadence |
| Ground contact time / vertical oscillation | ✅ on flat, ❌ on stairs | Stair geometry distorts them |
| GPS distance and pace | ❌ on stairs, ⚠️ sub-400 m laps | Short segment + stairs = noise |
| Step length, vertical ratio | ❌ wherever speed is wrong | Both are derived from speed |

**Peak HR is not an intensity criterion for reps under ~15 s.** Heart rate lags 20–30 s, so an 11 s
effort physically cannot express its intensity in the HR trace — a genuinely hard stair session can
legitimately peak around 130 bpm during the climbs. Judge short reps by **rep times** (consistency,
and the drop from first to last) plus the athlete's own report.

**And when the HR trace disagrees with the athlete's perceived effort, believe the athlete — and
retract.** Wrist optical HR degrades badly under the arm swing and wrist flexion of stair/hill work
(usually *under*-reading), on top of the physiological lag. In the case studied the trace showed climb
HR peaking at only 133 bpm, which was read as "intensity probably too low"; the athlete replied that it
felt far harder than that. The correct response is not to argue or to ask for a re-test — it is to say
plainly that the judgement was made on a bad instrument, retract it, and drop HR from that session type
as a monitoring variable entirely. Keep it only if the athlete happens to have a chest strap.

**The same logic runs both ways:** having retracted an HR-derived judgement, do not then substitute a
vague "go by feel". Replace it with an objective anchor that survives the bad instrument —
**rep 1 all-out, record the time, every later rep within +5 %.** That is measurable, comparable week to
week, and does not depend on any sensor.

**Two failure signatures to look for in rep times:**
- *Near-identical and slow* → the athlete found a repeatable rhythm instead of going hard.
  Fix with a calibration rule: **rep 1 all-out, record the time; every later rep within +5 %.**
- *Falling apart by rep 6–8* → recovery too short or too many reps. Cap the set where quality ends;
  do not chase the prescribed rep count.

**Also check the segment length, not just the rep time.** If total vertical gain ÷ number of reps is
small (e.g. 42 m ÷ 8 = ~5 m per climb), the athlete is reaching the top in a few seconds and never
gets a stable high-force phase — the stimulus is half of what a proper 10–12 s hill rep gives. Fix it
by finding a longer continuous climb, not by adding reps.

**Peak speed from record-level data:** split the stream on a speed threshold (e.g. >4 m/s) and take
the max within each run. It works, but on sub-100 m segments the peak is inflated by GPS noise — use
it as an order-of-magnitude check and prefer accelerometer-derived GCT/cadence when the number matters.
See `references/short-effort-metrics.md` for a worked example.

**A whole-session `maxSpeed` field beats anything derived from lap averages — but the rest of the
short-effort summary is mostly noise.** A connected-service API often carries fields the FIT lap
summary does not (peak speed, running power). Trust them in this order:

| field | short efforts (< 400 m) |
|---|---|
| `maxSpeed` | ✅ **use it** — it carries the information a lap average destroys |
| elapsed vs moving duration | ⚠️ moving-time excludes the closing deceleration, so a late watch-stop inflates `elapsed` by 1–2 s |
| GCT, stride length, vertical oscillation, vertical ratio | ✅ accelerometer-based, structure-independent |
| **running power, elevation gain** | ❌ **GPS-altitude contamination** |

Worked case for the last row: a **150 m** rep on a flat track reported **6 m of climb (≈4 % grade)** —
physically impossible — and the resulting power figures then **inverted** the expected relationship
(lower speed paired with higher power). Never explain a short-effort anomaly with power or grade; check
whether the altitude fix invented it first.

## Plan the season around the climate window, not the calendar

Where dew point is the binding constraint, the year has a **narrow good window** (in the case studied,
only Oct–Dec sit below 12 °C; summer sits at 22–23 °C). Direct planning consequences:

- Put the **high-volume / high-intensity block inside the window**, scheduled in advance.
- Write the heat-replacement rules (dew-point table) into the plan *before* summer, so intensity is
downgraded deliberately rather than chased and burned.
- When reviewing a summer month, ask "was this month trainable at all?" before calling the reduced
  load a mistake. Often it was not — and mislabelling it as a coaching error sends the next block in
  the wrong direction.

## Critical speed (CS) and D' from two time trials

A robust two-parameter model of sustainable performance, and a better race predictor than a
lactate-threshold pace.

```
CS = (d2 - d1) / (t2 - t1)          # m/s
D' = d2 - CS * t2                   # metres of work above CS
# predict a race: t = (distance - D') / CS
```

Use the two most reliable maximal efforts available (e.g. 3 K and 5 K).

**Staleness is the first thing to check.** A CS derived from a race three to six months old anchors a
*past* athlete. Date it in the model file and re-derive it at the next time trial — do not keep
prescribing from it just because it exists.

Sanity-check D' against an interval session: the model's continuous limit at a rep speed should be
in the same region as the total work done in the reps.

### Do NOT record a fixed "race pace / CS" percentage — corrected

An earlier version of this skill said to compute `race pace / CS` and compare it against a published
"well-trained runners sit 8–12 % above CS" band, with a ratio below ~7 % meaning the sustainable
ceiling is the limiter. **The athlete rejected the arithmetic, and was right:**

> *"fractional utilization 通常讨论 5K 速度相对于 V̇O₂max 速度 / CS 的利用程度，不是简单 (T−5K)/T。*
> *所以不应该记录‘6.4%’这个固定值。"*

The error is a **number carried across two different definitions** — a ratio computed from a
two-point-model CS, compared against a literature band measured against V̇O₂max velocity or a threshold
velocity. Not the same quantity, so the comparison is void — and the percentage then gets quoted back
in a later session looking like a measurement.

**Record the space, not the percentage.** For the case studied:

```
5 K pace          3:43/km
threshold pace    4:12/km        ->  29 s/km apart
```

That is legitimate, says the same useful thing, and needs no normalised ratio behind it. What to write
down: *the 5 K-specific velocity is still well above current threshold velocity; the sustainable
high-speed fraction still needs work.*

**General rule for this whole skill:** before recording any ratio, percentage or index, confirm it is
computed against the same reference as whatever you are comparing it to. A number that changed
definitions mid-sentence is worse than no number — it survives into the next session dressed as
evidence.

## Measurement design — the format has to match the quality being measured

Picking a test format is a design decision with its own failure mode: **the format can be safe and still
measure the wrong thing.** Four of these were made in one block on the same athlete, and all had to be
retracted.

### A test's distance comes from the physiological requirement, not from the benchmark it will be run against

The durability long run was first set at **18 km** for one reason: to match two historical **18.04 km**
benchmarks so the paces would be comparable. That anchor died the moment the climate step ran — the test
day's dew point was **10 °C lower**, so absolute paces could not be compared at all and the reading had
to be a ratio. **Once the read is a ratio, matching distance buys nothing** — while 18 km at ~5:05 is
**92 min**, barely inside the **>90 min** durability window, and 20 km is 102 min with margin *and* puts
more fatigue before the fast finish that the test exists to observe.

**Order of operations: pick the distance that delivers the physiological dose, then decide what it can be
compared to.** Reversed, the climate check can strip the comparison of meaning and leave a test that is
too short for its own question.

When the test day and the benchmarks disagree on climate, measure ratios — they survive it:

| metric | robust to a climate difference |
|---|---|
| pace at matched HR, last third ÷ first third | ✅ within one session |
| final fast segment ÷ the segment preceding it | ✅ |
| absolute pace | ❌ across days with different dew point |

And say the arithmetic out loud when cutting the distance: *"18 km = 92 min, the assessment threshold is
90 — you are testing on the boundary."* The athlete can check that; a paper argument about comparability
they cannot.

### Within one session, the measurement runs before the training block

When a session contains both, put the measurement first. **Measurement validity cannot be recovered
after the fact; an easy aerobic block's quality can.**

Worked case: a 10–12 km easy run plus a 2 × 150 m max-velocity test. Run the aerobic block first and
the velocity reading is taken in a glycogen-reduced, rhythm-locked state — several percent low, which
is the same magnitude as the difference the test exists to detect. It is also *the same error the test
is meant to remove*: the athlete's only prior 200 m mark had been taken as the **second** rep of a set,
after a race-pace session. Reproducing the fatigue source does not produce a cleaner number.

The athlete will ask the obvious thing — *"can't the aerobic run be the warm-up?"* — and is **half
right**: the first 15–20 min genuinely is the warm-up, and past ~30 min the same running flips from
potentiating to fatiguing. So **split rather than reorder**:

```
15 min easy + dynamic activation + 2-3 x 60 m progressive   <- this IS the warm-up
2 x 150 m all-out (opposite directions, 4-5 min walk between)
remaining 6-8 km at aerobic pace                            <- same total aerobic volume
```

**Read the 150 m, not the 60 m.** Hand-timing error on a lap button is ~0.2–0.3 s: harmless on a
23 s effort (1.3 %) and useless on a 10 s one (3 %). The 60 m is neural priming, not data.

### A rep session measures repeatability — it cannot measure continuity

After a 4 km TT collapsed at 1.4 km on pacing (see above), the fix proposed was to use **6 x 1000 m** as
stimulus *and* anchor: reps are self-limiting, so one bad rep costs a rep rather than the measurement.
Sound reasoning for **safety**, invalid for **this** limiter:

```
limiter            holding a pace for a long time WITHOUT a break
6 x 1000 measures  how fast you can go WITH 2:00 of recovery between each
```

Reps let HR fall 15–20 bpm and clear part of the lactate. The session proves **repeatability**; it says
nothing about continuity. "5 K pace = 3:41–3:46", derived from the fastest rep, was an over-read and had
to be withdrawn.

**State which quality a format can and cannot resolve before running it.** If the limiter is continuity,
the measurement must involve continuity — a long run with a fixed final segment, or a continuous
threshold effort. Both are sessions the athlete already runs, so the measurement costs no extra fatigue.

### A rep spread only means something together with its direction

An earlier rule read "spread > 8 s → the pace was too fast". The very next session broke it:

```
6 x 1000 m   spread 8.1 s    227.8 / 224.1 / 228.2 / 228.3 / 223.3 / 220.2 s
last rep = fastest of the set
```

By the old rule that was "too fast". It was the opposite — the athlete had more in hand, and the anchor
needed tightening, not loosening.

| spread | last rep | reading |
|---|---|---|
| large | slower | too fast — opened above what was repeatable |
| large | **fastest** | **under-paced, or over-restrained mid-session** |
| small | level | the pace was right |

**Report the split list, not just the spread.** A spread without its direction is unreadable, and it is
the field most likely to be quoted back later as a verdict.

### Pace drifting is not only "cannot hold back" — it is bidirectional

The same session in the athlete's words: *"I pushed on rep 2 and found it was faster, so on rep 3 I
deliberately held the pace back, and after that I could not hold it back again."* The splits show it
precisely: two restrained reps sitting ~4 s slower than the reps on either side of them.

The failure is not insufficient discipline. **Pace is being set by feel in both directions** — press when
it feels light, brake when it feels heavy — so the session's output becomes a function of perceived
effort rather than a controlled variable.

**Fix: one fixed number for every rep, with no in-session adjustment.** A rep that feels light is still
run at the number. Pair it with a single checkable ceiling on the opening rep ("first 1000 m no faster
than 3:45"; "the 400 m checkpoint is 90–92 s") so the judgement does not have to happen while running.

### Give the athlete a variance criterion, not a "slow first rep"

"First 400 m 98-99 s" was the instruction; the athlete ran **95.5 s, then 99.9 s**. The block average
landed exactly on target (4:01.6) while **12.6 s/km of swing inside one 6-minute block** wasted the dose.
Two lessons:

1. **A deliberately slow opening lap is not executable.** It contradicts every pacing instinct, so it is
   abandoned within the first 30 seconds. Do not prescribe it — prescribe a *spread*, which is measurable
   afterwards and does not require the athlete to overrule their own feel mid-lap.
2. **Police the variance, not the average.** Reconstruct the blocks from the 400 m auto-laps and score
   **max − min within each block: <= 3 s controlled, > 6 s means that block was two different sessions.**

```
block 1   3:58.8  4:09.8  3:59.5  3:57.2   spread 12.6   <- one block, two sessions
block 2   4:01.6  4:01.8  4:01.5  4:01.4   spread  0.4   <- the only clean one
blocks 3-6  3:54-3:56 opener, then 3:59-4:03            spread 5-8
```

**Every block opened with its fastest 400 m.** The untutored opening is ~1.5-2 % fast in a rep session
(3:42.5 for a 3:48 prescription) *and* in a threshold block (3:54 for a 4:00 block). That is **one
systematic bias, not two problems** — and it is why a fixed mid-block checkpoint beats a "start slow"
instruction.

**Reconstruction note:** on a 400 m track an interval block's laps read 400 / 400 / 400 / partial,
followed by one recovery lap. Group laps until the recovery lap, then sum — never compare a single 400 m
lap pace against a block pace; the block average is what the prescription was about.

### 30 minutes of continuous running does NOT establish threshold continuity

A retracted claim. A 30:00 continuous effort at 4:11.1 with HR plateauing at 181 was read as "threshold
continuity is fine". Neither half holds:

1. **The plateau only says 181 was the steady-state HR at that pace.** Whether the pace sat at or below
   MLSS is exactly what was unknown — and a later session at 4:07 reported as *"felt easy"* is evidence
   it sat **below**.
2. **30 min is not the ceiling.** Well-trained 5 000 m runners hold LT2 for **50–60 min**. Finishing
   30 min without drift has not touched the limit.

And the session was prescribed as "30 minutes", not "as far as you can in 30 minutes" — so it could not
answer the question at all. Correct reading: **threshold continuity unknown.**

**A 30-min maximal pace is also not LT2 pace.** It is roughly 2–4 % faster (5–10 s/km), because LT2 is
the ~60-min sustainable intensity. Use `LT2 ≈ 30-min pace + 5–10 s/km`, and take the **average HR of the
30-min effort as LTHR** — that is the more reliable of the two outputs. Skipping the conversion inflates
every threshold prescription by about one pace band.

→ full protocol, the drift criteria and the meter-free toolbox: `references/threshold-testing.md`

## Units and field traps (consumer fitness exports)

- Activity-summary JSON often stores **distance in cm** (`/100000` → km) and **duration in ms**.
- A field literally named `startTimeLocal` may already be local time expressed as an epoch — adding
  a UTC offset **double-shifts** it. Cross-check against a known training hour (e.g. an early-morning
  runner whose sessions must land at 05:00–06:30 local).
- Parsed per-activity JSON may use **true UTC** — that one *does* need the offset.
- `avg_step_length` is often **cm**; per-leg cadence must be **doubled** for total steps/min.
  Cross-check: `speed = total_steps_per_min × step_length` — if it's off by ~2x, the step length is
  per-stride or the cadence is per-leg.
- Merging two exports: dedupe by time proximity (<15 min), and state how far each source reaches —
  a "collapse in volume" is often just the export boundary.
- Walking a large export tree can hang on directory listing; use a depth-limited, time-guarded walk.
- **Parsed per-activity files commonly live in per-activity subdirectories**
  (`new_data/<activityId>/<activityId>_ACTIVITY.fit`). A parser that globs only the top level
  silently reports "0 files found" while the data sits right there. Glob **both** `*.fit` and
  `*/*.fit`. FIT parsing additionally needs `pip install fitparse`.
- **`summarizedActivities*.json` is a LIST wrapping one dict**: `[{ "summarizedActivitiesExport": [...] }]`.
  `json.load(...)["summarizedActivitiesExport"]` raises `TypeError: list indices must be integers or
  slices`; the working access is `json.load(...)[0]["summarizedActivitiesExport"]`. **Probe the type
  before parsing** — this cost two failed attempts in one session.
- **Those exports carry the whole `splits[].measurements[]` tree** — tens of MB of per-split measurement
  dicts. Extract summary fields and **never print the raw object**: one careless print blew a 1 MB
  stdout cap and pushed the useful numbers off-screen.
- **A connected-service `get_*_activities` call paginates at 100** (`limit` max 100, use `offset`), and
  **`detail="compact"` uses different field names than `detail="full"`** — a compact response returned
  `None` for every attribute a parser written against `full` read. Dump one full record's key list
  before writing the extractor.
- **Per-km splits need the FIT file, not the API.** The activity's `splitSummaries` returns only two
  whole-activity entries (one per `splitType`) — there is no per-lap table in the JSON response at all,
  so a parser that expects one silently reports a single 20 km "split".
- **FIT `record` messages do not always carry ground-contact time.** A record stream had `cadence`
  (per-leg, double it for steps/min), `enhanced_speed`, `heart_rate`, `temperature`,
  `vertical_oscillation`, `vertical_ratio` — but GCT existed only on the session/lap summary. Check the
  field inventory before promising a per-km GCT series.

→ working MCP-call harness, FIT download and source-selection table: `references/garmin-data-access.md`

## Reporting

## Reporting

- Give every conclusion an explicit **confidence level**, and say which conclusion rests on a thin
  sample (`n`).
- When new evidence overturns a previous judgement, **say "I was wrong" plainly and state what
  overturned it.** Do not quietly revise. Retracting openly is worth more than being consistent.
- Do not report the volume drop / intensity shift as a verdict until the climate confound is removed.
- If the user works in another language, keep the analysis output in theirs.
- **A heart-rate band without a pace ladder gets pushed back on — give both.** The athlete's words:
  *"HR isn't absolutely precise — give me reference paces."* He is right, and the fix is **not** to
  switch the control variable. Keep pace as the control and HR as the verifier, but state the pace band
  each HR band has historically corresponded to, derived from **that athlete's own recent sessions**
  (e.g. an easy run at 5:15.8 @ HR 139 plus a steady run at 5:04.6 @ HR 150–155 → HR 143–148 ≈
  5:10–5:20). Without it the session has no observable checkpoint while running. Pair it with an
  override rule so neither variable is silently ignored: *HR 5 bpm above the band → ease 5 s/km;
  HR below the band → allow 5 s/km faster.*
- **When the athlete's question contains a premise, test the premise before answering it.**
  *"Why is my long run slower than it used to be?"* was answered by the premise being false — the
  long-run-to-easy gap had held at 25–27 s/km for a year and **both** ends had slowed together. Explaining
  "why it got slower" would have manufactured a cause for an event that did not happen. The method (a
  weather-matched within-period self-comparison) is in skill `endurance-training-data-analysis`, section
  "先验关系，再验绝对值".
- **Do not re-ask a constraint the athlete has already answered.** "I have no race in November",
  stated twice, means design around it. Same for equipment ("no gym", "no hills", "no training
  partner"): accept → give the substitute → move on. Re-asking reads as not listening, and the
  substitute plan is usually better than the thing that was ruled out.
- When the athlete asks an **execution-level** question (what exactly counts as a warm-up, is a
  cool-down required, pace or heart rate, which day does strength go), answer with **criteria**, not
  slogans: the purpose of the item, its dose, and the check that tells them it was enough. Vague
  "listen to your body" answers come straight back as another question.
- **Show the full accounting when re-issuing a session, or it reads as a cut.** A Friday first written
  as "aerobic 10–12 km + speed test" was re-issued as "test + 6–8 km" and drew *"why did the aerobic
  volume drop by almost half?"* — correctly, because the 15-min warm-up (≈2.5 km of easy running) had
  been dropped out of the sum when the session was split into numbered steps. **List every running
  segment and its distance, including warm-up and cool-down, even when the athlete does not log them.**
- **Never say "cut" when the finding is "redundant".** Trimming a 60-move core routine to five drew
  *"do all my previous exercises have no value now? And no push-ups?"* — a fair objection, because the
  finding was **repetition**, not worthlessness: ten leg-raise variants of one movement, at a rep range
  that could never become a strength stimulus. Say **"reallocate the dose"**, and spend one line per
  group naming what it *was* good for before saying where it moved. The athlete put months into that
  work; the analysis should show it saw the work, not only the number.
- **If the athlete challenges a conversion conceptually, answer the concept before the arithmetic.**
  *"30 min → 60 min conversion — shouldn't threshold pace be one number?"* is a correct objection:
  MLSS **is** one pace (time-to-exhaustion ≈ 60–70 min in trained runners). The conversion exists only
  because a 30-min *maximal* effort sits **above** MLSS. Lead with that — otherwise the formula reads
  as two different thresholds, and the athlete is right to push back.
- **Do not assert a timescale; name what sets it.** *"It's a matter of years"* drew *"is it definitely
years? progress rates differ"* — also correct. Give a range per milestone (sub-17 and sub-16 are
  different projects: one is reconnecting what was lost, the other is raising the ceiling), state the
  binding constraint (volume and what it can be absorbed at), and name the one genuinely unknown —
  responder status — as unknown rather than smoothing it into the range.
- **A stated future direction is not a current priority.** The athlete said he would eventually move to
  longer distances; the next block was re-weighted toward that future phase (5 K-pace volume demoted to
  "maintenance", posterior-chain hypertrophy promoted from "negative" to "positive"). Corrected:
  *"right now I'm attacking 5 K, I'm not considering the rest."* **Record the future direction in the
  model; do not let it re-weight the block that is running now.** Optimising for a phase that has not
  started is a structural substitution for judgement — the same failure mode as a calendar-based block.
- **When the conditions change, re-derive the pace ladder — never carry last week's.** Told the
  athlete the long run would be ~10 °C of dew point cooler, then handed over a pace ladder derived from
  a 16 °C-dew-point session. He ran **22 s/km faster at a lower HR** than prescribed and said *"if I'd
  run to HR it would have been much faster."* Announcing cooler weather and then not adjusting the
  numbers is worse than not mentioning it: it licenses the athlete to ignore both.
- **When a prescription is wrong, name the mechanism, not just the outcome.** The same session drew
  *"why can't it measure durability?"* — the honest answer was *not* "intensity too low" (my first
  attempt) but **"I gave you ascending pace stages, which invalidates the comparison."** The wrong
  explanation was itself the thing being corrected; a diagnosis that blames the athlete's effort when
  the flaw was in the prescription costs credibility twice.

## Support files

- `references/heat-and-climate-matching.md` — dew-point thresholds, adjustment formulas, a worked
  real climate table, and a full worked example of a conclusion being corrected by climate matching.
- `references/prescribing-a-block.md` — the weekly intent set in detail, continuous vs interval
  threshold, %%CS pace tables, target arithmetic, double-threshold (principle vs form), hill/stair
  sprint specs, plyometric evidence and the no-gym substitution ladder.
- `references/period-comparison.md` — how to run a year-on-year / same-season matched comparison:
  the HR-band method and its ±10 s/km resolution limit, GCT-at-normalised-pace as the sensor-independent
  hard line, the reconciliation check, and the separate-workbook deliverable.
- `references/short-effort-metrics.md` — what is measurable on strides / stair sprints / short laps,
  with a worked example and the calibration rules for short maximal reps.
- `references/max-velocity-testing.md` — the max-velocity test end to end: rep length vs runway, the
  field-trust table for short efforts, peak-vs-sustained reserve arithmetic, and how a peak reading and
  a fading long run turn out to be the same finding.
- `references/threshold-testing.md` — the 30-minute threshold test end to end: pacing band **plus a
  10-min checkpoint** (a bare ceiling under-paces a continuous effort — see above), how to read the
  result (avgHR → LTHR, 30-min pace → LT2 via +5–10 s/km **only if the effort was maximal**), HR-drift
  criterion, and the five meter-free cross-checks for locating threshold without a lactate analyser.
- `references/durability-and-race-readiness.md` — MLSS time-to-exhaustion and the +12 s/km gap between
  intermittent and continuous MLSS; the durability / fatigability / repeatability / resilience
  constructs and how to assess each; what trains durability; why "no race" removes peaking but not
  race-readiness; decomposing "the level" into four slow variables; and separating the sub-17 and sub-16
  timelines.
- `references/recovery-monitoring.md` — what each wearable recovery field can and cannot support
  (duration vs staging vs HRV vs load balance vs race predictions), the time-in-bed arithmetic, how
  to report sleep and HRV when they disagree, and what to do when measured recovery contradicts a
  ramp that was planned in weeks rather than in recovery capacity.
- `references/strength-and-gpp.md` — strength and general physical preparation as a class: the
  cul-de-sac test, maintenance vs development dose, the time-budget arithmetic, the zero-transfer list,
  the eccentric gap, no-gym load substitutions, placement rules, and why core is not a strength session.
- `scripts/fetch_weather.py` — fetch real hourly weather per session and emit `sessions_weather.csv`.
- `scripts/heat_analysis.py` — monthly heat load, dew-point-matched comparison, efficiency series.
- `references/garmin-data-access.md` — how to actually pull the data: the stdio MCP JSON-RPC
  subprocess harness (when the native MCP tools are not loaded in the session), the FIT-download tool
  and its required env var, the `summarizedActivities` wrapper shape, FIT record field notes, and a
  source-selection table for which question each endpoint answers.
