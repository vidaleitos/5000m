import os, json, glob, fitparse
DATA_DIR = r"D:\running\GarminData\Data\new_data"
RECORD_KEEP = ['timestamp','heart_rate','enhanced_speed','speed','cadence','temperature',
               'enhanced_altitude','distance','power','stance_time','vertical_oscillation','vertical_ratio']
EVENT_KEEP = ['timestamp','event','event_type','event_group','timer_trigger']

def parse_fit(fp):
    ff = fitparse.FitFile(fp)
    out = {"file": os.path.basename(fp), "session": [], "laps": [], "records": [], "events": [], "workout_steps": []}
    for msg in ff.get_messages():
        name = msg.name
        data = {}
        for d in msg:
            if d.value is None: continue
            v = d.value
            if isinstance(v, bytes): continue
            if hasattr(v, 'isoformat'): v = v.isoformat()
            data[d.name] = v
        if name == 'session': out['session'].append(data)
        elif name == 'lap': out['laps'].append(data)
        elif name == 'record': out['records'].append({k: data[k] for k in RECORD_KEEP if k in data})
        elif name == 'event': out['events'].append({k: data[k] for k in EVENT_KEEP if k in data})
        elif name == 'workout_step': out['workout_steps'].append(data)
    return out

files = sorted(glob.glob(os.path.join(DATA_DIR, "*", "*.fit"))) + sorted(glob.glob(os.path.join(DATA_DIR, "*.fit")))
print("found", len(files), "fit files")
for fp in files:
    outp = fp + "_parsed.json"
    if os.path.exists(outp):
        continue
    try:
        r = parse_fit(fp)
    except Exception as e:
        print("ERR", os.path.basename(fp), e); continue
    json.dump(r, open(outp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print("parsed", os.path.basename(outp), "laps", len(r['laps']), "records", len(r['records']))
