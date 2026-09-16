# ADR-001：耗时任务使用异步 Job

## Context
构建、检测、修复、Dockerfile 生成可能超过 HTTP 生命周期。课程约束要求 A/B 组能查询进度并取结果。

## Alternatives
1. 同步等待：实现简单，但客户端和执行耦合，超时后结果丢失。
2. 异步 Job：POST 202 + GET 查询，复杂但解耦。

## Decision
选择异步 Job。创建接口返回 202 和 job_id，查询接口返回状态与产物引用。

## Consequences
- 需要任务存储与查询。
- 需要定义 QUEUED / RUNNING / SUCCEEDED / FAILED / TIMED_OUT / CANCELLED。
- 用契约样例验证行为。
