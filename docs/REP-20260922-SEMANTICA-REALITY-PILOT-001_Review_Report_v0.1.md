---
document_id: REP-20260922-SEMANTICA-REALITY-PILOT-001
type: review_report
title: "Semantica Reality Pilot 001 — One-Way Leasing 业务验证报告"
version: v0.1
status: Review
owner: Founder
executor: Codex
created: 2026-09-22
updated: 2026-09-22
privacy: internal
ticket_id: "https://github.com/cliffordzhangcheng/semantica-project/issues/3"
artifact_relation: evidence_for
source_of_truth: "GitHub Issue #3"
related_documents:
  - REP-20260922-SEMANTICA-REALITY-PILOT-001-EVIDENCE-AUDIT
---

# Semantica Reality Pilot 001 — One-Way Leasing 业务验证报告

## 审阅结论

**REALITY_PILOT_001_PASS_CANDIDATE — PENDING_BUSINESS_REVIEW_AND_FOUNDER_G7**

本轮验证的是一个受限的真实业务边界，不是生产放行，也不表示财务结清。

案例被稳定识别为：`ONE-N524 / ONE524SGH / CW202602001`，共 **26×20HC**，起始场站 `CNSGHMJ1`，目的地业务记录为 `PLGDNDCT`，还箱授权地点为 Tradecon Tuchom。Founder 已确认该身份、Tuchom 授权地点，以及全批26柜截至 2026-07-16 已 off-hire、无长期未还设备。

## 已复核的原始资料

| 资料 | 直接支持的事实 | 处理方式 |
|---|---|---|
| `Invoice-ONEN524SGH 2026.02.25.xlsx`、`PI-ONEN524SGH 2026.04.09.xlsx` | 26个逐柜箱号、每柜20HC、合同/booking/PO、CNSGHMJ1 | 纳入案例身份与箱型证据 |
| `container tracing.xlsx` | RLGU2503769：2026-01-29 租赁、2026-02-04 `GATE-OUT EMPTY` | 纳入来源绑定的业务事件 |
| `Gate In status from Owner 2026.05.21.xlsx` | RLGU2503769：2026-04-24 gate-in；其余逐柜 gate-in 状态 | 仅记录 gate-in，不自动等同 off-hire |
| Lak Phen 第20周周报附件 | ONE-N524 逐柜活动、`SIZE=20`、`HEIGHT=9 6`、出场/卸船/入场记录 | 交叉验证箱型和活动时间线 |
| `ERI TRDC26X20HCMAR-26.pdf` | 同一26箱清单及 Tradecon Tuchom redelivery instruction | 证明还箱授权地点，不证明每柜实物入场 |
| EMR、Per Diem、Debit Note | RLGU2503711 于 2026-05-13 off-hire；费用与维修事项 | 记录受支持的单柜 off-hire 和费用事实 |
| Founder 2026-09-22 业务确认 | 26柜均已于 2026-07-16 off-hire，无长期未还设备 | 作为 Founder 业务证明保存，不伪装成堆场 EIR |

原件未上传至 GitHub。受控语料只保存必要事实、原文件哈希和定位，见 `data/raw/reality-pilot-001-evidence.json`。

## 运行时事实边界

系统生成 10 条来源绑定、仅精确到“日”的业务事件。不会把 Excel 默认的午夜转成事件时分秒，也不会推断未被资料显示的状态。

可独立复核的状态推进包括：

1. `RLGU2503769: LEASED → GATE_OUT_EMPTY → GATE_IN_RECORDED`
2. `RLGU2503814: LEASED → GATE_OUT_FULL`
3. `RLGU2503711: GATE_IN_EMPTY → OFF_HIRE_RECORDED`

全批26柜的 2026-07-16 off-hire 是 Founder 确认的批次级事件，不被错误表示成每柜都有堆场 EIR。

## 门禁与复现结果

| 门禁 | 结果 | 含义 |
|---|---|---|
| GR / GC / GA / GSYNC | PASS | 关系、主张、工件和跨运行一致性通过 |
| GEVENT | PASS | 所有业务事件都有来源和定位 |
| GSTATE | PASS | 状态推进都有事件支撑；无孤立迁移 |
| GTIME | PASS | 时间线按来源日精度确定性重建；拒绝伪造时间戳 |
| G6 | PASS | 满足受限真实案例的实体、事件、状态和时间线最低条件 |
| GDET | PASS | 两次独立干净重建的案例实体、事件、状态迁移、时间线、业务图哈希一致 |

本分支当前提交：`c2ce9ec6db5e79ebd0fd28a23d786712e0abdc79`。本地 128 项测试通过；分支 CI 通过并上传复验证据。

## 明确不作出的主张

- 不主张已收到付款；
- 不主张 `SETTLED` 或 `CLOSED`；
- 不将 `GATE-IN` 自动当作 `OFF-HIRE`；
- 不把 Founder 的批次确认改写为逐柜堆场原件；
- 不把本案专属事实提升为通用 ontology relation。

## Founder G7 待决事项

若 Founder 接受上述受限业务边界、证据解释和不作出的主张，可明确批准 Founder G7。该批准只允许该工程基线进入下一阶段业务 ontology 验证；仍不代表生产上线或财务结案。PR #4 保持 draft，未经明确 merge 指令不合并 main。
