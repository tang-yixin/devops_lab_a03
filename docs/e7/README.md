# E7 阶段说明（A03 · A 轨道 BuildChecker）

> 任务：验证与 CI 门禁。本地完整 gate 八场景（同一样例三次一致 / 修复清零 / 构建失败 /
> 多输出 / 超时）+ GitHub Actions 全流程（正常 CI → main 分支保护 → 故意失败 PR 被实际
> 拒绝合并 → 修复 → 恢复合并）。本文件为开工骨架（2026-11-06 直推），收尾内容由组长
> 通过 PR 回填——分支保护启用后 main 不再接受直推。
> 个人交付物在各 `docs/<学号>/` 目录；本阶段报告模板在 `docs/e7/templates/`。

## 1. 完成情况（待收尾回填）

| 学号 | 个人分支 | PR | 新增判定测试 | 判定测试数 | gate 目录（首轮/复跑） | 归档（~/devops-submissions/） |
|---|---|---|---|---|---|---|
| 241250061 | student/241250061/e5-e7 | 待填 | 待填 | 6→7 | 待填 | 待填 |
| 241250093 | student/241250093/e5-e7 | 待填 | 待填 | 6→7 | 待填 | 待填 |
| 241250106 | student/241250106/e5-e7 | 待填 | 待填 | 6→7 | 待填 | 待填 |
| 241250107 | student/241250107/e5-e7 | 待填 | 待填 | 6→7 | 待填 | 待填 |

## 2. CI 闭环记录（组长执行，每组一次；待收尾回填）

| 阶段 | 运行 ID / PR | head SHA | 结论 | 证据位置（组长克隆 work/） |
|---|---|---|---|---|
| main 正常 CI | 待填 | 待填 | success | ci-normal/ |
| 分支保护配置 | — | — | strict/enforce_admins=true | ci-setup/ |
| 故意失败 PR（被拒） | 待填 | 待填 | failure + OPEN/BLOCKED | ci-rejection/ |
| 修复后恢复（MERGED） | 待填 | 待填 | success + MERGED | ci-recovery/ |

## 3. 交付物与位置

| 交付物 | 位置 | 说明 |
|---|---|---|
| 个人新增判定测试 | `tests/e7/test_e7_<学号>.py` | 新包 05 口径：独立小报告字典调 evaluate()，不碰 Docker |
| 个人 E7 报告 | `docs/<学号>/`（按 `docs/e7/templates/E7实验报告.md` 填写） | 用本人运行数据 |
| 个人验收记录 | `docs/<学号>/`（按 `docs/e7/templates/E7验收记录.csv` 填写） | A 轨道 B 行标 N/A |
| 原始证据 | 服务器各人克隆 `work/`（e7-01 / build-02 / e7-02 / ci-pr/）；组长本地镜像 `work/<学号>/` | 不进 git |
| CI 证据（全组共享） | 组长克隆 `work/ci-normal|ci-setup|ci-rejection|ci-recovery/` | artifact 已在 14 天保留期内下载 |
| 归档备份 | 服务器 `~/devops-submissions/<学号>/*.tar.gz` | tar 排除 .git/.env/密钥 |

## 4. 关键事件与备注（待收尾回填）

- （骨架占位：E7 包上传/乱码处理、CI 闭环执行细节、组员 PR 合并顺序等收尾时回填）

## 5. E7 之后

E7 为 E4—E7 系列最后一阶段。收尾时更新根 README 进度行与组长交接文档。
