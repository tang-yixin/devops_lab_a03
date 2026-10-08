# 证据目录说明

## 1. 目的

本文件说明 E3 并行测试基线实验包中证据目录的组织方式、保存内容、命名规范和使用方法。

目标是保证：

- 每次运行都有独立目录，不覆盖旧证据。
- 人工 ORACLE 答案与真实运行日志严格分开。
- 后续 BuildChecker、EChecker、DRAFT、MDFixer 能直接读取输入和证据。
- 别人能按 README 重跑，并能定位到具体版本、命令和失败原因。
- 失败记录、成功记录、拒绝记录都要保留。

---

## 2. 基本原则

1. **每次运行创建新目录**
   - 目录名使用时间戳，例如 `work/20261008-153000/`。
   - 不允许覆盖已有 `work/` 子目录。

2. **人工答案和实际日志分开**
   - 人工答案放在 `fixtures/` 中，标注 `INSTRUCTOR_ORACLE`。
   - 实际运行结果放在 `work/<timestamp>/` 中。
   - 人工报告不能计入工具准确率。

3. **成功和失败都要保存**
   - 构建成功日志要保存。
   - 构建失败日志、非零退出码、错误输出也要保存。
   - 无效候选、拒绝恢复记录也要保存。

4. **命令和观察结果结构化**
   - 所有实际执行命令写入 `commands.json`。
   - 关键观察写入 `observations.json`。
   - 原始日志、stdout、stderr、strace 输出按目录保存。

5. **可定位到版本**
   - 记录 Git commit、tag、SHA。
   - 记录源码快照、Makefile、头文件内容。
   - 记录工具版本、系统版本、CPU 架构。

---

## 3. 顶层目录

```text
E3_lab/
├── README.md
├── docs/
│   ├── A_GROUP.md
│   ├── B_GROUP.md
│   ├── EXPECTED_RESULTS.md
│   └── EVIDENCE_GUIDE.md
├── fixtures/
│   ├── md-rd/
│   ├── commits/
│   │   ├── C0/
│   │   ├── C1/
│   │   └── C2/
│   ├── draft/
│   └── mdfixer/
├── scripts/
│   ├── run_lab.py
│   ├── utils.py
│   ├── prepare_a_md_rd.py
│   ├── prepare_a_commits.py
│   ├── prepare_b_draft.py
│   ├── prepare_b_mdfixer.py
│   └── linux_trace.sh
└── work/
    └── <timestamp>/
        ├── commands.json
        ├── observations.json
        ├── md-rd/
        ├── commits/
        ├── draft/
        ├── mdfixer/
        └── evidence/
            └── linux-verified/
```

---

## 4. `fixtures/`：课程人工样例与 ORACLE

`fixtures/` 保存课程人工准备的样例源码和人工判断依据。所有人工标签必须标明 `ORACLE` 来源。

```text
fixtures/
├── md-rd/
│   ├── main.c
│   ├── config.h
│   ├── unused.h
│   ├── Makefile
│   └── ORACLE_findings.json
├── commits/
│   ├── C0/
│   │   ├── main.c
│   │   ├── config.h
│   │   └── Makefile
│   ├── C1/
│   │   ├── main.c
│   │   ├── config.h
│   │   ├── feature.h
│   │   └── Makefile
│   └── C2/
│       ├── main.c
│       ├── config.h
│       ├── feature.h
│       └── Makefile
├── draft/
│   ├── main.c
│   ├── Makefile
│   ├── README.md
│   ├── Dockerfile.broken
│   └── Dockerfile.reference
└── mdfixer/
    ├── fixed_report.json
    ├── Makefile.before
    ├── reference.patch
    └── invalid.patch
```

### 4.1 `fixtures/md-rd/ORACLE_findings.json`

人工判断 MD/RD 的预期答案。示例：

```json
{
  "provenance": "INSTRUCTOR_ORACLE",
  "findings": [
    {
      "type": "MISSING",
      "target": "main.o",
      "dependency": "config.h",
      "reason": "main.c includes config.h，但 Makefile 未声明；只改 config.h 不会触发 main.o 重建。"
    },
    {
      "type": "REDUNDANT",
      "target": "main.o",
      "dependency": "unused.h",
      "reason": "unused.h 被声明但未被源码包含；修改它会触发多余编译。"
    }
  ]
}
```

### 4.2 `fixtures/commits/`

保存 C0、C1、C2 三个连续提交的源码和 Makefile。

- C0：声明正确，输出 `BASE + MODE`，clean build 预期 10。
- C1：新增 `feature.h`，未补 Makefile 依赖，clean build 预期 12，预期发现 `MD: main.o -> feature.h`。
- C2：只改 `-DMODE=7`，源码保持 C1，增量预期 12，clean 预期 19。

### 4.3 `fixtures/draft/`

DRAFT 样本：

- `main.c`、`Makefile`、`README.md`。
- `Dockerfile.broken`：故意缺少工具链，预期构建失败。
- `Dockerfile.reference`：安装 `gcc make libc6-dev`，预期构建成功并输出 `hello E3`。

### 4.4 `fixtures/mdfixer/`

MDFixer 固定输入：

- `fixed_report.json`：固定 MD 报告，`main.o` 缺 `config.h`。
- `Makefile.before`：缺少依赖声明的 Makefile。
- `reference.patch`：参考修复补丁。
- `invalid.patch`：无效候选补丁，故意加入失败命令。

---

## 5. `work/<timestamp>/`：实际运行证据

每次运行 `python3 scripts/run_lab.py` 都会创建新的时间戳目录。

```text
work/<timestamp>/
├── commands.json
├── observations.json
├── md-rd/
├── commits/
├── draft/
├── mdfixer/
└── evidence/
    └── linux-verified/
```

### 5.1 `commands.json`

记录所有实际执行的命令。每条记录包含：

- `cmd`：命令或命令列表。
- `cwd`：工作目录。
- `start`、`end`：开始和结束时间。
- `returncode`：退出码。
- `stdout`：标准输出。
- `stderr`：标准错误。
- `error`：异常信息，如果执行失败。

示例：

```json
[
  {
    "cmd": ["make"],
    "cwd": "/path/to/work/20261008-153000/md-rd",
    "returncode": 0,
    "stdout": "cc -c main.c -o main.o\ncc main.o -o app\n",
    "stderr": ""
  }
]
```

### 5.2 `observations.json`

记录脚本观察到的关键结论。每条包含：

- `key`：观察项名称。
- `value`：观察值。
- `note`：说明。

示例：

```json
[
  {
    "key": "A_MD_RD",
    "value": "完成 MD/RD 样例运行",
    "note": "预期：增量输出 1；clean 输出 2；修改 unused.h 触发多余编译。"
  }
]
```

### 5.3 `md-rd/`

保存 MD/RD 样例的实际运行副本和证据。

建议保存：

- `main.c`、`config.h`、`unused.h`、`Makefile` 修改前后内容。
- 第一次 `make` 输出和退出码。
- 第一次 `./app` 输出。
- 修改 `config.h` 后的 `make`、`./app` 输出。
- `make clean`、完整重建的 `make`、`./app` 输出。
- 修改 `unused.h` 后的 `make` 输出。
- `ORACLE_findings.json` 与实际检测结果对照。

预期证据：

| 场景 | 预期输出 | 说明 |
|---|---|---|
| 第一次完整构建 | 1 | 编译成功，但不能说明依赖声明正确 |
| 只改 `config.h` | 增量仍输出 1 | 证明 MD |
| clean build | 输出 2 | 与增量对照，证明漏重建 |
| 修改 `unused.h` | 出现多余编译 | 证明 RD |

### 5.4 `commits/`

保存 C0、C1、C2 的实际运行证据。

建议结构：

```text
commits/
├── C0/
│   ├── make.stdout
│   ├── make.stderr
│   ├── app.stdout
│   └── exit-code.txt
├── C1/
│   ├── make.stdout
│   ├── make.stderr
│   ├── app.stdout
│   └── exit-code.txt
├── C2_incremental/
│   ├── make.stdout
│   ├── make.stderr
│   ├── app.stdout
│   └── exit-code.txt
├── C2_clean/
│   ├── make.stdout
│   ├── make.stderr
│   ├── app.stdout
│   └── exit-code.txt
└── EXPECTED.json
```

`EXPECTED.json` 示例：

```json
{
  "C0": { "clean": 10 },
  "C1": { "clean": 12, "expected_finding": "MD: main.o -> feature.h" },
  "C2": { "incremental": 12, "clean": 19, "note": "只改编译命令，普通 make 可能不重建" }
}
```

还要保存命令快照：

```bash
make -n -B main.o
```

用于比较 C1 与 C2 的编译命令变化。

### 5.5 `draft/`

保存 DRAFT 样本的构建与验证证据。

建议保存：

- `docker-build-broken.log`：失败构建日志。
- `docker-build-broken.exit-code`：非零退出码。
- `docker-build-reference.log`：参考成功构建日志。
- `docker-build-reference.exit-code`：0。
- `image-id.txt`：参考镜像 ID。
- `hello-output.txt`：容器运行输出 `hello E3`。
- `dockerfile.diff`：失败与参考 Dockerfile 的差异。

预期结果：

| 场景 | 预期 |
|---|---|
| `Dockerfile.broken` | 构建非零退出，日志可定位到 `make: not found` |
| `Dockerfile.reference` | 构建成功，运行输出 `hello E3` |

### 5.6 `mdfixer/`

保存 MDFixer 固定输入的修复与验证证据。

建议保存：

- `patch-check.log`：`git apply --check reference.patch` 输出。
- `patch-apply.log`：`git apply reference.patch` 输出。
- `before-config.txt`、`after-config.txt`：修改 `config.h` 前后内容。
- `before-fix.log`：修复前只改头文件仍输出旧值。
- `after-fix.log`：修复后 clean 输出新值。
- `second-change.log`：再次修改头文件后自动重建，预期输出 3。
- `invalid-candidate.log`：无效候选导致 `make` 非零退出。
- `recovery.log`：恢复原 Makefile 后构建和测试再次通过。

验证要求：

- 修复前：只改头文件仍输出旧值。
- 修复后：clean 输出新值。
- 再次修改头文件：不 clean 也能自动重建。
- 不能只靠 clean 成功证明 MD 修好了。

### 5.7 `evidence/linux-verified/`

保存 Linux 原始跟踪证据。

建议结构：

```text
evidence/linux-verified/
├── trace.log
├── trace.log.*
├── make.stdout
├── make.stderr
├── config-h-access.log
├── make-pn.txt
└── environment.txt
```

生成方式：

```bash
make clean
strace -ff -o trace.log -e trace=%file,%process make
grep -R "config.h" trace.log*
make -pn
```

记录内容：

- 进程、路径和文件访问。
- 区分编译器与构建器的读取。
- `openat` 只能说明文件被访问，不能直接判定 MD。
- 后续 BuildChecker 需要构图与归一化。
- `make -pn` 用于查看 Make 解析的声明。

### 5.8 `environment.txt`

记录实验环境：

```text
OS: ...
CPU: ...
git version: ...
make version: ...
cc version: ...
python3 version: ...
strace version: ...
```

Mac 的 `cc` 与容器内 `gcc` 可能不同。正式性能比较要保持同一环境。

---

## 6. 证据类型清单

| 证据类型 | 保存位置 | 用途 |
|---|---|---|
| 人工 ORACLE | `fixtures/.../ORACLE_findings.json` | 作为预期答案对照 |
| 实际命令 | `work/<timestamp>/commands.json` | 记录执行过什么 |
| 关键观察 | `work/<timestamp>/observations.json` | 记录观察到什么 |
| 构建日志 | `work/<timestamp>/*/make.stdout`、`make.stderr` | 判断编译是否通过 |
| 运行输出 | `work/<timestamp>/*/app.stdout` | 判断功能是否正确 |
| 失败日志 | `work/<timestamp>/draft/docker-build-broken.log` | 定位构建失败 |
| 镜像 ID | `work/<timestamp>/draft/image-id.txt` | 定位参考成功环境 |
| 补丁检查 | `work/<timestamp>/mdfixer/patch-check.log` | 验证补丁能否应用 |
| 无效候选 | `work/<timestamp>/mdfixer/invalid-candidate.log` | 验证拒绝和恢复 |
| strace | `work/<timestamp>/evidence/linux-verified/trace.log*` | 原始文件访问证据 |
| make -pn | `work/<timestamp>/evidence/linux-verified/make-pn.txt` | Make 解析声明 |
| 环境版本 | `work/<timestamp>/evidence/linux-verified/environment.txt` | 保证可复现 |

---

## 7. ORACLE 与实际记录分离

必须严格区分：

- `fixtures/`：课程人工样例，标注 `INSTRUCTOR_ORACLE`。
- `work/`：真实运行记录，来自实际命令和观察。
- `evidence/`：原始日志、strace、Docker 日志等。

禁止：

- 把人工报告当作工具输出。
- 把人工答案计入工具准确率。
- 用人工答案覆盖实际失败日志。
- 只保留成功记录，删除失败记录。

后续 E10 比较真实增量 / 全量报告一致性时，应使用：

- 人工 ORACLE 作为对照。
- 实际运行报告作为待评估对象。
- 差异单独记录，不混入准确率计算。

---

## 8. 命名与保存规范

1. 时间戳目录格式：`YYYYMMDD-HHMMSS`，例如 `20261008-153000`。
2. 日志文件使用明确名称：
   - `make.stdout`、`make.stderr`
   - `app.stdout`
   - `exit-code.txt`
   - `docker-build-broken.log`
   - `docker-build-reference.log`
   - `patch-check.log`
   - `patch-apply.log`
   - `invalid-candidate.log`
   - `recovery.log`
3. JSON 文件使用 UTF-8，缩进 2 空格。
4. 人工标签必须写 `provenance: INSTRUCTOR_ORACLE`。
5. 真实运行记录不写 `ORACLE`，只写实际命令、输出和退出码。
6. 每次运行保留旧目录，不删除、不覆盖。

---

## 9. 复现检查清单

完成 E3 后，检查：

- [ ] 别人能按 README 运行吗？
- [ ] 人工答案和实际日志分清了吗？
- [ ] 预期结果能说明依据吗？
- [ ] 失败记录能定位到具体版本吗？
- [ ] MD 和 RD 是否分别有可复现证据？
- [ ] C0 / C1 / C2 的差异是否清楚？
- [ ] 是否保留了旧证据，没有覆盖历史运行？
- [ ] 是否标注了 `ORACLE` 来源？
- [ ] 是否记录了 Git commit / SHA？
- [ ] 是否记录了工具版本和系统环境？
- [ ] Docker 失败和成功日志是否都保留？
- [ ] MDFixer 无效候选和恢复记录是否保留？
- [ ] Linux `strace` 和 `make -pn` 证据是否保存？

---

## 10. 禁止事项

- 不要覆盖已有 `work/<timestamp>/`。
- 不要把人工 ORACLE 报告计入工具准确率。
- 不要只保留成功日志。
- 不要删除失败构建日志。
- 不要在没有记录版本的情况下修改样例。
- 不要在公共样例目录直接运行 `make clean`。
- 不要把 Mac 环境结果和 Linux 容器结果混在同一性能比较中。

---

## 11. 与后续任务关系

| 后续任务 | 使用的 E3 证据 |
|---|---|
| E4 环境和密钥管理 | `environment.txt`、Dockerfile、镜像 ID |
| E5 BuildChecker / DRAFT | `md-rd/`、`draft/`、`commands.json` |
| E8 EChecker / MDFixer | `commits/`、`mdfixer/`、`EXPECTED.json` |
| E12 接入真实数据联调 | `fixtures/` 与 `work/` 中的真实提交和证据 |

---

## 12. 示例目录树

```text
work/20261008-153000/
├── commands.json
├── observations.json
├── md-rd/
│   ├── src/
│   ├── Makefile
│   ├── ORACLE_findings.json
│   ├── graph.schema.json
│   ├── finding-id-v1.json
│   ├── make.stdout
│   ├── make.stderr
│   ├── minicalc.stdout
│   ├── exit-code.txt
│   └── evidence/
│       └── linux-verified/
│           ├── trace.log
│           ├── trace.log.*
│           ├── make.stdout
│           ├── make.stderr
│           ├── access-config_h.log
│           ├── access-feature_h.log
│           ├── make-pn.txt
│           └── environment.txt
├── commits/
│   ├── C0/
│   ├── C1/
│   ├── C2_incremental/
│   ├── C2_clean/
│   └── EXPECTED.json
├── draft/
│   ├── docker-build-broken.log
│   ├── docker-build-broken.exit-code
│   ├── docker-build-reference.log
│   ├── docker-build-reference.exit-code
│   ├── image-id.txt
│   └── minicalc-output.txt
└── mdfixer/
    ├── patch-check.log
    ├── patch-apply.log
    ├── before-fix.log
    ├── after-fix.log
    ├── second-change.log
    ├── invalid-candidate.log
    └── recovery.log
```