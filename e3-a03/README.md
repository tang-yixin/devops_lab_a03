# E3 并行测试基线

## 1. 实验目标

E3 的目标是准备能让工具接受的测试项目，写出预期结果和判断依据，保留实际运行或失败记录。

具体要交付：

- **MD / RD 依赖声明故障样例**：一个漏声明依赖（Missing Dependency），一个冗余声明依赖（Redundant Dependency），附人工判断依据。
- **C0 / C1 / C2 连续提交基线**：C0 声明正确，C1 新增 include 未补 Makefile，C2 只改编译命令。
- **Linux 原始跟踪证据**：`strace` 与 `make -pn`，为后续 BuildChecker 构图提供原始材料。
- **DRAFT 与 MDFixer 固定输入**：失败构建样本、参考修复补丁、无效候选补丁。
- **人工 ORACLE 与实际运行记录严格分离**。

---

## 2. 与 E2 的关系

E3 **基于 E2 派生**，不修改 E2。

### 2.1 E2 提供的

从 `../e2-a03/` 读取：

- **契约**：`contracts/task.schema.json`、`graph.schema.json`、`openapi.json`、`finding-id-v1.json`、`shared-lock.json`。
- **共享样例**：`contracts/examples/` 下 27 个 A/B 组逐字节对齐的样例。
- **Minicalc 分析报告**：`artifacts/minicalc/c0|c1|c2/` 下的
  - `actual.json`：实际读取的文件依赖。
  - `declared.json`：Makefile 声明的依赖。
  - `md-only-report.json`：MD/RD 发现报告（人工 ORACLE 对照）。
  - `error-report.json`：系统错误报告（DRAFT 失败样例依据）。
  - `evidence.json`：证据记录。
- **校验脚本**：`validate.py`，结构校验 + 跨文件语义 + 产物哈希。

### 2.2 E3 提供的

- **Minicalc 风格样例源码**：E3 自己准备，放在 `fixtures/minicalc-src/`。
- **MD/RD 基线**：`fixtures/md-rd/`。
- **C0/C1/C2 提交基线**：`fixtures/commits/`。
- **DRAFT 样本**：`fixtures/draft/`。
- **MDFixer 固定输入**：`fixtures/mdfixer/`。
- **Linux 原始跟踪证据**：`work/<timestamp>/md-rd/evidence/linux-verified/`。

### 2.3 衔接原则

- E2 是**契约与报告来源**。
- E3 是**测试基线**。
- E2 内容变化时，只改 `config/e2_mapping.json`，重新运行 `run_lab.py`。
- E3 输出必须通过 `e2-a03/validate.py` 校验。

---

## 3. 当前遇到的问题（与 E2 的协作）

### 3.1 E2 不提供 Minicalc 源码

检查 `e2-a03/artifacts/minicalc/c0/`，实际只有：

```text
artifacts/minicalc/c0/
├── actual.json
├── declared.json
├── error-report.json
├── evidence.json
└── md-only-report.json
```

**没有 `src/`、没有 `Makefile`、没有可构建的项目。**

这意味着 E3 无法直接从 E2 复制源码来跑 `make` 和 `strace`。

### 3.2 源码可能在 B 组手上

推断依据：

- E2 阶段 A 组产出的是**分析报告**，要对 Minicalc 运行检测器才能得到 `actual.json`、`declared.json`。
- 要做这些分析，需要**可构建的 Minicalc 源码**。
- A 组仓库里没有，最可能来自 B 组，或课程统一提供。

### 3.3 E3 的应对策略

E3 文档本身写明：

> 先独立准备样本，E12 再接入另一组的真实数据。

因此 E3 采取：

1. **E3 自己准备 Minicalc 风格样例源码**，放在 `fixtures/minicalc-src/`。
2. **E2 的 JSON 报告作为 ORACLE 对照**，不提供源码。
3. **E12 再接入 B 组真实 Minicalc 数据**。
4. `e2_mapping.json` 只保留契约与报告路径，不再尝试复制 E2 源码。

### 3.4 待与 B 组确认

- [ ] B 组是否持有 Minicalc 源码？路径在哪？
- [ ] B 组的 Minicalc 构建命令与运行命令是什么？
- [ ] B 组的 `configuration_id` 是否为 `cc-default`？
- [ ] B 组镜像的 C2 digest 是否与 A 组拉取的一致？
- [ ] 配对组编号与成员信息，用于填写 `CONTRIBUTIONS.md`。

在 B 组提供真实源码前，E3 使用自己准备的 Minicalc 风格样例，保证实验可以独立推进。

---

## 4. 目录结构

```text
e3-a03/
├── README.md
├── config/
│   └── e2_mapping.json          # E2 -> E3 映射，唯一需要填的配置
├── docs/
│   ├── A_GROUP.md
│   ├── B_GROUP.md
│   ├── EXPECTED_RESULTS.md
│   └── EVIDENCE_GUIDE.md
├── fixtures/
│   ├── minicalc-src/            # E3 自己准备的 Minicalc 风格源码
│   │   ├── main.c
│   │   ├── config.h
│   │   ├── feature.h
│   │   └── Makefile
│   ├── md-rd/                   # 由 prepare_from_e2.py 派生
│   ├── commits/                 # C0 / C1 / C2
│   ├── draft/                   # DRAFT 样本
│   └── mdfixer/                 # MDFixer 固定输入
├── scripts/
│   ├── utils.py                 # Evidence 采集工具
│   ├── run_lab.py               # 主入口
│   ├── prepare_from_e2.py       # 从 E2 派生 fixtures
│   ├── prepare_a_md_rd.py       # A 组 MD/RD 运行
│   ├── prepare_a_commits.py     # A 组 C0/C1/C2 运行
│   ├── prepare_b_draft.py       # B 组 DRAFT 观察
│   ├── prepare_b_mdfixer.py     # B 组 MDFixer 固定输入
│   ├── verify_with_e2.py        # 调用 E2 validate.py
│   └── linux_trace.sh           # Linux 原始跟踪
└── work/
    └── <timestamp>/             # 每次运行新建，保留旧证据
```

---

## 5. 快速运行

```bash
cd e3-a03
python3 scripts/run_lab.py
```

输出最后一行：

```text
EVIDENCE_DIR=/path/to/e3-a03/work/20261008-153000
```

然后检查：

```bash
cat work/20261008-153000/commands.json
cat work/20261008-153000/observations.json
cat docs/EXPECTED_RESULTS.md
```

Linux 环境可额外运行：

```bash
cd work/20261008-153000/md-rd
bash ../../../scripts/linux_trace.sh . feature.h config.h
```

---

## 6. 配置说明

所有 E2 路径集中在 `config/e2_mapping.json`。

关键字段：

| 字段 | 含义 |
|---|---|
| `e2_root` | E2 根目录，默认 `../e2-a03` |
| `e2_validate` | E2 校验脚本，默认 `validate.py` |
| `e2_schemas` | E2 契约文件路径 |
| `minicalc_c0/c1/c2` | E2 Minicalc 报告目录 |
| `e3_source.src_dir` | E3 自己准备的源码目录 |
| `group_a.build_cmd` | A 组构建命令 |
| `group_a.run_cmd` | A 组运行命令 |
| `group_a.oracle_report` | E2 提供的 MD 报告路径 |
| `group_b.error_report` | E2 提供的错误报告路径 |
| `commits` | C0/C1/C2 的 E2 报告目录与预期 |

E2 路径变化时，只改此文件。

---

## 7. A 组与 B 组分工

### 7.1 A 组已完成

- MD/RD 样例运行与证据采集。
- C0/C1/C2 连续提交运行与证据采集。
- Linux 原始跟踪证据。
- 人工 ORACLE 与实际运行记录分离。

### 7.2 A 组暂时代为 B 组完成

A 组为实验包完整性，暂时生成：

- DRAFT 样本源码、Makefile、README。
- `Dockerfile.broken`、`Dockerfile.reference`。
- MDFixer 固定报告、`Makefile.before`、`reference.patch`、`invalid.patch`。

这些内容原本属于 B 组，代码中已加注释标明。

### 7.3 B 组还需完成

- 实际 `docker build` / `docker run`，保存日志、镜像 ID、输出。
- `git apply --check` / `git apply`，保存日志。
- 修复前只改头文件仍输出旧值。
- 修复后再次改头文件自动重建。
- 无效候选非零退出 + 恢复。
- 四种声明风格（Target / Macro / Hybrid / Implicit）。
- 隐式规则与 `.d` 文件（`-MMD -MP`）。
- 所有证据保存到 `work/<timestamp>/draft/` 和 `work/<timestamp>/mdfixer/`。

详见 `docs/B_GROUP.md`。

---

## 8. 证据保存原则

1. **每次运行创建新目录**：`work/YYYYMMDD-HHMMSS/`，不覆盖旧证据。
2. **人工答案与实际日志分开**：
   - 人工 ORACLE 放 `fixtures/`，标注 `INSTRUCTOR_ORACLE`。
   - 实际运行放 `work/<timestamp>/`。
   - 人工报告不计入工具准确率。
3. **成功和失败都保存**：构建失败日志、非零退出码、无效候选、拒绝恢复都要保留。
4. **可定位到版本**：记录 Git commit、SHA、源码快照、工具版本、系统环境。
5. **结构化记录**：`commands.json` 存命令，`observations.json` 存观察。

详见 `docs/EVIDENCE_GUIDE.md`。

---

## 9. 后续任务衔接

| 后续任务 | 使用的 E3 证据 |
|---|---|
| E4 环境和密钥管理 | `environment.txt`、Dockerfile、镜像 ID |
| E5 BuildChecker / DRAFT | `md-rd/`、`draft/`、`commands.json` |
| E8 EChecker / MDFixer | `commits/`、`mdfixer/`、`EXPECTED.json` |
| E10 增量 / 全量比较 | C0/C1/C2 运行记录与命令快照 |
| E12 接入真实数据联调 | B 组真实 Minicalc 源码与运行证据 |

---

## 10. 待办清单

### 10.1 与 E2 的对接

- [ ] 确认 E2 的 `md-only-report.json` 字段结构，对齐 ORACLE 格式。
- [ ] 确认 E2 的 `finding-id-v1.json` 算法，E3 输出必须一致。
- [ ] 确认 `graph.schema.json` 的节点与边格式，供 BuildChecker 使用。
- [ ] 确认 `validate.py` 的调用方式，E3 fixtures 应能通过校验。

### 10.2 与 B 组的对接

- [ ] 确认 B 组是否持有 Minicalc 源码及路径。
- [ ] 确认 B 组的构建与运行命令。
- [ ] 确认 `configuration_id` 与镜像 digest。
- [ ] 填写 `CONTRIBUTIONS.md`。

### 10.3 E3 自身

- [ ] 准备 `fixtures/minicalc-src/` 源码。
- [ ] 运行 `run_lab.py`，检查 `work/<timestamp>/` 证据完整。
- [ ] 运行 `linux_trace.sh`，检查 `evidence/linux-verified/` 证据完整。
- [ ] 更新 `docs/EXPECTED_RESULTS.md` 为实际预期。
- [ ] 检查 `docs/A_GROUP.md` 与 `docs/B_GROUP.md` 中的路径与命令是否与实际一致。

---

## 11. 当前状态

**已完成**：

- E3 脚本框架（`utils.py`、`run_lab.py`、`prepare_*.py`）。
- 从 E2 派生 fixtures 的配置驱动机制（`e2_mapping.json`）。
- Linux 跟踪脚本适配 Minicalc。
- A 组 MD/RD 与 C0/C1/C2 脚本。
- B 组 DRAFT 与 MDFixer 固定输入生成脚本（A 组暂时代为生成）。
- 文档结构（A 组、B 组、预期结果、证据指南）。

**待完成**：

- Minicalc 风格源码准备。
- 与 E2 报告字段结构的精确对齐。
- 与 B 组的源码和配置确认。
- 实际运行 `run_lab.py` 并采集完整证据。
- E12 接入 B 组真实数据。