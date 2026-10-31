# E5-A：从原始构建记录解释 MD/RD（241250093）

## 1. 运行信息

| 项 | 值 |
|---|---|
| 学号 | 241250093 |
| 分支 | `student/241250093/e5-e7` |
| 源码提交 | `502b927f7cf175259be9940e4c3caab0ef33731e`（`work/e5-01/source-commit.txt`） |
| 服务镜像 | `course1027-buildchecker:241250093` |
| 构建命令 | `python3 scripts/course.py build --out work/build-01 --build-timeout 1200` → `15 passed`，退出码 0 |
| 采集命令 | `python3 scripts/course.py e5 --out work/e5-01` → `E5_EXIT=0` |
| 证据目录 | `work/e5-01/`（`trace/t.*`、`make-db.txt`、`program-output.txt`） |
| 程序输出 | `1`（`evidence/program-output.txt`） |
| 采集时间 | 2026-10-30 16:26 UTC（北京时间 2026-10-31 00:26） |
| 工具版本 | GNU Make 4.4.1、gcc 14（cc1 位于 `/usr/libexec/gcc/x86_64-linux-gnu/14/cc1`）、Docker 29.1.3 |
| 运行环境 | Ubuntu 22.04.5 LTS / kernel 5.15.0-186-generic / 2 CPU / 1.7 GiB / Docker 29.1.3 |

## 2. 输入样例

- `main.c` 中 `#include "config.h"`，实际需要读取 `config.h` 才能完成编译。
- `Makefile` 中对 `main.o` 的依赖声明为：`main.o: main.c unused.h`
  （证据行：`evidence/make-db.txt:1061` → `main.o: main.c unused.h`）

即：声明里**漏掉了**真实需要的 `config.h`，**多写了**从未被读取的 `unused.h`。

## 3. 进程树与关键系统调用

### 3.1 进程派生链（由 `clone` 返回值与 `execve` 配对得到）

| PID（t.文件） | 进程 | 关键 `execve` 证据（文件:行号） | 父进程 / 派生证据 |
|---|---|---|---|
| t.14 | `make` | `t.14:1` `execve("/usr/bin/make", ["make", "-p", "app"], ...) = 0` | 采集器直接启动 |
| t.15 | `cc`（编译） | `t.15:1` `execve("/usr/bin/cc", ["cc", "-c", "main.c", "-o", "main.o"], ...) = 0` | `t.14:55` `clone(...) = 15` |
| t.16 | `cc1`（编译器本体） | `t.16:1` `execve("/usr/libexec/gcc/x86_64-linux-gnu/14/cc1", [... "main.c" ... "-o" "/tmp/ccuHGBbW.s"], ...) = 0` | `t.15:64` `clone(...) = 16` |
| t.17 | `as`（汇编器） | `t.17:5` `execve("/usr/bin/as", ["as", "--64", "-o", "main.o", "/tmp/ccuHGBbW.s"], ...) = 0`（前 4 行 `t.17:1~4` 为 PATH 逐个探测的 `ENOENT`） | `t.15:84` `clone(...) = 17` |
| t.18 | `cc`（链接） | `t.18:1` `execve("/usr/bin/cc", ["cc", "main.o", "-o", "app"], ...) = 0` | `t.14:66` `clone(...) = 18` |
| t.19 | `collect2` | `t.19:1` `execve("/usr/libexec/gcc/x86_64-linux-gnu/14/collect2", [... "-o" "app" ... "main.o" ...], ...) = 0` | `t.18:129` `clone(...) = 19` |
| t.20 | `ld` | `t.20:1` `execve("/usr/bin/ld", [... "-o" "app" ... "main.o" ...], ...) = 0` | `t.19:96` `clone(...) = 20` |

链形：`make(t.14) → cc(t.15) → cc1(t.16) / as(t.17)`，`make(t.14) → cc(t.18) → collect2(t.19) → ld(t.20)`。

### 3.2 关键文件 IO 证据

| 事实 | 证据（文件:行号） | 原始内容 |
|---|---|---|
| `cc1` 成功读取 `config.h` | `evidence/trace/t.16:580` | `openat(AT_FDCWD, "config.h", O_RDONLY\|O_NOCTTY) = 4` |
| `cc1` 的输入是 `main.c` | `evidence/trace/t.16:1` | `execve(... "main.c" ... "-o" "/tmp/ccuHGBbW.s" ...)` |
| `as` 写出 `main.o` | `evidence/trace/t.17:5` | `execve("/usr/bin/as", ["as", "--64", "-o", "main.o", "/tmp/ccuHGBbW.s"]) = 0` |
| `ld` 读入 `main.o` 生成 `app` | `evidence/trace/t.20:1` | `execve("/usr/bin/ld", [... "-o" "app" ... "main.o" ...]) = 0` |
| 无任何进程读取 `unused.h` | `grep -c 'unused\.h' trace/t.*` | `t.14:1`、`t.15:0`、`t.16:0`、`t.17:0`、`t.18:0`、`t.19:0`、`t.20:0` |

补充：`main.c` 的读行（`t.16` 中 `openat(..., "main.c", O_RDONLY...)`）与 `main.o` 的写行（`t.17` 中 `openat(..., "main.o", O_WRONLY|O_CREAT...)`）可用
`grep -n 'main\.c' work/e5-01/evidence/trace/t.16` 与 `grep -n 'main\.o' work/e5-01/evidence/trace/t.17` 直接定位；
`unused.h` 在 `t.14` 中的那 1 次出现是 `make` 对依赖文件做存在性/时间戳检查（`newfstatat`），并非读取内容，可用
`grep -n 'unused\.h' work/e5-01/evidence/trace/t.14` 确认。

## 4. 归属推理

1. **`config.h` 属于 `main.o` 的编译作业。**&#8203;
   `config.h` 的唯一读取点是 `t.16:580`，而 `t.16` 由 `t.15` 的 `clone`（`t.15:64`）派生，`t.15` 的命令行是
   `cc -c main.c -o main.o`，即 make 为产出 `main.o` 而启动的编译进程；`t.16` 是 gcc 14 的编译本体 `cc1`，
   其唯一输出是 `main.o`（经 `t.17` 的 `as` 落盘）。因此 `config.h` 的所有者只有一个：`main.o` 的编译作业。
   而 `make-db.txt:1061` 的声明 `main.o: main.c unused.h` 中并没有 `config.h`——这就是**漏声明（MD）**&#8203;。

2. **`unused.h` 是冗余声明。**&#8203;
   `grep -c 'unused\.h'` 在整个 trace 中只有 `t.14`（make 自己）出现 1 次，且该次是 make 在判断依赖文件
   是否存在/是否需要重编时的 `newfstatat` 检查，不是内容读取；`t.15~t.20`（cc / cc1 / as / collect2 / ld）
   的计数全为 0，说明没有任何编译或链接作业读过它。声明里写了它、实际却不影响任何产物——这就是**冗余声明（RD）**&#8203;。

3. **`app` 的声明是正确的。**&#8203;
   `t.18` 的 `cc main.o -o app` → `collect2(t.19)` → `ld(t.20)`，链接阶段实际输入就是 `main.o`，
   与 Makefile 中 `app: main.o` 一致，既无 MD 也无 RD。

## 5. 结论表

| 目标 | 实际读取的输入 | Makefile 声明 | MD（漏声明） | RD（冗余声明） |
|---|---|---|---|---|
| `main.o` | `main.c`、`config.h` | `main.c`、`unused.h`（`make-db.txt:1061`） | **`config.h`**（`t.16:580`） | **`unused.h`**（`t.15~t.20` 计数全 0） |
| `app` | `main.o`（`t.20:1`） | `main.o` | 无 | 无 |

## 6. 与论文的差异

| 维度 | 论文做法 | 本次实验做法 | 差异影响 |
|---|---|---|---|
| 归因方式 | 程序化、自动跟踪并归并依赖 | 人工从 strace 原始行 + 父子进程关系推导 | 人可读、可复核，但难以规模化 |
| 规模 | 面向任意规模项目 | 单样例（`fixtures/md-rd/`）一次全量构建 | 只验证方法可行性，未验证性能与扩展性 |
| 噪音过滤 | 论文需处理系统头/库文件 | 只统计项目根目录内的文件，天然滤掉 `/usr/include`、`/usr/lib` 等系统路径 | 简化归因，但也可能漏掉来自包管理器的真实依赖 |
| 记录粒度 | 依赖图级别 | 系统调用级别（全进程 strace + `make -p` 数据库） | 证据更原始、更可追溯，但数据量大 |
| 声明对照 | 自动对比 | 人工对照 `make-db.txt` 与 trace | 结论明确，但依赖人工判读 |
