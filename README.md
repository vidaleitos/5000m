# Fajir — 5000m 训练数据与教练资料

私人备份仓库。**含 GPS 轨迹与健康数据，必须保持 private。**

## 目录

| 路径 | 内容 |
|---|---|
| `GarminData/` | 脚本、分析页、计划、FIT 原始数据 |
| `GarminData/Data/` | Garmin 导出（DI_CONNECT）与增量 FIT |
| `old/` | 2025–2026 旧训练营计划（PDF，9 期） |
| `hermes/skills/coaching/` | 教练技能：分析、数据、复盘中、块设计 |
| `hermes/skills/garmin-mcp*` | Garmin MCP 接入与配置 |
| `hermes/memories/` | MEMORY.md / USER.md 快照 |
| `logs/` | 训练日志 xlsx |

## 关键文件

- `GarminData/PLAN_2026-11-13_v3.md` — 当前计划（v3）
- `GarminData/build_log.py` — 训练日志构建工具
- `GarminData/ATHLETE_MODEL.md` — 运动员模型

## 不备份

`*.epub`（书籍）、`pip-cache/`、`.obsidian/`、凭据与会话令牌（`.gitignore` 已排除）。

## 更新

```bash
cd /d/running
git add -A
git commit -m "update: YYYY-MM-DD"
git push
```
