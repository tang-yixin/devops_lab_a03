# 决策记录

背景与约束：在共享 2GiB 内存服务器复现 EChecker 的历史依赖图复用/失效机制；main 受
`e7-a-quality-gate` + `e8e10-quality-gate` 双必需检查与 strict/enforce_admins 保护；
`labs/e8e10/lab.py` 为教师参考实现，E10 六场景矩阵硬断言「保守刷新两目标」；
组长已占用 4 个测试方向（声明补齐复用、新建头文件间接包含、头文件内加 include、删冗余声明消 RD），
本人方向由组员手册 §6 分配为：E8「helper.c 直接 include extra.h → helper.o 新增 MISSING extra.h」、
E9「Makefile 依赖行改为 main.c config.h → 两项发现全消、resolved 两条」。

选择与替代方案：
1. 个人贡献取「只加测试、不改 lab.py」。替代方案：把全目标保守刷新改为仅刷新受影响目标
   （E9/E10 手册进阶项）——会改变 E10 矩阵预期、增加 CI 风险，且与本次「验证参考实现」的目标不符，放弃；
   改以测试刻画复用、失效、消除三类边界。
2. E8 自有方向选择 helper.o 侧的直接包含，而非 main.o 侧：组长与另两位同学的场景集中在
   main.c/config.h 与声明行，选 helper.c 可证明 `scan()` 对**每个**翻译单元独立求实际图，
   而非只对有已知 MD 的目标生效；同时用「增量 vs 全量三集合一致」补一次全量核对。
3. E9 自有方向选择一次性把声明行改为 `main.c config.h`（补 config.h 且删 unused.h），
   与组长「只删冗余声明、MD 仍在」形成互补：验证 `resolved` 能同时容纳 MISSING 与 REDUNDANT 两类消除，
   且声明行不参与 key 时真实图仍复用。
4. 测试文件通过 SFTP 整文件上传（而非多层 bash→ssh→容器 heredoc 追加），避免反斜杠/换行转义歧义；
   字符串中的换行用常规 `\n` 字面量，上传后以本地 `ast.parse` 做语法预检再运行。

A（缓存何时失效、配置身份如何绑定）：`scan()` 的 key = 所有 .c/.h 中以 # 开头的预处理指令 +
Makefile 中以 TAB 开头的配方行 + CFLAGS + `gcc --version` 首行；声明行**不在** key 内。
因此 C1（函数体）、C3（声明行）指纹不变 → 两目标复用；C2（新增 include）与本人 E8 场景
（helper.c 新增 include）改变 directives → 保守刷新两目标。声明改变只触发声明图重解析与 findings 重算。

代价与覆盖范围：保守刷新会在 helper.o 未受影响时也重新执行 gcc -MM（用保守性换正确性）；
本人两个用例只覆盖 A 轨道 direct 风格的 Makefile，未覆盖 macro/mixed 变量风格与 E10 性能矩阵；
教学实现用 gcc -MM 而非 strace 采集真实读取，故「实际图」是编译期依赖投影。

验证命令与实际证据：
- `python3 -m unittest discover -s labs/e8e10 -p test_profile.py -v`（容器内）
  → `work/unit-tests-20261114-184641.log`：`Ran 13 tests ... OK`，退出码 0。
- E8 `work/e8-A-manual.9id8kE`：BASELINE_PASS / BUILDCHECKER_BASELINE_PASS / REUSE_PASS；
  findings.json status=SUCCEEDED、trace/t.14:579、make-db.txt:1044；内层 git 干净。
- E9 `work/e9-A-manual.DNoKlY`：C0_BUILD_AND_BASELINE_PASS / C1_REUSE_PASS /
  C2_REFRESH_PASS / C3_RESOLVED_PASS；`git -C project log --oneline --reverse` 与四份 JSON 的 commit 一致。
- 环境：`python3 run_lab.py build` → ENV_BUILD_EXIT=0，镜像 `course-e8e10:241250093`
  = sha256:7791e4343736f3e3d7c9f7b0b458b8f025f95cbda8e9b706338f9c553bbea491，gcc 14.2.0。
