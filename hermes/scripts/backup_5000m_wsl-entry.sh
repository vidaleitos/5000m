#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# cron 入口（在 WSL 里运行）
# Hermes gateway 跑在 WSL2 Ubuntu，而 git / SSH key 在 Windows 侧，
# 所以这里只做一件事：找到 Windows 的 git-bash，把真正的脚本交给它。
# 真正的逻辑：D:/running/hermes/scripts/backup_5000m.sh（已纳入仓库版本管理）
# ─────────────────────────────────────────────────────────────
set -u

TARGET="D:/running/hermes/scripts/backup_5000m.sh"
GB=""

for c in \
  /mnt/d/apps/Git/usr/bin/bash.exe \
  /mnt/d/apps/Git/bin/bash.exe \
  "/mnt/c/Program Files/Git/bin/bash.exe" \
  "/mnt/c/Program Files/Git/usr/bin/bash.exe"
do
  if [ -x "$c" ]; then GB="$c"; break; fi
done

if [ -z "$GB" ]; then
  echo "❌ 5000m 备份：在 WSL 里找不到 Windows git-bash"
  echo "   试过：/mnt/d/apps/Git/usr/bin/bash.exe、/mnt/d/apps/Git/bin/bash.exe、/mnt/c/Program Files/Git/…"
  exit 1
fi

if [ ! -f "/mnt/d/running/hermes/scripts/backup_5000m.sh" ]; then
  echo "❌ 5000m 备份：找不到 $TARGET"
  exit 1
fi

exec "$GB" "$TARGET"
