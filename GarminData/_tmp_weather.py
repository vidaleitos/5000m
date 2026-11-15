import json, urllib.request, sys

def get(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")

out = {}
try:
    j = json.loads(get("https://wttr.in/Heze?format=j1"))
    for day in j.get("weather", []):
        d = day["date"]
        print("=" * 60)
        print(d, "min", day.get("mintempC"), "max", day.get("maxtempC"), "avg", day.get("avgtempC"),
              "sunrise", day["astronomy"][0].get("sunrise"), "sunset", day["astronomy"][0].get("sunset"))
        for h in day["hourly"]:
            t = int(h["time"]) // 100
            if t in (5, 6, 7, 8, 12, 18, 20, 21):
                print("   ", f"{t:02d}:00", "temp", h["tempC"], "feels", h["FeelsLikeC"], "hum", h["humidity"],
                      "dew", h["DewPointC"], "wind", h["windspeedKmph"], "rain%", h["chanceofrain"],
                      h["weatherDesc"][0]["value"])
except Exception as e:
    print("WTHR FAIL", e)
