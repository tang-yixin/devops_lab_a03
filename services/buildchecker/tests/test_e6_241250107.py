import unittest
import tempfile
import os
from buildchecker.fullcheck import declaration_graph

class TestDeclarationGraphPhonyAndOrderOnly(unittest.TestCase):
    def test_phony_and_order_only(self):
        # 构造符合 Make 数据库格式的文本，包含 # Files 段、.PHONY 和 order-only 依赖
        make_db_text = """
# Files
app: main.o | build_dir
.PHONY: clean
clean:
"""
        # 将文本写入一个临时文件，因为 declaration_graph 需要读取文件路径
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".txt") as f:
            f.write(make_db_text)
            tmp_path = f.name

        try:
            # 调用解析函数，root 设置为 "/app" 模拟项目根目录
            result = declaration_graph(tmp_path, "/app")

            # 断言 1：.PHONY 声明的 clean 目标不应出现在结果中
            self.assertNotIn("clean", result, "伪目标 clean 应被过滤掉")

            # 断言 2：app 目标存在，并且其 order-only 依赖包含 build_dir
            app_entry = result.get("app")
            self.assertIsNotNone(app_entry, "目标 app 应被解析出来")
            self.assertTrue(any("build_dir" in item for item in app_entry["order_only"]),
                            "order-only 依赖 build_dir 应被单独记录在 order_only 字段中")
        finally:
            os.unlink(tmp_path)

if __name__ == '__main__':
    unittest.main()
