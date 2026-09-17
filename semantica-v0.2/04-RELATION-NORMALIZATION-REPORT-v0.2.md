# Relation Normalization Report v0.2

**Date:** 2026-09-17 14:49:34
**Baseline:** semantica-report-20260917-yiboke.md

## G1: Relation Type Normalization

### Original vs Normalized

| Original Type | Normalized Type | Count | Reason |
|--------------|-----------------|-------|--------|
| route_to | route_to | 9 | Contextual normalization |
| origin_of | origin_of | 6 | Contextual normalization |

### Relation Quality Assessment

- Total relations: 15
- Contextual relations: 9
- Party relations: 0
- Unknown/conflict: 0

## G2: Shipment-Centric Relations

### Role-Indexed Relations

```python
# PartyRole → Organization mapping per shipment
for shipment in 6 shipments:
    shipment.shipper --[plays_role: SHIPPER]--> shipment
    shipment.consignee --[plays_role: CONSIGNEE]--> shipment
    shipment.forwarder --[plays_role: FORWARDER]--> shipment
```

### Route Relations

```python
# Origin → Destination with route context
routes = [
    {'code': 'HAM-DXB', 'origin': 'HAM', 'destination': 'DXB'},
    {'code': 'SIN-DWC', 'origin': 'SIN', 'destination': 'DWC'},
    {'code': 'HAM-DMM', 'origin': 'HAM', 'destination': 'DMM'},
    {'code': 'ROT-DXB', 'origin': 'ROT', 'destination': 'DXB'},
    {'code': 'HAM-HKG', 'origin': 'HAM', 'destination': 'HKG'},
    {'code': 'ROT-HKG', 'origin': 'ROT', 'destination': 'HKG'},
]
for route in routes:
    route.origin --[route: route.code]--> route.destination
```

## G3: Missing Relations Identified

| Missing Relation | Expected Source | Priority |
|-----------------|-----------------|----------|
| Shipper ↔ Consignee direct link | Commercial Invoice | HIGH |
| Forwarder ↔ Carrier link | MAWB | HIGH |
| Cargo ↔ Weight actual value | Air Freight Quotation | MEDIUM |
| Flight date ↔ Actual departure | MAWB | MEDIUM |
| Charge amount ↔ Actual total | Statement of Account | MEDIUM |

## Validation Status

| Gate | Requirement | Status | Blockers |
|------|-------------|--------|----------|
| G0 | All relations have source | PARTIAL | Some inferred |
| G1 | No duplicate relations | PASS | 0 duplicates |
| G2 | Contextual role resolution | PASS | 6 shipments mapped |
| G3 | Evidence traceable | PARTIAL | Needs PDF text verification |
