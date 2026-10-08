#!/usr/bin/env python3
"""
原本 B 组任务：DRAFT。
A 组已从 E2 派生 minicalc 源码、Makefile、README、Dockerfile。
B 组需实际构建 Docker 镜像、运行、验证输出并保存证据。
"""
from pathlib import Path
from utils import Evidence


def prepare_b_draft(root: Path, ev: Evidence):
    d = root / "fixtures" / "draft"
    if not (d / "Dockerfile.broken").exists():
        ev.observe("B_DRAFT", "跳过", "fixtures/draft/Dockerfile.broken 不存在")
        return

    ev.observe(
        "B_DRAFT",
        "已从 E2 派生 minicalc DRAFT 样本",
        f"待 B 组执行: "
        f"docker build -f {d}/Dockerfile.broken -t e3-draft-broken {d}; "
        f"docker build -f {d}/Dockerfile.reference -t e3-draft-ref {d}; "
        f"docker run --rm e3-draft-ref"
    )