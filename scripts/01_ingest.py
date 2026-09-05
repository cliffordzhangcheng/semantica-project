#!/usr/bin/env python3
"""
Step 1: 数据摄取与解析
使用 FileIngestor 统一接入本地文件（PDF/Word/HTML/JSON/CSV/MD/TXT...）
"""
from pathlib import Path
import json
import sys
from pipeline_compat import ingest_documents

DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR = Path(__file__).parent.parent / "outputs"

def main():
    DATA_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)

    if not any(DATA_DIR.iterdir()):
        print(f"⚠️  {DATA_DIR} 为空，请先放入 PDF/Word/HTML/JSON 等文件")
        print(f"   示例：cp /var/minis/attachments/*.pdf {DATA_DIR}/")
        sys.exit(1)

    docs = ingest_documents(DATA_DIR)
    print(f"✅ 摄入文档数: {len(docs)}")

    # 保存中间结果
    output_file = OUTPUT_DIR / "01_raw.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(
            docs,
            f, ensure_ascii=False, indent=2
        )
    print(f"💾 已保存: {output_file}")

if __name__ == "__main__":
    main()
