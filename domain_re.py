"""Domain Relation Extractor — pattern-based RE for logistics domain."""
from __future__ import annotations
import re
from typing import Dict, List, Tuple

DOMAIN_REL_PATTERNS: List[Tuple[str, str, str, int]] = [
    ("operates_at", r"马士基|Maersk|MSC|达飞|中远|长荣|阳明|Hapag|ONE|以星|HMM|万海", r"厦门|上海|宁波|深圳|广州|天津|青岛|大连|香港|新加坡|鹿特丹|汉堡|洛杉矶|长滩|纽约|釜山", 30),
    ("deploys", r"马士基|Maersk|MSC|达飞|中远|长荣|阳明|Hapag|ONE|以星|HMM|万海", r"40HC|40HQ|20GP|20GP|45G1|42G1|22G1|冷藏箱|冻柜|开顶箱|框架箱", 20),
    ("leases_to", r"马士基|Maersk|MSC|CMA|中远|长荣|阳明|Hapag|ONE|以星|HMM|万海", r"货代|Forwarder|NVOCC|无船承运|物流商|租箱|租赁|出租", 35),
    ("has_metric", r"40HC|40HQ|20GP|20GP|冷藏箱|冻柜|集装箱", r"利用率|Utilization|空置|Idle|周转|Turnover|IRR|ROI|残值|Residual|出租率|回本|Payback", 50),
    ("sets_rate", r"马士基|Maersk|MSC|达飞|中远|长荣|阳明|Hapag|ONE|以星|HMM|万海", r"日租金|per diem|租金|USD|\\$\\d+|RMB", 10),
    ("subject_to", r"40HC|40HQ|20GP|20GP|集装箱|箱", r"租期|lease term|free days|免费期|免箱期|\\d+年|\\d+月", 10),
    ("serves", r"厦门|上海|宁波|深圳|广州|天津|青岛|大连|香港|新加坡|鹿特丹|釜山", r"马士基|Maersk|MSC|达飞|中远|长荣|阳明|Hapag|ONE|以星|HMM|万海", 30),
    ("books", r"货代|Forwarder|NVOCC|无船承运", r"40HC|40HQ|20GP|20GP|集装箱|箱", 15),
    ("stored_at", r"40HC|40HQ|20GP|20GP|集装箱|箱", r"堆场|Depot|Yard|货运站|CFS|Container Freight Station", 15),
    ("contracts", r"马士基|Maersk|MSC|达飞|中远|长荣|阳明|Hapag|ONE|以星|HMM|万海", r"堆场|Depot|Yard|货运站|CFS|码头|Terminal", 20),
    ("funds", r"投资方|投资人|资本提供|Capital Provider|资金方|Fund", r"SPV|项目公司|投资主体|Project SPV|离岸|Offshore", 25),
    ("owns", r"SPV|项目公司|投资主体|Project SPV", r"Container Asset|集装箱|40HC|20GP|Container", 30),
    ("contains", r"Container Batch|批次|Batch", r"Container Asset|集装箱|40HC|20GP", 20),
    ("manufactured_by", r"40HC|20GP|集装箱|Container", r"Manufacturer|箱厂|CIMC|太平|中集|制造商", 25),
    ("purchased_under", r"SPV|项目公司|投资主体|Project SPV", r"Purchase Contract|采购合同|PurchaseContract", 25),
    ("leased_under", r"40HC|20GP|集装箱|Container", r"Lease Contract|租赁合同|租约|LeaseContract", 25),
    ("leased_to", r"Lease Contract|租赁合同|租约|LeaseContract", r"Lessee|租箱客户|承租方|买家|Buyer", 25),
    ("operates_on", r"40HC|20GP|集装箱|Container", r"Trade Lane|航线|贸易航线", 25),
    ("moved_by", r"40HC|20GP|集装箱|Container", r"Reposition|调箱|Reposition Task|调箱任务", 25),
    ("generates", r"Lease|租赁|Sale|出售|买卖|租约", r"Invoice|发票|Receipt|回单|收款凭证|InvoicePayment", 25),
    ("governs", r"Decision Card|决策卡|DecisionCard|Decision", r"Action|动作|Event|事件|Approve|Buy|Lease|Sell|Release", 25),
    ("supports", r"Evidence Record|证据记录|EvidenceRecord|Evidence|证据", r"Object|Relation|Event|Decision|Entity|对象|关系|事件|决策", 30),
    ("responsible_for", r"Operator|运营管理人|源海通|Cosmos Whales|鲸航", r"Object|Action|Event|Decision|Asset|资产|Container|箱|Mission|任务", 30),
    ("commits", r"投资方|投资人|资本提供|Capital Provider|资金方", r"Capital Commitment|资金承诺|承诺资金|投资额度", 25),
    ("triggers", r"Lessee|租箱客户|承租方|违约|Default", r"Default Chain|违约链|Payment Arrears|欠款|坏账|Bad Debt", 25),
    # ONEWAY v0.2
    ("intermediates", r"箱代|Container.?Agent|中间人", r"One.?Way|单程|OneWayContract", 30),
    ("provides", r"箱东|Container.?Owner|SOC.?Owner", r"SOC|SOCContainer|货主自有箱", 25),
    ("publishes", r"承运商|Carrier|马士基|Maersk|ONE|CMA", r"Wish.?List|箱型需求|需求清单", 30),
    ("charters_under", r"承运商|Carrier|马士基|Maersk|ONE|CMA|Hapag", r"One.?Way|单程|OneWayContract", 30),
    ("earns", r"箱代|Container.?Agent|中间人", r"PUC|Pick.?Up.?Charge|提箱费|箱价差", 25),
    ("off_hires_at", r"Container|箱|ContainerAsset", r"Depot|堆场|还箱点|Off.?Hire", 30),
    ("disposes_via", r"Container|箱|ContainerAsset", r"Disposal.?Channel|处置渠道|二手市场|拆解", 30),
    ("guarantees", r"PLA|协议.?运量|PLAContract", r"Minimum.?Volume|最低箱量|协议箱量", 25),
    ("feeds", r"Empty.?Stock|空箱库存|EmptyStockPosition", r"Reposition|调箱|RepositionTask", 30),
    ("sells_to", r"箱东|Container.?Owner|SOC.?Owner", r"箱代|Container.?Agent|中间人", 30),
]


def extract_domain_relations(text: str, entities: List[Dict]) -> List[Dict]:
    relations = []
    for rel_type, subj_pat, obj_pat, window in DOMAIN_REL_PATTERNS:
        subj_matches = list(re.finditer(subj_pat, text))
        obj_matches = list(re.finditer(obj_pat, text))
        for sm in subj_matches:
            for om in obj_matches:
                distance = om.start() - sm.end()
                if 0 < distance <= window:
                    subj_text = sm.group()
                    obj_text = om.group()
                    subj_id = _find_entity_id(subj_text, entities)
                    obj_id = _find_entity_id(obj_text, entities)
                    if subj_id and obj_id:
                        relations.append({
                            "source": subj_id,
                            "target": obj_id,
                            "type": rel_type,
                            "confidence": min(0.9 - distance * 0.01, 0.9),
                            "metadata": {"extraction_method": "domain_pattern", "distance": distance},
                        })
    seen = set()
    unique = []
    for r in relations:
        key = (r["source"], r["target"], r["type"])
        if key not in seen:
            seen.add(key)
            unique.append(r)
    return unique


def _find_entity_id(text: str, entities: List[Dict]) -> str:
    for e in entities:
        if e["text"] == text:
            return e.get("id", e["text"])
    for e in entities:
        et = e["text"]
        if et in text or text in et:
            return e.get("id", e["text"])
    return None