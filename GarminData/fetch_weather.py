import json, os, urllib.request, datetime as dt, csv, time
root = "D:/running/GarminData/Data"
OUT = "D:/running/GarminData/sessions_weather.csv"

S = []
for a in json.load(open(root + "/DI_CONNECT/DI-Connect-Fitness/hheu010@gmail.com_1_summarizedActivities.json", encoding="utf-8"))[0]["summarizedActivitiesExport"]:
    if a.get("activityType") != "running":
        continue
    S.append(dict(t=dt.datetime.utcfromtimestamp(a["startTimeLocal"] / 1000), km=a["distance"] / 100000,
                  mn=a["duration"] / 60000, hr=a.get("avgHr"), mx=a.get("maxHr"),
                  loc=a.get("locationName") or "Heze", name=a.get("name")))
for d in sorted(os.listdir(root + "/new_data")):
    fp = f"{root}/new_data/{d}/{d}_ACTIVITY.fit_parsed.json"
    if not os.path.exists(fp):
        continue
    s = json.load(open(fp, encoding="utf-8"))["session"][0]
    t = dt.datetime.fromisoformat(s["start_time"]) + dt.timedelta(hours=8)
    if any(abs((t - x["t"]).total_seconds()) < 900 for x in S):
        continue
    S.append(dict(t=t, km=(s.get("total_distance") or 0) / 1000, mn=(s.get("total_timer_time") or 0) / 60,
                  hr=s.get("avg_heart_rate"), mx=s.get("max_heart_rate"), loc="Heze", name=s.get("name")))
S.sort(key=lambda x: x["t"])
print("sessions:", len(S), flush=True)

LOC = {"Heze": (35.0041, 115.1825), "Weifang": (36.6607, 119.0263)}
CACHE = {}
CF = "D:/running/GarminData/_wx_cache.json"
if os.path.exists(CF):
    CACHE = json.load(open(CF, encoding="utf-8"))


def fetch(lat, lon, sd, ed, tag):
    url = (f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}"
           f"&start_date={sd}&end_date={ed}"
           f"&hourly=temperature_2m,relative_humidity_2m,dew_point_2m,apparent_temperature"
           f"&timezone=Asia%2FShanghai")
    for attempt in range(4):
        try:
            r = json.loads(urllib.request.urlopen(url, timeout=90).read().decode())
            return {tm: [r["hourly"]["temperature_2m"][i], r["hourly"]["relative_humidity_2m"][i],
                         r["hourly"]["dew_point_2m"][i], r["hourly"]["apparent_temperature"][i]]
                    for i, tm in enumerate(r["hourly"]["time"])}
        except Exception as e:
            print("  retry", tag, attempt, repr(e)[:90], flush=True)
            time.sleep(3)
    return {}


months = sorted({x["t"].strftime("%Y-%m") for x in S})
for mo in months:
    y, m = map(int, mo.split("-"))
    nd = (dt.date(y + (m == 12), (m % 12) + 1, 1) - dt.timedelta(days=1)).day
    ed = dt.date(y, m, nd)
    if ed > dt.date(2026, 9, 21):
        ed = dt.date(2026, 9, 21)
    for loc in ["Weifang", "Heze"]:
        key = f"{loc}|{mo}"
        if key in CACHE:
            continue
        lat, lon = LOC[loc]
        res = fetch(lat, lon, f"{y}-{m:02d}-01", ed.strftime("%Y-%m-%d"), key)
        if res:
            CACHE[key] = res
            json.dump(CACHE, open(CF, "w"))
        print("  fetched", key, len(res), flush=True)

rows = []
miss = 0
for x in S:
    hh = x["t"].replace(minute=0, second=0, microsecond=0)
    res = CACHE.get(f'{x["loc"]}|{x["t"]:%Y-%m}', {})
    v = res.get(hh.strftime("%Y-%m-%dT%H:%M"))
    if not v:
        miss += 1
        continue
    pace = 60 / (x["km"] / (x["mn"] / 60)) if x["km"] and x["mn"] else ""
    rows.append(dict(t=x["t"].strftime("%Y-%m-%d %H:%M"), mo=x["t"].strftime("%Y-%m"),
                     dow=x["t"].strftime("%a"), km=round(x["km"], 2), min=round(x["mn"], 1),
                     pace=round(pace, 3) if pace else "", hr=x["hr"], mx=x["mx"],
                     T=v[0], RH=v[1], DP=v[2], AT=v[3], loc=x["loc"], name=x["name"]))

with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print("WROTE", OUT, "rows", len(rows), "missed", miss, flush=True)
