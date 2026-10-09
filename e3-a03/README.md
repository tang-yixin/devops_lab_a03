# A03 E3 并行测试基线

> 依据课程课件《E3_并行测试基线_20260930.pptx》。本阶段目标：为四类工具准备
> **可判对错的测试基线**——固定项目版本与环境、写清预期输出与判断依据、
> 保留实际运行与失败记录。真实检测器（BuildChecker/EChecker）在后续 E5/E8 实现。

## 与 E2 的关系

- E2 完成了四服务接口契约（schema/openapi/样例/ADR），并用 `gcc -MM` 静态推导出
  Minicalc C0/C1/C2 的预期图与报告。
- E3 把这些「纸上预期」升级为**真实可重跑、可判对错**的证据：真实 `make` 命令、
  退出码、增量 vs 全量对照、失败日志、Linux `strace` 原始跟踪。
- E2 成果原样保留在 `../e2-a03/`，本目录只新增 E3 内容，不改写 E2。

## 本组（A03）E3 职责

| 工具 | 准备输入 | 预期证据 |
|---|---|---|
| BuildChecker | main.c / Makefile / 头文件 | MD、RD 及依据 |
| EChecker | C0/C1/C2 与历史图预期 | 错误变化与命令变化 |
| （B 组）DRAFT | README、源码、构建命令 | 成功输出、失败日志 |
| （B 组）MDFixer | 固定 MD 报告、Makefile | Patch、验证与拒绝案例 |

A 组重点：MD/RD 项目与判断依据、C0/C1/C2 真实提交及预期变化、
真实 SHA + 预期报告 + 命令/输出/失败记录、Linux strace 证据。

## 已确定信息（复用自 E2）

| 项 | 值 |
|---|---|
| A 组编号 / 配对 | A03 / B03 |
| 目标项目 | `https://github.com/hardtosleep/Minicalc-DevOps-Test.git` |
| 基线 C0 | `e3a1eda0965e545d96467d275bccaf78c890fcac` |
| 增量 C1 | `f863c2deff1bd95e56f1578b872ae6aa26e3bfc8` |
| 增量 C2 | `e103bcb3726a3fd7253deb0d791ac74fac77cafe` |
| configuration_id | `cc-default` |
| 编译选项 | `-std=c11 -Wall -Wextra -Iinclude -g` |
| 成员分工 | 见 `../e2-a03/docs/TEAM.md` |

> Minicalc 三提交语义：C0=3MD+1RD、C1=4MD+1RD、C2=4MD+0RD（详见 Minicalc 仓库 README）。

## 目录结构

```text
e3-a03/
├── README.md
├── fixtures/            # 课程人工样例
│   ├── md-rd/           # config.h / unused.h 的 MD/RD 演示
│   └── commits/         # C0/C1/C2 演示（声明正确→新增include→只改编译命令）
├── work/                # 真实 Git 提交与参考修复（Minicalc）
├── evidence/            # 实际命令、输出、失败记录、strace 原始跟踪
│   └── linux-verified/
├── scripts/             # run_lab.py 等一键脚本
└── docs/                # E3 文档（BACKLOG、CONTRIBUTIONS、VERIFICATION 等）
```

## 环境与版本

正式证据统一在 **WSL Ubuntu 22.04.5 (x86_64)** 采集（gcc 11.4.0、GNU Make 4.3、
strace 5.16）。Windows 本机仅用于 git 与脚本。完整对照见 `evidence/environment.md`。

## E3 任务阶段

| 阶段 | 内容 | 状态 |
|---|---|---|
| 1. 环境与脚手架 | 记录 git/make/cc/python3/strace 版本、OS/CPU；搭 e3 分支与目录 | 完成 |
| 2. MD/RD 人工样例手动对照 | config.h/unused.h 实际构建 + 改头文件，产出 INSTRUCTOR_ORACLE 标签报告 | 完成 |
| 3. 真实 C0/C1/C2 固化 + Linux 跟踪 | Minicalc 真实 make 命令/退出码、增量 vs clean 对照、strace 证据 | 未开始 |
| 4. 汇总与互查 | README/环境/命令/日志/SHA/个人贡献，与 B 组交叉检查 | 未开始 |

详见 `docs/BACKLOG.md`。

## 与 B 组对接

B03 已推送 E3 基线（SHA `9f39cc8`，`e3-b03/`），包含 DRAFT 失败/成功 Docker 样本、
固定 MD 报告、四种 Makefile 修复参考补丁。A03 需在阶段 4 前完成基线并回发
仓库地址、提交 SHA、验证结果，供双方交叉检查。
