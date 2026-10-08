# extras/ · 留档的未启用实现

| 文件 | 说明 |
|---|---|
| `../scripts/backspace-burst` | 「长按返回 = 连续快删」的实现（按住 Backspace 借系统按键重复连删）。<br>**已于 2026-10-08 重新启用**，脚本从 `extras/` 提回 `scripts/`，由 `install.sh` 安装。 |
| `../system/patch/` | 让「长按返回可配置」的本机补丁（`apply-patch.sh --mapping`）+ 唤醒即重连补丁（`apply-wake-reconnect.py`）。重装/升级 mi-remote 后需重跑 `apply-patch.sh`。 |
