# C0/C1/C2 演示样例对照证据

> 依据 PPT 第 23–27 页。在 WSL Ubuntu 22.04.5 (x86_64) 中建临时 Git 仓库，
> 按 C0→C1→C2 三次提交，验证「声明正确→新增 include 漏声明→只改编译命令」
> 三类场景的增量 vs clean 行为。样例源码见 `../fixtures/commits/`。

## 三版本说明

| 版本 | 改动 | Makefile 变化 | 预期 |
|---|---|---|---|
| C0 | 声明正确：main.c 读 config.h，Makefile 声明 config.h | — | clean = 10 |
| C1 | main.c 新增 `#include "feature.h"` 并用 FEATURE | 未补 feature.h（漏声明） | clean = 12；改 feature.h 不重建 |
| C2 | 只改 `CFLAGS` 为 `-O0 -DMODE=7`，源码保持 C1 | 仅改编译命令 | 增量 = 12；clean = 19 |

## 实际观察（脚本 `../scripts/commits_check.sh`）

| 场景 | 预期 | 实际 | 结论 |
|---|---|---|---|
| C0 clean | 10 | `10` | 声明正确，无 MD/RD（本例范围） |
| C1 增量 / clean | 12 | `12` / `12` | 输出正确，但**不能据此判断无 MD** |
| C1 只改 feature.h 后 make | 不重建 | `make: 'app' is up to date.` → 仍 `12` | **MD：main.o 缺 feature.h 声明，漏重建** |
| C2 增量（保留 C1 产物） | 12 | `12` | **命令变化未触发普通时间戳重建** |
| C2 clean | 19 | `19` | 完整重建后 `-DMODE=7` 生效 |

## Git 历史（临时仓库内）

```text
2453ac1 (tag: c2) C2: change CFLAGS only (-DMODE=7)
8c9f980 (tag: c1) C1: add feature.h include (missing decl)
00221cc (tag: c0) C0: baseline (declared correctly)
```

## 结论

- C1 的 MISSING（`main.o → feature.h`）通过「只改 feature.h → 增量不重建」实锤；
- C2 的「只改编译命令」场景证明：普通 `make` 时间戳检查会漏掉命令变化，
  增量输出旧值 12，clean 才输出 19——这正是 EChecker 需要关注的命令变化。
- 判断依据见 `../fixtures/commits/oracle-report.json`（`INSTRUCTOR_ORACLE`）。
