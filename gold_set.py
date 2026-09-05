"""Gold Set for AI-Depot Ontology NER/RE evaluation.

Aligned with domain_ner.py patterns — these are the entities
the domain regex patterns are designed to extract.
"""
GOLD_TEXT = (
    "马士基(Maersk)在厦门港口部署了40HC集装箱，"
    "向货代Forwarder提供长租服务，日租金约1.5美元。"
    "租期3年，预计利用率85%，IRR约12%。"
)

GOLD_ENTITIES = [
    {"text": "马士基", "label": "ShippingLine", "start_char": 0, "end_char": 3},
    {"text": "Maersk", "label": "ShippingLine", "start_char": 4, "end_char": 10},
    {"text": "厦门", "label": "Port", "start_char": 13, "end_char": 15},
    {"text": "40HC", "label": "ContainerType", "start_char": 20, "end_char": 24},
    {"text": "货代", "label": "FreightForwarder", "start_char": 31, "end_char": 33},
    {"text": "Forwarder", "label": "FreightForwarder", "start_char": 34, "end_char": 43},
    {"text": "美元", "label": "Currency", "start_char": 58, "end_char": 60},
    {"text": "租期", "label": "LeaseTerm", "start_char": 62, "end_char": 64},
    {"text": "利用率", "label": "Metric", "start_char": 72, "end_char": 76},
    {"text": "IRR", "label": "Metric", "start_char": 80, "end_char": 83},
]

GOLD_RELATIONS = [
    {"source": "马士基", "target": "厦门", "type": "operates_at", "confidence": 0.9},
    {"source": "马士基", "target": "40HC", "type": "deploys", "confidence": 0.85},
    {"source": "马士基", "target": "货代", "type": "leases_to", "confidence": 0.8},
    {"source": "40HC", "target": "利用率", "type": "has_metric", "confidence": 0.75},
]