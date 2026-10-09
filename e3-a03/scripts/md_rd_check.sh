#!/bin/bash
set -u
SRC=/mnt/d/DevOps/devops_lab_a03/e3-a03/fixtures/md-rd
D=/tmp/e3-md-rd-a03
rm -rf "$D"
mkdir -p "$D"
cp "$SRC"/* "$D"/
cd "$D"

echo "=== STEP4: first full build ==="
make
echo "make exit=$?"
echo "--- run app ---"
./app
echo "app exit=$?"

echo "=== STEP5: edit config.h to VALUE 2, incremental build (expect stale 1) ==="
sed -i 's/#define VALUE 1/#define VALUE 2/' config.h
sleep 1
touch config.h
make
echo "make exit=$?"
echo "--- run app (expect 1, stale) ---"
./app
echo "app exit=$?"

echo "=== STEP6: clean build (expect 2) ==="
make clean
make
echo "--- run app (expect 2) ---"
./app
echo "app exit=$?"

echo "=== STEP7: edit unused.h comment only, make (expect recompile) ==="
sed -i 's/REDUNDANT/REDUNDANT-mark/' unused.h
make
echo "make exit=$?"
