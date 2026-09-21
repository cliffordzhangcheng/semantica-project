"""Official EvidenceValidator - strict contract validation"""
import json
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

class EvidenceContract:
    """Full evidence contract per CR-SI-02"""
    REQUIRED_FIELDS = {
        'evidence_id', 'source_id', 'source_document_id', 'locator', 
        'text_basis', 'extractor'
    }
    LOCATOR_FIELDS = {'page', 'chunk', 'start', 'end'}

class EvidenceValidator:
    """Strict evidence validation - no weak fallbacks"""
    
    def __init__(self):
        self.required_fields = EvidenceContract.REQUIRED_FIELDS
    
    def validate(self, evidence_file: Path) -> Tuple[int, int, list]:
        """Validate evidence file, returns (total, valid, errors)"""
        if not evidence_file.exists():
            return 0, 0, ["Evidence file missing"]
        
        total = 0
        valid = 0
        errors = []
        
        for line_num, line in enumerate(evidence_file.read_text().strip().split('\n'), 1):
            if not line.strip():
                continue
            total += 1
            try:
                ev = json.loads(line)
                missing = self.required_fields - set(ev.keys())
                if missing:
                    errors.append(f"Line {line_num}: missing {missing}")
                else:
                    valid += 1
            except json.JSONDecodeError as e:
                errors.append(f"Line {line_num}: invalid JSON - {e}")
        
        return total, valid, errors
    
    def validate_evidence(self, evidence: dict) -> List[str]:
        """Validate single evidence record - for tests compatibility"""
        errors = []
        
        # Check required fields
        missing = self.required_fields - set(evidence.keys())
        if missing:
            errors.append(f"Missing required fields: {missing}")
        
        # Check locator structure
        if 'locator' in evidence:
            loc = evidence['locator']
            if loc and not isinstance(loc, str):
                errors.append("Locator must be a string")
        
        # Check evidence_span if present
        if 'evidence_span' in evidence:
            span = evidence['evidence_span']
            if span and not isinstance(span, dict):
                errors.append("evidence_span must be a dict")
        
        # Check source_hash if present
        if 'source_hash' in evidence:
            if not isinstance(evidence['source_hash'], str):
                errors.append("source_hash must be a string")
        
        return errors
    
    def validate_contract(self, evidence: dict) -> Tuple[bool, list]:
        """Validate single evidence against full contract - returns (is_valid, errors)"""
        errors = self.validate_evidence(evidence)
        return len(errors) == 0, errors


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: evidence_validator.py <evidence_file>")
        sys.exit(1)
    
    validator = EvidenceValidator()
    evidence_file = Path(sys.argv[1])
    
    total, valid, errors = validator.validate(evidence_file)
    
    print(f"Evidence Validation Report")
    print(f"Total: {total}")
    print(f"Valid: {valid}")
    print(f"Invalid: {total - valid}")
    
    if errors:
        print(f"\nErrors:")
        for e in errors[:10]:
            print(f"  - {e}")
    
    sys.exit(0 if total == valid and not errors else 1)