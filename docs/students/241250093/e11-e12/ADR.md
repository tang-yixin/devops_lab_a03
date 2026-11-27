# ADR：集成接口决策（241250093）

编号、日期、作者：ADR-E11E12-093 / 2026-11-27 / 241250093 李翔宇

## 问题

E11/E12 要在一条流水线里把 BuildChecker 真实图、EChecker 增量检测、DRAFT 候选构建、MDFixer 补丁串起来，
且 E12 的 repair **必须消费本轮 incremental-check 的真实报告**（不能再用 E11-B 的固定 MD）。
同时要在共享服务器上完成 API 五条契约，其中「服务重启」要求在任务 RUNNING 时强杀 serve 容器——
缓存已热，固定样例任务约 6–8 秒就完成，睡固定秒数必然杀到已完成任务，演示会失败。
还要保证本人数据（prepare SHA / job_id / trace_id）与组长样例完全分开。

## 候选方案

1. **STALE_REPORT 演示**：改 fixed-md 信封 commit / 改 data.commit / 伪造一个不存在的报告路径。
   选「改信封 commit 为 40 个 0」——`check_envelope` 正是按信封 commit 与 target 比对，能精确复现
   「输入版本不一致时停止修复」；改 data.commit 会在更后面被拦，演示不到信封层；伪造路径只会得到 OSError。
2. **E11 自主提交对**：把 base/target 对调 / 用 C0 与 C0 自身 / 另造一个提交。选对调——两个提交都是真实历史，
   不需要改样例仓库，且能看到「反向 diff」下 key 变化导致的全刷新与 `resolved`。
3. **重启契约**：提交后睡 2 秒再 kill / 轮询 HTTP 状态 / 轮询宿主 `state.json` 文件。
   选 0.02 秒间隔直接读 `work/api-jobs/<job>/state.json`——比 HTTP 轮询少一跳，实测第 1 次迭代就抓到 RUNNING。
4. **evdience 组织**：所有 run 共用一个 OUT 覆盖 / 每个实验独立 OUT。选独立 OUT（手册 §12 明确
   `OUTPUT_EXISTS` 要换新目录，原结果保留），失败演示也不覆盖成功证据。
5. **认证**：复用组长 `devops-auth/241250061` 的 token / 重新授权本人账号。选后者（见 E10 ADR 第 8 条）。

## 采用方案与原因

采用 1「改信封 commit」+ 2「base/target 对调」+ 3「0.02 秒轮询 state.json 立即 kill」+ 4「独立 OUT」+ 5「本人设备码授权」。
原因：全部可在不修改教师参考实现、不假装数据的前提下完成；失败演示的 `result.error` 与成功链路的
`result.json` 各自留痕，验收时能逐条对照；重启演示不依赖任务耗时的运气。

## 输入输出字段

- E11 请求：`mode` / `repo`（必须 `/course/data/...` 容器路径）/ `base` / `target`（40 位完整 SHA）/
  `candidate` / `fixed_report` / `expected_output` / `build_timeout`；真实项目额外带 `profile`
  （4 个对象目标、src/+include、flags 白名单、key_globs、build/run、header 检查）。
- 输出 envelope：`schema_version=e11e12-1`、`job_id`、`trace_id`、`kind`、`commit`、`status`、
  `data`、`artifacts[{uri,sha256,bytes}]`；`artifact://<job_id>/<相对路径>` 映射到
  `GET /v1/jobs/<job_id>/files/<相对路径>`，响应头 `X-Content-SHA256` 必须与清单 sha256 一致。
- 消费约束：`check_envelope(report, target_sha, kind)` 验 schema/commit/status/kind；
  `load_artifact` 验内容哈希；`patch()` 再验 `report.commit == HEAD`，否则 `STALE_REPORT`。

## 兼容性与测试

- 固定样例与真实项目**分开验收**：固定样例 `recheck` 仍保留 `REDUNDANT(main.o,unused.h)`；
  真实项目因 c2 提交让 util.c 真实引用 legacy.h，`recheck findings=[]`。报告如实记录这一差异，
  没有把固定样例结论硬套到真实项目。
- 本人新增 `StudentContract241250093`（`labs/e11e12/test_contract.py`，2 用例）覆盖幂等键空串/非字符串
  的拒收分支，并断言拒绝发生在写 `keys`/`jobs` 之前、不产生 `job-*` 目录；HTTP 层对应的 400 由
  `work/api-client/联调记录.json` 实测记录。
- 五条 API 契约实测：重放 202 同 job_id、冲突 409、缺 repo 400、失败 `INVALID_REQUEST` 换键重试成功、
  RUNNING 被 kill 后 `SERVER_RESTARTED` 且旧完成任务仍可查/可下载。
- 代价：轮询 `state.json` 依赖容器与宿主共享挂载（本课程镜像正是 `-v $PWD:/course`），
  换成非挂载部署需改回 HTTP 轮询；本 ADR 只适用于当前课堂环境。
