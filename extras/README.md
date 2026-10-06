# extras/ · 留档的未启用实现

| 文件 | 说明 |
|---|---|
| `backspace-burst` | 「长按返回 = 连续快删」的实现（按住 Backspace 借系统按键重复连删）。<br>该功能**已按需求回退**（现在长按同短按），保留备查。 |
| `../system/patch/` | 让「长按返回可配置」的本机补丁（已回退，未应用）。想恢复连删时：先 `bash system/patch/apply-patch.sh`，再把 `back.hold` 指回 `extras/backspace-burst` 并把该脚本装到 `~/.local/bin`。 |
