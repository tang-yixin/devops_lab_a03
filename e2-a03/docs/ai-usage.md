# AI_USAGE.md

本文件记录 E2 期间 AI 参与设计的过程证据。每条记录包含：工具/模型、任务、
AI 建议摘要、人工判断与理由、采纳/修改/拒绝、关联文件与版本、验证方式与结果。

> 说明：以下记录均为实际发生的过程。凡尚未与 B 组实际对接验证的事项，
> 一律标注为「待验证」，不写成已完成。

---

## 记录 1：统一任务模型的状态枚举命名

- **工具/模型**：DeepSeek（对话式生成初版契约）
- **任务**：设计 `task.schema.json` 中 `status` 字段的取值集合
- **AI 建议**：使用 `PENDING` / `DONE` 两个状态，理由是"简单直观"
- **人工判断**：不采纳。课程 PPT 第 8 页明确要求区分
  `QUEUED` / `RUNNING` / `SUCCEEDED` / `FAILED` / `TIMED_OUT` / `CANCELLED`。
  AI 的两状态模型无法表达"已受理但未开始"与"执行中"的区别，
  也无法表达超时和取消这两种终态，会导致 B 组无法判断任务是否还在跑。
- **采纳/修改/拒绝**：**修改**。保留 AI 的"状态机"思路，但按课程规范
  扩展为六状态枚举。
- **关联文件**：`contracts/task.schema.json`（`status` 字段）
- **验证方式与结果**：在 `tools/validate.py` 中加入 `ALLOWED_STATUS` 白名单，
  构造 `status=PENDING` 的非法样例，校验器正确拒绝（`[FAIL] Job 非法 status`）。
- **版本**：见 `personal-contribution.md` 中对应提交 SHA

---

## 记录 2：`error` 字段与 `null` 的契约冲突

- **工具/模型**：GitHub Copilot（辅助审查 schema 与样例一致性）
- **任务**：检查 `task.schema.json` 与两个 Job 响应样例是否自洽
- **AI 建议**：初版 schema 将 `error` 定义为 `{ "$ref": "#/$defs/JobError" }`，
  即只接受对象类型
- **人工判断**：这是真实缺陷。两个 Job 样例在成功时写的是 `"error": null`，
  用 JSON Schema 校验器实测报错：
  `path=['error'] | None is not of type 'object'`。
  契约必须能表达"成功时没有错误"这一正常情况。
- **采纳/修改/拒绝**：**修改**。改为
  `"error": { "oneOf": [{ "$ref": "#/$defs/JobError" }, { "type": "null" }] }`，
  使 `error` 在成功时为 `null`、失败时为 `JobError` 对象。
- **关联文件**：`contracts/task.schema.json`、`contracts/full-check-job.example.json`、
  `contracts/incremental-check-job.example.json`
- **验证方式与结果**：用 `jsonschema` 的 `Draft202012Validator` 校验，
  两个 Job 样例由「报错」变为 `VALID`；同时新增负向用例
  "SUCCEEDED 却带 error"，校验器正确拒绝。
- **版本**：见 `personal-contribution.md` 中对应提交 SHA

---

## 记录 3：`validate.py` 的覆盖范围不足

- **工具/模型**：GitHub Copilot（辅助审查校验脚本）
- **任务**：核对 `tools/validate.py` 是否满足 PPT 第 25 页
  "运行 validate.py，检查四类请求与响应"
- **AI 建议**：初版脚本只实现了 `FULL_CHECK` 与 `INCREMENTAL_CHECK`
  两个分支，`DRAFT` 与 `REPAIR` 传入后会直接输出 `[PASS]` 而不做任何检查
- **人工判断**：这是"假通过"，比不检查更危险——B 组会误以为 DRAFT/REPAIR
  请求已被验证。另外脚本完全不校验 Job 响应样例，
  无法验证 ADR-002（错误与发现分离）是否被契约正确表达。
- **采纳/修改/拒绝**：**修改**。重写为：
  1. 用 `REQUIRED_INPUT` 表覆盖四类请求的必填字段；
  2. 新增 `validate_job()` 校验响应样例的 status 枚举、
     `error` 与 `status` 的一致性、`findings` 结构；
  3. 支持一次传入多个文件，失败时返回退出码 1。
- **关联文件**：`tools/validate.py`
- **验证方式与结果**：构造 10 个非法输入用例（非法 `job_type`、
  缺 `environment`/`build`/`baseline`/`base_commit`、
  `baseline.commit` 不匹配、`baseline.configuration_id` 不匹配、
  非法 `status`、`SUCCEEDED` 却带 `error`、非法 `finding.type`），
  **10/10 全部被正确拒绝**；4 个有效样例全部 `[PASS]`。
- **版本**：见 `personal-contribution.md` 中对应提交 SHA

---

## 记录 4：文件名拼写错误

- **工具/模型**：GitHub Copilot（辅助检查交付物清单）
- **任务**：核对 `contracts/` 目录文件名与 PPT 第 24 页、Backlog 的约定是否一致
- **AI 建议**：生成时把产物样例命名为 `aritifact.example.json`
- **人工判断**：拼写错误，正确拼写为 `artifact`。
  PPT 第 24 页与 `docs/backlog.md` 中均写作 `artifact.example.json`，
  文件名不一致会导致 B 组按约定路径找不到文件。
- **采纳/修改/拒绝**：**修改**。重命名为 `artifact.example.json`。
- **关联文件**：`contracts/artifact.example.json`
- **验证方式与结果**：重命名后 `contracts/` 目录清单与 Backlog 约定一致。
- **版本**：见 `personal-contribution.md` 中对应提交 SHA

---

## 记录 5：产物引用方式（待与 B 组确认）

- **工具/模型**：DeepSeek
- **任务**：决定依赖图等大产物如何在 A、B 组之间交接
- **AI 建议**：把依赖图 JSON 直接内联进 `Job.output`
- **人工判断**：不采纳。依赖图、日志体积大，内联会让每个 Job 响应膨胀，
  且无法单独下载或校验完整性。PPT 第 24 页要求"Job 保存元数据，
  大文件通过引用交接"。
- **采纳/修改/拒绝**：**修改**。改为 `ArtifactRef` 引用，
  含 `artifact_id` / `type` / `uri` / `media_type` / `producer_job_id` /
  `sha256` / `commit` / `configuration_id`，并新增 `read_method` 字段
  说明下游读取方式。
- **关联文件**：`contracts/artifact.example.json`、`contracts/task.schema.json`
  （`$defs.ArtifactRef`、`$defs.ReadMethod`）、`docs/adr-003-artifact-by-reference.md`
- **验证方式与结果**：`artifact.example.json` 通过 `ArtifactRef` 的
  JSON Schema 校验。**`read_method` 的具体取值（HTTP 端点还是共享卷路径）
  尚未与 B 组确认，待课堂配对练习后回填。**
- **版本**：见 `personal-contribution.md` 中对应提交 SHA

---

## 待办：尚未验证的事项

以下内容**不能**写成"已验证"，需在与 B 组对接后补充：

- [ ] B 组能否实际读取 `artifact://` 引用的文件（PPT 第 24 页要求 E12 证明）
- [ ] B 组 MDFixer 是否只消费 `type=MISSING` 的 finding
- [ ] `configuration_id` 的最终取值（当前占位 `cc-MODE0`）
- [ ] 构建镜像与 `clean_build_command` 的最终约定
- [ ] 课堂三轮配对练习的实际结论
