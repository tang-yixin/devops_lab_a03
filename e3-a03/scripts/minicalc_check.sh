#!/bin/bash
set -u
SRC=/mnt/d/DevOps/Minicalc-DevOps-Test
D=/tmp/e3-minicalc-a03
rm -rf "$D"
git clone -q "$SRC" "$D"
cd "$D"

for TAG in c0 c1 c2; do
  echo "==================== $TAG ===================="
  git checkout -q "$TAG"
  SHA=$(git rev-parse HEAD)
  echo "commit full SHA = $SHA"
  echo "--- make clean ---"
  make clean
  echo "make clean exit=$?"
  echo "--- make (full build) ---"
  make
  echo "make exit=$?"
  echo "--- functional test: make test ---"
  make test
  echo "make test exit=$?"
  echo ""
done

echo "==================== MD/RD 行为观察（基于 c0） ===================="
git checkout -q c0
make clean >/dev/null 2>&1
make >/dev/null 2>&1
echo "c0 clean build done, app output check:"
./minicalc "1+2*3"

# MD 演示：改 util.h（main.o 实际依赖但未声明），make 应不重建 main.o
echo "--- MD: 改 include/util.h 后 make（预期 main.o 不重建） ---"
touch include/util.h
make
echo "--- RD: 改 include/legacy.h 后 make（预期 util.o 被多余重建） ---"
touch include/legacy.h
make
echo "done"
