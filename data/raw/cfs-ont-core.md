---
document_id: CFS-ONT-CORE-001
type: ontology_core
title: CFS-ONT Core v0.1（集装箱货运站本体核心）
version: v0.1
status: Candidate（草案，待真实场站验证后逐项升级）
project: AI-Depot / CFS-Portal
form: 语义契约核心（语义层 + 治理层双层）
medium: 综合
akos_domain: logistics-ont / cfs-ont
privacy: internal
confidence: ⚠️ Pending（结构为草案/推断，基于 vault 一手语料与行业通识，待真实 CFS 验证）
stage: wiki-candidate
datum: 2026-08-15
source: LOGISTICS-ONT_Core_v0.1 × GlobeLink 费用代码全表 × 海运出口泳道图(LCL入仓) × 小包仓库SOP × FBA操作规范 × 监管规定（港口经营/危货/海关232号令） × 子代理网络调研
agent: dsh-web（张程 agent）
relation: increments LOGISTICS-ONT_Core_v0.1（Forwarder Extension 的 CFS 细化）
tags: [AI-Depot, CFS, Ontology, Semantic-Contract, 拼箱, 拆箱, CR-draft]
---

# CFS-ONT Core v0.1

> **定位**：在 LOGISTICS-ONT 公共底座之上，为"集装箱货运站（CFS，Container Freight Station）"建立语义契约——覆盖**出口集拼 / 进口拆箱分拨 / 电商集货仓**三类典型 CFS 场景。
> **与堆场本体的关系**：堆场（DEPOT-ONT）管"箱"，CFS（CFS-ONT）管"货+箱内作业"；两者在 Gate/EDI/计费/客户上共享同一公共底座。
> **目标**：让"拆拼箱业务是什么、凭什么信、谁能动、改没改过"可被 AI Agent 精准读写。

---

## 0. 一句话

**CFS 是"货进箱、箱进港"的作业与数据中枢**：出口把多票散货（LCL）拼进一个箱，进口把一个箱拆成多票分拨——语义层定义这些对象与规则，治理层保证 Agent 有据可依、有权限、可审计。

---

## 1. 双层总览

```
CFS-ONT Core
├── ★ 语义层（Semantic Layer）—— 业务是什么
│   ├── Organization   组织/角色（CFS/货代/船司/报关行/拖车/司机/仓管/理货/查验）
│   ├── Entity         实体（货物/装箱单/舱单/提单/仓库位/集装箱/设备）
│   ├── Relationship   关系（入仓/拼箱/拆箱/存储/计费/查验）
│   ├── Event          事件（入仓/出仓/拼箱完成/拆箱完成/查验/涨方/放行）
│   ├── Document       单据（到货总单/装箱单P/L/舱单/提单/报关单/过磅单/VGM/EDI报文）
│   ├── Rule           规则（先进先出/截关/危货禁运/计抛/涨方/查验流程）
│   ├── Function       函数（CBM利用率/计抛重/拼箱方案/费用试算/时效）
│   ├── Action         动作（入仓/出仓/拼箱/拆箱/过磅/放行/计费）
│   └── Decision       决策（拼箱方案/扣件处理/涨方处理/放行，带 Gate 与留痕）
│
└── ★ 治理层（Governance Layer）
    ├── Evidence / Confidence / Validation Method / Version / Permission / Audit
    └── （沿用 LOGISTICS-ONT 治理层规约，不重复定义）
```

---

## 2. 语义层（Semantic Layer）

### 2.1 Organization（组织/角色）
| Actor | 说明 | 状态 |
|---|---|---|
| CFS | 集装箱货运站（拼箱仓库/拆箱仓） | ✅ |
| Forwarder / NVOCC | 货代/无船承运人（拼箱庄家） | ✅ |
| Consignor / Consignee | 发货人/收货人 | ✅ |
| ShippingLine | 船公司 | ✅ |
| CustomsBroker | 报关行 | ✅ |
| Trucker / Driver | 拖车/司机 | ✅ |
| WarehouseStaff | 仓管/理货/叉车工 | ✅ |
| Inspector | 海关查验/商检 | ⚠️ 视监管模式 |

### 2.2 Entity（实体）
| Entity | 说明 | 对齐（LOGISTICS-ONT） |
|---|---|---|
| CargoLot / Shipment | 一票货物（多件/多袋/多托） | ➕ CFS 新增 |
| Package | 件（单件包裹/纸箱/袋） | ➕ CFS 新增（小包仓核心） |
| Pallet | 托盘 | ➕ CFS 新增 |
| Container | 集装箱（拼箱后装入） | DP.CONTAINER ✅ |
| WarehouseSlot | 库位（区-排-层） | ➕ CFS 新增（类比 YardSlot） |
| WeighBridgeRecord | 过磅记录 | ➕ CFS 新增 |
| Equipment | 叉车/安检机/地磅 | ❓ 待盘点 |

### 2.3 Relationship（关系）
| From | Relationship | To | 状态 |
|---|---|---|---|
| CargoLot | consolidated_into | Container | ✅ 拼箱 |
| CargoLot | deconsolidated_from | Container | ✅ 拆箱 |
| CargoLot | stored_at | WarehouseSlot | ✅ |
| Package | belongs_to | CargoLot | ✅ 小包仓 |
| CargoLot | declared_in | CustomsDeclaration | ✅ |
| CFS | issues | ArrivalNote / DispatchNote | ✅ 到货总单/出仓总单 |
| Trucker | delivers | CargoLot | ✅ |
| Forwarder | books | Container | ✅ |

### 2.4 Event（事件）
- ArrivalIn（入仓登记）/ OutboundDispatch（出仓）/ ConsolidationCompleted（拼箱完成）/ DeconsolidationCompleted（拆箱完成）/ WeighingRecorded（过磅）/ InspectionHeld（查验）/ VolumeSurplusDetected（涨方）/ CustomsReleased（放行）/ BillingTriggered（计费）/ ContainerGateIn（箱进场） ✅

### 2.5 Document（单据）
| 单据 | 说明 | 状态 |
|---|---|---|
| 到货总单（Arrival Note） | 入仓登记：客户/袋数/票数/重量 | ✅ 小包仓SOP一手 |
| 出仓总单（Dispatch Note） | 出仓：按代理/渠道/舱位 | ✅ 小包仓SOP一手 |
| Packing List / Cargo Manifest | 装箱单/舱单 | ✅ |
| 提单（HBL/MBL） | 分单/主单 | ✅ 出口泳道图 |
| 报关单 | 出口/进口报关 | ✅ |
| 过磅单 / VGM | 重量申报 | ✅ 出口泳道图 |
| 扣件记录 | 问题件（拦截/欠费/重量差/渠道不匹配/单号重复） | ✅ 小包仓SOP一手 |
| EDI 报文 | UN/EDIFACT（订舱/提单/舱单） | ✅ GlobeLink/Logwing 一手 |
| 费用单（Invoice） | CFS 拼箱费/仓储费/操作费 | ✅ 费用代码全表 |

### 2.6 Rule（规则）
| Rule | Condition → Action | 状态 |
|---|---|---|
| FIFO出仓 | 出仓按先进先出，直客优于同行 | ✅ 小包仓SOP一手 |
| 计抛收费 | 泡重货结合（材积/6000 等），按航司要求 | ✅ 小包仓SOP+FBA SOP一手 |
| 重量差异扣件 | 出入仓重量差超阈值（同行10g/出仓30g）→ 复核 | ✅ 小包仓SOP一手 |
| 危货/违禁禁运 | 爆炸品/毒气/放射等禁运清单 → 拒收 | ✅ RFS合同+FBA SOP一手 |
| 涨方处理 | 实际体积>预报 → 通知/改单/补费 | ✅ 出口泳道图一手 |
| 截关/Cut-off | 错过截关 → 赶不上本班船 | ✅ 航运通识语料 |
| 监管场所合规 | 海关监管场所设置规范（68号公告）→ 数据报送 | ⚠️ 网络调研待核 |

### 2.7 Function（函数，可计算）
- calc_chargeable_weight（计抛重：实重 vs 材积重）✅ 小包仓SOP
- calc_cbm_utilization（CBM 利用率）✅
- suggest_consolidation（拼箱方案：货→箱匹配）✅ 3D bin packing 方向
- estimate_cfs_fee（拼箱费/仓储费/操作费试算）✅ 费用代码 CFS 条目
- track_shipment_status（货状态追踪）✅
- detect_anomaly（异常检测：扣件/涨方/超期）✅

### 2.8 Action（动作，可执行）
- RECEIVE_CARGO（入仓登记）/ DISPATCH_CARGO（出仓）/ CONSOLIDATE（拼箱）/ DECONSOLIDATE（拆箱）/ WEIGH（过磅）/ HOLD_INSPECTION（查验/扣件）/ RELEASE（放行）/ GENERATE_BILLING（计费）/ CREATE_DISPATCH_NOTE（出仓总单）
> 每个 Action 的治理规约（Risk/Permission/Approval/Audit）沿用 LOGISTICS-ONT 动作治理八属性。

### 2.9 Decision（决策，带 Gate 与留痕）
- 拼箱方案选择 / 扣件处置 / 涨方处理 / 放行决策
- 每条决策：输入证据 → 判定依据 → 结果 → 记录人/机 → 时间戳。

---

## 3. 与堆场（DEPOT-ONT）的关系与边界

| 维度 | DEPOT-ONT（堆场） | CFS-ONT（货运站） |
|---|---|---|
| 核心对象 | Container / YardSlot | CargoLot / WarehouseSlot |
| 作业 | 收还箱/验修/堆存 | 入出仓/拼拆箱/过磅 |
| 计费 | 堆存/吊卸/拖运/修箱 | 拼箱费/仓储费/操作费/过磅 |
| 共享底座 | 组织/单据(EIR)/EDI/客户/SLA | 组织/单据(舱单/提单)/EDI/客户 |
| 交界 | — | 拼箱完成后 Container GateIn → 进入堆场/码头 |

> **协同价值**：同一运营商往往"堆场+CFS"一体（如马士基 JV 堆场含 CFS、珉系可扩展）；一个 LOGISTICS-ONT 底座 + 两个扩展 = 一套语义管住"箱"和"货"。

---

## 4. Assumptions Register（新增）

| # | Assumption | Evidence | 若错影响 |
|---|---|---|---|
| A1 | 腰部 CFS 仍以 Excel/纸质为主 | 多厂商同指 + 在线托书率 0% 一手证据 | 数字化地基机会可能被高估 |
| A2 | CFS 与堆场常为同一运营商 | 马士基 JV 堆场 CFS 案例 ✅ | 若分离，需独立获客 |
| A3 | 拼箱方案（bin packing）是核心 AI 价值点 | 3D 装箱优化行业有量化案例 ⚠️ | 价值点偏移 |
| A4 | 电商"先查验后装运"监管场站是新窗口 | 2025-2026 多地落地 ⚠️ | 窗口期判断偏差 |

---

## 5. 下一步

1. [ ] 用真实 CFS（候选：深圳/上海拼箱仓、东擎式电商集货仓）验证语义层各元素。
2. [ ] 与 D-B1 指标规范对齐（CBM 利用率/时效/差错率/计费准确率）。
3. [ ] 生成可加载 schema（JSON/YAML）喂给 CFS-ONT runtime。
4. [ ] 对照招商国科 CFSS 功能清单查漏。

*执行：dsh-web（张程 agent）· 2026-08-15 · 依据 AKOS 方法论总纲 + LOGISTICS-ONT Core v0.1*
