# 语音模型

默认引擎用的是 [Sherpa-ONNX Paraformer 中文](https://huggingface.co/csukuangfj/sherpa-onnx-paraformer-zh-2023-09-14)
（Apache-2.0），权重放在本目录的 `paraformer-zh/`。


| 文件                            | 大小             | 说明                                                   |
| ------------------------------- | ---------------- | ------------------------------------------------------ |
| `paraformer-zh/model.int8.onnx` | 243,371,218 字节 | 权重（**不进 git**：GitHub 单文件上限 100 MB） |
| `paraformer-zh/tokens.txt`      | 75,756 字节      | 词表（随仓库）                                         |
| `paraformer-zh/SHA256SUMS`      | —               | 校验和                                                 |

服务只通过 `--paraformer-model-dir` 读本目录，不再使用 `~/.local/share/mi-remote-linux/models/`。

缺权重时（新克隆）：

```bash
mi-remote model download --target "$(pwd)/models/paraformer-zh"
mi-remote model status --target "$(pwd)/models/paraformer-zh"
```

`./install.sh` 也会在本目录没有 `model.int8.onnx` 时自动下载到这里。
