# DevOps 实验 A 组仓库

本仓库是 DevOps 教学实验 **A 组**的成果仓库，按实验轮次分分支管理。

## 分支约定

| 分支 | 内容 | 状态 |
|---|---|---|
| `main` | 仓库说明与分支索引，不含实验成果 | 保留为空壳 |
| `e2` | 实验 E2：需求与接口契约 | 当前工作分支 |
| `e3` | 实验 E3（待开始） | 未创建 |

> 实验成果放在各自的分支上，`main` 只作为仓库入口。

## 目录结构

```text
devops_lab_a03/
├── .gitignore
├── README.md
└── e2-a03/                     # E2 实验成果
    ├── contracts/              # 接口契约与样例
    │   ├── task.schema.json                    # 统一任务模型 Schema
    │   ├── full-check-request.example.json     # BuildChecker 请求样例
    │   ├── full-check-job.example.json         # BuildChecker 响应样例
    │   ├── incremental-check-request.example.json  # EChecker 请求样例
    │   ├── incremental-check-job.example.json      # EChecker 响应样例
    │   ├── error-report.example.json           # 交给 B 组 MDFixer 的错误报告
    │   ├── artifact.example.json               # 产物引用样例
    │   └── invalid-missing-baseline.json       # 非法输入样例（缺 baseline）
    ├── docs/                   # 设计文档
    │   ├── api-contract.md                     # A/B 组接口总约定
    │   ├── adr-001-async-job.md                # ADR：耗时任务用异步 Job
    │   ├── adr-002-error-vs-finding.md         # ADR：系统错误与检测发现分离
    │   ├── adr-003-artifact-by-reference.md    # ADR：大产物按引用交接
    │   ├── backlog.md                          # 可验收任务清单
    │   ├── ai-usage.md                         # AI 使用过程证据
    │   └── personal-contribution.md            # 个人贡献与版本追溯
    └── tools/
        └── validate.py         # 契约最小校验脚本
```

## 实验 E2 简介

**主题**：需求与接口契约。本阶段不实现服务，只约定 A/B 两组微服务之间的数据交接。

**A 组职责**：

| 工具 | 职责 | 交付给谁 |
|---|---|---|
| BuildChecker | 全量依赖检测 | EChecker / MDFixer |
| EChecker | 跨提交增量检测 | MDFixer |

**B 组职责**：DRAFT（生成可构建环境）、MDFixer（修复缺失依赖）。

**核心设计决策**：

1. **异步 Job 模型** — 耗时任务先受理再后台执行，`POST` 返回 `202` + `job_id`，`GET /v1/jobs/{job_id}` 查询状态与产物引用。见 `adr-001`。
2. **系统错误与检测发现分离** — 检测到缺失依赖（MD）是**正常分析结果**，`status=SUCCEEDED`，写入 `findings`；工具本身没跑完才是 `FAILED`/`TIMED_OUT`，写入 `error`。见 `adr-002`。
3. **大产物按引用交接** — 依赖图、日志等大文件不内联进 Job 响应，只返回 `ArtifactRef`（`artifact://` URI + 元数据）。见 `adr-003`。

## 校验

```powershell
cd e2-a03

# 有效样例应全部通过
python tools/validate.py contracts/full-check-request.example.json `
                        contracts/incremental-check-request.example.json `
                        contracts/full-check-job.example.json `
                        contracts/incremental-check-job.example.json

# 非法样例应被拒绝（退出码 1）
python tools/validate.py contracts/invalid-missing-baseline.json
```

校验脚本覆盖四类请求（`DRAFT` / `FULL_CHECK` / `INCREMENTAL_CHECK` / `REPAIR`）
的必填字段，以及 Job 响应的状态枚举、`error` 与 `status` 一致性、`findings` 结构。

## 当前状态

**已完成**：

- 统一任务模型 Schema 与四类请求/响应样例
- 三份 ADR、Backlog、AI 使用记录
- 契约校验脚本，10 个负向用例全部被正确拒绝

**待完成**（需与 B 组对接或选定被检测项目后补充）：

- [ ] 选定被检测的 C 项目，替换样例中的 `<full-sha>` / `<C0-full-sha>` / `<C1-full-sha>`
- [ ] 与 B 组确认 `configuration_id`、构建镜像、`clean_build_command`
- [ ] 与 B 组确认产物读取方式（HTTP 端点或共享卷）
- [ ] 确认配对组编号，替换 `pair01` / `A01` / `B01`
- [ ] 填写 `personal-contribution.md` 的真实姓名、学号与提交 SHA
- [ ] 记录课堂三轮配对练习结论

详见 `e2-a03/docs/backlog.md` 与 `e2-a03/docs/ai-usage.md` 末尾的待办清单。
