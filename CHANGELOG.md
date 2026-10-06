# Changelog

本项目遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 的结构；日期为本地时间。
版本号未正式发布前统一记在 `Unreleased` 下。

## Unreleased

### 新增（Added）

- **小米 MiMo 云端 ASR**：`system/cloud-asr.json` 同时放地址、模型和 api_key（gitignore，不提交）；模板 `cloud-asr.json.example`
- **仓库结构**：新增 `tools/`（维护工具：键位图生成、logo 生成），运行时脚本仍留在 `scripts/`（会被装进 `~/.local/bin`）
- **项目 logo**：圆形徽章（遥控器 + 信号弧），`docs/images/logo.png`，同时用作桌面图标；托盘栏仍是绿/黄/红三色状态圆点
- **开源化包装**：双语 README（`README.md` 英文 / `README.zh-CN.md` 中文）、`LICENSE`(MIT)、`CHANGELOG.md`、
  `CONTRIBUTING.md`、`THIRD_PARTY.md`（第三方组件与许可证清单）、**键位图**（脚本随配置自动生成）

- **托盘应用 Baton**（Flutter，纯托盘无窗口）
  - 三层连接状态：蓝牙链路 / HID 按键节点 / 服务与注入守护
  - 图标三态：🟢 正常 · 🟡 按键可用但语音未连 · 🔴 服务或按键异常
  - 菜单：状态展示 · **键位速查 ▸**（实时读 `mapping.json` 生成）· 重新检测 · 重启服务 · 重连蓝牙 · 查看日志 · 打开文档 · 退出
  - **断连提醒**：蓝牙断开/恢复时桌面通知（1 分钟冷却，恢复提醒不受冷却限制）
  - 开机自启（`install.sh` 写入 `~/.config/autostart/`）
- **uinput 注入垫片**：GNOME Wayland 下替代不可用的 `wtype`
  - `mi-remote-uinputd`（常驻守护进程 + unix socket）+ `ydotool`（客户端垫片）
  - 实测 30 ms/次（对比"每次新建虚拟设备"的 2.1 s/次）
- **窗口切换器**：长按菜单进入，保持 Alt 后 `←/→` 可遍历**所有**窗口（原生 `Alt+Tab` 只能在两个窗口间跳），闲置 8 秒自动选定、可顺延
- **窗口聚焦**：启动 OpenCode/Cursor 时若目标目录已打开，直接拉到前台
  - 借助 GNOME 扩展 `winrects@cua` 的 DBus 接口（`GetRects`/`Activate`）
- **启动器**：`open-workspace-{opencode,cursor,terminal,files}`（最大化、已开则聚焦、带日志）
- **install.sh**：一键部署/更新（幂等；udev 已最新时跳过、无需 sudo；支持 `SUDO_PASS=`）

### 变更（Changed）

- 文档合并：`docs/键位表.md` + `docs/适配流程.md` + `docs/需求.md` → 单份 [`docs/指南.md`](docs/指南.md)
  （第 1 章键位表 · 第 2 章适配流程与踩坑 · 第 3 章路线图；已回退功能不再写成操作指南）

- 键位反复打磨后的最终形态（详见 `docs/指南.md` 第 1 章）
  - 返回：短按 = 删除（即时）；Esc 从"返回双击"移走（曾因连按被判双击而误打断 AI）
  - 电源：短按 = `Esc`；长按 = 关闭当前窗口（`Alt+F4`）；去掉双击（消除"连按两次误关窗"）
  - 主页：去掉短按/长按，只保留双击启动 OpenCode
  - TV：短按 = `Ctrl+B`（OpenCode 把阻塞的工具转后台）；去掉长按（原 Super 活动概览）
  - 音量：短按 = `PageUp`/`PageDown`（不再调系统音量）
  - 下键：恢复纯 `↓`（菜单导航）
- udev 规则：同时匹配设备名 `小米蓝牙语音遥控器` 与 `MI RC`（实测设备名会变），并加 BLE HID 兜底

### 移除（Removed）

- OpenCode 层（leader 宏那套）；备份见 `system/mapping.json.with-opencode-layer.bak`
- 启动层（短按 TV 进层启动 5 个目标）；备份见 `system/mapping.json.with-launch-layer.bak`
- 鼠标模式（电源键改为 Esc/关窗后无入口；实现仍在，可用 `power.hold = {"type":"mouse_mode"}` 恢复）
- 长按返回"连续快删"（实现留档于 `extras/backspace-burst` 与 `system/patch/`）

### 修复（Fixed）

- 语音识别乱码：默认 `--gain 6` 把遥控麦削波（峰值顶满 32768）→ 服务改为 `--gain 0`
- GNOME 下按键注入全线失效：Mutter 不实现 `wtype` 依赖的虚拟键盘协议 → 卸载 wtype + 自写 uinput 垫片
- 官方安装器（v0.4.1）venv shebang 残留临时目录导致装完无法执行 → 批量改写 shebang
- 终端里语音粘贴无效 → 服务参数 `--paste-shortcut ctrl-shift-v`
- 垫片拉起守护进程时解释器无 `evdev` → 自动挑选带 evdev 的解释器（venv python）
- 蓝牙设备名变化导致 udev 规则失效、按键静默失效 → 多重匹配
