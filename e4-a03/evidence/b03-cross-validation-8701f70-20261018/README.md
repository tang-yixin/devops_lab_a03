# B03 E4 交叉验证证据

## 来源与范围

- B03 仓库：`https://github.com/Wangyuhan29/b-group-project`
- 固定实测 SHA：`8701f70d4a3f76592832eedde62b02bb59711ef4`
- 验证服务器：A03 共享 Linux 云服务器，Ubuntu 22.04.5 LTS，x86_64
- 执行命令：在该 SHA 的干净检出目录执行 `make all`
- 服务器运行目录：`/root/a03-cross-validation/b03-e4-8701f70-20261018/repo/work/20261018T080204939449Z`

服务器无法匿名访问 B03 私有 GitHub 仓库，因此本次使用从已核对的本地 B03 仓库生成的 Git bundle 传入服务器，并在服务器检出固定 SHA。`metadata.txt` 保存了检出 SHA、工作区状态、服务器内核和 bundle SHA-256；未传入密码、Token 或 `.env` 内容。

## 结果

| 检查项 | 实际结果 |
| --- | --- |
| 环境自检 | 通过，`problems=[]`；2 CPU、约 1.7 GiB 内存、约 69.2 GiB 可用磁盘 |
| 构建 | 通过；镜像 `e4-draft:241250061`，架构 `amd64` |
| 单测 | `6 passed in 0.02s` |
| 冒烟 | `build_exit_code=1`，错误含 `/bin/sh: 1: make: not found`，`make_not_found=true`，`passed=true` |
| 密钥扫描 | 未发现问题，包含工作区、Git 历史和镜像 |

冒烟中的构建失败是 B03 README 规定的 E4 预期行为，表示样例容器按设计缺少 `make`，不是 `make all` 失败。

B03 文档记录的其自身服务器为 Ubuntu 24.04.4；本次 A03 复核使用 Ubuntu 22.04.5。两者均为 x86_64 Linux，本次结果用于证明该固定版本在 A03 的实际服务器上可复现，不把两个服务器的系统版本当作完全相同。

## 原始文件

原始文件位于 `raw/20261018T080204939449Z/`：

- `env.json`
- `build.log`
- `image.json`
- `toolchain.lock`
- `test.log`
- `smoke.json`
- `secret-scan.txt`

这些文件是服务器下载后的原始证据副本，不应手工改写。查看结论时以本索引和原始 JSON/日志共同为准。

文件完整性校验列在 `SHA256SUMS.txt`，校验根目录下的 `metadata.txt` 和 `raw/` 中的全部原始文件。
