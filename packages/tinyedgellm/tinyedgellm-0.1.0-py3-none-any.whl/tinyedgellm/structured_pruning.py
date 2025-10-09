"""
Structured pruning algorithms for TinyEdgeLLM.
Implements pruning of attention heads, neurons, and layers.
"""

import torch
import torch.nn as nn
import numpy as np
from typing import Dict, List, Tuple, Optional
from transformers.models.gpt2.modeling_gpt2 import GPT2Attention, GPT2Block


class AttentionHeadPruner:
    """
    Prune attention heads based on importance scores.
    """

    def __init__(self, model: nn.Module):
        self.model = model

    def prune_heads(self, head_importance: Dict[str, torch.Tensor], pruning_ratio: float = 0.1) -> nn.Module:
        """
        Prune attention heads across all layers.
        """
        print(f"Pruning {pruning_ratio*100:.1f}% of attention heads...")

        for name, module in self.model.named_modules():
            if isinstance(module, GPT2Attention):
                layer_name = '.'.join(name.split('.')[:-1])  # Get parent layer name
                if layer_name in head_importance:
                    importance_scores = head_importance[layer_name]
                    self._prune_attention_heads(module, importance_scores, pruning_ratio)

        return self.model

    def _prune_attention_heads(self, attention_module: GPT2Attention, importance_scores: torch.Tensor, pruning_ratio: float):
        """
        Prune heads in a single attention module.
        """
        num_heads = attention_module.num_heads
        head_dim = attention_module.head_dim
        hidden_size = attention_module.embed_dim

        # Determine how many heads to keep
        num_heads_to_keep = max(1, int(num_heads * (1 - pruning_ratio)))
        _, indices_to_keep = torch.topk(importance_scores, num_heads_to_keep, largest=True)

        # Create mask for heads to keep
        head_mask = torch.zeros(num_heads, dtype=torch.bool)
        head_mask[indices_to_keep] = True

        # Update attention weights and biases
        with torch.no_grad():
            # c_attn: [hidden_size, 3 * hidden_size]
            # Split into query, key, value: each [hidden_size, hidden_size]
            c_attn_weight = attention_module.c_attn.weight.data
            c_attn_bias = attention_module.c_attn.bias.data

            # Reshape to [num_heads, head_dim, 3, hidden_size]
            c_attn_weight_reshaped = c_attn_weight.view(num_heads, head_dim, 3, hidden_size)
            c_attn_bias_reshaped = c_attn_bias.view(num_heads, head_dim, 3)

            # Keep only selected heads
            c_attn_weight_pruned = c_attn_weight_reshaped[head_mask].view(-1, 3 * hidden_size)
            c_attn_bias_pruned = c_attn_bias_reshaped[head_mask].view(-1)

            # Update the layer
            attention_module.c_attn.weight.data = c_attn_weight_pruned
            attention_module.c_attn.bias.data = c_attn_bias_pruned

            # Update c_proj (output projection)
            c_proj_weight = attention_module.c_proj.weight.data
            c_proj_bias = attention_module.c_proj.bias.data

            # c_proj: [hidden_size, hidden_size] -> [pruned_hidden_size, hidden_size]
            pruned_hidden_size = num_heads_to_keep * head_dim
            c_proj_weight_pruned = c_proj_weight[:, :pruned_hidden_size]
            attention_module.c_proj.weight.data = c_proj_weight_pruned

            # Update attention parameters
            attention_module.num_heads = num_heads_to_keep
            attention_module.embed_dim = pruned_hidden_size


class NeuronPruner:
    """
    Prune neurons (hidden dimensions) in MLP layers.
    """

    def __init__(self, model: nn.Module):
        self.model = model

    def prune_neurons(self, neuron_importance: Dict[str, torch.Tensor], pruning_ratio: float = 0.1) -> nn.Module:
        """
        Apply magnitude-based pruning to linear layers (safe, unstructured pruning).
        """
        print(f"Applying magnitude pruning with ratio {pruning_ratio} to linear layers...")

        for name, module in self.model.named_modules():
            if isinstance(module, nn.Linear):
                layer_name = '.'.join(name.split('.')[:-1])
                if layer_name in neuron_importance:
                    self._prune_linear_layer_magnitude(module, pruning_ratio)

        return self.model

    def _prune_linear_layer_magnitude(self, linear_module: nn.Linear, pruning_ratio: float):
        """
        Prune weights in a linear layer using magnitude-based pruning.
        This zeros out the smallest weights without changing dimensions.
        """
        with torch.no_grad():
            # Flatten weight matrix to get all weight magnitudes
            weight_flat = linear_module.weight.data.abs().flatten()

            # Calculate threshold for pruning
            k = int((1 - pruning_ratio) * weight_flat.numel())
            if k >= weight_flat.numel():
                return  # Don't prune if ratio is too high

            threshold = torch.kthvalue(weight_flat, weight_flat.numel() - k)[0]

            # Create mask for weights above threshold
            mask = (linear_module.weight.data.abs() >= threshold).float()

            # Apply mask (zero out small weights)
            linear_module.weight.data *= mask


class LayerPruner:
    """
    Prune entire transformer layers.
    """

    def __init__(self, model: nn.Module):
        self.model = model

    def prune_layers(self, layer_importance: Dict[str, float], pruning_ratio: float = 0.1) -> nn.Module:
        """
        Prune entire transformer layers.
        """
        print(f"Pruning {pruning_ratio*100:.1f}% of layers...")

        # Get all transformer blocks
        blocks = []
        for name, module in self.model.named_modules():
            if isinstance(module, GPT2Block):
                blocks.append((name, module))

        if not blocks:
            return self.model

        # Sort blocks by importance
        block_importance = []
        for name, _ in blocks:
            importance = layer_importance.get(name, 1.0)  # Default importance
            block_importance.append((name, importance))

        # Sort by importance (keep most important)
        block_importance.sort(key=lambda x: x[1], reverse=True)

        # Determine how many blocks to keep
        num_blocks = len(blocks)
        num_to_keep = max(1, int(num_blocks * (1 - pruning_ratio)))

        # Keep top blocks
        blocks_to_keep = [name for name, _ in block_importance[:num_to_keep]]

        # Remove blocks that are not in the keep list
        for name, module in blocks:
            if name not in blocks_to_keep:
                self._remove_layer(name)

        return self.model

    def _remove_layer(self, layer_name: str):
        """
        Remove a layer from the model.
        """
        # This is complex and model-specific
        # For transformers, we'd need to rebuild the model without the layer
        print(f"Removing layer {layer_name} (simplified implementation)")

        # In a full implementation, this would require:
        # 1. Identifying the layer in the model structure
        # 2. Removing it from the ModuleList
        # 3. Updating all subsequent connections

        # For now, we'll just disable the layer by setting it to identity
        name_parts = layer_name.split('.')
        parent = self.model
        for part in name_parts[:-1]:
            parent = getattr(parent, part)

        # Replace with identity (simplified)
        identity_layer = nn.Identity()
        setattr(parent, name_parts[-1], identity_layer)


def compute_structured_importance(
    model: nn.Module,
    tokenizer: Optional[object] = None,
    calibration_data: Optional[List[str]] = None,
    method: str = 'magnitude'
) -> Tuple[Dict[str, torch.Tensor], Dict[str, torch.Tensor], Dict[str, float]]:
    """
    Compute importance scores for structured pruning.

    Returns:
        Tuple of (head_importance, neuron_importance, layer_importance)
    """
    head_importance = {}
    neuron_importance = {}
    layer_importance = {}

    if calibration_data is None:
        calibration_data = ["Hello world this is a test sentence."]

    # Compute importance for attention heads
    for name, module in model.named_modules():
        if isinstance(module, GPT2Attention):
            layer_name = '.'.join(name.split('.')[:-1])
            head_importance[layer_name] = torch.rand(module.num_heads)  # Placeholder

        elif isinstance(module, nn.Linear):
            layer_name = '.'.join(name.split('.')[:-1])
            # Importance based on weight magnitudes
            neuron_importance[layer_name] = torch.norm(module.weight, p=2, dim=1)

        elif isinstance(module, GPT2Block):
            # Layer importance (placeholder - could be based on gradient norms)
            layer_importance[name] = 1.0

    return head_importance, neuron_importance, layer_importance


def apply_structured_pruning(
    model: nn.Module,
    pruning_ratio: float = 0.1,
    tokenizer: Optional[object] = None,
    calibration_data: Optional[List[str]] = None,
    prune_heads: bool = True,
    prune_neurons: bool = True,
    prune_layers: bool = False
) -> nn.Module:
    """
    Apply structured pruning to the model.

    Args:
        model: Model to prune
        pruning_ratio: Fraction to prune
        tokenizer: Tokenizer for calibration
        calibration_data: Calibration data
        prune_heads: Whether to prune attention heads
        prune_neurons: Whether to prune neurons
        prune_layers: Whether to prune layers

    Returns:
        Pruned model
    """
    print(f"Applying structured pruning with ratio {pruning_ratio}...")

    # Compute importance scores
    head_importance, neuron_importance, layer_importance = compute_structured_importance(
        model, tokenizer, calibration_data
    )

    # Apply different types of pruning
    if prune_heads:
        head_pruner = AttentionHeadPruner(model)
        model = head_pruner.prune_heads(head_importance, pruning_ratio)

    if prune_neurons:
        neuron_pruner = NeuronPruner(model)
        model = neuron_pruner.prune_neurons(neuron_importance, pruning_ratio)

    if prune_layers:
        layer_pruner = LayerPruner(model)
        model = layer_pruner.prune_layers(layer_importance, pruning_ratio)

    return model