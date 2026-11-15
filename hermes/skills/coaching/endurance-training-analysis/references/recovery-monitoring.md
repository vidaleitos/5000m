# Recovery monitoring from wearable data

How to read sleep / HRV / load-balance out of a Garmin (or equivalent) export, and — more
importantly — what each field can and cannot support.

This exists because a standing assumption ("sleep is not a constraint") survived many sessions
**on self-report alone**, and was wrong when finally measured. See the SKILL.md section on
"measured data vs the athlete's report".

---

## What to pull, and what each field is worth

| field | source | confidence | use for |
|---|---|---|---|
| **sleep duration** | nightly | **high** — consistent across nights | the ceiling on how fast volume may rise |
| **time in bed** | duration + awake | high | the actual intervention target |
| **sleep score** | nightly composite | **medium** — algorithm-weighted | trend across weeks only |
| **REM / deep split** | staging | **low–medium** — movement-sensitive | flag only, never a verdict |
| **HRV (last night, weekly avg, baseline band)** | nightly | **high** for acute load | is the athlete coping *right now* |
| **HRV status (balanced / unbalanced)** | derived | high | permission to load, not a limit on volume |
| **training-load balance (aerobicLow / aerobicHigh / anaerobic)** | weekly | medium | independent check on *where* the load sits |
| **VO2max** | rolling estimate | medium | long-run trend only |
| **race predictions** | model | **low** — systematically optimistic | trend / sanity bound only |
| **training readiness** | derived | often simply absent | do not build on it |

**"Returns empty" is a normal outcome.** Several derived Garmin fields come back as `[]` regardless
of auth. Treat an empty array as *no data*, never as a zero or a bad reading, and do not retry-loop.

---

## The reading rules

### 1. Duration is the load-bearing number; staging is decoration

Duration reproduces across nights and survives a loose watch. Sleep score and REM/deep splits do not
— movement and wear position both distort them. A single night at "REM 0" is weak evidence; **eight
nights at REM 0–0.58 h against a normal ~1.5 h is a pattern.** Count nights before concluding.

### 2. Sleep architecture and HRV answer different questions — report both

```
sleep 4.2-5.5 h, score 40-44        -> recovery DEPTH is short
HRV 74 vs baseline 52-79, BALANCED  -> autonomic load is being HANDLED
```

Both are true. The summary is **"autonomic load is being handled; recovery depth is not"**. Collapsing
that into "recovery is broken" over-corrects the plan; collapsing it into "HRV is fine" ignores the
ceiling. Neither is a licence to keep loading without saying what the ceiling is.

### 3. Convert "sleep more" into arithmetic the athlete can act on

```
4.18 h asleep + 1.82 h awake  =  ~6.0 h in bed
7.0 h asleep target           ->  ~8.0 h in bed
```

That is an instruction ("in bed by X"). "Sleep more" is not — it comes straight back as another
question. **Check time-in-bed before assuming insomnia**; in the case studied the athlete fell asleep
quickly and simply did not put himself in bed.

### 4. Load balance tells you *where* the load sits, not how much

```
aerobicLow 1216 / aerobicHigh 1933 / anaerobic 342
```

High-aerobic dominating low-aerobic is the wearable's version of **"quality-heavy, easy-thin"** —
the same diagnosis the pace-band histogram reaches from entirely different data. When two unrelated
sources agree, say so explicitly; that is what converts an analysis into a finding.

### 5. Race predictions are a trend, never an absolute

Observed: watch predicted **18:15** for 5 km while the derived training band implied **18:45–19:10**,
and the athlete's own profile history showed the widget running 60–70 s optimistic across a season.
Quote it with the direction of its bias, use the gap as a *statement about uncertainty*, and never
feed it into a pace prescription.

---

## When measured recovery contradicts the plan

The failure mode is not "ignored the data" — it is **having planned the ramp in weeks instead of in
recovery capacity**, because no recovery data existed. When it appears:

1. **Say the plan was built on an assumption and that the assumption is now failing** — in writing.
2. **Keep the session types, cut the growth rate.** The stimuli (threshold, race pace, long run,
   neuromuscular) are unchanged; what changes is how fast the volume around them may expand.
3. **Let a low-readiness day change the session *type*, not delete the session.** A max-velocity test
   on a 44-score, REM-0 night produces a low number that then gets misread as "his speed is poor".
   Postpone it to a ≥65-score morning rather than replacing it with nothing.
4. **A lower-bound reading is worse than no reading** when the reading's whole purpose is to decide
   where to spend training budget. It does not merely fail to inform — it misinforms in a specific
   direction.

## Where the data comes from

Prefer an MCP/data source over manual export — it makes recovery a **daily** input instead of a
periodic archaeology exercise. A manual export also stops at whatever date it was downloaded, which
is often exactly the window you need.

**A package built for a different agent framework is still usable if it ships a stdio MCP entry
point.** Working example: a Garmin plugin written for another harness exposes
`bin: { garmin-connect-mcp: lib/mcp.js, garmin-connect-auth: lib/auth-cli.js }` — the host agent
neither knows nor cares what framework it was written for.

```bash
npm install -g <pkg>
hermes mcp add garmin --command garmin-connect-mcp --env GARMIN_USERNAME=<email>
hermes mcp show garmin          # confirms registration
```

Three things cost real time and are worth knowing in advance:

1. **Auth needs a TTY.** A browser-session auth CLI started from a plain foreground call exits with
   *"Interactive authentication requires a local terminal (TTY)"*. Run it as a **pty-backed background
   process**. It opens the system browser; the athlete types the password there and the CLI reports
   `credentials_collected_by_cli=username-only`. **Never accept or relay a password.**
2. **`hermes mcp add` reports `Failed to connect: Connection closed` before auth exists** — answer `y`
   to save anyway. If the server's own startup error is `Fatal error: <ENV_VAR> is required`, that is
   a missing environment variable, not a broken install.
3. **Verify with a live tool call, not with `hermes mcp list`.** `enabled` only proves the config was
   written. And when scripting the handshake, **do not use `subprocess.run(input=...)`** — it closes
   stdin, the server shuts down mid-session-restore, and you get a successful `initialize` followed by
   silence that looks exactly like a hang. Use `Popen` with stdout on a reader thread and a deadline.
   Success reads `✅ Connected successfully.` followed by real JSON. **Tools only appear in a new chat
   session** — the tool list is built at startup, so say that to the athlete explicitly.

### Region / account selection

Where a provider splits platforms (Garmin global vs `garmin.cn`), **derive the region from the
athlete's own data instead of asking.** The export's social profile carries `profileImageUrlLarge`,
and its host names the platform — `garmin-connect-prod` ⇒ global. A wrong guess is harmless (it just
fails to find the account) but reading it saves a round trip, and it also confirms which account the
data you have been analysing actually belongs to.
