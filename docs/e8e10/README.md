# E8—E10 阶段说明（A03 · A 轨道 EChecker）

> 任务：论文2复现。A 组论文 = EChecker（ISSTA 2024，增量构建依赖检查/修复）。
> E8 = 全量基线与历史图复用（真实 BuildChecker 建依赖基线 + 解释 MD/RD + 未变化复用）；
> E9 = 逐提交更新依赖图（C1 复用 / C2 刷新新增 MD / C3 声明修复消除 MD）；
> E10 = 增量/全量一致性与耗时（六场景×5 次矩阵 + 性能计时 + 动态交叉核对，2026-11-20）。
> 本文件为 E8/E9 收尾版（2026-11-15）；E10 完成后更新。
> 教学代码在 `labs/e8e10/`，入口 `run_lab.py`，个人报告在 `docs/students/<学号>/e8-e10/`。

## 1. 完成情况（2026-11-14 至 11-15，四人交付并合并）

| 学号 | 个人分支 | PR（均 MERGED） | E8 OUT | E9 OUT | 自有测试方向（E8 / E9） | 测试数* | 归档（~/devops-submissions/） |
|---|---|---|---|---|---|---|---|
| 241250061 | student/241250061/e8-e10 | #22（4ad24d1，11-14） | e8-A-manual.7JGkNs | e9-A-manual.ENG44c | 声明补齐仍复用+新建头文件间接包含 / 头文件内 include+删冗余声明消 RD（4 用例） | 7→11 | E8-E10-20261114-163149.tar.gz |
| 241250093 | student/241250093/e8-e10 | #23（0c16b78，11-14） | e8-A-manual.9id8kE | e9-A-manual.DNoKlY | helper.c 直接 include→helper.o 新增 MD / Makefile 依赖行改 main.c config.h→findings 清零（2 用例） | 11→13 | E8-E10-20261114-190226.tar.gz |
| 241250107 | student/241250107/e8-e10 | #24（043f5b3）+ 修复 #26（dc93aef）/补 CI #27（fb5c73a），11-15 | e8-A-manual.IVypuc | e9-A-manual.D6pLag | include+声明同步补→added 空 / config.h VALUE 改值→刷新发现不变（2 用例，初版空测试已重写） | 13→15 | E8-E10-20261115-183941.tar.gz |
| 241250106 | student/241250106/e8-e10 | #25（31523e4，11-15） | e8-A-manual.rkuztf | e9-A-manual.S8RK1A | 删未被包含的 extra.h→刷新发现不变 / CFLAGS -O0→-O1→刷新发现不变（2 用例） | 15→17 | E8-E10-20261115-190943.tar.gz |

\* 测试数 = 首次运行项数 → 本人测试并入后项数。基线 7 项（课程包）+ 组长 4 项 + 三人各 2 项，
**四人合并后 main 上教学测试共 17 项**（`python3 -m unittest discover -s labs/e8e10 -p test_profile.py`）。
方向互不重复（8 个测试类，E8/E9 各四类）。

- 各人 E8 均 PASS：BASELINE_PASS（gcc -MM 独立预期：main.o 缺 config.h 声明=MD、多
  unused.h=RD）+ BUILDCHECKER_BASELINE_PASS（真实 strace 全量检测投影到对象目标，
  trace/t.14 读 config.h、make-db.txt:1044 声明行）+ REUSE_PASS（未变化输入两目标复用）。
- 各人 E9 均 PASS：C0→C1（函数体变化，两目标复用）→C2（加 include extra.h，两目标刷新+
  新增 MD extra.h）→C3（Makefile 补声明，两 MD 消除、RD unused.h 保留），四份 JSON 与内部
  git log --reverse 逐提交一致。
- 各人 CI：PR run 双门禁（e7-a-quality-gate + e8e10-quality-gate）均 success 后**自行合并**
  （六条自检标准见组员手册 §9），artifact 在 14 天保留期内下载至各自 `work/ci-e8e10/<run_id>/`。

## 2. 组级前置（组长执行，每组一次，2026-11-14）

| 阶段 | 运行 / PR | head SHA | 结论 |
|---|---|---|---|
| E8-E10 包上传 | GBK 解压（Python zipfile，E6/E7 同款坑） | — | 316 文件中文名正常 |
| 教学包导入 | [PR #21](https://github.com/tang-yixin/devops_lab_a03/pull/21)（teaching/e8-e10） | eceec5c | 双门禁 success → MERGED（1a0e18c） |
| 必需检查扩充 | PUT branches/main/protection | 1a0e18c | contexts=[e7-a-quality-gate, e8e10-quality-gate]，strict/enforce_admins/审批 0 保留 |

## 3. 交付物与位置

| 交付物 | 位置 | 说明 |
|---|---|---|
| 教学代码 | `labs/e8e10/`（lab.py、test_profile.py、environment/）+ `run_lab.py` | main 参考实现，未改；个人只加测试 |
| 自有测试 | `labs/e8e10/test_profile.py` 内 `StudentE8A<E9A><学号>` ×8 类 | main 共 17 项，方向互不重复 |
| 个人报告 | `docs/students/<学号>/e8-e10/`（个人报告 / ADR / AI_USAGE 三份） | 三份必交，AI_USAGE 未用也写"未调用" |
| 原始证据 | 服务器各人克隆 `work/`（e8-A-manual.* / e9-A-manual.* / unit-tests-*.log / ci-e8e10/ / environment-build-*.log） | 组长本机 `work/<学号>/` 存四人镜像，不进 git |
| 归档备份 | 服务器 `~/devops-submissions/<学号>/E8-E10-*.tar.gz` ×4 | 组长本机 D:\DevOps\E8-E9\submissions\ 另存 |

## 4. 关键事件与备注

- **镜像与环境**：E8-E10 使用新镜像 `course-e8e10:<学号>`（含 gcc 14.2.0 / make 4.4.1 /
  strace），不能复用 E4—E7 的 course1027 镜像；`lab_python` 在 `--network none + SYS_PTRACE`
  下运行。2GiB 内存下多人同时 build 会挤兑，组员自行错峰（`docker ps` 观察）。
- **GBK 文件名乱码（11-14）**：E8-E10 包 unzip 后中文目录名乱码，沿用 E6/E7 方法用
  Python zipfile 按 GBK 还原，316 文件正常。
- **gh 2.4.0 老版本**：`run list --json` 用 `name` 非 `workflowName`；`pr checks` 退出码
  不可信，权威判定用 run 的 `conclusion` 与 `gh pr view --json mergeStateStatus`。
- **107 空测试发现与修复（11-15）**：组长收尾检查发现 107 的 E8/E9 两个测试初版为"空测试"
  （写死字典、不调用 scan，永远通过），实验主线真实合格但自主任务不达标；出具修复指引
  （项目外 `D:\DevOps\E8-E9\E8-E9_241250107测试修复指引_20261115.md`，断言值由组长在容器
  实测）后，107 本人于当日重写为真实 fixture+scan 场景：解决与 main 的合并冲突后 17/17 OK，
  经 [PR #26](https://github.com/tang-yixin/devops_lab_a03/pull/26)（head=d51dbcc，CI 43723101314
  success）合并，[PR #27](https://github.com/tang-yixin/devops_lab_a03/pull/27) 补报告 CI 信息。
  修复后 main 上测试仍为 17 项；artifact 43723101314 由组长核实补下载至其
  `work/ci-e8e10/43723101314/`（本人报告所记路径初始缺失）。
