# E5 阶段说明（A03 · A 轨道 BuildChecker）

> 任务：从原始构建记录（strace 全进程 trace + Make 数据库）人工推导 Makefile 依赖声明错误，
> 样例 `fixtures/md-rd/`。结论：**MD(main.o) = config.h，RD(main.o) = unused.h**；`app` 无差异。
> 本目录存放 E5 阶段级文档；个人交付物在各 `docs/<学号>/` 目录。

## 1. 完成情况（截至 2026-10-31，四人均交付并合并）

| 学号 | 个人分支 | PR | 采集源码 SHA | config.h 读取证据* | 随机临时文件（真实性判据） | 归档（服务器 ~/devops-submissions/） |
|---|---|---|---|---|---|---|
| 241250061 | student/241250061/e5-e7 | #5 | 6a8e730 | t.16:580 | /tmp/ccg7ypwf.s | buildchecker-E4-E7-20261030-193832.tar.gz |
| 241250093 | student/241250093/e5-e7 | #8 | 502b927 | t.16:580 | /tmp/ccuHGBbW.s | buildchecker-E4-E7-20261031-004645.tar.gz |
| 241250106 | student/241250106/e5-e7 | #9 | e15750b | t.16:580 | /tmp/ccRAuHNM.s | buildchecker-E4-E7-20261031-143838.tar.gz |
| 241250107 | student/241250107/e5-e7 | #10 | d93fb94 | t.17:580 | /tmp/ccqYkHpy.s | buildchecker-E4-E7-20261031-160830.tar.gz |

\* 行号取自各自 `work/e5-01/evidence/` 的原始 trace，组长已在服务器上逐人抽查核对。
四人的 build（15 项单测）与 e5 采集退出码均为 0，程序输出均为 `1`，make-db 声明行均为
`make-db.txt:1061 → main.o: main.c unused.h`。

说明：不同运行的 PID 编号可能整体漂移（241250107 的进程树为 t.15—t.21，其余三人为
t.14—t.20），同一进程文件内的行号稳定。因此真实性判据取编译器随机临时文件名
（`/tmp/ccXXXXXX.s`，每次运行必不相同），四人各不相同。

## 2. 交付物与位置

| 交付物 | 位置 | 说明 |
|---|---|---|
| 个人结论文档 | `docs/<学号>/e5-a.md` | 进程树、行号证据、归属推理、MD/RD 表、与论文差异 |
| 个人实验报告 | `docs/<学号>/实验报告.md` | 模板为 E5—E7 活文档：E5 节已填，E6/E7 阶段回来补写 |
| 个人验收记录 | `docs/<学号>/验收记录.csv` | C01/C02 已 PASS；其余 PENDING 待 E6/E7 |
| 原始证据 | 服务器各人克隆 `work/e5-01/`（不进 git） | trace/、make-db.txt、program-output.txt、runner/ 等 |
| 归档备份 | 服务器 `~/devops-submissions/<学号>/*.tar.gz` | tar 排除 .git/.env/密钥；各人可另存本地 |

## 3. 阶段时间线（PR 记录，均合并至 main）

| PR | 内容 | 日期 |
|---|---|---|
| #4 | 组长导入 E5—E7 课程参考实现（import_template --stage E5E7 --track A --upgrade） | 10-30 |
| #5 | 组长 E5 交付（docs/241250061） | 10-30 |
| #6 | 个人文档按学号目录归位（避免组员同名文件合并冲突） | 10-30 |
| #7 | CI 修复：海外 Runner 改走 docker.io 官方源（见下文 daocloud 事件） | 10-30 |
| #8 / #9 / #10 | 三名组员 E5 交付（每人各自采集、各自行号） | 10-31 |

## 4. 关键事件与备注

- **GitHub 访问抖动**：服务器到 github.com 偶发 GnuTLS 超时。处理口径：原命令重试
  （多数 5 次内可过）；仍失败时经组长本地电脑中转推送（本地 `git fetch ssh://服务器路径
  <分支>` 后 `git push origin`）。
- **daocloud CI 事件（10-30）**：E7 门禁 workflow 在 GitHub 海外 Runner 上因 `m.daocloud.io`
  返回损坏元数据而失败（run 41059691591，两次 attempt 均停在基础镜像元数据拉取，与代码无关；
  服务器在国内访问 daocloud 正常）。修复：workflow 构建命令加
  `--build-arg BASE_IMAGE=docker.io/...`，digest 与 Dockerfile 默认值一致（PR #7）。
  修复后 CI 全绿。
- **doctor 内存门槛**：课程配置服务器 2 GiB（可见 1.7 GiB）低于 E5—E7 doctor 的 4 GiB 门槛，
  各人自检 problems 恒报 1 项；已按课程口径报助教统一处理，不影响 build/e5 运行与退出码。
- **个人实验记录表**：课程包另有"个人实验记录模板"（06_提交与排错），其 E5 字段与各人
  实验报告.md 的 E5 节一致，验收需要时可按报告内容补填。

## 5. 仓库结构（E5 完成后）

    devops_lab_a03/
    ├── docs/
    │   ├── e5/                          本文件：E5 阶段说明
    │   └── 241250061/ 241250093/ 241250106/ 241250107/
    │                                    每人三件套：e5-a.md / 实验报告.md / 验收记录.csv
    ├── scripts/ services/ fixtures/ tests/ course-support/ .github/
    │                                    E5—E7 课程工作区（入口 scripts/course.py）
    ├── work/                            个人运行证据（不进 git，在各人服务器克隆内）
    └── e2-a03/ e3-a03/ e4-a03/          E1—E4 历史成果（只读）

## 6. E6 开始前的准备（每人，同步 main 到个人分支）

在自己克隆执行（学号替换为自己的）：

    git switch main && git pull --ff-only origin main
    git switch student/<学号>/e5-e7 && git merge --no-edit main
    git push origin student/<学号>/e5-e7

往个人分支合并 main 不需要 PR、不影响 main；只有并入 main 才走 PR。
