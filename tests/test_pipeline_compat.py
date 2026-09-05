import json
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from pipeline_compat import (  # noqa: E402
    build_graph,
    export_graph,
    ingest_documents,
    normalize_documents,
    serialize_records,
)


class PipelineCompatibilityTests(unittest.TestCase):
    def test_current_semantica_pipeline_runs_without_legacy_imports(self):
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp) / "data"
            output_dir = Path(tmp) / "outputs"
            data_dir.mkdir()
            (data_dir / "sample.txt").write_text(
                "Alice works for Acme Corp.", encoding="utf-8"
            )

            documents = ingest_documents(data_dir)
            self.assertEqual(len(documents), 1)
            self.assertIn("text", documents[0])

            normalized = normalize_documents(documents)
            self.assertEqual(len(normalized), 1)
            self.assertTrue(normalized[0]["text"])

            entities = serialize_records(
                "pattern",
                normalized[0]["text"],
                record_type="entities",
                doc_id=normalized[0]["id"],
            )
            self.assertIsInstance(entities, list)

            relation_entities = [
                {
                    "id": "doc:e0",
                    "text": "Alice",
                    "label": "PERSON",
                    "start_char": 0,
                    "end_char": 5,
                },
                {
                    "id": "doc:e1",
                    "text": "Acme Corp",
                    "label": "ORG",
                    "start_char": 16,
                    "end_char": 25,
                },
            ]
            relations = serialize_records(
                "pattern",
                "Alice works for Acme Corp.",
                record_type="relations",
                doc_id="doc",
                entities=relation_entities,
            )
            self.assertIsInstance(relations, list)

            graph = build_graph(relation_entities, relations)
            self.assertIn("entities", graph)
            self.assertIn("relationships", graph)
            self.assertEqual(len(graph["entities"]), 2)

            output_dir.mkdir()
            export_graph(graph, output_dir / "graph.json", "json")
            exported = json.loads((output_dir / "graph.json").read_text())
            self.assertIn("entities", exported)


if __name__ == "__main__":
    unittest.main()
