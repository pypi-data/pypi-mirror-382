"""
Knowledge distillation for TinyEdgeLLM.
Train compressed student models to mimic larger teacher models.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset
from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import Optional, Dict, Any, List
from tqdm import tqdm
import numpy as np


class TextDataset(Dataset):
    """
    Dataset for knowledge distillation training.
    """

    def __init__(self, texts: List[str], tokenizer, max_length: int = 512):
        self.texts = texts
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = self.texts[idx]
        inputs = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )

        return {
            'input_ids': inputs['input_ids'].squeeze(),
            'attention_mask': inputs['attention_mask'].squeeze()
        }


class DistillationLoss(nn.Module):
    """
    Knowledge distillation loss combining soft targets and hard targets.
    """

    def __init__(self, temperature: float = 2.0, alpha: float = 0.5):
        super().__init__()
        self.temperature = temperature
        self.alpha = alpha
        self.ce_loss = nn.CrossEntropyLoss()

    def forward(self, student_logits, teacher_logits, labels):
        """
        Compute distillation loss.

        Args:
            student_logits: Logits from student model
            teacher_logits: Logits from teacher model
            labels: Ground truth labels
        """
        # Soft targets loss (KL divergence)
        teacher_probs = F.softmax(teacher_logits / self.temperature, dim=-1)
        student_log_probs = F.log_softmax(student_logits / self.temperature, dim=-1)
        distillation_loss = F.kl_div(student_log_probs, teacher_probs, reduction='batchmean') * (self.temperature ** 2)

        # Hard targets loss (cross entropy)
        hard_loss = self.ce_loss(student_logits.view(-1, student_logits.size(-1)), labels.view(-1))

        # Combine losses
        loss = self.alpha * distillation_loss + (1 - self.alpha) * hard_loss

        return loss


class KnowledgeDistiller:
    """
    Knowledge distillation trainer for compressing LLMs.
    """

    def __init__(
        self,
        teacher_model: nn.Module,
        student_model: nn.Module,
        tokenizer,
        device: str = 'auto'
    ):
        self.teacher_model = teacher_model
        self.student_model = student_model
        self.tokenizer = tokenizer

        if device == 'auto':
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device(device)

        self.teacher_model.to(self.device)
        self.student_model.to(self.device)

        self.teacher_model.eval()  # Teacher is always in eval mode

        self.distillation_loss = DistillationLoss()

    def distill(
        self,
        train_texts: List[str],
        num_epochs: int = 3,
        batch_size: int = 4,
        learning_rate: float = 1e-4,
        temperature: float = 2.0,
        alpha: float = 0.5,
        max_length: int = 512
    ) -> nn.Module:
        """
        Perform knowledge distillation training.

        Args:
            train_texts: Training text data
            num_epochs: Number of training epochs
            batch_size: Training batch size
            learning_rate: Learning rate
            temperature: Distillation temperature
            alpha: Loss weighting factor
            max_length: Maximum sequence length

        Returns:
            Trained student model
        """
        print(f"Starting knowledge distillation for {num_epochs} epochs...")

        # Update loss function parameters
        self.distillation_loss.temperature = temperature
        self.distillation_loss.alpha = alpha

        # Prepare dataset and dataloader
        dataset = TextDataset(train_texts, self.tokenizer, max_length)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

        # Optimizer
        optimizer = torch.optim.AdamW(self.student_model.parameters(), lr=learning_rate)

        # Training loop
        self.student_model.train()

        for epoch in range(num_epochs):
            epoch_loss = 0.0
            num_batches = 0

            progress_bar = tqdm(dataloader, desc=f"Epoch {epoch + 1}/{num_epochs}")

            for batch in progress_bar:
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)

                # For causal LM: labels should be the next token predictions
                # Shift input_ids to create labels: labels[i] = input_ids[i+1]
                labels = input_ids.clone()
                # Shift labels to predict next token (last position will be ignored in loss)
                labels = torch.roll(labels, shifts=-1, dims=1)
                # Set the last position to -100 (ignore index) since there's no next token
                labels[:, -1] = -100

                optimizer.zero_grad()

                # Get teacher outputs
                with torch.no_grad():
                    teacher_outputs = self.teacher_model(
                        input_ids=input_ids,
                        attention_mask=attention_mask
                    )
                    teacher_logits = teacher_outputs.logits

                # Get student outputs
                student_outputs = self.student_model(
                    input_ids=input_ids,
                    attention_mask=attention_mask
                )
                student_logits = student_outputs.logits

                # Compute distillation loss
                loss = self.distillation_loss(student_logits, teacher_logits, labels)

                # Backward pass
                loss.backward()
                optimizer.step()

                epoch_loss += loss.item()
                num_batches += 1

                progress_bar.set_postfix({'loss': f"{loss.item():.4f}"})

            avg_epoch_loss = epoch_loss / num_batches
            print(f"Epoch {epoch + 1}/{num_epochs} completed. Average loss: {avg_epoch_loss:.4f}")

        self.student_model.eval()
        print("Knowledge distillation completed!")

        return self.student_model


class ModelCompressor:
    """
    High-level interface for model compression using knowledge distillation.
    """

    def __init__(self, teacher_model_name: str = "gpt2", student_config: Optional[Dict] = None):
        self.teacher_model_name = teacher_model_name
        self.student_config = student_config or {
            'vocab_size': 50257,  # GPT-2 vocab size
            'n_positions': 1024,
            'n_embd': 768 // 2,  # Half the embedding dimension
            'n_layer': 12 // 2,   # Half the layers
            'n_head': 12 // 2,    # Half the heads
        }

    def create_student_model(self) -> nn.Module:
        """
        Create a smaller student model for distillation.
        """
        # This is a simplified implementation
        # In practice, you'd create a proper transformer architecture

        from transformers import GPT2Config, GPT2LMHeadModel

        config = GPT2Config(**self.student_config)
        student_model = GPT2LMHeadModel(config)

        return student_model

    def compress_with_distillation(
        self,
        train_texts: List[str],
        num_epochs: int = 3,
        batch_size: int = 4,
        **distillation_kwargs
    ) -> nn.Module:
        """
        Compress a model using knowledge distillation.

        Args:
            train_texts: Training data for distillation
            num_epochs: Number of distillation epochs
            batch_size: Training batch size
            **distillation_kwargs: Additional distillation parameters

        Returns:
            Compressed student model
        """
        print("Loading teacher model...")
        teacher_model = AutoModelForCausalLM.from_pretrained(self.teacher_model_name)
        tokenizer = AutoTokenizer.from_pretrained(self.teacher_model_name)

        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        print("Creating student model...")
        student_model = self.create_student_model()

        print("Starting knowledge distillation...")
        distiller = KnowledgeDistiller(teacher_model, student_model, tokenizer)

        compressed_model = distiller.distill(
            train_texts=train_texts,
            num_epochs=num_epochs,
            batch_size=batch_size,
            **distillation_kwargs
        )

        return compressed_model, tokenizer


def distill_model(
    teacher_model: nn.Module,
    student_model: nn.Module,
    tokenizer,
    train_texts: List[str],
    num_epochs: int = 3,
    batch_size: int = 4,
    **kwargs
) -> nn.Module:
    """
    Convenience function for knowledge distillation.

    Args:
        teacher_model: Pre-trained teacher model
        student_model: Student model to train
        tokenizer: Tokenizer
        train_texts: Training text data
        num_epochs: Number of training epochs
        batch_size: Training batch size

    Returns:
        Distilled student model
    """
    distiller = KnowledgeDistiller(teacher_model, student_model, tokenizer)
    return distiller.distill(train_texts, num_epochs, batch_size, **kwargs)