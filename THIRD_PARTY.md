# 第三方组件与致谢（Third-party notices）

本项目**依赖、调用或打包**了下列开源项目。感谢这些作者的工作 🙏

> 说明：除标注「随仓库分发」的项外，其余均为**运行环境中的依赖**（系统包或上游项目）。
> Paraformer 的 `tokens.txt` 随仓库；`model.int8.onnx` 放在工作树 `models/paraformer-zh/`，不进 git。
> 许可证以各上游仓库为准。

## 核心依赖（本项目的底座）

| 项目 | 用途 | 许可证 | 链接 |
|---|---|---|---|
| **goodtiger/mi-remote-linux** | 遥控器 GATT/ATVV 连接、按键解码、动作引擎、语音管道。**本项目是它的 GNOME/Wayland 补丁与周边** | MIT | <https://github.com/goodtiger/mi-remote-linux> |
| └ `install-mi-remote.py`（**随仓库分发**） | 上游官方安装器（离线备用） | 同上（MIT） | 见上 |
| └ `system/patch/mapping_engine.py.*`（**随仓库分发**） | 上游源文件的原始版与打过补丁的版本（让"长按返回"可配置） | 同上（MIT） | 见上 |

## 语音识别

| 项目 | 用途 | 许可证 | 链接 |
|---|---|---|---|
| **Sherpa-ONNX**（k2-fsa） | 本地离线中文识别（代码保留，默认不加载） | Apache-2.0 | <https://github.com/k2-fsa/sherpa-onnx> |
| **Xiaomi MiMo ASR**（`mimo-v2.5-asr`） | 默认云端转写（Token Plan，Key 不进仓库） | 专有云服务 | <https://mimo.mi.com/docs/en-US/usage-guide/Speech-Recognition> |
| `csukuangfj/sherpa-onnx-paraformer-zh-2023-09-14` | 中文 Paraformer 模型（233 MB，权重放在 `models/paraformer-zh/`，**onnx 不进 git**） | Apache-2.0 | <https://huggingface.co/csukuangfj/sherpa-onnx-paraformer-zh-2023-09-14> |
| **faster-whisper**（SYSTRAN） | 备用离线识别引擎 | MIT | <https://github.com/SYSTRAN/faster-whisper> |
| **python-evdev** | 读取遥控器按键事件 / 本项目的 uinput 注入垫片 | BSD-3-Clause | <https://github.com/gvalkov/python-evdev> |
| **NumPy** | 音频数组处理（经 mi-remote 引入） | BSD-3-Clause | <https://numpy.org> |

## 托盘应用（`app/`）

| 项目 | 用途 | 许可证 | 链接 |
|---|---|---|---|
| **Flutter / Dart** | 托盘应用框架 | BSD-3-Clause | <https://github.com/flutter/flutter> |
| **tray_manager** | 系统托盘图标与菜单（Linux 走 AppIndicator） | MIT | <https://pub.dev/packages/tray_manager> |
| **menu_base** | tray_manager 的菜单模型（子菜单支持） | MIT | <https://pub.dev/packages/menu_base> |
| GTK 3 / **libayatana-appindicator** | 托盘后端（系统库） | LGPL-2.1+ | <https://github.com/AyatanaIndicators/libayatana-appindicator> |
| **winrects@cua**（GNOME 扩展，随 CUA 安装） | 通过 DBus 列出/激活窗口（窗口聚焦与切换器依赖它） | 见 Cua 项目许可 | — |

## 工具链 / 辅助

| 项目 | 用途 | 许可证 | 链接 |
|---|---|---|---|
| **cairosvg** | 生成键位图时把 SVG 转成 PNG | LGPL-3.0 | <https://github.com/Kozea/CairoSVG> |
| **Pillow**（可选） | 图片处理（键位图脚本备用路径） | MIT-CMU | <https://python-pillow.org> |
| **playerctl** | 媒体播放控制（音量键旁边的媒体操作） | LGPL-3.0 | <https://github.com/altdesktop/playerctl> |
| **libnotify**（`notify-send`） | 桌面通知、浮层、断连提醒 | LGPL-2.1 | <https://gitlab.gnome.org/GNOME/libnotify> |
| **Pillow / numpy** 之外的 Python 标准库 | — | PSF-2.0 | <https://www.python.org> |

## 系统组件（GNOME / Wayland 平台）

| 组件 | 用途 | 许可证 |
|---|---|---|
| **BlueZ** | 蓝牙协议栈（配对、GATT、HID） | GPL-2.0（库为 LGPL-2.1） |
| **systemd / udev** | 用户服务、设备权限规则 | LGPL-2.1 |
| **GNOME / Mutter / libinput** | 合成器与输入栈（本项目所有注入都最终落到它） | GPL-2.0+ / MIT |
| **PipeWire / WirePlumber**（`wpctl`） | 系统音量与音频通道 | MIT |
| **gnome-terminal / nautilus** | 启动器打开的目标（系统应用） | GPL-3.0 |

## 目标应用（本项目为它们定制键位，非依赖）

| 应用 | 说明 | 许可证 |
|---|---|---|
| **OpenCode** | AI 编程 CLI（`Ctrl+B` 等键位按其默认绑定设计） | 见 [anomalyco/opencode](https://github.com/anomalyco/opencode) |
| **Cursor** | AI 编辑器（双击 TV 打开） | 专有软件 |

## 硬件

- 目标设备：**小米蓝牙遥控器 2 Pro**（RC003，BLE VID:PID `2717:32b8`）
  官方产品页：<https://www.mi.com/xiaomi-bluetooth-remote-2-pro>

---

如果你在使用中发现遗漏了某个依赖或致谢，欢迎提 Issue / PR 补充。
