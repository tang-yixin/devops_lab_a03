# 预期结果汇总

## A 组

| 版本/场景 | 人工预期发现 | 程序行为 |
|---|---|---|
| MD/RD 第一次构建 | MD: config.h；RD: unused.h | 与 E2 报告一致 |
| 只改 config.h | MD 导致旧产物 | 增量输出旧值 |
| clean build | 完整重建 | 输出新值 |
| 修改 unused.h | RD 导致多余编译 | 重新出现 cc 命令 |
| C0 | 无 MD/RD | clean = 10 |
| C1 | MD: main.o -> feature.h | clean = 12 |
| C2 | 上述 MD 仍存在 | 增量 = 12；clean = 19 |

## B 组

| 场景 | 预期 |
|---|---|
| Dockerfile.broken | 构建非零退出，`make: not found` |
| Dockerfile.reference | 构建成功，运行输出与 E2 报告一致 |
| MDFixer 参考补丁 | 再次改头文件后输出新值 |
| MDFixer 无效补丁 | make 非零退出，恢复后再次通过 |