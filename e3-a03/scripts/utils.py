#!/usr/bin/env python3
import json
import shutil
import subprocess
import time
from pathlib import Path


class Evidence:
    def __init__(self, workdir):
        self.workdir = Path(workdir)
        self.workdir.mkdir(parents=True, exist_ok=True)
        self.commands = []
        self.observations = []

    def run(self, cmd, cwd=None, env=None, check=False, timeout=120):
        cwd_path = Path(cwd) if cwd else None
        rec = {"cmd": cmd, "cwd": str(cwd_path) if cwd_path else None, "start": time.time()}
        try:
            p = subprocess.run(
                cmd, cwd=cwd_path, env=env, shell=isinstance(cmd, str),
                text=True, capture_output=True, timeout=timeout,
            )
            rec.update({"returncode": p.returncode, "stdout": p.stdout, "stderr": p.stderr})
            if check and p.returncode != 0:
                raise RuntimeError(f"命令失败: {cmd}\n{p.stderr}")
        except Exception as e:
            rec.update({"returncode": None, "stdout": "", "stderr": "", "error": str(e)})
            if check:
                raise
        finally:
            rec["end"] = time.time()
            self.commands.append(rec)
        return rec

    def run_shell(self, script, cwd=None, args=None, check=False, timeout=300):
        """
        调用外部 shell 脚本，例如 linux_trace.sh。
        script: 脚本路径
        cwd: 工作目录（样例目录，脚本会在其下生成 evidence/linux-verified/）
        args: 传给脚本的额外参数列表
        """
        cmd = ["bash", str(script)] + [str(a) for a in (args or [])]
        return self.run(cmd, cwd=cwd, check=check, timeout=timeout)

    def observe(self, key, value, note=""):
        self.observations.append({"key": key, "value": value, "note": note})

    def save(self):
        (self.workdir / "commands.json").write_text(
            json.dumps(self.commands, indent=2, ensure_ascii=False), encoding="utf-8")
        (self.workdir / "observations.json").write_text(
            json.dumps(self.observations, indent=2, ensure_ascii=False), encoding="utf-8")


def write_file(path, content):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def copy_if_exists(src, dst):
    src, dst = Path(src), Path(dst)
    if not src.exists():
        return False
    if src.is_dir():
        shutil.copytree(src, dst, dirs_exist_ok=True)
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    return True