#!/usr/bin/env python3
import shutil
from pathlib import Path
from utils import Evidence, read_json


def load_mapping(root: Path) -> dict:
    return read_json(root / "config" / "e2_mapping.json")


def prepare_a_commits(root: Path, ev: Evidence):
    src = root / "fixtures" / "commits"
    if not src.exists():
        ev.observe("A_COMMITS", "跳过", "fixtures/commits 不存在")
        return

    mapping = load_mapping(root)
    ga = mapping["group_a"]
    build = ga["build_cmd"]
    run = ga["run_cmd"]
    clean = ga["clean_cmd"]

    work = ev.workdir / "commits"
    if work.exists():
        shutil.rmtree(work)
    shutil.copytree(src, work)

    expected_path = work / "EXPECTED.json"
    expected = read_json(expected_path) if expected_path.exists() else {}

    for name in ("C0", "C1", "C2"):
        d = work / name
        if not d.exists():
            ev.observe(f"A_{name}", "缺失", f"{d} 不存在")
            continue
        ev.run(clean, cwd=d)
        ev.run(build, cwd=d)
        ev.run(run, cwd=d)
        ev.observe(f"A_{name}", "运行完成", str(expected.get(name, {})))