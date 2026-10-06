#!/bin/bash
# 构建并（重）启动 Baton 托盘应用
#
# 用法: ./run.sh [--no-build]
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

export PATH="$HOME/flutter/bin:$PATH"
APP_NAME=baton
BUNDLE="build/linux/x64/release/bundle/$APP_NAME"

if [ "${1:-}" != "--no-build" ]; then
  echo "== 构建（release）=="
  flutter build linux --release 2>&1 | tail -2
fi

echo "== 重启应用 =="
# -x 精确匹配进程名，避免误杀别的进程/脚本自身
pkill -x "$APP_NAME" 2>/dev/null || true
sleep 1
nohup "$BUNDLE" >/tmp/baton.log 2>&1 &
sleep 6

pid=$(pgrep -x "$APP_NAME" | head -1 || true)
if [ -z "$pid" ]; then
  echo "❌ 启动失败，日志："; tail -20 /tmp/baton.log; exit 1
fi
echo "✅ 已运行 pid=$pid（托盘图标：看顶栏）"

bus=$(busctl --user list 2>/dev/null | awk -v p="$pid" '$3==p {print $1; exit}')
if [ -n "${bus:-}" ]; then
  gdbus call --session --dest org.kde.StatusNotifierWatcher --object-path /StatusNotifierWatcher \
    --method org.freedesktop.DBus.Properties.Get org.kde.StatusNotifierWatcher RegisteredStatusNotifierItems 2>/dev/null \
    | grep -q "$bus" && echo "✅ 托盘项已注册（$bus）" || echo "⚠️ 托盘项未在 watcher 里（图标可能未显示）"
fi
