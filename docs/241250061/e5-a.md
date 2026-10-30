# E5-A：从原始构建记录解释 MD/RD（241250061）

## 1. 运行信息

- 轨道/阶段/入口：A / e5 / cloud-v1
- 源码提交：`6a8e7301250fcea236f977381f5c16fc6c0a5fba`（main，见 work/e5-01/source-commit.txt）
- 服务镜像：`course1027-buildchecker:241250061`（构建记录 work/build-01/image/）
- 运行命令与退出码：`python3 scripts/course.py e5 --out work/e5-01`，退出 0
- 采集时间（UTC）：2026-10-30T11:22:58Z（work/e5-01/invocation.json）
- 工具版本：宿主 Docker 29.1.3；容器内 GNU Make 4.4.1、gcc 14（/usr/libexec/gcc/x86_64-linux-gnu/14/）、strace `-ff -s 4096 -e trace=%file,%process`

## 2. 输入样例（fixtures/md-rd）

`main.c` 包含 `config.h` 并使用 VALUE；`config.h` 定义 `VALUE=1`；Makefile 对象规则为
`main.o: main.c unused.h`；`unused.h` 未被任何源文件包含。

## 3. 进程树与关键系统调用

```text
t.14 make -p app
├─ t.15 cc -c main.c -o main.o        编译驱动
│   ├─ t.16 cc1                        编译器本体
│   └─ t.17 as --64 -o main.o ...      汇编器
└─ t.18 cc main.o -o app               链接驱动
    └─ t.19 collect2
        └─ t.20 ld -o app ... main.o   链接器
```

| 证据 | 文件:行 | 内容 |
|---|---|---|
| cc1 读 main.c | trace/t.16:67 | `openat(AT_FDCWD, "main.c", O_RDONLY\|O_NOCTTY) = 3` |
| cc1 读 config.h | trace/t.16:580 | `openat(AT_FDCWD, "config.h", O_RDONLY\|O_NOCTTY) = 4` |
| as 写 main.o | trace/t.17:23 | `openat(AT_FDCWD, "main.o", O_RDWR\|O_CREAT\|O_TRUNC) = 3` |
| make 仅检查 unused.h 存在 | trace/t.14:46 | `newfstatat(AT_FDCWD, "unused.h", {S_IFREG\|0644,...}) = 0` |
| ld 读 main.o 生成 app | trace/t.20:1,81 | execve 参数含 `-o app ... main.o`，随后 `newfstatat("main.o")` |
| 程序输出 | evidence/program-output.txt | `1` |

## 4. 归属推理

config.h 的成功读取发生在 t.16（cc1）。t.16 由 t.15 派生，t.15 的命令行是
`cc -c main.c -o main.o`，其子进程 t.17（as）在 t.17:23 创建并写入 main.o——
即该编译作业唯一输出是 main.o。因此 config.h 属于目标 main.o 的实际依赖。
搜索时出现的 stat/access 及失败尝试（如 t.17:1–4 中 as 的 ENOENT 路径搜索）不作为读取证据，
结论取自成功读打开及其所属构建进程。

## 5. 人工结论（MD/RD）

| 目标 | 实际读取（项目内） | Make 声明 | MD（漏声明） | RD（冗余声明） |
|---|---|---|---|---|
| main.o | main.c、config.h | main.c、unused.h（make-db.txt:1061） | config.h | unused.h |
| app | main.o | main.o | 无 | 无 |

- unused.h 仅被 make 自身做存在性检查（t.14:46），t.15—t.20 任何构建进程都未读取它
  （grep 计数 t.15—t.20 均为 0）→ 冗余声明。
- 过滤规则：cc1 同时读取 /usr/include、/usr/lib/gcc/... 下的系统头文件，均位于项目根目录
  之外，不列入项目依赖集合。

## 6. 与论文跟踪实现和实验规模的差异

- 论文实现以系统调用拦截做进程级依赖跟踪并程序化输出依赖集合；本实验用 strace 离线采集
  全进程 trace 后人工归属，结论依赖上表的行号证据。
- 论文覆盖任意规模项目与增量构建场景；本实验限定 GNU Make、单 Make 进程、单次全量构建、
  每个构建作业一个最终输出（2 个目标、4 个项目文件的固定样例）。
- 论文实现有显式的项目边界/虚拟化配置；本实验以“项目根目录”为边界手工过滤系统头文件。
