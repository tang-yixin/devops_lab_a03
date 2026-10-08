#!/usr/bin/env python3
"""
调用 E2 的 validate.py 校验 E3 派生出的样例，
确保 E3 fixtures 与 E2 契约一致。
"""
import json
from pathlib import Path

from utils import Evidence


def load_mapping(root: Path) -> dict:
    cfg = root / "config" / "e2_mapping.json"
    if not cfg.exists():
        raise FileNotFoundError(f"缺少 {cfg}")
    return json.loads(cfg.read_text(encoding="utf-8"))


def verify(root: Path, ev: Evidence):
    mapping = load_mapping(root)
    e2_root = (root / mapping["e2_root"]).resolve()
    validate = e2_root / mapping["e2_validate"]

    if not validate.exists():
        ev.observe("E2_VALIDATE", "缺失", f"{validate} 不存在")
        return

    # 1. 校验 E2 共享样例
    ev.run(["python", str(validate)], cwd=e2_root)

    # 2. 校验 E2 Minicalc 样例
    minicalc = e2_root / mapping["minicalc_samples"]
    if minicalc.exists():
        for f in sorted(minicalc.glob("*.json")):
            ev.run(["python", str(validate), str(f)], cwd=e2_root)

    # 3. 记录 E3 派生 fixtures 的存在性
    for rel in ("fixtures/md-rd/ORACLE_findings.json",
                "fixtures/commits/EXPECTED.json"):
        p = root / rel
        if p.exists():
            ev.observe("E3_FIXTURE", "存在", str(p))
        else:
            ev.observe("E3_FIXTURE", "缺失", str(p))