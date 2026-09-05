"""Compatibility helpers for Semantica 0.6.x.

The Minis project was written against an older Semantica API.  This module
keeps the pipeline scripts small while translating the current API's objects
and dictionaries into the stable JSON contract used by the pipeline.
"""

from __future__ import annotations

import hashlib
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List

from semantica.export import GraphExporter
from semantica.ingest import FileIngestor
from semantica.kg import GraphBuilder
from semantica.normalize import (
    LanguageDetector,
    TextCleaner,
)
from semantica.semantic_extract import Entity, NERExtractor, RelationExtractor


def _record_to_dict(record: Any) -> Dict[str, Any]:
    if is_dataclass(record):
        return asdict(record)
    if hasattr(record, "model_dump"):
        return record.model_dump()
    if hasattr(record, "dict"):
        return record.dict()
    if hasattr(record, "__dict__"):
        return dict(record.__dict__)
    if isinstance(record, dict):
        return dict(record)
    raise TypeError(f"Unsupported Semantica record: {type(record)!r}")


def ingest_documents(data_dir: Path) -> List[Dict[str, Any]]:
    data_dir = Path(data_dir).resolve()
    documents = []
    for file_object in FileIngestor().ingest_directory(str(data_dir), recursive=True):
        raw = file_object.content or b""
        text = raw.decode("utf-8", errors="replace")
        file_path = Path(file_object.path)
        try:
            relative_name = str(file_path.relative_to(data_dir))
        except ValueError:
            relative_name = file_path.name
        document_id = hashlib.sha1(relative_name.encode("utf-8")).hexdigest()[:16]
        documents.append(
            {
                "id": document_id,
                "text": text,
                "metadata": {**(file_object.metadata or {}), "name": relative_name},
            }
        )
    return documents


def normalize_documents(documents: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    cleaner = TextCleaner()
    language_detector = LanguageDetector()
    normalized = []
    for document in documents:
        text = cleaner.clean(document["text"])
        normalized.append(
            {
                **document,
                "text": text,
                "language": language_detector.detect(text),
            }
        )
    return normalized


def _extractor_config(mode: str, llm_model: str, api_key: str | None) -> Dict[str, Any]:
    config: Dict[str, Any] = {}
    if mode in {"llm", "hybrid"}:
        config.update({"model": llm_model, "api_key": api_key})
    return config


def extract_entities(text: str, mode: str = "pattern", llm_model: str = "deepseek-chat", api_key: str | None = None) -> List[Dict[str, Any]]:
    extractor = NERExtractor(
        method=mode,
        **_extractor_config(mode, llm_model, api_key),
    )
    return [_record_to_dict(entity) for entity in extractor.extract(text)]


def extract_relations(text: str, entities: List[Dict[str, Any]], mode: str = "pattern", llm_model: str = "deepseek-chat", api_key: str | None = None) -> List[Dict[str, Any]]:
    extractor = RelationExtractor(
        method=mode,
        **_extractor_config(mode, llm_model, api_key),
    )
    entity_objects = [
        Entity(
            text=entity["text"],
            label=entity.get("label", "ENTITY"),
            start_char=entity.get("start_char", 0),
            end_char=entity.get("end_char", 0),
            confidence=entity.get("confidence", 1.0),
            metadata={**entity.get("metadata", {}), "id": entity.get("id")},
        )
        for entity in entities
    ]
    records = []
    for relation in extractor.extract(text, entity_objects):
        data = _record_to_dict(relation)
        subject = data.pop("subject", {})
        object_ = data.pop("object", {})
        subject_metadata = subject.get("metadata", {})
        object_metadata = object_.get("metadata", {})
        records.append(
            {
                **data,
                "source": subject_metadata.get("id") or subject.get("text"),
                "target": object_metadata.get("id") or object_.get("text"),
                "type": data.get("predicate", "related_to"),
            }
        )
    return records


def serialize_records(
    mode: str,
    text: str,
    *,
    record_type: str,
    doc_id: str,
    entities: List[Dict[str, Any]] | None = None,
    llm_model: str = "deepseek-chat",
    api_key: str | None = None,
) -> List[Dict[str, Any]]:
    if record_type == "entities":
        records = extract_entities(text, mode, llm_model, api_key)
        records = [
            {**record, "id": f"{doc_id}:e{index}"}
            for index, record in enumerate(records)
        ]
    elif record_type == "relations":
        records = extract_relations(text, entities or [], mode, llm_model, api_key)
    else:
        raise ValueError(f"Unknown record type: {record_type}")
    return [{**record, "doc_id": doc_id} for record in records]


def build_graph(entities: List[Dict[str, Any]], relations: List[Dict[str, Any]]) -> Dict[str, Any]:
    # The 0.6.x fuzzy merge can collapse unrelated entities when their
    # metadata is sparse. Preserve source entities by default; deduplication
    # can be enabled as a separate, reviewed stage when domain rules exist.
    return GraphBuilder(merge_entities=False).build(entities, relations)


def export_graph(graph: Dict[str, Any], output_path: Path, format_name: str) -> None:
    GraphExporter().export(graph, output_path, format=format_name)
