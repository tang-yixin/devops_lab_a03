# AI使用记录

工具/模型/日期：WorkBuddy AI 助手（腾讯混元 Hy / Tencent Hunyuan Hy）/ 2026-11-14。

输入上下文与问题：E8-E9 组员操作手册（`E8-E9_组员操作手册_20261114.md`）、教师分发包
`DevOps_E8_E10` 的 `02_操作手册/8_E8_A组.md`、`9_E9_A组.md`、`08_个人测试编写示例.md`、
`03_实验包/classroom_helpers.sh`、`04_模板/` 三份模板、仓库 `labs/e8e10/lab.py` 参考实现，
以及已合并的组长 `docs/students/241250061/e8-e10/` 三份报告与 `StudentE8A241250061` /
`StudentE9A241250061` 测试类。用户委托 AI 代为在服务器上按顺序执行 E8/E9 全流程、编写两个
自有测试、填写三份报告并完成 PR/合并/归档；学号 241250093 与服务器登录口令由用户提供，
身份经本地文件 `241250093 李翔宇 第一次实验作业.png` 与用户确认。

模型建议：
- 按手册拆分为「同步 main → 建分支 → 构建镜像 → E8 逐框 → E9 逐提交 → 加测试 → 三份报告 →
  PR/双门禁/合并 → artifact/tar」的可核对步骤，每步打印 PASS 标志并保存 steps 日志；
- 用 SFTP 整文件上传测试代码与报告，避开 bash→ssh→容器 heredoc 多层转义；
- 两个自有测试严格采用手册分配给 241250093 的方向，且先写独立预期再运行；
- 报告中「学生源码 SHA」取 OUT/student-source-commit.txt（外层 `4ad24d11…`），
  与样例 project 内部 C0–C3 SHA 分开记录，不串用；
- 遵循「写文件步骤失败不原样重跑」的坑位提醒，把 E9 的 C1/C2/C3 拆成独立会话顺序执行。

采纳/拒绝及理由：
- 采纳「只加测试、不改 lab.py」：保持教师参考实现与 E10 矩阵预期，降低 CI 风险（见 ADR）。
- 拒绝照抄组长的 OUT / C0–C3 SHA / trace 行号：全部数据取自本人 `work/e8-A-manual.9id8kE`、
  `work/e9-A-manual.DNoKlY` 的实际输出，验收可当场抽查。
- 拒绝把保守刷新改为受影响目标粒度刷新：与 E10 六场景矩阵断言冲突，留作扩展计划。

人工修改：无代码级人工改动。学号与服务器口令由用户提供；报告中的姓名、校区、轨道等个人信息沿用
本人既有 E5—E7 报告口径；完成报告由用户自行发送给组长（AI 不代发外部消息）。

实际验证命令/输入/结果：
- `python3 run_lab.py build` → ENV_BUILD_EXIT=0；`docker image inspect course-e8e10:241250093`
  → sha256:7791e434…；`gcc --version` → 14.2.0；`lab_ready` 输出仓库/学号/镜像三行。
- E8（OUT `work/e8-A-manual.9id8kE`）：CREATED、BASELINE_PASS、BUILDCHECKER_BASELINE_PASS、
  REUSE_PASS `['main.o','helper.o'] []`；内层 git status 干净。
- E9（OUT `work/e9-A-manual.DNoKlY`）：CREATED、C0_BUILD_AND_BASELINE_PASS（app 输出 1）、
  C1_REUSE_PASS、C2_REFRESH_PASS（added=[[MISSING,main.o,extra.h]]）、
  C3_RESOLVED_PASS（resolved 两条、findings 仅余 REDUNDANT unused.h）；
  `git log --oneline --reverse` = 4784da1 / b69a813 / c9f2a5d / 669b537，与四份 JSON 一致。
- 定向测试：`docker run ... python3 -m unittest discover -s labs/e8e10 -p test_profile.py -v`
  → `work/unit-tests-20261114-184641.log`：`Ran 13 tests ... OK`，退出码 0。

参考实现与个人贡献边界：`lab.py`、`run_lab.py`、`classroom_helpers.sh`、`.github/workflows/e8e10.yml`、
课程模板与全部 fixtures 均来自教师参考包，未修改；组内已合并的 11 项基线测试（含组长 4 项）保持原样。
个人贡献 = `labs/e8e10/test_profile.py` 中 `StudentE8A241250093` / `StudentE9A241250093` 两个类共 2 个用例、
`docs/students/241250093/e8-e10/` 三份报告，以及本人两个 OUT 证据目录与归档。服务器操作由 AI 受托执行，
输入与输出完整留痕于 `work/` 下的 steps 日志、build 日志与 unit-tests 日志。
