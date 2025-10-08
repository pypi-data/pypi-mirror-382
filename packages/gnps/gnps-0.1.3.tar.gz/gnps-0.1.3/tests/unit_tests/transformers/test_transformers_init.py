"""Tests for transformers __init__ module."""

import pytest
from gnps.transformers import BaseTransformer, PythonTransformer
from gnps.transformers.base_transformer import BaseTransformer as BaseTransformerClass
from gnps.transformers.python_transformer import PythonTransformer as PythonTransformerClass


class TestTransformersInit:
    """Test the transformers __init__ module imports."""

    def test_base_transformer_import(self):
        """Test that BaseTransformer is imported correctly."""
        assert BaseTransformer is BaseTransformerClass

    def test_python_transformer_import(self):
        """Test that PythonTransformer is imported correctly."""
        assert PythonTransformer is PythonTransformerClass

    def test_all_exports(self):
        """Test that __all__ exports are correct."""
        from gnps.transformers import __all__
        assert "BaseTransformer" in __all__
        assert "PythonTransformer" in __all__
        assert len(__all__) == 2
