#!/usr/bin/env python3
"""E2 A 组最小契约校验。

用法:
    python tools/validate.py <file.json> [...]

对请求样例做结构校验，对 Job 响应样例做统一任务模型校验。
退出码 0 表示全部通过，1 表示存在失败项。
"""
import json
import sys
from pathlib import Path

ALLOWED_JOB_TYPES = {"DRAFT", "FULL_CHECK", "INCREMENTAL_CHECK", "REPAIR"}
ALLOWED_STATUS = {
    "QUEUED", "RUNNING", "SUCCEEDED", "FAILED", "TIMED_OUT", "CANCELLED",
}
ALLOWED_ERROR_CODES = {"ENV_3002", "EXEC_4002", "ANALYSIS_5001", "REQUEST_4001"}
ALLOWED_FINDING_TYPES = {"MISSING", "REDUNDANT"}

# 每类请求的必填输入字段
REQUIRED_INPUT = {
    "DRAFT": ["repository", "build"],
    "FULL_CHECK": ["repository", "environment", "build"],
    "INCREMENTAL_CHECK": ["repository", "base_commit", "baseline", "environment", "build"],
    "REPAIR": ["repository", "error_report", "environment", "build"],
}

# 每类请求中，input 子对象里的必填键
REQUIRED_SUBKEYS = {
    "repository": ["url", "commit"],
    "environment": ["image", "configuration_id"],
    "build": ["clean_build_command", "project_root"],
    "baseline": ["actual_graph_uri", "commit", "configuration_id"],
    "error_report": ["uri"],
}

_failures = []


def fail(msg):
    _failures.append(msg)
    print(f"[FAIL] {msg}")


def ok(msg):
    print(f"[PASS] {msg}")


def load(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception as e:
        fail(f"无法读取/解析 {path}: {e}")
        return None


def check_subkeys(obj, parent, keys, label):
    for key in keys:
        if key not in obj:
            fail(f"{label} 缺少 {parent}.{key}")


def validate_request(obj, label):
    jt = obj.get("job_type")
    if jt not in ALLOWED_JOB_TYPES:
        fail(f"{label}: 非法 job_type: {jt}")
        return

    inp = obj.get("input")
    if not isinstance(inp, dict):
        fail(f"{label}: 缺少 input 对象")
        return

    for key in REQUIRED_INPUT[jt]:
        if key not in inp:
            fail(f"{label}: {jt} 缺少 input.{key}")

    for key in REQUIRED_INPUT[jt]:
        if key in inp and key in REQUIRED_SUBKEYS:
            if not isinstance(inp[key], dict):
                fail(f"{label}: input.{key} 必须是对象")
                continue
            check_subkeys(inp[key], f"input.{key}", REQUIRED_SUBKEYS[key], label)

    # 增量检测的基线一致性
    if jt == "INCREMENTAL_CHECK" and "baseline" in inp and "base_commit" in inp:
        baseline = inp["baseline"]
        if isinstance(baseline, dict):
            if baseline.get("commit") != inp["base_commit"]:
                fail(f"{label}: baseline.commit 必须等于 base_commit")
            env = inp.get("environment")
            if isinstance(env, dict) and baseline.get("configuration_id") != env.get("configuration_id"):
                fail(f"{label}: baseline.configuration_id 必须等于 environment.configuration_id")

    if not _failures:
        ok(f"{label}: 请求通过 A 组最小校验")


def validate_finding(finding, label, where):
    if not isinstance(finding, dict):
        fail(f"{label}: {where} 必须是对象")
        return
    for key in ["type", "target", "dependency", "commit", "detector"]:
        if key not in finding:
            fail(f"{label}: {where} 缺少 {key}")
    if finding.get("type") not in ALLOWED_FINDING_TYPES:
        fail(f"{label}: {where}.type 非法: {finding.get('type')}")


def validate_job(obj, label):
    for key in ["schema_version", "job_id", "trace_id", "job_type", "status"]:
        if key not in obj:
            fail(f"{label}: Job 缺少 {key}")

    if obj.get("job_type") not in ALLOWED_JOB_TYPES:
        fail(f"{label}: Job 非法 job_type: {obj.get('job_type')}")

    status = obj.get("status")
    if status not in ALLOWED_STATUS:
        fail(f"{label}: Job 非法 status: {status}")

    # 系统错误与检测发现分离：终态失败必须有 error，成功不得有 error
    error = obj.get("error")
    if status in {"FAILED", "TIMED_OUT"}:
        if not isinstance(error, dict):
            fail(f"{label}: status={status} 时 error 必须存在")
        elif error.get("code") not in ALLOWED_ERROR_CODES:
            fail(f"{label}: 非法 error.code: {error.get('code')}")
    elif status == "SUCCEEDED" and error is not None:
        fail(f"{label}: status=SUCCEEDED 时 error 必须为 null")

    output = obj.get("output")
    if status == "SUCCEEDED" and isinstance(output, dict):
        for finding in output.get("findings", []):
            validate_finding(finding, label, "output.findings[]")
        for finding in output.get("added_findings", []):
            validate_finding(finding, label, "output.added_findings[]")

    if not _failures:
        ok(f"{label}: Job 通过统一任务模型校验")


def classify(obj):
    """请求样例带 input 且无 job_id；Job 响应样例带 job_id。"""
    if "job_id" in obj:
        return "job"
    return "request"


def main():
    if len(sys.argv) < 2:
        fail("用法: python tools/validate.py <file.json> [...]")
        sys.exit(1)

    for path in sys.argv[1:]:
        obj = load(path)
        if obj is None:
            continue
        label = Path(path).name
        kind = classify(obj)
        if kind == "job":
            validate_job(obj, label)
        else:
            validate_request(obj, label)

    print()
    if _failures:
        print(f"共 {len(_failures)} 项失败")
        sys.exit(1)
    print("全部通过")


if __name__ == "__main__":
    main()
