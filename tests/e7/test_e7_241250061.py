"""E7 student oracle test (241250061): an original report carrying one extra finding must be rejected.

输入：在完全合法的 original 报告（两条精确错误、状态/退出码/证据锚点齐全）里额外塞入第三条
带完整 evidence 的 finding，CLI 退出码仍为 1。
预期：evaluate() 必须以 ValueError 拒绝（错误集合与预期不符）；同一报告去掉多余 finding 后
必须通过——证明拒绝确实来自"多出一条"，而非报告其他字段。
"""
import importlib.util
from pathlib import Path
import unittest

gate_path = next(parent / "scripts/run_e7_a_gate.py" for parent in Path(__file__).resolve().parents
                 if (parent / "scripts/run_e7_a_gate.py").is_file())
spec = importlib.util.spec_from_file_location("gate", gate_path)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

def successful(findings):
    return {"trace_id": "test", "status": "SUCCEEDED", "build_exit_code": 0, "clean_exit_code": 0, "findings": findings}

class ExtraFindingTests(unittest.TestCase):
    def test_extra_finding_is_rejected(self):
        expected = [{"type": t, "target": target, "dependency": dep, "evidence": ["test"]}
                    for t, target, dep in gate.EXPECTED]
        extra = expected + [{"type": "MISSING", "target": "main.o", "dependency": "stdio.h",
                             "evidence": ["test"]}]
        with self.assertRaises(ValueError):
            gate.evaluate("original-1", 1, successful(extra))
        gate.evaluate("original-1", 1, successful(expected))

if __name__ == "__main__":
    unittest.main()
