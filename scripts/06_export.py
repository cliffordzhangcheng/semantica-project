#!/usr/bin/env python3
"""
Step 6: 导出闭环
支持 8+ 种格式：JSON/GraphML/Turtle/SIF/CSV/GEXF/FAISS/...
下游可直接接入 Gephi、Neo4j、SPARQL、RAG 系统
"""
from pathlib import Path
import pickle
from pipeline_compat import export_graph

GRAPH_PKL = Path(__file__).parent.parent / "outputs" / "05_graph.pkl"
OUTPUT_DIR = Path(__file__).parent.parent / "outputs"

def main():
    with open(GRAPH_PKL, "rb") as f:
        G = pickle.load(f)

    formats = {
        "json":    OUTPUT_DIR / "06_graph.json",
        "graphml": OUTPUT_DIR / "06_graph.graphml",
        "turtle":  OUTPUT_DIR / "06_graph.ttl",
        "sif":     OUTPUT_DIR / "06_graph.sif",      # Neo4j 批量导入
        "csv_n":   OUTPUT_DIR / "06_nodes.csv",
        "csv_e":   OUTPUT_DIR / "06_edges.csv",
        "gexf":    OUTPUT_DIR / "06_graph.gexf",     # Gephi 可视化
    }

    success = []
    failed = []
    for fmt, path in formats.items():
        try:
            export_graph(G, path, fmt)
            success.append((fmt, path))
            print(f"✅ {fmt:6s} → {path}")
        except Exception as e:
            failed.append((fmt, str(e)))
            print(f"❌ {fmt:6s} 失败: {e}")

    print(f"\n🎉 导出完成: 成功 {len(success)} 个, 失败 {len(failed)} 个")
    print("\n📦 下游使用建议:")
    print("  - JSON/CSV → 程序处理、ETL 管道")
    print("  - GraphML/GEXF → Gephi、Cytoscape 可视化")
    print("  - Turtle → 语义网 / SPARQL 端点")
    print("  - SIF → Neo4j LOAD CSV")

if __name__ == "__main__":
    main()
