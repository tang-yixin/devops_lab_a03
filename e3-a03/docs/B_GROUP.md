# B 组工作说明

## 1. B 组定位

B 组负责 DRAFT 样本、MDFixer 固定输入、补丁应用与修复验证、无效候选与恢复验证等工作。

本文件说明：

- 当前项目中已经为 B 组完成了什么。
- B 组还需要完成什么。
- 已有输入在哪里。
- 预期结果和证据要求是什么。

---

## 2. 当前项目已为 B 组完成的内容

### 2.1 DRAFT 样本文件

样例来源：E2 `artifacts/minicalc/c0/`

- 源码：`fixtures/draft/src/`
- Makefile：`fixtures/draft/Makefile`
- README：`fixtures/draft/README.md`
- `Dockerfile.broken`：故意缺少工具链
- `Dockerfile.reference`：安装 `gcc make libc6-dev`

构建：`make`
运行：`./minicalc`
预期输出：与 E2 `full-response.json` 一致，退出码 0。

### 2.2 MDFixer 固定输入

已生成 MDFixer 固定输入，位于：

```text
fixtures/mdfixer/
```

包含：

- `fixed_report.json`
- `Makefile.before`
- `reference.patch`
- `invalid.patch`

`fixed_report.json`：

```json
{
  "provenance": "INSTRUCTOR_ORACLE",
  "findings": [
    {"type": "MISSING", "target": "main.o", "dependency": "config.h"}
  ]
}
```

`Makefile.before`：

```make
app: main.o
	cc main.o -o app

main.o: main.c
	cc -c main.c -o main.o

clean:
	rm -f main.o app
```

`reference.patch`：

```diff
--- a/Makefile
+++ b/Makefile
@@ -1,7 +1,7 @@
 app: main.o
 	cc main.o -o app
 
-main.o: main.c
+main.o: main.c config.h
 	cc -c main.c -o main.o
 
 clean:
```

`invalid.patch`：

```diff
--- a/Makefile
+++ b/Makefile
@@ -1,7 +1,7 @@
 app: main.o
-	cc main.o -o app
+	exit 1
 
 main.o: main.c
 	cc -c main.c -o main.o
```

### 2.3 已生成的文档

已生成：

- `docs/B_GROUP.md`：本说明。
- `docs/EXPECTED_RESULTS.md`：预期结果汇总中的 B 组部分。
- `docs/EVIDENCE_GUIDE.md`：证据目录说明，包含 B 组证据保存要求。

### 2.4 已生成的脚本

已生成：

- `scripts/prepare_b_draft.py`：生成 DRAFT 样本和两个 Dockerfile。
- `scripts/prepare_b_mdfixer.py`：生成 MDFixer 固定报告、参考补丁和无效补丁。

这些脚本只负责生成样例和固定输入，不负责实际执行 Docker 构建、补丁应用和修复验证。

---

## 3. B 组还需要完成的内容

B 组需要基于已生成的样例和固定输入，完成实际运行、验证和证据采集。

### 3.1 DRAFT 失败构建与参考成功验证

需要完成：

1. 构建 `Dockerfile.broken`，预期非零退出。
2. 保存失败构建日志，能定位到 `make: not found`。
3. 构建 `Dockerfile.reference`，预期成功。
4. 保存构建日志、镜像 ID。
5. 运行参考镜像，验证输出 `hello E3`，退出码 0。
6. 保存 Dockerfile diff、构建退出码、运行输出。

建议证据位置：

```text
work/<timestamp>/draft/
├── docker-build-broken.log
├── docker-build-broken.exit-code
├── docker-build-reference.log
├── docker-build-reference.exit-code
├── image-id.txt
├── hello-output.txt
└── dockerfile.diff
```

预期结果：

| 场景 | 预期 |
|---|---|
| `Dockerfile.broken` | 构建非零退出，日志可定位到 `make: not found` |
| `Dockerfile.reference` | 构建成功，运行输出 `hello E3` |

### 3.2 MDFixer 补丁应用与修复验证

需要完成：

1. 复制 `fixtures/mdfixer/` 到工作目录。
2. 使用 `Makefile.before` 作为修复前状态。
3. 执行 `git apply --check reference.patch`，保存检查日志。
4. 执行 `git apply reference.patch`，保存应用日志。
5. 修复前验证：只改 `config.h`，`make` 后仍输出旧值。
6. 修复后验证：`make clean && make`，输出新值。
7. 再次修改 `config.h`，不 clean，`make` 后应自动重建，预期输出 3。
8. 验证无效候选：应用 `invalid.patch`，`make` 应非零退出。
9. 恢复原 `Makefile`，再次构建和测试应通过。
10. 保存所有日志和退出码。

建议证据位置：

```text
work/<timestamp>/mdfixer/
├── patch-check.log
├── patch-apply.log
├── before-fix.log
├── after-fix.log
├── second-change.log
├── invalid-candidate.log
└── recovery.log
```

验证要求：

- 修复前：只改头文件仍输出旧值。
- 修复后：clean 输出新值。
- 再次修改头文件：不 clean 也能自动重建。
- 不能只靠 clean 成功证明 MD 修好了。
- 无效候选必须被拒绝，并能恢复到可构建状态。

### 3.3 四种声明风格完整样例

需要基于同一个缺失依赖 `main.o -> config.h`，准备四种声明风格的参考修复：

| 风格 | 原声明方式 | 参考修复 |
|---|---|---|
| Target | `main.o: main.c` | 直接补 `config.h` |
| Macro | `main.o: $(DEPS)` | 在 `DEPS` 中补 `config.h` |
| Hybrid | `main.c $(HEADERS)` | 保留直接项，更新头文件宏 |
| Implicit | `%.o: %.c` | 编译生成 `.d`，再 `include` |

需要为每种风格生成：

- 修复前 Makefile。
- 修复后 Makefile。
- 行为验证命令与输出。
- 再次修改头文件后的重建证据。

### 3.4 隐式规则与 `.d` 文件验证

需要完成：

1. 编写使用 `-MMD -MP` 的 Makefile：

```make
%.o: %.c
	$(CC) -MMD -MP -c $< -o $@

-include main.d
```

2. 编译后检查 `main.d` 内容，典型为：

```text
main.o: main.c config.h
```

3. 再次修改 `config.h`，不 clean，验证自动重建。
4. 保存 `.d` 文件内容和构建日志。

### 3.5 无效候选与恢复验证

需要完成：

1. 使用 `invalid.patch` 故意加入失败命令。
2. 执行 `make`，预期非零退出。
3. 保存失败日志。
4. 恢复原 `Makefile`。
5. 再次执行 `make` 和功能测试，预期通过。
6. 保存恢复日志。

### 3.6 真实运行记录表

需要整理 B 组真实运行记录，例如：

| 场景 | 实际观察 | 解释 |
|---|---|---|
| 失败候选 | 非零退出 | 构建失败日志可定位 |
| 成功参考 | 输出 `hello E3` | 样本构建与验证可用 |
| 参考补丁 | 再次改头文件输出 3 | 修复有效 |
| 无效补丁 | `make` 非零退出 | 候选被拒绝 |
| 恢复副本 | 构建和测试再次通过 | 可恢复 |

---

## 4. B 组证据保存要求

所有证据保存到：

```text
work/<timestamp>/draft/
work/<timestamp>/mdfixer/
```

必须区分：

- 人工 ORACLE：`fixtures/mdfixer/fixed_report.json`。
- 实际运行日志：`work/<timestamp>/mdfixer/*.log`。
- 实际 Docker 日志：`work/<timestamp>/draft/*.log`。

禁止：

- 把人工报告当作工具输出。
- 把人工答案计入工具准确率。
- 只保留成功记录，删除失败记录。
- 覆盖已有 `work/<timestamp>/`。

---

## 5. B 组检查清单

完成 B 组后，应检查：

- [ ] 别人能按 README 运行吗？
- [ ] 人工答案和实际日志分清了吗？
- [ ] 预期结果能说明依据吗？
- [ ] 失败记录能定位到具体版本吗？
- [ ] `Dockerfile.broken` 失败日志是否保存？
- [ ] `Dockerfile.reference` 构建日志、镜像 ID、运行输出是否保存？
- [ ] `git apply --check` 和 `git apply` 日志是否保存？
- [ ] 修复前只改头文件是否仍输出旧值？
- [ ] 修复后再次改头文件是否自动重建？
- [ ] 无效候选是否被拒绝？
- [ ] 恢复后是否再次构建和测试通过？
- [ ] 四种声明风格是否都有样例和验证？
- [ ] `.d` 文件内容和隐式规则验证是否保存？
- [ ] 是否记录了 Git commit / SHA？
- [ ] 是否记录了工具版本和系统环境？

---

## 6. B 组与后续任务关系

| 后续任务 | 使用的 B 组证据 |
|---|---|
| E4 环境和密钥管理 | `work/<timestamp>/draft/` 中的 Dockerfile、镜像 ID、构建日志 |
| E5 DRAFT | `fixtures/draft/`、`work/<timestamp>/draft/` |
| E8 MDFixer | `fixtures/mdfixer/`、`work/<timestamp>/mdfixer/` |
| E12 接入真实数据联调 | DRAFT 与 MDFixer 的实际运行记录和验证证据 |

---

## 7. 当前项目已完成 / 待完成总览

| 内容 | 状态 | 位置 |
|---|---|---|
| DRAFT 样本源码、Makefile、README | 已完成 | `fixtures/draft/` |
| `Dockerfile.broken`、`Dockerfile.reference` | 已完成 | `fixtures/draft/` |
| MDFixer 固定报告、参考补丁、无效补丁 | 已完成 | `fixtures/mdfixer/` |
| DRAFT 实际 Docker 构建与运行 | 待 B 完成 | `work/<timestamp>/draft/` |
| MDFixer 补丁应用与修复验证 | 待 B 完成 | `work/<timestamp>/mdfixer/` |
| 四种声明风格完整样例 | 待 B 完成 | `fixtures/mdfixer/` 或 `work/<timestamp>/mdfixer/` |
| 隐式规则与 `.d` 文件验证 | 待 B 完成 | `work/<timestamp>/mdfixer/` |
| 无效候选与恢复验证 | 待 B 完成 | `work/<timestamp>/mdfixer/` |
| 真实运行记录表 | 待 B 完成 | `docs/B_GROUP.md` 或 `work/<timestamp>/mdfixer/` |

## 已为 B 组完成

- 从 E2 派生的 Minicalc DRAFT 样本（`fixtures/draft/`）
- `Dockerfile.broken`、`Dockerfile.reference`
- MDFixer 固定输入（`fixtures/mdfixer/`）
- `finding-id-v1.json`、`repair-request.json`、`incremental-request.json`

## B 组还需完成

- 实际 `docker build` / `docker run`，保存日志、镜像 ID、输出
- `git apply --check` / `git apply`，保存日志
- 修复前只改头文件仍输出旧值
- 修复后再次改头文件自动重建
- 无效候选非零退出 + 恢复
- 四种声明风格（Target / Macro / Hybrid / Implicit）
- 隐式规则与 `.d` 文件（`-MMD -MP`）
- 所有证据保存到 `work/<timestamp>/draft/` 和 `work/<timestamp>/mdfixer/`