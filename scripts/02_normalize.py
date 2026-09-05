#!/usr/bin/env python3
"""
Step 2: 数据规范化
五工具链：文本清洗 → 语言检测 → 实体规范化 → 日期标准化 → 数字标准化
"""
from pathlib import Path
import json
from pipeline_compat import normalize_documents

INPUT_FILE = Path(__file__).parent.parent / "outputs" / "01_raw.json"
OUTPUT_FILE = Path(__file__).parent.parent / "outputs" / "02_normalized.json"

def main():
    with open(INPUT_FILE, encoding="utf-8") as f:
        docs = json.load(f)

    normalized = normalize_documents(docs)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(normalized, f, ensure_ascii=False, indent=2)
    print(f"✅ 规范化完成: {len(normalized)} 篇")
    langs = {d['language'] for d in normalized}
    print(f"   语言分布: {langs}")

if __name__ == "__main__":
    main()
