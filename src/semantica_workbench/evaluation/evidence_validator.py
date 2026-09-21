"""Official EvidenceValidator - strict contract validation"""
import hashlib
from pathlib import Path
from typing import Dict, Any, Tuple, Optional

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
        """Returns (total, valid_count, errors)"""
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
    
    def validate_contract(self, evidence: dict) -> Tuple[bool, list]:
        """Validate single evidence against full contract"""
        errors = []
        
        # Check required fields
        missing = self.required_fields - set(evidence.keys())
        if missing:
            errors.append(f"Missing fields: {missing}")
        
        # Check locator structure
        if 'locator' in evidence:
            loc = evidence['locator']
            if isinstance(loc, dict):
                if not any(k in loc for k in ['page', 'chunk', 'start', 'end']):
                    errors.append("Locator has no valid position fields")
            elif not isinstance(loc, str):
                errors.append("Locator must be dict or string")
        
        # Check evidence_span
        if 'evidence_span' in evidence:
            span = evidence['evidence_span']
            if not isinstance(span, dict) or 'start' not in span or 'end' not in span:
                errors.append("Invalid evidence_span")
        
        # Check source_hash
        if 'source_hash' not in evidence:
            errors.append("Missing source_hash")
        
        return len(errors) == 0, errors


if __name__ == "__main__":
    import sys
    import json
    from pathlib import Path
    
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
