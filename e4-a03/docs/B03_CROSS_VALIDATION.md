# A03/B03 E4 交叉验证说明

## 目的

本文件记录 A03/B03 的 E4 双向互查结果，并保留按固定版本重跑的入口。范围仅限 E4 的环境、自检、构建、单元测试、冒烟和密钥扫描，不包含 E5 的真实 Checker、四服务联调或算法验收。

## 闭环状态（2026-10-18）

两方向实测均通过，B03 已回传反向复核结果，并核验 A03 提供的 B03 复核证据及
SHA-256 清单。本轮 E4 双向互查已闭环，不再将“等待 B03 反向复核”列为待办。

| 方向 | 固定实测 SHA | 执行环境 | 结论与 A03 归档 |
| --- | --- | --- | --- |
| A03 → B03 | `8701f70d4a3f76592832eedde62b02bb59711ef4` | A03 Ubuntu 22.04.5，x86_64，2 CPU，约 1.7 GiB 可见内存 | 通过；[正向证据](../evidence/b03-cross-validation-8701f70-20261018/README.md) |
| B03 → A03 | `6abc4d815b4a4baae7cc9d72fc221653a7897e19` | B03 Ubuntu 24.04.4，x86_64，2 CPU，约 1.7 GiB 可见内存 | 通过；[反向回执](../evidence/b03-reviewed-a03-6abc4d8-20261018/README.md) |

B03 报告与反向证据的固定归档提交为
`580f8a904bd24a18f1743320093b46aabb95adf8`，原文见
[B03 双向互查报告](https://github.com/Wangyuhan29/b-group-project/blob/580f8a904bd24a18f1743320093b46aabb95adf8/docs/e4/A03_CROSS_VALIDATION_20261018.md)。
该归档提交不是 B03 的实测源码版本，不能替换上表中的 `8701f70…`。

## A03 已完成的 B03 复核

- B03 仓库：`https://github.com/Wangyuhan29/b-group-project`
- 固定 SHA：`8701f70d4a3f76592832eedde62b02bb59711ef4`
- A03 验证命令：在 Linux 服务器的干净检出目录执行 `make all`
- 证据入口：`evidence/b03-cross-validation-8701f70-20261018/`
- 服务器原始运行目录：`work/20261018T080204939449Z/`

实际结果为：`doctor` 通过且 `problems=[]`；镜像构建通过；6 项单测通过；smoke 识别 `/bin/sh: 1: make: not found`，`build_exit_code=1` 但 `passed=true`；密钥扫描未发现问题。完整日志和 JSON 见证据目录的 `raw/`。

B03 文档记录的其自身服务器为 Ubuntu 24.04.4；A03 本次实际环境为 Ubuntu 22.04.5。两者均为 x86_64 Linux，系统版本差异已保留在 `env.json`，不影响本次按固定 SHA 的复核结论。

本次 B03 私有仓库不能由服务器匿名 clone，因此使用已核对的 Git bundle 传入服务器，再按完整 SHA 检出。bundle 的 SHA-256 和工作区状态见证据目录的 `metadata.txt`。这不改变源码内容，也没有传入密码、Token 或 `.env`。

## B03 已完成的 A03 复核

B03 在学号 `241250086` 的独立克隆中按 README 原样运行 `make all`，报告明确
为 AI 辅助执行，源码与配置未修改，运行前后工作区干净。

- 实际工作目录：`/root/241250086/a03-e4-cross-20261018/e4-a03/`。
- 成功证据目录：上述目录下的 `work/20261018-170959/`。
- 实测 SHA：`6abc4d815b4a4baae7cc9d72fc221653a7897e19`。
- 环境：Ubuntu 24.04.4、x86_64、2 CPU、约 1.7 GiB 可见内存、Docker Engine 29.1.3。
- 结果：`make all` 总退出码 `0`；doctor `problems=[]`；镜像构建成功；
  `3 passed`；冒烟 `make_exit_code=0`、`app_output=1`、`passed=true`，
  strace 正常记录打开 `config.h`；仓库、Git 历史及镜像密钥扫描通过。
- 构建日志保留了 pip 网络超时及原命令自动重试成功的过程，未删去异常记录。

A03 已从 B03 固定归档提交取回 `manifest.json`、`receipt.json`、元数据、
`make-all.log` 和七份运行文件，逐项核对 manifest 中的 10 个文件哈希，全部一致。
同时重新核对 A03 → B03 的 8 项 SHA-256 清单，全部一致。
这是收到回执后的静态证据核验，不冒充 A03 在 B03 服务器上再次执行。
原始传输压缩包未纳入仓库，其哈希仅保留为 B03 的传输记录。

## B03 复核 A03 的重跑步骤（已验收，留作复现入口）

A03 组员本轮 E4 实际统一运行的版本是下面的固定 SHA。B03 应使用这个 SHA
进行行为复核，以便与 A03 四位成员的证据保持同一版本口径：

`6abc4d815b4a4baae7cc9d72fc221653a7897e19`

历史提交 `b7b92bef8d82e50f7cfe0ee89822c2207cb118b3` 和
`e6bdfe76ec26a1b1bbbc83804bfd629104d51ade` 是该版本之后的文档/证据归档提交，
不是本轮成员运行基线；功能代码未改变。后续收尾提交同理。
交叉验证应以 `6abc...` 的完整 SHA 为准，不要直接使用未核对的最新分支头。

以下命令仅用于新的独立克隆，不在存在未提交修改的开发目录中执行版本切换：

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

