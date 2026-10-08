#!/usr/bin/env python3
import time
from pathlib import Path

from utils import Evidence
from prepare_from_e2 import prepare_from_e2
from prepare_a_md_rd import prepare_md_rd
from prepare_a_commits import prepare_a_commits
from prepare_b_draft import prepare_b_draft
from prepare_b_mdfixer import prepare_b_mdfixer
from verify_with_e2 import verify


def run_linux_trace(root: Path, ev: Evidence):
    """
    A 组要求：Linux 原始跟踪证据。
    调用 scripts/linux_trace.sh，在 md-rd 样例目录下生成
    evidence/linux-verified/ 证据。
    """
    script = root / "scripts" / "linux_trace.sh"
    if not script.exists():
        ev.observe("LINUX_TRACE", "跳过", f"{script} 不存在")
        return

    md_rd = ev.workdir / "md-rd"
    if not (md_rd / "Makefile").exists():
        ev.observe("LINUX_TRACE", "跳过", f"{md_rd}/Makefile 不存在")
        return

    ev.run_shell(
        script,
        cwd=md_rd,
        args=["feature.h", "config.h"],
    )
    ev.observe("LINUX_TRACE", "完成", str(md_rd / "evidence" / "linux-verified"))


def main():
    root = Path(__file__).resolve().parents[1]
    stamp = time.strftime("%Y%m%d-%H%M%S")
    work = root / "work" / stamp
    work.mkdir(parents=True, exist_ok=True)

    ev = Evidence(work)

    # 1. 从 E2 派生 E3 fixtures
    prepare_from_e2(root)

    # 2. A 组：MD/RD 与 C0/C1/C2
    prepare_md_rd(root, ev)
    prepare_a_commits(root, ev)

    # 3. 用 E2 validate.py 校验派生的样例
    verify(root, ev)

    # 4. A 组：Linux 原始跟踪证据
    run_linux_trace(root, ev)

    # 5. B 组：DRAFT 与 MDFixer（A 组暂时代为生成输入）
    prepare_b_draft(root, ev)
    prepare_b_mdfixer(root, ev)

    ev.observe("EVIDENCE_DIR", str(work), "本次运行的证据目录")
    ev.save()
    print(f"EVIDENCE_DIR={work}")


if __name__ == "__main__":
    main()