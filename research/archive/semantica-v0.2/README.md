# Semantica-AKOS Logistics Reality Ontology v0.2

意保克空运货代业务Ontology规范与实现

## 文件清单

| 文件 | 说明 |
|------|------|
| `SPEC-Semantica-AKOS-Logistics-Reality-Ontology-v0.2.md` | 技术规范文档 |
| `01-SPEC-IMPLEMENTATION-REPORT-v0.2.md` | 实施报告 |
| `02-ONTOLOGY-CANONICAL-SCHEMA-v0.2.yaml` | Ontology Schema |
| `03-ENTITY-CANONICALIZATION-MAP-v0.2.json` | 实体规范化映射 |
| `04-RELATION-NORMALIZATION-REPORT-v0.2.md` | 关系规范化报告 |
| `05-KNOWLEDGE-GRANULARITY-ANALYSIS-v0.2.md` | 知识粒度分析 |
| `06-INCOTERM-INDEPENDENT-MODEL-v0.2.md` | Incoterm独立模型 |
| `07-PARTY-ROLE-RESOLUTION-v0.2.md` | PartyRole解析 |
| `08-SHIPMENT-REALITY-RECORDS-v0.2.json` | 6条航线完整记录 |
| `09-EVIDENCE-MAPS-v0.2.json` | Evidence绑定 |
| `10-SIX-SHIPMENT-RECONSTRUCTION-v0.2.json` | 重建验证结果 |
| `11-AUTOMATED-VALIDATION-RESULTS-v0.2.json` | 自动化验证 |
| `12-GAP-ANALYSIS-AND-RISK-REGISTRY-v0.2.json` | GAP与风险登记 |
| `13-SHADOW-KNOWLEDGE-GRAPH-v0.2.ttl` | RDF知识图谱 |
| `14-VOCABULARY-CHANGE-LOG-v0.2.csv` | 词汇变化日志 |
| `15-FOUNDER-REVIEW-PACKET-v0.2.md` | 创始人审核包 |
| `knowledge-graph.html` | **交互式知识图谱可视化** |

## 快速开始

### 查看知识图谱
双击打开 `knowledge-graph.html` 或使用浏览器访问：
```
minis://workspace/semantica-v0.2/knowledge-graph.html
```

### 功能特性
- 🔄 力导向图可视化
- 🔍 节点点击查看详情
- 🎯 航线高亮筛选
- 📊 统计面板
- ⚠️ GAP分析面板

## 闸门状态

| Gate | 状态 |
|------|------|
| G0 Corpus Integrity | ✅ PASS |
| G1 Canonical Vocabulary | ✅ PASS |
| G2 Ontology Normalization | ✅ PASS |
| G3 Evidence Binding | ✅ PASS |
| G4 Six-Shipment Reality | ✅ PASS |
| G5 Automated Validation | ✅ PASS |
| G6 Shadow Knowledge Graph | ✅ PASS |
| G7 Founder Review | ⏳ PENDING |

## 航线映射

| Shipment ID | 航线 | 起运地 | 目的地 | 日期 |
|-------------|------|--------|--------|------|
| YBK-HAM-DXB-20250507 | HAM-DXB | 汉堡 | 迪拜 | 2025-05-07 |
| YBK-SIN-DWC-20250619 | SIN-DWC | 新加坡 | 迪拜WTC | 2025-06-19 |
| YBK-HAM-DMM-20250620 | HAM-DMM | 汉堡 | 达曼 | 2025-06-20 |
| YBK-ROT-DXB-20250928 | ROT-DXB | 鹿特丹 | 迪拜 | 2025-09-28 |
| YBK-HAM-HKG-20260227 | HAM-HKG | 汉堡 | 香港 | 2026-02-27 |
| YBK-ROT-HKG-20260227 | ROT-HKG | 鹿特丹 | 香港 | 2026-02-27 |

## 关键GAP

| GAP ID | 问题 | 影响 |
|--------|------|------|
| GAP-001 | 无Incoterm数据 | HIGH |
| GAP-002 | 无承运人名称 | HIGH |
| GAP-003 | 无实际重量 | MEDIUM |
| GAP-004 | 无MAWB编号 | MEDIUM |
| GAP-005 | Incoterm碰撞证据稀疏 | LOW |

## GitHub仓库

https://github.com/cliffordzhangcheng/semantica-project/tree/main/semantica-v0.2