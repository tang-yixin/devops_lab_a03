# 决策记录

背景与约束：E8-E9 在共享 2GiB 内存服务器复现 EChecker 图复用/失效机制；仓库 main 受 e7-a-quality-gate + e8e10-quality-gate 双必需检查与 strict 保护；lab.py 为教师参考实现，E10 六场景矩阵硬断言"保守刷新两目标"，教学材料明示完整论文覆盖范围为扩展任务。

选择与替代方案：
1. 个人贡献取"只加测试、不改 lab.py"。替代方案：把全目标刷新改为仅刷新受影响目标（E9 手册进阶项）——会改变 E10 矩阵预期并增加 CI 风险，放弃；改以测试刻画复用/新增/消除三类边界。
2. E8 基线双来源：gcc -MM 独立预期 + BuildChecker 真实图投影。单一来源无法避免工具自证。
3. 测试代码换行用 chr(10)：经 本机bash→ssh→容器python 多层通道追加代码时反斜杠转义两次出现歧义（执行记录有事故与修复），改用无反斜杠等价写法杜绝复发。

A（缓存何时失效、配置身份如何绑定）：预处理指令集合+配方行+flags+编译器版本构成 key；声明行不参与 key——故 C3 补声明只重算声明图、复用真实图；include/头文件内容变化必失效。

代价与覆盖范围：chr(10) 写法风格略异于常规字面量；参考实现保守刷新会在 helper.o 未受影响时也重扫（保守性换正确性）。

验证命令与实际证据：python3 -m unittest discover -s labs/e8e10 -p test_profile.py -v → Ran 11 tests OK（work/unit-tests-20261114-162408.log）；E8/E9 手册全部 PASS 标志及 steps 日志见 work/e8-A-manual.7JGkNs、work/e9-A-manual.ENG44c。
