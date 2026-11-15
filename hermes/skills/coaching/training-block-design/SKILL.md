---
name: training-block-design
description: Use when designing an athlete's next training block.
---

# Training Block Design under real constraints

For the recurring task: "here is the last few days of training and my goal — what should I do next?"

A block is two decisions: **what adaptation matters most right now**, and **how to fit it around the
constraints the athlete actually has**. Most bad blocks come from getting the second one wrong.

Analysis (is he fitter than last month? what limits him?) belongs in `endurance-training-analysis`.
This skill is the design side.

---

## 1. Anchor to the athlete's actual rolling state — not the calendar

The athlete trains continuously. "Week" is an **accounting unit**, not a schedule boundary.

- Before writing anything, pull the **last 3–7 days of actual sessions**. That rolling window is week 1.
- **Do not start the plan "tomorrow"** and do not restart a week because the plan says the week starts
  on Monday. The athlete will have already trained that day.
- Write the table as **"done ✓ + remaining days"**, never as a grid pretending to start from zero.
- Correction received: a plan that began the next day was answered with "but I already did my
  recovery run today." The fix is not a smaller plan — it is re-anchoring the window.
- Carry forward the quality already done inside the window. If the athlete did a rep session two days
  ago, that session **is** this week's quality; do not stack a second one on top.

### Read the plan artifact before prescribing a session — it drifts out of sync with itself

**The plan file is the anchor of §1, and it can contradict itself.** Before naming the content of a
specific session, open the file. Do not answer from memory of what was designed — that is how a
prescription and its own document end up disagreeing.

Worked failure: asked for the next day's session, the answer given was *"2×15 min threshold"*. The
plan file contained **three** versions of the same Wednesday session:

| Where | What it said |
|---|---|
| Block skeleton | `3×10 min` — **stale residue**, never updated |
| Weekly template | `continuous 20 → 25 → 30 → 35 min` — the actual **design intent** |
| The conversation | `2×15 min` — matched **neither** |

Root cause: a design decision (intervals → continuous threshold) was patched into the reasoning
section but not into the skeleton, and the conversational answer was then given without reading either.

**Resolution rules when versions disagree:**

1. **The reasoning section wins over a skeleton line.** A skeleton is a summary and summaries go stale
   the moment a decision changes; the paragraph that argues *why* is what was actually decided.
2. **A version that appears nowhere in the file is never right** — it means the answer was improvised.
3. **Then fix the drift**, in the same turn. Leave a dated correction note naming every version and
   which one is now authoritative, so the stale line cannot be picked up again.

This is the same family as §2's *"give decisions, not procedures"* — but inverted: a **procedure**
written down is safe, a **decision** written down is only safe if it is read before being restated.

---

## 2. Prescribe stimuli and doses — NEVER numbers to hit

**The most repeated correction in this coaching relationship. It was made twice, on two different
variables, and both times the athlete was right.**

### The two failures

- **A "minimum interval between sessions" table** (48 h / 72 h / …). Answered with:
  *"没有具体的数字就不要用间隔来死板的限制自己"* — do not let interval numbers rigidly constrain you.
  The table was also factually wrong for this athlete: their own best block ran medium / hard / long
  on Mon / Wed / Sat with no such rule, and the Norwegian double-threshold method puts **two threshold
  sessions in one day**.
- **"Volume target 82–88 km/week; don't go above 100."** Answered with:
  *"跑量是结果，即使一周100也是一种结果"* — volume is a **result**; even 100 km in a week is a result.
  Their own history contains a **106.6 km week with zero injury**, so the cap contradicted their own
  evidence. Imposing a generic rule over the athlete's own data is the error.

### The correct form

Specify each week by **which stimuli must occur and at what dose**. The kilometres are whatever those
add up to.

| Stimulus | Dose | Purpose |
|---|---|---|
| Threshold / sub-threshold | 30–45 min of work | pushes critical speed — usually the real limiter |
| Race pace | 4–6 km | converts CS into event-specific ability |
| Long run | 1 × 15–20 km | aerobic base + late-race fatigue resistance |
| Easy aerobic | fills the rest | raises the ceiling on how much threshold work is absorbable |
| Neuromuscular | 2–3 stride sessions, 1 hill/stair session | ground-contact time, running economy |

> The weekly total is the sum of those. Whether it lands at 65 or 100 depends on what those five look
> like and how the athlete recovers — **not the other way round.**

A plan table should read: *expected* volume (a consequence) next to *required stimuli* (the target).
Label the columns that way, or the number silently becomes the goal.

### Corollary — do not set an upper bound either

"Don't go above N km" is the same error inverted. Where **too much** shows up is in readable signals,
never in a number:

- first rep of a quality session goes flat / pace decay > 6 s/km
- the legs never "come alive" during warm-up
- morning resting HR ≥ 5 bpm off baseline two days running
- a single-point pain (not muscle soreness)

Any of those → back off. None of them → **no cap.**

### A structure is not a substitute for judgement

Same error, one level up. The athlete's own words:
*"不要分一二三四层和制造清单以及库，这会导致机械化和片面化"* — do not build tiers, lists and libraries;
that produces mechanical, one-sided coaching.

**Root cause: a structure is created so a thing becomes "executable", and the moment it is fixed it
loses the ability to respond to the athlete's state that day — which is where all the difficulty
actually lives. The longer the checklist, the less judgement happens.**

The line that matters:

| | |
|---|---|
| **"Tomorrow: 7–8 km easy at 5:20–5:40"** | ✅ a **decision** — about one specific tomorrow. Give it. |
| **"Available tools for the elastic stimulus"** | ❌ a **procedure** — it decides *for* the athlete, and it does not know their state. |

**Rules**

1. **Give decisions, not procedures.** Each day's prescription is specific, dated, and expires.
2. **Tables only for data** — pace tables, lap splits, era comparisons. Anything that *guides
   behaviour* is prose plus the reasoning. **No tiers, no checklists, no libraries, no ladders.**
3. **A principle may be short; it may not be a lookup table.** Test: can the athlete use it without
   me? If it can only be *consulted*, it will eventually be consulted against their interest.
4. **Name the class when you make the same mistake a third time.** Here: description→target
   (intervals), description→target (volume), two quantities conflated, tool mistaken for standard,
   judgement replaced by structure. Five instances, one root.

**Accept the trade:** writing less gives the athlete less *apparent* completeness. Some of that
reassurance was never real — a checklist can be complete in form and empty in content.

### Do not define the goal negatively — it makes the driving mechanism optional

A framing error with a real performance consequence. Written in a plan:
*"the goal is not strength, it is the ability to hold position for the whole session."*

Athlete's correction: *"目标不是力量，但是力量是重要的，只能说目标不是肌肥大。力量、功能、协调性很重要，
肌肉的围度只能说是最后训练的结果。"*

**Why this is not pedantry.** If the goal is stated as *not strength*, then **progressive overload
becomes optional** — and progressive overload is the fundamental driver of adaptation in every tissue.
A programme built on that sentence plateaus, and nobody can see why.

Two separate things were being conflated:

| | |
|---|---|
| **Not the goal** | hypertrophy (circumference) |
| **Are the goal** | strength, function, coordination |
| **Only a result** | circumference, as a by-product — and at low load with no gym it is unlikely anyway, so it is not a risk to manage, just not a design target |

The concrete error hiding inside it: **strength is a continuum** — maximal strength at one end,
strength *endurance* at the other. "Can't hold the scapula for 90 minutes" is a strength-endurance
problem. That is a branch of strength, not "not strength".

**Operational consequence — the capability chain is not "position → time → load → fatigue".**
It is:

> **coordination/position → strength → strength-endurance → event-specific (under fatigue)**

- **Coordination/position** — the only stage where neither load nor duration is added. Position only,
  because load destroys a pattern that is still being built.
- **Strength** — **as soon as position is stable, add load. Do not wait.** Zero-load time extension
  degenerates into *holding with very little force for a long time*, which trains nothing.
- **Strength-endurance** — add time **under load**. Zero-load duration trains coordination; loaded
  duration is what trains the quality that actually degrades at 90 minutes.
- **Event-specific** — only after the above.

**Load and duration then advance in parallel** — not "finish adding time, then add load".

**This applies to the lower body too**, not just supplementary work. Pogo hops and Bulgarian split
squats are also a strength prescription: they need progressive load (backpack 5 → 15 kg), not
"learn the movement, then hold 2 bodyweight sets forever".

### Structure must run ahead of performance — tendon adapts slower than the heart

The second, harder consequence of letting overload look optional. Supplied by the athlete:

> *"肌腱适应速度慢于心肺。这是很多进步快跑者的共同问题：心肺几个月提高很多，肌腱需要半年甚至几年。*
> *所以力量应该领先。"*

| Tissue | Adaptation timeline |
|---|---|
| cardiac output, vascular, mitochondrial | **weeks to months** |
| tendon / connective tissue | **six months to years** |

**Performance rising faster than the structure carrying it is the injury mechanism.** So strength and
structural work is not a supplement that trails the running — it has to **lead** it. Practical form:
keep progressively loading the strength work (backpack 5 → 10 → 15 kg, row difficulty angle, plyometric
volume) on a **monthly** clock, independent of how fast the aerobic side is moving.

**It has a forward-looking half as well.** An athlete targeting 16:00 (3:12/km) is heading for a
ground-contact time near 190 ms, down from 218 ms at current threshold pace — an order of magnitude more
elastic/tendon demand. That accumulates over years and has to start while the running is still slow
enough to afford it.

**Do not let "muscle is not the current bottleneck" shrink the strength prescription.** That inference
was made once here and the athlete rejected it, correctly: *a capacity not currently limiting is still
not optional to maintain and build.* A capacity may be cut for **scheduling** reasons in a compressed
week — stated as a tradeoff — but never on the judgement that it does not matter. Detail:
`references/supplementary-upper-body-core.md`.

### Boundary — "a result" is not "structureless"

With no structure at all, volume drifts. This athlete's August sat at 42 km/week — part heat, part an
over-cautious system — and that was drift, not design. The structure lives in the **stimulus set**,
not in the kilometres. Keep the stimulus set explicit; leave the total free.

### Also: volume is an output of the process, so an athlete's peak volume explains less than it looks

An 80 km/week block did not measurably beat a 67 km/week block on sub-maximal efficiency for this
athlete. That does **not** prove volume is useless — it proves the efficiency metric is blind to what
volume builds (capillary/mitochondrial density, stroke volume, late-race durability). Say which of the
two you mean before drawing a conclusion. And when volume *is* the goal, say what it is *for*:
**volume raises the ceiling on how much quality work can be absorbed.**

### A base phase is not an intensity holiday — do not zero the race-pace stimulus

When an athlete announces *"base phase"*, the reflexive move is to strip the quality and stack easy
volume. **Check what the stripped work was doing first.**

Race-pace work is **> 90 % aerobically supplied**, and a session of 6–11 km of work at race pace is a
*larger* aerobic stimulus than a 40-minute LT1 run — not a sharpening tool held back for later. In the
case studied the athlete's entire PR history sat inside one four-month window whose signature was
**1–2 sessions a week of 6–11 km of work at 3:38–3:49**; the band then collapsed from 61 km to 8 km once
the block changed shape. See `endurance-training-data-analysis`,
`references/pace-band-volume-analysis.md`.

So assess a base phase on **where the work sits**, not on how much of it there is:

- **Which band is empty?** That is the real question, and the athlete's own session histogram answers it
  — see `endurance-training-analysis`, the empty-zone section.
- **"Easy aerobic fills the rest" does not mean the rest is all easy.** If the band between threshold
  and race pace has gone to zero, the block has lost its main aerobic lever — it has not gained a base.
- **Name the zone in the athlete's own numbers before designing around it.** "2× LT1" is a label; LT1
  and LT2 differ several-fold in recovery cost and are routinely confused because both feel
  "comfortably hard".
- **A goal list is not a phase** — but **"not a phase" does not mean "drop the others"**. Seven
  targets (aerobic base, general fitness, muscular strength, endurance, tendon strength, speed, form)
  contain no priority. Run them through the §7 schedule-or-hook test to find **which one is the driver**.
  The driver should be the one whose *input* is the constraint — for aerobic base that is total work
  time, not a particular pace.

  ⚠ **Say "main direction", not "pick one or two and demote the rest".** That phrasing was corrected:

  > *"我知道它们不是并列的，但是不代表不练。一个周期只能说明以什么为主要方向，
  > 但是不应该把其他的能力忘掉。"*

  | | |
  |---|---|
  | ❌ **"1–2 drivers, everything else demoted to hooks"** | reads as *stop training them* |
  | ✅ **"one main direction; every capacity still trained"** | the cycle decides **who gets the best slot**, not **who gets trained** |

  **All capacities are trained in every phase. What the cycle allocates is sequencing and freshness** —
  which stimulus gets the fresh days, which gets attached to an existing habit. That is exactly the §7
  schedule-or-hook split: a **scheduling** category, not an **abandonment** category. Confusing the two
  turns a priority into a deletion, and the athlete will (correctly) push back.

> **A base phase is not about removing intensity — it is about putting intensity in the right place.**

---

## 3. Interval spacing is a reading of residual fatigue, not a clock

Never hand over a table of minimum hours. Hand over the principle and the read:

- The stronger the next stimulus, the cleaner the traces from the last one must be.
- Easy running leaves almost no trace → daily, even twice-daily, is fine.
- **Do not by default put two hard sessions back to back — that is a default, not a prohibition.**
  If there is a reason (fatigue resistance, simulating consecutive-day pressure), do it and watch the
  second session. *A reasoned exception is training; an unreasoned one is noise.*

**The read is the warm-up.** The first 10–15 minutes is the daily diagnostic:

- legs come alive, movement smooth, HR rising normally → run the plan
- legs heavy, movement stiff, HR ≥ 5 bpm above normal at the same pace → **change today's plan**

Second read: the **first rep** of the next quality session. A flat first rep means the traces are still
there — back off, do not push through.

**State that the plan table is a statement of intent, not a schedule.** The athlete may move sessions;
what must hold is that every stimulus occurs and traces are cleared. Anything that is a rule rather
than a read will eventually be obeyed against the athlete's interest.

### The long run's day is a structural variable — and "it breaks my rhythm" is a real objection

Received correction: with the long run on **Sunday**, Monday can never be a quality day, so the week's
anchor drifts later every cycle and no two weeks line up. The athlete's objection — *"then next week's
quality session isn't Monday, and so on; the timing stops being fixed"* — is a **structural** complaint,
not a preference, and it had to be fixed rather than argued with.

The fix is to anchor the week on its **quality days** and place the long run where the anchor survives.
For this athlete the long run belongs on **Saturday**: that is where his own history has it (5/02, 5/09,
6/13, 6/20, 10/17 — all Saturday), and it puts 48 h before Monday's quality, which his own data has
already validated (an 18 km Saturday followed two days later by a strong 6 × 1000 m session).

So the shape is **Mon / Wed / Sat hard, four easy days around them, the same every week.**

⚠ **Frame this as the athlete's own pattern, not a spacing rule.** He has explicitly rejected interval
tables (§2). What is being offered is *"this is where your history puts it, and here is why"* — not a
48 h law.

---

## 4. Heart rate is a validator, not a controller

**Pace is the control variable; HR is the validation variable.** Pace decides what you do today; HR
tells you what it cost.

- *During* a session: run to pace, breathing and movement quality. Do not stare at HR.
- *After* a session: compare average HR against past sessions at the same pace and same climate.
- Only a **≥ 5 bpm** deviation at matched pace and matched climate is worth acting on.

**Never let an HR cap define "easy".** This athlete's ≤ 140 bpm easy-running cap produced large amounts
of work at 61–66 % of critical speed — training time spent for almost no return. Removing the cap gave
the same pace at **7–15 bpm lower HR within one week**, at a *higher* dew point.

Keep HR anyway, because pace cannot see cost: identical pace at + 8 bpm is the signal for poor
recovery, sleep debt, illness, or heat. Dropping HR entirely loses that; using it to *steer* loses the
training.

---

## 5. One new variable per week

Adding volume, doubles, and strength training in the same week is the most common overshoot. Sequence:

| Week | Introduce |
|---|---|
| 1 | volume (restore toward the athlete's own historical norm) |
| 2 | a second daily session / doubles |
| 3 | hold — introduce nothing, push what is already there |
| 4 | deload + measure |

**Set volume against the athlete's own history, not against zero.** Restoring dropped volume back to
their own median is not the same as adding new load and should not be treated with new-load caution.
Say which one you are doing.

### The deload week keeps the stimuli — it cuts volume only

**Athlete-supplied structure, and it is the correct one:** *"三周递增负荷，第四周降负荷，但是保留相同的刺激；
然后下个周期负荷再递增。"* (3 weeks loading → deload on the 4th → next cycle loads again.)

**What a deload is allowed to touch: volume. Not intensity, not frequency, not session type.**

| | What it does | Why |
|---|---|---|
| Volume of easy running, long run, **rep counts** | **cut ~30 %** | volume's fatigue is what accumulates fastest and clears slowest; it is also the cheapest thing to lose for one week |
| **Pace / HR targets, number of quality sessions, session types** | **unchanged** | the adaptations are **specific and decay fastest** — cut the quality and the week stops being a deload and becomes detraining |

So the deload table must show both columns at once: quality work drops (e.g. 8.0 → 3.5 km of work)
**while the pace, the number of hard days and the structure of each session stay exactly where they were.**
Say that explicitly, or "降负荷" gets read as "everything down".

**Progression across cycles is a step, not a ramp.** New cycle's **week 1 ≈ previous cycle's week 3** —
the peak the athlete has already held becomes the new floor, and the loading weeks climb from there. That
is what makes it *递增* across cycles rather than a single 4-week bump.

**The athlete has this structure right — do not "improve" it.** Validate it and fill in the mechanism;
that is what turns their structure into something they can adjust on evidence rather than on feel.

---

## 6. Prescribe by pace only when the climate permits

Reuse the dew-point table from `endurance-training-analysis`. Under high dew point, issue an explicit
rule in the plan: convert quality sessions to HR/effort, or move/cancel them. **Do not chase paces.**

Write this rule into the plan itself, not just into the analysis — its whole purpose is to stop the
athlete repeating a summer collapse the next time the weather turns.

### Put the week's key session on the best-condition day, not the fixed weekday

When the climate is the binding constraint, **which weekday the quality session lands on is a
scheduling variable, not a structural one.** Check the multi-day forecast *before* fixing it, and be
willing to swap two adjacent days.

Worked decision: the week's key threshold session sat on Wednesday at dew point **18.1 °C** — the
worst day of the week. The forecast showed a cold front arriving the next day, dropping dew point to
**3.2 °C** (a 15 °C fall in 24 hours, and the first such day of the season).

- **What the swap buys:** at an unchanged cardiovascular cost, dew point 3.2 instead of 18.1 is worth
  roughly **5–6 s/km.** The value of a threshold session is decided by *how fast the athlete can
  actually run it*, so the same session is not the same session on those two days.
- **What it costs:** the gap to the following quality session shrank from 72 h to 48 h. That was
  accepted **because the athlete's own best block already ran on 48 h gaps** — check their history
  before treating a shortened gap as a cost.
- **Move the easy day into the vacated slot**, and say plainly that the easy day must stay easy: the
  swap only works if the recovery day is real.
- **A quality session at a large dew-point drop needs one instruction:** the first set is not a
  target. Let the body meet the new temperature before chasing the window.

**Fallbacks when the good day itself is unusable — decide on the morning, not in advance:**

- **Rain on a rep session → convert to continuous.** Reps on wet roads produce distorted pace data
  with no analytical value, while continuous threshold running is largely insensitive to pace
  precision. Keep the stimulus, drop the measurement that would have been corrupted anyway.
- **Do not defer to a dry day that has strong wind.** Wind hurts short reps more than rain does —
  a 20–22 km/h wind makes 1000 m splits incomparable in a way that 6 mm of rain does not.

Related: the load-accumulation read that justified the swap (matched pace, matched climate, HR up)
lives in `endurance-training-analysis` under the recovery-check section.

---

## 7. Trim before you add

**If an exercise cannot be connected to the athlete's limiting factor or to equipment they actually
have, delete it. Do not invent a vague substitute.** Record the reason so a future session does not
helpfully add it back.

Worked examples from real use:

- **Nordic hamstring curl → deleted.** No ankle fixation available, and its main evidence base is
  *injury prevention* (hamstring/ACL). The athlete had 19 months with zero injury gaps, so the gap it
  addresses did not exist. Cost of finding a fixation point exceeded the benefit.
- **Band-resisted sprint → deleted.** Athlete could only obtain a short mini band — insufficient
  resistance and length. Do not let a purchase list you suggested become a requirement you then
  design around.

Deletion is a real coaching act. Say why it went, in the plan, so it stays gone.

### Tell the athlete, not just the file

A deletion recorded only in the plan document is still an **unexplained gap** from the athlete's side.
When they ask *"why is there no X in my training?"* the honest reading is: **a tradeoff was made and
never stated.**

**This fired twice inside a single session** — first on core training, then again on push-ups. Two
occurrences of the same class, so name it: **a silent omission is indistinguishable from an oversight,
and the athlete cannot tell the difference — which means they cannot audit the judgement.**

The standing rule: **state the tradeoff at the moment you make it**, in the same reply, before the
question is asked. "I have deliberately left X out, here is why, and here is what would change my
mind." One sentence. It costs nothing and it is the difference between a programme the athlete can
reason about and one they can only obey.

Corollary: when the athlete *does* surface the omission, the answer must include the class, not just
the instance — "this is the second time I have done this" is more useful than a defence of the
specific item.

The answer that works, in this order:

1. **Own it** — "you're right, I left it out and I didn't say why."
2. **The judgement, with reasons** — one line each, no hedging.
3. **The evidence that supports it — from *their* data, not the literature.** Worked example (why no
   core training): the case for skipping it was not "the evidence is weak" (that is only an admission
   of ignorance) but that **their own sessions showed no late-session mechanical decay** —
   matched-pace ground-contact time was identical in km 5 and km 14 of a long run, and *shorter* in
   rep 3 than rep 1 of a threshold session. Late-session trunk collapse is precisely where a
   core/stability gap surfaces. It did not surface.
4. **What would change the judgement** — concrete triggers, not "if you feel bad". For core: a
   single-point back/pelvis signal, visible trunk collapse in the last 1–2 km of a 5 k (best seen on
   video), or the *pelvis* wobbling during single-leg work (as opposed to the leg being weak).
5. **Admit the bias if there is one.** "I may under-weight it because the literature is weak —
   *weak evidence* means 'I don't know', not 'it doesn't matter'. If you feel the trunk is the
   limiter, tell me and I'll add it on your report rather than on the papers."

**Second-order point:** single-leg strength work *is* trunk work in the functional sense — split
squats and single-leg RDLs demand exactly the anti-rotation and pelvic control running demands. So the
correct answer to "I have no core training" is often **"you are doing it, in a more specific form"** —
not a defence of the omission.

### "No equipment" is often not a downgrade — check before building a fallback

Before designing a fallback, check what the equipment was actually **for**. In the case studied, the
mini band supplied four accessory items and the rope duplicated something already in the programme.
Three of the four band exercises had **bodyweight equivalents that isolate the target muscle more
directly**. The two highest-value items — pogo hops and single-leg strength — need no equipment at all
beyond a step.

So the honest answer to "what do I do with no equipment?" was **"you don't need it"** — not a
hierarchy of degraded options. Substitution table, plyometric dosing, the quality rule, and where
strength sits in the week: `references/strength-without-a-gym.md`.

### Check the *environment*, not just the equipment list

The same question was asked again for a different muscle group, and the first answer was wrong:
*"the lats and teres major have no zero-equipment solution."* That was **declaring a structural gap
because "equipment" had been defined too narrowly.**

> **A table is a bar. A door handle is a bar. A tree branch is a bar. A park rail is a bar.**
> **Fixed objects are not equipment — they are the environment.**

So before declaring any gap, check the environment for something to pull against, in this order:

1. **Under a table / desk** — inverted row. Real bodyweight load, equals a bar row. The single
   highest-value option and it is in every home.
2. **Park or estate bars, low rails, a thick low tree branch** — the athlete runs outdoors, so these
   are already on the route; two sets on the way home costs no extra trip.
3. **Door handle + towel** — towel looped over a closed door handle, lean back and row.

Only then the pure-ground substitutes (prone straight-arm extension / prone swimmer for the lats;
towel self-resistance row), which are directionally correct but very light — high-rep endurance work,
not loading.

**Long-lever note, which matters for a 181.5 cm athlete:** a 2 kg dumbbell is not 2 kg of stimulus.
With the arms **straight** (dumbbell pullover to the hips, lying down), the moment arm is the whole arm,
so 2 kg produces a torque far larger than its weight suggests. **Judge a load by the lever, not the
number on the dumbbell.** Long limbs are an advantage here if the exercise is chosen to use them.

### Supplementary work that does not compete with running: schedule it, or hook it?

The test is one question — **does the effect depend on *when* you do it?**

| Answer | Category | Examples |
|---|---|---|
| **Depends** | **Must be scheduled** | lower-body plyometrics, stair sprints, quality sessions — the effect depends on nervous-system freshness, and doing them tired trains a slow, deformed version of something else |
| **Does not depend** | **Hang on an existing habit** | upper back, core, mobility — cold is fine, 5 minutes counts, the effect is the same at any hour |

Upper-body and core work therefore **does not need a slot in the plan and does not contend with
running for any resource** (it is not involved in propulsion). One constraint remains: **never to
failure** — upper-back failure degrades arm swing for the next 24–48 h, and core failure degrades
trunk stability for the run.

**But "do it whenever there's time" fails, because there is never time.** Its failure mode is *never
happens*. Attach each item to an event that already occurs, and then stop managing it:

- the minute before going inside after a run
- the gap while water boils or a lift arrives
- the two minutes before bed

**Hooks beat schedules: a schedule depends on the athlete remembering it; a hook does not.**

The split is also *physiologically better*, not just more convenient: postural/endurance qualities are
trained by **repeated touching** — several short returns to the correct position across a day is closer
to the real demand (holding for 45–90 min) than one 10-minute block. Resistance training wants
concentrated stimulus; postural endurance wants frequency.

### When the athlete already owns their strength/core programme — give the interface, not a schedule

Received correction: *"我的力量训练和核心有我自己的安排."* Once the athlete owns that side of the
programme, **stop scheduling it** — and do not keep re-proposing it, which reads as not listening (§10).

What is left is exactly **one** coupling point, and it is worth stating once:

> **Lower-body strength and stair work put DOMS at 24–48 h. Wherever it lands within 48 h before a
> quality day, that quality day degrades** — pace cannot be held, or it is held with worse rep-to-rep
> dispersion.

So write the running week as **fixed points + movable days**: name the quality days, then say explicitly
that the remaining easy days can move to fit his strength placement. That hands him the only constraint
that matters and leaves the arrangement his.

(This is the §7 schedule-or-hook test applied to a whole programme he has already built: the coupling is
real, everything else is his call.)

### Substitution ladder for "no hill available"

1. **Stairs / stadium steps** — usually the best option. Bigger vertical component, shorter ground
   contact, far easier to find than a 10-second hill, and the force direction is closer to racing.
   Protocol: 8–12 s × 8–10 reps, walk down, full recovery. Quality criterion is *fast ground contact
   held across all reps*, not "finishing the set" — stop when the last rep is visibly slower.
2. Band-resisted sprint — needs an anchor point (fence/pole/tree); no partner required.
3. Gentle long slope (3–5 % over 60–100 m), 15–20 s reps.
4. Flat accelerations (20–30 m) — maintenance value only.

Graded specs if a slope is the chosen tool: **5–8 % over 60–100 m for 10–15 s** is the sweet spot;
8–12 % / 40–70 m is more force-dominant; 3–5 % / 100–150 m drifts into an aerobic session; > 15 %
collapses posture and stride. Find one by running 10 s and marking where you stopped.

### Mini bands are activation tools, not resistance

A short loop band cannot load a sprint. Use it for glute-med stability and ankle dorsiflexion
(tibialis anterior matters directly for fast ground contact), in 5 minutes before a strength day, never
inside a quality session.

**It also cannot do anchored work at all** — too short to reach working distance from an anchor, and no
handles. So Pallof press, face pulls and pulldowns are off the table even though "you have a 20 lb band"
sounds like they are available. **A "20 lb band" names both a long tube band (anchored work: yes) and a
short loop band (no) — verify the form, not the rating.** Pull-apart survives but with limited range,
and that is fine: the stimulus comes from **scapular retraction, not from how far the hands travel**.
Substitutions for the capacities a loop band cannot cover:
`references/substitution-dimension-check.md`.

---

## 8. Every prescription needs a check, or it comes back as another question

When the athlete asks an **execution-level** question (what exactly counts as a warm-up, is a cool-down
required, pace or heart rate, which day does strength go), answer with **criteria**: the purpose of the
item, its dose, and the check that tells them it was enough. Slogans like "listen to your body" come
straight back as another question.

See `references/execution-layer-prescriptions.md` for the worked answers — warm-up by session type,
dynamic-drill list and dose, the 3-phase strides recipe, cool-down, strength/quality day placement,
and what to record.

**Keep the recording burden near zero.** The athlete records the session the way they always have;
filtering, segmenting and cleaning is the analyst's job, not a new pre-run decision. Say so explicitly
— "train, and I'll handle the data" removes a real source of friction.

---

## 9. No race on the calendar → manufacture the measurement

Without a race there is no conversion test and no way to know whether the work became performance.
Replace it with a **standardized self-test protocol** — see `references/self-test-protocol.md`.

- Schedule measurement points roughly every 6 weeks so they join into a trend line.
- **Standardize the protocol** or the data points are not comparable and cannot be used to recompute
  model parameters.
- **Explicitly stop the athlete chasing the goal time in a test.** A blown test yields no data point.
  State the realistic target range from current data and say plainly that the requirement is *clean*,
  not *impressive*.
- Say once, plainly, what the athlete loses by never racing (pressure, tactical pacing, competition
  feedback), then design around it and stop raising it.

### Removing the race also removes the reason to hold back

A race calendar is what makes tapering, reserving and sequencing-by-proximity rational. Delete the race
and most of that scaffolding stops being science and becomes **invented constraint**:

| With a race | **No race** |
|---|---|
| maximise performance on one day | **maximise cumulative adaptation rate** |
| peak, then taper | no peak, no taper |
| deload week restores freshness | **deload week lands adaptation** — shallower is fine (−25 % rather than −35 %) |
| phase boundaries set by the calendar | **phase boundaries set by response** |
| slow-adapting qualities can be "saved for later" | **there is no later — nothing may be queued** |

Three things said here had to be withdrawn once the athlete pointed out there was no race: *"measure
this in December"*, *"the base phase doesn't need that precision"*, and *"hold the race-pace band at a
maintenance dose"*. All three were race-calendar reasoning wearing a physiological costume. The last is
worth naming on its own: a maintenance dose is the correct answer **when something must be preserved for
a date**, and the wrong answer when the quality is the slowest-adapting one the athlete owns.

**Phase transitions then need observable criteria**, because nothing else is ticking:

- a pace band is **acquired** when it repeats with low RPE and low rep-to-rep dispersion
- the aerobic side is **stalling** when pace at fixed HR has not moved for 3–4 weeks
- load is **too high** when a deload produces no bounce
- mechanics are **adapted** when ground-contact stops lengthening at matched pace

---

## 10. Stop asking after two answers

If the athlete answers a constraint question twice, redesign around the answer and state the cost once.
A third ask reads as not listening and burns the coaching relationship. Same for repeating a suggestion
inside different framing — "do not nag" is a real requirement here, not politeness.

Applies to equipment too: **accept the answer, give the substitute, move on.** "No gym" → bodyweight +
loaded backpack + stairs. "No hills" → stairs. "No partner" → anchor the band to a fence or just skip
it. "Only a mini band" → activation only. Each of those was answered once and then re-litigated; do not
repeat the mistake.

---

## 11. Close the loop

Every block ends in a measurement. After the test, recompute the model parameters (critical speed / D′,
and efficiency at a reference HR) and update the **athlete model file** — the facts live there, the
methods live in the skills.

Write down explicitly **which previous judgement was overturned** and by what data. Openly retracting
is worth more than staying consistent; quietly revising is the thing that destroys trust. When you
notice you have made the *same class* of error twice (here: turning a description into a target, on
intervals and then on volume), name the pattern — that is what stops the third occurrence.

---

## 12. Diagnose before you prescribe — and do not over-claim the diagnosis

Two identical errors were made in one session, both the same shape: **one measurement treated as a
verdict.** Both were caught by the athlete.

**Error 1 — a composite test reported as a decomposed cause.** Wall angel came back clearly limited and
was written up as *"thoracic extension restriction is the main cause"*. Wall angel loads thoracic
extension, glenohumeral elevation/external rotation **and** scapular upward rotation with posterior tilt
simultaneously. It can only support: *there is a composite restriction; the composition is
undetermined.* **Never name a component of a composite test as the cause.**

**Error 2 — a capacity deficit reported as a pathology.** Pain within seconds of a dead hang was flagged
as a red flag needing professional assessment. What settled it: **only** under that load, **bilateral**,
**no injury history**, quality is *traction* not sharp, absent in every other position. That is the
shoulder girdle not yet able to tolerate bodyweight traction. **"A few seconds" is the tell — fatigue
takes time; a few seconds is load intolerance, not fatigue.** Correct response: keep training what is not
provoked (horizontal pulling needs no overhead position), and build tolerance with a **feet-supported
partial hang**, not by repeating maximal hangs.

**A third, quieter error in the same family:** a *high* test number read as "no problem". 87 s of prone W
hold sounds adequate, but the athlete's qualifier — *"it would drift down if I stopped actively
controlling it"* — turns it into a **control** finding, not an endurance one. Read the qualifier, not just
the number.

Full method — mechanism list with discriminating tests and numeric criteria, decomposition tests, the
capacity-vs-pathology criteria table, and the restraint required on the causal chain:
`references/limitation-diagnosis.md`.

**Keep the causal restraint.** Evidence supports that trunk/upper-body fatigue *may* degrade running
economy, and preliminary evidence links postural work to 5 k improvement. It does **not** support writing
that this athlete's symptom necessarily costs them performance, that a specific movement is the solution,
or that symptom relief *is* competitive improvement.

---

## 13. Stop-loss rules — every one of them points at deleting, not adding

The athlete's own requirement, made explicit. Name the exits before they are needed: the failure mode of
supplementary work is **growth**, not neglect.

- **Capability up, running performance unchanged for 12 weeks** → cut the accessory work to maintenance
  and give the time back to running. It was not the limiter.
- **Symptom better, performance unchanged** → record it as symptom improvement. **Never as competitive
  improvement.**
- **A movement or capacity produces nothing for 8 weeks** → review **movement, dose, assumption and
  priority together** — no fixed order, no default dose increase. **If dose is the first thing you
  reach for, you have presumed the problem is quantity.** Then delete.
- **Capability up, symptom unchanged** → the cause is elsewhere; change the hypothesis, do not add more
  of the same.

**The two questions every 4–8-week review must also ask** — not just "did it get stronger" (it almost
always did, because training does that):

> **Does this capacity still deserve training resource? Is it addressing the actual limiter?**

And **do not put a calendar on anything** — not the equipment ceiling ("enough for N months"), not a
progression timeline. Both are **states**, decided by movement quality, load, RPE and rate of progress.

### Escalation has a horizontal axis, not only a vertical one

Before escalating any movement, ask **whether that capacity is still the limiter.** If it is already
sufficient, **transfer the training capacity to something else** rather than endlessly raising the
difficulty of the same movement. A pure upward "path" drawing implies permanent climbing, and it is the
same error family as a ladder or a lookup table. Move sideways when: capacity sufficient · vertical
blocked by anatomy · adaptation flattened · the movement has nothing left to give · another area has
fallen behind (all pull, no push).

> **Training capacity is finite. How it is allocated matters more than how hard one movement gets.**

**These rules are now a blank row in the athlete's own planning template** — he answers "is this still
the limiter?" himself each week, so the analysis side does not need to restate them weekly. See
`endurance-training-data-analysis`, `references/persistent-log-workbook.md` §2 (记录页 vs 计划页).

Equipment tiers (full / limited / none — all three, always), the mechanical-tension ceilings that say
when bodyweight genuinely runs out, and the **tracks-not-stages** framing: 
`references/progression-tiers-and-stop-rules.md`.

---

## Support files

- `references/limitation-diagnosis.md` — how to find the limiter without over-claiming it: the candidate
  mechanism list with discriminating tests, why a composite test cannot name a cause, the
  capacity-vs-pathology criteria, and the causal-chain restraint.
- `references/progression-tiers-and-stop-rules.md` — full/limited/no-equipment tiers for every capacity,
  substitution-is-not-one-to-one, mechanical-tension ceilings (**stated as states, never as dates**), the
  corrected position on maximal strength, tracks-not-stages, horizontal-vs-vertical escalation, the
  symptom-goal/capability-goal split, and the stop-loss rules.
- `references/self-test-protocol.md` — the standardized time-trial protocol (warm-up, pacing strategy,
  conditions, what to record) plus how to execute a maximal effort alone with no pacer.
- `references/execution-layer-prescriptions.md` — worked criteria for warm-up, dynamic drills, strides,
  cool-down, and where strength/hill work sits in the week.
- `references/strength-without-a-gym.md` — the two stimuli that matter, the zero-equipment set and its
  substitution table, plyometric dose and the quality rule, and why doubles are the *best* strength slot
  rather than an obstacle.
- `references/supplementary-upper-body-core.md` — prescribing upper-body and core work for a runner:
  the negative-goal pitfall, the coordination→strength→strength-endurance→specific chain, the movement
  sets with progression, per-movement compensation cues, and why the goal is never "comprehensive".
- `references/substitution-dimension-check.md` — how to judge whether a substitute is genuinely
  equivalent: the eight stimulus dimensions, three worked substitutions with the gaps each one leaves,
  the two-scheme (A/B) table shape that works, and the fully-bodyweight version of a programme with its
  two irreducible gaps.
