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
    ├── validate.py             # 契约校验脚本（与 B 组逐字节一致）
    ├── contracts/              # 接口契约与样例
    │   ├── task.schema.json                # 统一任务模型 Schema（与 B 组一致）
    │   ├── openapi.json                    # 四个创建接口 + 查询接口（与 B 组一致）
    │   ├── shared-lock.json                # 共享文件 SHA-256 锁（与 B 组一致）
    │   ├── graph.schema.json               # Minicalc 编译图格式（与 B 组一致）
    │   ├── finding-id-v1.json              # finding_id 算法与测试向量（与 B 组一致）
    │   └── examples/
    │       ├── manifest.json               # 27 个共享样例清单（与 B 组一致）
    │       ├── *.json                      # 共享正反样例（与 B 组一致）
    │       └── minicalc/                   # A 组独有：Minicalc 真实数据样例
    ├── artifacts/              # 产物与哈希索引
    │   ├── index.json                      # 全部产物注册（demo 来自 B 组，minicalc 为本组生成）
    │   ├── demo/                           # B 组共享演示产物
    │   └── minicalc/                       # A 组生成：c0/c1/c2 的图、报告、证据
    └── docs/                   # 设计文档（大写命名）
        ├── API-CONTRACT.md                 # A/B 组接口总约定
        ├── ADR-001-async-job.md            # ADR：耗时任务用异步 Job
        ├── ADR-002-error-vs-finding.md     # ADR：系统错误与检测发现分离
        ├── ADR-003-artifact-by-reference.md # ADR：大产物按引用交接
        ├── BACKLOG.md                      # 可验收任务清单
        ├── AI_USAGE.md                     # AI 使用过程证据
        └── CONTRIBUTIONS.md                # 个人贡献与版本追溯
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

1. **异步 Job 模型** — 耗时任务先受理再后台执行，`POST` 返回 `202` + `job_id`，`GET /v1/jobs/{job_id}` 查询状态与产物引用。见 `ADR-001`。
2. **系统错误与检测发现分离** — 检测到缺失依赖（MD）是**正常分析结果**，`status=SUCCEEDED`，写入 `findings`；工具本身没跑完才是 `FAILED`/`TIMED_OUT`，写入 `error`。见 `ADR-002`。
3. **大产物按引用交接** — 依赖图、日志等大文件不内联进 Job 响应，只返回 `artifact://` URI，产物按目录映射并用 `index.json` 注册 SHA-256。见 `ADR-003`。

## 校验

```powershell
cd e2-a03
$env:PYTHONUTF8 = 1    # Windows 下避免 GBK 解码问题

# 共享样例 + 产物哈希（27 examples，19 valid + 8 expected rejections）
python validate.py

# A 组 Minicalc 真实数据样例（完整校验，含 artifact 解析）
python validate.py contracts/examples/minicalc/full-request.json
python validate.py contracts/examples/minicalc/full-response.json
python validate.py contracts/examples/minicalc/error-report-c0.json
python validate.py contracts/examples/minicalc/md-only-report-c0.json
python validate.py contracts/examples/minicalc/incremental-request.json
python validate.py contracts/examples/minicalc/incremental-response.json
python validate.py contracts/examples/minicalc/repair-request.json
```

校验脚本与 B 组一致：结构校验（Draft 2020-12 子集）+ 跨文件语义
（提交/配置匹配、MD-only、状态与 error 一致性）+ 产物哈希。

## 当前状态

**已完成**：

- 契约与 B 组逐字节对齐（schema、openapi、validate.py、27 个共享样例、shared-lock）
- 用真实目标项目 Minicalc 的 C0/C1/C2 完整 SHA 生成 A 组独有样例
- 三份 ADR、Backlog、API-CONTRACT、AI_USAGE 记录
- 校验脚本通过 27 个共享样例与 A 组 Minicalc 样例

**待完成**（需与 B 组对接或留到 E3）：

- [ ] 与 B 组确认 `configuration_id`（当前 `cc-default`）与构建镜像（当前为占位值）
- [ ] 确认配对组编号与成员信息，填写 `CONTRIBUTIONS.md`
- [ ] 记录课堂三轮配对练习结论
- [ ] 生成 Minicalc 真实产物（`artifacts/minicalc/`），实现真实检测器（E3）

详见 `e2-a03/docs/BACKLOG.md` 与 `e2-a03/docs/AI_USAGE.md` 末尾的待办清单。
