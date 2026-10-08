#!/usr/bin/env python3
"""
原本 B 组任务：MDFixer 固定输入。
A 组暂时代为生成 fixed_report.json、Makefile.before、reference.patch、invalid.patch。
B 组需自行完成补丁应用、行为验证、无效候选恢复、声明风格与 .d 文件验证。
"""
import json
from pathlib import Path
from utils import Evidence, write_file


def prepare_b_mdfixer(root: Path, ev: Evidence):
    d = root / "fixtures" / "mdfixer"
    d.mkdir(parents=True, exist_ok=True)

    # --- 以下为 B 组固定输入，A 组暂时代为生成 ---
    # 人工 ORACLE 报告：minicalc 缺 config.h
    write_file(d / "fixed_report.json", json.dumps({
        "provenance": "INSTRUCTOR_ORACLE",
        "findings": [
            {"type": "MISSING", "target": "main.o", "dependency": "config.h"}
        ]
    }, indent=2, ensure_ascii=False))

    # 修复前 Makefile：缺少 config.h 依赖
    write_file(d / "Makefile.before", """app: main.o
	cc main.o -o app

main.o: main.c
	cc -c main.c -o main.o

clean:
	rm -f main.o app
""")

    # 参考补丁：补上 config.h 依赖（Target 风格）
    write_file(d / "reference.patch", """--- a/Makefile
+++ b/Makefile
@@ -1,7 +1,7 @@
 app: main.o
 	cc main.o -o app

-main.o: main.c
+main.o: main.c config.h
 	cc -c main.c -o main.o

 clean:
""")

    # 无效候选补丁：故意加入失败命令，预期 make 非零退出
    write_file(d / "invalid.patch", """--- a/Makefile
+++ b/Makefile
@@ -1,7 +1,7 @@
 app: main.o
-	cc main.o -o app
+	exit 1

 main.o: main.c
 	cc -c main.c -o main.o
""")

    ev.observe(
        "B_MDFixer",
        "已生成 MDFixer 固定输入（A 组暂时代为生成，实际验证待 B 组完成）",
        f"待 B 组执行: git apply --check; git apply; make; 改头文件验证; 恢复验证"
    )