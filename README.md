# 5000m

> **一个 5000 米项目的全部 —— 从原始数据到判断依据。**
> *Everything behind a 5000 m project — from raw data to the reasoning that sits on top of it.*
> *Todo lo que hay detrás de un proyecto de 5000 m: desde los datos en bruto hasta el razonamiento que se construye sobre ellos.*

---

## 中文

这不是一份训练日志的备份，而是一个运动员训练过程的完整工作档案：

- **原始数据** —— Garmin FIT 文件与 DI_CONNECT 全量导出（GPS 轨迹、心率、步频、触地时间、垂直振荡、垂直比）。
- **训练日志** —— 按训练周期整理的 xlsx 工作簿。
- **周期计划** —— 每个训练块的课表、配速锚点，以及每一条锚点背后的证据。
- **教练技能** —— 分析框架：阈值测试、耐久性判读、热适应匹配、跨周期比较、无器械力量方案。
- **运动员模型** —— 当前能力结构、限制因素，以及已经被数据推翻的旧判断。

**目标** 18:33 → 17 分 → 16 分台

**原则** 配速由测量驱动，不由日历驱动；每个判断都带置信度；被推翻的判断留在记录里，不删。

---

## English

This is not a backup of a training log. It is the complete working archive of one athlete's build:

- **Raw data** — Garmin FIT files and a full DI_CONNECT export (GPS, heart rate, cadence, ground contact time, vertical oscillation, vertical ratio).
- **Training log** — a workbook organised by training block.
- **Block plans** — the sessions, the pace anchors, and the evidence behind every anchor.
- **Coaching skills** — analysis frameworks for threshold testing, durability, heat-adjusted comparison, period comparison, and strength work without a gym.
- **Athlete model** — the current capability profile, the limiting factor, and the judgements that data has already overturned.

**Target** 18:33 → sub-17 → sub-16

**Principle** Paces are driven by measurement, not by the calendar; every judgement carries a confidence level; overturned judgements stay in the record instead of being deleted.

---

## Español

Esto no es la copia de seguridad de un diario de entrenamiento. Es el archivo de trabajo completo de la progresión de un atleta:

- **Datos en bruto** — archivos FIT de Garmin y una exportación completa de DI_CONNECT (GPS, frecuencia cardíaca, cadencia, tiempo de contacto con el suelo, oscilación vertical, ratio vertical).
- **Diario de entrenamiento** — un libro de trabajo organizado por bloques.
- **Planes de bloque** — las sesiones, las referencias de ritmo y la evidencia detrás de cada una.
- **Habilidades de entrenador** — marcos de análisis para tests de umbral, durabilidad, comparación ajustada por calor, comparación entre períodos y trabajo de fuerza sin gimnasio.
- **Modelo del atleta** — el perfil actual de capacidades, el factor limitante y los juicios que los datos ya han revertido.

**Objetivo** 18:33 → por debajo de 17 → por debajo de 16

**Principio** Los ritmos los marca la medición, no el calendario; cada juicio lleva su nivel de confianza; los juicios revertidos se quedan en el registro en lugar de borrarse.

---

## 目录 / Structure / Estructura

| 路径 | 内容 / Contents / Contenido |
|---|---|
| `GarminData/` | 脚本、分析页、计划、FIT 原始数据 |
| `GarminData/Data/` | Garmin DI_CONNECT 导出与增量 FIT |
| `old/` | 2025–2026 旧训练营计划（PDF，9 期） |
| `hermes/skills/coaching/` | 教练技能：分析／数据／复盘／块设计 |
| `hermes/skills/garmin-mcp*` | Garmin MCP 接入与配置 |
| `hermes/memories/` | MEMORY.md / USER.md 快照 |
| `logs/` | 训练日志 xlsx |

## 关键文件 / Key files

- `GarminData/PLAN_2026-11-13_v3.md` — 当前计划（v3）
- `GarminData/ATHLETE_MODEL.md` — 运动员模型
- `GarminData/build_log.py` — 训练日志构建工具

## 不备份 / Excluded

`*.epub`（书籍）、`pip-cache/`、`.obsidian/`、凭据与会话令牌（`.gitignore` 已排除）。

> ⚠️ 含 GPS 轨迹与健康数据 —— **仓库必须保持 private**。

## 更新 / Update

```bash
cd /d/running
git add -A
git commit -m "update: YYYY-MM-DD"
git push
```
