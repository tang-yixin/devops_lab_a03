# ADR-003：大产物通过 artifact:// 引用交接

## Context
依赖图、日志、报告很大，不适合塞进每个 Job 响应。PPT 第 24 页要求
"Job 保存元数据，大文件通过引用交接"。

## Alternatives
1. 把依赖图 JSON 直接内联进 `Job.output`：实现简单，但每个响应膨胀，
   无法单独下载或校验完整性。
2. `artifact://` URI + 本地目录映射 + 索引哈希：Job 只返回 URI 字符串，
   产物文件按目录存放并用 `index.json` 注册 SHA-256。

## Decision
采用方案 2。Job 的 `output` 只返回 URI（如 `actual_graph_uri`），
具体内容按引用交接。产物元数据（`artifact`）必填：
- `artifact_id`、`type`、`uri`、`media_type`、`producer_job_id`
- `repository`、`configuration_id`、`sha256`

解析规则：`artifact://<dir>/<name>` 映射到仓库内 `artifacts/<dir>/<name>`，
文件在 `artifacts/index.json` 注册。解析器验证目录边界、存在性和 SHA-256，
拒绝联网 URI 和未注册产物。

## Consequences
- E2 双方收到同一份仓库即可离线读取产物，无需部署 HTTP 下载接口。
- 必须维护 `artifacts/index.json` 与每个产物的 SHA-256。
- 真实跨机器读取需双方共享 HTTPS 下载地址或对象存储，并补充鉴权与保留期。
- E12 必须证明另一组能读取文件（当前未完成）。
- `sha256` 设为必填（而非 PPT 中的按需选项），以便离线校验。
