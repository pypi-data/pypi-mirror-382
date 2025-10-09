"""
Benchmarking module for TinyEdgeLLM.
Provides utilities for measuring model performance metrics.
"""

import torch
import time
import psutil
import os
from typing import Dict, Any, List
from pathlib import Path
import numpy as np


class ModelBenchmark:
    """
    Comprehensive benchmarking suite for model performance.
    """

    def __init__(self, model_path: str = None, model: torch.nn.Module = None):
        self.model_path = model_path
        self.model = model
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    def measure_latency(self, input_tensor: torch.Tensor, num_runs: int = 100) -> Dict[str, float]:
        """
        Measure inference latency.
        """
        if self.model:
            model = self.model.to(self.device).eval()
            input_tensor = input_tensor.to(self.device)

            # Warm up
            with torch.no_grad():
                for _ in range(10):
                    _ = model(input_tensor)

            # Measure latency
            latencies = []
            with torch.no_grad():
                for _ in range(num_runs):
                    start_time = time.time()
                    _ = model(input_tensor)
                    torch.cuda.synchronize() if torch.cuda.is_available() else None
                    end_time = time.time()
                    latencies.append((end_time - start_time) * 1000)  # ms

        else:
            # For exported models, use appropriate runtime
            latencies = self._measure_exported_latency(input_tensor, num_runs)

        return {
            'mean_latency_ms': np.mean(latencies),
            'std_latency_ms': np.std(latencies),
            'min_latency_ms': np.min(latencies),
            'max_latency_ms': np.max(latencies),
            'p50_latency_ms': np.percentile(latencies, 50),
            'p95_latency_ms': np.percentile(latencies, 95),
            'p99_latency_ms': np.percentile(latencies, 99)
        }

    def _measure_exported_latency(self, input_tensor: torch.Tensor, num_runs: int) -> List[float]:
        """
        Measure latency for exported models.
        """
        # Placeholder - implement based on model format
        return [10.0] * num_runs  # Dummy values

    def measure_model_size(self) -> Dict[str, float]:
        """
        Measure model size in various formats.
        """
        if self.model:
            # Calculate parameter count
            total_params = sum(p.numel() for p in self.model.parameters())
            trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)

            # Calculate memory footprint
            param_size = 0
            for param in self.model.parameters():
                param_size += param.numel() * param.element_size()

            buffer_size = 0
            for buffer in self.model.buffers():
                buffer_size += buffer.numel() * buffer.element_size()

            model_size_mb = (param_size + buffer_size) / (1024 ** 2)

        else:
            # For exported models
            if self.model_path and Path(self.model_path).exists():
                model_size_mb = Path(self.model_path).stat().st_size / (1024 ** 2)
                total_params = 0  # Would need to load model to count
                trainable_params = 0
            else:
                model_size_mb = 0
                total_params = 0
                trainable_params = 0

        return {
            'model_size_mb': model_size_mb,
            'total_parameters': total_params,
            'trainable_parameters': trainable_params
        }

    def measure_memory_usage(self, input_tensor: torch.Tensor) -> Dict[str, float]:
        """
        Measure memory usage during inference.
        """
        if not torch.cuda.is_available():
            return {'memory_usage_mb': 0.0}

        torch.cuda.reset_peak_memory_stats()
        torch.cuda.empty_cache()

        if self.model:
            model = self.model.to(self.device).eval()
            input_tensor = input_tensor.to(self.device)

            with torch.no_grad():
                _ = model(input_tensor)

            memory_used = torch.cuda.max_memory_allocated() / (1024 ** 2)
        else:
            memory_used = 0.0

        return {'memory_usage_mb': memory_used}

    def measure_perplexity(self, model: torch.nn.Module, tokenizer, test_texts: List[str]) -> float:
        """
        Measure model perplexity on test texts.
        """
        model.eval()
        total_loss = 0
        total_tokens = 0

        for text in test_texts:
            inputs = tokenizer(text, return_tensors='pt', truncation=True, max_length=512)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = model(**inputs, labels=inputs['input_ids'])
                loss = outputs.loss
                num_tokens = inputs['input_ids'].numel()

            total_loss += loss.item() * num_tokens
            total_tokens += num_tokens

        avg_loss = total_loss / total_tokens
        perplexity = torch.exp(torch.tensor(avg_loss)).item()

        return perplexity

    def benchmark_comprehensive(
        self,
        input_tensor: torch.Tensor,
        test_texts: List[str] = None,
        tokenizer = None
    ) -> Dict[str, Any]:
        """
        Run comprehensive benchmark suite.
        """
        results = {}

        # Latency
        results['latency'] = self.measure_latency(input_tensor)

        # Model size
        results['size'] = self.measure_model_size()

        # Memory usage
        results['memory'] = self.measure_memory_usage(input_tensor)

        # Perplexity (if applicable)
        if self.model and test_texts and tokenizer:
            results['perplexity'] = self.measure_perplexity(self.model, tokenizer, test_texts)
        else:
            results['perplexity'] = None

        # Compression ratio (would need original model for comparison)
        results['compression_ratio'] = None

        # Performance per watt (placeholder - would need power measurement)
        results['performance_per_watt'] = None

        return results


def benchmark_model(
    model: torch.nn.Module,
    input_tensor: torch.Tensor,
    test_texts: List[str] = None,
    tokenizer = None,
    model_path: str = None
) -> Dict[str, Any]:
    """
    Convenience function to benchmark a model.
    """
    benchmark = ModelBenchmark(model_path=model_path, model=model)
    return benchmark.benchmark_comprehensive(input_tensor, test_texts, tokenizer)


def compare_models(
    original_model: torch.nn.Module,
    optimized_model: torch.nn.Module,
    input_tensor: torch.Tensor,
    test_texts: List[str] = None,
    tokenizer = None
) -> Dict[str, Dict[str, Any]]:
    """
    Compare original vs optimized model performance.
    """
    original_benchmark = ModelBenchmark(model=original_model)
    optimized_benchmark = ModelBenchmark(model=optimized_model)

    original_results = original_benchmark.benchmark_comprehensive(input_tensor, test_texts, tokenizer)
    optimized_results = optimized_benchmark.benchmark_comprehensive(input_tensor, test_texts, tokenizer)

    # Calculate compression metrics
    if original_results['size']['model_size_mb'] > 0:
        compression_ratio = original_results['size']['model_size_mb'] / optimized_results['size']['model_size_mb']
    else:
        compression_ratio = 1.0

    perplexity_drop = None
    if original_results['perplexity'] and optimized_results['perplexity']:
        perplexity_drop = (optimized_results['perplexity'] - original_results['perplexity']) / original_results['perplexity']

    return {
        'original': original_results,
        'optimized': optimized_results,
        'compression_ratio': compression_ratio,
        'perplexity_drop_percent': perplexity_drop * 100 if perplexity_drop else None
    }