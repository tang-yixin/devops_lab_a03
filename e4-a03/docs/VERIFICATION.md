# A03 E4 验证记录

本文件由组长在组员实际运行后填写。成员记录必须对应同一个完整 commit SHA，
失败或重试产生的目录不能冒充最终成功证据。原始证据已从服务器复制到本目录下的
`evidence/member-<学号>-<日期>/`。

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
