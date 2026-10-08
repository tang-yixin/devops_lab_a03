# A 组工作说明

## 1. A 组定位

A 组负责准备 GNU Make 项目的依赖声明故障样例，并建立连续提交基线，为后续 BuildChecker、EChecker 提供可判断对错、可复现、可追溯的输入和证据。

A 组只聚焦以下内容：

- MD / RD 样例。
- C0 / C1 / C2 连续提交。
- Linux 原始跟踪证据。
- 人工 ORACLE 答案与实际运行记录分离。

A 组不负责 DRAFT 样本、MDFixer 补丁验证、Docker 构建等 B 组任务。

---

## 2. A 组已完成内容

### 2.1 MD/RD 样例

样例来源：E2 `artifacts/minicalc/c0/`

- 源码：`fixtures/md-rd/src/`
- Makefile：`fixtures/md-rd/Makefile`
- ORACLE：`fixtures/md-rd/ORACLE_findings.json`（来自 E2 `contracts/examples/minicalc/md-only-report-c0.json`）
- 契约：`graph.schema.json`、`finding-id-v1.json`

构建：`make`
运行：`./minicalc`
清理：`make clean`

| 场景 | 命令 | 预期 |
|---|---|---|
| 第一次完整构建 | `make && ./minicalc` | 输出与 E2 报告一致 |
| 只改 `config.h` | `make && ./minicalc` | 增量仍输出旧值，证明 MD |
| clean build | `make clean && make && ./minicalc` | 输出新值，与增量对照 |
| 修改冗余头文件 | `make` | 出现多余编译，证明 RD |

---

### 2.2 C0 / C1 / C2 连续提交

已生成 C0、C1、C2 三个连续提交，位于：

```text
fixtures/commits/C0/
fixtures/commits/C1/
fixtures/commits/C2/
```

#### C0：正确的初始版本

```c
// main.c
#include <stdio.h>
#include "config.h"

#ifndef MODE
#define MODE 0
#endif

int main(void) {
    printf("%d\n", BASE + MODE);
    return 0;
}
```

```c
// config.h
#define BASE 10
```

```make
# Makefile
CFLAGS = -O0

app: main.o
	cc main.o -o app

main.o: main.c config.h
	cc $(CFLAGS) -c main.c -o main.o

clean:
	rm -f main.o app
```

预期：clean build 输出 10。

#### C1：新增 include，遗漏声明

```c
// main.c
#include <stdio.h>
#include "config.h"
#include "feature.h"

#ifndef MODE
#define MODE 0
#endif

int main(void) {
    printf("%d\n", BASE + FEATURE + MODE);
    return 0;
}
```

```c
// feature.h
#define FEATURE 2
```

```make
# Makefile 保持
main.o: main.c config.h
```

预期：clean build 输出 12；人工预期发现 `MD: main.o -> feature.h`。

#### C2：只改变编译命令

C2 源码保持 C1，只改 Makefile：

```make
CFLAGS = -O0 -DMODE=7
```

预期：增量输出 12；clean build 输出 19。  
说明普通 Make 的时间戳检查可能漏掉命令变化。

已实际执行并保存证据：

```text
work/<timestamp>/commits/C0/
work/<timestamp>/commits/C1/
work/<timestamp>/commits/C2_incremental/
work/<timestamp>/commits/C2_clean/
work/<timestamp>/commits/EXPECTED.json
```

`EXPECTED.json` 示例：

```json
{
  "C0": { "clean": 10 },
  "C1": { "clean": 12, "expected_finding": "MD: main.o -> feature.h" },
  "C2": { "incremental": 12, "clean": 19, "note": "只改编译命令，普通 make 可能不重建" }
}
```

还保存了命令快照：

```bash
make -n -B main.o
```

用于比较 C1 与 C2 的编译命令变化。

---

### 2.3 Linux 原始跟踪证据

A 组提供 Linux 跟踪脚本：

```text
scripts/linux_trace.sh
```

用法：

```bash
bash scripts/linux_trace.sh <工作目录> [关注的头文件名...]
```

示例：

```bash
bash scripts/linux_trace.sh work/<timestamp>/md-rd feature.h config.h
```

`run_lab.py` 会自动调用，针对 `work/<timestamp>/md-rd/` 生成证据。

脚本内部执行：

```bash
make clean
strace -ff -o trace.log -e trace=%file,%process make
grep -R feature.h trace.log*
grep -R config.h trace.log*
make -pn
```

证据保存到：

```text
work/<timestamp>/md-rd/evidence/linux-verified/
```

包含：

- `trace.log`、`trace.log.*`
- `make.stdout`、`make.stderr`
- `access-feature_h.log`
- `access-config_h.log`
- `make-pn.txt`
- `environment.txt`

用途：

- 记录进程、路径和文件访问。
- 区分编译器与构建器的读取。
- 说明只看到 `openat` 还不足以直接判 MD。
- 后续 BuildChecker 需要构图与归一化。
- `make -pn` 用于查看 Make 解析的声明。

与 E2 的衔接：

- 关注的头文件名来自 E2 Minicalc 的 MD 发现，例如 `feature.h`。
- `environment.txt` 记录的工具版本应与 E2 `validate.py` 运行环境一致。
- 若 E2 已提供 Minicalc 构建日志，E3 的 `strace` 作为补充原始证据。

---

### 2.4 环境与版本记录

A 组已记录实验环境：

```text
OS: ...
CPU: ...
git version: ...
make version: ...
cc version: ...
python3 version: ...
strace version: ...
```

保存位置：

```text
work/<timestamp>/evidence/linux-verified/environment.txt
```

注意：Mac 的 `cc` 与容器内 `gcc` 可能不同，正式性能比较要保持同一环境。

---

### 2.5 实际运行记录

A 组已保存：

- `work/<timestamp>/commands.json`：所有实际命令、工作目录、退出码、stdout、stderr。
- `work/<timestamp>/observations.json`：关键观察结论。

示例 `commands.json`：

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

示例 `observations.json`：

```json
[
  {
    "key": "A_MD_RD",
    "value": "完成 MD/RD 样例运行",
    "note": "预期：增量输出 1；clean 输出 2；修改 unused.h 触发多余编译。"
  }
]
```

---

## 3. A 组交付物清单

A 组已交付：

1. `fixtures/md-rd/`：MD/RD 样例源码与 ORACLE 报告。
2. `fixtures/commits/C0`、`C1`、`C2`：连续提交源码与 Makefile。
3. `work/<timestamp>/md-rd/`：MD/RD 实际运行证据。
4. `work/<timestamp>/commits/`：C0/C1/C2 实际运行证据与 `EXPECTED.json`。
5. `work/<timestamp>/evidence/linux-verified/`：Linux 原始跟踪证据。
6. `work/<timestamp>/commands.json`：实际命令记录。
7. `work/<timestamp>/observations.json`：观察结果记录。
8. `docs/A_GROUP.md`：本说明。
9. `docs/EXPECTED_RESULTS.md`：预期结果汇总中的 A 组部分。

---

## 4. A 组检查清单

完成 A 组后，应检查：

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
- [ ] Linux `strace` 和 `make -pn` 证据是否保存？

---

## 5. A 组与后续任务关系

| 后续任务 | 使用的 A 组证据 |
|---|---|
| E5 BuildChecker | `fixtures/md-rd/`、`work/<timestamp>/md-rd/` |
| E8 EChecker | `fixtures/commits/`、`work/<timestamp>/commits/EXPECTED.json` |
| E10 增量 / 全量比较 | C0/C1/C2 实际运行记录与命令快照 |
| E12 接入真实数据联调 | `fixtures/` 与 `work/` 中的真实提交和证据 |

---

## 6. A 组不做的事

A 组不负责：

- DRAFT 样本的 Docker 构建与运行。
- MDFixer 补丁应用与修复验证。
- 四种声明风格完整样例。
- 隐式规则与 `.d` 文件验证。
- 无效候选与恢复验证。

这些属于 B 组任务，见 `docs/B_GROUP.md`。

## 与 E2 的衔接

A 组的 MD/RD 与 C0/C1/C2 不再使用玩具样例，而是从 E2 派生：

- 项目：`e2-a03/artifacts/minicalc/c0/src`
- Makefile：`e2-a03/artifacts/minicalc/c0/Makefile`
- ORACLE：`e2-a03/contracts/examples/minicalc/md-only-report-c0.json`
- 图格式：`e2-a03/contracts/graph.schema.json`
- finding_id：`e2-a03/contracts/finding-id-v1.json`

E3 输出必须通过 `e2-a03/validate.py` 校验。