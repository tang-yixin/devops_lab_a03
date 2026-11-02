# E6 阶段说明（A03 · A 轨道 BuildChecker）

> 任务：论文 1 MVP——自动依赖检测。跟踪构建生成实际依赖图（strace）与声明依赖图
> （Make 数据库），比对得出错误；`--fixed` 修复后复检清零。结论与 E5 一致：
> **MISSING(main.o) = config.h，REDUNDANT(main.o) = unused.h**；修复后 findings=[]。
> 本目录存放 E6 阶段级文档；个人交付物在各 `docs/<学号>/` 目录。

## 1. 完成情况（截至 2026-11-02，四人均交付并合并）

| 学号 | 个人分支 | PR | 测试提交 SHA | 单测（基线→重建） | config.h 读取证据* | 随机临时文件（真实性判据） | 归档（服务器 ~/devops-submissions/） |
|---|---|---|---|---|---|---|---|
| 241250061 | student/241250061/e5-e7 | #11 | e3ba922 | 15 → 16 | t.14:579 | /tmp/cc456HxH.s | buildchecker-E4-E7-20261101-161424.tar.gz |
| 241250093 | student/241250093/e5-e7 | #13 | b28de86 | 16 → 18 | t.14:579 | /tmp/ccxv0LgP.s | buildchecker-E4-E7-20261101-204040.tar.gz |
| 241250106 | student/241250106/e5-e7 | #12 | b5fab6c | 16 → 20 | t.14:579 | /tmp/cc3xJluZ.s | buildchecker-E4-E7-20261101-200049.tar.gz |
| 241250107 | student/241250107/e5-e7 | #14 | b66d20d | 16 → 17 | t.15:579 | /tmp/ccoici21.s | buildchecker-E4-E7-20261102-180927.tar.gz |

\* 行号取自各自 `work/e6-before/evidence/` 的原始 trace。四人四次运行（修复前/后 ×首跑/复跑）
status 均为 SUCCEEDED，findings 精确 2 条 → 0 条，verify 均 passed=true、changed_inputs=["Makefile"]，
input_sha256 仅 Makefile 变化（fd1dcd76…→128069c9…）。

- 新增测试方向各不相同：241250061 一致声明→零发现；241250093 项目根外读取被过滤；
  241250106 失败系统调用（ENOENT/EACCES/ENOSPC）不进依赖图；241250107 .PHONY 展开与
  order-only 分离。全组合并后服务测试共 **23 项**（15 原有 + 8 新增）。
- 241250107 的进程树整体漂移 +1（cc1 为 t.15 而非 t.14），与其 E5 运行行为一致；
  四人随机临时文件名互不相同，真实性判据成立。
- 基线单测 15（组长先交付）与 16（后交付者，main 已含组长测试）并存属正常时间差。

## 2. 交付物与位置

| 交付物 | 位置 | 说明 |
|---|---|---|
| 个人新增测试 | `services/buildchecker/tests/test_e6_<学号>.py` | 文件名含学号，四人零冲突；pytest 自动收集 |
| 个人实验报告 | `docs/<学号>/实验报告.md` E6 节 | 活文档回填：运行表、行号证据、机制四条、测试说明 |
| 个人验收记录 | `docs/<学号>/验收记录.csv` | C03、A01 已 PASS；B01–B03 标 N/A（A 轨道） |
| 原始证据 | 服务器各人克隆 `work/`；组长本地镜像 `work/<学号>/` | build-e6-01/02、e6-before/after(-02)×2，不进 git |
| 归档备份 | 服务器 `~/devops-submissions/<学号>/*.tar.gz` | tar 排除 .git/.env/密钥 |

## 3. 阶段时间线（PR 记录，均合并至 main）

| PR | 内容 | 日期 |
|---|---|---|
| #11 | 组长 E6 交付（测试 test_e6_241250061.py + docs/241250061 E6 节） | 11-01 |
| #12 | 组员 241250106 交付（失败系统调用测试 ×4 用例） | 11-01 开出，11-02 合并 |
| #13 | 组员 241250093 交付（项目根外过滤测试 ×2 用例） | 11-01 开出，11-02 合并 |
| #14 | 组员 241250107 交付（.PHONY/order-only 测试） | 11-02 开出并合并 |
| 收尾提交 | 组长：本文件、根 README 进度行、成员记录统一修正 | 11-02 |

## 4. 关键事件与备注

- **E6 包中文文件名乱码（11-01）**：DevOps_E6_Student_Cloud.zip 为 GBK 文件名，Linux unzip
  直接解压产生 12 个乱码文件、check_package 失败。组长用 Python zipfile 按 GBK 还原文件名
  重新解压后 138 个文件校验全部通过。包已就位于服务器 `/root/devops-materials/`，
  组员无需（也不应）重复解压。
- **GitHub 网络抖动**：E6 期间服务器 push/pull/merge 多次遇 GnuTLS -110、Empty reply、
  443 连接超时（最长挂 130 秒），均在 5 次重试内恢复，未动用本地中转方案。
- **gh 2.4.0 的 pr checks 退出码**：存在 pending 检查时也返回 1，轮询 CI 需按输出文本
  判定（pending→继续等，fail→才失败），不能只看退出码。
- **记录修正（收尾提交）**：241250107 实验报告基线单测 15→16（其分支含组长测试提交，
  证据 work/build-e6-01 实际为 16 passed）、验收记录 C03 证据路径补 `/evidence/`；
  三名组员验收记录 B01–B03 由 PENDING 统一改为 N/A（A 轨道不适用）。
- **doctor 内存门槛**：同 E5，2 GiB 服务器恒报 1 项，按课程口径处理，不影响 build/e6。
- **本地证据镜像**：四人 E6 证据（6 目录 ×4 ≈3.4M）已镜像至组长本地 `work/<学号>/`，
  与 E5 批次共存（work/ 共 4.2M，不进 git），随整项目压缩包提交。

## 5. 仓库结构（E6 完成后）

    devops_lab_a03/
    ├── docs/
    │   ├── e5/ e6/                      阶段说明（本文件为 e6）
    │   └── 241250061/ 241250093/ 241250106/ 241250107/
    │                                    每人：实验报告.md（E5/E6 节已填）/ 验收记录.csv / e5-a.md
    ├── services/buildchecker/tests/     test_cli + test_fullcheck + test_e6_<学号> ×4（共 23 项）
    ├── scripts/ services/ fixtures/ tests/ course-support/ .github/
    │                                    E5—E7 课程工作区（入口 scripts/course.py）
    ├── work/                            个人运行证据（不进 git；服务器在各人克隆内，
    │                                    组长本地 work/<学号>/ 存四人 E5+E6 证据镜像）
    └── e2-a03/ e3-a03/ e4-a03/          E1—E4 历史成果（只读）

## 6. E7 开始前的准备（每人，同步 main 到个人分支）

在自己克隆执行（学号替换为自己的）：

    git switch main && git pull --ff-only origin main
    git switch student/<学号>/e5-e7 && git merge --no-edit main
    git push origin student/<学号>/e5-e7

E7 涉及 GitHub Actions 与分支保护，开始前留意课程包 05_E7验证与CI 的操作手册；
Actions artifact 只保留 14 天，成功/失败 run 完成后及时下载随归档保存。
