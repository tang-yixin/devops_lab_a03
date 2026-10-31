# E5-A：从原始构建记录解释 MD/RD（241250107）
## 1. 运行信息
- 源码提交：d93fb9498e16262d2c650e79e7aa36393e11b886
- 镜像：course1027-buildchecker:241250107
- 运行命令与退出码：`python3 scripts/course.py e5 --out work/e5-01`，退出码 0
- 采集时间：2026-10-31
- 工具版本：GNU Make 4.3、gcc 14、Docker 29.1.3

## 2. 输入样例
- `main.c` 包含 `config.h`
- `Makefile` 声明 `main.o: main.c unused.h`

## 3. 进程树与关键系统调用
构建过程中的进程派生链及关键系统调用如下：
- **make** (`t.15`) 派生出编译进程 `cc` (`t.16`) 进行目标文件编译。
- **cc** (`t.16`) 派生出编译器 `cc1` (`t.17`) 和汇编器 `as` (`t.18`)。
- 编译器 **cc1** (`t.17`) 成功读取头文件：
  `work/e5-01/evidence/trace/t.17:580:openat(AT_FDCWD, "config.h", O_RDONLY|O_NOCTTY) = 4`
- 汇编器 **as** (`t.18`) 生成目标文件 `main.o`。
- **make** (`t.15`) 派生出链接进程 `cc` (`t.19`)，并进一步通过 `collect2` (`t.20`) 调用链接器 **ld** (`t.21`) 读取 `main.o` 生成 `app`。
- 经核对，除了 make 进程对 `unused.h` 的存在性检查外，没有任何编译进程读取 `unused.h`。

## 4. 归属推理
`config.h` 被 `t.17`（cc1 编译器）成功读取。通过进程树可以确认，`t.17` 是由 `t.16`（cc）派生出来的，而 `t.16` 的完整执行命令是 `cc -c main.c -o main.o`，其唯一输出目标是 `main.o`。因此，`config.h` 是 `main.o` 编译作业中实际被读取的依赖。

## 5. 结论表
| 目标 | 实际读取的项目依赖 | Make 声明 | 结论 |
|---|---|---|---|
| main.o | main.c、config.h | main.c、unused.h | **MD=config.h，RD=unused.h** |
| app | main.o | main.o | 无 |

## 6. 与论文的差异
- 本次实验采用人工分析 `strace` 的方式推导依赖，而论文使用了程序化跟踪。
- 本次仅测试单个 C 语言小样例的完整构建过程，而论文面向任意规模和复杂度的构建环境。
- 本次分析需依靠项目根目录边界过滤系统头文件，而论文有更复杂的环境隔离。
- Makefile 的声明行位于 `make-db.txt` 的第 1061 行：`main.o: main.c unused.h`。
