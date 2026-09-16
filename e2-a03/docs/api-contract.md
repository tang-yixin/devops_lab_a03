# E2 A 组接口契约：BuildChecker / EChecker

## 1. 角色
- A 组：BuildChecker（全量检测）、EChecker（增量检测）
- B 组：DRAFT（环境生成）、MDFixer（修复）
- 下游：B 组重新构建、测试、重检

## 2. 统一任务模型
公共字段：
- schema_version
- job_id
- trace_id
- job_type：DRAFT / FULL_CHECK / INCREMENTAL_CHECK / REPAIR
- status：QUEUED / RUNNING / SUCCEEDED / FAILED / TIMED_OUT / CANCELLED
- execution
- input / output / error

## 3. 创建与查询
| 操作 | 端点 |
|---|---|
| 生成构建环境 | POST /v1/dockerfile-jobs |
| 全量检测 | POST /v1/full-check-jobs |
| 增量检测 | POST /v1/incremental-check-jobs |
| 修复缺失依赖 | POST /v1/repair-jobs |
| 查询任务 | GET /v1/jobs/{job_id} |

创建请求只带 `job_type`、`idempotency_key`、`input`、`execution`。  
服务端返回 `job_id` 与 `status=QUEUED`。

## 4. A 组 BuildChecker
### 输入
- repository.url
- repository.commit（完整 SHA）
- environment.image
- environment.configuration_id
- build.clean_build_command
- build.project_root

### 输出
- actual_graph：ArtifactRef，type=ACTUAL_GRAPH
- declared_graph：ArtifactRef，type=DECLARED_GRAPH
- findings：MISSING / REDUNDANT
- summary

### 成功语义
检测到 MD/RD 仍算 `SUCCEEDED`。  
工具没跑完才算 `FAILED / TIMED_OUT / CANCELLED`，写入 `error`。

## 5. A 组 EChecker
### 输入
- repository.url
- repository.commit（当前 C1）
- base_commit（C0）
- baseline.actual_graph_uri
- baseline.commit（必须等于 base_commit）
- baseline.configuration_id（必须与当前 environment.configuration_id 匹配）
- environment.image
- environment.configuration_id
- build.clean_build_command
- build.project_root

### 输出
- baseline_commit
- current_commit
- updated_actual_graph：ArtifactRef，type=UPDATED_ACTUAL_GRAPH
- findings
- added_findings
- removed_findings
- summary

## 6. 错误码
| 错误码 | 含义 | 写入位置 |
|---|---|---|
| ENV_3002 | 镜像构建失败 | job.error |
| EXEC_4002 | 任务超时 | job.error |
| ANALYSIS_5001 | 分析器失败 | job.error |
| REQUEST_4001 | 创建请求校验失败 | HTTP 400 / error |

## 7. 与 B 组交接
### B 给 A
- 仓库版本
- 镜像或构建方案
- configuration_id
- clean_build_command
- project_root
- EChecker 所需历史图

### A 给 B
- actual_graph
- declared_graph
- MD/RD 报告
- updated_actual_graph
- 位置与证据

## 8. 版本兼容
- 可兼容：新增可选字段，共享 Schema 同步更新，保留已有字段含义。
- 可能破坏：删除/改名/改语义、状态枚举改变、严格 Schema 拒绝新增字段。
