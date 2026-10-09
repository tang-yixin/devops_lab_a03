#!/bin/bash
set -u
# 可移植路径：脚本所在目录 → e3-a03 → 仓库根
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
E3_DIR="$(dirname "$SCRIPT_DIR")"
REPO_DIR="$(dirname "$E3_DIR")"
# Minicalc 仓库：优先环境变量 MINICALC_REPO，默认仓库同级目录
SRC="${MINICALC_REPO:-$REPO_DIR/../Minicalc-DevOps-Test}"
EVID="$E3_DIR/evidence/linux-verified"
mkdir -p "$EVID"
D=/tmp/e3-strace-a03
rm -rf "$D"
git clone -q "$SRC" "$D"
cd "$D"
git checkout -q c0
OUT=/tmp/e3-strace-a03-out
rm -rf "$OUT"
mkdir -p "$OUT"

echo "=== 环境 ==="
uname -m
gcc --version | head -1
make --version | head -1
strace --version | head -1

echo "=== make clean 后 strace 跟踪 make ==="
make clean >/dev/null 2>&1
strace -ff -o "$OUT/trace.log" -e trace=%file,%process make > "$OUT/make.stdout" 2>&1
echo "strace exit=$?"

echo "=== make -pn 抓声明依赖 ==="
make -pn > "$OUT/make-pn.txt" 2>&1
echo "make -pn exit=$?"

# ---- 保存关键证据到仓库 ----
{
  echo "# strace 原始跟踪证据（Minicalc c0，WSL Ubuntu x86_64）"
  echo ""
  echo "生成时间：$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  echo "## 构建命令输出（make.stdout）"
  echo '```'
  cat "$OUT/make.stdout"
  echo '```'
  echo ""
  echo "## make -pn 中 .o 声明规则"
  echo '```'
  grep -nE "^(main|parser|token|util)\.o:" "$OUT/make-pn.txt"
  echo '```'
  echo ""
  echo "## 各 trace 文件对应进程"
  echo '```'
  for f in "$OUT"/trace.log.*; do
    pid=$(basename "$f")
    exe=$(grep -m1 "execve" "$f" | sed 's/.*execve("//;s/".*//')
    echo "$pid -> $exe"
  done
  echo '```'
  echo ""
  echo "## 头文件访问分类（newfstatat = make 检查状态；openat = 编译器实际读取）"
  echo '```'
  for h in config.h parser.h token.h util.h legacy.h; do
    echo "--- $h ---"
    echo "stat(状态检查)次数: $(grep -h "newfstatat.*$h" "$OUT"/trace.log.* 2>/dev/null | wc -l)"
    echo "openat(实际读取)次数: $(grep -h "openat.*$h.*O_RDONLY" "$OUT"/trace.log.* 2>/dev/null | grep -v ENOENT | wc -l)"
    grep -h "openat.*$h" "$OUT"/trace.log.* 2>/dev/null | grep -v ENOENT | head -3
  done
  echo '```'
} > "$EVID/strace-evidence.md"

echo "已写入 $EVID/strace-evidence.md"
echo "trace 文件数: $(ls -1 "$OUT"/trace.log.* | wc -l)"
