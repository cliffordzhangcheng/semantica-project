#!/usr/bin/env python3
"""
Step 4: 关系抽取
输入：实体列表 + 原文 → 输出：三元组 (head, relation, tail)
同样支持 pattern / llm / hybrid 三模式
"""
from pathlib import Path
import json
import os
from pipeline_compat import serialize_records

ENTITIES_FILE = Path(__file__).parent.parent / "outputs" / "03_entities.json"
NORMALIZED_FILE = Path(__file__).parent.parent / "outputs" / "02_normalized.json"
OUTPUT_FILE = Path(__file__).parent.parent / "outputs" / "04_relations.json"

def main():
    with open(ENTITIES_FILE, encoding="utf-8") as f:
        entities = json.load(f)

    with open(NORMALIZED_FILE, encoding="utf-8") as f:
        docs = {d["id"]: d["text"] for d in json.load(f)}

    mode = os.getenv("RELATION_MODE", "pattern")
    llm_model = os.getenv("LLM_MODEL", "deepseek-chat")
    api_key = os.getenv("DEEPSEEK_API_KEY")

    if mode in ("llm", "hybrid") and not api_key:
        print("⚠️  LLM 模式需设置 DEEPSEEK_API_KEY，回退到 pattern 模式")
        mode = "pattern"

    print(f"🔧 Relation 模式: {mode}")

    relations = []
    for doc_id, text in docs.items():
        doc_ents = [e for e in entities if e["doc_id"] == doc_id]
        if not doc_ents:
            continue
        relations.extend(
            serialize_records(
                mode,
                text,
                record_type="relations",
                doc_id=doc_id,
                entities=doc_ents,
                llm_model=llm_model,
                api_key=api_key,
            )
        )

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(relations, f, ensure_ascii=False, indent=2)

    print(f"✅ 抽取关系三元组: {len(relations)} 条")
    if relations:
        print(f"   示例: {relations[0]}")

if __name__ == "__main__":
    main()
