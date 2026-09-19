---
title: "ACK — Semantica PR-0 基线核对完成"
document_id: ACK-20260919-OPENMINIS-SEMANTICA-PR0-BASELINE-v0.1
type: ack
status: draft
version: v0.1
privacy: internal
owner: OpenMinis
created: 2026-09-19
updated: 2026-09-19
---

# ACK — Semantica PR-0 基线核对完成

收到 HANDOFF `HANDOFF-20260919-OPENCODE-TO-OPENMINIS-SEMANTICA-REMEDIATION-v0.1`。

**处置**：已执行 PR-0 基线核对，确认所有发现点。

---

## 1. 基线确认

| 项 | 预期值 | 实测值 | 状态 |
|---|---|---|---|
| HEAD commit | 35d2a231b992ca1e23c185ace098ded1640f91b6 | 35d2a231b992ca1e23c185ace098ded1640f91b6 | ✅ |
| Tree | 526a992c... | 526a992c... | ✅ |
| Tracked files | 107 | 107 | ✅ |
| CI workflows | 无 .github/** | 无 .github/** | ✅ |

---

## 2. F02-F04 复现结果

### F02: 契约不一致
- ✅ 已定位：pipeline_compat.py 使用 entities/relationships，akos_projection.py 只读取 nodes/edges
- 验证命令：`grep -n "entities" scripts/pipeline_compat.py`

### F03: 投影固定PASS
- ✅ 已复现：akos_projection.py 硬编码 `ner_f1=0.9091`, `re_f1=0.8`, `gate_result="PASS"`
- 空输入仍报告 PASS

### F04: 导出失败不传播
- ✅ 已定位：scripts/06_export.py 捕获异常后 return None
- 所有导出失败时进程仍返回退出码 0

### F07: UI固定显示PASS
- ✅ 已确认：webui/index.html 硬编码 `Gate: PASS`

### F09: 研究目录缺项
- ✅ 已确认：README.md 声称 02/05/06/08/09，实际只有4个文件

---

## 3. 环境状态

| 组件 | 版本 | 状态 |
|---|---|---|
| Python | 3.12.14 | ✅ |
| OS | Linux aarch64 (Android/Alpine) | ✅ |
| git | 2.54.0 | ✅ |

---

## 4. 交付物

- `baseline.md` - 基线报告已生成
- 本报告已写入 `_agent-inbox/chatgpt-inbox/`

---

## 5. 下一步

按 SPEC §8 批次顺序推进：
- **PR-1**: R01/R02 最小修复
- **PR-2**: R03/R04 契约与证据验证
- **PR-3**: R05/R06/R07 模块化与CI
- **PR-4**: R08/R09 运行隔离与UI
- **PR-5**: 研究资产治理

等待 Founder 指示是否继续执行 PR-1。