#!/usr/bin/env python3
"""
Step 3: 实体抽取 (NER)
三模式：pattern(免费快) / llm(高准) / hybrid(自动降级)
通过环境变量 DEEPSEEK_API_KEY 切换 LLM 模式
"""
from pathlib import Path
import json
import os
from pipeline_compat import serialize_records

INPUT_FILE = Path(__file__).parent.parent / "outputs" / "02_normalized.json"
OUTPUT_FILE = Path(__file__).parent.parent / "outputs" / "03_entities.json"

def main():
    with open(INPUT_FILE, encoding="utf-8") as f:
        docs = json.load(f)

    # 模式选择：pattern / llm / hybrid
    # LLM 模式需设置环境变量 DEEPSEEK_API_KEY
    mode = os.getenv("NER_MODE", "pattern")
    llm_model = os.getenv("LLM_MODEL", "deepseek-chat")
    api_key = os.getenv("DEEPSEEK_API_KEY")

    if mode in ("llm", "hybrid") and not api_key:
        print("⚠️  LLM 模式需设置 DEEPSEEK_API_KEY，回退到 pattern 模式")
        mode = "pattern"

    print(f"🔧 NER 模式: {mode}")

    entities = []
    for d in docs:
        entities.extend(
            serialize_records(
                mode,
                d["text"],
                record_type="entities",
                doc_id=d["id"],
                llm_model=llm_model,
                api_key=api_key,
            )
        )

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(entities, f, ensure_ascii=False, indent=2)

    print(f"✅ 抽取实体: {len(entities)} 个")
    if entities:
        from collections import Counter
        print(f"   类型分布: {dict(Counter(e['label'] for e in entities))}")

if __name__ == "__main__":
    main()
