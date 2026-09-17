# SPEC-Semantica-AKOS-Logistics-Reality-Ontology-v0.2

**Status:** EXECUTION READY  
**Date:** 2026-09-17  
**Execution Owner:** OpenMinis / Semantica  
**Architecture / Review Owner:** ChatGPT / AKOS  
**Domain Reality Source:** 意保克空运货代实际业务资料  
**Baseline Report:** `semantica-report-20260917-yiboke.md`  
**Previous Spec:** `SPEC-20260917-YIBOKE-AIR-FREIGHT-ONTOLOGY`  
**Target Classification:** `CONTROLLED REALITY ONTOLOGY PILOT`

---

# 0. Executive Instruction

本任务不是重新做一次实体抽取，也不是立即建立 Neo4j Production Knowledge Graph。

本轮目标是：

> 将 v0.1 已完成的"PDF → Entity/Relation Candidate Extraction"，升级为：
>
> **Reality Evidence → Canonical Domain Model → Validated Ontology → Evidence-bound Knowledge Graph Candidate**

本轮原则：

**DO NOT SCALE BEFORE NORMALIZATION.**

在当前 64 份 PDF 和已识别的 6 个实际业务样本没有完成语义规范化、证据绑定、关系恢复和 Reality Validation 之前：

- 不扩大 Ontology 到大量新客户；
- 不宣布 Production Ready；
- 不建立不可逆生产数据库；
- 不把 NER 抽取结果直接视为业务 Truth；
- 不因为 PDF extraction 成功而将 Ontology confidence 标记为 HIGH。

本轮完成后，意保克数据应成为：

> **AKOS Logistics Ontology 第一个受控 Reality Grounding Pilot。**

---

# 1. Current Baseline

以 `semantica-report-20260917-yiboke.md` 为唯一 v0.1 baseline。

当前已完成：

- 64 个 PDF 文档文本提取；
- 230 个 entity candidates；
- 15 个 relation candidates；
- 6 条主要航线；
- 6 个业务样本；
- Organization / Person / PortCode / Location / ServiceType / DocumentType / ChargeType / FinancialValue / Weight / Port 等候选类型；
- 初步 Turtle triples；
- 初步业务流程；
- 初步 provenance 声明。

这些成果全部保留，不覆盖、不删除。

v0.2 必须作为新的版本产物。

---

# 2. Problem Statement

v0.1 已证明 Reality Corpus 可以被 Semantica 摄入，但尚未证明 Ontology 可以作为 AKOS Truth Layer。

当前主要问题包括但不限于：

## P1 — Semantic Type Collision

当前存在：

- EXW → ServiceType
- EXW → ChargeType
- FOB → ServiceType
- FOB → ChargeType
- CIF → ServiceType
- CIF → ChargeType

这是 ontology typing collision。

EXW / FOB / CIF 等必须进入独立 canonical concept：

`Incoterm`

但不能简单批量硬编码迁移。

必须：

1. 找回原 PDF evidence；
2. 判断文本上下文；
3. canonicalize；
4. 保存旧 classification；
5. 记录 correction provenance。

---

## P2 — Context-Free Party Relationships

不得长期保存：

`Company A → shipper_consignee → Company B`

作为无上下文永久关系。

Shipper / Consignee / Notify Party / Forwarder / Carrier 等属于：

**Party 在一个 Shipment / Job 中的 Role。**

目标模型应能够表达：

`Organization`
→ `plays_role`
→ `PartyRole`
→ `in_shipment`
→ `Shipment`

---

## P3 — Route Modeling Too Flat

以下模式不得作为最终业务模型：

`HAM → route_to → DXB`

或：

`HAM → origin_of → DXB`

Route 必须拥有自己的上下文。

至少：

`Shipment`
→ `has_route`
→ `Route`

`Route`
→ `has_leg`
→ `RouteLeg`

`RouteLeg`
→ `origin`
→ `TransportNode`

`RouteLeg`
→ `destination`
→ `TransportNode`

HAM / DXB / DWC / HKG 等不得只作为字符串存在。

---

## P4 — Measurement / Value Objects Misclassified as Core Entities

当前 230 个 candidates 中，大量为：

- Weight
- FinancialValue

这些不能默认与 Organization / Shipment 等作为同级独立现实实体。

必须区分：

### Domain Entity
具有独立业务身份：

- Shipment
- Organization
- Person
- Document
- Route
- TransportNode
- Cargo

### Value Object / Measurement
描述其他实体：

- WeightMeasurement
- MonetaryAmount
- Rate
- Quantity
- Dimension
- Currency

Value Object 可以有 graph node，但必须明确 `value_object=true`，不得与 autonomous business entity 混淆。

---

## P5 — Canonicalization Missing

以下可能属于同一概念：

- invoice
- 发票
- Commercial Invoice

以下可能属于同一概念：

- MAWB
- Master Air Waybill

以下必须 canonicalize：

- cif / CIF
- EXW / exw
- organization name variants
- person name variants
- airport/code variants

禁止为了提高 entity count 而保留明显 duplicate concepts。

---

## P6 — Evidence Binding Insufficient

任何进入 Validated Ontology 的事实必须能回答：

> "这个事实来自哪个现实文件的什么位置？"

每一个 validated entity / relationship / business state 至少绑定：

- source_document_id
- source_filename
- source_page 或可等价定位信息
- evidence_text_span
- extraction_timestamp
- extraction_method
- source_hash
- confidence
- validation_status

如果 PDF parser 无法可靠提供 page：

允许使用：

`document + chunk_id + text span + hash`

但禁止只有：

`source = PDF`

这样的粗粒度 provenance。

---

# 3. Target Ontology v0.2

本轮不追求"完整国际货代 Ontology"。

只建立能够解释当前意保克样本的最小可用 Reality Ontology。

## 3.1 Core Classes

必须至少评估并建立：

```yaml
core_classes:

  Shipment:
    description: 一次具体货运业务/Job，是核心业务上下文

  Organization:
    description: 公司、承运人、货代、客户、代理等法人或组织

  Person:
    description: 真实联系人或业务经办人

  PartyRole:
    description: Organization/Person 在特定 Shipment 中承担的角色

  Cargo:
    description: Shipment 所运输货物

  Route:
    description: Shipment 的完整运输路径

  RouteLeg:
    description: Route 中单段运输

  TransportNode:
    description: 机场、港口、仓库等运输节点

  Location:
    description: 国家、城市、地区等地理实体

  Service:
    description: 实际提供的物流服务

  Incoterm:
    description: EXW / FOB / CIF / DAP / DDP 等贸易术语

  Document:
    description: 与 Shipment 相关的业务文件

  Charge:
    description: 一个实际收费项目

  MonetaryAmount:
    description: 金额值对象

  WeightMeasurement:
    description: 重量值对象

  BusinessEvent:
    description: 现实中发生、能够改变 Shipment 状态的业务事件

  ShipmentState:
    description: Shipment 当前业务状态

  Evidence:
    description: 支撑实体、关系或状态判断的现实证据
```

---

# 4. Role Model

Shipper / Consignee / Notify Party / Forwarder / Carrier / Agent 不优先建立为 Organization subtype。

优先采用：

```text
Organization
    ↓ plays_role
PartyRole
    ↓ in_context
Shipment
```

允许：

```yaml
PartyRole.role_type:
  - SHIPPER
  - CONSIGNEE
  - NOTIFY_PARTY
  - FORWARDER
  - CARRIER
  - ORIGIN_AGENT
  - DESTINATION_AGENT
  - CUSTOMER
  - UNKNOWN
```

如果证据不足：

必须标记 `UNKNOWN`。

不得推断。

---

# 5. Document Model

至少 canonicalize：

```yaml
DocumentType:
  - QUOTATION
  - BOOKING_FORM
  - PROFORMA_INVOICE
  - COMMERCIAL_INVOICE
  - MASTER_AIR_WAYBILL
  - HOUSE_AIR_WAYBILL
  - STATEMENT_OF_ACCOUNT
  - OTHER
  - UNKNOWN
```

必须保留：

`raw_document_type`

例如：

```yaml
raw_document_type: "invoice"
canonical_document_type: "UNKNOWN"
```

只有证据足够时才能升级：

```yaml
canonical_document_type: "COMMERCIAL_INVOICE"
```

禁止通过文件名猜测后直接认定。

---

# 6. Incoterm Normalization

建立独立：

`Incoterm`

候选包括当前 corpus 中实际出现的：

- EXW
- FOB
- CFR
- CIF
- FCA
- CPT
- CIP
- DAP
- DPU
- DDP

注意：

本 SPEC 不声明所有候选一定实际存在于对应 Shipment。

必须逐条绑定 source evidence。

Incoterm 不得同时分类为：

- ServiceType
- ChargeType

原错误 classification 必须保留在 migration / correction log 中。

---

# 7. Charge Model

`Charge` 必须表示实际收费项目。

至少支持：

```yaml
Charge:
  charge_type:
  description:
  amount:
  currency:
  unit_rate:
  quantity_basis:
  payer:
  payee:
  related_shipment:
  related_document:
  source_evidence:
```

对于：

- AF Rate
- THC
- Fuel Surcharge
- Security Surcharge
- War Risk
- AWC Filing

可以作为 ChargeType candidates。

对于 `COD`：

当前 corpus 含义不得根据缩写直接判断。

如果上下文不足：

```yaml
canonical_type: UNKNOWN
raw_label: COD
```

禁止 OpenMinis 自行使用通用知识覆盖原始证据。

---

# 8. Location / Airport Normalization

当前 HAM / DXB / DWC / HKG / SIN / DMM / ROT 等必须：

1. 从原始文件读取真实上下文；
2. 保存 raw code；
3. 建 canonical TransportNode；
4. link 到 Location；
5. 记录代码体系。

建议：

```yaml
TransportNode:
  node_type: AIRPORT
  code:
  code_system: IATA
  canonical_name:
  city:
  country:
```

如果无法从 corpus 确定：

字段使用 `UNKNOWN`。

允许外部 reference enrichment，但：

**外部知识必须明确标记为 external_reference，不得伪装成 corpus-derived truth。**

---

# 9. Shipment-Centric Reality Model

本轮最重要的转换：

不要围绕"230 个散落实体"继续扩张。

围绕目前 6 个真实业务建立：

**6 个 Shipment Reality Records**

每一个 Shipment 尽可能恢复：

```yaml
shipment:
  shipment_id:
  customer:
  shipper:
  consignee:
  notify_party:
  forwarder:
  carrier:

  cargo:
    description:
    gross_weight:
    chargeable_weight:
    quantity:
    package_count:

  incoterm:

  route:
    origin:
    destination:
    legs:

  services:

  documents:

  charges:

  events:

  current_state:

  timeline:

  evidence:

  unknowns:

  conflicts:

  confidence:
```

---

# 10. Business Event / State Model

禁止将以下线性流程直接视为 Truth：

`Booking → Quotation → Invoice → MAWB → Departure → Arrival → Customs → Delivery → SOA`

该流程只能作为：

`v0.1 hypothesis`

v0.2 必须尝试从 document timestamp / event evidence 恢复真实 timeline。

推荐状态候选：

```yaml
ShipmentState:
  - INQUIRY
  - QUOTED
  - BOOKED
  - CONFIRMED
  - CARGO_RECEIVED
  - DEPARTED
  - IN_TRANSIT
  - ARRIVED
  - CUSTOMS_PROCESSING
  - RELEASED
  - DELIVERED
  - SETTLEMENT_PENDING
  - CLOSED
  - UNKNOWN
```

这些状态是 schema candidates。

只有 evidence 可以证明的状态才实例化。

---

# 11. Evidence-First Triple Contract

每条进入 Shadow Graph 的 Triple 必须至少包含：

```yaml
triple:
  subject:
  predicate:
  object:

  provenance:
    source_document_id:
    source_filename:
    page_or_chunk:
    evidence_span:
    source_hash:

  extraction:
    method:
    extracted_at:

  confidence:
    extraction_confidence:
    typing_confidence:
    relation_confidence:
    reality_confidence:

  validation:
    status:
    validator:
    validated_at:
```

---

# 12. Confidence Model

废弃单一：

`confidence = HIGH`

改为：

```yaml
confidence:

  source_extraction_confidence:
    description: 是否可靠读取原始文档

  entity_extraction_confidence:
    description: 是否可靠识别文本中的候选实体

  semantic_typing_confidence:
    description: 是否可靠判断实体属于哪个 ontology type

  relation_confidence:
    description: 是否有证据证明实体之间存在该关系

  reality_confidence:
    description: 是否足以进入 AKOS Truth Layer
```

建议状态：

```text
HIGH
MEDIUM
LOW
UNKNOWN
```

规则：

> `source_extraction_confidence = HIGH`
>
> 不代表
>
> `reality_confidence = HIGH`

---

# 13. Explicit Data Quality Tests

必须加入 automated validation。

## DQ-01

禁止：

`Person → schema:telephone → PersonName`

当前类似：

`schema:telephone "Daisy Shi"`

必须触发失败。

---

## DQ-02

Incoterm 不得同时属于：

`ServiceType + ChargeType`

---

## DQ-03

已 canonicalize 的 airport code 不得只作为 free-text string 存入 validated graph。

---

## DQ-04

同一个 canonical entity 不得因为大小写差异重复实例化。

例如：

`CIF`
`cif`

---

## DQ-05

Business Role 必须拥有 Shipment context。

---

## DQ-06

没有 source evidence 的 relationship：

不得进入 Validated Graph。

---

## DQ-07

存在冲突的事实：

不得自动选择其中一个。

必须：

```text
CONFLICT
```

---

## DQ-08

无法判断的语义：

必须：

```text
UNKNOWN
```

禁止 hallucinated completion。

---

# 14. Progressive Gates

## G0 — Corpus Integrity

验证：

- 64 份原始 PDF identity；
- document count；
- hashes；
- extraction completeness；
- 文件不能被修改。

### PASS 条件

所有源文件具备稳定 identity。

---

## G1 — Canonical Vocabulary

完成：

- Entity vocabulary；
- Relationship vocabulary；
- Incoterm normalization；
- DocumentType normalization；
- ChargeType normalization；
- Airport/location normalization rules。

### PASS 条件

不存在已知的 EXW/FOB/CIF 双重类型错误。

---

## G2 — Ontology Normalization

完成：

- Shipment-centric model；
- PartyRole；
- Route/RouteLeg；
- Measurement Value Objects；
- Evidence object；
- BusinessEvent / ShipmentState。

### PASS 条件

Schema 可以完整表示至少一个意保克 Shipment。

---

## G3 — Evidence Binding

将：

Entity / Relation / State

绑定回现实文件。

### PASS 条件

所有进入 validated candidate graph 的事实拥有 evidence pointer。

---

## G4 — Six-Shipment Reality Reconstruction

重点不是 entity count。

必须完成 6 个业务样本的逐单恢复。

### PASS 条件

每单至少生成：

- Parties
- Roles
- Route
- Documents
- Charges
- Timeline
- Evidence
- Unknowns
- Conflicts

数据不存在时允许 UNKNOWN。

---

## G5 — Automated Validation

运行本 SPEC 所有 DQ tests。

### PASS 条件

P0 Semantic Integrity Error = 0。

---

## G6 — Shadow Knowledge Graph

可以生成：

- Turtle / RDF；
- JSON-LD；
- 或 Semantica native graph representation。

但：

**只允许 Shadow。**

不得写入 AKOS Production Truth Store。

---

## G7 — Human / Founder Review Candidate

输出：

```text
REALITY_ONTOLOGY_VALIDATION_CANDIDATE
```

不得自动输出：

```text
PRODUCTION_READY
```

生产晋升另开 Gate。

---

# 15. Acceptance Criteria

必须至少满足：

### AC-01
64 个原始 PDF 不被修改。

### AC-02
保留 v0.1 全部原始 extraction results。

### AC-03
v0.2 独立版本化。

### AC-04
EXW/FOB/CIF 不再同时作为 ServiceType / ChargeType。

### AC-05
建立 Incoterm canonical class。

### AC-06
建立 Shipment core entity。

### AC-07
建立 PartyRole。

### AC-08
Shipper / Consignee relation 具备 Shipment context。

### AC-09
建立 Route。

### AC-10
建立 RouteLeg。

### AC-11
airport/location 具备 canonicalization mechanism。

### AC-12
Weight 转换为 Measurement semantics。

### AC-13
FinancialValue 转换为 MonetaryAmount semantics。

### AC-14
DocumentType canonicalized。

### AC-15
原始 label 永久保留。

### AC-16
entity deduplication 可追溯。

### AC-17
每条 validated relationship 有 provenance。

### AC-18
每个 provenance 可定位回 source document。

### AC-19
证据不足返回 UNKNOWN。

### AC-20
冲突返回 CONFLICT。

### AC-21
禁止无证据自动补全。

### AC-22
Daisy Shi / telephone 类型错误被检测并修复。

### AC-23
业务流程不再被硬编码成唯一线性 Truth。

### AC-24
建立 BusinessEvent 模型。

### AC-25
建立 ShipmentState 模型。

### AC-26
至少完成 6 个 Shipment Reality Records。

### AC-27
每个 Shipment 输出 evidence coverage。

### AC-28
每个 Shipment 输出 unknown list。

### AC-29
每个 Shipment 输出 conflict list。

### AC-30
输出四层以上 confidence。

### AC-31
source extraction confidence 与 reality confidence 分离。

### AC-32
所有 P0 validation tests PASS。

### AC-33
生成 Shadow Graph。

### AC-34
不得写入 Production Graph。

### AC-35
不得自动宣布 Production Ready。

---

# 16. Required Deliverables

请生成：

```text
01-SPEC-IMPLEMENTATION-REPORT-v0.2.md

02-ONTOLOGY-CANONICAL-SCHEMA-v0.2.yaml

03-ENTITY-CANONICALIZATION-MAP-v0.2.json

04-RELATION-CANONICALIZATION-MAP-v0.2.json

05-INCOTERM-NORMALIZATION-v0.2.json

06-DOCUMENTTYPE-NORMALIZATION-v0.2.json

07-CHARGE-NORMALIZATION-v0.2.json

08-SHIPMENT-REALITY-RECORDS-v0.2.json

09-EVIDENCE-PROVENANCE-INDEX-v0.2.json

10-ONTOLOGY-CONFLICT-REGISTER-v0.2.json

11-ONTOLOGY-UNKNOWN-REGISTER-v0.2.json

12-DATA-QUALITY-VALIDATION-REPORT-v0.2.md

13-SHADOW-KNOWLEDGE-GRAPH-v0.2.ttl

14-ONTOLOGY-CHANGELOG-v0.1-to-v0.2.md

15-FOUNDER-REVIEW-PACKET-v0.2.md
```

如果 OpenMinis 有更适合的原生结构，可以增加文件。

不得删除上述核心产物。

---

# 17. Founder Review Packet

`FOUNDER-REVIEW-PACKET-v0.2.md` 不要堆技术细节。

只回答：

## A. 原来有什么问题？

最多 10 项。

## B. 本轮修复了什么？

before / after 对照。

## C. 6 个 Shipment 恢复到什么程度？

每单一行。

## D. 还有哪些 UNKNOWN？

按重要性列出。

## E. 哪些事实存在 CONFLICT？

单独列出。

## F. 有哪些事实目前可以进入 AKOS Truth？

列数量和覆盖率。

## G. 有哪些事实禁止进入 Truth？

说明原因。

## H. 推荐下一 Gate

只允许：

```text
PASS_TO_DOMAIN_VALIDATION
```

或：

```text
REWORK_REQUIRED
```

不得自动 Production Promotion。

---

# 18. Metrics

本轮不要以：

`实体总数增加多少`

作为核心 KPI。

核心指标改为：

```yaml
metrics:

  shipment_reconstruction_coverage:

  evidence_binding_coverage:

  canonicalization_coverage:

  duplicate_resolution_rate:

  relationship_evidence_coverage:

  semantic_conflict_count:

  unknown_count:

  unsupported_relation_count:

  dq_pass_rate:

  reality_confidence_distribution:
```

尤其输出：

> **Evidence-bound Relationship %**

这是本轮最重要指标之一。

---

# 19. Execution Constraints

1. 原始 PDF = READ ONLY。
2. v0.1 = IMMUTABLE BASELINE。
3. 所有 correction 必须留 changelog。
4. 不得覆盖原 extraction。
5. 不得为了提高完整率猜字段。
6. 不得把外部常识冒充 corpus reality。
7. 外部 enrichment 必须标记 source class。
8. UNKNOWN 是合法结果。
9. CONFLICT 是合法结果。
10. 不以 entity count 优化模型。
11. 不进行 Production DB migration。
12. 不进行 Neo4j Production Deployment。
13. 不触碰 AKOS Production Truth Store。
14. 本轮默认 Shadow Execution。

---

# 20. Architectural Principle

本项目必须遵循：

```text
Reality
  ↓
Evidence
  ↓
Candidate Facts
  ↓
Canonicalization
  ↓
Ontology Mapping
  ↓
Validation
  ↓
Shadow Graph
  ↓
Human / SME Review
  ↓
Validated Truth
  ↓
Agent / Workflow
```

禁止：

```text
PDF
 ↓
NER
 ↓
Graph
 ↓
Truth
```

---

# 21. Relationship to AKOS

本 Pilot 的最终目的不是做一个好看的知识图谱。

它是验证：

> **真实企业资料是否能够经过 Semantica 转换成 AKOS 可执行、可追溯、可演化的 Reality Ontology。**

未来成功路径：

```text
Customer Reality
      ↓
Evidence Corpus
      ↓
Semantica Ontology
      ↓
Shadow Graph
      ↓
Founder Review
      ↓
Validated Truth
      ↓
AKOS Production
```

本 SPEC 仅覆盖：

```text
Evidence Corpus → Semantica Ontology → Shadow Graph
```

AKOS 侧的集成 Gate 另开。

---

# 22. Execution Notes

## 优先级

1. **G4 是本轮重点**：
   - 每个 Shipment 至少产出：
     - Parties + Roles
     - Route
     - Documents
     - Charges
     - Timeline
     - Evidence
     - Unknowns

2. **不要重复 v0.1 的 extraction**：
   - 直接读取已提取的 JSON
   - 做 canonicalization / correction / binding

3. **v0.1 产物必须保留**：
   - `yiboke_air_freight_ontology_corpus.json`
   - `semantica-report-20260917-yiboke.md`
   - 所有 PDF 文本文件

4. **v0.2 产物放在独立目录**：
   - `/var/minis/workspace/semantica-v0.2/`
   - 不得覆盖 v0.1 产物

## 命名约定

- v0.1 产物：`*-v0.1.*` 或 `semantica-report-20260917-yiboke.md`
- v0.2 产物：`*-v0.2.*`
- 版本 changelog：`*-CHANGELOG-v0.1-to-v0.2.md`
- Evidence index：`*-PROVENANCE-INDEX-v0.2.json`
- Conflict register：`*-CONFLICT-REGISTER-v0.2.json`
- Unknown register：`*-UNKNOWN-REGISTER-v0.2.json`

## 禁止操作

1. 不删除 v0.1 产物；
2. 不在本次对话中直接创建 AKOS 连接；
3. 不允许 OpenMinis 自行决定将某类事实升级为 Truth；
4. 不允许用外部知识覆盖 corpus 内缺失证据；
5. 不允许把 "合理推断" 当成 "Reality Truth"；
6. 不允许直接部署 Neo4j Production；
7. 不允许输出未经 founder review 的 Promotion 结论。

---

# 23. Output Contract

本轮结束前，你必须：

1. 输出 `01-SPEC-IMPLEMENTATION-REPORT-v0.2.md`；
2. 输出所有 15 个核心 artifact；
3. 明确告知：
   - 哪些事实可以进入 AKOS Truth；
   - 哪些事实仍为 Candidate；
   - 哪些事实被明确禁止；
   - 推荐的下一步 Gate 动作；
4. 不得输出 `FINAL_PRODUTION_READY`；
5. 必须在 Founder Review Packet 中明确推荐 `PASS_TO_DOMAIN_VALIDATION` 或 `REWORK_REQUIRED`。

---

**END OF SPEC v0.2**