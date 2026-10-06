#!/bin/bash
# 升级/重装 mi-remote 后，重新应用"长按返回可配置"补丁
# 用法: bash apply-patch.sh [版本号，默认 0.4.1]
set -euo pipefail
V="${1:-0.4.1}"
F="$HOME/.local/share/mi-remote-linux/versions/$V/lib/python3.12/site-packages/mi_remote_linux/mapping_engine.py"
[ -f "$F" ] || { echo "找不到 $F"; exit 1; }
# 若补丁字段已存在，跳过
if grep -q 'self._binding(key).hold is None' "$F"; then echo "补丁已存在，无需处理"; exit 0; fi
sed -i 's/if key == "back" and self.effective_layer == 0:/if key == "back" and self.effective_layer == 0 and self._binding(key).hold is None:/' "$F"
grep -q 'self._binding(key).hold is None' "$F" && echo "✅ 补丁已应用: $F" || { echo "❌ 补丁失败（代码可能已变）"; exit 1; }
echo "接着执行: systemctl --user restart mi-remote"
