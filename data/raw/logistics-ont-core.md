---
document_id: LOGISTICS-ONT-CORE-001
type: ontology_core
title: LOGISTICS-ONT Core v0.1
version: v0.1
status: Candidate (Change Request CR-AI-DEPOT-ARCHITECTURE-v0.3 交付)
project: AI-Depot
form: 语义契约核心（语义层 + 治理层双层）
medium: 综合
akos_domain: logistics-ont
privacy: internal
confidence: ⚠️ Pending（结构为草案/推断，待真实场站验证后逐项升级）
stage: wiki-candidate
datum: 2026-08-09
source: CR-AI-DEPOT-ARCHITECTURE-v0.3 × AI-Depot_Case_Architecture_v0.2 §4 × DEPOT-ONT schema × v0.1 YAML
agent: opencode
relation: increments AI-Depot_Case_Architecture_v0.2（不覆盖 v0.1/v0.2 资产）
tags: [AI-Depot, LOGISTICS-ONT, Ontology, Semantic-Contract, Governance, CR-v0.3]
---

# LOGISTICS-ONT Core v0.1

> **CR §1 交付**：把 v0.2 的 LOGISTICS-ONT Core 细分为**语义层 + 治理层**双层。Ontology 作为"人与系统、系统与 Agent 之间共享业务语义的**契约**"。
> **目标**：让架构**可执行**——每个语义元素都带可被验证/可被 AI 消费的定义，而非概念罗列。

---

## 0. 一句话

**语义层定义"业务是什么"，治理层定义"凭什么信它、谁能动它、改没改过"**；两层合起来，Agent 才能既读懂、又负责任地使用这份契约。

---

## 1. 双层总览

```
LOGISTICS-ONT Core
├── ★ 语义层（Semantic Layer）—— 业务是什么
│   ├── Organization  组织/角色
│   ├── Entity        实体
│   ├── Relationship  关系
│   ├── Event         事件
│   ├── Document      单据
│   ├── Rule          规则
│   ├── Function      函数
│   ├── Action        动作
│   └── Decision      决策
│
└── ★ 治理层（Governance Layer）—— 凭什么信 / 谁能动 / 改没改
    ├── Evidence      证据来源
    ├── Confidence    可信度分级
    ├── Validation Method  验证法
    ├── Version       版本
    ├── Permission    权限
    └── Audit         审计
```

> **关键设计**：语义元素（Entity/Rule/Function/Action/Decision）**每一条都带治理层注解**——不是"有"就完事，而是"有 + 有依据 + 有版本 + 有权限 + 可审计"。

---

## 2. 语义层（Semantic Layer）

### 2.1 Organization（组织/角色）
定义堆场业务涉及的主体。| Actor/Object/是否独立建模 | ⚠️ 待陈总确认
- Depot / Customer / ShippingLine / Forwarder / Trucker / Driver / Staff
- 用途：为后续权限（谁看谁的箱）和 Agent 角色（谁来操作）奠基。

### 2.2 Entity（实体）
| Entity | 说明 | 对齐 |
|---|---|---|
| Container | 箱（20/40/45，干/冷/危，箱况状态机） | DP.CONTAINER ✅ |
| ContainerType | 箱型全表 | ⚠️ 需确认 9 箱型 |
| YardSlot | 堆位（A-xx-xx-x 三维） | DP.YARD_SLOT ✅ |
| Truck | 拖车 | ⚠️ 与 Trucker 关系 |
| Equipment | 设备/IoT | ❓ 待盘点 |

### 2.3 Relationship（关系）
| From | Relationship | To | 状态 |
|---|---|---|---|
| Container | stored_at | YardSlot | ✅ |
| Container | located_at | Depot | ✅ |
| RepairOrder | repairs | Container | ✅ |
| Billing | charges | Customer | ✅ |
| Depot | issues | EIR | ✅ |
| Trucker | handles | Container | ✅ |

### 2.4 Event（事件）
- GateIn / GateOut / InspectionCompleted / DamageReported / StorageExpired / BillingTriggered / PTIChecked ✅

### 2.5 Document（单据）
- EIR / RepairOrder / Invoice / GateTransaction / Booking / Order（字段对齐 GB/T 16561，Booking ⚠️ 是否存在于 AI DEPOT）

### 2.6 Rule（规则）
| Rule | Condition → Action | 状态 |
|---|---|---|
| FreeTimeExpired | 超免费期 → 计堆存费+通知 | ✅ |
| StorageCharge | 产生堆存/吊装费 → 生成账单 | ✅ |
| DamageDetected | 验损 → 建修单/索赔 | ✅ |
| HazardousRouting | 危货箱 → 入 dgZone 否则告警 | ✅ |
| SLACompliance | 按权重评分 → 对比目标 | ✅ |

### 2.7 Function（函数，可计算）
- calc_storage_fee / estimate_repair_cost / turn_time / fifo_rate / recommend_slot / pti_cost / dg_compliance_risk

### 2.8 Action（动作，可执行）
- RECEIVE_CONTAINER / RELEASE_CONTAINER / CREATE_REPAIR_ORDER / APPROVE_REPAIR / REPOSITION_EMPTY / GENERATE_BILLING / RECOMMEND_SLOT / RUN_PTI_CHECK / DG_COMPLIANCE_CHECK
> 每个 Action 的**治理规约在 §4 / D3 单独展开**（Risk/Permission/Approval/Audit）。

### 2.9 Decision（决策，带 Gate 与留痕）
- 翻箱 / 堆存推荐 / 批准维修 / 异常处置
- 每条决策：输入证据 → 判定依据 → 结果 → 记录人/机 → 时间戳。

---

## 3. 治理层（Governance Layer）

> 语义层每个元素按其类型附加以下治理注解。集中维护，供人/Agent 双读。

### 3.1 Evidence（证据来源）
| 级别 | 含义 | 示例 |
|---|---|---|
| `Verified by Source` | 系统实测/真实数据/已核实文档 | 修箱估价引擎未接入（AI DEPOT 实测） |
| `Industry Assumption` | 行业通识/推断，无本案例一手验证 | 翻箱率基线 15-30% |
| `Needs Expert Validation` | 需陈总/AI DEPOT IT 确认 | Booking 是否存在 |
| `Needs System Data Mapping` | 需对接真实系统才能证实 | Equipment/IoT |

### 3.2 Confidence（可信度）
- ✅ 事实验证 / ⚠️ 单源或推断 / ❓ 假设（沿用证据分级口径）

### 3.3 Validation Method（验证法）
- 交叉来源 / 专家确认（陈总） / 试点取证（试测 1 月） / 接口映射（对接系统）

### 3.4 Version（版本）
- 本体层级：Core 语义契约版本 + 每个元素版本（如 `calc_storage_fee v1.1`）
- 变更走 Change Request，留痕。

### 3.5 Permission（权限）
- 谁能读（View）：按 角色/组织/对象 维度
- 谁能写（Write / Execute）：HIGH 动作需人工批准（见 D3 Action Governance）
- 生产分水岭：跨系统写操作默认禁止，除非显式授权。

### 3.6 Audit（审计）
- 谁在何时对哪个语义元素做了何种变更/执行 → 记为不可篡改日志。
- HIGH 动作执行前后强制留痕。

---

## 4. 语义层 × 治理层：使用规约（如何给 Agent 消费）

```
Agent 读对象:
  ① 查 Entity+属性              ← 语义层
  ② 查该字段 Evidence/Confidence ← 治理层（决定是否可信）
  ③ 执行 Action 前查 Permission ← 治理层（决定能否动）
  ④ 执行后写 Audit              ← 治理层（留痕）
```

**铁律**：Agent 采信某断言前，必查其 Evidence+Confidence+Validation；执行 HIGH Action 前，必过 Permission+人工批准。(CR §1/§3 汇合)

---

## 5. 与 v0.1/v0.2 的关系

| 资产 | 关系 |
|---|---|
| AI-Depot_Ontology_Model_v0.1.yaml | 语义层实体/关系/事件/规则的机器源，本文件是其"双层+治理"升级骨架 |
| AI-Depot_Case_Architecture_v0.2 §4 | 本文件扩展自 v0.2 §4（把 Function/Action/Decision/Permission 显式化并补 Evidence/Confidence/Validation/Version/Audit） |

---

## 6. Assumptions Register（新增，参考 v0.2 A5-A8）

| # | Assumption | Evidence | 若错影响 |
|---|---|---|---|
| A9 | 语义层与治理层可解耦独立演进 | ⚠️ 设计推断 | 本体版本管理复杂 |
| A10 | Organization 建模粒度（拆分 Driver/Staff）合理 | ⚠️ 推断 | 权限矩阵过度设计 |
| A11 | Decision 元素可承载 Gate 留痕 | ⚠️ 设计推断 | 决策审计链路缺失 |

---

## 7. 下一步

1. [ ] 用治理层 Evidence/Confidence 对语义层全部元素过一遍，逐项标注（已部分完成 ✅/⚠️/❓）。
2. [ ] 陈总确认 Organization 建模粒度和 Booking 是否存在 → 更新 ⚠️/❓。
3. [ ] 与 D-B1 指标规范字典做语义对齐（哪个指标读哪个 Entity/Function/Event）。
4. [ ] 生成一份"可加载 schema"（JSON/YAML），喂给 DEPOT-ONT runtime。

*执行：opencode（张程 agent）· 2026-08-09 · 依据 CR-AI-DEPOT-ARCHITECTURE-v0.3 §1*