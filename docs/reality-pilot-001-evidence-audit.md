---
document_id: REP-20260922-SEMANTICA-REALITY-PILOT-001-EVIDENCE-AUDIT
type: evidence_audit
title: "Reality Pilot 001 — One-Way Leasing 证据充分性复核"
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
---

# Reality Pilot 001：证据充分性复核

**证据结论：足以建立受限的业务事件与状态时间线；不足以声称已结算或关闭。**

本复核覆盖企业微信邮箱可见邮件、Lak Phen 原始周报附件和 `/Users/mac/New Era/Transworld/Oneway/26x20HC 2026.01.12/` 中的 ONE-N524 专属资料。原件和完整邮件不提交到 GitHub；受控 [evidence manifest](../data/raw/reality-pilot-001-evidence.json) 只保留来源相对路径、SHA-256、必要定位和最小事实。

| 来源 | 能证明的事实 | 不能证明的事实 |
|---|---|---|
| `PI-ONEN524SGH 2026.04.09.xlsx` | ONE-N524 / ONE524SGH / CW202602001；26 个逐箱记录；每箱 `20'HC`；CNSGHMJ1 | 对手方接受、付款已收 |
| `ERI TRDC26X20HCMAR-26.pdf` | 同一26个箱号；Tradecon Tuchom 还箱授权地点 | 实际每箱已在 Tuchom 入场或 off-hire |
| Lak Phen `XIA-2026wk20_Monday.xlsx` | ONE-N524 的17个已观察箱；`SIZE=20`、`HEIGHT=9 6`；逐箱 GATE-OUT、DISCHARG、GATE-IN 及日期 | 未显示的9箱状态；GATE-IN 自动等同 off-hire |
| `TWDN-2026-08001...pdf` | RLGU2503711 记录为 2026-05-13 off-hire；另4箱在 2026-07-16 仍未交还 | 付款、结清或关闭 |
| Founder 2026-09-22 业务确认 | 全部26柜已于 2026-07-16 off-hire，无长期未还设备 | 逐柜堆场 EIR、付款、结清或关闭 |

## 受控业务边界

案例身份为 `CASE-ONE-N524`：26×20HC、CNSGHMJ1、PLGDNDCT、Tradecon Tuchom 还箱指令。运行时只生成来源支持的日精度事件：租赁日期记录、发票开具、GATE-OUT/FULL、DISCHARG/FULL、GATE-IN/EMPTY 和 RLGU2503711 的 off-hire 记录。Excel 单元格显示的午夜不是事件时间，运行产物不会生成时分秒或时区。

有效的逐箱状态推进只有两条：RLGU2503814 的 `LEASED → GATE_OUT_FULL`，以及 RLGU2503711 的 `GATE_IN_EMPTY → OFF_HIRE_RECORDED`。Founder 确认的全批 off-hire 作为独立的批次事件保存，不伪装成逐箱堆场记录。

GEVENT、GSTATE、GTIME 和 G6 通过时只代表上述受限业务边界。任何付款、全批26箱已归还、SETTLED 或 CLOSED 主张仍需要独立来源材料和重新审计。
