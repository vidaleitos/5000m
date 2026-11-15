#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
new_data FIT 解析器 —— 每日增量数据处理工具（2026-08-23 起）
用法：把 FIT 文件放进 D:\\running\\GarminData\\Data\\new_data，
     然后运行: python parse_new_data.py
输出：每个 FIT 旁边生成 <文件名>.fit_parsed.json（已解析的自动跳过）。
依赖：pip install fitparse（如报 ImportError 请先安装）
"""
import os
import json
import glob

DATA_DIR = r"D:\running\GarminData\Data\new_data"

RECORD_KEEP = ['timestamp', 'heart_rate', 'enhanced_speed', 'speed', 'cadence',
               'temperature', 'enhanced_altitude', 'distance', 'power',
               'stance_time', 'vertical_oscillation', 'vertical_ratio']
EVENT_KEEP = ['timestamp', 'event', 'event_type', 'event_group', 'timer_trigger']


def parse_fit(fp):
    import fitparse
    ff = fitparse.FitFile(fp)
    out = {
        "file": os.path.basename(fp),
        "session": [],
        "laps": [],
        "records": [],
        "events": [],
        "workout_steps": [],
    }
    for msg in ff.get_messages():
        name = msg.name
        data = {}
        for d in msg:
            if d.value is None:
                continue
            v = d.value
            if isinstance(v, bytes):
                continue
            if hasattr(v, 'isoformat'):
                v = v.isoformat()
            data[d.name] = v

        if name == 'session':
            out['session'].append(data)
        elif name == 'lap':
            out['laps'].append(data)
        elif name == 'record':
            out['records'].append({k: data[k] for k in RECORD_KEEP if k in data})
        elif name == 'event':
            out['events'].append({k: data[k] for k in EVENT_KEEP if k in data})
        elif name == 'workout_step':
            out['workout_steps'].append(data)
    return out


def main():
    # 支持两种放法：直接放 new_data/*.fit，或放 new_data/<activityId>/*.fit
    fits = sorted(glob.glob(os.path.join(DATA_DIR, '*.fit'))) + \
           sorted(glob.glob(os.path.join(DATA_DIR, '*', '*.fit')))
    print("=" * 50)
    print(f"new_data 目录找到 {len(fits)} 个 FIT 文件")
    print("=" * 50)
    for fp in fits:
        out_fp = fp + '_parsed.json'
        if os.path.exists(out_fp):
            print(f"跳过(已解析): {os.path.basename(fp)}")
            continue
        print(f"解析中: {os.path.basename(fp)} ...")
        try:
            result = parse_fit(fp)
        except Exception as e:
            print(f"  错误: {e}")
            continue
        with open(out_fp, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=1)
        n_laps = len(result['laps'])
        print(f"  完成 -> {os.path.basename(out_fp)}"
              f" | records={len(result['records'])} laps={n_laps}"
              f" events={len(result['events'])}")
    print("完成。把生成的 _parsed.json 内容告诉教练即可。")


if __name__ == '__main__':
    main()
