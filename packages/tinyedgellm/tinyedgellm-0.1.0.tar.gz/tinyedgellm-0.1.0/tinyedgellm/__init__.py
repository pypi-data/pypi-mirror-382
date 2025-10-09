"""
TinyEdgeLLM: A modular framework for LLM quantization, structured pruning, and edge deployment.
"""

from .quantization import quantize_and_prune
from .benchmarking import benchmark_model, compare_models
from .advanced_quantization import GPTQQuantizer, AWQQuantizer, BitsAndBytesQuantizer
from .structured_pruning import apply_structured_pruning, AttentionHeadPruner, NeuronPruner, LayerPruner
from .knowledge_distillation import KnowledgeDistiller, ModelCompressor, distill_model

__version__ = "0.1.0"
__all__ = [
    "quantize_and_prune",
    "benchmark_model",
    "compare_models",
    "GPTQQuantizer",
    "AWQQuantizer",
    "BitsAndBytesQuantizer",
    "apply_structured_pruning",
    "AttentionHeadPruner",
    "NeuronPruner",
    "LayerPruner",
    "KnowledgeDistiller",
    "ModelCompressor",
    "distill_model"
]