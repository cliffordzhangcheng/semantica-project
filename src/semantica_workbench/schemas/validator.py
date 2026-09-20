#!/usr/bin/env python3
"""Schema validation for canonical graphs"""
import json
from pathlib import Path
from typing import Any


class GraphSchemaValidator:
    """Validate canonical graph structure"""
    
    REQUIRED_ENTITY_FIELDS = {"id", "type", "text_basis", "provenance"}
    REQUIRED_PROVENANCE_FIELDS = {
        "evidence_id", "source_id", "source_document_id",
        "locator", "text_basis", "extractor"
    }
    
    def validate(self, graph: dict) -> list[str]:
        """Validate graph structure, return list of errors"""
        errors = []
        
        if "entities" not in graph or not graph["entities"]:
            errors.append("Missing or empty 'entities' field")
        
        if "relationships" not in graph:
            errors.append("Missing 'relationships' field")
        
        if "graph_hash" not in graph:
            errors.append("Missing 'graph_hash' field")
        
        if "entities" in graph and graph["entities"]:
            entity_ids = set()
            for i, entity in enumerate(graph["entities"]):
                entity_errors = self._validate_entity(entity, i)
                errors.extend(entity_errors)
                if "id" in entity:
                    entity_ids.add(entity["id"])
            
            # Check relationship references
            if "relationships" in graph:
                for rel in graph["relationships"]:
                    if "source_id" in rel and rel["source_id"] not in entity_ids:
                        errors.append(f"Relationship references non-existent source: {rel['source_id']}")
                    if "target_id" in rel and rel["target_id"] not in entity_ids:
                        errors.append(f"Relationship references non-existent target: {rel['target_id']}")
        
        return errors
    
    def _validate_entity(self, entity: dict, index: int) -> list[str]:
        """Validate single entity"""
        errors = []
        prefix = f"Entity[{index}]"
        
        if "id" not in entity or not entity["id"]:
            errors.append(f"{prefix}: Missing 'id'")
        
        if "type" not in entity or not entity["type"]:
            errors.append(f"{prefix}: Missing or empty 'type'")
        
        if "text_basis" not in entity or not entity["text_basis"]:
            errors.append(f"{prefix}: Missing 'text_basis'")
        
        if "provenance" not in entity:
            errors.append(f"{prefix}: Missing 'provenance'")
        elif not entity["provenance"]:
            errors.append(f"{prefix}: Empty 'provenance'")
        else:
            for field in self.REQUIRED_PROVENANCE_FIELDS:
                if field not in entity["provenance"]:
                    errors.append(f"{prefix}.provenance: Missing '{field}'")
        
        return errors
