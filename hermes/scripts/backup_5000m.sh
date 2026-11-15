#!/usr/bin/env bash
# 每周把 D:/running 提交并推送到 GitHub vidaleitos/5000m (private)
#
# 调用链（注意：Hermes gateway 跑在 WSL2，git 和 SSH key 在 Windows 侧）：
#   cron → (WSL) profile/scripts/backup_5000m.sh  ← 薄包装，只负责找到 git-bash
#        → (Windows git-bash) 本文件 → git add/commit/push
#
# 所以本文件必须在 **Windows git-bash** 里执行，不要直接用 WSL 的 bash 跑
# （WSL 看不到 /d/running，也没有 Windows 的 ~/.ssh）。
set -u

REPO="/d/running"

if ! cd "$REPO" 2>/dev/null; then
  echo "❌ 5000m 备份失败：无法进入 $REPO"
  exit 1
fi

git add -A 2>/dev/null

# ── 凭据护栏：命中就中止，绝不推送 ──────────────────
BAD=$(git diff --cached --name-only | grep -iE '(^|/)(\.env.*|.*session\.json|.*token.*|.*credential.*|.*secret.*)$' || true)
if [ -n "$BAD" ]; then
  git reset -q
  echo "❌ 5000m 备份已中止：检测到疑似凭据文件"
  echo "$BAD" | head -10
  exit 1
fi

if git diff --cached --quiet; then
  echo "5000m 备份：无变更（$(date +%F)）"
  exit 0
fi

N=$(git diff --cached --name-only | wc -l | tr -d ' ')

if ! git commit -q -m "auto: $(date +%F)"; then
  echo "❌ 5000m 备份失败：commit 出错"
  exit 1
fi

H=$(git rev-parse --short HEAD)

if out=$(GIT_SSH_COMMAND="ssh -o ConnectTimeout=25 -o ServerAliveInterval=30" git push 2>&1); then
  echo "✅ 5000m 备份完成：${N} 个文件 → ${H}（$(date +%F)）"
else
  echo "❌ 5000m 备份：commit ${H} 成功但推送失败（${N} 个文件本地已保存）"
  echo "$out" | tail -5
  exit 1
fi
