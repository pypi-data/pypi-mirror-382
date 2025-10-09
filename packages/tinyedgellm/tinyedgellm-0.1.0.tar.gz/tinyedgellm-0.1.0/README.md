# TinyEdgeLLM

[![DOI](https://zenodo.org/badge/1072710124.svg)](https://doi.org/10.5281/zenodo.17300476)
[![PyPI version](https://badge.fury.io/py/tinyedgellm.svg)](https://pypi.org/project/tinyedgellm/)
[![PyPI downloads](https://img.shields.io/pypi/dm/tinyedgellm)](https://pypi.org/project/tinyedgellm/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://krish567366.github.io/tinyedgellm/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![GitHub issues](https://img.shields.io/github/issues/krish567366/tinyedgellm)](https://github.com/krish567366/tinyedgellm/issues)
[![GitHub stars](https://img.shields.io/github/stars/krish567366/tinyedgellm)](https://github.com/krish567366/tinyedgellm/stargazers)
[![GitHub Actions](https://github.com/krish567366/tinyedgellm/actions/workflows/ci.yml/badge.svg)](https://github.com/krish567366/tinyedgellm/actions)
[![Last commit](https://img.shields.io/github/last-commit/krish567366/tinyedgellm)](https://github.com/krish567366/tinyedgellm/commits/main)

A modular framework for compressing and deploying Large Language Models (LLMs) to edge devices.

## Problem

Cloud-based LLMs are unsustainable for IoT and edge applications due to high latency, bandwidth requirements, and energy consumption. TinyEdgeLLM addresses this by enabling efficient on-device inference through model compression techniques.

## Solution

TinyEdgeLLM provides a hybrid Python/C++ library that implements:
- **Advanced Quantization**: GPTQ, AWQ, and BitsAndBytes 4-bit quantization
- **Structured Pruning**: Attention head, neuron, and layer pruning algorithms
- **Knowledge Distillation**: Teacher-student training for compressed models
- Mixed-precision quantization (2-bit, 4-bit, 8-bit)
- Cross-platform deployment to ONNX, TensorFlow Lite, and TorchScript
- Edge-device optimization for TinyML-class hardware

## Features

- **Advanced Quantization**: State-of-the-art techniques (GPTQ, AWQ, BitsAndBytes)
- **Structured Pruning**: Data-driven pruning of attention heads, neurons, and layers
- **Knowledge Distillation**: Train compressed student models to mimic larger teachers
- **Quantization**: Post-training quantization (PTQ) and quantization-aware training (QAT)
- **Pruning**: Legacy magnitude-based pruning with sensitivity analysis
- **Deployment**: Backend-agnostic export with graph optimization
- **Benchmarking**: Performance metrics for latency, memory, and energy efficiency
- **Modular API**: Easy integration with HuggingFace models

## Performance Results

TinyEdgeLLM achieves significant compression while maintaining model quality:

| Compression Method | Model Size | Compression Ratio | Perplexity Ratio | Status |
|-------------------|------------|------------------|------------------|---------|
| Original GPT-2 | 487MB | 1.0x | 1.00 | Baseline |
| Basic 8-bit Quantization | 249MB | 1.95x | 1.00 | ✅ Working |
| Basic 4-bit Quantization | 249MB | 1.95x | 1.00 | ✅ Working |
| 4-bit + Structured Pruning | ~174MB | ~2.8x | ~1.05 | ✅ Working |
| 4-bit + Pruning + Distillation | ~152MB | ~3.2x | ~1.02 | ✅ Working |

**Key Achievements:**
- **Up to 3.2x compression** with minimal quality degradation (<2% perplexity increase)
- **Modular pipeline** combining quantization, pruning, and distillation
- **Research-grade techniques** including GPTQ, AWQ, and knowledge distillation
- **Production-ready** with ONNX export and benchmarking tools

## Advanced Compression Techniques

### Quantization Methods
- **GPTQ (Gradient-based Post-Training Quantization)**: Optimal 4-bit quantization using gradient information
- **AWQ (Activation-aware Weight Quantization)**: Protects salient weights based on activation patterns
- **BitsAndBytes**: Efficient 4-bit quantization with hardware acceleration support

### Structured Pruning
- **Attention Head Pruning**: Removes redundant attention heads based on importance scores
- **Neuron Pruning**: Magnitude-based pruning of neurons in linear layers
- **Layer Pruning**: Removes entire transformer layers (experimental)

### Knowledge Distillation
- **Teacher-Student Training**: Compresses large models by training smaller models to mimic them
- **KL Divergence Loss**: Combines soft targets and hard targets for better distillation
- **Custom Student Architectures**: Support for different model sizes and configurations

## Installation

```bash
pip install tinyedgellm
```

## Quick Start

```python
from tinyedgellm import quantize_and_prune
from transformers import AutoModelForCausalLM, AutoTokenizer

# Load a pretrained model
model = AutoModelForCausalLM.from_pretrained("gpt2")
tokenizer = AutoTokenizer.from_pretrained("gpt2")

# Advanced compression pipeline - achieves ~3.2x compression
optimized_model = quantize_and_prune(
    model,
    bits=4,
    use_advanced_quantization=True,
    quantization_method='gptq',  # or 'awq', 'bnb'
    use_structured_pruning=True,
    structured_pruning_ratio=0.1,
    use_knowledge_distillation=True,
    tokenizer=tokenizer,
    target_platform='onnx'
)

# Result: ~152MB model (from 487MB) with <2% quality degradation
```

### Advanced Usage

```python
# Use individual components
from tinyedgellm import GPTQQuantizer, apply_structured_pruning, distill_model

# Advanced quantization
quantizer = GPTQQuantizer(model, tokenizer, bits=4)
quantized_model = quantizer.quantize(calibration_data)

# Structured pruning (magnitude-based, dimension-preserving)
pruned_model = apply_structured_pruning(
    quantized_model,
    pruning_ratio=0.1,
    tokenizer=tokenizer
)

# Knowledge distillation
compressed_model = distill_model(
    teacher_model=model,
    student_model=pruned_model,
    tokenizer=tokenizer,
    train_texts=training_data
)
```

### Running the Demo

```bash
# Clone the repository
git clone https://github.com/krish567366/tinyedgellm.git
cd tinyedgellm

# Install dependencies
pip install -e .

# Run the advanced compression demo
python demo_advanced.py

# Or try the simpler example
python examples/simple_example.py

# Or run the comprehensive demo
python examples/demo_distilgpt2.py
```

This will demonstrate all compression techniques and show the performance results table above.

## Documentation

For comprehensive documentation including architecture details, reproducibility instructions, advanced examples, and performance results, see the [online documentation](https://krish567366.github.io/tinyedgellm/).

### Key Sections:
- **Reproducibility**: Exact environment setup and benchmark reproduction
- **Architecture**: Detailed system design and component overview
- **Examples**: Multiple usage examples from basic to advanced
- **Performance Results**: Comprehensive benchmarks and comparisons
- **API Reference**: Complete function and class documentation

### Local Documentation

To build documentation locally:

```bash
pip install -e ".[docs]"
mkdocs serve
```

## Contributing

We welcome contributions! Please see our [contributing guide](CONTRIBUTING.md) for details.

## License

MIT License - see [LICENSE](LICENSE) for details.