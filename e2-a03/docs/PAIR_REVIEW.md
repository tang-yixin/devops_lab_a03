# A/B 配对评审记录

> 以下为按 PPT 第 16 页三轮练习，结合双方已完成的客观事实填写。标注「B 组确认」的项依据 B 组消息/仓库，最终以双方共同确认为准。

| 项目 | 实际记录 |
|---|---|
| 日期、A/B 组号、参会成员 | A03 / B03，鼓楼校区；A：唐一心、李翔宇、王子贤、刘馨蔓；B：王宇晗、朱玄、靳滨硕 |
| 评审的完整 commit SHA | C0 `e3a1eda…`、C1 `f863c2d…`、C2 `e103bcb…`（Minicalc） |
| 第一轮：A 的环境/基线需求，B 的交付是否足够 | A 需要 Minicalc C0/C1/C2 的环境（镜像、`configuration_id`、构建命令）；B 提供 C2 镜像 digest，A 已拉取并 `docker run` 4 断言 PASS |
| 第二轮：B 的 MD 报告需求，A 如何生成并交付 | B 需要非空 MD-only 报告；A 提供 `md-only-report-c0.json`（3 MISSING），`repair-request.json` 消费之 |
| 第三轮：选择哪条失败输入，预期状态/错误码 | 缺 `baseline` 的增量请求（`invalid-incremental-no-baseline.json`），预期 `INPUT_1001` + HTTP 400 |
| A 组执行 validate.py 的结果 | `27 examples (19 valid, 8 expected rejections)` + Minicalc 7 样例全部 PASS |
| B 组执行 validate.py 的结果 | B 组确认 33 个共享文件哈希一致（`SHARED_SYNC`） |
| 产物读取方式和实际读取证据 | `artifact://` 目录映射 + `index.json` SHA-256；本地校验通过；C2 镜像 `docker run` 4 断言 PASS |
| 采纳/修改的 ADR | ADR-004（版本变更）、ADR-005（Minicalc/图格式/finding_id） |
| 未决问题、负责人、截止日期 | C0/C1 环境、真实 Checker 联调 → 留待 E3 |
| A 组确认人与 B 组确认人 | 唐一心（241250061）／ 王宇晗（241250086） |
