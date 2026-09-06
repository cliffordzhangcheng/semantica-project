"""Process Diagnosis Engine — analyzes enterprise processes against CONTAINER-INVESTMENT-ONT.

Usage: python3 diagnosis_engine.py <enterprise_profile.json>
"""
import json
import sys
from collections import defaultdict

# Load graph
with open("outputs/06_graph.json") as f:
    GRAPH = json.load(f)

NODES = {n["id"]: n for n in GRAPH["nodes"]}
EDGES = GRAPH["edges"]

# Build adjacency
OUT_EDGES = defaultdict(list)
IN_EDGES = defaultdict(list)
for e in EDGES:
    OUT_EDGES[e["source"]].append(e)
    IN_EDGES[e["target"]].append(e)


def get_node_text(nid):
    n = NODES.get(nid)
    return n.get("text", nid) if n else nid


def get_node_label(nid):
    n = NODES.get(nid)
    return n.get("label", "UNKNOWN") if n else "UNKNOWN"


def diagnose(profile):
    """Run process diagnosis against enterprise profile."""
    findings = []

    # 1. Asset coverage
    container_nodes = [n for n in GRAPH["nodes"] if n.get("label") in
                       ("ContainerAsset", "ContainerType", "ContainerBatch")]
    container_edges = [e for e in EDGES if e.get("type") in
                       ("owns", "leased_under", "stored_at", "subject_to", "moved_by")]
    findings.append({
        "dimension": "资产覆盖",
        "score": min(len(container_nodes) / 50, 1.0),
        "detail": f"图谱覆盖 {len(container_nodes)} 个集装箱相关实体 / {len(container_edges)} 条资产关系",
        "status": "ok" if len(container_edges) > 5 else "gap"
    })

    # 2. ONEWAY capability
    oneway_nodes = [n for n in GRAPH["nodes"] if n.get("label") in
                    ("OneWayContract", "ContainerOwner", "ContainerAgent", "WishList", "PLAContract")]
    oneway_edges = [e for e in EDGES if e.get("type") in
                    ("intermediates", "charters_under", "publishes", "earns", "off_hires_at", "disposes_via")]
    findings.append({
        "dimension": "单程租赁能力",
        "score": min(len(oneway_edges) / 15, 1.0),
        "detail": f"ONEWAY 关系: {len(oneway_edges)} 条 / 15 目标 (intermediates/charters_under/publishes/earns/off_hires_at/disposes_via)",
        "status": "ok" if len(oneway_edges) >= 10 else "gap"
    })

    # 3. Financial model
    fin_nodes = [n for n in GRAPH["nodes"] if n.get("label") in
                 ("CapitalCommitment", "ProjectSPV", "InvoicePayment", "PUCMargin")]
    fin_edges = [e for e in EDGES if e.get("type") in
                 ("funds", "commits", "generates", "earns")]
    findings.append({
        "dimension": "财务模型",
        "score": min(len(fin_edges) / 6, 1.0),
        "detail": f"资金关系: {len(fin_edges)} 条 (funds/commits/generates/earns)",
        "status": "ok" if len(fin_edges) >= 4 else "gap"
    })

    # 4. Risk coverage
    risk_nodes = [n for n in GRAPH["nodes"] if n.get("label") in
                  ("Risk", "DefaultChain", "EvidenceRecord")]
    risk_edges = [e for e in EDGES if e.get("type") in
                  ("triggers", "supports", "subject_to")]
    findings.append({
        "dimension": "风险覆盖",
        "score": min(len(risk_nodes) / 20, 1.0),
        "detail": f"风险实体: {len(risk_nodes)} 个 / 关系: {len(risk_edges)} 条",
        "status": "ok" if len(risk_nodes) >= 10 else "gap"
    })

    # 5. Operational capability
    ops_nodes = [n for n in GRAPH["nodes"] if n.get("label") in
                 ("Depot", "InspectionRepairOrder", "RepositionTask", "EmptyStockPosition")]
    ops_edges = [e for e in EDGES if e.get("type") in
                 ("stored_at", "off_hires_at", "moved_by", "feeds", "disposes_via")]
    findings.append({
        "dimension": "运营能力",
        "score": min(len(ops_edges) / 15, 1.0),
        "detail": f"运营关系: {len(ops_edges)} 条 (stored_at/off_hires_at/moved_by/feeds/disposes_via)",
        "status": "ok" if len(ops_edges) >= 8 else "gap"
    })

    # 6. Governance
    gov_nodes = [n for n in GRAPH["nodes"] if n.get("label") in
                 ("DecisionCard", "EvidenceRecord", "Gate", "PersonOrg")]
    gov_edges = [e for e in EDGES if e.get("type") in
                 ("governs", "supports", "responsible_for")]
    findings.append({
        "dimension": "治理能力",
        "score": min(len(gov_nodes) / 30, 1.0),
        "detail": f"治理实体: {len(gov_nodes)} 个 / 关系: {len(gov_edges)} 条",
        "status": "ok" if len(gov_nodes) >= 15 else "gap"
    })

    # Overall
    scores = [f["score"] for f in findings]
    overall = sum(scores) / len(scores)

    return {
        "overall_score": round(overall, 3),
        "dimensions": findings,
        "recommendations": generate_recommendations(findings)
    }


def generate_recommendations(findings):
    recs = []
    for f in findings:
        if f["status"] == "gap":
            if f["dimension"] == "单程租赁能力":
                recs.append("加强 ONEWAY 管道：获取承运商 wish list，建立箱东/SOC 箱渠道")
            elif f["dimension"] == "财务模型":
                recs.append("完善资金追踪：建立 SPV 资金隔离 + PUC 结算流程")
            elif f["dimension"] == "运营能力":
                recs.append("补齐运营节点：Depot 费率表 + 调运成本 + 处置渠道")
    return recs


if __name__ == "__main__":
    profile = {}
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            profile = json.load(f)

    result = diagnose(profile)
    print(json.dumps(result, ensure_ascii=False, indent=2))