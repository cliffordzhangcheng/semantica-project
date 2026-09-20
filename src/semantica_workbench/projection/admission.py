#!/usr/bin/env python3
"""Admission control for projections"""
from typing import Any, Dict


class ProjectionAdmission:
    """Control admission of projections to ontology"""
    
    def is_admitted(self, gate_result: Dict[str, Any]) -> bool:
        """Check if projection is admitted based on gate results"""
        overall = gate_result.get("overall", "NOT_EVALUATED")
        
        # FAIL must reject
        if overall == "FAIL":
            return False
        
        # NOT_EVALUATED means gates weren't run
        if overall == "NOT_EVALUATED":
            return False
        
        # Only PASS admits
        return overall == "PASS"
    
    def validate(self, projection: Dict[str, Any]) -> list[str]:
        """Validate projection before admission"""
        errors = []
        
        if "status" not in projection:
            errors.append("Missing 'status' field")
        elif projection["status"] == "FAILED":
            errors.append("Projection status is FAILED")
        
        if "graph_hash" not in projection:
            errors.append("Missing 'graph_hash' field")
        
        if "metrics" not in projection or not projection.get("metrics"):
            errors.append("Missing or empty 'metrics' field")
        
        return errors
