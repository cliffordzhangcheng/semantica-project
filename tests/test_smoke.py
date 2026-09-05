#!/usr/bin/env python3
"""
Smoke tests for Semantica pipeline scripts.
验证：脚本可导入、核心类可实例化、基础流程不报错。
"""
import sys
import importlib
import unittest
from pathlib import Path

# 将项目根目录加入路径，以便 import scripts.xxx
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from semantica.utils.exceptions import ValidationError

class TestImports(unittest.TestCase):
    """测试各脚本模块可正常导入"""

    def test_01_ingest_import(self):
        m = importlib.import_module('scripts.01_ingest')
        self.assertTrue(hasattr(m, "main"))

    def test_02_normalize_import(self):
        m = importlib.import_module('scripts.02_normalize')
        self.assertTrue(hasattr(m, "main"))

    def test_03_ner_import(self):
        m = importlib.import_module('scripts.03_ner')
        self.assertTrue(hasattr(m, "main"))

    def test_04_relation_import(self):
        m = importlib.import_module('scripts.04_relation')
        self.assertTrue(hasattr(m, "main"))

    def test_05_build_and_store_import(self):
        m = importlib.import_module('scripts.05_build_and_store')
        self.assertTrue(hasattr(m, "main"))

    def test_06_export_import(self):
        m = importlib.import_module('scripts.06_export')
        self.assertTrue(hasattr(m, "main"))

class TestCoreClasses(unittest.TestCase):
    """测试 Semantica 核心类可实例化（不依赖外部数据）"""

    def test_file_ingestor(self):
        from semantica.ingest import FileIngestor
        ingestor = FileIngestor()
        self.assertIsNotNone(ingestor)

    def test_normalizers(self):
        from semantica.normalize import (
            TextCleaner, LanguageDetector, EntityNormalizer,
            DateNormalizer, NumberNormalizer
        )
        for cls in [TextCleaner, LanguageDetector, EntityNormalizer,
                    DateNormalizer, NumberNormalizer]:
            obj = cls()
            self.assertIsNotNone(obj)

    def test_ner_extractor_pattern(self):
        from semantica.semantic_extract import NERExtractor
        extractor = NERExtractor(mode="pattern")
        self.assertIsNotNone(extractor)

    def test_relation_extractor_pattern(self):
        from semantica.semantic_extract import RelationExtractor
        extractor = RelationExtractor(mode="pattern")
        self.assertIsNotNone(extractor)

    def test_graph_builder(self):
        from semantica.kg import GraphBuilder
        builder = GraphBuilder(merge_entities=True)
        self.assertIsNotNone(builder)

    def test_graph_store_backend_validation(self):
        from semantica.graph_store import GraphStore
        # 测试不支持的backend会抛出ValidationError
        with self.assertRaises(ValidationError):
            GraphStore(backend="networkx")

    def test_graph_exporter(self):
        from semantica.export import GraphExporter
        import networkx as nx
        G = nx.Graph()
        exporter = GraphExporter(G)
        self.assertIsNotNone(exporter)

    def test_vectorizer(self):
        from semantica.embeddings import TextEmbedder
        # 使用轻量模型，避免下载大模型
        vectorizer = TextEmbedder(model="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        self.assertIsNotNone(vectorizer)

    def test_vector_store_faiss(self):
        from semantica.vector_store import VectorStore
        store = VectorStore(backend="faiss", dim=384)
        self.assertIsNotNone(store)

class TestConfigFiles(unittest.TestCase):
    """测试配置文件存在且格式正确"""

    def test_backend_yaml(self):
        import yaml
        cfg_path = PROJECT_ROOT / "config" / "backend.yaml"
        self.assertTrue(cfg_path.exists())
        with open(cfg_path) as f:
            cfg = yaml.safe_load(f)
        self.assertIn("backend", cfg)
        self.assertIn(cfg["backend"], ["networkx", "neo4j", "falkordb", "age"])

    def test_ontology_yaml(self):
        import yaml
        cfg_path = PROJECT_ROOT / "config" / "ontology.yaml"
        self.assertTrue(cfg_path.exists())
        with open(cfg_path) as f:
            cfg = yaml.safe_load(f)
        self.assertIn("classes", cfg)
        self.assertIn("relations", cfg)

class TestPipelineFiles(unittest.TestCase):
    """测试关键文件存在"""

    def test_requirements_txt(self):
        req_path = PROJECT_ROOT / "requirements.txt"
        self.assertTrue(req_path.exists())
        content = req_path.read_text()
        self.assertIn("semantica", content)
        self.assertIn("faiss-cpu", content)

    def test_run_all_sh(self):
        run_path = PROJECT_ROOT / "run_all.sh"
        self.assertTrue(run_path.exists())
        self.assertTrue(run_path.stat().st_mode & 0o111)  # 可执行

    def test_env_example(self):
        env_path = PROJECT_ROOT / ".env.example"
        self.assertTrue(env_path.exists())
        content = env_path.read_text()
        self.assertIn("DEEPSEEK_API_KEY", content)

if __name__ == "__main__":
    unittest.main(verbosity=2)
