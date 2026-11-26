# AI使用记录（E11-E12）

工具/模型/日期：Claude Code（ccs-claude-zhipu GLM-5.3）/ 2026-11-26。

输入上下文与问题：教师 DevOps_E11_E12 分发包；组长委托 AI 执行本人 E11-E12 全流程（固定样例三模式、API 契约、真实项目 Minicalc 适配与接入），组长全程知情并核对。

模型建议：profile 机制设计（默认行为零回归）；候选 Dockerfile TUNA 镜像源行；DRAFT 超时的预热缓存方案；API 重启契约的时序坑；Docker COPY 目录平铺问题的定位与修复。

采纳/拒绝及理由：全部采纳并实测验证；性能与发现数据如实保留。

人工修改：服务器重装后 gh 重新授权、三 PR 合并授权、真实项目提交内容确认均由组长本人完成。

实际验证命令/输入/结果：run_e11e12.py test 13/13 OK；e11-a/e11-b/e12/真实项目四模式 SUCCEEDED；API 五条契约实测通过。

参考实现与个人贡献边界：pipeline/server/vendor 来自教师参考包未改语义（仅按手册扩目标映射）；个人贡献=profile 适配 + 两个测试类 + 四模板 + 自主任务。
