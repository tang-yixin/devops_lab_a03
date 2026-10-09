# E3 个人贡献记录

> 说明：`devops_lab_a03` 仓库的 E3 提交由唐一心统一提交（git 作者 `29699`）；
> 目标项目 `Minicalc-DevOps-Test` 的真实提交（c0/c1/c2）由李翔宇独立提交（作者 `hardtosleep`）。
> 未使用 Issue/PR 流程，以 Git 提交记录为准。下表是成员的大致分工，表中 SHA 仅标注该成员主要参与的提交，不代表该提交仅含其一人工作。

| 姓名/学号 | 工作和文件 | commit SHA | 提交说明 | 验证结果 |
|---|---|---|---|---|
| 唐一心（241250061） | E3 骨架与统筹：`e3-a03/README.md`、根 `README.md` 拆分、`docs/BACKLOG.md` | `084593e` | 搭建 e3-a03 骨架、拆分 README | 目录结构与 PPT 第 12 页一致 |
| 唐一心（241250061） | Linux 原始跟踪：`scripts/strace_check.sh`、`evidence/linux-verified/` | `3bcd1da` | strace 原始跟踪证据 | `legacy.h` 0 次 openat，实锤 REDUNDANT |
| 李翔宇（241250093） | MD/RD 人工样例：`fixtures/md-rd/`、`oracle-report.json`、`evidence/md-rd-manual-check.md` | `0807d3c` | MD/RD 人工样例手动对照 | 增量输出旧值 1、多余编译，与 PPT 一致 |
| 李翔宇（241250093） | Minicalc 真实运行：`scripts/minicalc_check.sh`、`evidence/minicalc-real-run.md` | `91edad7` | Minicalc 真实运行证据 | 三 commit `make`/`make test` 退出码 0，7/8/27 通过 |
| 王子贤（241250106） | C0/C1/C2 演示样例：`fixtures/commits/`、`oracle-report.json`、`evidence/commits-manual-check.md` | `4b5a76d` | C0/C1/C2 演示样例增量 vs clean | 输出 10/12/19 符合预期，含「只改编译命令」 |
| 王子贤（241250106） | 脚本可移植性改造：`scripts/*.sh` 路径参数化（SCRIPT_DIR 推导 + MINICALC_REPO 环境变量） | `18231ed` | 脚本参数化 | 4 个脚本去除本机硬编码路径，可跨环境复现 |
| 刘馨蔓（241250107） | 环境与版本记录：`evidence/environment.md` | `4f2f835` | 记录环境与版本 | WSL Ubuntu 22.04.5 x86_64 工具链齐全 |
| 刘馨蔓（241250107） | E3 文档补全、验证汇总与 B03 交叉复核：`docs/VERIFICATION.md`、`docs/CONTRIBUTIONS.md`、`evidence/b03-cross-check.md`、`work/README.md`、`README.md` 完善 | `0dcc3b6` | 补全汇总文档 + 复核 B03 | B03 基线本地模拟全 PASS；验证记录与 E2 预期报告对照一致 |

可用 `git log --format="%H %an <%ae> %s"` 获取真实版本、作者和说明。

## 验证命令

```bash
# 在 WSL Ubuntu 中复现（脚本均写入 /tmp，不污染源文件）
bash e3-a03/scripts/md_rd_check.sh       # MD/RD 手动对照
bash e3-a03/scripts/commits_check.sh     # C0/C1/C2 演示
bash e3-a03/scripts/minicalc_check.sh    # Minicalc 真实运行
bash e3-a03/scripts/strace_check.sh      # strace 原始跟踪
```

## 未完成项

- 与 B03 的交叉检查（待 B03 复核 A03 基线）、平台统一（x86_64 vs arm64）留待阶段 4 收尾 / E12 联调。
- 真实检测器（BuildChecker/EChecker）在 E5/E8 实现，不属于 E3。
