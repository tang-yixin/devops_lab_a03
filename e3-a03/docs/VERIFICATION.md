# E3 验证记录

执行环境：WSL Ubuntu 22.04.5 (x86_64)、gcc 11.4.0、GNU Make 4.3、strace 5.16；
Windows 本机仅用于 git 与脚本。

| 验证项 | 实际结果 | 依据 |
|---|---|---|
| MD 演示（改 config.h 增量） | 增量 `make: 'app' is up to date` → 输出旧值 1；clean 输出 2 | `evidence/md-rd-manual-check.md` |
| RD 演示（改 unused.h 注释） | 触发多余重编译 `cc -c main.c -o main.o` | 同上 |
| C0/C1/C2 演示（只改编译命令） | C0 clean=10；C1 clean=12、改 feature.h 不重建；C2 增量=12、clean=19 | `evidence/commits-manual-check.md` |
| Minicalc 三 commit 真实构建 | c0/c1/c2 均 `make clean`/`make` 退出码 0 | `evidence/minicalc-real-run.md` |
| Minicalc 功能测试 | `1+2*3`=7、`10-4/2`=8、`3*(4+5)`=27 全通过 | 同上 |
| strace 原始跟踪 | `legacy.h` 仅 newfstatat、0 次 openat → REDUNDANT 实锤 | `evidence/linux-verified/` |
| 环境版本记录 | git/make/gcc/python3/strace 齐全，x86_64 | `evidence/environment.md` |

## 与 E2 预期报告的对照

- Minicalc 三 commit 真实运行结果与 `e2-a03/artifacts/minicalc/` 中的预期报告一致
  （C0=3MD+1RD、C1=4MD+1RD、C2=4MD+0RD）。
- strace 从系统调用层面印证了 E2 报告「util.o → legacy.h 为 REDUNDANT」的结论。

## 结论

- E3 四个阶段（环境与脚手架 / MD-RD 手动对照 / 真实 C0-C1-C2 + strace / 汇总互查）的
  实验部分均已完成并留有可复现脚本与证据。
- 真实检测器（BuildChecker/EChecker）、四服务联调不在 E3 范围（E5/E8/E12）。

## 交叉检查闭环

- A03 复核 B03：运行 `verify_baselines.py`，DRAFT、四种 MDFixer 风格、无效候选拒绝全部
  PASS（详见 `evidence/b03-cross-check.md`）。
- B03 复核 A03：B03 独立读取 A03 新增的 16 个原始 trace，解码正常，编译器读取头文件关系
  与 C0 人工预期一致，确认通过（B03 复核记录见其 `e3-b03/evidence/a03-strace-retry-20261010/`）。
- 平台统一：双方确认后续真实 Docker 构建统一到 linux/amd64（E12 前对齐）。
- B03 跨架构（Apple Silicon 上跑 amd64 容器）重跑 strace 出现的解码异常，是跨架构系统调用
  跟踪兼容问题，非本组脚本问题；留待原生 x86_64 环境重跑，不影响 E3 交付。

## 后续阶段（不属于 E3）

- 真实检测器（BuildChecker/EChecker）在 E5/E8 实现。
- 四服务联调、真实 Docker 构建与跨机器产物读取在 E12。
