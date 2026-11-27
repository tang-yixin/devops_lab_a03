# AI使用记录（E10-E12 续写）

工具/模型/日期：WorkBuddy AI 助手（腾讯混元 Hy / Tencent Hunyuan Hy）/ 2026-11-27（E8/E9 段见下方，执行日 2026-11-14）。

## 本次输入上下文与问题

`E10-E12_组员操作手册_20261126.md`、教师手册 `DevOps_E8_E10/02_操作手册/10_E10_A组.md`、
`DevOps_E11_E12/02_操作手册/` 四份（公共准备、E11 轨道内集成、E12 接口联调、真实项目接入）、
`04_模板/` 四份模板、仓库 `labs/e8e10/lab.py` / `labs/e11e12/{pipeline,server,test_contract}.py`、
组长 `docs/students/241250061/e11-e12/` 参考报告与 `StudentE10A241250061` 类、
`/root/devops-materials/real-project-integration/real-dataset.json`。用户委托 AI 在服务器上按顺序完成
E10 补做、E11/E12 与真实项目接入、两个自有测试、七份报告、两个 PR、三门禁自行合并与证据归档；
学号 241250093 由用户明确给出，服务器新口令由手册提供。

## 模型建议与采纳情况

- 按手册拆成「重新认证 → 同步 main/建两分支 → 两镜像 → E10 逐框 → E11 A/B + 两条自主任务 →
  E12 五阶段 + API 五契约 → 真实项目 → 两测试 → 七份报告 → 两 PR/三门禁/合并 → artifact/tar」，
  每步打印 PASS 标志并把 steps 日志留在 `work/`。**采纳**。
- 多行远程命令不走命令行参数（换行会被拼接吃掉），改用本地 `.sh` 文件经标准输入送入 SSH 会话；
  Python 代码块用 `<<'PY'` heredoc。**采纳**，E10 步骤 0–7 / 8–14 各一次会话，步骤退出码全 0。
- 测试与报告用 SFTP 整文件上传，上传前本地 `ast.parse` 语法预检。**采纳**。
- 自主场景先写 `selfcase-expected.txt` 独立预期再跑；性能比值 <1 照实保留。**采纳**。
- E11 自主任务①把 base/target 对调、②把 fixed-md 信封 commit 改成 40 个 0 得到 STALE_REPORT，
  均用新的 `work/` 子目录保留原结果。**采纳**。
- API 重启契约不睡固定秒数，提交后 0.02 秒间隔轮询 `state.json`，状态一变 RUNNING 立即 `docker kill`。**采纳**，
  第 1 次轮询就抓到 RUNNING，重启后任务标 `SERVER_RESTARTED`。

## 拒绝/修正的建议

- **拒绝**照抄组长或他人的 OUT 路径、base/target SHA、job_id、trace_id：本人 `prepare` 生成的
  `9317562… / 0a0fa4a…` 与所有 job_id/trace_id 均取自本人 `work/` 输出，报告与 CSV 逐一核对。
- **拒绝**复用组长 `devops-auth/241250061` 的 token：本人历史 PR 作者是 `hardtosleep`，
  改用设备码重新授权本人账号（见 ADR 第 8 条）。
- **修正**：`gh auth login --web` 首次报 `Post https://github.com/login/device/code: unexpected EOF`，
  改用 curl 直连 GitHub OAuth device 端点取 user_code，用户浏览器输码后由脚本轮询 access_token 并写 hosts.yml。
- **修正**：本机默认 Python 换成 3.13 后无 paramiko，改用装有 paramiko 4.0.0 的 Python 3.10 解释器。
- **拒绝**把自主场景 5 行塞进 30 行主矩阵：会破坏 `len(rows)==30` 断言，改为独立 CSV/JSON。

## 人工参与

学号、服务器旧/新口令、GitHub 设备码授权（浏览器 revoke 旧授权 + 输入一次性码）由用户完成；
其余服务器操作由 AI 受托执行。完成报告由用户自行发送给组长，AI 不代发外部消息。

## 实际验证命令/输入/结果（本次）

- `python3 run_lab.py build` → ENV8_EXIT=0（`sha256:ad43eccb…`）；`python3 run_e11e12.py build` →
  ENV11_EXIT=0（`sha256:4e5cb7c1…`）；`lab_ready` 输出仓库/学号/镜像三行。
- E10 `work/e10-A-manual.mce6fE`：30 行 equal=True、MATRIX_PASS、gate rows=30；自主场景 5 次全刷新、
  findings 不变、full_over_inc=0.9772；`final-buildchecker` status=SUCCEEDED。
- E11-A `work/e11-a-01`（job-6989a805…）、E11-B `work/e11-b-01`（job-34acab59…）、
  对调 `work/e11-a-02`（job-3b825a95…）、STALE `work/e11-b-stale-01`（job-975dc4d2…）。
- E12 固定样例 `work/e12-01`（job-420ca6cc…）、真实项目 `work/e12-real-01`（job-01842573…）。
- API `work/api-client/联调记录.json` 与 `重启契约.json`：health 200、5 条契约全通过、
  `X-Content-SHA256` 与清单一致。
- 测试：e8e10 套件 23 项 OK（`work/unit-tests-e10-20261127-163740.log`）；e11e12 套件见
  `work/unit-tests-e11e12-*.log`。

## 参考实现与个人贡献边界

教师参考包（`lab.py`、`pipeline.py`、`server.py`、`run_lab.py`、`run_e11e12.py`、`classroom_helpers.sh`、
全部 fixtures、手册代码块）与组长适配代码（`set_profile` / profile 请求字段 / real-candidate.Dockerfile）
均来自他人，**未修改**；E8/E9 段三份报告原文保留。个人贡献 =
`labs/e8e10/test_profile.py` 的 `StudentE10A241250093` 类（2 用例）、
`labs/e11e12/test_contract.py` 的 `StudentContract241250093` 类（2 用例）、
`docs/students/241250093/e8-e10/` 三份续写与 `docs/students/241250093/e11-e12/` 四份模板填写，
以及本人 `work/` 下四个 OUT 系列、API 联调记录与证据归档。所有对外操作（PR、合并）经用户授权执行。
