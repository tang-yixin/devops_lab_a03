# E5-A：从原始构建记录解释 MD/RD（241250106）

## 1. 运行信息

| 项 | 值 |
|---|---|
| 学号 | 241250106（王子贤，A03 组，A 轨道） |
| 分支 | `student/241250106/e5-e7` |
| 源码提交 | `e15750b43aedb045e8677aeeabd36f9e5a56ffe2`（`work/e5-01/source-commit.txt`） |
| 服务镜像 | `course1027-buildchecker:241250106`，镜像 ID `sha256:d41cef0cf7d6ce1990cde32caa21f0e125e555c6390faa67b7809f4865602ebb` |
| 构建命令 | `python3 scripts/course.py build --out work/build-01 --build-timeout 1200` → `15 passed`，`BUILD_AND_TEST_EXIT_CODE=0` |
| 采集命令 | `python3 scripts/course.py e5 --out work/e5-01` → `E5_EXIT=0` |
| 证据目录 | `work/e5-01/`（`evidence/trace/t.*`、`evidence/make-db.txt`、`evidence/program-output.txt`、`runner/`） |
| 程序输出 | `1`（`evidence/program-output.txt`） |
| 采集时间 | 2026-10-31T06:25:55Z UTC（北京时间 2026-10-31 14:25:55，`work/e5-01/invocation.json`） |
| 服务容器 | `9f6e9dc9b6aa6b99265f3b7813369ec866575f194717dfe847d8ab6f8d8219e2`（`work/e5-01/service-container-id.txt`） |
| 工具版本 | 容器内 GNU Make 4.4.1、gcc 14.2.0（`cc1` 位于 `/usr/libexec/gcc/x86_64-linux-gnu/14/cc1`）、binutils 2.44、strace 6.13、Python 3.13.14；宿主机 Docker 29.1.3 |
| 运行环境 | Ubuntu 22.04.5 LTS / kernel 5.15.0-186-generic / 2 CPU / 1.7 GiB / 磁盘 67.3 GiB |

工具版本取自镜像内 `/opt/toolchain.lock`（`gcc=4:14.2.0-1`、`make=4.4.1-2`、`strace=6.13+ds-1`），
Make 版本另有原始证据 `work/e5-01/evidence/make-db.txt:3` → `# GNU Make 4.4.1`。

## 2. 输入样例

- `main.c` 第二行为 `#include "config.h"`，`main()` 用 `config.h` 里的 `VALUE` 打印，
  因此**必须**读到 `config.h` 才能编译通过。
- `Makefile` 对 `main.o` 的依赖声明为：`main.o: main.c unused.h`
  （原始证据行：`evidence/make-db.txt:1061` → `main.o: main.c unused.h`），
  链接规则为 `app: main.o`（`evidence/make-db.txt:609` → `app: main.o`）。

即：声明里**漏掉了**真实需要的 `config.h`，又**多写了**从未被读取的 `unused.h`。

## 3. 进程树与关键系统调用

### 3.1 进程派生链（由 `clone` 返回值与 `execve` 配对得到）

| PID（t. 文件） | 进程 | 关键 `execve` 证据（文件:行号） | 父进程 / 派生证据 |
|---|---|---|---|
| t.14 | `make` | `t.14:1` `execve("/usr/bin/make", ["make", "-p", "app"], ...) = 0` | 采集器在容器内直接启动 |
| t.15 | `cc`（编译） | `t.15:1` `execve("/usr/bin/cc", ["cc", "-c", "main.c", "-o", "main.o"], ...) = 0` | `t.14:55` `clone(child_stack=..., flags=CLONE_VM\|CLONE_VFORK\|SIGCHLD) = 15` |
| t.16 | `cc1`（编译器本体） | `t.16:1` `execve("/usr/libexec/gcc/x86_64-linux-gnu/14/cc1", [... "main.c" ... "-o" "/tmp/ccRAuHNM.s"], ...) = 0` | `t.15:64` `clone(...) = 16` |
| t.17 | `as`（汇编器） | `t.17:5` `execve("/usr/bin/as", ["as", "--64", "-o", "main.o", "/tmp/ccRAuHNM.s"], ...) = 0`（`t.17:1~4` 为 PATH 逐个探测的 `ENOENT`） | `t.15:84` `clone(...) = 17` |
| t.18 | `cc`（链接） | `t.18:1` `execve("/usr/bin/cc", ["cc", "main.o", "-o", "app"], ...) = 0` | `t.14:66` `clone(...) = 18` |
| t.19 | `collect2` | `t.19:1` `execve("/usr/libexec/gcc/x86_64-linux-gnu/14/collect2", [... "-o" "app" ... "main.o" ...], ...) = 0` | `t.18:129` `clone(...) = 19` |
| t.20 | `ld` | `t.20:1` `execve("/usr/bin/ld", [... "-o" "app" ... "main.o" ...], ...) = 0` | `t.19:96` `clone(...) = 20` |

链形：`make(t.14) → cc(t.15) → cc1(t.16) / as(t.17)`；`make(t.14) → cc(t.18) → collect2(t.19) → ld(t.20)`。
每个 `clone` 前一行都有 `clone3(...) = -1 ENOSYS`（如 `t.14:54`、`t.15:63`、`t.18:128`、`t.19:95`），
说明容器内核不提供 `clone3`，glibc 回退到 `clone`，子进程 PID 与 `t.<PID>` 文件名一一对应。

### 3.2 关键文件 IO 证据

| 事实 | 证据（文件:行号） | 原始内容 |
|---|---|---|
| `cc1` 的输入是 `main.c` | `evidence/trace/t.16:67` | `openat(AT_FDCWD, "main.c", O_RDONLY\|O_NOCTTY) = 3` |
| `cc1` 成功读取 `config.h` | `evidence/trace/t.16:580` | `openat(AT_FDCWD, "config.h", O_RDONLY\|O_NOCTTY) = 4` |
| `as` 写出 `main.o` | `evidence/trace/t.17:23` | `openat(AT_FDCWD, "main.o", O_RDWR\|O_CREAT\|O_TRUNC, 0666) = 3` |
| `ld` 读入 `main.o` | `evidence/trace/t.20:82` | `openat(AT_FDCWD, "main.o", O_RDONLY) = 7` |
| `ld` 生成 `app` | `evidence/trace/t.20:71` | `openat(AT_FDCWD, "app", O_RDWR\|O_CREAT\|O_TRUNC, 0666) = 3` |
| `make` 只对 `unused.h` 做存在性检查 | `evidence/trace/t.14:46` | `newfstatat(AT_FDCWD, "unused.h", {st_mode=S_IFREG\|0644, st_size=43, ...}, 0) = 0` |
| 没有任何进程读取 `unused.h` | `grep -c 'unused\.h' trace/t.*` | `t.14:1`、`t.15:0`、`t.16:0`、`t.17:0`、`t.18:0`、`t.19:0`、`t.20:0`；`grep -l` 仅命中 `t.14` |

补充：`config.h` 在整个 trace 中**只出现一次**（`grep -n 'config\.h' trace/t.*` 仅返回 `t.16:580`），
读取者是 `cc1`；`main.o` 的两次 `openat`（`t.17:23` 写、`t.20:82` 读）分别属于汇编器 `as` 和链接器 `ld`。

## 4. 归属推理

1. **`config.h` 属于 `main.o` 的编译作业。**
   `config.h` 的唯一读取点是 `t.16:580`。`t.16` 由 `t.15` 在 `t.15:64` 处 `clone` 派生，
   而 `t.15` 的命令行是 `cc -c main.c -o main.o`（`t.15:1`），并且是 `make` 在 `t.14:55` 处
   为重建 `main.o` 而启动的编译进程；`t.16` 是这次编译的编译器本体 `cc1`，它把结果写到临时汇编
   `/tmp/ccRAuHNM.s`（`t.16:1`），再由同父的 `as` 落盘成 `main.o`（`t.17:23`）。
   因此 `config.h` 这次读取的所有者是唯一的：`main.o` 的编译作业。
   而 `make-db.txt:1061` 的声明 `main.o: main.c unused.h` 中没有 `config.h` —— 这就是**漏声明（MD）**。

2. **`unused.h` 是冗余声明。**
   `grep -l 'unused\.h' trace/t.*` 只命中 `t.14`（`make` 自己），且唯一一次出现是
   `t.14:46` 的 `newfstatat`——make 在判断依赖文件是否存在/是否需要重编时的元数据检查，
   不是内容读取；`t.15~t.20`（`cc` / `cc1` / `as` / `cc` / `collect2` / `ld`）计数全为 0。
   声明里写了它、实际却不影响任何产物 —— 这就是**冗余声明（RD）**。

3. **`app` 的声明是正确的。**
   `t.18` 的 `cc main.o -o app`（`t.18:1`）→ `collect2(t.19)` → `ld(t.20)`，
   链接阶段真正读入的输入只有 `main.o`（`t.20:82`），输出 `app`（`t.20:71`），
   与 Makefile 中 `app: main.o`（`make-db.txt:609`）一致，既无 MD 也无 RD。

## 5. 结论表

| 目标 | 实际读取的输入 | Makefile 声明 | MD（漏声明） | RD（冗余声明） |
|---|---|---|---|---|
| `main.o` | `main.c`（`t.16:67`）、`config.h`（`t.16:580`） | `main.c`、`unused.h`（`make-db.txt:1061`） | **`config.h`** | **`unused.h`**（`t.15~t.20` 计数全 0，仅 `t.14:46` 一次 stat） |
| `app` | `main.o`（`t.20:82`） | `main.o`（`make-db.txt:609`） | 无 | 无 |

## 6. 与论文的差异

| 维度 | 论文做法 | 本次实验做法 | 差异影响 |
|---|---|---|---|
| 归因方式 | 程序化、自动跟踪并归并依赖 | 人工从 strace 原始行 + 父子进程关系推导 | 人可读、可复核，但难以规模化 |
| 规模 | 面向任意规模项目 | 单样例（`fixtures/md-rd/`）一次全量构建 | 只验证方法可行性，未验证性能与扩展性 |
| 噪音过滤 | 论文需处理系统头文件与库文件 | 只统计项目根目录内的文件，天然滤掉 `/usr/include`、`/lib/x86_64-linux-gnu` 等系统路径（如 `t.17:6~14` 的 `libbfd`/`libz`/`libc` 打开） | 简化归因，但可能漏掉来自包管理器的真实依赖 |
| 记录粒度 | 依赖图级别 | 系统调用级别（全进程 strace + `make -p` 数据库） | 证据更原始、更可追溯，但数据量大 |
| 声明对照 | 自动对比 | 人工对照 `make-db.txt` 与 trace | 结论明确，但依赖人工判读 |
