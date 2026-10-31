# DevOps 实验 A 组仓库

本仓库是 DevOps 教学实验 **A 组**（A03）的成果仓库。E1—E4 成果按轮次目录
归档；自 E5 起，仓库根目录是 A 轨道（BuildChecker）E5—E7 云主机实验的
工作区：全组共用 main 上的课程参考实现，个人工作在 `student/<学号>/e5-e7`
分支上进行，通过 PR 合并回 main。

## E5—E7 工作区（仓库根目录）

- 可运行的教学参考实现（已含 E6/E7 代码），统一入口：`python3 scripts/course.py`
  （子命令 `doctor / build / e5 / e6 / gate`，镜像名 `course1027-buildchecker:<学号>`）。
- 操作手册见课程包 `DevOps_E4_E7_GitHub`（03_E5论文复现 / 04_E6核心实现 / 05_E7验证与CI）。
- `work/` 为个人运行证据，不提交；`course-support/` 内含 CI 配置与报告模板。
- E4 及更早阶段的 Makefile/Compose 命令属于旧阶段接口；E5 起优先使用 course.py，
  避免与 E4 镜像标签混用。
- `.github/workflows/e7-quality-gate.yml` 供 E7 GitHub Actions 使用。
- 阶段进度：**E5 已完成**（2026-10-31，四人均交付并合并）。阶段说明、成员成果索引与
  事件记录见 [docs/e5/README.md](docs/e5/README.md)；个人成果在各 `docs/<学号>/` 目录。

## 分支约定

| 分支 | 内容 | 状态 |
|---|---|---|
| `main` | 实验成果主线（课程参考实现 + 全员合并成果） | 默认分支 |
| `e2` `e3` `e4` | E2—E4 阶段成果分支（已完成） | 保留 |
| `e5-reference-import` | E5—E7 课程参考模板一次性导入 | 合并后保留 |
| `student/<学号>/e5-e7` | 每位成员的 E5—E7 个人分支 | 长期使用 |

> E1—E4 各轮成果同时保留在 main 对应目录（`e2-a03/ e3-a03/ e4-a03/`），互不覆盖。

## 组队信息

| 字段 | 值 |
|---|---|
| A 组编号 | A03（配对 B03，鼓楼校区） |
| A 组联系人 | 唐一心（241250061） |
| B 组联系人 | 王宇晗（241250086） |
| A 组仓库 | https://github.com/tang-yixin/devops_lab_a03.git |
| B 组仓库 | https://github.com/Wangyuhan29/b-group-project.git |
| 目标项目 | https://github.com/hardtosleep/Minicalc-DevOps-Test.git |

成员分工详见 `e2-a03/docs/TEAM.md`（成员跨轮次不变，各轮次具体贡献见对应目录的
`docs/CONTRIBUTIONS.md`）。
