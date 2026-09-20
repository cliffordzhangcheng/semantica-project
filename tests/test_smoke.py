#!/usr/bin/env python3
"""Smoke tests - minimal version for CI"""
import unittest

class TestImports(unittest.TestCase):
    def test_semantica_import(self):
        import semantica
        self.assertTrue(hasattr(semantica, '__version__'))
    
    def test_semantica_workbench_import(self):
        import semantica_workbench
        self.assertIsNotNone(semantica_workbench)

if __name__ == "__main__":
    unittest.main(verbosity=2)
