# ADR-003：大产物通过 artifact:// 引用交接

## Context
依赖图、日志、报告很大，不适合塞进每个 Job 响应。

## Decision
Job 只返回 ArtifactRef：
- artifact_id
- type
- uri：artifact://pair01/full01/actual.json
- media_type
- producer_job_id
- sha256
- commit
- configuration_id

B 组通过 GET /v1/artifacts/{artifact_id} 或共享存储读取。

## Consequences
- 必须约定 URI 解析方式。
- E12 必须证明另一组能读取文件。
- 核验完整性时使用 sha256。
