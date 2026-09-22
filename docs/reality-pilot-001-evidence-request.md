---
document_id: REP-20260922-SEMANTICA-REALITY-PILOT-001
type: evidence_request
title: "Reality Pilot 001 — One-Way Leasing 一次性证据请求"
version: v0.2
status: Superseded
state: superseded_by_evidence_audit
owner: Founder
executor: Codex
created: 2026-09-22
updated: 2026-09-22
privacy: private
ticket_id: "https://github.com/cliffordzhangcheng/semantica-project/issues/3"
artifact_relation: evidence_for
source_of_truth: "GitHub Issue #3"
next_action: "以受控 evidence manifest 重建并复核 Reality Pilot 001"
trigger_condition: "仅在新增事实或原始资料哈希变化时重新审计"
continuation_owner: Codex
escalation_owner: Founder
---

# Reality Pilot 001：历史证据请求（已被替代）

> 本文件记录 2026-09-22 仓库快照审计的证据缺口。随后获得的 Lak Phen 第20周原始周报与 `/Users/mac/New Era/Transworld/Oneway/26x20HC 2026.01.12/` 中的已核对文件解决了稳定案例身份、箱型、活动和至少两条状态推进所需的最小证据。当前结论见 [evidence audit](reality-pilot-001-evidence-audit.md)；本文件不再表示当前 G6 状态。

**REALITY_PILOT_001_BLOCKED_WITH_EVIDENCE_REQUEST**

唯一任务是 [GitHub Issue #3](https://github.com/cliffordzhangcheng/semantica-project/issues/3)。本文件是该任务的证据请求，不是新 SPEC。审计基线为 `eed15e981c6aa937e2137bcf77f9e5a0a73ab42f`。机器可读清单、源文件 SHA-256 和精确定位见 [readiness matrix](reality-pilot-001-readiness-matrix.json)。

审计覆盖该提交下 `data/`、`corpus/`、`research/` 的全部 77 个跟踪文件，包括 80 条邮件导出记录；没有读取实时邮箱或将仓库之外的材料自动纳入证据。新出现但未跟踪的 forwarder 材料不属于本次审计。结论中的“缺失”仅指本次受审仓库快照，不能推断原邮箱或业务系统也没有材料。

## 1. 先核实同一个真实案例

优先案例摘要为 **26×20'HC，Shanghai → Gdansk/Tuchom**。但 `corpus/cntransworld_emails.jsonl` 第 1 行（UID 1）的正文明确写 **Contract ONE-N524，26×20'GP，Shanghai → Gdansk**。两者有数量/路线相似性，但箱型不一致；该邮件没有证明 Tuchom 堆场关联。`ONE-N524` 只能作为待核实案例编号，不能自动合并成已确认身份。

请提供一页案例索引或现有单据中的对应字段：案例/合同号、26 个箱号或可核对的批次清单、真实 ISO 箱型、起运地、实际还箱堆场、合同双方及各自角色。明确摘要中的 HC 是否误写；若两者不是同一案例，请指定对应的真实批次。不要用 Hapag-Lloyd 报价、其他合同 ONE-N617 或一般 Maersk wish list 补齐本案字段。

## 2. 已有材料的实际强度

| 证据类别 | 状态 | 现有证据与不能证明的内容 |
|---|---|---|
| 业务模式、HL 商业条款 | PRESENT（背景） | 摘要有 90–100 天、per diem、Net 60 和 2026-06-12 跟进；属于 HL 报价，不能移植到本批 Maersk 候选案例。 |
| Wish list / request | PARTIAL | Cosmos 邮件 UID 190 有条件性 corridor 表，有效期叙述到 2026-09-30；不是本批箱的需求或接受通知。不能说只有一句 wish-list 叙述，但也不能当 booking。 |
| Contract / case identity | PARTIAL | 合同名与 ONE-N524 编号可定位，签署条款及批次身份未落库；另有 GP/HC 冲突。 |
| 对手方接受 / booking | MISSING | 无本批箱的接受/booking 原始记录；邮件所说 invoice “booked in our system”是财务入账，不是箱运 booking。 |
| Release / pickup | MISSING | 未找到本批 release/EIR/提箱记录及真实日期。 |
| Transit / operation | PARTIAL | 已完成路线摘要没有 event-level 操作凭据。 |
| Return / off-hire | PARTIAL | UID 1 回述“最后 4 箱于 2026-07-16 归还”；它不是堆场收箱确认，也不能给全部 26 箱补同一天的还箱时间。 |
| Invoice / PUC settlement | PARTIAL | UID 1 有 USD 150×26=3900、借项通知单和其他金额；UID 9 要求拆分租赁/维修发票。PDF 仅见文件名，原件未跟踪。 |
| Payment | PARTIAL | UID 9 的引用邮件叙述已收 USD 6890、余 USD 921.62，但线程混合 ONE-N524 与 ONE-N617，缺本案分摊及对账凭据；不能据此宣布本案 SETTLED/CLOSED。 |

导出质量：相关 CN 邮件正文恰为 2,000 字符，相关 Cosmos 邮件恰为 3,000 字符，且尾部中断，存在截断迹象。UID 17 在 2026 年邮件中写到到期日 `19th Sept'25`，不能擅自改成 2026。邮件发送日期、引用邮件日期、事件发生日期和预计付款日期必须分开。

## 3. 一次性交付的最小材料包

可一次上传已有 `.eml`/`.msg`、PDF、EIR、堆场/业务系统导出；不要求重写业务报告。接受邮件作为证据，但必须保留完整消息、角色、案例关联及明确的发生事实，不能只给摘要或附件文件名。

| 材料 | 为什么需要 | 最低材料 / 可接受替代 | 必须保留字段 |
|---|---|---|---|
| A. 身份与箱型核对（必需） | 先证明是同一个稳定真实案例 | ONE-N524 合同/订单页和箱清单；或双方可核对的批次索引。解释 HC/GP 与 Tuchom 关联 | 案例号、合同/booking 引用、箱号或稳定批次键、数量、ISO 箱型、参与方角色、起运/还箱地点 |
| B. 接受或 booking（必需） | 证明对手方接受了本批操作，提供第一条真实事件 | 对手方接受邮件、booking confirmation、已接受的 release order；须明确“接受”，一般合作描述不够 | 原消息标识/单号、接受方、明确行为、案例/批次引用、实际日期或有证据的时间区间、时区若已知 |
| C. Release / pickup（必需） | 证明箱子确实被交付/提走，不能用报价替代 | 堆场 EIR/gate-out、提箱确认、实际执行的 release 记录或带来源的操作台账 | 单据号、箱/批次关联、堆场、动作已发生标记、实际日期/区间、发出方；分批须保留每批数量 |
| D. Return / off-hire（必需） | 证明收箱及状态推进，并核对最后 4 箱与全批 26 箱 | 堆场 EIR/gate-in、正式 off-hire confirmation 或堆场来源的完整收箱台账 | 收箱地点、箱/批次关联、各批日期/区间、数量、off-hire 接受标记、确认方；覆盖范围不足须明确 |
| E. 报价/合同条款（条件必需） | 若声称本案费率、免箱期、违约费或合同状态，必须证明适用性 | 已接受报价、签署相关合同页或完整双方确认邮件；可只交本案适用条款页 | 合同号、双方角色、接受/生效条件、费率/币种/单位、免箱期/适用日期、批次引用 |
| F. 发票与结算（条件必需） | 若验证 PUC/经济结果或 SETTLEMENT_PENDING，需要真实金额及本案分摊 | 下述 PI/debit-note PDF、修订发票及 ONE-N524 明细；或财务系统带来源导出 | 单号、案例号、出具/修订日期、币种、金额、费目、税/维修/per diem 区分、抵扣/剩余余额 |
| G. 付款及结清（仅 SETTLED/CLOSED 必需） | “预计下周付”“已收合并款”不等于本案结清 | 入账证明或收款方完整确认 + 合并款分摊表；若 CLOSED，另需无未结义务的结案确认 | 收款实际日期/区间、交易引用、币种/实收金额、ONE-N524 分摊、余额/争议、结案确认方与日期 |

优先找回已有引用原件：`PI-ONEN524SGH 20260409 chopped.pdf`、`TWDN-2026-05001-DebitNote-Maersk-ONEN524.pdf`、`TWDN-2026-08001-DebitNote-Maersk-ONEN524.pdf`，以及 CN UID 1/9/17 的完整原始邮件和相关附件。文件名中的数字不当作发票发生日；应读取单据正文。请明确 `19th Sept'25` 的原始含义，不直接修正导出正文。

**最小业务验证边界**：先提交 A–D，使同一案例至少有 3 条真实、有序且有来源的事件，可验证至少 2 次状态变化。若只验证操作结果，F/G 不单独阻塞该边界；若目标包含费用、SETTLED 或 CLOSED，则相应 E–G 必需。最终允许的状态路径仍须独立业务复核，不能用凑数量代替验证。

**可选**：初始 wish list、运输/使用跟踪、船名航次/提单、照片、完整历史邮件、无关条款页；只有对应主张进入本案时才成为必需。未提供使用事件，就不生成 IN_USE。业务日期只到“日”或有界区间也可以，保留原始精度；不要补成午夜或任意时区。区间重叠而无法排序时，应补充先后证据而不是编造时间。

## 4. 脱敏与来源保留

- 可遮盖个人电话、私人地址、无关联系人、银行账号全号、签名图像和无关合同；不需要提供邮箱密码/API 密钥。
- 公司名、箱号和业务单号可用稳定代号，但同一对象跨材料必须一致，保留身份映射在受控本地；不能每页随机换号。来源方业务角色必须保留。
- 日期、动作、数量、箱型、货币/单位及用于本次验证的金额不能随意平移或改写；如不能披露，明确缺失或可信有界区间，不提供虚构替代值。
- 保留邮件 Message-ID（可稳定脱敏）、正文/引用层级、附件与原消息对应关系；保留单据页码/行号、来源系统、原文件名、导出/脱敏说明。原件与脱敏副本分开保存并各计算 SHA-256，不覆盖原件。
- 后续只将确有必要且获准的脱敏材料纳入仓库；银行凭证/完整私密邮件不默认提交到 GitHub。不要把合并线程中的其他案例金额自动归给 ONE-N524。

## 5. 当前处理与下一次触发

本轮只交付此请求与 readiness matrix，不创建 case runtime 实体、事件、状态迁移或时间线。GEVENT/GSTATE/GTIME 尚未实现/评估，G6=BLOCKED；既有 GR/GC/GA/GDET/GSYNC 保持工程基线范围。证据不足分支遵循 Issue #3 §14，因此不提前编写依赖虚构事件的运行产物或新业务测试；115 项原测试仍应完整验证。

Founder 只需一次提供/指向上述材料包并明确 GP/HC 身份；无需逐条分多轮回复。材料进入 governed corpus 后，Codex 在同一 Issue #3、同一分支重新做充分性审计，只有通过才实现新门禁、对抗测试和两次干净业务时间线重建。独立复核和 Founder G7 仍是后续边界。本轮不申请 merge，不改变 main 或生产。
