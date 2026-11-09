"""E7 student oracle test (241250106): findings with a zero CLI exit code must be rejected.

方向（组长分配）：**有 findings 但 CLI 退出码是 0，必须拒绝**
（evaluate 的报错原文：CLI exit code does not enforce findings gate）。

输入：完全合法的 original 报告——trace_id、status=SUCCEEDED、build_exit_code=0、
clean_exit_code=0 齐全，findings 恰为 EXPECTED 的两条且每条都带 evidence 锚点——只把
CLI 退出码从 1 改成 0。
预期：evaluate() 必须以 ValueError 拒绝，且错误信息是退出码门禁那一条（不是 oracle 集合
不符、也不是缺 evidence）；同一份报告把退出码改回 1 必须通过——对照证明拒绝来自"退出码
没有把 findings 传达给调用方"，而不是报告里别的字段。

对称方向：修复后（fixed）findings=[] 却仍报退出码 1，同样必须被同一条规则拒绝；只有
"有发现→1、无发现→0"的配对才允许通过。
"""
import importlib.util
from pathlib import Path
import unittest

gate_path = next(parent / "scripts/run_e7_a_gate.py" for parent in Path(__file__).resolve().parents
                 if (parent / "scripts/run_e7_a_gate.py").is_file())
spec = importlib.util.spec_from_file_location("gate", gate_path)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

EXIT_CODE_ERROR = "CLI exit code does not enforce findings gate"


def successful(findings):
    return {"trace_id": "test", "status": "SUCCEEDED", "build_exit_code": 0,
            "clean_exit_code": 0, "findings": findings}


def expected_findings():
    return [{"type": t, "target": target, "dependency": dep, "evidence": ["test"]}
            for t, target, dep in gate.EXPECTED]


class FindingsExitCodeTests(unittest.TestCase):
    def test_zero_exit_with_findings_is_rejected(self):
        """有发现却报 0：三个 original 场景都必须拒绝，且必须是退出码那一条报错。"""
        findings = expected_findings()
        for name in ("original-1", "original-2", "original-3"):
            with self.assertRaisesRegex(ValueError, EXIT_CODE_ERROR):
                gate.evaluate(name, 0, successful(findings))

    def test_nonzero_exit_with_same_findings_passes(self):
        """对照：同一份报告，退出码报 1 则通过——证明上面拒绝的是退出码而非其他字段。"""
        findings = expected_findings()
        for name in ("original-1", "original-2", "original-3"):
            self.assertIsNone(gate.evaluate(name, 1, successful(findings)))

    def test_repaired_case_must_exit_zero(self):
        """对称方向：fixed 场景无发现却报 1，也必须被同一条规则拒绝。"""
        with self.assertRaisesRegex(ValueError, EXIT_CODE_ERROR):
            gate.evaluate("fixed", 1, successful([]))
        self.assertIsNone(gate.evaluate("fixed", 0, successful([])))

    def test_any_other_exit_code_is_rejected_too(self):
        """不是"非 0 即通过"：只有 1 能传达成"有发现"，2/3 之类同样必须拒绝。"""
        findings = expected_findings()
        for code in (0, 2, 3):
            with self.assertRaisesRegex(ValueError, EXIT_CODE_ERROR):
                gate.evaluate("original-1", code, successful(findings))


if __name__ == "__main__":
    unittest.main()
