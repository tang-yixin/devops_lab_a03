# strace 原始跟踪证据（Minicalc c0，WSL Ubuntu x86_64）

生成时间：2026-10-09T13:01:18Z

## 构建命令输出（make.stdout）
```
gcc -std=c11 -Wall -Wextra -Iinclude -g -c src/main.c -o main.o
gcc -std=c11 -Wall -Wextra -Iinclude -g -c src/parser.c -o parser.o
gcc -std=c11 -Wall -Wextra -Iinclude -g -c src/token.c -o token.o
gcc -std=c11 -Wall -Wextra -Iinclude -g -c src/util.c -o util.o
gcc -std=c11 -Wall -Wextra -Iinclude -g main.o parser.o token.o util.o -o minicalc
```

## make -pn 中 .o 声明规则
```
815:parser.o: src/parser.c include/parser.h
832:util.o: src/util.c include/util.h include/legacy.h
1127:main.o: src/main.c include/config.h include/parser.h
1296:token.o: src/token.c include/token.h
```

## 各 trace 文件对应进程
```
trace.log.442 -> /usr/bin/make
trace.log.443 -> /usr/bin/gcc
trace.log.444 -> /usr/lib/gcc/x86_64-linux-gnu/11/cc1
trace.log.445 -> /usr/local/sbin/as
trace.log.446 -> /usr/bin/gcc
trace.log.447 -> /usr/lib/gcc/x86_64-linux-gnu/11/cc1
trace.log.448 -> /usr/local/sbin/as
trace.log.449 -> /usr/bin/gcc
trace.log.450 -> /usr/lib/gcc/x86_64-linux-gnu/11/cc1
trace.log.451 -> /usr/local/sbin/as
trace.log.452 -> /usr/bin/gcc
trace.log.453 -> /usr/lib/gcc/x86_64-linux-gnu/11/cc1
trace.log.454 -> /usr/local/sbin/as
trace.log.455 -> /usr/bin/gcc
trace.log.456 -> /usr/lib/gcc/x86_64-linux-gnu/11/collect2
trace.log.457 -> /usr/bin/ld
```

## 头文件访问分类（newfstatat = make 检查状态；openat = 编译器实际读取）
```
--- config.h ---
stat(状态检查)次数: 1
openat(实际读取)次数: 1
openat(AT_FDCWD, "include/config.h", O_RDONLY|O_NOCTTY) = 4
--- parser.h ---
stat(状态检查)次数: 3
openat(实际读取)次数: 2
openat(AT_FDCWD, "include/parser.h", O_RDONLY|O_NOCTTY) = 4
openat(AT_FDCWD, "include/parser.h", O_RDONLY|O_NOCTTY) = 4
--- token.h ---
stat(状态检查)次数: 3
openat(实际读取)次数: 3
openat(AT_FDCWD, "include/token.h", O_RDONLY|O_NOCTTY) = 4
openat(AT_FDCWD, "include/token.h", O_RDONLY|O_NOCTTY) = 4
openat(AT_FDCWD, "include/token.h", O_RDONLY|O_NOCTTY) = 4
--- util.h ---
stat(状态检查)次数: 3
openat(实际读取)次数: 2
openat(AT_FDCWD, "include/util.h", O_RDONLY|O_NOCTTY) = 4
openat(AT_FDCWD, "include/util.h", O_RDONLY|O_NOCTTY) = 4
--- legacy.h ---
stat(状态检查)次数: 1
openat(实际读取)次数: 0
```
