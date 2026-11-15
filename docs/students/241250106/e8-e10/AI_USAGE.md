# AI使用记录

工具/模型/日期：DeepSeek Harness 编码代理（deepseek 系列模型，编辑器内运行），2026-11-15；配合本人手工确认方向与数据。

输入上下文与问题：输入是教师手册 `8_E8_A组.md`、`9_E9_A组.md`、`08_个人测试编写示例.md`、本组 `E8-E9_组员操作手册_20261114.md` 与仓库内 `labs/e8e10/lab.py`、`labs/e8e10/test_profile.py`。要解决的问题有三个：（1）按手册把 E8 的 0—7 步、E9 的 0—10 步在自己的 OUT 里逐框跑通并留下可回溯证据；（2）在分配给我的方向上写出"先有独立预期、再看实现结果"的测试；（3）把 OUT 里的真实数字（提交 SHA、trace 行号、reused/refreshed/added/resolved）填进报告三件套，而不是抄参考值。

模型建议：① 把 E8 基线拆成"gcc -MM 投影"与"真实 BuildChecker 投影"两步，先用前者写独立预期、再用后者覆盖 `actual` 并标注 `baseline_source`，避免把工具输出当预期；② E8 测试选"删除未被包含的 extra.h"，E9 测试选"CFLAGS -O0→-O1"，两者都只动 key 的一个成员（文件集合 / 配置），因此能把"刷新"和"发现不变"分开断言；③ 每个用例补一条反例断言（`extra.h` 不在实际依赖里；`-O7` 抛 `UNSUPPORTED_FLAGS`）；④ 报告里如实记录套件计数 15→17 而不是手册的 11→13，因为 main 已并入 093/107 的 PR。

采纳/拒绝及理由：采纳 ①②③④。拒绝的写法有两种：一是把 `scan()` 的返回值在测试里写成硬编码字典再断言（107 的两个用例是这种风格），它验证的是测试自己写死的常量，无法发现实现回归，我不采用；二是为了让 `refreshed` 看起来"更聪明"去改 `lab.py` 的失效粒度，这会连带改掉 E10 矩阵断言的预期，超出本次范围，也不采用。另外拒绝把 `key` 的整个 JSON 直接与旧值比较来代替字段级断言——那样断言失败时无法指出是文件集合变了还是配置变了。

人工修改：本人确认了 E8/E9 的方向与用例命名（类名带学号 `StudentE8A241250106` / `StudentE9A241250106`）、确认报告里 `校区` 一栏留空待补、确认不修改 `lab.py`、确认只在手册给的 `test_profile.py` 底部粘贴位置追加类。测试里的换行用 `'\n'` 字面量写在 `write_text(...)` 中（不经 shell 转义），与手册示例语义一致。

实际验证命令/输入/结果：
- `docker run --rm --network none --user "$(id -u):$(id -g)" -e HOME=/tmp -v "$PWD:/course" -w /course "course-e8e10:241250106" python3 -m unittest discover -s labs/e8e10 -p test_profile.py -v`
  → 加用例前 `Ran 15 tests ... OK`（`work/unit-tests-before-20261115-190344.log`），加完后 `Ran 17 tests ... OK`（`work/unit-tests-20261115-190353.log`），两次退出码 0。
- `lab_python "$OUT"`（E8 0—7 步）→ `BASELINE_PASS`、`BUILDCHECKER_BASELINE_PASS`、`REUSE_PASS`，逐步 `STEP_EXIT_CODE=0`；证据在 `work/e8-A-manual.rkuztf/`。
- `lab_python "$OUT"`（E9 0—10 步）→ `C0_BUILD_AND_BASELINE_PASS`、`C1_REUSE_PASS`、`C2_REFRESH_PASS`、`C3_RESOLVED_PASS`；证据在 `work/e9-A-manual.S8RK1A/`。
- CI 侧（提交后自动）：两个门禁 `e7-a-quality-gate` 与 `e8e10-quality-gate` 在该 head 上均为 success，artifact 已下载到 `work/ci-e8e10/<run_id>/`（最终 run ID 与结论以 PR 记录为准）。

未调用模型时写明未调用；记录参考实现和自己的贡献边界：本阶段**调用了** AI 编码代理来执行手册命令、起草测试与报告初稿；参考实现（`lab.py`、`fixture/scan/commit`、课程包样例与组长已合并的两个测试类）是课程提供的既有代码，不是我的产出；我的贡献边界是：分配方向上的两个测试用例（断言与预期由本人确认）、E8/E9 两个 OUT 里的实跑证据、报告三件套中的真实数字与解释。
