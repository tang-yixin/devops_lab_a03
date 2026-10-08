#!/usr/bin/env python3
import json
import shutil
from pathlib import Path
from utils import Evidence, write_file, read_json


def load_mapping(root: Path) -> dict:
    return read_json(root / "config" / "e2_mapping.json")


def prepare_md_rd(root: Path, ev: Evidence):
    fixture = root / "fixtures" / "md-rd"
    if not (fixture / "src").exists():
        ev.observe("A_MD_RD", "跳过", "fixtures/md-rd/src 不存在，请先运行 prepare_from_e2")
        return

    mapping = load_mapping(root)
    ga = mapping["group_a"]
    build = ga["build_cmd"]
    run = ga["run_cmd"]
    clean = ga["clean_cmd"]

    work = ev.workdir / "md-rd"
    if work.exists():
        shutil.rmtree(work)
    shutil.copytree(fixture, work)

    # 第一次完整构建
    ev.run(build, cwd=work)
    ev.run(run, cwd=work)

    # 修改头文件：从 ORACLE_findings.json 读取 MISSING 目标
    oracle_path = work / "ORACLE_findings.json"
    if oracle_path.exists():
        oracle = read_json(oracle_path)
        findings = oracle.get("findings", [])
    else:
        findings = []
        ev.observe("A_MD_RD", "无 ORACLE", "ORACLE_findings.json 不存在")

    missing = [f for f in findings if f.get("type") == "MISSING"]
    if missing:
        dep = missing[0]["dependency"]
        # 尝试在 src/ 下寻找该头文件
        candidates = list((work / "src").rglob(dep))
        if candidates:
            header = candidates[0]
            text = header.read_text(encoding="utf-8")
            write_file(header, text + "\n/* E3 modified */\n")
            ev.run(build, cwd=work)
            ev.run(run, cwd=work)
        else:
            ev.observe("A_MD_RD", "未找到头文件", dep)

    # clean build 对照
    ev.run(clean, cwd=work)
    ev.run(build, cwd=work)
    ev.run(run, cwd=work)

    ev.observe(
        "A_MD_RD", "完成",
        f"来源: {fixture}，ORACLE findings: {len(findings)}"
    )