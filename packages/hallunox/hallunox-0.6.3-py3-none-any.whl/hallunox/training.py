"""
Training Module for HalluNox

This module contains the training pipeline for the hallucination detection model,
including dataset loading, model training, and evaluation components.
"""

import os
import sys
import json
import random
import logging
import argparse
from pathlib import Path
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict, Union
from tqdm import tqdm
import warnings

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from torch.cuda.amp import autocast, GradScaler

from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    get_linear_schedule_with_warmup,
)
from datasets import load_dataset
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    roc_auc_score,
)

# Import from hallunox modules
from .detector import ProjectionHead, get_pooled_embeddings
from .utils import setup_logging

# Import FlagEmbedding for BGE-M3
try:
    from FlagEmbedding import BGEM3FlagModel
    BGE_M3_AVAILABLE = True
except ImportError:
    BGE_M3_AVAILABLE = False
    warnings.warn(
        "FlagEmbedding not available. Install with: pip install -U FlagEmbedding",
        ImportWarning
    )

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

logger = setup_logging()


@dataclass
class TrainingConfig:
    """
    Configuration class for training the hallucination detection model.
    
    This configuration follows the approach described in the research paper,
    with optimized settings for Llama-3.2-3B and BGE-M3 integration.
    """
    model_id: str = "convaiinnovations/gemma-finetuned-4b-it"
    embed_model_id: str = "BAAI/bge-m3"
    max_length: int = 512

    # Model architecture dimensions (auto-detected from model config)
    llm_hidden_size: int = None  # Auto-detected from model config
    embedding_dim: int = 1024    # BGE-M3 embedding dimension

    batch_size: int = 8  # Optimized for Llama-3.2-3B
    learning_rate: float = 5e-4  # Adjusted for larger model
    weight_decay: float = 1e-4
    warmup_steps: int = 300
    max_epochs: int = 6
    gradient_accumulation_steps: int = 4
    max_grad_norm: float = 1.0

    val_split: float = 0.15
    num_workers: int = 0

    output_dir: str = "./models/hallucination_llama32_bge"
    log_steps: int = 25

    use_fp16: bool = True
    use_wandb: bool = False
    wandb_project: str = "hallucination-detection-llama32"

    # Dataset configuration
    use_truthfulqa: bool = True
    use_halueval: bool = True
    use_fever: bool = True
    use_xsum_factuality: bool = True
    use_squad_v2: bool = True
    use_natural_questions: bool = True
    max_samples_per_dataset: int = 3000

    # Confidence score thresholds (as per research paper)
    high_confidence_threshold: float = 0.9
    medium_confidence_threshold: float = 0.7
    low_confidence_threshold: float = 0.3

    # BGE-M3 specific settings
    bge_use_fp16: bool = True
    bge_max_length: int = 512


class MultiDatasetLoader:
    """
    Enhanced dataset loader that incorporates multiple knowledge-intensive datasets
    for comprehensive hallucination detection training.
    
    This follows the multi-signal approach described in the paper by combining
    diverse datasets with different types of factual content and hallucinations.
    """

    def __init__(self, config: TrainingConfig):
        self.config = config
        self.datasets_loaded = []

    def load_truthfulqa_dataset(self) -> Tuple[List[str], List[float]]:
        """Load TruthfulQA dataset for truthfulness evaluation"""
        try:
            logger.info("📥 Loading TruthfulQA dataset...")
            dataset = load_dataset("truthfulqa/truthful_qa", "generation", split="validation")

            texts, labels = [], []

            for i, example in enumerate(dataset):
                if i >= self.config.max_samples_per_dataset:
                    break

                question = example['question']

                # Use best answer for high confidence examples
                if example.get('best_answer'):
                    text = f"Question: {question}\nAnswer: {example['best_answer']}"
                    texts.append(text)
                    labels.append(self.config.high_confidence_threshold)

                # Use incorrect answers for low confidence examples
                if example.get('incorrect_answers'):
                    for incorrect_answer in example['incorrect_answers'][:2]:
                        text = f"Question: {question}\nAnswer: {incorrect_answer}"
                        texts.append(text)
                        labels.append(self.config.low_confidence_threshold)

            logger.info(f"✅ TruthfulQA loaded: {len(texts)} examples")
            self.datasets_loaded.append(f"TruthfulQA: {len(texts)} examples")
            return texts, labels

        except Exception as e:
            logger.warning(f"⚠️ Could not load TruthfulQA: {e}")
            return [], []

    def load_halueval_dataset(self) -> Tuple[List[str], List[float]]:
        """Load HaluEval dataset for hallucination detection"""
        try:
            logger.info("📥 Loading HaluEval dataset...")
            dataset = load_dataset("pminervini/HaluEval", split="data")

            texts, labels = [], []

            for i, example in enumerate(dataset):
                if i >= self.config.max_samples_per_dataset:
                    break

                knowledge = example.get('knowledge', '')
                dialogue_history = example.get('dialogue_history', '')
                response = example.get('response', '')
                hallucination_type = example.get('hallucination', 'no')

                if response:
                    if knowledge and dialogue_history:
                        text = f"Knowledge: {knowledge[:200]}...\nDialogue: {dialogue_history[:200]}...\nResponse: {response}"
                    elif knowledge:
                        text = f"Knowledge: {knowledge[:200]}...\nResponse: {response}"
                    else:
                        text = f"Response: {response}"

                    texts.append(text)

                    if hallucination_type == 'no':
                        labels.append(self.config.high_confidence_threshold)
                    else:
                        labels.append(self.config.low_confidence_threshold)

            logger.info(f"✅ HaluEval loaded: {len(texts)} examples")
            self.datasets_loaded.append(f"HaluEval: {len(texts)} examples")
            return texts, labels

        except Exception as e:
            logger.warning(f"⚠️ Could not load HaluEval: {e}")
            return [], []

    def load_fever_dataset(self) -> Tuple[List[str], List[float]]:
        """Load FEVER dataset for fact verification"""
        try:
            logger.info("📥 Loading FEVER dataset...")
            dataset = load_dataset("fever", "v1.0", split="train")

            texts, labels = [], []

            for i, example in enumerate(dataset):
                if i >= self.config.max_samples_per_dataset:
                    break

                claim = example['claim']
                label = example['label']
                evidence = example.get('evidence', {})

                evidence_text = ""
                if evidence and 'wiki_url' in evidence and evidence['wiki_url']:
                    evidence_text = f" Evidence: {str(evidence)[:100]}..."

                text = f"Claim: {claim}{evidence_text}"
                texts.append(text)

                if label == 'SUPPORTS':
                    labels.append(self.config.high_confidence_threshold)
                elif label == 'REFUTES':
                    labels.append(self.config.low_confidence_threshold)
                else:  # NOT ENOUGH INFO
                    labels.append(self.config.medium_confidence_threshold)

            logger.info(f"✅ FEVER loaded: {len(texts)} examples")
            self.datasets_loaded.append(f"FEVER: {len(texts)} examples")
            return texts, labels

        except Exception as e:
            logger.warning(f"⚠️ Could not load FEVER: {e}")
            return [], []

    def load_xsum_factuality_dataset(self) -> Tuple[List[str], List[float]]:
        """Load XSum Factuality dataset for summarization hallucination detection"""
        try:
            logger.info("📥 Loading XSum Factuality dataset...")
            dataset = load_dataset("google-research-datasets/xsum_factuality", "xsum_factuality", split="train")

            texts, labels = [], []

            for i, example in enumerate(dataset):
                if i >= self.config.max_samples_per_dataset:
                    break

                summary = example['summary']
                is_factual = example.get('is_factual', -1)

                if is_factual != -1 and summary:
                    texts.append(f"Summary: {summary}")

                    if is_factual == 1:
                        labels.append(self.config.high_confidence_threshold)
                    else:
                        labels.append(self.config.low_confidence_threshold)

            logger.info(f"✅ XSum Factuality loaded: {len(texts)} examples")
            self.datasets_loaded.append(f"XSum Factuality: {len(texts)} examples")
            return texts, labels

        except Exception as e:
            logger.warning(f"⚠️ Could not load XSum Factuality: {e}")
            return [], []

    def load_squad_v2_dataset(self) -> Tuple[List[str], List[float]]:
        """Load Squad v2 dataset with answerable/unanswerable questions"""
        try:
            logger.info("📥 Loading Squad v2 dataset...")
            dataset = load_dataset("squad_v2", split="train")

            texts, labels = [], []

            for i, example in enumerate(dataset):
                if i >= self.config.max_samples_per_dataset:
                    break

                context = example["context"][:300]
                question = example["question"]
                answers = example["answers"]["text"]

                if answers:
                    answer = answers[0]
                    text = f"Context: {context}\nQuestion: {question}\nAnswer: {answer}"
                    texts.append(text)
                    labels.append(self.config.high_confidence_threshold)
                else:
                    text = f"Context: {context}\nQuestion: {question}\nAnswer: This question cannot be answered based on the given context."
                    texts.append(text)
                    labels.append(self.config.low_confidence_threshold)

            logger.info(f"✅ Squad v2 loaded: {len(texts)} examples")
            self.datasets_loaded.append(f"Squad v2: {len(texts)} examples")
            return texts, labels

        except Exception as e:
            logger.warning(f"⚠️ Could not load Squad v2: {e}")
            return [], []

    def load_natural_questions_dataset(self) -> Tuple[List[str], List[float]]:
        """Load Natural Questions dataset"""
        try:
            logger.info("📥 Loading Natural Questions dataset...")
            dataset = load_dataset("natural_questions", split="train[:3000]")

            texts, labels = [], []

            for i, example in enumerate(dataset):
                if i >= self.config.max_samples_per_dataset:
                    break

                question = example["question"]["text"]
                annotations = example.get("annotations", {})

                has_answer = False
                if annotations and "short_answers" in annotations:
                    for annotation in annotations["short_answers"]:
                        if annotation.get("start_token", -1) != -1:
                            has_answer = True
                            break

                if has_answer:
                    texts.append(f"Question: {question}\nAnswer: [Answerable from context]")
                    labels.append(self.config.high_confidence_threshold)
                else:
                    texts.append(f"Question: {question}\nAnswer: [Cannot be answered from context]")
                    labels.append(self.config.low_confidence_threshold)

            logger.info(f"✅ Natural Questions loaded: {len(texts)} examples")
            self.datasets_loaded.append(f"Natural Questions: {len(texts)} examples")
            return texts, labels

        except Exception as e:
            logger.warning(f"⚠️ Could not load Natural Questions: {e}")
            return [], []

    def create_synthetic_examples(self) -> Tuple[List[str], List[float]]:
        """Create synthetic examples for edge cases and balanced training"""
        logger.info("📥 Creating synthetic examples...")

        high_conf_texts = [
            "What is the capital of France?",
            "What is 2 + 2?",
            "What is machine learning?",
            "How does photosynthesis work?",
            "What is the speed of light?",
            "What is gravity?",
            "How do computers work?",
            "What is DNA?",
            "What is the water cycle?",
            "What is democracy?",
        ] * 100

        high_conf_labels = [self.config.high_confidence_threshold] * len(high_conf_texts)

        med_conf_texts = [
            "How do neural networks learn?",
            "What are the benefits of renewable energy?",
            "How does the immune system work?",
            "What causes climate change?",
            "How do vaccines work?",
            "What is quantum computing?",
            "How does artificial intelligence work?",
            "What is blockchain technology?",
        ] * 100

        med_conf_labels = [self.config.medium_confidence_threshold] * len(med_conf_texts)

        low_conf_texts = [
            "What is my password?",
            "Tell me my personal email address?",
            "What will happen tomorrow?",
            "What is my home address?",
            "What will the stock market do next week?",
            "Who will win the next election?",
            "What are my personal thoughts?",
            "What is my bank account number?",
            "Can you predict the lottery numbers?",
            "What will I do next year?",
        ] * 100

        low_conf_labels = [self.config.low_confidence_threshold] * len(low_conf_texts)

        all_texts = high_conf_texts + med_conf_texts + low_conf_texts
        all_labels = high_conf_labels + med_conf_labels + low_conf_labels

        logger.info(f"✅ Synthetic examples created: {len(all_texts)} examples")
        self.datasets_loaded.append(f"Synthetic: {len(all_texts)} examples")
        return all_texts, all_labels

    def load_all_datasets(self) -> Tuple[List[str], List[float]]:
        """Load all enabled datasets and combine them for training"""
        logger.info("🚀 LOADING MULTIPLE DATASETS FOR HALLUCINATION DETECTION")
        logger.info("=" * 70)

        all_texts, all_labels = [], []

        if self.config.use_truthfulqa:
            texts, labels = self.load_truthfulqa_dataset()
            all_texts.extend(texts)
            all_labels.extend(labels)

        if self.config.use_halueval:
            texts, labels = self.load_halueval_dataset()
            all_texts.extend(texts)
            all_labels.extend(labels)

        if self.config.use_fever:
            texts, labels = self.load_fever_dataset()
            all_texts.extend(texts)
            all_labels.extend(labels)

        if self.config.use_xsum_factuality:
            texts, labels = self.load_xsum_factuality_dataset()
            all_texts.extend(texts)
            all_labels.extend(labels)

        if self.config.use_squad_v2:
            texts, labels = self.load_squad_v2_dataset()
            all_texts.extend(texts)
            all_labels.extend(labels)

        if self.config.use_natural_questions:
            texts, labels = self.load_natural_questions_dataset()
            all_texts.extend(texts)
            all_labels.extend(labels)

        texts, labels = self.create_synthetic_examples()
        all_texts.extend(texts)
        all_labels.extend(labels)

        # Shuffle combined dataset
        combined = list(zip(all_texts, all_labels))
        random.shuffle(combined)
        all_texts, all_labels = zip(*combined)

        logger.info("=" * 70)
        logger.info(f"📊 FINAL COMBINED DATASET SUMMARY:")
        logger.info(f"   Total examples: {len(all_texts):,}")
        logger.info(f"   High confidence (≥{self.config.high_confidence_threshold}): {sum(1 for l in all_labels if l >= self.config.high_confidence_threshold):,}")
        logger.info(f"   Medium confidence ({self.config.medium_confidence_threshold}-{self.config.high_confidence_threshold}): {sum(1 for l in all_labels if self.config.medium_confidence_threshold <= l < self.config.high_confidence_threshold):,}")
        logger.info(f"   Low confidence (<{self.config.medium_confidence_threshold}): {sum(1 for l in all_labels if l < self.config.medium_confidence_threshold):,}")
        logger.info("\n   📋 Datasets loaded:")
        for dataset_info in self.datasets_loaded:
            logger.info(f"      - {dataset_info}")
        logger.info("=" * 70)

        return list(all_texts), list(all_labels)


class HallucinationDataset(Dataset):
    """
    PyTorch Dataset class for hallucination detection training.
    
    This dataset pre-computes BGE-M3 embeddings and pairs them with
    confidence labels for efficient training.
    """
    
    def __init__(
        self,
        texts: List[str],
        labels: List[float],
        embed_model: BGEM3FlagModel,
        device: str = "cuda",
        max_length: int = 512,
    ):
        self.texts = texts
        self.labels = torch.tensor(labels, dtype=torch.float32)
        self.embed_model = embed_model
        self.device = device
        self.max_length = max_length

        logger.info(f"🔄 Computing BGE-M3 embeddings for {len(texts)} samples...")

        # Compute embeddings in batches
        batch_size = 16
        embeddings = []

        for i in tqdm(range(0, len(texts), batch_size), desc="Computing BGE-M3 embeddings"):
            batch_texts = texts[i:i+batch_size]

            # Use BGE-M3 encode method to get dense embeddings
            batch_outputs = self.embed_model.encode(
                batch_texts,
                batch_size=len(batch_texts),
                max_length=max_length,
                return_dense=True,
                return_sparse=False,
                return_colbert_vecs=False,
            )

            batch_embeddings = torch.tensor(
                batch_outputs['dense_vecs'],
                dtype=torch.float32
            )
            embeddings.append(batch_embeddings)

        self.embeddings = torch.cat(embeddings, dim=0)
        logger.info(f"✅ BGE-M3 embeddings computed: {self.embeddings.shape}")

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        return {
            "text": self.texts[idx],
            "ref_emb": self.embeddings[idx],
            "label": self.labels[idx],
        }


def simple_collate_fn(batch):
    """Simple collate function for the HallucinationDataset"""
    texts = [d["text"] for d in batch]
    ref_embs = torch.stack([d["ref_emb"] for d in batch])
    labels = torch.stack([d["label"] for d in batch])
    return {"texts": texts, "ref_embs": ref_embs, "labels": labels}


class Trainer:
    """
    Main trainer class for the hallucination detection model.
    
    This implements the training pipeline described in the research paper,
    combining Llama-3.2-3B with BGE-M3 for confidence-aware routing.
    """
    
    def __init__(self, config: TrainingConfig):
        self.config = config
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"🚀 Using device: {self.device}")

        if not BGE_M3_AVAILABLE:
            raise ImportError("FlagEmbedding is required for BGE-M3. Install with: pip install -U FlagEmbedding")

        # Load models
        logger.info("📥 Loading Llama-3.2-3B-Instruct model...")
        self.tokenizer = AutoTokenizer.from_pretrained(config.model_id)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        model_dtype = torch.float16 if (config.use_fp16 and torch.cuda.is_available()) else torch.float32
        self.llm = AutoModelForCausalLM.from_pretrained(
            config.model_id,
            torch_dtype=model_dtype,
            device_map="auto" if torch.cuda.is_available() else None,
        )

        logger.info("📥 Loading BGE-M3 embedding model...")
        self.embed_model = BGEM3FlagModel(
            config.embed_model_id,
            use_fp16=config.bge_use_fp16
        )

        # Create projection head with correct dimensions
        self.projector = ProjectionHead(
            config.llm_hidden_size,  # 3072 for Llama-3.2-3B
            config.embedding_dim,    # 1024 for BGE-M3
            hidden_dim=1536,         # Intermediate dimension
        ).to(self.device)

        logger.info(f"📐 LLM hidden size: {config.llm_hidden_size}")
        logger.info(f"📐 BGE-M3 embedding size: {config.embedding_dim}")

        self.optimizer = optim.AdamW(
            self.projector.parameters(),
            lr=config.learning_rate,
            weight_decay=config.weight_decay,
        )

        self.scaler = GradScaler() if (config.use_fp16 and torch.cuda.is_available()) else None

        os.makedirs(config.output_dir, exist_ok=True)

        if config.use_wandb:
            try:
                import wandb
                wandb.init(project=config.wandb_project, config=config.__dict__)
            except ImportError:
                logger.warning("⚠️ wandb not installed, skipping logging")

    def create_dataset(self) -> Tuple[List[str], List[float]]:
        """Create enhanced dataset using multiple sources"""
        dataset_loader = MultiDatasetLoader(self.config)
        return dataset_loader.load_all_datasets()

    def train(self):
        """Main training loop implementing the multi-signal confidence estimation"""
        texts, labels = self.create_dataset()

        # Shuffle & split
        data = list(zip(texts, labels))
        random.shuffle(data)
        split_idx = int(len(data) * (1 - self.config.val_split))
        train_data = data[:split_idx]
        val_data = data[split_idx:]

        logger.info(f"🎯 Training on {len(train_data):,} samples, validating on {len(val_data):,}")

        train_ds = HallucinationDataset(
            [t for t, _ in train_data],
            [l for _, l in train_data],
            self.embed_model,
            self.device,
            self.config.bge_max_length,
        )
        val_ds = HallucinationDataset(
            [t for t, _ in val_data],
            [l for _, l in val_data],
            self.embed_model,
            self.device,
            self.config.bge_max_length,
        )

        train_loader = DataLoader(
            train_ds,
            batch_size=self.config.batch_size,
            shuffle=True,
            num_workers=self.config.num_workers,
            collate_fn=simple_collate_fn,
            pin_memory=True if self.device == "cuda" else False,
        )
        val_loader = DataLoader(
            val_ds,
            batch_size=self.config.batch_size,
            shuffle=False,
            num_workers=self.config.num_workers,
            collate_fn=simple_collate_fn,
            pin_memory=True if self.device == "cuda" else False,
        )

        total_steps = (len(train_loader) * self.config.max_epochs) // self.config.gradient_accumulation_steps
        scheduler = get_linear_schedule_with_warmup(
            self.optimizer,
            num_warmup_steps=self.config.warmup_steps,
            num_training_steps=total_steps,
        )

        global_step = 0
        best_val_loss = float("inf")

        logger.info("🚀 Starting Llama-3.2-3B + BGE-M3 training!")
        logger.info("=" * 70)

        for epoch in range(self.config.max_epochs):
            logger.info(f"📅 Epoch {epoch + 1}/{self.config.max_epochs}")

            # Training
            self.projector.train()
            epoch_loss = 0
            train_pbar = tqdm(train_loader, desc=f"Training Epoch {epoch+1}")

            for batch_idx, batch in enumerate(train_pbar):
                llm_emb = get_pooled_embeddings(
                    self.llm,
                    self.tokenizer,
                    batch["texts"],
                    self.device,
                    self.config.max_length,
                )
                ref_embs = batch["ref_embs"].to(self.device)
                labels = batch["labels"].to(self.device)

                # Forward pass with optional mixed precision
                if self.scaler is not None:
                    with autocast():
                        llm_emb = llm_emb.float()
                        proj = self.projector(llm_emb)
                        sim = F.cosine_similarity(proj, ref_embs, dim=1)
                        preds = torch.sigmoid(sim)
                        loss = F.mse_loss(preds, labels) / self.config.gradient_accumulation_steps
                    self.scaler.scale(loss).backward()
                else:
                    llm_emb = llm_emb.float()
                    proj = self.projector(llm_emb)
                    sim = F.cosine_similarity(proj, ref_embs, dim=1)
                    preds = torch.sigmoid(sim)
                    loss = F.mse_loss(preds, labels) / self.config.gradient_accumulation_steps
                    loss.backward()

                if (batch_idx + 1) % self.config.gradient_accumulation_steps == 0:
                    if self.scaler is not None:
                        self.scaler.unscale_(self.optimizer)
                        torch.nn.utils.clip_grad_norm_(self.projector.parameters(), self.config.max_grad_norm)
                        self.scaler.step(self.optimizer)
                        self.scaler.update()
                    else:
                        torch.nn.utils.clip_grad_norm_(self.projector.parameters(), self.config.max_grad_norm)
                        self.optimizer.step()

                    scheduler.step()
                    self.optimizer.zero_grad()
                    global_step += 1

                epoch_loss += loss.item() * self.config.gradient_accumulation_steps

                train_pbar.set_postfix({
                    'Loss': f'{loss.item():.4f}',
                    'LR': f'{scheduler.get_last_lr()[0]:.2e}'
                })

                if batch_idx % self.config.log_steps == 0 and batch_idx > 0:
                    avg_loss = epoch_loss / (batch_idx + 1)
                    progress = (batch_idx + 1) / len(train_loader) * 100
                    logger.info(f"📊 Epoch {epoch+1} - Step {batch_idx}/{len(train_loader)} ({progress:.1f}%)")
                    logger.info(f"   Current Loss: {loss.item():.4f}")
                    logger.info(f"   Average Loss: {avg_loss:.4f}")
                    logger.info(f"   Learning Rate: {scheduler.get_last_lr()[0]:.2e}")
                    logger.info(f"   Global Step: {global_step}")

            # Validation
            logger.info("🔍 Running validation...")
            val_loss, metrics = self.validate(val_loader)

            logger.info("=" * 70)
            logger.info(f"📈 EPOCH {epoch+1} RESULTS:")
            logger.info(f"   Train Loss: {epoch_loss/len(train_loader):.4f}")
            logger.info(f"   Val Loss: {val_loss:.4f}")
            logger.info(f"   Accuracy: {metrics['accuracy']:.4f}")
            logger.info(f"   F1 Score: {metrics['f1']:.4f}")
            logger.info(f"   Precision: {metrics['precision']:.4f}")
            logger.info(f"   Recall: {metrics['recall']:.4f}")
            logger.info("=" * 70)

            # Save best model
            if val_loss < best_val_loss:
                logger.info(f"🏆 New best model! Validation loss improved: {best_val_loss:.4f} -> {val_loss:.4f}")
                best_val_loss = val_loss
                checkpoint = {
                    'projector_state': self.projector.state_dict(),
                    'optimizer_state': self.optimizer.state_dict(),
                    'scheduler_state': scheduler.state_dict(),
                    'config': self.config.__dict__,
                    'epoch': epoch,
                    'best_val_loss': best_val_loss,
                    'metrics': metrics,
                }

                model_path = os.path.join(self.config.output_dir, "best_model.pt")
                torch.save(checkpoint, model_path)
                logger.info(f"💾 Model checkpoint saved: {model_path}")

        logger.info("🎉 Llama-3.2-3B + BGE-M3 training completed!")

    def validate(self, loader: DataLoader) -> Tuple[float, dict]:
        """Validation loop with comprehensive metrics"""
        self.projector.eval()
        total_loss = 0
        all_preds, all_labels = [], []

        with torch.no_grad():
            val_pbar = tqdm(loader, desc="Validation")
            for batch in val_pbar:
                llm_emb = get_pooled_embeddings(
                    self.llm,
                    self.tokenizer,
                    batch["texts"],
                    self.device,
                    self.config.max_length,
                )
                ref_embs = batch["ref_embs"].to(self.device)
                labels = batch["labels"].to(self.device)

                llm_emb = llm_emb.float()
                proj = self.projector(llm_emb)
                sim = F.cosine_similarity(proj, ref_embs, dim=1)
                preds = torch.sigmoid(sim)
                loss = F.mse_loss(preds, labels)

                total_loss += loss.item()
                all_preds.extend(preds.cpu().tolist())
                all_labels.extend(labels.cpu().tolist())

                val_pbar.set_postfix({'Loss': f'{loss.item():.4f}'})

        avg_loss = total_loss / len(loader)

        # Calculate metrics
        bin_preds = [1 if p > 0.6 else 0 for p in all_preds]
        bin_labels = [1 if l > 0.6 else 0 for l in all_labels]

        if len(set(bin_labels)) == 1:
            accuracy = 1.0 if bin_preds == bin_labels else 0.0
            precision = recall = f1 = accuracy
        else:
            accuracy = accuracy_score(bin_labels, bin_preds)
            precision, recall, f1, _ = precision_recall_fscore_support(
                bin_labels, bin_preds, average="binary", zero_division=0
            )

        try:
            auc = roc_auc_score(all_labels, all_preds)
        except ValueError:
            auc = 0.0

        return avg_loss, {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "auc": auc,
        }


def main():
    """Main training function with command-line interface"""
    parser = argparse.ArgumentParser(description="Train hallucination detector with Llama-3.2-3B and BGE-M3")
    parser.add_argument("--batch_size", type=int, default=8, help="Batch size")
    parser.add_argument("--learning_rate", type=float, default=5e-4, help="Learning rate")
    parser.add_argument("--max_epochs", type=int, default=6, help="Maximum epochs")
    parser.add_argument("--output_dir", type=str, default="./models/hallucination_llama32_bge", help="Output directory")
    parser.add_argument("--model_id", type=str, default="unsloth/Llama-3.2-3B-Instruct", help="Model ID from HuggingFace")
    parser.add_argument("--embed_model_id", type=str, default="BAAI/bge-m3", help="Embedding model ID")
    parser.add_argument("--max_length", type=int, default=512, help="Max sequence length")
    parser.add_argument("--bge_max_length", type=int, default=512, help="Max BGE-M3 sequence length")

    # Dataset configuration
    parser.add_argument("--no_truthfulqa", action="store_true", help="Disable TruthfulQA dataset")
    parser.add_argument("--no_halueval", action="store_true", help="Disable HaluEval dataset")
    parser.add_argument("--no_fever", action="store_true", help="Disable FEVER dataset")
    parser.add_argument("--no_xsum_factuality", action="store_true", help="Disable XSum Factuality dataset")
    parser.add_argument("--no_squad_v2", action="store_true", help="Disable Squad v2 dataset")
    parser.add_argument("--no_natural_questions", action="store_true", help="Disable Natural Questions dataset")
    parser.add_argument("--max_samples_per_dataset", type=int, default=3000, help="Max samples per dataset")

    parser.add_argument("--use_wandb", action="store_true", help="Use Weights & Biases logging")
    parser.add_argument("--no_fp16", action="store_true", help="Disable FP16 training")
    parser.add_argument("--no_bge_fp16", action="store_true", help="Disable FP16 for BGE-M3")

    args = parser.parse_args()

    config = TrainingConfig(
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        max_epochs=args.max_epochs,
        output_dir=args.output_dir,
        model_id=args.model_id,
        embed_model_id=args.embed_model_id,
        max_length=args.max_length,
        bge_max_length=args.bge_max_length,
        use_truthfulqa=not args.no_truthfulqa,
        use_halueval=not args.no_halueval,
        use_fever=not args.no_fever,
        use_xsum_factuality=not args.no_xsum_factuality,
        use_squad_v2=not args.no_squad_v2,
        use_natural_questions=not args.no_natural_questions,
        max_samples_per_dataset=args.max_samples_per_dataset,
        use_wandb=args.use_wandb,
        use_fp16=not args.no_fp16,
        bge_use_fp16=not args.no_bge_fp16,
    )

    logger.info("🚀 LLAMA-3.2-3B + BGE-M3 HALLUCINATION DETECTION TRAINING")
    logger.info("=" * 70)
    logger.info("Configuration:")
    for k, v in config.__dict__.items():
        logger.info(f"  {k}: {v}")
    logger.info("=" * 70)
    logger.info("📋 Model Details:")
    logger.info(f"  LLM: {config.model_id} (Hidden Size: {config.llm_hidden_size})")
    logger.info(f"  Embeddings: {config.embed_model_id} (Dimension: {config.embedding_dim})")
    logger.info("=" * 70)

    trainer = Trainer(config)
    trainer.train()


if __name__ == "__main__":
    main()
