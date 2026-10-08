#!/usr/bin/env python3
"""
从 e2-a03 派生 E3 fixtures。
E2 是契约与真实数据来源，E3 是测试基线。
本脚本不改动 E2，只读 + 复制。
"""
import json
from pathlib import Path
from utils import read_json, copy_if_exists, write_file


def load_mapping(root: Path) -> dict:
    cfg = root / "config" / "e2_mapping.json"
    if not cfg.exists():
        raise FileNotFoundError(f"缺少 {cfg}，请先填写 E2 映射。")
    return read_json(cfg)


def resolve(e2_root: Path, rel: str) -> Path:
    return (e2_root / rel).resolve()


def derive_md_rd(root: Path, mapping: dict, e2_root: Path):
    """A 组 MD/RD：从 E2 minicalc c0 派生，契约来自 E2 schemas。"""
    dst = root / "fixtures" / "md-rd"
    dst.mkdir(parents=True, exist_ok=True)

    ga = mapping["group_a"]
    # 复制 c0 源码与 Makefile
    copy_if_exists(resolve(e2_root, ga["source_root"]), dst / "src")
    copy_if_exists(resolve(e2_root, ga["makefile"]), dst / "Makefile")

    # 复制 E2 的人工 ORACLE 报告（md-only-report-c0.json）
    oracle_src = resolve(e2_root, ga["oracle_report"])
    if oracle_src.exists():
        copy_if_exists(oracle_src, dst / "ORACLE_findings.json")
    else:
        write_file(dst / "ORACLE_findings.json", json.dumps({
            "provenance": "INSTRUCTOR_ORACLE",
            "note": "等待 E2 提供 md-only-report-c0.json",
            "findings": []
        }, indent=2, ensure_ascii=False))

    # 复制 E2 契约，供 E3 检测结果对齐
    copy_if_exists(resolve(e2_root, mapping["e2_schemas"]["graph"]),
                   dst / "graph.schema.json")
    copy_if_exists(resolve(e2_root, mapping["e2_schemas"]["finding_id"]),
                   dst / "finding-id-v1.json")


def derive_commits(root: Path, mapping: dict, e2_root: Path):
    """A 组 C0/C1/C2：直接引用 E2 的 minicalc artifacts。"""
    dst_root = root / "fixtures" / "commits"
    dst_root.mkdir(parents=True, exist_ok=True)

    for name, info in mapping["commits"].items():
        art = resolve(e2_root, info["artifact_dir"])
        dst = dst_root / name
        if art.exists():
            copy_if_exists(art, dst)
        else:
            write_file(dst / "MISSING.txt",
                       f"E2 中不存在 {info['artifact_dir']}，请先补齐 E2 的 Minicalc C0/C1/C2 产物。\n")

    # 生成 EXPECTED.json，供 EChecker 对照
    expected = {
        name: {k: v for k, v in info.items() if k != "artifact_dir"}
        for name, info in mapping["commits"].items()
    }
    write_file(dst_root / "EXPECTED.json",
               json.dumps(expected, indent=2, ensure_ascii=False))


def derive_draft(root: Path, mapping: dict, e2_root: Path):
    """B 组 DRAFT：以 E2 minicalc 为项目，E2 错误报告为失败样例依据。"""
    dst = root / "fixtures" / "draft"
    dst.mkdir(parents=True, exist_ok=True)

    ga = mapping["group_a"]
    # 复制 minicalc 源码与 Makefile 作为可构建项目
    copy_if_exists(resolve(e2_root, ga["source_root"]), dst / "src")
    copy_if_exists(resolve(e2_root, ga["makefile"]), dst / "Makefile")

    # 写 README（说明构建与验证命令，来自 E2）
    gb = mapping["group_b"]
    write_file(dst / "README.md", f"""# Minicalc DRAFT 样本

来源：E2 `{ga['source_root']}`

构建：`{' '.join(ga['build_cmd'])}`
验证：`{' '.join(ga['run_cmd'])}`
""")

    # 失败候选：基于 E2 错误报告
    err = resolve(e2_root, gb["error_report"])
    if err.exists():
        copy_if_exists(err, dst / "error-report.json")

    # 生成参考与失败 Dockerfile（沿用 E3 模板，但项目指向 minicalc）
    write_file(dst / "Dockerfile.broken", """FROM python:3.13-slim
WORKDIR /work
COPY . /work
RUN make
CMD ["./minicalc"]
""")
    write_file(dst / "Dockerfile.reference", """FROM python:3.13-slim
WORKDIR /work
COPY . /work
RUN apt-get update && \\
    apt-get install -y --no-install-recommends gcc make libc6-dev && \\
    rm -rf /var/lib/apt/lists/* && \\
    make
CMD ["./minicalc"]
""")


def derive_mdfixer(root: Path, mapping: dict, e2_root: Path):
    """B 组 MDFixer：以 E2 finding 格式与 repair-request 为固定输入。"""
    dst = root / "fixtures" / "mdfixer"
    dst.mkdir(parents=True, exist_ok=True)

    gb = mapping["group_b"]
    # 从 E2 复制修复请求、报告，作为固定输入
    for key in ("repair_request", "full_request", "full_response",
                "incremental_request", "incremental_response"):
        src = resolve(e2_root, gb.get(key, ""))
        if src.exists():
            copy_if_exists(src, dst / f"{key}.json")

    # 复制 finding-id 契约，供 MDFixer 输出对齐
    copy_if_exists(resolve(e2_root, mapping["e2_schemas"]["finding_id"]),
                   dst / "finding-id-v1.json")

    # 若 E2 提供 reference/invalid 补丁则复制，否则留空占位
    for name in ("reference.patch", "invalid.patch", "Makefile.before"):
        if not (dst / name).exists():
            write_file(dst / name, f"# 等待 B 组或 E2 提供 {name}\n")


def prepare_from_e2(root: Path):
    mapping = load_mapping(root)
    e2_root = resolve(root, mapping["e2_root"])
    if not e2_root.exists():
        raise FileNotFoundError(f"找不到 E2 根目录: {e2_root}")

    derive_md_rd(root, mapping, e2_root)
    derive_commits(root, mapping, e2_root)
    derive_draft(root, mapping, e2_root)
    derive_mdfixer(root, mapping, e2_root)

    print(f"[E3] 已从 {e2_root} 派生 fixtures")