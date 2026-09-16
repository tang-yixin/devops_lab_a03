# E2 Backlog

| 任务 | 责任方 | 产物 | 验收条件 |
|---|---|---|---|
| 统一任务模型 | A/B 共同 | task.schema.json | 四类对象可表达 |
| BuildChecker 请求/响应样例 | A | full-check-request.example.json / full-check-job.example.json | 有效样例通过校验 |
| EChecker 请求/响应样例 | A | incremental-check-request.example.json / incremental-check-job.example.json | 缺 baseline 被拒绝 |
| 错误报告样例 | A | error-report.example.json | B 组能只消费 MISSING |
| 产物访问约定 | A/B 共同 | artifact.example.json + ADR-003 | B 组能读取 artifact:// |
| 错误码表 | A | api-contract.md | 系统错误与发现分离 |
| validate.py | A | tools/validate.py | 四类请求可检查，非法输入被拒绝 |
| AI_USAGE | A/B 各自 | ai-usage.md | AI 建议、人工判断、验证可追溯 |
| 个人贡献 | 每人 | personal-contribution.md | Git SHA、文件、验证结果可追溯 |
| 课堂三轮练习记录 | A01/B01 | ADR + Backlog | 第一轮环境、第二轮 MD、第三轮失败输入 |
