# 决策记录

背景与约束：本次 E8—E9 每人至少 1 个自有测试，方向由组长分配以避免组内重复（组长已占"声明补齐复用""新建头文件间接包含""头文件内加 include""删冗余声明消 RD"；093 占"helper.c 直接包含"与"依赖行换成 main.c config.h"；107 占"加 include 同时补声明"与"config.h VALUE 1→2"）。我分到 **E8：删除未被包含的 extra.h → 指纹变、两目标刷新、发现集合不变**，**E9：CFLAGS -O0→-O1 → 配置指纹变、两目标刷新、发现不变**。约束：只能改 `labs/e8e10/test_profile.py`（`lab.py` 的保守刷新是 E10 矩阵断言的前提，不动机），测试要在成品镜像内、`--network none`、无 root 的容器里可重复跑，且样例必须落临时目录，不能碰手册 OUT 里的项目。

选择与替代方案：
A（E8）：选"删除一个从未被 `#include` 的头文件"。理由是它能**只动 key 里的文件集合、不动任何文件内容**：`scan()` 的 `key.directives` 是按文件名收录所有 `.c/.h` 的预处理指令行，`extra.h` 消失后 key 必然变化，而 `gcc -MM` 的结果与声明行都不含 `extra.h`，于是"刷新但发现不变"可以在同一份数据里被精确断言。替代方案否掉的原因：(a) 在 `helper.c` 里加 include——已被 093 占用，且会新增 MD，方向变成"发现变化"；(b) 新建头文件经 `config.h` 间接包含——组长已占，同样新增 MD；(c) 改 Makefile 配方行字节——虽然也触发刷新，但那是"配方身份"而不是"文件集合"，与 C1/C3 的复用叙事混在一起，解释力弱。
B（E9）：选 `CFLAGS` 从 `-O0` 改为 `-O1`。理由是 `-O1` 在白名单内（不会触发 `UNSUPPORTED_FLAGS`），且只影响代码生成、按定义不可能改变 `#include` 关系，于是"key.flags 变 → 刷新，而实际图/声明图/发现不变"是可解释的强预期，而不是巧合。替代方案否掉的原因：(a) 改 `config.h` 的 VALUE——107 已占，且那属于 `directives`，测不到 `flags` 这个成员；(b) 改 Makefile 声明行——走复用分支，完全不碰配置身份；(c) 加 `-DMODE=1`——虽在 flags 白名单里，但它改变预处理宏，容易与"依赖集不变"的预期纠缠，且在 E8/E9 的叙事里没有 `-O1` 干净。
另外每个用例都额外加了**反例方向的断言**（E8：`extra.h` 不在任何实际依赖里、增量与全量三集合一致；E9：`-O7` 必须抛 `UNSUPPORTED_FLAGS`），用来说明"配置/输入不被识别时应拒绝，而不是当作没变化"。

代价与覆盖范围：保守刷新是 key 级而不是边级，代价是删一个无关文件也会让两个目标全部重算——在真实仓库里这会放大无效分析成本，我的测试恰好把这条代价固化成可观察行为（而不是靠注释声明）。覆盖范围有限：只覆盖 `direct` 声明风格的两个翻译单元，`macro`/`mixed` 风格、系统头文件、宏条件编译、多目标共享同一 key 的情形都未覆盖；`-O0 -DMODE=1` 这个白名单分支也没测。E8 用例只证明"文件移除"会失效，没有证明"文件新增但无人包含"也会失效（同一 key 机制，但未单独断言）。

验证命令与实际证据：在 `student/241250106/e8-e10` 分支、`course-e8e10:241250106` 镜像内执行
`docker run --rm --network none --user "$(id -u):$(id -g)" -e HOME=/tmp -v "$PWD:/course" -w /course "course-e8e10:241250106" python3 -m unittest discover -s labs/e8e10 -p test_profile.py -v`。
加用例前 `Ran 15 tests ... OK`（`work/unit-tests-before-20261115-190344.log`），加完后 `Ran 17 tests ... OK`（`work/unit-tests-20261115-190353.log`），退出码均 0；两条新用例首次运行即通过。实际值：E8 用例 `key` 不等、`directives` 里 `extra.h` 消失、`reused=[]`、`refreshed=['main.o','helper.o']`、`findings` 与旧值逐字段相同、`added=[]`、`resolved=[]`；E9 用例 `key.flags` `-O0`→`-O1`、`reused=[]`、`refreshed=['main.o','helper.o']`、`findings` 不变、`added=[]`、`resolved=[]`、`-O7` 抛 `ValueError('UNSUPPORTED_FLAGS')`。
