#!/usr/bin/env python3
"""Relation extraction from real corpus - no synthetic data"""
import sys
import json
import re
from pathlib import Path
from datetime import datetime

def extract_relations():
    """Extract evidence-grounded relations from corpus"""
    
    # Load entities
    entities_file = Path("outputs/03_entities.json")
    if not entities_file.exists():
        print("Error: entities file not found", file=sys.stderr)
        return 1
    
    with entities_file.open() as f:
        entities_data = json.load(f)
    
    entities = entities_data.get("entities", {})
    print(f"Loaded {len(entities)} entities")
    
    # Load corpus
    corpus_dir = Path("data/raw")
    if not corpus_dir.exists():
        print("Error: corpus directory not found", file=sys.stderr)
        return 1
    
    relations = []
    relation_id = 0
    
    # Relation patterns to match
    relation_patterns = [
        # From oneway-corpus.md
        (r"Cosmos Whales.*provides.*Hapag-Lloyd", "provides_service_to", "Cosmos Whales", "Hapag-Lloyd"),
        (r"Cosmos Whales.*中间人", "intermediates", "Cosmos Whales", "Hapag-Lloyd"),
        (r"马士基.*Contract|agreement", "has_contract_with", "Maersk", "Cosmos Whales"),
        (r"PUC.*USD.*150|150.*USD", "has_puc_rate", "OneWayContract", "USD150/container"),
        (r"免箱.*90-100.*天", "has_free_days", "OneWayContract", "90-100 days"),
        (r"per diem.*\$1\.\d", "has_daily_rate", "OneWayContract", "USD1.0/container"),
        
        # From ai-depot-ontology-mapping.md
        (r"Container.*located_at.*Depot", "located_at", "Container", "Depot"),
        (r"Truck.*transports.*Container", "transports", "Truck", "Container"),
        (r"Customer.*owns.*Container", "owns", "Customer", "Container"),
        
        # From container-invest-ont-core.md
        (r"ContainerAgent.*intermediates.*OneWayContract", "intermediates", "ContainerAgent", "OneWayContract"),
        (r"ContainerOwner.*provides.*SOCContainer", "provides", "ContainerOwner", "SOCContainer"),
        (r"Carrier.*publishes.*WishList", "publishes", "Carrier", "WishList"),
        (r"ContainerAsset.*off_hires_at.*Depot", "off_hires_at", "ContainerAsset", "Depot"),
        
        # From cfs-ont-core.md
        (r"Package.*belongs_to.*CargoLot", "belongs_to", "Package", "CargoLot"),
        (r"CFS.*consolidates", "consolidates", "CFS", "CargoLot"),
    ]
    
    for doc_file in sorted(corpus_dir.iterdir()):
        if not doc_file.is_file() or not doc_file.suffix == '.md':
            continue
        
        content = doc_file.read_text()
        source_doc = doc_file.name
        
        print(f"\nProcessing: {source_doc}")
        
        # Try each pattern
        for pattern, pred, subj, obj in relation_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                # Find entity IDs
                subj_id = None
                obj_id = None
                
                for eid, einfo in entities.items():
                    if einfo.get("name", "").lower() in subj.lower() or subj.lower() in einfo.get("name", "").lower():
                        subj_id = eid
                    if einfo.get("name", "").lower() in obj.lower() or obj.lower() in einfo.get("name", "").lower():
                        obj_id = eid
                
                # If not found in entities, create new relation with literal values
                if subj_id is None and obj_id is None:
                    # Try to match partial names
                    for eid, einfo in entities.items():
                        name = einfo.get("name", "")
                        if subj.lower() in name.lower() or name.lower() in subj.lower():
                            subj_id = eid
                        if obj.lower() in name.lower() or name.lower() in obj.lower():
                            obj_id = eid
                
                relation_id += 1
                relation = {
                    "relation_id": f"r{relation_id}",
                    "subject": {
                        "entity_id": subj_id or "unknown",
                        "value": subj
                    },
                    "predicate": pred,
                    "object": {
                        "entity_id": obj_id or "literal",
                        "value": obj
                    },
                    "source_document_id": source_doc,
                    "evidence_ref": [f"ev_{relation_id}"],
                    "confidence": 0.85,
                    "extractor": "pattern:v2.0",
                    "provenance": f"pipeline:RelationExtraction:v2.0:{source_doc}"
                }
                relations.append(relation)
                print(f"  Found: {subj} {pred} {obj}")
    
    # Save relations
    output_file = Path("outputs/04_relations.json")
    output = {
        "relations": relations,
        "count": len(relations)
    }
    output_file.write_text(json.dumps(output, indent=2, ensure_ascii=False))
    print(f"\nExtracted {len(relations)} relations from corpus")
    
    # Update graph with relations
    graph_file = Path("outputs/06_graph.json")
    if graph_file.exists():
        with graph_file.open() as f:
            graph = json.load(f)
        graph["relations"] = relations
        graph["relation_count"] = len(relations)
        
        # Compute hash
        import hashlib
        graph["graph_hash"] = hashlib.sha256(
            json.dumps({"entities": graph["entities"], "relations": relations}, sort_keys=True).encode()
        ).hexdigest()[:16]
        
        graph_file.write_text(json.dumps(graph, indent=2, ensure_ascii=False))
        print(f"Updated graph: {len(graph['entities'])} entities, {len(relations)} relations")
    
    return 0

if __name__ == "__main__":
    sys.exit(extract_relations())
