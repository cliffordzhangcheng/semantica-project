# Party Role Resolution v0.2

**Date:** 2026-09-17 11:28:06
**Baseline:** semantica-report-20260917-yiboke.md

## G2: Party Role Resolution

### Organization → PartyRole Mapping

| Organization | Role | Shipment(s) | Evidence |
|--------------|------|-------------|----------|
| Epoch Offshore Engineering (Shanghai) Co.,Ltd | SHIPPER | HAM-DXB, SIN-DWC, HAM-DMM | Proforma Invoice |
| Epoch Offshore Engineering Co.,Ltd (HK) | SHIPPER | HAM-HKG, ROT-HKG | Commercial Invoice |
| PAC Ocean Solutions DMCC | CONSIGNEE | HAM-DXB, SIN-DWC, HAM-DMM | MAWB |
| Sino Crafts FZE | CONSIGNEE | ROT-DXB | MAWB |
| United Fuel Treatment Co. | NOTIFY_PARTY | All | MAWB |
| Xiamen Transworld Logistics Co., Ltd | FORWARDER | All | Booking Form |
| VSNB | AGENT | CNTR emails | Email signatures |

### PartyRole Schema

```yaml
PartyRole:
  definition: "Organization或Person在特定Shipment中承担的角色"
  properties:
    - role_type: "SHIPPER / CONSIGNEE / NOTIFY_PARTY / FORWARDER / CARRIER / AGENT"
    - organization_ref: "→ Organization"
    - person_ref: "→ Person (optional)"
    - shipment_ref: "→ Shipment"
    - effective_date: "开始承担角色的日期"
    - evidence: ["相关证据ID列表"]
  
  relationships:
    - "Organization plays_role PartyRole"
    - "Person may_play_role PartyRole"
    - "PartyRole in_shipment Shipment"
    - "PartyRole has_evidence Evidence"
```

### Known Conflicts

| Conflict | Resolution | Rationale |
|----------|------------|-----------|
| EPOCH OFFSHORE出现两次(HK/SH) | 同一公司的不同法律实体 | HK注册 vs Shanghai注册 |
| VSNB角色不明 | 标记为AGENT | 来自CNTR邮件签名 |

### Gap Assessment

| Missing Party Role | Expected Source | Priority |
|-------------------|-----------------|----------|
| CARRIER | MAWB - Airline | HIGH |
| CUSTOMS_BROKER | If applicable | MEDIUM |
| WAREHOUSE_OPERATOR | If applicable | LOW |
| INSURANCE_COMPANY | If CIF/CIP | MEDIUM |
