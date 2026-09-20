# ADR-005：Minicalc 目标项目、图格式与 finding_id

## Context
A 组提供 Minicalc-DevOps-Test 作为共同目标项目，含 C0/C1/C2 三个真实提交。
需约定图格式、finding_id、配置与镜像。

## Decision
- 以 Minicalc 三个 tag 的完整 SHA 固定可复现实验。
- 图格式采用最小边列表：`schema_version` + `commit` + `configuration_id` + `edges`，
  边为 `[target, dependency]`，仓库相对路径，含传递头文件包含。
- finding_id 用 `[repository.url, configuration_id, type, target, dependency]`
  的紧凑 UTF-8 JSON 数组做完整 SHA-256，前缀 `finding-`，不含 commit/行号/时间。
- `configuration_id` 暂用 `cc-default`，编译选项 `-std=c11 -Wall -Wextra -Iinclude -g`。
- 构建镜像由 B 组 DRAFT 产出（C2 digest 已提供），A 组用于环境对齐。

## Alternatives
- 从 C2 逆推旧版本无法证明真实 commit 内容，不采用。
- 内联图进 Job 响应会膨胀且无法离线校验，改用 artifact:// 引用。

## Consequences
- 图格式与 finding_id 已与 B 组共享并加入 `shared-lock.json`。
- 真实检测器（动态追踪）尚未实现，当前产物由 `gcc -MM` 辅助生成。
- C0/C1 镜像待 B 组补充；跨机器产物读取与 A 组重检留待 E3/E12。
