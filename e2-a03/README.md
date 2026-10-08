# A03 E2 需求与接口契约

> 依据课程课件《E2_需求与接口契约_20260910.pptx》。本阶段不实现服务，只约定 A/B
> 两组微服务之间的数据交接。设计细节见 `docs/`。

## A 组职责

| 工具 | 职责 | 交付给谁 |
|---|---|---|
| BuildChecker | 全量依赖检测 | EChecker / MDFixer |
| EChecker | 跨提交增量检测 | MDFixer |

B 组职责：DRAFT（生成可构建环境）、MDFixer（修复缺失依赖）。

## 核心设计决策

1. **异步 Job 模型** — 耗时任务先受理再后台执行，`POST` 返回 `202` + `job_id`，
   `GET /v1/jobs/{job_id}` 查询状态与产物引用。见 `docs/ADR-001`。
2. **系统错误与检测发现分离** — 检测到缺失依赖（MD）是正常分析结果，
   `status=SUCCEEDED`，写入 `findings`；工具未跑完才是 `FAILED`/`TIMED_OUT`，
   写入 `error`。见 `docs/ADR-002`。
3. **大产物按引用交接** — 依赖图、日志等大文件不内联进 Job 响应，只返回
   `artifact://` URI，按目录映射并用 `index.json` 注册 SHA-256。见 `docs/ADR-003`。

## 目录结构

```text
e2-a03/
├── validate.py             # 契约校验脚本（与 B 组逐字节一致）
├── contracts/              # 接口契约与样例
│   ├── task.schema.json    # 统一任务模型 Schema
│   ├── openapi.json        # 四个创建接口 + 查询接口
│   ├── shared-lock.json    # 共享文件 SHA-256 锁
│   ├── graph.schema.json   # Minicalc 编译图格式
│   ├── finding-id-v1.json  # finding_id 算法与测试向量
│   └── examples/           # 27 个共享样例 + minicalc/ 真实数据样例
├── artifacts/              # 产物与哈希索引
│   ├── index.json          # 全部产物注册
│   ├── demo/               # B 组共享演示产物
│   └── minicalc/           # A 组生成：c0/c1/c2 的图、报告、证据
└── docs/                   # 设计文档（大写命名）
```

## 校验

```powershell
cd e2-a03
$env:PYTHONUTF8 = 1    # Windows 下避免 GBK 解码问题

python validate.py    # 共享样例 + 产物哈希（27 examples，19 valid + 8 expected rejections）
python validate.py contracts/examples/minicalc/full-request.json       # 以下为 Minicalc 完整校验
python validate.py contracts/examples/minicalc/full-response.json
python validate.py contracts/examples/minicalc/error-report-c0.json
python validate.py contracts/examples/minicalc/md-only-report-c0.json
python validate.py contracts/examples/minicalc/incremental-request.json
python validate.py contracts/examples/minicalc/incremental-response.json
python validate.py contracts/examples/minicalc/repair-request.json
```

校验脚本与 B 组一致：结构校验 + 跨文件语义 + 产物哈希。

## 状态

- 已完成：契约与 B 组逐字节对齐；Minicalc C0/C1/C2 真实 SHA 样例；ADR/Backlog/AI_USAGE；校验通过。
- 待完成（留到 E3）：真实检测器（BuildChecker/EChecker）、镜像内联调。

详见 `docs/BACKLOG.md`、`docs/SUBMISSION.md`、`docs/VERIFICATION.md`。
