"""
Unit tests for TinyEdgeLLM.
"""

import pytest
import torch
import numpy as np
from unittest.mock import Mock, patch

# Import after ensuring dependencies are available
try:
    from tinyedgellm.quantization import analyze_layer_sensitivity, apply_quantization
    from tinyedgellm.pruning import compute_magnitude_importance
    from tinyedgellm.deployment import ModelExporter
    from tinyedgellm.benchmarking import ModelBenchmark
except ImportError:
    pytest.skip("Dependencies not available", allow_module_level=True)


class TestQuantization:
    """Test quantization functionality."""

    def test_analyze_layer_sensitivity(self):
        """Test layer sensitivity analysis."""
        # Create mock model
        model = Mock()
        model.named_modules.return_value = [
            ('layer1', Mock(spec=torch.nn.Linear, weight=torch.randn(10, 5))),
            ('layer2', Mock(spec=torch.nn.Linear, weight=torch.randn(20, 10))),
        ]

        # Mock tokenizer
        tokenizer = Mock()

        sensitivity = analyze_layer_sensitivity(model, tokenizer)

        assert isinstance(sensitivity, dict)
        assert len(sensitivity) == 2
        assert all(isinstance(v, int) for v in sensitivity.values())

    def test_apply_quantization(self):
        """Test quantization application."""
        # Create simple model
        model = torch.nn.Sequential(
            torch.nn.Linear(10, 5),
            torch.nn.ReLU(),
            torch.nn.Linear(5, 1)
        )

        original_params = sum(p.numel() for p in model.parameters())

        quantized_model = apply_quantization(model, bits=8)

        # Model should still be functional
        assert quantized_model is not None
        with torch.no_grad():
            output = quantized_model(torch.randn(1, 10))
            assert output.shape == (1, 1)


class TestPruning:
    """Test pruning functionality."""

    def test_compute_magnitude_importance(self):
        """Test magnitude-based importance computation."""
        model = Mock()
        model.named_modules.return_value = [
            ('linear1', Mock(spec=torch.nn.Linear, weight=torch.randn(10, 5))),
        ]

        importance = compute_magnitude_importance(model)

        assert isinstance(importance, dict)
        assert 'linear1' in importance
        assert importance['linear1'].shape == (10,)  # Output dimension


class TestDeployment:
    """Test deployment functionality."""

    @patch('torch.onnx.export')
    @patch('pathlib.Path.exists', return_value=True)
    @patch('pathlib.Path.with_stem')
    def test_export_onnx(self, mock_with_stem, mock_exists, mock_export):
        """Test ONNX export."""
        exporter = ModelExporter()

        # Mock the path operations
        mock_path = Mock()
        mock_path.__str__ = Mock(return_value="exports/model.onnx")
        mock_with_stem.return_value = mock_path

        model = Mock()
        input_sample = torch.randn(1, 10)

        # Mock the optimization to avoid file operations
        with patch.object(exporter, '_optimize_onnx', return_value=mock_path):
            path = exporter.to_onnx(model, input_sample)

        assert path == str(mock_path)
        mock_export.assert_called_once()


class TestBenchmarking:
    """Test benchmarking functionality."""

    def test_model_benchmark_initialization(self):
        """Test benchmark initialization."""
        benchmark = ModelBenchmark()
        assert benchmark.device.type in ['cpu', 'cuda']

    def test_measure_model_size(self):
        """Test model size measurement."""
        model = torch.nn.Linear(10, 5)
        benchmark = ModelBenchmark(model=model)

        size_info = benchmark.measure_model_size()

        assert 'model_size_mb' in size_info
        assert 'total_parameters' in size_info
        assert size_info['total_parameters'] == 55  # 10*5 + 5


if __name__ == "__main__":
    pytest.main([__file__])