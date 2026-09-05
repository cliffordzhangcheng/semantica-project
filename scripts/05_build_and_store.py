#!/usr/bin/env python3
"""
Step 5: 构建知识图谱 & 统一存储后端
- GraphBuilder.merge_entities=True 自动合并同指实体
- GraphStore 仅改 backend 参数即可在 NetworkX/Neo4j/FalkorDB/AGE 间切换
"""
from pathlib import Path
import json
import pickle
from pipeline_compat import build_graph

ENTITIES_FILE = Path(__file__).parent.parent / "outputs" / "03_entities.json"
RELATIONS_FILE = Path(__file__).parent.parent / "outputs" / "04_relations.json"
CONFIG_FILE = Path(__file__).parent.parent / "config" / "backend.yaml"
GRAPH_PKL = Path(__file__).parent.parent / "outputs" / "05_graph.pkl"

def main():
    with open(ENTITIES_FILE, encoding="utf-8") as f:
        entities = json.load(f)
    with open(RELATIONS_FILE, encoding="utf-8") as f:
        relations = json.load(f)

    graph = build_graph(entities, relations)
    print(
        f"📊 图谱构建完成: {len(graph['entities'])} 节点, "
        f"{len(graph['relationships'])} 边"
    )

    # Semantica 0.6.x returns a portable graph dictionary.  Persisting this
    # contract keeps the default NetworkX-like pipeline local and avoids
    # pretending that the new GraphStore supports the old `save/load` API.
    with open(GRAPH_PKL, "wb") as f:
        pickle.dump(graph, f)
    print(f"💾 已保存图对象: {GRAPH_PKL}")

if __name__ == "__main__":
    main()
