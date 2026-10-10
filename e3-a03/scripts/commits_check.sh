#!/bin/bash
set -u
# 可移植路径：脚本所在目录 → e3-a03 目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
E3_DIR="$(dirname "$SCRIPT_DIR")"
SRC="$E3_DIR/fixtures/commits"
D=/tmp/e3-commits-a03
rm -rf "$D"
mkdir -p "$D"
cd "$D"
git init -q
git config user.email "a03@example.com"
git config user.name "A03"

# ---- C0: 声明正确 ----
cp "$SRC/c0"/* .
git add -A && git commit -qm "C0: baseline (declared correctly)"
git tag c0
make clean >/dev/null 2>&1
make >/dev/null 2>&1
echo "C0 clean build app output = $(./app)"

# ---- C1: 新增 include feature.h，未补 Makefile 依赖 ----
cp "$SRC/c1"/main.c "$SRC/c1"/feature.h .
git add -A && git commit -qm "C1: add feature.h include (missing decl)"
git tag c1
make >/dev/null 2>&1
echo "C1 incremental app output = $(./app)"
make clean >/dev/null 2>&1 && make >/dev/null 2>&1
echo "C1 clean build app output = $(./app)"
# 只改 feature.h，验证漏重建（证明 main.o 缺 feature.h 声明）
sed -i 's/#define FEATURE 2/#define FEATURE 20/' feature.h
make
echo "C1 after edit feature.h only, make output (expect up-to-date): app = $(./app)"
git checkout -- feature.h

# ---- C2: 只改编译命令 -DMODE=7，源码保持 C1 ----
cp "$SRC/c2"/Makefile .
git add -A && git commit -qm "C2: change CFLAGS only (-DMODE=7)"
git tag c2
make
echo "C2 incremental (kept C1 artifacts) app output = $(./app)"
make clean >/dev/null 2>&1 && make >/dev/null 2>&1
echo "C2 clean build app output = $(./app)"

echo "---- git log ----"
git log --oneline --decorate
