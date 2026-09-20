"""Document ingestion - direct implementation"""
import sys
from pathlib import Path

def main():
    data_dir = Path("data/raw")
    if not data_dir.exists() or not any(data_dir.iterdir()):
        print(f"Error: No input documents in {data_dir}", file=sys.stderr)
        return 2
    # Ingest is a no-op for now (data is already in raw/)
    print(f"Ingested {len(list(data_dir.iterdir()))} documents")
    return 0

if __name__ == "__main__":
    sys.exit(main())
