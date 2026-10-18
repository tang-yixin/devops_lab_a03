# A03/B03 E4 交叉验证说明

## 目的

本文件记录 A03 对 B03 E4 可重复工程环境的相邻组复核方法，并给出 B03 复核 A03 的入口。范围仅限 E4 的环境、自检、构建、单元测试、冒烟和密钥扫描，不包含 E5 的真实 Checker、四服务联调或算法验收。

## A03 已完成的 B03 复核

- B03 仓库：`https://github.com/Wangyuhan29/b-group-project`
- 固定 SHA：`8701f70d4a3f76592832eedde62b02bb59711ef4`
- A03 验证命令：在 Linux 服务器的干净检出目录执行 `make all`
- 证据入口：`evidence/b03-cross-validation-8701f70-20261018/`
- 服务器原始运行目录：`work/20261018T080204939449Z/`

实际结果为：`doctor` 通过且 `problems=[]`；镜像构建通过；6 项单测通过；smoke 识别 `/bin/sh: 1: make: not found`，`build_exit_code=1` 但 `passed=true`；密钥扫描未发现问题。完整日志和 JSON 见证据目录的 `raw/`。

B03 文档记录的其自身服务器为 Ubuntu 24.04.4；A03 本次实际环境为 Ubuntu 22.04.5。两者均为 x86_64 Linux，系统版本差异已保留在 `env.json`，不影响本次按固定 SHA 的复核结论。

本次 B03 私有仓库不能由服务器匿名 clone，因此使用已核对的 Git bundle 传入服务器，再按完整 SHA 检出。bundle 的 SHA-256 和工作区状态见证据目录的 `metadata.txt`。这不改变源码内容，也没有传入密码、Token 或 `.env`。

## B03 复核 A03 的步骤

A03 组员本轮 E4 实际统一运行的版本是下面的固定 SHA。B03 应使用这个 SHA
进行行为复核，以便与 A03 四位成员的证据保持同一版本口径：

`6abc4d815b4a4baae7cc9d72fc221653a7897e19`

当前 `e4` 分支上的 `b7b92bef8d82e50f7cfe0ee89822c2207cb118b3` 是该版本之后的
文档/证据归档提交，不是本轮成员运行基线；其功能代码未改变。交叉验证应以
`6abc...` 的完整 SHA 为准，不要直接使用未核对的最新分支头。

```sh
git clone --branch e4 --single-branch https://github.com/tang-yixin/devops_lab_a03.git devops_lab_a03
cd devops_lab_a03
git checkout --detach 6abc4d815b4a4baae7cc9d72fc221653a7897e19
git config --local user.name "<本次复核者学号>"
git config --local user.email "<本次复核者学号>@localhost"
cd e4-a03
git rev-parse HEAD
git status --short --branch
make all
```

应核对以下结果：

- `git rev-parse HEAD` 为 `6abc4d815b4a4baae7cc9d72fc221653a7897e19`，工作区无未提交修改；
- `make doctor` 的 `problems` 为空；
- `make test` 为 `3 passed`；
- `smoke.json` 中 `passed=true`、程序输出为 `1`，并记录打开 `config.h`；
- `secret-scan.txt` 显示未发现问题；
- 回传完整 SHA、Linux/Docker 环境、实际 `work/<时间>/` 路径以及异常时的原始日志。

复核证据不应包含服务器密码、真实 Token、`.env` 内容或私钥。`work/` 是运行时目录，若需要提交原始证据，应复制到明确的 `evidence/` 子目录并保留文件名及 SHA。

