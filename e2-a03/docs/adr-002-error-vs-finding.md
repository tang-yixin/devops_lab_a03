# ADR-002：系统错误与检测发现分离

## Context
“发现缺失依赖”不是工具失败。如果把 MD 写成 FAILED，B 组会误判为执行失败。

## Decision
- 检测正常完成：status=SUCCEEDED，findings 写 MISSING / REDUNDANT。
- 工具没跑完：status=FAILED / TIMED_OUT / CANCELLED，error 写 ENV_3002 / EXEC_4002 / ANALYSIS_5001。

## Consequences
消费者必须同时检查 status 和 findings。  
B 组 MDFixer 只消费 findings 中的 MISSING。
