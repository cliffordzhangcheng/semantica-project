#!/usr/bin/env python3
"""Relation extraction with proper entity resolution and evidence grounding"""
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone

# Import entity resolver
import sys; sys.path.insert(0, str(Path(__file__).parent))
from entity_resolver import resolve_entity, clean_entity_name, build_entity_index


def extract_relations_from_corpus(
    corpus_files: List[Path],
    entities: Dict[str, dict],
    evidence_records: List[dict]
) -> Tuple[List[dict], int]:
    """Extract relations from corpus files with proper entity resolution."""
    
    relations = []
    entity_index = build_entity_index(entities)
    relation_id_counter = 1
    
    # Track which relations we've already found to avoid duplicates
    seen_relations = set()
    
    # Known relationship patterns from ontology
    RELATION_PATTERNS = [
        # Pattern: Entity relationship Entity (with known predicates)
        (r'(\w+)\s+(intermediates|provides|transports|located_at|belongs_to|has_contract_with|has_pricing|has_contract_term|operates|owns|publishes|off_hires_at|leases|consolidates|transitions)\s+(\w+(?:\s+\w+)?)', 2),
        # Pattern: From -> Relationship -> To
        (r'(\w+)\s+->\s+(\w+)\s+->\s+(\w+(?:\s+\w+)?)', 3),
    ]
    
    # Additional predicate patterns (property assignments)
    PROPERTY_PATTERNS = [
        (r'(\w+)\s+has_(\w+)\s+([\d$.\/\w-]+)', 'has_'),
        (r'(\w+)\s+is\s+([\d$.\/\w-]+)', 'is'),
    ]
    
    for doc_file in corpus_files:
        content = doc_file.read_text()
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # Skip headers and metadata
            if line.startswith('#') or line.startswith('---') or '|---' in line:
                continue
            
            # Try to match relation patterns
            for pattern, expected_groups in RELATION_PATTERNS:
                matches = re.findall(pattern, line)
                for match in matches:
                    if len(match) >= 2:
                        from_entity = match[0].strip()
                        
                        # Handle multi-part predicates
                        if len(match) >= 3:
                            predicate = match[1] if match[1] else 'related_to'
                            to_entity = match[2].strip()
                        else:
                            predicate = 'related_to'
                            to_entity = ''
                        
                        # Resolve entities
                        subj_id = resolve_entity(entities, from_entity)
                        obj_id = resolve_entity(entities, to_entity) if to_entity else None
                        
                        # Skip if both unknown
                        if subj_id is None and obj_id is None:
                            continue
                        
                        # Create dedup key
                        rel_key = f"{subj_id or from_entity}:{predicate}:{obj_id or to_entity}"
                        if rel_key in seen_relations:
                            continue
                        seen_relations.add(rel_key)
                        
                        # Create relation
                        relation = {
                            "relation_id": f"r{relation_id_counter}",
                            "subject": {
                                "entity_id": subj_id or from_entity,
                                "value": from_entity,
                                "type": entities.get(subj_id, {}).get('type', 'Unknown') if subj_id else 'Unknown'
                            },
                            "predicate": predicate,
                            "object": {
                                "entity_id": obj_id or to_entity,
                                "value": to_entity,
                                "type": entities.get(obj_id, {}).get('type', 'Unknown') if obj_id else 'Unknown'
                            },
                            "evidence_ref": [],
                            "evidence_span": {"start": i, "end": i+1},
                            "provenance": f"pattern:{doc_file.name}:{i}",
                            "relation_status": "EXTRACTED"
                        }
                        
                        # Ground evidence
                        for ev in evidence_records:
                            if ev.get('source_document_id') == doc_file.name:
                                relation['evidence_ref'].append(ev.get('evidence_id'))
                        
                        relations.append(relation)
                        relation_id_counter += 1
                        break
            
            # Try property patterns (has_xxx, is xxx)
            for prop_pattern, prefix in PROPERTY_PATTERNS:
                matches = re.findall(prop_pattern, line)
                for match in matches:
                    if len(match) >= 2:
                        entity = match[0].strip()
                        prop_name = match[1]
                        prop_value = match[2].strip() if len(match) > 2 else ''
                        
                        # Skip if entity not resolved
                        entity_id = resolve_entity(entities, entity)
                        if entity_id is None:
                            continue
                        
                        # Create relation
                        predicate = f"{prefix}{prop_name}" if prefix else prop_name
                        rel_key = f"{entity_id}:{predicate}:{prop_value}"
                        
                        if rel_key not in seen_relations:
                            seen_relations.add(rel_key)
                            
                            relation = {
                                "relation_id": f"r{relation_id_counter}",
                                "subject": {
                                    "entity_id": entity_id,
                                    "value": entity,
                                    "type": entities.get(entity_id, {}).get('type', 'Unknown')
                                },
                                "predicate": predicate,
                                "object": {
                                    "entity_id": None,
                                    "value": prop_value,
                                    "type": "Property"
                                },
                                "evidence_ref": [],
                                "evidence_span": {"start": i, "end": i+1},
                                "provenance": f"property:{doc_file.name}:{i}",
                                "relation_status": "EXTRACTED"
                            }
                            
                            # Ground evidence
                            for ev in evidence_records:
                                if ev.get('source_document_id') == doc_file.name:
                                    relation['evidence_ref'].append(ev.get('evidence_id'))
                            
                            relations.append(relation)
                            relation_id_counter += 1
                            break
    
    return relations, relation_id_counter - 1


def main():
    base = Path(__file__).parent.parent
    outputs_dir = base / "outputs"
    corpus_dir = base / "data" / "raw"
    
    # Load entities
    entities_file = outputs_dir / "06_graph.json"
    if not entities_file.exists():
        print("ERROR: entities file not found")
        return 1
    
    try:
        with entities_file.open() as f:
            graph_data = json.load(f)
            entities = graph_data.get("entities", {})
    except (ValueError, TypeError) as e:
        print(f"ERROR: Failed to load entities: {e}")
        return 1
    
    # Load evidence
    evidence_file = outputs_dir / "evidence.jsonl"
    evidence_records = []
    if evidence_file.exists():
        for line in evidence_file.read_text().strip().split('\n'):
            if line.strip():
                try:
                    evidence_records.append(json.loads(line))
                except (ValueError, TypeError):
                    pass
    
    # Extract relations
    corpus_files = list(corpus_dir.glob("*.md"))
    if not corpus_files:
        print("ERROR: No corpus files found")
        return 1
    
    print(f"Loaded {len(entities)} entities")
    print(f"Loaded {len(evidence_records)} evidence records")
    print(f"Processing {len(corpus_files)} corpus files...")
    
    relations, count = extract_relations_from_corpus(
        corpus_files, entities, evidence_records
    )
    
    # Calculate unknown entity count
    unknown_count = sum(
        1 for r in relations 
        if r.get('subject', {}).get('entity_id') == 'unknown' 
        or r.get('object', {}).get('entity_id') == 'unknown'
        or r.get('subject', {}).get('entity_id') is None
        or r.get('object', {}).get('entity_id') is None
    )
    
    output = {
        "relations": relations,
        "count": count,
        "unknown_entity_count": unknown_count,
        "resolution_rate": f"{((count - unknown_count) / count * 100):.1f}%" if count > 0 else "0%",
        "extraction_timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    output_file = outputs_dir / "04_relations.json"
    with output_file.open('w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nExtracted {count} relations from {len(corpus_files)} documents")
    print(f"Unknown entity count: {unknown_count}")
    print(f"Resolution rate: {output['resolution_rate']}")
    print(f"Output: {output_file}")
    
    return 0


if __name__ == "__main__":
    exit(main())
