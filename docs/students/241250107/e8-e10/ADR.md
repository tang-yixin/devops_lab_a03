# 决策记录

背景与约束：
在 E8/E9 实验中，我们需要为依赖图机制增加测试。A 轨道的核心任务是验证历史图的建立、未变化时的复用（E8），以及逐提交更新时的刷新、新增与消除逻辑（E9）。约束条件是必须使用分配到的测试方向（学号 241250107 分配为：同时添加 include 和声明、配置内容改变），且实验仅针对单 Make 进程和单输出目标进行教学简化验证，不涉及外部真实网络。

选择与替代方案：
A轨道关注点：
1. 缓存何时失效：当输入（源码、Makefile）的指纹发生变化时（如 E9 的 C2 增加了 include，或 C3 修改了 Makefile），缓存失效并触发刷新（refreshed）；当输入不变时（E8 的未变化扫描，或 E9 的 C1 仅修改函数体），缓存复用（reused）。
2. 配置身份如何绑定：扫描结果与实际配置（CFLAGS、编译选项等）绑定，配置发生变化必然导致指纹变化，从而触发相关目标刷新。

选择方案：
- E8 方向：构造“main.c 加 include "extra.h" 且 Makefile 同时补 extra.h 声明”的测试。
- E9 方向：构造“config.h 的 VALUE 值从 1 改为 2”的测试。

替代方案：
未选择“删除头文件”或“改变 CFLAGS”作为测试方向，因为这会导致依赖图发生更复杂的结构性变化，难以隔离验证“同时添加”和“配置改变”这两种特定场景。

代价与覆盖范围：
代价：由于是教学简化的单进程、单输出构建场景，无法覆盖大型项目中的并发构建、多输出目标以及系统级头文件变化带来的影响。
覆盖范围：验证了项目内部本地依赖（config.h, extra.h, unused.h）在“同时添加声明与引用”、“纯内容变化”边界情况下的增量逻辑。

验证命令与实际证据：
验证命令：
在终端执行 docker run 测试命令（见下方完整命令），或直接运行单元测试验证逻辑：
docker run --rm --network none --user "$(id -u):$(id -g)" -e HOME=/tmp -v "$PWD:/course" -w /course "course-e8e10:241250107" python3 -m unittest discover -s labs/e8e10 -p test_profile.py -v

实际证据：
- E8 证据：`work/e8-A-manual.IVypuc/baseline.json`、`incremental.json` 显示 `reused=['main.o', 'helper.o']`，`refreshed=[]`。
- E9 证据：`work/e9-A-manual.D6pLag/` 目录下的 `C1.json`（复用）、`C2.json`（刷新+新增MD）、`C3.json`（MD消除，RD保留）。
- 测试运行结果：`Ran 15 tests in 0.469s OK`，退出码 `TEST_EXIT_CODE=0`。
