# Incoterm Independent Model v0.2

**Date:** 2026-09-17 14:49:34
**Baseline:** semantica-report-20260917-yiboke.md

## G1: Incoterm Canonicalization

### Old Model (v0.1)
```yaml
ServiceType:
  - EXW (confused with service)
  - FOB (confused with charge type)
  - CIF (confused with both)
ChargeType:
  - COD (confused with payment term)
```

### New Model (v0.2)
```yaml
Incoterm:
  definition: "International Commercial Term - defines risk transfer point"
  canonical_values:
    - EXW: "Ex Works - maximum obligation on buyer"
    - FOB: "Free On Board - risk transfers when goods on board vessel"
    - CIF: "Cost Insurance and Freight - seller pays cost + insurance + freight"
    - CFR: "Cost and Freight"
    - FCA: "Free Carrier"
    - CPT: "Carriage Paid To"
    - CIP: "Carriage and Insurance Paid To"
    - DAP: "Delivered at Place"
    - DPU: "Delivered at Place Unloaded"
    - DDP: "Delivered Duty Paid - maximum obligation on seller"
  
  properties:
    risk_transfer_point: string
    seller_responsibility: [shipping, insurance, customs, duties]
    buyer_responsibility: [shipping, insurance, customs, duties]
    applicable_transport: [any, sea_only, air_only]
  
  examples_from_corpus:
    - EXW: Found in quotation context
    - FOB: NOT FOUND (gap)
    - CIF: NOT FOUND (gap)
```

## G2: Conflict Resolution

| Conflict | Resolution | Rationale |
|----------|------------|-----------|
| EXW as ServiceType | → Incoterm | It's a trade term, not a service |
| FOB as ChargeType | → Incoterm | Risk transfer point, not a charge |
| CIF as ServiceType | → Incoterm | Includes insurance + freight |

## G3: Incoterm → Shipment Links

```turtle
@prefix ybk: <http://example.org/yiboke#> .
@prefix schema: <http://schema.org/> .

# Incoterm definition
ybk:EXW a schema:DefinedTerm ;
    schema:name "EXW - Ex Works" ;
    schema:description "Seller makes goods available at their premises" ;
    schema:riskTransferPoint "Seller premises" ;
    schema:applicableTransport "Any" .

ybk:FOB a schema:DefinedTerm ;
    schema:name "FOB - Free On Board" ;
    schema:description "Risk transfers when goods are on board the vessel" ;
    schema:riskTransferPoint "On board vessel" ;
    schema:applicableTransport "Sea and inland waterway" .
```

## Gap Assessment

| Incoterm | Found in Corpus | Expected Frequency | Confidence |
|----------|----------------|-------------------|------------|
| EXW | Partial | LOW | MEDIUM |
| FOB | NO | HIGH | N/A |
| CIF | NO | HIGH | N/A |
| DAP | NO | MEDIUM | N/A |
| DDP | NO | LOW | N/A |

**Recommendation:** Search additional quotation documents for Incoterm mentions.
