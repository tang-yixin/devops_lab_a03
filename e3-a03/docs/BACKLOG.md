# E3 Backlog（A03）

> 状态：`进行中` = 本阶段正在做；`未开始` = 待后续阶段；`完成` = 已实现并记录。

## 阶段 1：环境与脚手架

| ID | 责任方 | 产物 | 验收条件 | 状态 |
|---|---|---|---|---|
| E3-A01 | A 全体 | `e3-a03/` 目录骨架 + README | 目录结构与 PPT 第 12 页一致，README 含已确定信息 | 完成 |
| E3-A02 | A 全体 | 环境版本记录 | 记录 OS/CPU、git/make/cc/python3/strace 版本 | 完成 |

## 阶段 2：MD/RD 人工样例手动对照

| ID | 责任方 | 产物 | 验收条件 | 状态 |
|---|---|---|---|---|
| E3-A03 | A | `fixtures/md-rd/` 样例 + 手动构建 | 漏声明→增量不重建；多余声明→多余编译；产出 ORACLE 报告 | 完成 |

## 阶段 3：真实 C0/C1/C2 固化 + Linux 跟踪

| ID | 责任方 | 产物 | 验收条件 | 状态 |
|---|---|---|---|---|
| E3-A04 | A | `fixtures/commits/` C0/C1/C2 演示（含「只改编译命令」） | 增量 vs clean 输出符合预期（10/12/19） | 完成 |
| E3-A05 | A | `work/` 真实 Minicalc 运行记录 | 真实 make 退出码/输出、增量 vs clean 对照、失败日志 | 完成 |
| E3-A06 | A | `evidence/linux-verified/` strace | `strace -ff` + `make -pn` 原始跟踪可定位依赖读取 | 完成 |

## 阶段 4：汇总与互查

| ID | 责任方 | 产物 | 验收条件 | 状态 |
|---|---|---|---|---|
| E3-A07 | A 全体 | `docs/CONTRIBUTIONS.md`、`VERIFICATION.md`、README 完善 | 每人 commit SHA + 验证结果；与 B 组交叉检查通过 | 完成（A03 已复核 B03；待 B03 复核 A03） |

## 边界（不属于 E3）

- 真实检测器 BuildChecker → E5；EChecker → E8；四服务联调 → E12。
