# E4 假 Key 检出与清理复测

测试位置：服务器 /root/e4-members/241250061/devops_lab_a03/e4-a03/

测试方法：

1. 临时向已跟踪的 .env.example 追加测试用假 Key。
2. 使用与 make scan 相同的命令扫描工作区、Git 历史和镜像。
3. 确认扫描器返回非零退出码并报告疑似泄露。
4. 恢复 .env.example，确认文件差异为空。
5. 再次扫描，确认退出码为 0 且显示未发现问题。

结果：

- 检出阶段退出码：1
- 检出阶段：发现 2 处疑似泄露
- 恢复后文件差异：空
- 清理复测退出码：0
- 清理复测：未发现问题

原始输出：

- e4-a03-fake-key-detected.txt
- e4-a03-clean-scan.txt
- e4-a03-fake-key-detected.exit
- e4-a03-clean-scan.exit
- e4-a03-fake-key-clean.diff

测试值原文未归档，服务器工作区已恢复干净，未产生 Git 提交。
