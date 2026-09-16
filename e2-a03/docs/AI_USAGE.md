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

## 记录 5：产物引用方式

- **工具/模型**：DeepSeek（初版）、GitHub Copilot（对齐 B 组后复审）
- **任务**：决定依赖图等大产物如何在 A、B 组之间交接
- **AI 建议**：初版把依赖图 JSON 直接内联进 `Job.output`；后改为
  `ArtifactRef` 对象（含 `read_method` 字段）。
- **人工判断**：内联会让每个 Job 响应膨胀，且无法单独下载或校验完整性；
  `read_method` 是 A 组自定义字段，B 组草案没有，属于"契约外字段"。
  B 组草案采用 `artifact://<dir>/<name>` → `artifacts/<dir>/<name>` 目录映射 +
  `index.json` 注册 SHA-256 的方案，更可离线校验，且是双方共同契约。
- **采纳/修改/拒绝**：**修改**。对齐 B 组方案：`output` 只返回 URI 字符串，
  产物元数据（`artifact`）必填 `sha256`，解析器只访问 `artifacts/` 目录内
  已注册文件。
- **关联文件**：`docs/ADR-003-artifact-by-reference.md`、
  `contracts/task.schema.json`（`$defs.artifact`）、`artifacts/index.json`
- **验证方式与结果**：`python validate.py`（无参数）返回
  `27 examples ... artifact references and SHA-256 verified`，证明
  `artifact://demo/*` 引用与哈希校验通过。A 组独有 Minicalc 产物
  （`artifacts/minicalc/`）尚未生成，留到 E3。
- **版本**：见 `CONTRIBUTIONS.md` 中对应提交 SHA

---

## 记录 6：A 组初版契约与 B 组草案的字段冲突

- **工具/模型**：GitHub Copilot（辅助比对 B 组 `a-group-project`）
- **任务**：核对 A 组初版契约与 B 组草案的差异，决定是否对齐
- **AI 建议**：初版与 B 组在 `build`、`environment`、`output`、`error`、
  `Finding` 结构上存在多处冲突（如 `clean_build_command` vs
  `command/clean_command/verify_command`，内联 `ArtifactRef` vs URI 字符串，
  4 个错误码 vs 9 个错误码，`location` 字符串 vs 对象）。
- **人工判断**：B 组是下游消费者，且提供了 `shared-lock.json` 做逐字节
  一致性校验，说明双方应共享同一份契约文件。自行保留差异会增加对接摩擦，
  且无法通过 B 组的哈希校验。
- **采纳/修改/拒绝**：**采纳对齐**。直接采用 B 组的 `task.schema.json`、
  `openapi.json`、`validate.py`、27 个共享样例（逐字节一致），
  保留 A 组自己的 ADR 论证与 Minicalc 真实数据样例。
- **关联文件**：`contracts/task.schema.json`、`contracts/openapi.json`、
  `contracts/shared-lock.json`、`contracts/examples/`、`validate.py`
- **验证方式与结果**：`python validate.py` 返回
  `PASS: 27 examples (19 valid, 8 expected rejections)`；A 组 Minicalc
  样例单独校验通过（见 BACKLOG E2-A02~A05）。
- **版本**：见 `CONTRIBUTIONS.md` 中对应提交 SHA

---

## 记录 7：用 Minicalc 真实数据替换占位符

- **工具/模型**：GitHub Copilot（辅助编写样例）
- **任务**：把 A 组样例中的 `<full-sha>`、`<C0-full-sha>`、`<C1-full-sha>`
  等占位符替换为真实目标项目 Minicalc 的数据
- **AI 建议**：直接使用 Minicalc 仓库的 C0/C1/C2 三个 tag 的完整 SHA，
  并用 `gcc -MM` 核对了 README 声称的依赖缺陷。
- **人工判断**：人工复核了 Makefile 规则行号（C0：main.o 在第 30 行、
  parser.o 在第 34 行、util.o 在第 41 行），确认 C0 的 3 MISSING + 1 REDUNDANT
  与 README 一致；`main.o→token.h` 是传递依赖（main.c → parser.h → token.h），
  按"编译器实际读取"口径应计入 MISSING。
- **采纳/修改/拒绝**：**采纳**。生成 `contracts/examples/minicalc/` 下 7 个样例
  （full/incremental 请求与响应、error-report、md-only-report、repair-request）。
- **关联文件**：`contracts/examples/minicalc/*.json`
- **验证方式与结果**：4 个不涉及 artifact 解析的样例通过完整校验；
  3 个涉及 artifact 解析的样例通过 `--structure-only` 结构校验
  （真实产物留到 E3 生成）。
- **版本**：见 `CONTRIBUTIONS.md` 中对应提交 SHA

---

## 待办：尚未验证的事项

以下内容**不能**写成"已验证"，需在与 B 组对接后补充：

- [ ] B 组能否实际读取 `artifact://` 引用的文件（PPT 第 24 页要求 E12 证明）
- [ ] B 组 MDFixer 是否只消费 `type=MISSING` 的 finding
- [ ] `configuration_id` 的最终取值（当前用 `cc-default`，待 B 组确认）
- [ ] 构建镜像的最终取值（当前占位 `e2-fixture:contract-example-only`，
      待 B 组提供可运行镜像）
- [ ] 课堂三轮配对练习的实际结论
- [ ] Minicalc 真实产物（`artifacts/minicalc/`）的图、证据、报告生成（E3）

> 注：记录 1~4 中的 `tools/validate.py`、`artifact.example.json` 等路径是
> 当时中间状态的名称，现已统一为根目录 `validate.py` 与 B 组共享样例
> `contracts/examples/`，见记录 6。
