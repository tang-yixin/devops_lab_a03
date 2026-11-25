# AI使用记录

工具/模型/日期：Claude Code（ccs-claude-zhipu GLM-5.3）/ 2026-11-14。

输入上下文与问题：教师 DevOps_E8_E10_20261031 分发包（操作手册、labs/e8e10 参考实现、08 测试示例）；组长委托 AI 在服务器执行本人 E8/E9 实验全流程、编写测试并起草文档，组长全程知情。

模型建议：任务分层清单与公共准备分层；自研测试场景（新建头文件间接包含、删冗余声明）；GBK 解压与免交互 SSH 方案；C2 步骤代码块损坏后的 git checkout 修复；测试换行改用 chr(10) 规避转义歧义。

采纳/拒绝及理由：场景设计与修复方案采纳并验证通过；"改 lab.py 刷新粒度"方向经评估与 E10 矩阵预期冲突而放弃（见 ADR）。

人工修改：PR #21 合并、e8e10-quality-gate 设为必需检查由组长本人决策；报告个人信息由组长核对；两次转义事故处置过程组长知情。

实际验证命令/输入/结果：unittest 11 项 OK 退出 0；E8 BASELINE_PASS / BUILDCHECKER_BASELINE_PASS / REUSE_PASS；E9 C0_BUILD_AND_BASELINE_PASS / C1_REUSE_PASS / C2_REFRESH_PASS / C3_RESOLVED_PASS。

参考实现与个人贡献边界：lab.py、run_lab.py、e8e10.yml 全部来自教师参考包，未修改；个人贡献=test_profile.py 两个类四个测试（两个改编自 08 示例、两个自研场景）与 docs/students/241250061/e8-e10 三份报告；服务器操作由 AI 受托执行，输入输出完整留痕于 D:/DevOps/E8-E9/ 执行记录与 work/ OUT。

---

工具/模型/日期：Claude Code（ccs-claude-zhipu GLM-5.3）/ 2026-11-25（E10 补做会话）。

输入上下文与问题：教师 DevOps_E8_E10_20261031 包 E10 部分（10_E10_A组.md）；服务器 11-25 重装重建后，组长委托 AI 执行 E10 补做全流程（组长全程知情并授权）。

模型建议：六场景逐项脚本化执行并留痕（/root/e10-driver 16 个脚本，本机 D:/DevOps/E10-E12/driver 同步）；自主场景选链式第 3 头；发现并处置服务器无法直连 Docker Hub（dockerd 配 m.daocloud.io mirror，属系统级配置，未改教师包任何文件）；识别组长新生成 PAT 异常（权限仅 read:packages 且有历史使用记录，疑似在旧 token 行上 Regenerate），暂停 push/PR 等提交链步骤等待新 PAT。

采纳/拒绝及理由：上述采纳并全部实测验证；性能汇总如实保留 full/inc<1 的刷新场景数据（手册明示不替换成论文加速倍数）。

人工修改：服务器重装、root 密码更换、PAT 生成/作废均由组长本人操作。

实际验证命令/输入/结果：E10 六场景×5 次 30 行 equal=True；DYNAMIC_CROSSCHECK_AND_MATRIX_PASS；gate.json passed=true rows=30；MATRIX_PASS 六类各 5 次；chain 五次 equal=True（CHAIN_FIVE_REPEATS_PASS）；unittest Ran 18 tests OK 退出 0（work/unit-tests-20261125-193551.log）。

参考实现与个人贡献边界：lab.py、run_lab.py、e8e10.yml 未修改（沿教师参考包）；E10 个人贡献=自主 chain 场景（预期先行+五次测量+summary）与 test_profile.py 新增 StudentE10A241250061；服务器操作由 AI 受托执行，输入输出留痕于 /root/e10-driver/、work/e10-A-manual.bteGid 与 D:/DevOps/E10-E12/ 执行记录。
