# Minicalc 真实运行证据（E3-A05）

> 依据 PPT 第 7–8、18–27 页。在 WSL Ubuntu 22.04.5 (x86_64)、gcc 11.4.0、
> GNU Make 4.3 中对真实目标项目 Minicalc 三个 commit 执行真实 `make`，
> 记录退出码、输出与功能测试。脚本 `../scripts/minicalc_check.sh`。

## 三个 commit 构建与功能测试

| commit | 完整 SHA | `make clean` 退出码 | `make` 退出码 | `make test`（7/8/27） |
|---|---|---|---|---|
| c0 | `e3a1eda0965e545d96467d275bccaf78c890fcac` | 0 | 0 | 全部通过 |
| c1 | `f863c2deff1bd95e56f1578b872ae6aa26e3bfc8` | 0 | 0 | 全部通过 |
| c2 | `e103bcb3726a3fd7253deb0d791ac74fac77cafe` | 0 | 0 | 全部通过 |

构建命令（Makefile 内）：`gcc -std=c11 -Wall -Wextra -Iinclude -g`，
4 个目标（main.o / parser.o / token.o / util.o）→ 链接 `minicalc`。

功能测试 `make test` 三用例：`1+2*3`=7、`10-4/2`=8、`3*(4+5)`=27，均正确。

## MD/RD 行为观察（基于 c0）

| 操作 | 实际 make 输出 | 结论 |
|---|---|---|
| `touch include/legacy.h` 后 make | 重建 `util.o` + 链接 | **RD 实锤**：legacy.h 被声明但 util.c 未读取，多余编译 |
| `touch include/util.h` 后 make | 重建 `util.o`（**不重建 main.o**）+ 链接 | 部分印证 MD：main.o 未重建；但 util.o 同时重建是因为 util.o 规则**本身声明了 util.h** |

> 说明：真实项目中缺失的头文件（util.h、token.h）同时被**其他目标**声明，
> 因此无法像阶段二玩具样例那样得到"单一目标"的干净 MD 演示。干净的
> 单目标 MD 行为已在 `fixtures/md-rd/` 完成。这里仅如实记录现象与原因。

## 结论

- 三个 commit 在 Linux 环境均能 `make clean && make` 成功（退出码 0），功能测试通过。
- 真实运行结果与 `e2-a03/artifacts/minicalc/` 中的预期报告一致（C0=3MD+1RD 等）。
- 本阶段只做「真实运行记录」，未做 strace 动态追踪（见 E3-A06）与检测器实现（E5/E8）。
