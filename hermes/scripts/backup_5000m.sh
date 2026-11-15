#!/usr/bin/env bash
# 每周把 D:/running 提交并推送到 GitHub vidaleitos/5000m (private)
#
# 必须在 **Windows git-bash** 里执行（本机 bash 由 Git for Windows 提供）。
# 每次运行都会往 hermes/scripts/backup-status.log 追加一行心跳，
# 所以即使训练数据没有变化，也会有一周一次的提交 —— 那就是“任务还在跑”的凭证。
set -u

REPO="/d/running"
LOG_REL="hermes/scripts/backup-status.log"

if ! cd "$REPO" 2>/dev/null; then
  echo "❌ 5000m 备份失败：无法进入 $REPO"
  exit 1
fi

LOG="$REPO/$LOG_REL"
NOW="$(date '+%Y-%m-%d %H:%M')"
TODAY="$(date +%F)"

say() { printf '%s  %s\n' "$NOW" "$*" >> "$LOG"; }

# ── 凭据护栏：命中就中止，绝不推送 ──────────────────
git add -A 2>/dev/null
BAD=$(git diff --cached --name-only | grep -iE '(^|/)(\.env.*|.*session\.json|.*token.*|.*credential.*|.*secret.*)$' || true)
if [ -n "$BAD" ]; then
  git reset -q
  say "ABORT 检测到疑似凭据文件，未提交"
  echo "❌ 5000m 备份已中止：检测到疑似凭据文件"
  echo "$BAD" | head -10
  exit 1
fi

CHANGED=$(git diff --cached --name-only | grep -v "^$LOG_REL$" | wc -l | tr -d ' ')

if [ "$CHANGED" -eq 0 ]; then
  say "OK    无变更（心跳）"
  OUT="无变更（心跳）"
else
  say "OK    ${CHANGED} 个文件"
  OUT="$CHANGED 个文件"
fi

# 心跳行本身也要进这次提交
git add "$LOG_REL" 2>/dev/null

if ! git commit -q -m "auto: $TODAY"; then
  echo "❌ 5000m 备份失败：commit 出错"
  exit 1
fi

H=$(git rev-parse --short HEAD)

if out=$(GIT_SSH_COMMAND="ssh -o ConnectTimeout=25 -o ServerAliveInterval=30" git push 2>&1); then
  echo "✅ 5000m 备份完成：${OUT} → ${H}（$TODAY）"
else
  echo "❌ 5000m 备份：commit ${H} 成功但推送失败（本地已保存）"
  echo "$out" | tail -5
  exit 1
fi
