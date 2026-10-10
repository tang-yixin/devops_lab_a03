# B03 基线交叉复核记录（A03 侧）

> 依据 PPT 第 10–11 页「相互检查」。A03 在 WSL Ubuntu 22.04.5 (x86_64) 上
> 运行 B03 的 `e3-b03/verify_baselines.py`，对 DRAFT 与 MDFixer 基线做交叉复核。

## 环境

| 项 | 值 |
|---|---|
| 复核方 | A03 |
| 被复核方 | B03（`b-group-project`，E3 基线 SHA `9f39cc8`） |
| 平台 | Linux-6.18.33 WSL2 x86_64 (glibc 2.35) |
| Python | 3.10.12 |

## 复核结果（`verify_baselines.py` 输出）

| 项 | 结果 |
|---|---|
| DRAFT 本地构建/输出 | PASS（`./hello` → `hello E3`） |
| DRAFT 缺工具链模拟 | 退出码 127（`make: not found`） |
| MDFixer 风格 target | PASS（增量 1 → clean 2 → 修复后增量 3） |
| MDFixer 风格 macro | PASS |
| MDFixer 风格 hybrid | PASS |
| MDFixer 风格 implicit | PASS（含 `main.d` 含 config.h 断言） |
| 无效候选拒绝 | PASS（失败退出码 2，恢复后输出 1） |

## 未复核项

- **Docker 部分**：脚本用本地模拟（`LOCAL_FAILURE_SIMULATION`）替代真实 `docker build`，
  且 B03 参考镜像标注为 `linux/arm64`，与 A03 的 `x86_64` 不同。真实 Docker 构建
  留待双方在统一平台（linux/amd64）或 E12 联调时验证。

## 结论

- B03 的 E3 基线（DRAFT + MDFixer 四种风格 + 无效候选拒绝）在 A03 环境可复现、可判对错。
- 平台差异（x86_64 vs arm64）不影响本地模拟部分的复核，但真实 Docker 镜像需统一平台后再交叉验证。
