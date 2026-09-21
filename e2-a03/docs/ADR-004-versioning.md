# ADR-004：严格 Schema 与版本变更

## Context
PPT 第 26 页提醒严格 Schema 可能拒绝新增字段。本组 `task.schema.json` 与 B 组一致，
所有对象 `additionalProperties: false`。

## Decision
- 初版 `schema_version` 固定 `1.0`，所有对象严格拒绝未知字段。
- 新增字段（含可选字段）都需双方更新 Schema、样例、`shared-lock.json` 并同步版本。
- 字段改名、删字段、改语义、状态枚举变更使用新的主版本。

## Alternatives
宽松接收未知字段：利于演进，但易漏掉拼写错误，破坏"双方理解一致"的验收目标。

## Consequences
- 契约变更需双方评审 + 更新 ADR/CHANGELOG + 校验记录。
- 不能声称"新增字段总是兼容"。
- 共享文件哈希锁（`shared-lock.json`）保证任何一方改动都会被立即发现。
