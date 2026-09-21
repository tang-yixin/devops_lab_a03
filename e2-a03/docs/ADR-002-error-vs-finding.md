# ADR-002：系统错误与检测发现分离

## Context
"发现缺失依赖"不是工具失败。如果把 MD 写成 FAILED，B 组会误判为执行失败，
从而错误地触发重试或告警。

## Alternatives
1. 发现 MD/RD 时 status 写 FAILED：直观，但混淆了"分析有产出"与"工具没跑完"。
2. 分离表示：检测正常完成（含发现）为 SUCCEEDED；工具没跑完才是终态失败。

## Decision
采用方案 2，并明确各状态的 `output`/`error` 语义：

| status | output | error | 含义 |
|---|---|---|---|
| QUEUED / RUNNING / CANCELLED | null | null | 未完成或无结果 |
| SUCCEEDED | 必填 | null | 分析完成，可能报告 MD/RD |
| FAILED / TIMED_OUT | null | 必填 | 工具没跑完 |

- 检测正常完成：`status=SUCCEEDED`，发现写进 `ERROR_REPORT.findings`。
- 工具没跑完：`FAILED`/`TIMED_OUT`/`CANCELLED`，`error.code` 写
  `ENV_3002` / `EXEC_4002` / `ANALYSIS_5001` 等。
- `TIMED_OUT` 的 `error.code` 必须是 `EXEC_4002`。

## Consequences
- 消费者必须同时检查 `status` 和 `findings`。
- B 组 MDFixer 只消费非空 MD-only 报告中的 MISSING finding，RD 从不提交。
- 校验器据此做语义检查：SUCCEEDED 却带 error、FAILED 却无 error、
  finding 的 type 与 evidence 不一致都会被拒绝。
