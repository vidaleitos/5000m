#!/usr/bin/env python3
"""Match every training session to REAL hourly weather (Open-Meteo historical reanalysis).

Why: body-worn temperature sensors are skin-heat contaminated and useless across seasons
(the same watch read 23 C for runs that were actually 0 C). Fetch real weather instead.

Usage:
    python fetch_weather.py                     # uses CONFIG below
    python fetch_weather.py sessions.csv out.csv     # sessions from a CSV

If no input CSV is given, builds the session list from a Garmin export using
`load_garmin_export()` -- edit SESSIONS_JSON / NEW_DATA_DIR / LOCATIONS for your export.

Output columns: t, mo, dow, km, min, pace, hr, mx, T, RH, DP, AT, loc
  T/RH/DP/AT = real air temp, relative humidity, dew point, apparent temp at the
  nearest whole hour to session start (local time).

Notes
-----
* Free, no API key. Archive lags a few days -- never request future dates (400 error).
* Requests are cached per (location, month) in _wx_cache.json so reruns are cheap.
  Large multi-year requests DO time out; fetch month-by-month as done here.
* SSL/EOF errors on this endpoint are normal and transient -- the retry loop handles them.
"""
import csv
import datetime as dt
import json
import os
import sys
import time
import urllib.request

# ---------------------------------------------------------------- CONFIG
LOCATIONS = {
    "Heze": (35.0041, 115.1825),
    "Weifang": (36.6607, 119.0263),
}
TIMEZONE = "Asia/Shanghai"

SESSIONS_JSON = (r"D:/running/GarminData/Data/DI_CONNECT/DI-Connect-Fitness/"
                 r"hheu010@gmail.com_1_summarizedActivities.json")
NEW_DATA_DIR = r"D:/running/GarminData/Data/new_data"
CACHE_FILE = "_wx_cache.json"
DEFAULT_OUT = "sessions_weather.csv"
# -----------------------------------------------------------------------


def load_garmin_export():
    """Return [{t(local datetime), km, mn, hr, mx, loc, name}].

    UNIT TRAPS (see skill SKILL.md):
      * summarizedActivities distance is CENTIMETRES, duration is MILLISECONDS
      * summarizedActivities startTimeLocal is ALREADY local-as-epoch -> do NOT add offset
      * parsed per-activity start_time is TRUE UTC -> DO add the local offset
    """
    sessions = []
    if os.path.exists(SESSIONS_JSON):
        blob = json.load(open(SESSIONS_JSON, encoding="utf-8"))[0]
        for a in blob.get("summarizedActivitiesExport", []):
            if a.get("activityType") != "running":
                continue
            sessions.append(dict(
                t=dt.datetime.utcfromtimestamp(a["startTimeLocal"] / 1000),
                km=a["distance"] / 100000.0,
                mn=a["duration"] / 60000.0,
                hr=a.get("avgHr"), mx=a.get("maxHr"),
                loc=a.get("locationName") or "Heze",
                name=a.get("name"),
            ))

    if os.path.isdir(NEW_DATA_DIR):
        for d in sorted(os.listdir(NEW_DATA_DIR)):
            fp = os.path.join(NEW_DATA_DIR, d, f"{d}_ACTIVITY.fit_parsed.json")
            if not os.path.exists(fp):
                continue
            sess = json.load(open(fp, encoding="utf-8"))["session"][0]
            t = dt.datetime.fromisoformat(sess["start_time"]) + dt.timedelta(hours=8)
            if any(abs((t - x["t"]).total_seconds()) < 900 for x in sessions):
                continue  # dedupe overlapping exports
            sessions.append(dict(
                t=t, km=(sess.get("total_distance") or 0) / 1000.0,
                mn=(sess.get("total_timer_time") or 0) / 60.0,
                hr=sess.get("avg_heart_rate"), mx=sess.get("max_heart_rate"),
                loc="Heze", name=sess.get("name"),
            ))
    sessions.sort(key=lambda x: x["t"])
    return sessions


def load_session_csv(path):
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    out = []
    for r in rows:
        out.append(dict(
            t=dt.datetime.fromisoformat(r["t"] if "T" in r["t"] else r["t"].replace(" ", "T")),
            km=float(r["km"]), mn=float(r.get("min") or 0),
            hr=float(r["hr"]) if r.get("hr") else None,
            mx=float(r["mx"]) if r.get("mx") else None,
            loc=r.get("loc") or next(iter(LOCATIONS)),
            name=r.get("name"),
        ))
    return out


def fetch(lat, lon, sd, ed, tag, attempts=4):
    url = (f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}"
           f"&start_date={sd}&end_date={ed}"
           f"&hourly=temperature_2m,relative_humidity_2m,dew_point_2m,apparent_temperature"
           f"&timezone={TIMEZONE}")
    for i in range(attempts):
        try:
            r = json.loads(urllib.request.urlopen(url, timeout=90).read().decode())
            h = r["hourly"]
            return {tm: [h["temperature_2m"][j], h["relative_humidity_2m"][j],
                         h["dew_point_2m"][j], h["apparent_temperature"][j]]
                    for j, tm in enumerate(h["time"])}
        except Exception as e:                       # noqa: BLE001 - transient SSL/EOF
            print(f"  retry {tag} {i} {e!r:.80}", flush=True)
            time.sleep(3)
    print(f"  FAILED {tag}", flush=True)
    return {}


def build_weather_cache(sessions):
    cache = json.load(open(CACHE_FILE, encoding="utf-8")) if os.path.exists(CACHE_FILE) else {}
    today = dt.date.today()
    for mo in sorted({x["t"].strftime("%Y-%m") for x in sessions}):
        y, m = map(int, mo.split("-"))
        last = (dt.date(y + (m == 12), (m % 12) + 1, 1) - dt.timedelta(days=1))
        last = min(last, today - dt.timedelta(days=1))   # archive lags; future dates -> HTTP 400
        for loc in {x["loc"] for x in sessions}:
            key = f"{loc}|{mo}"
            if key in cache or loc not in LOCATIONS:
                continue
            lat, lon = LOCATIONS[loc]
            res = fetch(lat, lon, f"{y}-{m:02d}-01", last.strftime("%Y-%m-%d"), key)
            if res:
                cache[key] = res
                json.dump(cache, open(CACHE_FILE, "w"))
            print(f"  fetched {key} {len(res)}", flush=True)
    return cache


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else None
    out = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUT
    sessions = load_session_csv(src) if src else load_garmin_export()
    print(f"sessions: {len(sessions)}", flush=True)
    cache = build_weather_cache(sessions)

    rows, missed = [], 0
    for x in sessions:
        hh = x["t"].replace(minute=0, second=0, microsecond=0)
        w = cache.get(f'{x["loc"]}|{x["t"]:%Y-%m}', {}).get(hh.strftime("%Y-%m-%dT%H:%M"))
        if not w:
            missed += 1
            continue
        pace = 60 / (x["km"] / (x["mn"] / 60)) if x["km"] and x["mn"] else ""
        rows.append(dict(t=x["t"].strftime("%Y-%m-%d %H:%M"), mo=x["t"].strftime("%Y-%m"),
                         dow=x["t"].strftime("%a"), km=round(x["km"], 2), min=round(x["mn"], 1),
                         pace=round(pace, 3) if pace else "", hr=x["hr"], mx=x["mx"],
                         T=w[0], RH=w[1], DP=w[2], AT=w[3], loc=x["loc"], name=x.get("name")))
    if not rows:
        print("no rows matched - nothing written")
        return
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"WROTE {out} rows={len(rows)} missed={missed}")


if __name__ == "__main__":
    main()
