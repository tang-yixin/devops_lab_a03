# 验证记录

执行环境：Windows + Python 3.13 + gcc（MinGW 12.3）；Docker 用于 C2 镜像冒烟验证（`docker run` 4 断言 PASS）。

| 命令/项目 | 实际结果 |
|---|---|
| `python validate.py` | 27 个共享样例：19 个有效、8 个预期拒绝；产物 SHA-256 校验通过 |
| Minicalc 7 个样例 | 全部 PASS（含 artifact 解析） |
| `shared-lock.json` 与 B 组比对 | 33 个共享文件哈希完全一致 |
| `gcc -MM` 依赖扫描 | C0=3MD+1RD、C1=4MD+1RD、C2=4MD+0RD，与 B 组及 Minicalc README 一致 |
| finding_id 测试向量 | 与 `finding-id-v1.json` 完全吻合（`finding-4a7595ca26e9e7666102f337dfd726da30ed2e10b4b6dffd0f0fccf495899d7f`） |
| C2 镜像 `docker run` | 三个算术用例 + 版本断言全 PASS |
| 真实检测器（BuildChecker/EChecker） | 未实现（E3） |
| 跨机器产物下载、A/B 评审 | 未开展 |

## 结论

- E2 契约层面已与 B 组完全对齐并可通过校验。
- 真实检测器、镜像内联调属于 E3，尚未完成。
- 本组产物由 `gcc -MM` 辅助生成，非完整 Checker 动态追踪输出。
