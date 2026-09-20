#!/usr/bin/env python3
"""Smoke tests - minimal version for CI"""
import unittest

class TestImports(unittest.TestCase):
    def test_python_running(self):
        """验证Python可正常运行"""
        import sys
        self.assertIsNotNone(sys.version)
    
    def test_os_available(self):
        """验证os模块可导入"""
        import os
        self.assertTrue(hasattr(os, 'path'))

if __name__ == "__main__":
    unittest.main(verbosity=2)
