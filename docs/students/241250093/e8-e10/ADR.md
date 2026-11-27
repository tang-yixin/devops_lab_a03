# 决策记录（E10 续写）

编号、日期、作者：ADR-E10-093 / 2026-11-27 / 241250093 李翔宇（E8/E9 原有决策保留，见下方 1–4 条）

背景与约束：在共享 1.7 GiB 内存服务器复现 EChecker 的历史依赖图复用/失效机制；E10 时 main 已扩为
`e7-a-quality-gate` + `e8e10-quality-gate` + `e11e12-integration` 三必需检查；`labs/e8e10/lab.py` 是教师参考实现，
E10 六场景矩阵硬断言「保守刷新两目标」；服务器 11-25 重装过系统，镜像与 GitHub CLI 授权全部需要重建。
组长已占用「链式第 3 头」E10 方向，组员手册分配 093 的方向是「删除一个未被任何源文件包含的头文件」。

## 选择与替代方案（原有 4 条保留)

1. 个人贡献取「只加测试、不改 lab.py」。替代方案：把全目标保守刷新改为仅刷新受影响目标
   （E9/E10 手册进阶项）——会改变 E10 矩阵预期、增加 CI 风险，且与「验证参考实现」目标不符，放弃；
   改以测试刻画复用、失效、消除三类边界。
2. E8 自有方向选择 helper.o 侧直接包含，证明 `scan()` 对每个翻译单元独立求实际图，并补一次「增量 vs 全量三集合一致」。
3. E9 自有方向选择一次性把声明行改为 `main.c config.h`，验证 `resolved` 能同时容纳 MISSING 与 REDUNDANT 两类消除。
4. 测试文件用 SFTP 整文件上传（而非多层 bash→ssh→容器 heredoc 追加），上传前本地 `ast.parse` 预检。

## E10 新增决策（本次）

5. **自主场景选「删除已声明但未被包含的 unused.h」，而不是删 extra.h 或另造孤立头。**
   候选：① 删 `extra.h`（完全未声明、未被 include）——已被 241250106 的 E8 用例占用；
   ② 新建 `orphan.h` 再删除——多一次提交，且无法检验声明图行为；
   ③ 删 `unused.h`——它被 Makefile 声明、从未被任何源文件 include。
   采用 ③。理由：`scan()` 的 key 按文件名收录所有 .c/.h 的预处理指令，删文件必然改 key → 可验证保守刷新；
   同时 `declarations()` 只解析 Makefile 文本、不检查文件是否存在，因此 REDUNDANT(main.o,unused.h) 应保留，
   这比 ① 多覆盖一条「声明引用已删除文件」的边界，且方向不撞车。独立预期写在
   `work/e10-A-manual.mce6fE/selfcase-expected.txt`，先写后跑，5 次结果全部命中。

6. **自主场景结果与统计另存文件，不追加进 30 行主矩阵。**
   候选：把 5 行写进 `matrix/results.csv` 变成 35 行（会破坏步骤 8/9 的 `len(rows)==30` 断言与 gate.rows=30）；
   采用独立 `selfcase-results.csv` / `selfcase-performance.csv` / 5 对 JSON。理由：手册要求
   「六类各 5 次，共 30 行全 equal=True」，自主场景是第七类，单独验收更清楚，且保留原始矩阵可复核。

7. **比值 <1 的性能数据照实保留，不做美化。**
   include / flags / header 三个场景强制刷新两个目标，`full_over_inc` 分别为 0.9628 / 0.9769 / 0.9724，
   自主场景 0.9772。原因：小样例下增量路径同样要跑两次 gcc -MM，还多一次 key 比较，没有加速可讲。
   写成「论文加速倍数」会与 `performance-summary.csv` 的原始值冲突，验收一查就穿帮。

8. **GitHub 授权不复用组长凭据。** 重装后服务器只剩 `devops-auth/241250061` 的 token（账号 tang-yixin），
   而本人历史 PR #17/#23 作者是 `hardtosleep`。按手册先 revoke 旧授权，再用设备码端点重新授权本人账号，
   token 写入 `$GH_CONFIG_DIR/hosts.yml`（600）；`gh auth login --web` 首次请求 device/code 被 GitHub 断连
   （`unexpected EOF`），改用 curl 直接走 OAuth device flow 拿到 user_code，用户浏览器输码后轮询 access_token。
   替代方案「直接复制组长 hosts.yml」被拒：PR 作者会变成组长，且违反「旧授权曾在失陷主机暴露」的处理要求。

## A（缓存何时失效、配置身份如何绑定）

`scan()` 的 key = 所有 .c/.h 中以 # 开头的预处理指令 + Makefile 中以 TAB 开头的配方行 + CFLAGS + `gcc --version` 首行；
声明行**不在** key 内。故 unchanged / body / declaration 复用两目标，include / flags / header / 删除头文件刷新两目标。
声明改变只触发声明图重解析与 findings 重算。

## 代价与覆盖范围

保守刷新会在 helper.o 未受影响时也重新执行 gcc -MM（用保守性换正确性）；本人 E10 用例只覆盖 A 轨道 direct
风格 Makefile 与单文件删除，未覆盖 macro/mixed 变量风格；教学实现用 gcc -MM 而非 strace 采集真实读取。

## 验证命令与实际证据

- `python3 run_lab.py build` → ENV8_EXIT=0，镜像 `course-e8e10:241250093` = `sha256:ad43eccb…`，`lab_ready` 三行正常。
- E10 `work/e10-A-manual.mce6fE`：`steps/` 9 份日志 STEP_EXIT_CODE 全 0；六场景 6 个 `*_FIVE_REPEATS_PASS`、
  `DYNAMIC_CROSSCHECK_AND_MATRIX_PASS`、`MATRIX_PASS`、自主场景 `SELFCASE_…_FIVE_REPEATS_PASS`；
  `final-buildchecker/findings.json` status=SUCCEEDED、trace_id `e6-554e41aa…`、`make-db.txt:1052`。
- 定向测试 `work/unit-tests-e10-20261127-163740.log`：`Ran 23 tests ... OK`，退出码 0（21 → 23）。
- E11-E12 镜像 `python3 run_e11e12.py build` → ENV11_EXIT=0，`sha256:4e5cb7c1…`。
