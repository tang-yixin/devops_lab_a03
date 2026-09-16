# E2 Backlog

> 状态说明：`完成` = 已实现并本地验证；`待确认` = 需与 B 组或真实成员对接；
> `E3 边界` = 本次 E2 只定义契约，实现留到 E3。

## E2 任务

| ID | 责任方 | 产物 | 验收条件 | 状态 |
|---|---|---|---|---|
| E2-A01 | A/B 共同 | `contracts/task.schema.json` + `shared-lock.json` | 四类任务可表达，共享文件与 B 组逐字节一致 | 完成 |
| E2-A02 | A | `contracts/examples/minicalc/full-request.json` / `full-response.json` | 真实仓库与 C0 完整 SHA，输出四个 URI | 完成 |
| E2-A03 | A | `contracts/examples/minicalc/incremental-request.json` / `incremental-response.json` | baseline 必填，版本/配置匹配，输出新增/消除 finding ID | 完成 |
| E2-A04 | A | `contracts/examples/minicalc/md-only-report-c0.json` / `repair-request.json` | REPAIR 只消费非空 MD-only 报告 | 完成 |
| E2-A05 | A | `contracts/examples/minicalc/error-report-c0.json` | C0 的 3 MD + 1 RD，location/evidence 结构完整 | 完成 |
| E2-A06 | A/B 共同 | `docs/ADR-003` + `artifacts/index.json` | artifact:// 目录映射 + SHA-256 校验 | 完成 |
| E2-A07 | A | `validate.py` | 27 个共享正反样例通过；非法输入被拒绝 | 完成 |
| E2-A08 | A/B 共同 | `contracts/graph.schema.json` + `contracts/finding-id-v1.json` | 图格式与 finding_id 算法双方一致 | 完成 |
| E2-A09 | A | `artifacts/minicalc/{c0,c1,c2}/` | C0/C1/C2 图、报告、证据可被解析，SHA-256 注册 | 完成 |
| E2-A10 | 全体 | `docs/TEAM`、`CONTRIBUTIONS.md`、`AI_USAGE.md` | 真实身份、AI 采纳判断、提交 SHA 可追溯 | 待确认 |
| E2-A11 | A/B 共同 | 课堂三轮练习记录 | 第一轮环境、第二轮 MD、第三轮失败输入 | 待确认 |

## E3 边界任务（本次不实现）

| ID | 责任方 | 产物 | 验收条件 | 状态 |
|---|---|---|---|---|
| E3-A01 | A-QA | Minicalc 真实产物（`artifacts/minicalc/`） | C0/C1/C2 的图、证据、报告可被解析 | 完成（gcc -MM 辅助，非真实检测器） |
| E3-A02 | A-FULL | 真实全量检测器 | 采集实际/声明图并评估 MD/RD | 未实现 |
| E3-A03 | A-INCREMENTAL | 真实增量检测器 | 复用基线、分析变更影响 | 未实现 |
| E3-A04 | A/B-CONTRACT | 图格式与 finding ID 稳定性 | 真实图和跨提交身份稳定 | 已定（graph.schema.json + finding-id-v1.json） |
| E3-A05 | A/B-CONTRACT | 修复后重检协议 | 明确 base+patch hash 或新提交 | 待定 |
| E12-A01 | A/B-QA | 真实四服务联调与跨机器下载 | 产物可跨机器读取并通过重检 | 未开展 |

## 关键验收口径

- **有效样例**：`python validate.py contracts/examples/minicalc/<file>` 返回 PASS。
- **共享一致性**：`python validate.py`（无参数）返回
  `27 examples (19 valid, 8 expected rejections)`。
- **非法输入**：`invalid-*.json` 被正确拒绝，错误码与 `manifest.json` 一致。
- **产物读取**：`artifact://` 解析只访问 `artifacts/` 目录内已注册文件，
  校验 SHA-256，拒绝联网 URI。
