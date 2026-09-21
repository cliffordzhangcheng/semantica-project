#!/usr/bin/env python3
"""Generate business SPO claims from entities and relations"""
import sys
import json
from pathlib import Path
from datetime import datetime

def generate_business_spo():
    """Generate business-semantic claims from relations"""
    
    # Load graph
    graph_file = Path("outputs/06_graph.json")
    if not graph_file.exists():
        print("Error: graph file not found", file=sys.stderr)
        return 1
    
    with graph_file.open() as f:
        graph = json.load(f)
    
    entities = graph.get("entities", {})
    relations = graph.get("relations", [])
    
    # Load evidence
    evidence_file = Path("outputs/evidence.jsonl")
    evidence_map = {}
    if evidence_file.exists():
        for line in evidence_file.read_text().strip().split('\n'):
            if line.strip():
                try:
                    ev = json.loads(line)
                    evidence_map[ev.get('evidence_id')] = ev
                except:
                    pass
    
    # Business SPO patterns
    business_spo_templates = [
        # Relation -> Claim mappings
        ("provides_service_to", "provides_service_to", "OBSERVED"),
        ("intermediates", "intermediates", "OBSERVED"),
        ("has_contract_with", "has_business_agreement", "OBSERVED"),
        ("has_puc_rate", "has_pricing", "SUPPORTED"),
        ("has_free_days", "has_contract_term", "SUPPORTED"),
        ("has_daily_rate", "has_pricing", "SUPPORTED"),
        ("located_at", "located_at", "OBSERVED"),
        ("transports", "transports", "OBSERVED"),
        ("owns", "owned_by", "OBSERVED"),
        ("belongs_to", "belongs_to", "OBSERVED"),
        ("provides", "provides", "OBSERVED"),
        ("publishes", "publishes", "OBSERVED"),
        ("off_hires_at", "off_hires_at", "OBSERVED"),
    ]
    
    claims = []
    claim_id = 0
    
    for rel in relations:
        claim_id += 1
        
        subj = rel.get("subject", {})
        obj = rel.get("object", {})
        pred = rel.get("predicate", "")
        
        # Find matching SPO template
        spo_type = None
        status = "OBSERVED"
        for pattern, spo, st in business_spo_templates:
            if pattern in pred:
                spo_type = spo
                status = st
                break
        
        if spo_type is None:
            spo_type = pred
            status = "OBSERVED"
        
        claim = {
            "claim_id": f"c_business_{claim_id}",
            "subject": {
                "entity_id": subj.get("entity_id", "unknown"),
                "type": entities.get(subj.get("entity_id", ""), {}).get("type", "Entity"),
                "value": subj.get("value", "Unknown")
            },
            "predicate": spo_type,
            "object": {
                "entity_id": obj.get("entity_id", "literal"),
                "type": "Entity" if obj.get("entity_id", "") != "literal" else "Literal",
                "value": obj.get("value", "Unknown")
            },
            "claim_status": status,
            "evidence_ref": rel.get("evidence_ref", []),
            "confidence": rel.get("confidence", 0.8),
            "provenance": rel.get("provenance", "pipeline:RelationExtraction"),
            "timestamp": datetime.now().isoformat()
        }
        claims.append(claim)
    
    # Save claims
    claims_file = Path("outputs/claims_business_spo.jsonl")
    with claims_file.open('w') as f:
        for claim in claims:
            f.write(json.dumps(claim, ensure_ascii=False) + '\n')
    
    print(f"Generated {len(claims)} business SPO claims")
    
    # Also update main claims file
    all_claims_file = Path("outputs/claims.jsonl")
    existing_claims = []
    if all_claims_file.exists():
        for line in all_claims_file.read_text().strip().split('\n'):
            if line.strip():
                try:
                    existing_claims.append(json.loads(line))
                except:
                    pass
    
    # Combine: keep original + add business SPO
    with all_claims_file.open('w') as f:
        for c in existing_claims:
            f.write(json.dumps(c, ensure_ascii=False) + '\n')
        for c in claims:
            f.write(json.dumps(c, ensure_ascii=False) + '\n')
    
    print(f"Total claims: {len(existing_claims) + len(claims)}")
    return 0

if __name__ == "__main__":
    sys.exit(generate_business_spo())
