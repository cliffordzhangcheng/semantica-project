"""Domain NER fallback for AI-Depot / Logistics Ontology.

Pattern NER fails on Chinese domain entities. This module provides
rule-based domain entity extraction as a fallback when LLM is unavailable.
"""
from __future__ import annotations

import re
from typing import Dict, List, Tuple

# Domain entity patterns: (label, regex, priority)
DOMAIN_PATTERNS: List[Tuple[str, str, int]] = [
    # Shipping Lines
    ("ShippingLine", r"马士基|Maersk|MSC|地中海航运|达飞|CMA CGM|中远|COSCO|长荣|Evergreen|阳明|Yang Ming|Hapag-Lloyd|赫伯罗特|ONE|海洋网联|以星|ZIM|HMM|现代|万海|Wan Hai", 10),
    # Ports
    ("Port", r"厦门|上海|宁波|深圳|广州|天津|青岛|大连|香港|新加坡|鹿特丹|汉堡|洛杉矶|长滩|纽约|釜山|东京|横滨|神户|名古屋|蒙巴萨|肯尼亚|雅加达|巴生|丹戎不碌", 8),
    # Container Types
    ("ContainerType", r"40HC|40HQ|40\'HC|20GP|20\'GP|45G1|42G1|22G1|4500|冷藏箱|冻柜|开顶箱|框架箱|罐箱", 9),
    # Freight Forwarders
    ("FreightForwarder", r"货代|Forwarder|NVOCC|无船承运|物流商|Logistics", 7),
    # Depot / Yard
    ("Depot", r"堆场|Depot|Yard|集装箱堆场|货运站|CFS|Container Freight Station", 7),
    # Business Roles
    ("Shipper", r"发货人|Consignor|Shipper|货主", 6),
    ("Consignee", r"收货人|Consignee|收货方", 6),
    ("Trucker", r"拖车|Trucker|Driver|司机|车队", 6),
    # Documents
    ("Document", r"提单|B/L|BillOfLading|装箱单|PackingList|舱单|Manifest|订舱|Booking|EIR|设备交接单|报关单|CustomsDecl", 5),
    # Financial
    ("Currency", r"USD|美金|美元|EUR|RMB|人民币|CNY|JPY|日元|HKD|港币", 5),
    ("RentRate", r"日租金|per diem|Per Diem|每天\d+|\$\d+\.?\d*", 6),
    # Lease Terms
    ("LeaseTerm", r"租期|lease term|\d+年|\d+月|free days|免费期|免箱期", 6),
    # Equipment
    ("Equipment", r"岸桥|起重机|Cranes?|龙门吊|RTG|QC|正面吊|Side.?lifter|Top.?lifter|Forklift|叉车|地磅|WeighBridge", 5),
    # Insurance
    ("Insurance", r"保险|Insurance|全损|Total Loss|CLAUS", 4),
    # Risk
    ("Risk", r"违约|Default|坏账|Bad Debt|风险|Risk|信用|Credit|制裁|Sanctions", 5),
    # KPI / Metrics
    ("Metric", r"利用率|Utilization|IRR|ROI|回报率|残值|Residual|空置|Idle|周转|Turnover|回本|Payback|OOS|离场率", 6),
    # Organization
    ("Organization", r"公司|Company|Corp|Ltd|Limited|Inc|集团|Group|Co\.|SOE|国企|民企", 4),
    # Agreement / Contract
    ("Contract", r"合同|Contract|Agreement|协议|Term|T&C|SLA|KPI附录|费率表|Tariff", 5),
    # Action / Event
    ("Action", r"采购|Purchase|租赁|Lease|出租|Rent|调箱|Reposition|维修|Repair|交付|Deliver|归还|Return|出售|Sell|处置|Dispose", 5),
    # Container Investment domain — SPV / Capital / Investor
    ("SPV", r"SPV|项目公司|投资主体|Project SPV|离岸|Offshore", 7),
    ("CapitalProvider", r"投资人|资本提供|Capital Provider|投资方|资金方|Fund", 6),
    ("Operator", r"运营管理人|Operator|源海通|Cosmos Whales|鲸航", 7),
    ("Lessee", r"租箱客户|Lessee|租客|承租方|买家|Buyer", 6),
    ("CapitalCommitment", r"资金承诺|Capital Commitment|承诺资金|投资额度", 6),
    ("DecisionCard", r"Decision Card|决策卡|决策|Decision", 5),
    ("EvidenceRecord", r"Evidence Record|证据记录|证据|Evidence", 5),
    ("Gate", r"闸门|Gate|G\d|G0|G1|G2|G3|G4|G5", 6),
    ("RepositionTask", r"调箱任务|Reposition Task|调箱单", 5),
    ("InspectionRepairOrder", r"检验|Inspection|维修单|Repair Order|修箱", 5),
    ("InvoicePayment", r"发票|Invoice|回单|Receipt|收款凭证|付款|Payment", 5),
    ("TradeLane", r"航线|Trade Lane|贸易航线|起讫|Origin.*Destination", 5),
    ("ContainerBatch", r"批次|Container Batch|Batch", 5),
    # CI-ONT specific entity patterns
    ("CapitalCommitment", r"Capital Commitment|资金承诺|承诺资金|投资额度|Capital Commitment", 6),
    ("ProjectSPV", r"SPV|项目公司|投资主体|Project SPV|离岸公司|Offshore", 7),
    ("CapitalProvider", r"投资方|投资人|资本提供|Capital Provider|资金方|Fund", 6),
    ("Operator", r"运营管理人|Operator|源海通|Cosmos Whales|鲸航商社", 7),
    ("Lessee", r"Lessee|租箱客户|承租方|租客|买家|Buyer", 6),
    ("LeaseContract", r"Lease Contract|租赁合同|租约|LeaseContract|租约合同", 6),
    ("PurchaseContract", r"Purchase Contract|采购合同|PurchaseContract|采购单", 6),
    ("DecisionCard", r"Decision Card|决策卡|DecisionCard|决策记录", 5),
    ("EvidenceRecord", r"Evidence Record|证据记录|EvidenceRecord|证据单", 5),
    ("RepositionTask", r"Reposition Task|调箱任务|调箱单|RepositionTask", 5),
    ("InspectionRepairOrder", r"Inspection Repair Order|检验维修单|修箱单|InspectionRepairOrder", 5),
    ("InvoicePayment", r"Invoice Payment|收款凭证|InvoicePayment|回款单", 5),
    ("TradeLane", r"Trade Lane|贸易航线|航线网络|TradeLane", 5),
    ("ContainerAsset", r"Container Asset|箱资产|ContainerAsset|资产箱", 6),
    ("DefaultChain", r"Default Chain|违约链|DefaultChain|违约处理", 5),
    ("PersonOrg", r"Person|Organization|人员|组织|PersonOrg", 4),
    # ONEWAY / 箱贸 domain
    ("OneWayContract", r"One.?Way.?Container.?Lease|单程租箱|单程租赁|ONEWAY|One.?Way.?Lease", 7),
    ("ContainerOwner", r"箱东|Container.?Owner|SOC.?Owner|箱产权方", 6),
    ("ContainerAgent", r"箱代|Container.?Agent|箱务代理|中间人|中介", 6),
    ("WishList", r"Wish.?List|箱型需求|需求清单|箱型清单", 6),
    ("PLAContract", r"PLA|协议.?运量|Protocol.?Lease.?Agreement|最低箱量", 6),
    ("SOCContainer", r"SOC|货主自有箱|Shipper.?Own.?Container|SOC.?Container", 7),
    ("PUCMargin", r"PUC|Pick.?Up.?Charge|提箱费|箱价差", 6),
    ("OffHireCondition", r"Off.?Hire|还箱条件|还箱标准|Redelivery", 6),
    ("EmptyStockPosition", r"空箱库存|Empty.?Stock|空箱积压|空箱位置", 6),
    ("DisposalChannel", r"处置渠道|Disposal.?Channel|二手市场|拆解|翻新|报废", 5),
]


def extract_domain_entities(text: str) -> List[Dict]:
    """Extract domain entities using regex patterns with priority ordering."""
    entities = []
    seen_spans = set()

    # Sort by priority descending
    sorted_patterns = sorted(DOMAIN_PATTERNS, key=lambda x: -x[2])

    for label, pattern, priority in sorted_patterns:
        for match in re.finditer(pattern, text):
            span = (match.start(), match.end())
            # Skip overlapping spans (first match wins by priority)
            if any(s[0] <= span[0] < s[1] or s[0] <= span[1] < s[1] for s in seen_spans):
                continue
            seen_spans.add(span)
            entities.append({
                "text": match.group(),
                "label": label,
                "start_char": match.start(),
                "end_char": match.end(),
                "confidence": min(0.5 + priority * 0.05, 0.95),
                "metadata": {"extraction_method": "domain_pattern", "priority": priority},
            })

    # Sort by position
    entities.sort(key=lambda e: e["start_char"])
    return entities


def augment_with_domain(text: str, existing_entities: List[Dict]) -> List[Dict]:
    """Merge Semantica pattern results with domain patterns."""
    domain = extract_domain_entities(text)
    existing_spans = {(e["start_char"], e["end_char"]) for e in existing_entities}

    # Add domain entities that don't overlap
    for de in domain:
        span = (de["start_char"], de["end_char"])
        if not any(s[0] <= span[0] < s[1] or s[0] <= span[1] < s[1] for s in existing_spans):
            existing_entities.append(de)

    # Re-sort
    existing_entities.sort(key=lambda e: e["start_char"])
    return existing_entities


if __name__ == "__main__":
    test = "马士基在厦门部署40HC集装箱，向货代Forwarder提供长租服务，日租金约1.5美元。"
    entities = extract_domain_entities(test)
    print(f"Text: {test}")
    print(f"Extracted {len(entities)} domain entities:")
    for e in entities:
        print(f"  [{e['label']}] '{e['text']}' (conf={e['confidence']:.2f})")