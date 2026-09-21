# A → B 交接说明

## 对接顺序

1. B 说明 DRAFT 输出中的仓库版本、镜像、项目根目录、构建和验证命令；A 确认能使用。
2. A 按同一目标仓库、完整 SHA 和 configuration_id 执行 FULL_CHECK，保存图、报告和证据。
3. A 后续执行 INCREMENTAL_CHECK 时携带旧图、base_commit 和相同配置，输出当前图和发现变化。
4. A 将 MISSING 过滤成独立 ERROR_REPORT，保留位置、证据、提交和配置，交给 B 的 REPAIR。
5. B 返回候选补丁与构建/测试结果，双方协商修复源码身份后由 A 重检。

## 本次已有可查看文件

A 组已生成的目标项目产物在 `artifacts/minicalc/{c0,c1,c2}/`：

| 文件 | B 应检查的内容 |
|---|---|
| `c0/actual.json` / `c0/declared.json` | C0 实际/声明依赖图 |
| `c0/error-report.json` | C0 的 3 MISSING + 1 REDUNDANT |
| `c0/md-only-report.json` | 仅含 3 MISSING，供 REPAIR 消费 |
| `c0/evidence.json` | `gcc -MM` 原始输出 |
| `c1/*`、`c2/*` | 对应提交的图、报告、证据 |
| `../../artifacts/index.json` | 全部产物 SHA-256 注册 |

## artifact URI 如何读取

`artifact://minicalc/<commit>/<name>` 映射为仓库内 `artifacts/minicalc/<commit>/<name>`，
用 `artifacts/index.json` 验证 SHA-256。

## 当前边界

- 构建镜像：B 组已提供 C2 digest，A 组已 `docker run` 冒烟验证通过。
- 产物由 `gcc -MM` 辅助生成，不含论文的进程/系统调用动态追踪。
- C1/C2 变化基于逐版本重新扫描，未实现 EChecker 增量算法。
- 真实 Checker 联调、跨机器产物读取仍待开展（E3/E12）。
