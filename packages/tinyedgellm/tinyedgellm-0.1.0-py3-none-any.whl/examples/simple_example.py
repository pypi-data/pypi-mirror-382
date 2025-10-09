#!/usr/bin/env python3
"""
Simple TinyEdgeLLM Usage Example
Demonstrates basic model compression and deployment
"""

from tinyedgellm import quantize_and_prune, benchmark_model
from transformers import AutoModelForCausalLM, AutoTokenizer


def main():
    # Load a small model for quick testing
    model_name = "gpt2"
    model = AutoModelForCausalLM.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    print(f"Original model size: {model.num_parameters():,} parameters")

    # Simple compression
    result = quantize_and_prune(
        model=model,
        bits=8,  # 8-bit for better compatibility
        use_advanced_quantization=False,  # Use basic quantization
        use_structured_pruning=False,     # Skip pruning for simplicity
        use_knowledge_distillation=False, # Skip distillation for speed
        tokenizer=tokenizer,
        target_platform='onnx'
    )

    print(f"Compressed model saved to: {result['model_path']}")
    print(f"Compression ratio: {result.get('compression_ratio', 'N/A')}")

    # Quick benchmark
    test_text = "Hello world, this is a test."
    input_tensor = tokenizer(test_text, return_tensors='pt')['input_ids']

    metrics = benchmark_model(result['optimized_model'], input_tensor)
    print(".2f")


if __name__ == "__main__":
    main()