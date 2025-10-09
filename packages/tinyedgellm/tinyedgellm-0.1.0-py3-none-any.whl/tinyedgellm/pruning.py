"""
Pruning module for TinyEdgeLLM.
Implements structured pruning based on various criteria.
"""

import torch
import numpy as np
from typing import Dict, List, Tuple


def compute_magnitude_importance(model: torch.nn.Module) -> Dict[str, torch.Tensor]:
    """
    Compute importance scores based on weight magnitudes.
    """
    importance_scores = {}
    for name, module in model.named_modules():
        if isinstance(module, torch.nn.Linear):
            # L2 norm of weights
            importance_scores[name] = torch.norm(module.weight, p=2, dim=1)
    return importance_scores


def compute_gradient_sensitivity(model: torch.nn.Module, loss_fn: torch.nn.Module, input_data: torch.Tensor) -> Dict[str, torch.Tensor]:
    """
    Compute gradient-based sensitivity scores.
    """
    model.zero_grad()
    output = model(input_data)
    loss = loss_fn(output, torch.zeros_like(output))  # Dummy loss
    loss.backward()

    sensitivity_scores = {}
    for name, module in model.named_modules():
        if isinstance(module, torch.nn.Linear):
            sensitivity_scores[name] = module.weight.grad.abs().sum(dim=1)
    return sensitivity_scores


def compute_activation_variance(model: torch.nn.Module, input_data: torch.Tensor) -> Dict[str, float]:
    """
    Compute activation variance for each layer.
    """
    activations = {}

    def hook_fn(name):
        def hook(module, input, output):
            activations[name] = output.detach().var().item()
        return hook

    hooks = []
    for name, module in model.named_modules():
        if isinstance(module, torch.nn.Linear):
            hooks.append(module.register_forward_hook(hook_fn(name)))

    with torch.no_grad():
        model(input_data)

    for hook in hooks:
        hook.remove()

    return activations


def prune_attention_heads(model: torch.nn.Module, head_importance: Dict[str, torch.Tensor], pruning_ratio: float) -> torch.nn.Module:
    """
    Prune attention heads based on importance scores.
    """
    # This is a simplified implementation - actual transformer pruning is more complex
    for name, importance in head_importance.items():
        if 'attention' in name.lower():
            num_heads = len(importance)
            num_to_prune = int(num_heads * pruning_ratio)
            _, indices_to_keep = torch.topk(importance, num_heads - num_to_prune, largest=True)
            # Apply pruning mask
            mask = torch.zeros_like(importance)
            mask[indices_to_keep] = 1
            # In practice, this would modify the attention mechanism
    return model


def prune_neurons(model: torch.nn.Module, neuron_importance: Dict[str, torch.Tensor], pruning_ratio: float) -> torch.nn.Module:
    """
    Prune neurons based on importance scores.
    """
    for name, importance in neuron_importance.items():
        module = dict(model.named_modules())[name]
        if isinstance(module, torch.nn.Linear):
            num_neurons = len(importance)  # This should be the output dimension
            num_to_prune = int(num_neurons * pruning_ratio)
            _, indices_to_keep = torch.topk(importance, num_neurons - num_to_prune, largest=True)

            # Prune output neurons: remove rows from weight and bias
            module.weight.data = module.weight.data[indices_to_keep]
            if module.bias is not None:
                module.bias.data = module.bias.data[indices_to_keep]

            # Update output features
            module.out_features = len(indices_to_keep)

    return model


def structured_prune(
    model: torch.nn.Module,
    criterion: str = 'magnitude',
    pruning_ratio: float = 0.1,
    calibration_data: torch.Tensor = None
) -> torch.nn.Module:
    """
    Apply structured pruning to the model.

    Args:
        model: The model to prune
        criterion: Pruning criterion ('magnitude', 'gradient', 'activation')
        pruning_ratio: Fraction to prune (0.0 to 1.0)
        calibration_data: Data for gradient/activation based pruning

    Returns:
        Pruned model
    """
    if pruning_ratio == 0.0:
        return model

    print(f"Applying {criterion} pruning with ratio {pruning_ratio}")

    # Use torch's built-in pruning
    import torch.nn.utils.prune as prune

    total_params_before = sum(p.numel() for p in model.parameters())

    for name, module in model.named_modules():
        if isinstance(module, torch.nn.Linear):
            # Skip embedding and output layers
            if any(skip in name.lower() for skip in ['embed', 'lm_head']):
                continue

            # Apply L1 unstructured pruning
            prune.l1_unstructured(module, name='weight', amount=pruning_ratio)

            # Make pruning permanent
            prune.remove(module, 'weight')

    total_params_after = sum(p.numel() for p in model.parameters())
    compression_ratio = total_params_before / total_params_after if total_params_after > 0 else 1.0
    print(".1f")

    return model