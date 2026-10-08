#!/usr/bin/env bash
set -euo pipefail

# 用法：
#   bash linux_trace.sh <工作目录> [关注的头文件名...]
# 示例：
#   bash linux_trace.sh work/20261008-153000/md-rd feature.h config.h

WORKDIR="${1:-.}"
shift || true
HEADERS=("$@")

if [ ${#HEADERS[@]} -eq 0 ]; then
  HEADERS=("feature.h" "config.h")
fi

cd "$WORKDIR"

if [ ! -f Makefile ]; then
  echo "错误：$WORKDIR 下没有 Makefile" >&2
  exit 1
fi

mkdir -p evidence/linux-verified
cd evidence/linux-verified

{
  echo "OS: $(uname -a)"
  echo "CPU: $(uname -m)"
  echo "git: $(git --version 2>/dev/null || echo 'N/A')"
  echo "make: $(make --version 2>/dev/null | head -n1 || echo 'N/A')"
  echo "cc: $(cc --version 2>/dev/null | head -n1 || echo 'N/A')"
  echo "strace: $(strace --version 2>/dev/null | head -n1 || echo 'N/A')"
} > environment.txt

make clean || true
strace -ff -o trace.log -e trace=%file,%process make \
  > make.stdout 2> make.stderr || true

for h in "${HEADERS[@]}"; do
  safe=$(echo "$h" | tr '/.' '__')
  grep -R "$h" trace.log* > "access-${safe}.log" || true
done

make -pn > make-pn.txt 2>&1 || true

echo "证据已保存到: $(pwd)"