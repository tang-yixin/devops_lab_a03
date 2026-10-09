# E3 环境与版本记录

> 依据 PPT 第 15 页「A 组步骤 1：检查环境」。
> 原则：正式证据统一在 **WSL Ubuntu 22.04.5 (x86_64)** 采集；
> Windows 本机只用于仓库管理（git）与脚本（python）。MinGW 的 gcc 仅作预演参考，
> 不用于正式比对（其 `make clean` 的 `rm -f` 在 Windows 下会失败，且依赖图可能与
> Linux gcc 不同）。

## 检查日期

2026-10-09

## 本机环境对照

| 工具 | Windows 11 本机 | WSL Ubuntu 22.04.5 (x86_64) |
|---|---|---|
| 架构 | — | x86_64 |
| git | 2.53.0.windows.2 ✅ | 2.34.1 ✅ |
| make | ❌ 无 | GNU Make 4.3 ✅ |
| cc / gcc | MinGW gcc 12.3.0（预演参考） | gcc 11.4.0 ✅ |
| python / python3 | 3.13.7 ✅（命令名 `python`） | 3.10.12 ✅（命令名 `python3`） |
| strace | ❌ 无 | 5.16 ✅ |

## 结论

- **WSL Ubuntu 22.04.5 内 gcc + GNU Make + strace 齐全**，满足 E3 全部 Linux 工具链需求。
- 正式证据（make 输出/退出码、增量 vs clean 对照、strace 跟踪）一律在 WSL 内采集。
- B03 的容器证据为 `linux/arm64`，与本组 `x86_64` 不同；阶段 4 交叉检查时需
  对齐「统一在哪个平台比较」，留待后续与 B 组确认。

## 兜底命令（环境被重置时才需要，当前无需执行）

```bash
wsl -d Ubuntu-22.04
sudo apt update
sudo apt install -y build-essential strace
```
