# 个人贡献记录

> 说明：`devops_lab_a03` 仓库的提交由唐一心统一提交（git 作者 `29699`）；
> 目标项目 `Minicalc-DevOps-Test` 仓库由李翔宇独立提交（作者 `hardtosleep`）。
> 未使用 Issue/PR 流程，以 Git 提交记录为准。下表是成员的大致分工，表中 SHA 仅标注该成员主要参与的提交，不代表该提交仅含其一人工作。

| 姓名/学号 | 工作和文件 | commit SHA | 提交说明 | 验证结果 |
|---|---|---|---|---|
| 唐一心（241250061） | A/B 契约对齐与协调：`contracts/shared-lock.json`（31→33 同步）、`graph.schema.json`、`finding-id-v1.json`、`docs/API-CONTRACT.md`、`TEAM.md`、`SUBMISSION.md` | `7aebdd2`、`b1f5fe2`、`052cc86`（devops_lab_a03） | 同步共享锁至 33 文件；补全文档与 ADR | 33 个共享文件哈希与 B 组一致 |
| 李翔宇（241250093） | 目标项目 `Minicalc-DevOps-Test` 创建，埋入依赖缺陷并产出 C0/C1/C2 三个提交 | `e3a1eda`（C0）、`f863c2d`（C1）、`e103bcb`（C2）、`1208549`（devops_lab_a03） | minicalc baseline / configurable token capacity / restore legacy hook | 三版本构建与测试通过，MD/RD 分布 3/1、4/1、4/0 |
| 王子贤（241250106） | EChecker 增量检测：`incremental-request.json`、`incremental-response.json`、`md-only-report-c0.json`、`repair-request.json`、`artifacts/minicalc/{c1,c2}/` | `b75b40f`（devops_lab_a03） | 生成 Minicalc 产物与增量样例 | 增量样例通过完整校验（含 artifact 解析） |
| 刘馨蔓（241250107） | 契约校验与质量：`validate.py` 回归、`artifacts/index.json` 哈希、`docs/VERIFICATION.md`、`docs/AI_USAGE.md` | `4e74f03`（devops_lab_a03） | 校验脚本与产物哈希验证 | `python validate.py` 27 样例通过，Minicalc 7 样例通过 |

可用 `git log --format="%H %an <%ae> %s"` 获取真实版本、作者和说明。

## 验证命令

```bash
# 共享样例 + 产物哈希（Windows 需先设置 UTF-8）
$env:PYTHONUTF8=1
python validate.py

# A 组 Minicalc 样例（完整校验，含 artifact 解析）
python validate.py contracts/examples/minicalc/full-request.json
python validate.py contracts/examples/minicalc/full-response.json
python validate.py contracts/examples/minicalc/error-report-c0.json
python validate.py contracts/examples/minicalc/md-only-report-c0.json
python validate.py contracts/examples/minicalc/incremental-request.json
python validate.py contracts/examples/minicalc/incremental-response.json
python validate.py contracts/examples/minicalc/repair-request.json
```

## 未完成项

- C2 镜像已拉取并 `docker run` 冒烟验证通过（4 个断言 PASS）；C0/C1 环境待 B 组补充。
- 真实检测器（BuildChecker/EChecker 算法）未实现，当前产物由 `gcc -MM` 辅助生成；Checker 联调留到 E3。
