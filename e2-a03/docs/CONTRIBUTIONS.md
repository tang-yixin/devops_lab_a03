# 个人贡献

> 姓名、学号、Git SHA 待真实成员填写。填写后替换下表中的占位符。

| 姓名 | 学号 | Git SHA | 负责内容 | 验证结果 |
|---|---|---|---|---|
| 成员1 | ... | ... | `contracts/task.schema.json`、`shared-lock.json`、`validate.py` | `python validate.py` 返回 27 examples（19 valid + 8 rejections） |
| 成员2 | ... | ... | `contracts/examples/minicalc/full-*`、`error-report-c0.json` | FULL_CHECK 与报告样例通过校验 |
| 成员3 | ... | ... | `contracts/examples/minicalc/incremental-*`、`md-only-report-c0.json`、`repair-request.json` | 增量与修复样例通过结构校验 |
| 成员4 | ... | ... | `docs/ADR-*`、`BACKLOG.md`、`API-CONTRACT.md`、`AI_USAGE.md` | 契约对齐 B 组、Minicalc 数据真实、AI 过程可追溯 |

## 验证命令

```bash
# 共享样例 + 产物哈希（Windows 需先设置 UTF-8）
$env:PYTHONUTF8=1
python validate.py

# A 组 Minicalc 样例
python validate.py contracts/examples/minicalc/full-request.json
python validate.py contracts/examples/minicalc/full-response.json
python validate.py contracts/examples/minicalc/error-report-c0.json
python validate.py contracts/examples/minicalc/md-only-report-c0.json
python validate.py contracts/examples/minicalc/incremental-request.json --structure-only
python validate.py contracts/examples/minicalc/incremental-response.json --structure-only
python validate.py contracts/examples/minicalc/repair-request.json --structure-only
```

## 未完成项

- 构建镜像仍为占位值 `e2-fixture:contract-example-only`，待 B 组提供可运行镜像。
- Minicalc 真实产物（`artifacts/minicalc/`）的图、证据、报告未生成，留到 E3。
- `configuration_id` 用 `cc-default`，待与 B 组最终确认。
- 课堂三轮配对练习记录待开展后回填。
