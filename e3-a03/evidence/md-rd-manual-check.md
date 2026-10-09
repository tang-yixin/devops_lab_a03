# MD/RD 人工样例手动对照证据

> 依据 PPT 第 17–22 页。在 WSL Ubuntu 22.04.5 (x86_64) 中实际构建，
> 验证「漏声明依赖（MD）→ 增量不重建」「多余声明依赖（RD）→ 多余编译」两类行为。
> 样例源码与 ORACLE 报告见 `../fixtures/md-rd/`。

## 样例说明

| 文件 | 内容 |
|---|---|
| `main.c` | `#include "config.h"`，打印 `VALUE` |
| `config.h` | `#define VALUE 1`（被读取但 Makefile 未声明 → MD） |
| `unused.h` | 仅注释（Makefile 声明但未读取 → RD） |
| `Makefile` | `main.o: main.c unused.h`（缺 config.h，多 unused.h） |

## 实际观察（脚本 `../scripts/md_rd_check.sh`）

| 步骤 | 操作 | 预期 | 实际 | 结论 |
|---|---|---|---|---|
| 4 第一次完整构建 | `make` + `./app` | 输出 1 | `1`，exit 0 | 编译成功，config.h 存在 |
| 5 只改 config.h→2 增量 | `make` + `./app` | 仍 1 | `make: 'app' is up to date.` → `1` | **MD：Make 认为无需重建，输出过时** |
| 6 clean build | `make clean && make` + `./app` | 2 | `2` | 同源码完整重建得新值，证明漏重建 |
| 7 只改 unused.h 注释 | `make` | 再次编译 | `cc -c main.c -o main.o` + `cc main.o -o app` | **RD：多余声明触发多余编译** |

## 结论

- 增量输出 `1` 与 clean 输出 `2` 的差异，证明 `main.o` 缺 `config.h` 声明（MISSING）。
- 仅改 `unused.h` 注释即触发重编译，证明 `unused.h` 为多余声明（REDUNDANT）。
- 两条发现的判断依据见 `../fixtures/md-rd/oracle-report.json`（`INSTRUCTOR_ORACLE`）。
- 本报告是人工参考答案，不计入真实检测器准确率；真实 Checker 输出留待 E5/E8。
