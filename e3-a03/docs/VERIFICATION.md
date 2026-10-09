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

## 未完成项

- 与 B03 交叉检查（需对方按 README 复现）与平台统一（x86_64 vs arm64）。
- 本轮文档补全的最终提交（见 `CONTRIBUTIONS.md` 未完成项）。
