#!/usr/bin/env python3
"""Entity resolver with name cleaning and canonical mapping"""
import json
import re
from pathlib import Path
from typing import Dict, Optional

# Canonical entity names from ontology
CANONICAL_NAMES = {
    # Business Actors
    'ContainerOwner': 'ContainerOwner',
    'container owner': 'ContainerOwner',
    'COSMOs': 'ContainerOwner',
    'Cosmos Whales': 'ContainerOwner',
    'Carrier': 'Carrier',
    'carrier': 'Carrier',
    'Maersk': 'Carrier',
    'Hapag-Lloyd': 'Carrier',
    'Hapag': 'Carrier',
    'ONE': 'Carrier',
    'Shipping Line': 'Carrier',
    'Freight Forwarder': 'FreightForwarder',
    'Depot': 'Depot',
    'customer': 'Customer',
    'Customer': 'Customer',
    
    # Physical Resources
    'Container': 'Container',
    'container': 'Container',
    'SOCContainer': 'SOCContainer',
    'SOC container': 'SOCContainer',
    'Truck': 'Truck',
    'truck': 'Truck',
    'Equipment': 'Equipment',
    
    # Business Objects
    'OneWayContract': 'OneWayContract',
    'oneway contract': 'OneWayContract',
    'WishList': 'WishList',
    'wishlist': 'WishList',
    'PLAContract': 'PLAContract',
    'Booking': 'Booking',
    'PUC': 'PUC',
    
    # Locations
    'Depot': 'Depot',
    'port': 'Port',
}

def clean_entity_name(raw_name: str) -> str:
    """Extract core entity name from raw NER output."""
    if not raw_name:
        return ''
    
    # Remove parenthetical explanations and notes
    cleaned = re.sub(r'\s*（[^）]*）', '', raw_name)
    cleaned = re.sub(r'\s*\([^)]*\)', '', cleaned)
    
    # Remove Chinese descriptions
    cleaned = re.sub(r'[\u4e00-\u9fa5]+', '', cleaned)
    
    # Take first meaningful word/phrase
    parts = cleaned.strip().split()
    if parts:
        # Return the first part or joined parts up to 3 words
        core = ' '.join(parts[:3])
        return core.strip()
    
    return cleaned.strip()

def resolve_entity(entities: Dict[str, dict], name: str) -> Optional[str]:
    """Resolve entity name to entity_id using cleaned names."""
    if not name:
        return None
    
    # Clean the input name
    cleaned_input = clean_entity_name(name)
    
    # Build reverse lookup: canonical name -> entity_id
    canonical_to_id = {}
    for eid, einfo in entities.items():
        raw_name = einfo.get('name', '')
        canonical = clean_entity_name(raw_name)
        canonical_to_id[canonical] = eid
        
        # Also index by type
        etype = einfo.get('type', '').lower()
        canonical_to_id[etype] = eid
    
    # Direct match with cleaned name
    if cleaned_input in canonical_to_id:
        return canonical_to_id[cleaned_input]
    
    # Partial match - check if input is contained in any canonical name
    for canonical, eid in canonical_to_id.items():
        if cleaned_input.lower() in canonical.lower() or canonical.lower() in cleaned_input.lower():
            return eid
    
    # Check canonical mapping
    for key, canonical in CANONICAL_NAMES.items():
        if cleaned_input.lower() == key.lower() or key.lower() in cleaned_input.lower():
            # Find entity with this canonical name
            for eid, einfo in entities.items():
                e_canonical = clean_entity_name(einfo.get('name', ''))
                if e_canonical == canonical or canonical.lower() in e_canonical.lower():
                    return eid
    
    return None

def build_entity_index(entities: Dict[str, dict]) -> Dict[str, str]:
    """Build comprehensive index from all entity name variations to IDs."""
    index = {}
    
    for eid, einfo in entities.items():
        raw_name = einfo.get('name', '')
        canonical = clean_entity_name(raw_name)
        
        # Index canonical name
        index[canonical] = eid
        
        # Index all word fragments (3+ chars)
        words = re.findall(r'\b\w{3,}\b', canonical.lower())
        for word in words:
            if word not in index:
                index[word] = eid
    
    return index

if __name__ == "__main__":
    # Test
    graph_file = Path("outputs/06_graph.json")
    if graph_file.exists():
        graph = json.loads(graph_file.read_text())
        entities = graph.get('entities', {})
        
        print("=== Cleaned Entity Names ===")
        for eid, e in sorted(entities.items()):
            raw = e.get('name', '')
            cleaned = clean_entity_name(raw)
            print(f"  {eid}: '{raw}' -> '{cleaned}' ({e.get('type')})")
        
        print("\n=== Test Resolutions ===")
        test_names = ['Maersk', 'Container', 'Depot', 'Truck', 'Customer', 'Cosmos', 'Hapag', 'ONE']
        for name in test_names:
            resolved = resolve_entity(entities, name)
            print(f"  '{name}' -> {resolved}")
    else:
        print("No graph file found")
