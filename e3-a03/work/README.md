# work/ —— 真实 Git 提交与参考修复

> 依据 PPT 第 12 页：`work/` 用于存放「真实 Git 提交与参考修复」。
> 说明：A 组的真实提交（Minicalc c0/c1/c2）不在本仓库，而在目标项目仓库
> `https://github.com/hardtosleep/Minicalc-DevOps-Test.git`，避免重复提交。

## 真实提交（引用）

| 提交 | 完整 SHA | 说明 |
|---|---|---|
| c0 | `e3a1eda0965e545d96467d275bccaf78c890fcac` | minicalc baseline（3 MISSING + 1 REDUNDANT） |
| c1 | `f863c2deff1bd95e56f1578b872ae6aa26e3bfc8` | configurable token capacity（+1 MISSING） |
| c2 | `e103bcb3726a3fd7253deb0d791ac74fac77cafe` | restore legacy hook（-1 REDUNDANT） |

## 真实运行证据

真实 `make` / `make test` / strace 的运行记录见：

- `../evidence/minicalc-real-run.md` —— 三 commit 构建与功能测试
- `../evidence/linux-verified/` —— strace 原始跟踪证据

## 参考修复（A 组侧）

A 组的职责是「诊断」（BuildChecker/EChecker 输出 MD/RD），「修复」（参考补丁）
由 B 组 MDFixer 负责。A 组不产出修复补丁，故本目录仅保留上面的真实提交引用。
