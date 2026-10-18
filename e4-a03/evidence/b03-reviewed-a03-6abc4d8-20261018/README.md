# B03 对 A03 的 E4 反向复核证据

## 来源与固定版本

- 被测仓库：`https://github.com/tang-yixin/devops_lab_a03.git`。
- 固定实测 SHA：`6abc4d815b4a4baae7cc9d72fc221653a7897e19`。
- 执行方：B03，学号身份 `241250086`，AI 辅助执行；不是 A03 在对方服务器代跑。
- B03 来源仓库：`https://github.com/Wangyuhan29/b-group-project`。
- 来源归档 SHA：`580f8a904bd24a18f1743320093b46aabb95adf8`。
- 来源目录：`artifacts/e4/a03-cross-validation-6abc4d8-20261018/`。
- [B03 原始双向报告](https://github.com/Wangyuhan29/b-group-project/blob/580f8a904bd24a18f1743320093b46aabb95adf8/docs/e4/A03_CROSS_VALIDATION_20261018.md)。

本目录从上述固定 Git 提交按原始字节提取，不从已被 Windows 自动换行转换的工作区复制。
除本 README 为 A03 编写的来源索引外，其余文件保留 B03 提交中的内容。

## 实际执行与结果

执行目录为 `/root/241250086/a03-e4-cross-20261018/e4-a03/`，
成功运行目录为其下 `work/20261018-170959/`。B03 干净检出固定版本，
没有修改源码或配置，按 README 原样执行 `make all`。

| 检查 | 结果 |
| --- | --- |
| 环境 | Ubuntu 24.04.4，x86_64，2 CPU，约 1.7 GiB 可见内存，Docker Engine 29.1.3 |
| doctor | `problems=[]` |
| build | 成功；日志保留 pip 超时后原命令自动重试成功的记录 |
| test | `3 passed in 0.01s` |
| smoke | `make_exit_code=0`，`app_output=1`，`trace_lines=1206`，`passed=true`；记录打开 `config.h` |
| scan | 仓库、Git 历史和镜像均未发现问题；`.env` 未跟踪、权限 600，内容未取回 |
| 总体 | `make all` 总退出码 `0`，运行前后工作区干净 |

## 文件与校验

```text
manifest.json                     B03 原始逐文件 SHA-256 清单与传输包哈希
receipt.json                      B03 运行回执
metadata.txt                      被测 SHA、origin、身份、内核和运行路径
make-all.log                      完整命令输出
raw/20261018-170959/
  env.json                        环境自检
  build.log                       构建日志
  image.json                      本地镜像信息
  toolchain.lock                  实际工具链版本
  test.log                        3 项单测
  smoke.json                      冒烟和系统调用记录
  secret-scan.txt                 扫描结果
```

2026-10-18，A03 核验 `manifest.json` 的 `files` 字段列出的 10 个文件，
SHA-256 全部一致；这些文件与来源 Git blob 逐字节一致。
本目录受 `../.gitattributes` 的 `-text` 规则保护，不要手工规范化换行或格式化 JSON。

`archive_sha256` 是 B03 对原始传输压缩包的记录，压缩包不在本仓库，
A03 本次未重新核验该包，不用重新打包的文件冒充它。
本地镜像 ID 也不代表已发布的 registry digest。

双向闭环结论见 [交叉验证记录](../../docs/B03_CROSS_VALIDATION.md)。
