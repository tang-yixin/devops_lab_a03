# E7 阶段说明（A03 · A 轨道 BuildChecker）

> 任务：验证与 CI 门禁。本地完整 gate 八场景（同一样例三次一致 / 修复清零 / 构建失败 /
> 多输出 / 超时）+ GitHub Actions 全流程（正常 CI → main 分支保护 → 故意失败 PR 被实际
> 拒绝合并 → 修复 → 恢复合并）+ 每人一项新增判定测试。
> E7 为 E4—E7 系列最后一阶段，本文件为收尾终版（2026-11-09，四人均交付）。
> 个人交付物在各 `docs/<学号>/` 目录；报告模板在 `docs/e7/templates/`。

## 1. 完成情况（2026-11-06 至 11-09，四人交付并合并）

| 学号 | 个人分支 | PR（均 MERGED） | 新增判定测试方向 | 判定测试数* | gate（首轮/复跑） | 归档（~/devops-submissions/） |
|---|---|---|---|---|---|---|
| 241250061 | student/241250061/e5-e7 | #16（307ba33，11-06 07:33Z） | original 多出一条 finding 必须拒绝（含对照） | 7→8 | e7-01 / e7-02 均 8/8 | buildchecker-E4-E7-20261106-153358.tar.gz |
| 241250093 | student/241250093/e5-e7 | #17（b5022ef，11-06 14:29Z） | finding 缺少 evidence 必须拒绝（含对照） | 7→8 | e7-01 / e7-02 均 8/8 | buildchecker-E4-E7-20261106-223025.tar.gz |
| 241250107 | student/241250107/e5-e7 | #18（6a82c4d，11-06 16:51Z） | 报告缺 trace_id 必须拒绝（含对照） | 7→8 | e7-01 / e7-02 均 8/8 | buildchecker-E4-E7-20261107-005147.tar.gz |
| 241250106 | student/241250106/e5-e7 | #19（1e8c6a8，11-09 05:00Z） | 有 findings 但退出码 0 必须拒绝（4 用例，含 fixed 对称方向） | 9→13 | e7-01 / e7-02 均 8/8 | buildchecker-E4-E7-20261109-130019.tar.gz |

\* 判定测试数 = 首次运行项数 → 本人测试并入后项数。首次数 = 6 项基线 + 当时已并入 main 的
组员测试数：061/093/107 在 main=307ba33（仅组长已并）时首轮均为 7；106 最晚开始，
首轮时 main=6a82c4d（061+093+107 已并）为 9，其测试含 4 个用例故一步到 13。
**四人合并后 main 上判定测试共 13 项**（`python3 -m unittest discover -s tests/e7`）。

- 两轮 gate（e7-01 加测试前 / e7-02 加测试后重建复跑）均 8 项全 `passed=true`、退出 0，
  复跑 7 个 trace_id 全部换新；unit-tests 场景服务测试 24 项（CI 演示测试已并入；
  判定测试不进服务镜像，不影响该数）。
- 各人证据要点一致：三次 original 错误集合精确为 MISSING(main.o, config.h) +
  REDUNDANT(main.o, unused.h) 且 trace_id 互异；fixed findings=[] 且 input_sha256 仅
  Makefile 变化；build-failed→CHECK_FAILED、unsupported→UNSUPPORTED、timeout→TIMED_OUT
  按预期识别（工具退出 1 与场景 PASS 并存为正确语义）。
- 各人 CI：PR run 均 success 后在保护规则下**自行合并**（六条自检标准见组员手册 §9），
  artifact 均在 14 天保留期内下载至各自 `work/ci-pr/`。

## 2. CI 闭环记录（组长执行，每组一次，2026-11-06）

| 阶段 | 运行 / PR | head SHA | 结论 | 证据位置（组长克隆 work/） |
|---|---|---|---|---|
| main 正常 CI | run [42157632198](https://github.com/tang-yixin/devops_lab_a03/actions/runs/42157632198) | fcc98d5 | success（gate 8/8，commit.txt 一致） | ci-normal/ |
| 分支保护 | —（check-runs 实查 App 15368） | — | e7-a-quality-gate / strict=true / enforce_admins=true / 审批 0 | ci-setup/ |
| 故意失败 PR [#15](https://github.com/tang-yixin/devops_lab_a03/pull/15) | run 42157951461 | 0173a7d | failure（assert 0 == 1，见 artifact gate/unit-tests/stdout.log）；普通合并被拒退出 1，OPEN/BLOCKED | ci-rejection/ |
| 修复恢复（同一 PR） | run 42159043852 | 8cc1459 | success（24 passed）→ MERGED（60158b4，11-06 03:54Z） | ci-recovery/ |

## 3. 交付物与位置

| 交付物 | 位置 | 说明 |
|---|---|---|
| 判定测试 | `tests/e7/test_e7_<学号>.py` ×4 + test_e7_a_gate.py | main 共 13 项，方向互不重复（多一条 finding / 缺 evidence / 缺 trace_id / 退出码不符） |
| 个人报告 | `docs/<学号>/实验报告.md` E7 与 CI 节 | 共享 CI 闭环事实 + 本人运行数据；验收记录 C04/C05/C06/A02 全 PASS（B01–B03 N/A） |
| 原始证据 | 服务器各人克隆 `work/`（e7-build-01 / e7-01 / build-02 / e7-02 / ci-pr）；组长另有 ci-normal / ci-setup / ci-rejection / ci-recovery | 组长本机 `work/<学号>/` 存四人镜像，不进 git |
| 归档备份 | 服务器 `~/devops-submissions/<学号>/*.tar.gz` ×4 | 组长本机 D:\DevOps\E7\submissions\ 另存四人 tar |

## 4. 关键事件与备注

- **E7 包 GBK 文件名乱码（11-06）**：与 E6 同款问题，unzip 后 17 个中文名文件乱码、
  check_package 失败；按 E6 方法用 Python zipfile 按 GBK 还原文件名重解压，1123 文件
  校验通过。包内代码与仓库逐字节一致（仅行尾差异），组员全程未接触课程包。
- **保护启用时机**：docs/e7 脚手架与模板直推（fcc98d5）是 main 最后一次直推；此后
  enforce_admins=true 对组长同样生效，一切变更走 PR（含本收尾文档）。
- **串行协议实战**：三人 PR 按"CI 绿 + CLEAN → 自行合并；BEHIND → fetch + merge
  origin/main + push 追平"执行，全程无冲突（测试文件与 docs 均按学号隔离），
  无人需要等待他人全流程完成；106 晚三天开始，首轮判定 9 项与机制预期一致。
- **gh 2.4.0 坑**：`run list` 无 `--branch`、`pr view` 无 `headRefOid`（用 `commits[-1].oid`）、
  `pr checks` 退出码不可信——一律按 headSha 与输出文本判定。
- **merge-ref 说明**：pull_request 事件 run 检出的是 refs/pull/N/merge，artifact 内
  commit.txt 是合并预览 SHA，与 PR head SHA 不同属正常（核对以 run 元数据 headSha 为准）。
- **GitHub 抖动**：11-06 多次 GnuTLS -110 / 443 超时（最长一轮 3 次失败后第 4 次成功）；
  重试 ≤5 次的口径全程够用。
- **终态**：四人交付合并后 main 最新 run 42564785219（1e8c6a8）success；
  secret_scan 295 文件含历史未发现问题。

## 5. 仓库结构（E7 完成后）

    devops_lab_a03/
    ├── docs/
    │   ├── e5/ e6/ e7/                   阶段说明（本文件为 e7 终版）
    │   ├── e7/templates/                 E7 报告/验收记录教师模板
    │   └── 241250061/ 241250093/ 241250106/ 241250107/
    │                                     每人：实验报告.md（E5/E6/E7 节已填）/ 验收记录.csv
    ├── tests/e7/                         判定测试：test_e7_a_gate.py（6）+ test_e7_<学号>.py ×4（1+1+1+4）共 13 项
    ├── services/buildchecker/tests/      服务测试 24 项（含 CI 演示测试 test_ci_reject_demo.py）
    ├── scripts/ services/ fixtures/ course-support/ .github/
    │                                     E5—E7 课程工作区（入口 scripts/course.py；
    │                                     .github/workflows/e7-quality-gate.yml = CI 门禁）
    ├── work/                             个人运行证据（不进 git；组长本机 work/<学号>/ 存镜像）
    └── e2-a03/ e3-a03/ e4-a03/           E1—E4 历史成果（只读）

## 6. E7 之后

E7 为 E4—E7 系列最后一阶段，本文件即终态。main 受 `e7-a-quality-gate` 必需检查保护
（strict / enforce_admins / 审批 0 / 仅 PR 合并），后续任何变更继续从个人分支发 PR。
