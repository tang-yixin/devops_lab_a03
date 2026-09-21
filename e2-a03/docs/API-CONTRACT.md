# E2 A 组接口契约：BuildChecker / EChecker

> 本契约已与 B 组 `b-group-project` 草案对齐。共享文件
> （`task.schema.json`、`openapi.json`、`validate.py`、`contracts/examples/`）
> 以 `contracts/shared-lock.json` 记录的 SHA-256 为准，双方一致。
> A 组独有样例（真实目标项目 Minicalc）在 `contracts/examples/minicalc/`。

## 1. 角色

- A 组：BuildChecker（全量检测）、EChecker（增量检测）
- B 组：DRAFT（环境生成）、MDFixer（修复缺失依赖）
- 下游：B 组重新构建、测试、重检

## 2. 目标项目

| 项 | 值 |
|---|---|
| 仓库 | `https://github.com/hardtosleep/Minicalc-DevOps-Test.git` |
| 语言/构建 | C11 + Makefile（`make` / `make test`） |
| 基线 C0 | `e3a1eda0965e545d96467d275bccaf78c890fcac` |
| 增量 C1 | `f863c2deff1bd95e56f1578b872ae6aa26e3bfc8` |
| 增量 C2 | `e103bcb3726a3fd7253deb0d791ac74fac77cafe` |
| configuration_id | `cc-default` |
| 构建镜像（C2） | `ghcr.io/wangyuhan29/minicalc-devops@sha256:c4e23321b6f51c9382d2c3b12eef8c9594d8aa9aab01daf8d52928b41f27dc6d`（私有 GHCR，仅含 C2 源码） |

## 3. 统一任务模型

公共字段：`schema_version`、`trace_id`、`job_type`、`execution`、`input`、
`job_id`、`status`、`output`、`error`。

- `job_type`：`DRAFT` / `FULL_CHECK` / `INCREMENTAL_CHECK` / `REPAIR`
- `status`：`QUEUED` / `RUNNING` / `SUCCEEDED` / `FAILED` / `TIMED_OUT` / `CANCELLED`

创建请求必填 `schema_version`、`trace_id`、`job_type`、`execution`、`input`、
`idempotency_key`；服务端生成 `job_id`，HTTP 202 返回 `job_id` + `QUEUED`。
公共任务单不含 `idempotency_key`，包含 `input`/`output`/`error`。

状态语义：

| status | output | error |
|---|---|---|
| QUEUED / RUNNING / CANCELLED | `null` | `null` |
| SUCCEEDED | 必填 | `null` |
| FAILED / TIMED_OUT | `null` | 必填 |

发现 MD/RD 属于 `ERROR_REPORT.findings`，检测成功仍为 `SUCCEEDED`。

## 4. 创建与查询

| 操作 | 端点 |
|---|---|
| 生成构建环境 | POST /v1/dockerfile-jobs |
| 全量检测 | POST /v1/full-check-jobs |
| 增量检测 | POST /v1/incremental-check-jobs |
| 修复缺失依赖 | POST /v1/repair-jobs |
| 查询任务 | GET /v1/jobs/{job_id} |

## 5. 公共输入结构

`repository`：`url`（绝对 URI）、`commit`（40 位小写十六进制 SHA）。

`build`：

| 字段 | 说明 |
|---|---|
| `command` | 构建命令，如 `make` |
| `clean_command` | 干净构建命令，如 `make clean && make` |
| `verify_command` | 验证命令，如 `make test` |
| `working_directory` | 工作目录，必须以 `/` 开头，且等于 `environment.project_root` |

`environment`：

| 字段 | 说明 |
|---|---|
| `image` | 构建镜像。B 组已提供 C2 固定 digest（私有 GHCR，需 `read:packages` 权限）；C0/C1 需对应版本源码另行验证 |
| `configuration_id` | 配置标识，本组用 `cc-default` |
| `project_root` | 项目根目录，必须以 `/` 开头，且等于 `build.working_directory` |

## 6. A 组 BuildChecker（FULL_CHECK）

### 输入
`repository` + `build` + `environment`（同上）。

### 输出（SUCCEEDED）
`output` 只返回四个 URI，具体内容按引用交接：

| 字段 | 指向 |
|---|---|
| `actual_graph_uri` | 实际依赖图 |
| `declared_graph_uri` | 声明依赖图 |
| `error_report_uri` | MD/RD 报告 |
| `evidence_uri` | 证据 |

### 成功语义
检测到 MD/RD 仍为 `SUCCEEDED`；工具没跑完才 `FAILED`/`TIMED_OUT`，
写入 `error`。

## 7. A 组 EChecker（INCREMENTAL_CHECK）

### 输入
`repository`（当前 commit）+ `build` + `environment` + `base_commit` + `baseline`。

`baseline`：`actual_graph_uri`、`declared_graph_uri`、`commit`、
`configuration_id`。校验规则：

- `baseline.commit` 必须等于 `base_commit`
- `baseline.configuration_id` 必须等于 `environment.configuration_id`
- 基线图产物元数据必须匹配同一仓库、旧提交和配置

### 输出（SUCCEEDED）
`output` 含当前图/报告/证据四个 URI，加：

| 字段 | 说明 |
|---|---|
| `added_finding_ids` | 相对基线新增的 finding ID |
| `resolved_finding_ids` | 相对基线消除的 finding ID |

## 8. Finding 与错误报告

`finding`：`finding_id`、`type`（MISSING/REDUNDANT）、`target`、`dependency`、
`commit`、`detector`、`location`（`{file, line}`）、`evidence`。

> 来源说明：`detector` 表示目标服务角色（BuildChecker / EChecker）。当前仓库内的
> Minicalc 样例与产物由 `gcc -MM` 辅助生成并人工整理，**不是**真实动态追踪
> 检测器的运行输出；真实检测器实现见 E3。

### finding_id 生成规则（见 `contracts/finding-id-v1.json`）

- 输入字段顺序：`[repository.url, configuration_id, type, target, dependency]`
- 序列化：紧凑 UTF-8 JSON 数组（`ensure_ascii=false`，无空格，无尾换行）
- 哈希：完整 SHA-256 小写十六进制，前缀 `finding-`
- **不含** commit、行号、时间戳，保证同一发现跨提交身份稳定
- 测试向量见 `finding-id-v1.json` 的 `test_vector`

`evidence`：

| 字段 | 说明 |
|---|---|
| `actual_dependency` | 实际构建是否读取该依赖 |
| `declared_dependency` | 声明是否包含该依赖 |
| `description` | 文字说明 |
| `uri` | 证据文件 URI |

MISSING 对应 `actual=true, declared=false`；REDUNDANT 对应
`actual=false, declared=true`。

`ERROR_REPORT`：`schema_version`、`repository`、`configuration_id`、
`producer_job_id`、`findings[]`。给 MDFixer 的 REPAIR 请求只消费
非空的 MD-only 报告（`type=MISSING`），RD 从不提交给修复器。

## 9. 图格式（见 `contracts/graph.schema.json`）

`actual.json` 与 `declared.json` 使用相同结构：

| 字段 | 说明 |
|---|---|
| `schema_version` | 固定 `"1.0"` |
| `commit` | 40 位小写十六进制 SHA |
| `configuration_id` | 配置标识，如 `cc-default` |
| `edges` | `[target, dependency]` 二维数组，去重 |

- 边方向统一为"目标依赖于文件"；路径用仓库相对路径和 `/`。
- 只覆盖项目内对象编译依赖（含传递头文件包含）。
- 完整结构见 `contracts/graph.schema.json`。

## 10. 错误码

| code | 含义 | 使用位置 |
|---|---|---|
| INPUT_1001 | 结构/值不合法、幂等键冲突 | HTTP 400/409；不创建 Job |
| INPUT_1002 | 仓库或完整提交不匹配 | HTTP 422；或受理后 FAILED |
| INPUT_1003 | 构建配置/工作目录不匹配 | HTTP 422；或受理后 FAILED |
| INPUT_1004 | 非 MD-only、空报告或位置不在 Makefile 范围 | HTTP 422；或受理后 FAILED |
| ARTIFACT_2001 | 产物不存在、不可读、哈希错误 | 受理后 FAILED |
| ENV_3002 | 镜像构建失败 | job.error |
| EXEC_4002 | 超时 | TIMED_OUT 的 job.error |
| ANALYSIS_5001 | 分析器失败 | job.error |
| REPAIR_6001 | 修复验收结果自相矛盾 | 校验拒绝 |

## 11. 产物读取

`artifact://<dir>/<name>` 映射到仓库内 `artifacts/<dir>/<name>`，文件在
`artifacts/index.json` 注册。解析器验证目录边界、存在性和 SHA-256，拒绝
联网 URI 和未注册产物。产物元数据必填 `sha256`（64 位十六进制）以便离线校验。

## 12. 版本兼容

- 可兼容（需接收方允许）：新增可选字段、共享 Schema 同步更新、保留已有字段含义。
- 可能破坏：删除/改名/改语义、状态枚举改变、严格 Schema（
  `additionalProperties: false`）拒绝新增字段——即使新字段可选，旧校验器仍可能拒绝。
- 变更共享字段必须双方评审，并同步更新 Schema、OpenAPI、样例和
  `shared-lock.json`。详见 `ADR-004`。
