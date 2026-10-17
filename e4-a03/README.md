# A03 BuildChecker 可重复工程环境（E4）

本目录基于课程 E4 A 组模板，用于在 A03 的共享云服务器上建立可重复的
BuildChecker 工程环境。E4 只验证环境、构建、测试、冒烟与密钥检查链路；
E5 起再在 `services/buildchecker/` 中实现论文方法。

所有命令都应在仓库的 `e4-a03/` 目录执行。组员测试时必须使用同一个完整
commit SHA；`work/` 是个人运行证据，默认不提交。

## 服务器资源口径

A03 按课程当前配置使用 2U、2 GiB 内存、2 CPU、80 GiB 磁盘的云服务器。
Ubuntu 会为系统保留一部分内存，因此 `free -h` 中的 `MemTotal` 可能显示约
1.7 GiB。`scripts/doctor.py` 已按这一课程配置将最低可见内存设为 1.5 GiB；
2 CPU 和 40 GiB 可用磁盘仍是最低要求。4 CPU、8 GiB 内存和 100 GiB 可用磁盘
是后续真实项目运行的建议值，低于建议值只产生 warning。

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
mkdir -p ~/<学号> && cd ~/<学号>
git clone --branch e4 --single-branch https://github.com/tang-yixin/devops_lab_a03.git
cd devops_lab_a03/e4-a03
git config --local user.name  "<学号>"
git config --local user.email "<学号>@localhost"
git remote -v
git rev-parse HEAD
git status --short
make doctor
make all
```

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
`work/<时间>/` 路径、`make all` 结论，以及与另一名组员的对照结论。不要提交
`.env`，也不要把服务器密码或真实 Token 写入日志。

小组汇总记录见 `docs/VERIFICATION.md` 和 `docs/CONTRIBUTIONS.md`。

## 约定

- 基础镜像按 digest 固定，升级时只改 `services/buildchecker/Dockerfile` 的 `ARG BASE_IMAGE` 一行，并在提交说明中写明新 digest。
- 新增 Python 依赖：写进 `requirements-dev.in`，执行 `make lock`，两个文件一起提交。
- 密钥只放在 `.env`（权限 600），不提交、不进镜像、不打印到日志。
- E4 每名组员各自在学号目录运行一次 `make all`，记录成功的 `work/<时间>/` 和所测源码 SHA，再与另一名组员对照。`work/` 默认不提交；E4 不要求个人创建分支、提交或合并。后续课程若要求提交原始证据，另按当时要求处理。
