# ADR：集成接口决策

编号、日期、作者：ADR-E11E12-1 / 2026-11-26 / 241250061（AI 受托起草，组长核对）

问题：E11-E12 要求 BuildChecker→EChecker→MDFixer 以版本化产物衔接并经异步任务 API 消费（e11e12-1 契约）；运行环境为国内云 ECS、四人共用同一 HOME 与 Docker 守护进程，且服务器无法直连 Docker Hub。

候选方案：
1. 修改 candidate.Dockerfile 追加国内 apt 镜像源以解 DRAFT 超时——**否**：候选内容是 prepare 固定生成且 pipeline 记录 candidate_sha256，改文件偏离课程固定输入；CI 在 GitHub 机房网络不受影响。
2. dockerd 系统级配 registry mirror（m.daocloud.io），library/docker 403 时改经 docker.1ms.run 按 digest 拉取后 retag——**采用**：系统一次全组受益、不动课程包文件，digest 钉死与上游内容一致。
3. DRAFT 超时最终解——宿主上以与 iter-02 完全相同的 Dockerfile 文本+文件内容不限时预构建一次，利用 buildkit 指令文本+内容哈希层缓存，全组后续 E11-B/E12/API 运行秒级命中——**采用**（共享服务器=共享层缓存，与 E4 手册"共用同一台服务器及 Docker 缓存"同机制；组员无需任何操作）。
4. gh 凭证——沿用 E5 设计：gh auth login --web OAuth token + 每人独立 GH_CONFIG_DIR（~/devops-auth/<学号>/github）；gh 2.4.0 无 --git-protocol 旗标，按 E5 手册原命令执行。

输入输出字段：e11e12-1 envelope（schema_version/job_id/trace_id/kind/commit/status/data/artifacts）；artifact://<job_id>/<相对路径> + SHA256 + bytes；消费前 check_envelope 核 schema/commit/status/kind，load_artifact 核内容哈希（ARTIFACT_HASH_MISMATCH 防中间篡改）；幂等键非空且 ≤128 字符、同键异输入 409。

兼容性与测试：vendor test_contract.py 10 项 + 新增 StudentContract241250061（幂等键长度契约先于请求校验拒收）；CI 工作流 e11e12.yml（契约测试+固定样例三模式）随导入 PR 进 main 后设为必需检查。

验证命令与实际证据：python3 run_e11e12.py test → 全部通过；run --request e11-a/e11-b/e12 三模式 SUCCEEDED（work/e11-a-01、e11-b-02、e12-01）；API 五条契约实测（work/api-jobs/、work/api-client/）。

---

增补（2026-11-26，真实项目接入）：Minicalc 不满足教学接口，选"profile 机制扩展目标映射"而非改写项目或复制 lab.py——默认 profile 行为与原实现逐字节等价（E8-E10 的 21 项测试与三门禁 CI 证明无回归），真实项目走请求内嵌 profile；候选 Dockerfile 加 TUNA 镜像源行属DRAFT 校验允许的 RUN 插入且解决 CN 网络 apt 慢；坑位：Docker COPY 目录进多源列表时只拷内容不保层级（`COPY Makefile src include ./` 平铺导致 make 失败），改 `COPY . ./`保持仓库结构——两份 Dockerfile 的非 RUN 行须保持一致（prepare_candidate 约束）。
