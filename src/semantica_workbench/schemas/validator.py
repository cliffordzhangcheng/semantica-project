"""Schema validation for canonical graph format."""
import json
from pathlib import Path
from typing import Any, Optional


class GraphSchemaValidator:
    """Validate canonical graph against JSON schema."""
    
    REQUIRED_ENTITY_FIELDS = {"id", "name", "type", "provenance"}
    REQUIRED_RELATIONSHIP_FIELDS = {"id", "type", "source", "target", "provenance"}
    REQUIRED_PROVENANCE_FIELDS = {
        "evidence_id", "source_id", "source_document_id",
        "locator", "text_basis", "extractor"
    }
    
    def __init__(self, schema_path: Optional[Path] = None):
        self.schema_path = schema_path or Path(__file__).parent / "canonical.graph.jsonschema"
        self.schema = self._load_schema()
    
    def _load_schema(self) -> dict:
        """Load JSON schema from file."""
        if not self.schema_path.exists():
            return {}
        with open(self.schema_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def validate(self, graph: dict) -> list[dict]:
        """Validate a graph dict against the schema.
        
        Returns a list of error dicts with 'path' and 'message' keys.
        """
        errors = []
        
        # Check top-level required fields
        # Note: metadata is optional for early-stage graphs
        if "entities" not in graph:
            errors.append({
                "path": "entities",
                "message": "Missing required field: entities"
            })
        if "graph_hash" not in graph:
            errors.append({
                "path": "graph_hash",
                "message": "Missing required field: graph_hash"
            })
        
        if not errors:
            # Validate entities
            entity_errors = self._validate_entities(graph.get("entities", []))
            errors.extend([{"path": f"entities.{i}.{e['field']}", "message": e["message"]} 
                          for i, e in enumerate(entity_errors)])
            
            # Validate relationships
            rel_errors = self._validate_relationships(graph.get("relationships", []), graph.get("entities", []))
            errors.extend([{"path": f"relationships.{i}.{e['field']}", "message": e["message"]} 
                          for i, e in enumerate(rel_errors)])
        
        return errors
    
    def _validate_entities(self, entities: list) -> list[dict]:
        """Validate entity list."""
        errors = []
        
        # Empty entities should fail (unless explicitly allowed)
        if not entities:
            errors.append({"field": "entities", "message": "Entities array is empty"})
        
        # Validate each entity
        for i, entity in enumerate(entities):
            # Check required fields
            for field in self.REQUIRED_ENTITY_FIELDS:
                if field not in entity:
                    errors.append({
                        "field": field,
                        "message": f"Entity {i} missing required field: {field}"
                    })
            
            # Check entity type
            if "type" in entity and entity["type"] not in ["PERSON", "ORGANIZATION", "LOCATION", "EVENT", "PRODUCT", "DOCUMENT", "MONEY", "TIME"]:
                errors.append({
                    "field": "type",
                    "message": f"Entity {i} has invalid type: {entity['type']}"
                })
            
            # Check provenance
            if "provenance" in entity:
                provenance_errors = self._validate_provenance(entity["provenance"], f"entity {i}")
                errors.extend(provenance_errors)
        
        return errors
    
    def _validate_relationships(self, relationships: list, entities: list) -> list[dict]:
        """Validate relationship list."""
        errors = []
        
        # Empty relationships is allowed
        if relationships:
            entity_ids = {e["id"] for e in entities if "id" in e}
            
            for i, rel in enumerate(relationships):
                # Check required fields
                for field in self.REQUIRED_RELATIONSHIP_FIELDS:
                    if field not in rel:
                        errors.append({
                            "field": field,
                            "message": f"Relationship {i} missing required field: {field}"
                        })
                
                # Check source/target reference valid entities
                if "source" in rel and rel["source"] not in entity_ids:
                    errors.append({
                        "field": "source",
                        "message": f"Relationship {i} references non-existent entity: {rel['source']}"
                    })
                if "target" in rel and rel["target"] not in entity_ids:
                    errors.append({
                        "field": "target",
                        "message": f"Relationship {i} references non-existent entity: {rel['target']}"
                    })
                
                # Check provenance
                if "provenance" in rel:
                    provenance_errors = self._validate_provenance(rel["provenance"], f"relationship {i}")
                    errors.extend(provenance_errors)
        
        return errors
    
    def _validate_provenance(self, provenance: dict, context: str) -> list[dict]:
        """Validate provenance fields."""
        errors = []
        
        # Empty provenance should fail
        if not provenance:
            errors.append({
                "field": "provenance",
                "message": f"{context} has empty provenance"
            })
            return errors
        
        # Check required provenance fields
        for field in self.REQUIRED_PROVENANCE_FIELDS:
            if field not in provenance or not provenance[field]:
                errors.append({
                    "field": field,
                    "message": f"{context} missing required provenance field: {field}"
                })
        
        return errors
