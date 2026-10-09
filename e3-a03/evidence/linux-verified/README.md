# Linux 原始跟踪分析（E3-A06）

> 依据 PPT 第 28 页。在 WSL Ubuntu 22.04.5 (x86_64) 对 Minicalc c0 执行
> `strace -ff -e trace=%file,%process make`，用系统调用证据区分「构建器读取」与
> 「编译器读取」。原始证据见同目录 `strace-evidence.md`。

## 方法

1. `make clean` 清空产物，确保重新编译。
2. `strace -ff` 跟踪 `make` 及其子进程的全部文件/进程系统调用。
3. `make -pn` 抓取 Make 解析出的**声明依赖**。
4. 对每个头文件统计两类调用：
   - `newfstatat` —— make 检查文件是否存在/时间戳（**声明层面**）。
   - `openat ... O_RDONLY` —— 编译器实际打开读取（**实际依赖层面**）。

## 进程区分

| 进程 | 角色 |
|---|---|
| `/usr/bin/make` | 构建器：读 Makefile、检查文件时间戳 |
| `/usr/bin/gcc` | 编译器驱动 |
| `cc1` / `as` / `collect2` / `ld` | 编译、汇编、链接各阶段 |

## 结论

| 头文件 | 实际读取 (openat) | 判定 |
|---|---|---|
| config.h / parser.h / token.h / util.h | 有 | 真实依赖（实际读取） |
| **legacy.h** | **无（0 次 openat）** | **REDUNDANT：Makefile 声明但编译器从未读取** |

## 解读

- `legacy.h` 只出现 `newfstatat`（make 因 Makefile 里 `util.o: ... legacy.h` 去检查它），
  **没有一次 `openat`**（gcc 编译 util.c 时根本没打开它）。这从系统调用层面实锤了
  E2 报告中「util.o → legacy.h 为 REDUNDANT」的结论。
- 其余四个头文件均有 `openat`，是真实读取依赖。

## 局限（如实记录）

- `openat` 只能证明「读了」，不能直接反推「读了这个文件就必须声明它」——
  PPT 第 28 页明确「只看到 openat 还不足以直接判 MD」。
- 完整 MD/RD 判定需要后续 BuildChecker 构图与归一化（E5），本阶段只做原始跟踪采集。
