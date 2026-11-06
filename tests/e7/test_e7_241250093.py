"""E7 student oracle test (241250093): a finding without evidence must be rejected.

输入：完全合法的 original-1 报告（两条精确错误 MISSING(main.o, config.h) +
REDUNDANT(main.o, unused.h)、status/build_exit_code/clean_exit_code/trace_id 齐全、CLI 退出码 1），
把第一条 finding 的 evidence 置空，其余字段与其余 finding 保持合法。
预期：evaluate() 必须以 ValueError 拒绝，报错指向 "Finding has no evidence anchor"；
对照：不拿掉 evidence 的同一报告必须通过——证明拒绝确实来自"缺少证据锚点"，
而非报告的其他字段（错误集合、状态、退出码、trace_id 均未改变）。
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
    return {"trace_id": "test", "status": "SUCCEEDED", "build_exit_code": 0,
            "clean_exit_code": 0, "findings": findings}


class MissingEvidenceTests(unittest.TestCase):
    def test_finding_without_evidence_is_rejected(self):
        findings = [{"type": t, "target": target, "dependency": dep, "evidence": ["test"]}
                    for t, target, dep in gate.EXPECTED]
        broken = [dict(f) for f in findings]
        broken[0]["evidence"] = []          # 第一条 finding 拿掉 evidence，其余保持合法
        with self.assertRaises(ValueError) as ctx:
            gate.evaluate("original-1", 1, successful(broken))
        self.assertIn("evidence", str(ctx.exception))
        gate.evaluate("original-1", 1, successful(findings))   # 对照：不拿掉则通过


if __name__ == "__main__":
    unittest.main()
