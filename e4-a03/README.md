# A03 BuildChecker 可重复工程环境（E4）

本目录基于课程 E4 A 组模板，用于在 A03 的共享云服务器上建立可重复的
BuildChecker 工程环境。E4 只验证环境、构建、测试、冒烟与密钥检查链路；
E5 起再在 `services/buildchecker/` 中实现论文方法。

所有命令都应在仓库的 `e4-a03/` 目录执行。组员测试时必须使用同一个完整
commit SHA；`work/` 是个人运行证据，默认不提交。

## 验收状态（2026-10-18）

E4 实验验收已完成：四名组员同版本 `make all`、工具链/结果对照、假 Key
检出与清理复测，以及与 B03 的双向互查均通过。最终文档提交和合并 `main`
属于仓库收尾操作，其状态单独记录在 [BACKLOG](docs/BACKLOG.md)，不提前记为已完成。

固定实测版本为 `6abc4d815b4a4baae7cc9d72fc221653a7897e19`。
B03 已在该版本上完成反向复核；后续文档和证据归档提交不替代该 SHA，
也不表示成员需要在每次文档提交后重跑。若修改 Dockerfile、依赖锁、脚本、
Compose、服务代码或样例，则应建立新的实测版本并重新验证。

## 目录结构

```text
e4-a03/
├── README.md                         E4 入口、命令、环境口径和目录说明
├── Makefile                          doctor/build/test/smoke/scan/all
├── compose.yaml                      BuildChecker 服务运行配置
├── services/buildchecker/             服务 Dockerfile、CLI 和 3 项单元测试
├── fixtures/md-rd/                   固定的 MD/RD 冒烟样例
├── scripts/                           doctor.py、secret_scan.py
├── requirements-dev.in                直接开发依赖
├── requirements-dev.lock              带哈希的依赖锁
├── .env.example                       不含真实密钥的运行配置模板
├── docs/                              BACKLOG、验证、贡献与双向互查记录
├── evidence/                          成员、假 Key 与双向互查原始证据
└── work/                              本地运行时证据，默认不提交
```

文档与证据入口：

- [BACKLOG](docs/BACKLOG.md)：阶段任务、完成状态、提交与合并清单。
- [验证记录](docs/VERIFICATION.md)、[贡献记录](docs/CONTRIBUTIONS.md)。
- [双向互查记录与重跑步骤](docs/B03_CROSS_VALIDATION.md)。
- [证据总索引](evidence/README.md)：四位成员、假 Key 回归、A03 → B03 和 B03 → A03。
- [A03 → B03 原始证据](evidence/b03-cross-validation-8701f70-20261018/README.md)。
- [B03 → A03 回执与原始证据](evidence/b03-reviewed-a03-6abc4d8-20261018/README.md)。

## 服务器资源口径

A03 按课程当前配置使用 2U、2 GiB 内存、2 CPU、80 GiB 磁盘的云服务器。
Ubuntu 会为系统保留一部分内存，因此 `free -h` 中的 `MemTotal` 可能显示约
1.7 GiB。`scripts/doctor.py` 已按这一课程配置将最低可见内存设为 1.5 GiB；
2 CPU 和 40 GiB 可用磁盘仍是最低要求。4 CPU、8 GiB 内存和 100 GiB 可用磁盘
是后续真实项目运行的建议值，低于建议值只产生 warning。

Dockerfile 会在构建时把 Debian 官方源替换为华为云 Debian 镜像，基础镜像
digest、Debian suite 和 Python 依赖锁文件不变。若镜像站临时不可用，应保留
完整 `build.log`，不要改动 digest 或删除锁文件来绕过构建。

## 服务器首次检查（组长）

组长可额外建立一个公共检查克隆，确认远程 `e4` 分支中的模板能够运行。这个
克隆只用于检查，不替代组长自己的个人运行：

```sh
mkdir -p ~/e4-group-setup
cd ~/e4-group-setup
git clone --branch e4 --single-branch https://github.com/tang-yixin/devops_lab_a03.git
cd devops_lab_a03/e4-a03
git remote -v
git rev-parse HEAD
git status --short
```

如果仓库文件完整，再设置该检查克隆的本地身份并运行 `make doctor`。环境确认后，
组长和每位组员仍按下一节在自己的学号目录重新克隆并运行。

## 每名组员第一次使用

```sh
mkdir -p ~/e4-members/<学号>
cd ~/e4-members/<学号>
git clone --branch e4 --single-branch https://github.com/tang-yixin/devops_lab_a03.git devops_lab_a03
cd devops_lab_a03
git switch e4
git checkout --detach 6abc4d815b4a4baae7cc9d72fc221653a7897e19
cd e4-a03
git config --local user.name  "<学号>"
git config --local user.email "<学号>@localhost"
git remote -v
git rev-parse HEAD
git status --short --branch
make doctor
make all
```

上面是本轮固定版本的重跑方式，应在新的独立克隆中执行；不要在含未提交修改的
开发目录切换版本。固定版本下看到 detached HEAD 是正常的。

`git remote -v` 应指向 A03 的真正远程仓库。服务器账号由组内共享，因此禁止
设置全局 Git 身份。每个人拥有独立克隆后，本地 Git 身份会被 `make doctor` 记录，
Makefile 还会用 `user.name` 生成带学号的镜像名和 Compose 项目名，避免组员互相
覆盖。运行 `make all` 本身不会创建提交，也不会自动上传证据。

## 命令

| 命令 | 作用 | 证据（work/<时间>/） |
| --- | --- | --- |
| `make doctor` | 服务器与 Git 身份自检 | env.json |
| `make build` | 构建服务镜像 | build.log、image.json、toolchain.lock |
| `make test` | 容器内运行单元测试 | test.log |
| `make smoke` | 用 E3 样例做冒烟测试 | smoke.json |
| `make scan` | 密钥检查（工作区、Git 历史、镜像） | secret-scan.txt |
| `make all` | 以上五步 | 同一个证据目录 |
| `make shell` | 进入服务容器；仓库的 `work/` 挂到容器的 `/app/work`，在那里保存的文件退出后仍保留 | — |
| `make lock` | 修改 requirements-dev.in 后重新生成锁文件 | requirements-dev.lock |

预期：`make test` 全部通过；`make smoke` 输出 `"passed": true`，strace 记录中能看到 `config.h` 被打开，`app_output` 为 `1`；`make scan` 显示"未发现问题"。

成功后记录以下信息交给组长：学号、`git rev-parse HEAD` 的完整输出、成功的
`work/<时间>/` 路径、`make all` 结论，以及与另一名组员的对照结论。组长统一归档
服务器上的 `work/<时间>/`，成员不需要压缩或上传证据。不要提交
`.env`，也不要把服务器密码或真实 Token 写入日志。

小组汇总记录见 `docs/VERIFICATION.md` 和 `docs/CONTRIBUTIONS.md`。四位成员的本地
运行证据索引见 `evidence/README.md`；这些证据均对应本轮统一 SHA，压缩包不纳入仓库。
假 Key 检出与清理复测记录见 `evidence/secret-scan-fixture-20261018/`。

## 约定

- 基础镜像按 digest 固定，升级时只改 `services/buildchecker/Dockerfile` 的 `ARG BASE_IMAGE` 一行，并在提交说明中写明新 digest。
- 新增 Python 依赖：写进 `requirements-dev.in`，执行 `make lock`，两个文件一起提交。
- 密钥只放在 `.env`（权限 600），不提交、不进镜像、不打印到日志。
- E4 每名组员各自在学号目录运行一次 `make all`，记录成功的 `work/<时间>/` 和所测源码 SHA，再与另一名组员对照。`work/` 默认不提交；E4 不要求个人创建分支、提交或合并。后续课程若要求提交原始证据，另按当时要求处理。
