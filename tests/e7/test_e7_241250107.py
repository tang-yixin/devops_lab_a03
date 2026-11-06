"""E7 student oracle test (241250107): report missing trace_id must be rejected."""
import importlib.util
from pathlib import Path
import unittest

gate_path = next(parent / "scripts/run_e7_a_gate.py" for parent in Path(__file__).resolve().parents
                 if (parent / "scripts/run_e7_a_gate.py").is_file())
spec = importlib.util.spec_from_file_location("gate", gate_path)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

def successful(findings):
    return {"trace_id": "test", "status": "SUCCEEDED", "build_exit_code": 0,
            "clean_exit_code": 0, "findings": findings}

class MissingTraceIdTests(unittest.TestCase):
    def test_missing_trace_id_is_rejected(self):
        # 构造合法的 findings 列表
        findings = [{"type": t, "target": target, "dependency": dep, "evidence": ["test"]}
                    for t, target, dep in gate.EXPECTED]
        report = successful(findings)
        
        # 故意删除 trace_id
        report.pop("trace_id")
        
        # 断言：缺少 trace_id 时，evaluate 必须抛出 ValueError 拒绝
        with self.assertRaises(ValueError):
            gate.evaluate("original-1", 1, report)
            
        # 对照：把 trace_id 加回来，必须通过（不抛错）
        gate.evaluate("original-1", 1, successful(findings))

if __name__ == "__main__":
    unittest.main()
