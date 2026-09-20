"""Document ingestion - generates 01_raw.json from data/raw"""
import sys
import json
from pathlib import Path
from datetime import datetime

def main():
    data_dir = Path("data/raw")
    output_dir = Path("outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if not data_dir.exists():
        print(f"Error: {data_dir} does not exist", file=sys.stderr)
        return 2
    
    files = list(data_dir.iterdir())
    if not files:
        print(f"Error: No files in {data_dir}", file=sys.stderr)
        return 2
    
    # Generate fresh 01_raw.json from current data/raw
    raw_docs = []
    for f in sorted(files):
        if f.is_file():
            content = f.read_text(errors='replace')
            raw_docs.append({
                "source": str(f.name),
                "size_bytes": f.stat().st_size,
                "content_hash": __import__('hashlib').sha256(content.encode()).hexdigest(),
                "content": content[:1000],  # truncate for storage
                "ingested_at": datetime.now().isoformat()
            })
    
    output_file = output_dir / "01_raw.json"
    output_file.write_text(json.dumps({"documents": raw_docs, "count": len(raw_docs)}, indent=2))
    
    print(f"Ingested {len(raw_docs)} documents → outputs/01_raw.json")
    return 0

if __name__ == "__main__":
    sys.exit(main())
