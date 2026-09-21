# A 组要求对照

依据：教师课件《E2_需求与接口契约_20260910.pptx》（27 页）。

| PPT 页 | 要求 | 对应文件/状态 |
|---|---|---|
| 2、3 | A 做 BuildChecker/EChecker，同号配对 | TEAM（待真实身份） |
| 5、19 | 公共任务单，环境/基线/修复/验证交接 | `contracts/task.schema.json`、`API-CONTRACT.md` |
| 7、27 | 四创建接口和查询，E2 不要求部署 | `contracts/openapi.json`，未部署 |
| 8、9 | MD/RD 不等于系统失败 | `ADR-002`，C0/C1 返回 SUCCEEDED 且带发现 |
| 10、21 | 全量实际/声明图，MD/RD、位置和证据 | `contracts/examples/minicalc/full-*`、`artifacts/minicalc/c0/` |
| 12、22 | 历史图、base commit、配置匹配和变化 | `incremental-*`、C0→C1 added/resolved |
| 12、23 | B 修复只消费 MD | `md-only-report-c0.json`、`repair-request.json` |
| 13–15 | ADR、AI 使用、个人贡献与版本 | `ADR-001~005`、`AI_USAGE.md`、`CONTRIBUTIONS.md` |
| 16、17 | 配对练习、接口一致、当堂检查 | `PAIR_REVIEW.md` |
| 17 | A 准备 MD/RD 项目与 C0/C1/C2 | Minicalc 三提交 + `artifacts/minicalc/` |
| 24 | 产物读取及追溯，E12 跨组读取证据 | `artifacts/index.json` 哈希注册；跨机器待验证 |
| 25、26 | 正反校验和版本变化 | `validate.py`、`shared-lock.json`、`ADR-004` |

本组自主方案：`gcc -MM` 教学检测、Minicalc 三次提交、finding_id 哈希（与 B 组约定一致）。
真实检测器（进程/系统调用追踪）尚未实现，属于 E3。
