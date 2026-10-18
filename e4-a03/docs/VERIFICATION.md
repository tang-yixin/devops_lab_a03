# A03 E4 验证记录

本文件由组长在组员实际运行后填写。成员记录必须对应同一个完整 commit SHA，
失败或重试产生的目录不能冒充最终成功证据。原始证据已从服务器复制到
`e4-a03/evidence/member-<学号>-<日期>/`。

截至 2026-10-18，E4 实验验收与双向互查均通过。阶段状态与尚未执行的 Git
交付操作见 [BACKLOG](BACKLOG.md)；后续文档归档提交不替代下面的统一实测 SHA。

## 统一运行版本

- 分支：`e4`
- 完整 commit SHA：`6abc4d815b4a4baae7cc9d72fc221653a7897e19`
- 云服务器：华为云 ECS，课程配置为 2 CPU、约 2 GiB 内存、80 GiB 磁盘
- 运行入口：仓库的 `e4-a03/` 目录

说明：Ubuntu 的 `MemTotal` 约 1.7 GiB 属于该配置的正常可见值。A03 使用更新后的
`doctor.py` 以 1.5 GiB 作为最低可见内存，不应通过修改运行结果或伪造资源记录绕过检查。

## 个人运行记录

| 学号 | 成功证据目录 | doctor | test | smoke | scan | 对照结论 |
| --- | --- | --- | --- | --- | --- | --- |
| 241250061 | `work/20261017-211203` | 通过 | `3 passed` | `passed=true`、输出 `1` | 未发现问题 | `evidence/member-241250061-20261017/` |
| 241250093 | `work/20261017-231942` | 通过 | `3 passed` | `passed=true`、输出 `1` | 未发现问题 | `evidence/member-241250093-20261017/` |
| 241250106 | `work/20261018-134140` | 通过 | `3 passed` | `passed=true`、输出 `1` | 未发现问题 | `evidence/member-241250106-20261018/` |
| 241250107 | `work/20261017-234531` | 通过 | `3 passed` | `passed=true`、输出 `1` | 未发现问题 | `evidence/member-241250107-20261017/` |

## 验收检查

- [x] 每位成员记录的 `git rev-parse HEAD` 完全一致
- [x] `env.json` 的 `problems` 为空
- [x] `test.log` 显示 3 个测试通过
- [x] `smoke.json` 的 `passed` 为 true，程序输出为 1，并记录打开 `config.h`
- [x] `secret-scan.txt` 显示未发现问题
- [x] 假 Key 能被扫描器检出，清理后扫描重新通过
- [x] 至少两名成员的 `toolchain.lock`、测试结论和冒烟结论完成对照
- [x] A03 按 B03 固定 SHA 完成正向复核并归档原始日志
- [x] B03 按 A03 统一实测 SHA 完成反向复核并回传通过结论
- [x] B03 核验 A03 正向证据；A03 核验反向 manifest 的 10 项哈希及正向 8 项清单，均一致

假 Key 回归证据位于 `evidence/secret-scan-fixture-20261018/`：临时测试值被扫描器
检出，扫描退出码为 `1`；恢复 `.env.example` 后文件差异为空，清理复测退出码为
`0`，并显示“未发现问题”。测试值原文未归档，服务器工作区已恢复干净。

## 成员证据归档

四位成员的证据目录均包含 `env.json`、`build.log`、`image.json`、
`toolchain.lock`、`test.log`、`smoke.json` 和 `secret-scan.txt`。成员使用的
服务器目录分别为：

| 学号 | 服务器项目目录 |
| --- | --- |
| 241250061 | `/root/e4-members/241250061/devops_lab_a03/e4-a03/` |
| 241250093 | `/root/e4-members/241250093/devops_lab_a03/e4-a03/` |
| 241250106 | `/root/e4-members/241250106/devops_lab_a03/e4-a03/` |
| 241250107 | `/root/e4-members/241250107/devops_lab_a03/e4-a03/` |

## 公共检查克隆

组长在服务器公共检查克隆中完成了一次历史基线运行，证据已复制到
`evidence/group-setup-241250061-20261017/`：

- 源码 SHA：`217bcf4a4e0a4456a32ed2231b1c3a227adc4373`
- 证据目录：服务器 `work/20261017-203614/`
- `make doctor`：通过，`problems` 为空
- `make test`：`3 passed`
- `make smoke`：`passed: true`，程序输出 `1`，打开 `config.h`
- `make scan`：未发现问题，包含 Git 历史和镜像检查
- 构建源：Debian 下载入口使用华为云镜像，基础镜像 digest 未改变

## B03 相邻组交叉验证

A03 已在自己的 Linux 云服务器上按 B03 提供的固定版本完成 E4 复核：

- B03 仓库：`https://github.com/Wangyuhan29/b-group-project`
- 固定 SHA：`8701f70d4a3f76592832eedde62b02bb59711ef4`
- 实际结果：环境 `problems=[]`，构建通过，`6 passed`，smoke 为预期的
  `build_exit_code=1` 且包含 `/bin/sh: 1: make: not found`、`passed=true`，密钥扫描未发现问题
- 原始证据：`evidence/b03-cross-validation-8701f70-20261018/`
- 操作和 B03 复核 A03 的步骤：`docs/B03_CROSS_VALIDATION.md`

本次私有仓库使用已核对的 Git bundle 传入服务器，并在服务器按完整 SHA 检出；没有传入密码、Token 或 `.env` 内容。

### B03 对 A03 的反向复核（已完成）

- 固定实测 SHA：`6abc4d815b4a4baae7cc9d72fc221653a7897e19`，与 A03 四人成员记录一致。
- 实际环境：B03 Ubuntu 24.04.4、x86_64、2 CPU、约 1.7 GiB 可见内存、Docker Engine 29.1.3。
- 结果：干净检出，按 README 原样执行 `make all`，总退出码 `0`；doctor `problems=[]`，
  镜像构建通过，`3 passed`，冒烟输出 `1`、正常记录打开 `config.h` 且 `passed=true`，
  仓库、Git 历史及镜像密钥扫描通过。
- B03 服务器原始路径：`/root/241250086/a03-e4-cross-20261018/e4-a03/work/20261018-170959/`。
- B03 报告及证据归档提交：`580f8a904bd24a18f1743320093b46aabb95adf8`。
- A03 本地留存：[反向证据与来源说明](../evidence/b03-reviewed-a03-6abc4d8-20261018/README.md)。

本轮 E4 双向互查已闭环。原始文件按字节保留，不将镜像 ID 当作已发布的 registry digest，
也不将 E4 环境验收写成 E5/E8 算法或 E12 联调已完成。

## 2026-10-18 收尾审计

- 运行相关文件与统一实测 SHA `6abc4d8…` 相比无差异；本轮仅补充文档、证据和归档换行保护规则。
- 四位成员的 `toolchain.lock` 完全一致，与 B03 反向复核归档中的工具链也一致，
  SHA-256 为 `bc70f4e9e436d2567c88588171d7fd4575a614c442874baa089407106bbf9358`。
- 两方向共 18 项清单哈希核验通过；反向 10 份文件同时与 B03 固定提交的 Git blob 逐字节一致。
- 本次修改/新增的 Markdown 链接、JSON、敏感信息模式检查和 Git 差异空白检查通过。
- 本次是本地文档与归档审计，未重新连接服务器或执行容器 `make all`；
  上述构建、单测、冒烟与镜像扫描结论来自已归档的成员运行及 B03 复核，不冒充新的实测。
