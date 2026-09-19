# 02-ONTOLOGY-CANONICAL-SCHEMA-v0.2

**Status**: DRAFT  
**Date**: 2026-09-17  
**Reference**: SPEC-Semantica-AKOS-Logistics-Reality-Ontology-v0.2

---

## Core Classes

```yaml
core_classes:
  Shipment:
    description: 一次具体货运业务/Job，是核心业务上下文
    required_fields:
      - shipment_id
      - customer
      - shipper
      - consignee
  
  Organization:
    description: 公司、承运人、货代、客户、代理等法人或组织
  
  Person:
    description: 真实联系人或业务经办人
  
  PartyRole:
    description: Organization/Person 在特定 Shipment 中承担的角色
    allowed_roles:
      - SHIPPER
      - CONSIGNEE
      - NOTIFY_PARTY
      - FORWARDER
      - CARRIER
      - ORIGIN_AGENT
      - DESTINATION_AGENT
      - CUSTOMER
      - UNKNOWN
  
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
  
  Incoterm:
    description: EXW / FOB / CIF / DAP / DDP 等贸易术语
    canonical_values:
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
  
  Document:
    description: 与 Shipment 相关的业务文件
    canonical_types:
      - QUOTATION
      - BOOKING_FORM
      - PROFORMA_INVOICE
      - COMMERCIAL_INVOICE
      - MASTER_AIR_WAYBILL
      - HOUSE_AIR_WAYBILL
      - STATEMENT_OF_ACCOUNT
      - OTHER
      - UNKNOWN
  
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
    canonical_states:
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
  
  Evidence:
    description: 支撑实体、关系或状态判断的现实证据
```

---

## Value Objects (not autonomous entities)

```yaml
value_objects:
  - WeightMeasurement
  - MonetaryAmount
  - Rate
  - Quantity
  - Dimension
  - Currency
```

标记规则：`value_object=true`

---

## Relations

```yaml
relations:
  plays_role:
    domain: [Organization, Person]
    range: PartyRole
  
  in_shipment:
    domain: PartyRole
    range: Shipment
  
  has_route:
    domain: Shipment
    range: Route
  
  has_leg:
    domain: Route
    range: RouteLeg
  
  origin:
    domain: RouteLeg
    range: TransportNode
  
  destination:
    domain: RouteLeg
    range: TransportNode
```

---

## Migration Notes

- v0.1中EXW/FOB/CIF同时作为ServiceType和ChargeType → v0.2迁移到Incoterm
- 保留原始分类在migration log中