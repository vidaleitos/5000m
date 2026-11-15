# Pulling Garmin data — harness, sources and field notes

Companion to the *Units and field traps* section. That section lists what goes wrong; this one is how
to get the data in the first place.

## 1. When the native MCP tools are not in the session

An MCP server registered with the agent is sometimes not loaded into the current session's toolset.
The server still works — call it directly over **stdio JSON-RPC** from `execute_code`. Reusable
skeleton:

```python
import subprocess, json, os, threading, time, queue

env = dict(os.environ)
env["GARMIN_USERNAME"] = "<account email>"
CMD = [r"C:\Users\<user>\AppData\Local\hermes\node\<server>.cmd"]

p = subprocess.Popen(CMD, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE, text=True, env=env, bufsize=1, shell=True)
q = queue.Queue()
threading.Thread(target=lambda: [q.put(l) for l in p.stdout], daemon=True).start()

def send(m):
    p.stdin.write(json.dumps(m) + "\n"); p.stdin.flush()

def wait_for(mid, timeout=120):
    t0 = time.time()
    while time.time() - t0 < timeout:
        try: l = q.get(timeout=2)
        except queue.Empty: continue
        l = l.strip()
        if not l.startswith("{"): continue          # skip banner/log noise
        try: d = json.loads(l)
        except Exception: continue
        if d.get("id") == mid: return d
    return None

send({"jsonrpc":"2.0","id":1,"method":"initialize","params":{
    "protocolVersion":"2024-11-05","capabilities":{},
    "clientInfo":{"name":"v","version":"1"}}})
wait_for(1)
send({"jsonrpc":"2.0","method":"notifications/initialized"})

def call(mid, name, args):
    send({"jsonrpc":"2.0","id":mid,"method":"tools/call",
          "params":{"name":name,"arguments":args}})
    d = wait_for(mid, 180)
    if not d or d.get("error"): return None
    c = d.get("result", {}).get("content", [])
    t = c[0].get("text", "") if c else ""
    try: return json.loads(t)
    except Exception: return t
```

Points that matter:

- **Read by `id`, not by line order.** stderr/log lines and warnings interleave on stdout; filter to
  lines that parse as JSON and match the request id.
- **Thread the reader.** A blocking `readline()` on a slow tool call deadlocks the whole cell.
- **Close stdin and terminate** at the end of the cell — otherwise orphan processes accumulate.
- Discover a tool's real schema with the client's `tool_describe` rather than guessing parameter
  names; guessing produced a wasted round-trip on `download` (it wants `GARMIN_FIT_DOWNLOAD_DIR` set
  in the environment, not a path argument).

## 2. Which source answers which question

| question | source | why |
|---|---|---|
| latest session summary, peak speed, power, running dynamics | activity list (`detail="full"`) | carries fields the FIT lap summary does not |
| **per-km / per-lap splits** | **FIT records** | the API's `splitSummaries` is whole-activity only |
| multi-year history, cross-period comparison | the offline `summarizedActivities*.json` export | one read, no pagination, ~540 activities |
| weather | Open-Meteo (see the climate section) | the watch's own temperature field is unusable |

## 3. Downloading a FIT through MCP

The download tool refuses to run unless a **trusted parent directory** is configured by environment
variable, and it isolates output under a per-region/per-account subfolder:

```python
env["GARMIN_FIT_DOWNLOAD_DIR"] = r"D:\running\GarminData\Data\new_data"
# -> D:\...\new_data\GARMIN_FIT_<region>_<account-email>\<activityId>.fit
```

The response is metadata only (`success`, `activityId`, `fileName`, `sizeBytes`, `sha256`) — **no local
path**, so glob for the file. Set the env var on your own subprocess; no client-config edit is needed.

## 4. FIT record field notes

Observed on a Garmin `record` stream for a 20 km run:

| field | note |
|---|---|
| `distance` | metres, cumulative — derive per-km splits from this plus `timestamp` |
| `enhanced_speed` | m/s, 1 Hz |
| `cadence` | **per-leg** — double it for steps/min (matched the session summary exactly) |
| `heart_rate` | bpm |
| `vertical_ratio` | derived from speed; still usable as a *relative* within-session series |
| `ground_contact_time` | **absent from the record stream** — session/lap summary only |

1 Hz sampling means a reported `maxSpeed` is a **1-second average**; an instantaneous peak is higher.
Do not treat it as the true ceiling, and do not compare it against a value derived from lap averages.

## 5. Building per-km splits from records

Cross each whole kilometre, take the segment either side of the crossing, and report time-at-crossing
(not a fixed 60-sample window) — the latter misallocates time whenever a record is dropped.

```python
marks = [0.0] + [float(k) for k in range(1, int(total_km) + 1)] + [total_km]
for a, b in zip(marks, marks[1:]):
    seg = [p for p in pts if a <= p["km"] <= b]
    if len(seg) < 2: continue
    dt = seg[-1]["t"] - seg[0]["t"]; dk = seg[-1]["km"] - seg[0]["km"]
    if dk <= 0: continue
    pace = dt / dk      # s/km
```

Sanity-check the result against the session summary's distance, duration and average pace before
interpreting anything — a 2 % mismatch means the distance offset was taken from the wrong record.

## 6. Security

Session tokens live in a per-account file under the plugin's own app-data directory and contain
**hashes, not plaintext** (`usernameHash`, `profileIdHash`). Never print the token blob, and never put
a password or one-time code through the terminal — authenticate through the official page in a browser
and let the CLI persist the session.
