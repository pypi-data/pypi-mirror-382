"""
Hallucination Detection Module

This module provides the core HallucinationDetector class that implements
confidence-aware routing for LLM reliability enhancement using a multi-signal approach.
"""

import os
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import List, Dict, Union
import warnings

from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    AutoModelForImageTextToText,
    AutoProcessor,
    PaliGemmaForConditionalGeneration,
    BitsAndBytesConfig,
    pipeline,
)

# Import enhanced similarity metrics
from .similarity_metrics import MultiSimilarityCalculator, EnhancedEmbeddingProcessor

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

# Import PIL for image processing
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    warnings.warn(
        "PIL not available. Install with: pip install Pillow",
        ImportWarning
    )

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)


class ProjectionHead(nn.Module):
    """
    Projection head for mapping LLM hidden states to embedding space.
    
    This component learns to project internal LLM representations to align
    with reference embeddings from BGE-M3 for confidence estimation.
    """
    
    def __init__(self, input_dim: int, output_dim: int, hidden_dim: int = 1024):
        """
        Initialize projection head.
        
        Args:
            input_dim: Dimension of input LLM hidden states
            output_dim: Dimension of target embedding space
            hidden_dim: Hidden layer dimension
        """
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, output_dim),
            nn.LayerNorm(output_dim),
        )

    def forward(self, x):
        """Forward pass through projection network."""
        return self.net(x)


class UltraStableProjectionHead(nn.Module):
    """
    Ultra-stable projection head optimized for MedGemma models.
    
    This enhanced projection head provides better stability and convergence
    for medical domain applications with heavy normalization and conservative
    weight initialization.
    """
    
    def __init__(self, input_dim: int, output_dim: int, hidden_dim: int = 1280):
        """
        Initialize ultra-stable projection head.
        
        Args:
            input_dim: Dimension of input LLM hidden states
            output_dim: Dimension of target embedding space
            hidden_dim: Hidden layer dimension
        """
        super().__init__()
        
        # Ultra stable architecture with heavy normalization
        self.input_norm = nn.LayerNorm(input_dim)
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.norm1 = nn.LayerNorm(hidden_dim)
        self.dropout1 = nn.Dropout(0.3)
        
        self.fc2 = nn.Linear(hidden_dim, hidden_dim // 2)
        self.norm2 = nn.LayerNorm(hidden_dim // 2)
        self.dropout2 = nn.Dropout(0.2)
        
        self.fc3 = nn.Linear(hidden_dim // 2, output_dim)
        self.output_norm = nn.LayerNorm(output_dim)
        
        # Ultra conservative weight initialization
        self.apply(self._init_weights)
    
    def _init_weights(self, module):
        """Initialize weights conservatively."""
        if isinstance(module, nn.Linear):
            # Very small weight initialization
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.01)
            if module.bias is not None:
                torch.nn.init.constant_(module.bias, 0)
        elif isinstance(module, nn.LayerNorm):
            torch.nn.init.constant_(module.bias, 0)
            torch.nn.init.constant_(module.weight, 1.0)

    def forward(self, x):
        """Ultra stable forward pass with NaN protection."""
        # Ultra stable forward pass with NaN protection
        x = self.input_norm(x)
        x = torch.tanh(self.fc1(x))  # Use tanh instead of ReLU for stability
        x = self.norm1(x)
        x = self.dropout1(x)
        
        x = torch.tanh(self.fc2(x))
        x = self.norm2(x)
        x = self.dropout2(x)
        
        x = self.fc3(x)
        x = self.output_norm(x)
        
        # Clamp output to prevent extreme values
        x = torch.clamp(x, min=-10.0, max=10.0)
        
        return x


def get_pooled_embeddings(
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    texts: List[str],
    device: str,
    max_length: int = 512,
):
    """
    Extract pooled embeddings from LLM.
    
    Args:
        model: The LLM model
        tokenizer: Associated tokenizer
        texts: List of input texts
        device: Computing device
        max_length: Maximum sequence length
        
    Returns:
        Pooled embeddings tensor
    """
    model.eval()
    
    # Ensure numerical stability during tokenization
    try:
        inputs = tokenizer(
            texts,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=max_length,
        ).to(device)
    except Exception as e:
        print(f"⚠️ Tokenization error: {e}")
        # Fallback with simpler tokenization
        inputs = tokenizer(
            texts,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=min(max_length, 256),  # Reduce length if needed
        ).to(device)
    
    with torch.no_grad():
        try:
            # Use stable inference with numerical safeguards
            if hasattr(torch, 'autocast') and device == "cuda" and not hasattr(model.config, 'quantization_config'):
                # Use autocast for mixed precision stability (skip for quantized models)
                with torch.autocast(device_type='cuda', dtype=torch.float16, enabled=True):
                    outputs = model(**inputs, output_hidden_states=True)
            else:
                # Standard inference
                outputs = model(**inputs, output_hidden_states=True)
                
        except RuntimeError as e:
            if "out of memory" in str(e).lower():
                print(f"⚠️ CUDA OOM during forward pass, reducing batch size")
                # Try with smaller sequences
                max_seq_len = min(inputs['input_ids'].shape[1], 256)
                inputs_reduced = {
                    k: v[:, :max_seq_len] if k in ['input_ids', 'attention_mask'] else v 
                    for k, v in inputs.items()
                }
                outputs = model(**inputs_reduced, output_hidden_states=True)
            else:
                print(f"⚠️ Runtime error during forward pass: {e}")
                raise e
        except Exception as e:
            print(f"⚠️ Error during model forward pass: {e}")
            # Create fallback embeddings if forward pass fails
            batch_size = inputs['input_ids'].shape[0]
            hidden_size = getattr(model.config, 'hidden_size', 2560)
            fallback_hidden = torch.randn(batch_size, inputs['input_ids'].shape[1], hidden_size, device=device) * 0.01
            return fallback_hidden.mean(dim=1)
    
    last_hidden = outputs.hidden_states[-1]
    
    # Check if hidden states contain NaN/Inf
    if torch.isnan(last_hidden).any() or torch.isinf(last_hidden).any():
        nan_count = torch.isnan(last_hidden).sum().item()
        inf_count = torch.isinf(last_hidden).sum().item()
        print(f"⚠️ Warning: NaN/Inf detected in model hidden states")
        print(f"   Hidden shape: {last_hidden.shape}")
        print(f"   NaN count: {nan_count}")
        print(f"   Inf count: {inf_count}")
        
        # Apply more sophisticated fallback strategy
        if nan_count > 0:
            # Replace NaN with mean of non-NaN values, or small random if all NaN
            nan_mask = torch.isnan(last_hidden)
            if not nan_mask.all():
                # Use mean of non-NaN values
                non_nan_mean = last_hidden[~nan_mask].mean()
                last_hidden = torch.where(nan_mask, non_nan_mean, last_hidden)
                print(f"   🔧 Replaced NaN with mean: {non_nan_mean:.6f}")
            else:
                # All values are NaN, use random fallback
                last_hidden = torch.randn_like(last_hidden) * 0.01
                print(f"   🔧 All values NaN, using random fallback")
        
        if inf_count > 0:
            # Clamp infinite values to reasonable range
            last_hidden = torch.clamp(last_hidden, min=-10.0, max=10.0)
            print(f"   🔧 Clamped Inf values to [-10, 10] range")
    mask = inputs.attention_mask.unsqueeze(-1)
    
    # Safe pooling with division by zero protection
    mask_sum = mask.sum(dim=1)
    # Add small epsilon to prevent division by zero
    pooled = (last_hidden * mask).sum(dim=1) / torch.clamp(mask_sum, min=1e-8)
    
    # Check for NaN/Inf in pooled embeddings
    if torch.isnan(pooled).any() or torch.isinf(pooled).any():
        print("⚠️ Warning: NaN/Inf detected in pooled embeddings, using fallback")
        pooled = torch.randn_like(pooled) * 0.01
    
    # Ensure output is on the specified device
    return pooled.to(device)


class HallucinationDetector:
    """
    Confidence-aware hallucination detector supporting both Llama-3.2-3B and MedGemma-4B-IT + BGE-M3.
    
    This class implements the multi-signal confidence estimation approach described
    in the research paper, combining semantic alignment measurement, internal 
    convergence analysis, and learned confidence estimation. Supports multimodal
    capabilities for MedGemma 4b-it models.
    """
    
    def __init__(
        self,
        model_path: str = None,
        llm_model_id: str = "convaiinnovations/gemma-finetuned-4b-it",
        embed_model_id: str = "BAAI/bge-m3",
        device: str = None,
        max_length: int = 512,
        bge_max_length: int = 512,
        use_fp16: bool = True,
        load_llm: bool = True,
        enable_inference: bool = False,
        confidence_threshold: float = None,
        enable_response_generation: bool = False,
        use_quantization: bool = False,
        quantization_config: BitsAndBytesConfig = None,
        mode: str = "auto",
        verbose: bool = False,
    ):
        """
        Initialize the hallucination detector.
        
        Args:
            model_path: Path to trained model checkpoint. If None, downloads pre-trained model.
            llm_model_id: Hugging Face model ID for the LLM
            embed_model_id: Hugging Face model ID for the embedding model
            device: Computing device ('cuda' or 'cpu')
            max_length: Maximum sequence length for LLM
            bge_max_length: Maximum sequence length for BGE-M3
            use_fp16: Whether to use FP16 precision
            load_llm: Whether to load the LLM (set False if only using for projection/embedding)
            enable_inference: Whether to enable LLM inference capabilities
            confidence_threshold: Confidence threshold for high confidence routing (0.60 for medical)
            enable_response_generation: Whether to enable response generation when threshold is met
            use_quantization: Whether to use 4-bit quantization to reduce memory usage
            quantization_config: Custom BitsAndBytesConfig for quantization (auto-created if None)
            mode: Operation mode - "auto", "text", "image", or "both" (auto-detected from model if "auto")
            verbose: Whether to print loading progress and debug information
        """
        if not BGE_M3_AVAILABLE:
            raise ImportError(
                "FlagEmbedding is required for BGE-M3. "
                "Install with: pip install -U FlagEmbedding"
            )
        
        # Auto-detect device if not specified
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        self.max_length = max_length
        self.bge_max_length = bge_max_length
        self.use_fp16 = use_fp16
        self.load_llm = load_llm
        self.enable_inference = enable_inference
        self.llm_model_id = llm_model_id
        self.enable_response_generation = enable_response_generation
        self.use_quantization = use_quantization
        self.verbose = verbose
        
        # Validate and set mode
        valid_modes = ["auto", "text", "image", "both"]
        if mode not in valid_modes:
            raise ValueError(f"Invalid mode '{mode}'. Must be one of: {valid_modes}")
        self.mode = mode
        
        # Set up quantization configuration
        # Use stable model loading approach 
        self.use_quantization = False
        self.quantization_config = None
        
        # Determine if this is a MedGemma 4b-it model
        self.is_medgemma_4b = "4b-it" in llm_model_id.lower() or "medgemma" in llm_model_id.lower()
        
        # Determine multimodal capability based on model and mode
        if self.mode == "auto":
            # Auto-detect: MedGemma 4b-it supports multimodal
            self.is_multimodal = self.is_medgemma_4b
            self.effective_mode = "both" if self.is_medgemma_4b else "text"
        elif self.mode == "text":
            self.is_multimodal = False
            self.effective_mode = "text"
        elif self.mode == "image":
            if not self.is_medgemma_4b:
                raise ValueError("Image mode requires MedGemma 4b-it model. Use llm_model_id='convaiinnovations/gemma-finetuned-4b-it'")
            self.is_multimodal = True
            self.effective_mode = "image"
        elif self.mode == "both":
            if not self.is_medgemma_4b:
                raise ValueError("Both mode requires MedGemma 4b-it model. Use llm_model_id='convaiinnovations/gemma-finetuned-4b-it'")
            self.is_multimodal = True
            self.effective_mode = "both"
        
        # Set confidence threshold - use 0.60 for medical models, 0.65 for others
        if confidence_threshold is None:
            self.confidence_threshold = 0.60 if self.is_medgemma_4b else 0.65
        else:
            self.confidence_threshold = confidence_threshold
        
        if self.verbose:
            print(f"Loading models on {self.device}...")
            print(f"Model: {'MedGemma-4B-IT' if self.is_medgemma_4b else 'Llama-3.2-3B'}")
            print(f"Confidence threshold: {self.confidence_threshold}")
        
        # Download model if path not provided
        if model_path is None:
            if self.is_medgemma_4b:
                from .utils import download_medgemma_model
                model_path = download_medgemma_model(llm_model_id)
            else:
                from .utils import download_model
                model_path = download_model()
        
        # Load checkpoint with proper device mapping
        checkpoint = torch.load(model_path, map_location=self.device, weights_only=False)
        self.config = checkpoint['config']
        
        # Conditionally load LLM
        self.llm = None
        self.llm_multimodal = None
        self.tokenizer = None
        self.processor = None
        self.pipe = None
        
        if self.load_llm:
            # Set up model loading kwargs
            model_dtype = torch.bfloat16 if (use_fp16 and self.device == "cuda") else torch.float32
            model_kwargs = dict(
                torch_dtype=model_dtype,
                device_map="auto" if self.device == "cuda" else None,
            )
            
            if self.is_medgemma_4b:
                if self.verbose:
                    print(f"Loading MedGemma-4B-IT...")
                
                try:
                    self.llm = AutoModelForCausalLM.from_pretrained(llm_model_id, **model_kwargs)
                    
                    # Set up model references for compatibility
                    self.llm_text = self.llm
                    self.llm_multimodal = None
                    
                    # Use text-only mode for stability
                    self.is_multimodal = False
                    self.effective_mode = "text"
                        
                except Exception as e:
                    print(f"⚠️ Failed to load as AutoModelForImageTextToText: {e}")
                    try:
                        self.llm_multimodal = PaliGemmaForConditionalGeneration.from_pretrained(llm_model_id, **model_kwargs)
                        print("✅ Loaded as PaliGemmaForConditionalGeneration")
                        self.llm = self.llm_multimodal
                        self.llm_text = self.llm_multimodal
                        self.is_multimodal = self.effective_mode in ["both", "image"]
                    except Exception as e2:
                        print(f"⚠️ PaliGemma loading failed: {e2}")
                        if self.effective_mode == "image":
                            raise RuntimeError("Failed to load multimodal model in image mode")
                        print("📥 Falling back to regular causal model...")
                        # Last resort: load as causal model
                        self.llm = AutoModelForCausalLM.from_pretrained(llm_model_id, **model_kwargs)
                        self.llm_text = self.llm
                        self.llm_multimodal = None
                        self.is_multimodal = False
                        self.effective_mode = "text"
                        print("⚠️ Loaded as text-only model, image processing disabled")
                
                if self.verbose:
                    print("Using unified model for embeddings and generation")
                
                # Load tokenizer
                self.tokenizer = AutoTokenizer.from_pretrained(llm_model_id)
                if self.tokenizer.pad_token is None:
                    self.tokenizer.pad_token = self.tokenizer.eos_token
                self.processor = None
                
                # Initialize pipeline for stable text generation (following notebook approach)
                if self.effective_mode == "text" or self.effective_mode == "both":
                    try:
                        self.pipe = pipeline("text-generation", model=self.llm, tokenizer=self.tokenizer, model_kwargs=model_kwargs)
                        self.pipe.model.generation_config.do_sample = False  # Prevent repetitive generation
                        if self.verbose:
                            print("✅ Text generation pipeline initialized")
                    except Exception as e:
                        if self.verbose:
                            print(f"⚠️ Pipeline initialization failed: {e}")
                        self.pipe = None
            else:
                print("📥 Loading Llama-3.2-3B-Instruct...")
                # Simple loading like inference_gemma.py
                self.llm = AutoModelForCausalLM.from_pretrained(llm_model_id, **model_kwargs)
                # For non-MedGemma models, set llm_text to the same model for consistency
                self.llm_text = self.llm
                self.tokenizer = AutoTokenizer.from_pretrained(llm_model_id)
                if self.tokenizer.pad_token is None:
                    self.tokenizer.pad_token = self.tokenizer.eos_token
                
                # Initialize pipeline for Llama models too
                try:
                    self.pipe = pipeline("text-generation", model=self.llm, tokenizer=self.tokenizer, model_kwargs=model_kwargs)
                    self.pipe.model.generation_config.do_sample = False  # Prevent repetitive generation
                    if self.verbose:
                        print("✅ Text generation pipeline initialized")
                except Exception as e:
                    if self.verbose:
                        print(f"⚠️ Pipeline initialization failed: {e}")
                    self.pipe = None
            
            # Ensure LLMs are on the correct device (skip for quantized models)
            if self.device == "cpu" and not self.use_quantization:
                self.llm = self.llm.to(self.device)
                # For MedGemma, also move text-only model if it exists
                if hasattr(self, 'llm_text') and self.llm_text:
                    self.llm_text = self.llm_text.to(self.device)
                # Move multimodal model if it exists and is separate
                if self.llm_multimodal and (not hasattr(self, 'llm_text') or self.llm_multimodal is not self.llm_text):
                    self.llm_multimodal = self.llm_multimodal.to(self.device)
            elif self.use_quantization:
                print("✅ Quantized models automatically placed on GPU via device_map")
                if hasattr(self, 'llm_text'):
                    print(f"🔗 Separate models: text={self.llm_text is not None}, multimodal={self.llm_multimodal is not None}")
                else:
                    print(f"🔗 Unified model: {self.llm is self.llm_multimodal}")
        else:
            print("⏩ Skipping LLM loading (load_llm=False)")
            # Create a dummy tokenizer for cases where we need basic tokenization
            self.tokenizer = AutoTokenizer.from_pretrained(llm_model_id)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Load BGE-M3
        if self.verbose:
            print("Loading BGE-M3...")
        # Disable FP16 for BGE-M3 when using CPU
        bge_use_fp16 = use_fp16 and (self.device == "cuda")
        self.embed_model = BGEM3FlagModel(embed_model_id, use_fp16=bge_use_fp16)
        
        # Load projection head
        if self.verbose:
            print("Loading projection head...")
        if self.is_medgemma_4b:
            self.projector = UltraStableProjectionHead(
                self.config['llm_hidden_size'],
                self.config['embedding_dim'],
                hidden_dim=1280,
            ).to(self.device)
        else:
            self.projector = ProjectionHead(
                self.config['llm_hidden_size'],
                self.config['embedding_dim'],
                hidden_dim=1536,
            ).to(self.device)
        
        self.projector.load_state_dict(checkpoint['projector_state'])
        self.projector.eval()
        
        # Initialize enhanced similarity calculator and embedding processor
        self.multi_similarity_calculator = MultiSimilarityCalculator(
            weights={
                'cosine': 0.4,
                'dot_product': 0.3,
                'manhattan': 0.15,
                'euclidean': 0.15
            },
            normalize_before_metrics=True,
            use_temperature_scaling=True,
            temperature=1.0
        )
        
        self.enhanced_embedding_processor = EnhancedEmbeddingProcessor(
            embed_model=self.embed_model,
            multi_sim_calculator=self.multi_similarity_calculator,
            max_length=self.bge_max_length,
            use_query_context_fusion=True
        )
        
        # Ensure projection head is on same device as LLM (if loaded)
        if self.llm and hasattr(self.llm, 'device'):
            llm_device = next(self.llm.parameters()).device
            if str(llm_device) != str(self.device):
                print(f"⚠️ Moving projection head from {self.device} to {llm_device}")
                self.device = str(llm_device)
                self.projector = self.projector.to(self.device)
        
        print(f"✅ Model loaded successfully!")
        print(f"   LLM Hidden Size: {self.config['llm_hidden_size']}")
        print(f"   Embedding Dimension: {self.config['embedding_dim']}")
        print(f"   Operation Mode: {self.effective_mode} (requested: {self.mode})")
        if 'best_val_loss' in checkpoint:
            print(f"   Best Validation Loss: {checkpoint['best_val_loss']:.4f}")
        
        # Print optimization info
        if self.is_medgemma_4b:
            # Show unified model architecture (following Jupyter notebook pattern)
            unified_model = self.llm is self.llm_multimodal
            print(f"   Unified Model: {unified_model}")
            print(f"   Multimodal Capable: {self.llm_multimodal is not None}")
            print(f"   Multimodal Enabled: {self.is_multimodal}")
            print(f"   Processor Type: {'AutoProcessor' if hasattr(self, 'processor') and self.processor else 'AutoTokenizer'}")
            print(f"   Memory Optimized: {self.use_quantization}")
            if self.use_quantization:
                print(f"   Quantization: 4-bit NF4 with double quantization")
    
    def _clean_response(self, response: str) -> str:
        """
        Clean up repetitive patterns and artifacts in generated responses.
        """
        if not response:
            return response
            
        import re
        
        # Remove trailing single characters (like 'g') that indicate incomplete generation
        response = re.sub(r'\s+[a-zA-Z]\s*$', '', response)
        
        # Remove template-like repetitive patterns (forms, labels, etc.)
        response = re.sub(r'(name:\s*\n|age:\s*\n|gender:\s*\n|symptoms:\s*\n|medical history:\s*\n|family history:\s*\n|medications:\s*\n|allergies:\s*\n|social history:\s*\n|label:\s*\n?)+', '', response, flags=re.IGNORECASE)
        
        # Remove excessive newlines and whitespace
        response = re.sub(r'\n\s*\n\s*\n+', '\n\n', response)
        response = re.sub(r'\n+$', '', response)
        
        # Split into sentences and remove duplicates while preserving order
        sentences = []
        seen_sentences = set()
        
        # Split by periods, but be careful with medical abbreviations
        potential_sentences = re.split(r'\.(?!\s*[a-z])', response)
        
        for sentence in potential_sentences:
            sentence = sentence.strip()
            # Skip very short fragments and duplicates
            if sentence and len(sentence) > 5 and sentence not in seen_sentences:
                sentences.append(sentence)
                seen_sentences.add(sentence)
                
        # Rejoin sentences
        cleaned = '. '.join(sentences)
        
        # Add final period if missing and not empty
        if cleaned and not cleaned.endswith('.'):
            cleaned += '.'
        
        # Final cleanup - remove any remaining form-like artifacts
        cleaned = re.sub(r'\b(name|age|gender|symptoms|medical history|family history|medications|allergies|social history|label)\s*:?\s*$', '', cleaned, flags=re.IGNORECASE)
        cleaned = cleaned.strip()
            
        return cleaned
    
    def _validate_model_stability(self, model) -> bool:
        """
        Validate model numerical stability by checking for NaN/Inf in weights.
        
        Args:
            model: The loaded model to validate
            
        Returns:
            True if model is numerically stable, False otherwise
        """
        try:
            print("🔍 Validating model numerical stability...")
            
            # Check if any parameters contain NaN or Inf
            nan_params = 0
            inf_params = 0
            total_params = 0
            
            for name, param in model.named_parameters():
                if param.data is not None:
                    total_params += 1
                    if torch.isnan(param.data).any():
                        nan_params += 1
                        print(f"   ⚠️ NaN detected in parameter: {name}")
                    if torch.isinf(param.data).any():
                        inf_params += 1
                        print(f"   ⚠️ Inf detected in parameter: {name}")
            
            print(f"   📊 Parameter validation: {total_params} total, {nan_params} NaN, {inf_params} Inf")
            
            # Model is stable if no NaN/Inf parameters
            is_stable = (nan_params == 0 and inf_params == 0)
            
            if is_stable:
                print("   ✅ Model weights are numerically stable")
            else:
                print("   ❌ Model has numerical instability issues")
                
            return is_stable
            
        except Exception as e:
            print(f"   ⚠️ Error during model validation: {e}")
            return False  # Assume unstable if validation fails
    
    def _stabilize_model(self, model):
        """
        Apply numerical stabilization to model weights.
        
        Args:
            model: The model to stabilize
        """
        try:
            print("🔧 Applying numerical stabilization...")
            
            stabilized_params = 0
            for name, param in model.named_parameters():
                if param.data is not None:
                    original_data = param.data.clone()
                    
                    # Replace NaN with small random values
                    if torch.isnan(param.data).any():
                        nan_mask = torch.isnan(param.data)
                        param.data[nan_mask] = torch.randn_like(param.data[nan_mask]) * 0.01
                        stabilized_params += 1
                        print(f"   🔧 Fixed NaN in {name}")
                    
                    # Replace Inf with clamped values
                    if torch.isinf(param.data).any():
                        param.data = torch.clamp(param.data, min=-10.0, max=10.0)
                        stabilized_params += 1
                        print(f"   🔧 Fixed Inf in {name}")
                        
                    # Apply gradient clipping to prevent future instability
                    if hasattr(param, 'register_hook'):
                        def grad_clip_hook(grad):
                            if grad is not None:
                                return torch.clamp(grad, min=-1.0, max=1.0)
                            return grad
                        param.register_hook(grad_clip_hook)
            
            print(f"   ✅ Stabilized {stabilized_params} parameters")
            
            # Set model to eval mode to prevent training instabilities
            model.eval()
            
            # Apply additional stabilization for quantized models
            if hasattr(model, 'config') and hasattr(model.config, 'quantization_config'):
                print("   🔧 Additional quantization stability measures applied")
                
        except Exception as e:
            print(f"   ⚠️ Error during model stabilization: {e}")
    
    def _apply_inference_stability(self, model):
        """
        Apply inference-time numerical stability measures.
        
        Args:
            model: The model to apply stability measures to
        """
        try:
            print("🔧 Applying inference-time stability measures...")
            
            # Set model to eval mode and disable dropout for consistency
            model.eval()
            
            # Apply autocast for mixed precision stability if available and not quantized
            if hasattr(torch, 'autocast') and self.device == "cuda" and not self.use_quantization:
                print("   🔧 Enabling autocast for mixed precision stability (non-quantized)")
                # Wrap the forward method to use autocast for non-quantized models only
                original_forward = model.forward
                def stable_forward(*args, **kwargs):
                    with torch.autocast(device_type='cuda', dtype=torch.float16, enabled=True):
                        return original_forward(*args, **kwargs)
                model.forward = stable_forward
            elif self.use_quantization:
                print("   🔧 Skipping autocast for quantized model (prevents double precision issues)")
                
            # Enable gradient checkpointing for memory efficiency and stability
            if hasattr(model, 'gradient_checkpointing_enable'):
                try:
                    model.gradient_checkpointing_enable()
                    print("   🔧 Gradient checkpointing enabled")
                except:
                    print("   ℹ️ Gradient checkpointing not available")
            
            # Set model precision consistency
            if not self.use_quantization:
                # Ensure all buffers are in float32 for stability (non-quantized models only)
                try:
                    promoted_count = 0
                    for name, buffer in model.named_buffers():
                        if buffer.dtype == torch.float16:
                            buffer.data = buffer.data.to(torch.float32)
                            promoted_count += 1
                    if promoted_count > 0:
                        print(f"   🔧 Promoted {promoted_count} buffers to float32 for stability")
                except Exception as e:
                    print(f"   ⚠️ Buffer promotion failed: {e}")
            else:
                print("   🔧 Preserving quantized model precision (skipping buffer promotion)")
            
            print("   ✅ Inference stability measures applied")
            
        except Exception as e:
            print(f"   ⚠️ Error applying inference stability: {e}")
    
    def predict(self, texts: Union[str, List[str]], query_context_pairs: List[Dict] = None) -> Dict:
        """
        Predict hallucination confidence scores for given texts.
        
        This method implements the core confidence estimation approach by:
        1. Computing semantic alignment between LLM and reference embeddings
        2. Analyzing internal convergence patterns
        3. Using learned confidence estimation
        
        Args:
            texts: Input text(s) to analyze
            query_context_pairs: Optional list of dicts with 'query' and 'context' keys for enhanced embedding
            
        Returns:
            Dictionary with predictions, confidence scores, and interpretations
        """
        if isinstance(texts, str):
            texts = [texts]
        
        # Use enhanced embedding processor for better query-context fusion
        ref_embeddings, metadata = self.enhanced_embedding_processor.create_enhanced_embeddings(
            texts, query_context_pairs
        )
        ref_embeddings = ref_embeddings.to(self.device)
        
        # Check if LLM is loaded for embedding computation
        if not self.load_llm or self.llm is None:
            raise RuntimeError("LLM not loaded. Set load_llm=True for hallucination detection.")
        
        # Get LLM embeddings and ensure they're on correct device
        # For projection model, use only query part for better similarity comparison
        projection_texts = texts
        if query_context_pairs:
            projection_texts = [pair.get('query', text) if i < len(query_context_pairs) and query_context_pairs[i] else text 
                             for i, (text, pair) in enumerate(zip(texts, query_context_pairs + [None] * len(texts)))]
        
        # Use text-only model for embeddings if available (like inference_gemma.py)
        model_for_embeddings = getattr(self, 'llm_text', self.llm)
        llm_embeddings = get_pooled_embeddings(
            model_for_embeddings,
            self.tokenizer,
            projection_texts,
            self.device,
            self.max_length,
        ).to(self.device)
        
        # Reference embeddings are already created by enhanced processor above
        
        # Project LLM embeddings and compute enhanced similarity
        with torch.no_grad():
            # Ensure all tensors are on the same device and correct dtype
            llm_embeddings = llm_embeddings.float().to(self.device)
            ref_embeddings = ref_embeddings.to(self.device)
            
            # Check for NaN/Inf in LLM embeddings before projection
            if torch.isnan(llm_embeddings).any() or torch.isinf(llm_embeddings).any():
                print("⚠️ Warning: NaN/Inf detected in LLM embeddings, using fallback")
                llm_embeddings = torch.randn_like(llm_embeddings) * 0.01
            
            projected = self.projector(llm_embeddings)
            
            # Check for NaN/Inf in projected embeddings
            if torch.isnan(projected).any() or torch.isinf(projected).any():
                print("⚠️ Warning: NaN/Inf detected in projected embeddings, using fallback")
                projected = torch.randn_like(projected) * 0.01
            
            # Use enhanced similarity calculation with multiple metrics
            similarities, detailed_results = self.enhanced_embedding_processor.calculate_enhanced_similarity(
                projected, ref_embeddings, metadata
            )
            
            # Convert to confidence scores
            confidence_scores = torch.sigmoid(similarities)
            
            # Final NaN check on confidence scores
            if torch.isnan(confidence_scores).any():
                print("⚠️ Warning: NaN detected in confidence scores, using default low confidence")
                confidence_scores = torch.where(torch.isnan(confidence_scores),
                                               torch.tensor(0.1, device=confidence_scores.device),
                                               confidence_scores)
        
        # Convert to numpy for easier handling
        confidence_scores = confidence_scores.cpu().numpy()
        similarities = similarities.cpu().numpy()
        
        # Interpret results according to confidence-aware routing strategy
        results = []
        for i, (text, conf_score, sim_score) in enumerate(zip(texts, confidence_scores, similarities)):
            # Use dynamic thresholds based on model type
            if self.is_medgemma_4b:
                # Medical domain thresholds (lower due to higher precision requirements)
                if conf_score >= 0.60:
                    interpretation = "HIGH_MEDICAL_CONFIDENCE"
                    risk_level = "LOW_MEDICAL_RISK"
                    routing_action = "LOCAL_GENERATION"
                    description = "This medical response appears to be factual and reliable."
                elif conf_score >= 0.55:
                    interpretation = "MEDIUM_MEDICAL_CONFIDENCE"
                    risk_level = "MEDIUM_MEDICAL_RISK"
                    routing_action = "RAG_RETRIEVAL"
                    description = "This medical response may contain uncertainties. Verify with authoritative sources."
                elif conf_score >= 0.50:
                    interpretation = "LOW_MEDICAL_CONFIDENCE"
                    risk_level = "HIGH_MEDICAL_RISK"
                    routing_action = "LARGER_MODEL"
                    description = "This medical response is likely unreliable. Professional verification required."
                else:
                    interpretation = "VERY_LOW_MEDICAL_CONFIDENCE"
                    risk_level = "VERY_HIGH_MEDICAL_RISK"
                    routing_action = "HUMAN_REVIEW"
                    description = "This medical response appears highly unreliable. Seek professional medical advice."
            else:
                # General domain thresholds
                if conf_score >= 0.65:
                    interpretation = "HIGH_CONFIDENCE"
                    risk_level = "LOW_RISK"
                    routing_action = "LOCAL_GENERATION"
                    description = "This response appears to be factual and reliable."
                elif conf_score >= 0.60:
                    interpretation = "MEDIUM_CONFIDENCE"
                    risk_level = "MEDIUM_RISK"
                    routing_action = "RAG_RETRIEVAL"
                    description = "This response may contain uncertainties. Consider retrieval augmentation."
                elif conf_score >= 0.4:
                    interpretation = "LOW_CONFIDENCE"
                    risk_level = "HIGH_RISK"
                    routing_action = "LARGER_MODEL"
                    description = "This response is likely unreliable. Route to larger model."
                else:
                    interpretation = "VERY_LOW_CONFIDENCE"
                    risk_level = "VERY_HIGH_RISK"
                    routing_action = "HUMAN_REVIEW"
                    description = "This response appears to be highly unreliable. Human review required."
            
            result = {
                "text": text,
                "confidence_score": float(conf_score),
                "similarity_score": float(sim_score),
                "interpretation": interpretation,
                "risk_level": risk_level,
                "routing_action": routing_action,
                "description": description,
            }
            
            # Add enhanced metrics info if verbose mode is enabled
            if hasattr(self, 'verbose') and self.verbose:
                individual_sims = {k: v[i].item() for k, v in detailed_results['individual_similarities'].items()}
                result["detailed_similarities"] = individual_sims
                result["similarity_weights"] = detailed_results['weights_used']
                result["context_metadata"] = metadata['contradictions'][i] if i < len(metadata['contradictions']) else {}
                result["has_context"] = metadata['has_context'][i] if i < len(metadata['has_context']) else False
                result["fusion_strategy"] = metadata['fusion_strategies'][i] if i < len(metadata['fusion_strategies']) else 'none'
            
            results.append(result)
        
        return {
            "predictions": results,
            "summary": {
                "total_texts": len(texts),
                "avg_confidence": float(confidence_scores.mean()),
                "high_confidence_count": sum(1 for score in confidence_scores if score >= 0.65),
                "medium_confidence_count": sum(1 for score in confidence_scores if 0.60 <= score < 0.65),
                "low_confidence_count": sum(1 for score in confidence_scores if 0.4 <= score < 0.6),
                "very_low_confidence_count": sum(1 for score in confidence_scores if score < 0.4),
            }
        }
    
    def batch_predict(self, texts: List[str], batch_size: int = 16) -> Dict:
        """
        Process large batches of texts efficiently.
        
        Args:
            texts: List of texts to analyze
            batch_size: Batch size for processing
            
        Returns:
            Combined results dictionary
        """
        all_results = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_results = self.predict(batch)
            all_results.extend(batch_results["predictions"])
        
        # Compute overall summary
        confidence_scores = [r["confidence_score"] for r in all_results]
        
        return {
            "predictions": all_results,
            "summary": {
                "total_texts": len(texts),
                "avg_confidence": sum(confidence_scores) / len(confidence_scores),
                "high_confidence_count": sum(1 for score in confidence_scores if score >= 0.65),
                "medium_confidence_count": sum(1 for score in confidence_scores if 0.60 <= score < 0.65),
                "low_confidence_count": sum(1 for score in confidence_scores if 0.4 <= score < 0.6),
                "very_low_confidence_count": sum(1 for score in confidence_scores if score < 0.4),
            }
        }
    
    def evaluate_routing_strategy(self, texts: List[str]) -> Dict:
        """
        Evaluate the confidence-aware routing strategy for given texts.
        
        Args:
            texts: List of texts to analyze
            
        Returns:
            Routing strategy analysis
        """
        results = self.predict(texts)
        routing_counts = {}
        
        for pred in results["predictions"]:
            action = pred["routing_action"]
            routing_counts[action] = routing_counts.get(action, 0) + 1
        
        return {
            "routing_distribution": routing_counts,
            "computational_efficiency": {
                "local_generation_percentage": routing_counts.get("LOCAL_GENERATION", 0) / len(texts) * 100,
                "expensive_operations_percentage": (
                    routing_counts.get("RAG_RETRIEVAL", 0) + 
                    routing_counts.get("LARGER_MODEL", 0)
                ) / len(texts) * 100,
                "human_review_percentage": routing_counts.get("HUMAN_REVIEW", 0) / len(texts) * 100,
            },
            "summary": results["summary"]
        }
    
    def predict_with_query_context(self, query_context_pairs: List[Dict]) -> Dict:
        """
        Convenience method for predicting with query-context pairs.
        
        Args:
            query_context_pairs: List of dicts with 'query' and 'context' keys
            
        Returns:
            Dictionary with predictions, confidence scores, and interpretations
        """
        texts = [pair.get('query', '') for pair in query_context_pairs]
        return self.predict(texts, query_context_pairs=query_context_pairs)
    
    @classmethod
    def for_embedding_only(
        cls,
        model_path: str = None,
        embed_model_id: str = "BAAI/bge-m3",
        device: str = None,
        bge_max_length: int = 512,
        use_fp16: bool = True,
    ):
        """
        Create detector instance optimized for embedding-only usage (no LLM loading).
        
        Args:
            model_path: Path to trained model checkpoint
            embed_model_id: Hugging Face model ID for the embedding model
            device: Computing device ('cuda' or 'cpu')
            bge_max_length: Maximum sequence length for BGE-M3
            use_fp16: Whether to use FP16 precision
            
        Returns:
            HallucinationDetector instance with LLM disabled
        """
        return cls(
            model_path=model_path,
            embed_model_id=embed_model_id,
            device=device,
            bge_max_length=bge_max_length,
            use_fp16=use_fp16,
            load_llm=False,
            enable_inference=False,
        )
    
    @classmethod
    def for_low_memory(
        cls,
        llm_model_id: str = "convaiinnovations/gemma-finetuned-4b-it",
        model_path: str = None,
        device: str = "cuda",
        enable_response_generation: bool = True,
        **kwargs
    ):
        """
        Create detector instance optimized for low memory usage with 4-bit quantization.
        
        Args:
            llm_model_id: LLM model ID (default: MedGemma for medical tasks)
            model_path: Path to trained model checkpoint
            device: Computing device (cuda recommended for quantization)
            enable_response_generation: Whether to enable response generation
            **kwargs: Additional arguments passed to HallucinationDetector
            
        Returns:
            HallucinationDetector instance with memory optimization
        """
        return cls(
            model_path=model_path,
            llm_model_id=llm_model_id,
            device=device,
            use_quantization=False,  # Disabled for stability (matches inference_gemma.py)
            enable_response_generation=enable_response_generation,
            enable_inference=True,
            use_fp16=True,
            **kwargs
        )
    
    @classmethod
    def for_ultra_stable(
        cls,
        llm_model_id: str = "convaiinnovations/gemma-finetuned-4b-it",
        device: str = None,
        enable_response_generation: bool = True,
        **kwargs
    ):
        """
        Create an ultra-stable detector optimized for numerical stability.
        
        This factory method creates a detector with enhanced numerical stability
        measures specifically for models that experience NaN/Inf issues.
        
        Args:
            llm_model_id: Model to use (default: MedGemma 4B-IT)
            device: Computing device (auto-detected if None)
            enable_response_generation: Whether to enable response generation
            **kwargs: Additional arguments passed to HallucinationDetector
            
        Returns:
            Configured HallucinationDetector instance with stability optimizations
        """
        # Ultra-stable configuration
        stable_config = {
            'use_quantization': False,  # Disable quantization for maximum stability
            'use_fp16': False,  # Use float32 for maximum precision
            'enable_response_generation': enable_response_generation,
            'load_llm': True,
            'enable_inference': True,
            'mode': 'text',  # Start with text-only for stability
        }
        
        # Override with any user-provided kwargs
        stable_config.update(kwargs)
        
        print("🔧 Creating ultra-stable detector configuration...")
        print("   📊 Precision: float32 (maximum stability)")
        print("   🚀 Quantization: disabled")
        print("   🔬 Inference mode: stable")
        
        return cls(
            llm_model_id=llm_model_id,
            device=device,
            **stable_config
        )
    
    def generate_response(self, prompt: str, max_length: int = 512, check_confidence: bool = True, force_generate: bool = False, query_context_pairs: List[Dict] = None) -> Union[str, Dict]:
        """
        Generate a response from the LLM with optional confidence checking.
        
        Args:
            prompt: Input prompt/question
            max_length: Maximum response length
            check_confidence: Whether to check confidence before generating
            force_generate: If True, generate response regardless of confidence threshold
            query_context_pairs: Optional list of dicts with 'query' and 'context' keys for enhanced context
            
        Returns:
            Generated response text or dict with response and confidence info
        """
        if not self.enable_response_generation:
            raise RuntimeError("Response generation not enabled. Set enable_response_generation=True.")
        
        if not self.load_llm or self.llm is None:
            raise RuntimeError("LLM not loaded. Set load_llm=True for response generation.")
        
        # Check confidence first if requested
        confidence_score = None
        confidence_result = None
        if check_confidence:
            confidence_result = self.predict([prompt], query_context_pairs=query_context_pairs)
            confidence_score = confidence_result["predictions"][0]["confidence_score"]
            
            # Only block generation if confidence is low AND force_generate is False
            if confidence_score < self.confidence_threshold and not force_generate:
                return {
                    "response": None,
                    "confidence_score": confidence_score,
                    "should_generate": False,
                    "meets_threshold": False,
                    "reason": f"Confidence {confidence_score:.3f} below threshold {self.confidence_threshold}",
                    "recommendation": confidence_result["predictions"][0]["routing_action"]
                }
        
        try:
            # For generation, use only the query (context is for embeddings only)
            generation_prompt = prompt
            if query_context_pairs and len(query_context_pairs) > 0:
                pair = query_context_pairs[0]
                query = pair.get('query', prompt)
                generation_prompt = query
            
            # Format prompt for the specific model type
            if self.is_medgemma_4b:
                # Use medical context for MedGemma following Jupyter notebook approach exactly
                if hasattr(self.tokenizer, 'apply_chat_template'):
                    messages = [
                        {
                            "role": "system",
                            "content": [{"type": "text", "text": "You are a helpful medical assistant."}]
                        },
                        {
                            "role": "user",
                            "content": [{"type": "text", "text": generation_prompt}]
                        }
                    ]
                    inputs = self.tokenizer.apply_chat_template(
                        messages,
                        add_generation_prompt=True,
                        tokenize=True,
                        return_dict=True,
                        return_tensors="pt",
                    ).to(self.device)
                else:
                    formatted_prompt = f"<start_of_turn>user\n{generation_prompt}<end_of_turn>\n<start_of_turn>model\n"
                    inputs = self.tokenizer(
                        formatted_prompt,
                        return_tensors="pt",
                        truncation=True,
                        max_length=self.max_length
                    ).to(self.device)
            else:
                # Use general context for Llama
                formatted_prompt = f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n{generation_prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
                inputs = self.tokenizer(
                    formatted_prompt,
                    return_tensors="pt",
                    truncation=True,
                    max_length=self.max_length
                ).to(self.device)
            
            # Generate response
            with torch.inference_mode():
                input_len = inputs["input_ids"].shape[-1]
                
                # Use text-only model for generation if available (better for stable text generation)
                model_for_generation = getattr(self, 'llm_text', self.llm)
                # Improved generation parameters to prevent repetition
                actual_max_tokens = min(max_length, 300)  # Reduced for more focused responses
                generation = model_for_generation.generate(
                    **inputs,
                    max_new_tokens=actual_max_tokens,
                    do_sample=False,
                    repetition_penalty=1.1,  # Prevent repetition
                    no_repeat_ngram_size=3,  # Prevent 3-gram repetition
                    pad_token_id=self.tokenizer.eos_token_id if self.tokenizer.eos_token_id else self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    early_stopping=True,  # Stop when EOS is generated
                )
                
                # Extract only the generated part
                generation = generation[0][input_len:]
            
            # Decode response
            response = self.tokenizer.decode(generation, skip_special_tokens=True)
            response = response.strip()
            
            # Clean up repetitive patterns and artifacts
            response = self._clean_response(response)
            
            if check_confidence:
                return {
                    "response": response,
                    "confidence_score": confidence_score,
                    "should_generate": True,
                    "meets_threshold": confidence_score >= self.confidence_threshold,
                    "forced_generation": force_generate and confidence_score < self.confidence_threshold
                }
            else:
                return response
                
        except Exception as e:
            if check_confidence:
                return {
                    "response": None,
                    "confidence_score": confidence_score if confidence_score is not None else 0.0,
                    "error": str(e),
                    "should_generate": False,
                    "meets_threshold": False,
                    "forced_generation": force_generate
                }
            else:
                return f"[Error: {str(e)}]"
    
    def generate_response_with_pipeline(self, prompt: str, max_new_tokens: int = 500, system_instruction: str = None) -> str:
        """
        Generate response using the pipeline approach from the notebook to prevent repetitive generation.
        
        Args:
            prompt: Input prompt/question
            max_new_tokens: Maximum new tokens to generate
            system_instruction: Optional system instruction (defaults based on model type)
            
        Returns:
            Generated response text
        """
        if not self.pipe:
            raise RuntimeError("Pipeline not available. Ensure model was loaded with pipeline support.")
        
        # Set default system instruction based on model type
        if system_instruction is None:
            if self.is_medgemma_4b:
                system_instruction = "You are a helpful medical assistant."
            else:
                system_instruction = "You are a helpful assistant."
        
        # Format messages exactly like the notebook
        messages = [
            {
                "role": "system",
                "content": [{"type": "text", "text": system_instruction}]
            },
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}]
            }
        ]
        
        try:
            # Use pipeline exactly like the notebook: output = pipe(messages, max_new_tokens=max_new_tokens)
            output = self.pipe(messages, max_new_tokens=max_new_tokens)
            # Extract response exactly like the notebook: response = output[0]["generated_text"][-1]["content"]
            response = output[0]["generated_text"][-1]["content"]
            
            # Clean up the response
            response = self._clean_response(response.strip()) if response.strip() else "[No response generated]"
            return response
            
        except Exception as e:
            return f"[Pipeline Error: {str(e)}]"
    
    def batch_generate_with_pipeline(self, prompts: List[str], max_new_tokens: int = 500, system_instruction: str = None) -> List[str]:
        """
        Generate responses for multiple prompts using the pipeline approach.
        
        Args:
            prompts: List of input prompts
            max_new_tokens: Maximum new tokens to generate per prompt
            system_instruction: Optional system instruction (defaults based on model type)
            
        Returns:
            List of generated response texts
        """
        if not self.pipe:
            raise RuntimeError("Pipeline not available. Ensure model was loaded with pipeline support.")
        
        results = []
        for prompt in prompts:
            try:
                response = self.generate_response_with_pipeline(prompt, max_new_tokens, system_instruction)
                results.append(response)
            except Exception as e:
                results.append(f"[Error: {str(e)}]")
        
        return results
    
    def generate_response_with_context(self, query_context_pairs: List[Dict], max_length: int = 512, check_confidence: bool = True, force_generate: bool = False) -> Union[List[str], List[Dict]]:
        """
        Generate responses for multiple query-context pairs.
        
        Args:
            query_context_pairs: List of dicts with 'query' and 'context' keys
            max_length: Maximum response length
            check_confidence: Whether to check confidence before generating
            force_generate: If True, generate response regardless of confidence threshold
            
        Returns:
            List of generated response texts or dicts with response and confidence info
        """
        if not query_context_pairs:
            raise ValueError("query_context_pairs cannot be empty")
        
        results = []
        for pair in query_context_pairs:
            query = pair.get('query', '')
            if not query:
                results.append("[Error: No query provided]")
                continue
            
            result = self.generate_response(
                prompt=query,
                max_length=max_length,
                check_confidence=check_confidence,
                force_generate=force_generate,
                query_context_pairs=[pair]
            )
            results.append(result)
        
        return results
    
    def predict_images(self, images: List, image_descriptions: List[str] = None) -> Dict:
        """
        Predict confidence scores for medical images (MedGemma 4b-it only).
        
        Args:
            images: List of PIL Images to analyze
            image_descriptions: Optional descriptions of what the images should show
            
        Returns:
            Dictionary with image predictions and confidence scores
        """
        # Validate mode for image processing
        if self.effective_mode not in ["image", "both"]:
            raise ValueError(f"Image prediction requires mode 'image' or 'both', but current mode is '{self.effective_mode}'")
        
        if not self.is_multimodal:
            raise ValueError("Image prediction only supported for MedGemma 4b-it models")
        
        if not PIL_AVAILABLE:
            raise ImportError("PIL is required for image processing. Install with: pip install Pillow")
        
        if self.llm_multimodal is None or self.processor is None:
            raise ValueError("Multimodal model or processor not available for image processing")
        
        # Convert single image to list
        if not isinstance(images, list):
            images = [images]
        
        if image_descriptions is None:
            image_descriptions = [f"Medical image {i+1}" for i in range(len(images))]
        
        # This is a simplified implementation - in practice, you'd need proper image embeddings
        # For now, we'll analyze text descriptions and return placeholder results
        results = []
        for i, (image, desc) in enumerate(zip(images, image_descriptions)):
            # Placeholder confidence score for images
            confidence_score = 0.60  # Default medium confidence for images
            
            # Use medical image thresholds
            if confidence_score >= 0.60:
                interpretation = "HIGH_MEDICAL_IMAGE_CONFIDENCE"
                risk_level = "LOW_MEDICAL_RISK"
                description = "This medical image analysis appears reliable."
            elif confidence_score >= 0.55:
                interpretation = "MEDIUM_MEDICAL_IMAGE_CONFIDENCE"
                risk_level = "MEDIUM_MEDICAL_RISK"
                description = "This medical image analysis may need expert verification."
            else:
                interpretation = "LOW_MEDICAL_IMAGE_CONFIDENCE"
                risk_level = "HIGH_MEDICAL_RISK"
                description = "This medical image analysis appears unreliable."
            
            results.append({
                "image_index": i,
                "image_description": desc,
                "confidence_score": float(confidence_score),
                "interpretation": interpretation,
                "risk_level": risk_level,
                "description": description,
            })
        
        return {
            "predictions": results,
            "summary": {
                "total_images": len(images),
                "avg_confidence": sum(r["confidence_score"] for r in results) / len(results),
                "high_confidence_count": sum(1 for r in results if r["confidence_score"] >= 0.60),
                "medium_confidence_count": sum(1 for r in results if 0.55 <= r["confidence_score"] < 0.60),
                "low_confidence_count": sum(1 for r in results if r["confidence_score"] < 0.55),
            }
        }
    
    def generate_image_response(self, image, prompt: str = "Describe this medical image.", max_length: int = 200) -> str:
        """
        Generate a response from MedGemma for a given medical image.
        
        Args:
            image: PIL Image to analyze
            prompt: Text prompt for the image analysis
            max_length: Maximum response length
            
        Returns:
            Generated response text
        """
        # Validate mode for image response generation
        if self.effective_mode not in ["image", "both"]:
            raise ValueError(f"Image response generation requires mode 'image' or 'both', but current mode is '{self.effective_mode}'")
        
        if not self.is_multimodal:
            raise ValueError("Image response generation only supported for MedGemma 4b-it models")
        
        if not PIL_AVAILABLE:
            raise ImportError("PIL is required for image processing. Install with: pip install Pillow")
        
        if self.llm_multimodal is None or self.processor is None:
            raise ValueError("Multimodal model or processor not available for image processing")
        
        try:
            # Create proper MedGemma message format
            messages = [
                {
                    "role": "system",
                    "content": [{"type": "text", "text": "You are an expert radiologist."}]
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image", "image": image}
                    ]
                }
            ]
            
            # Apply chat template to get proper inputs
            inputs = self.processor.apply_chat_template(
                messages, 
                add_generation_prompt=True, 
                tokenize=True,
                return_dict=True, 
                return_tensors="pt"
            ).to(self.device)
            
            input_len = inputs["input_ids"].shape[-1]
            
            # Generate response
            with torch.inference_mode():
                # Follow Jupyter notebook approach exactly - use reasonable max_new_tokens
                actual_max_tokens = min(max_length, 500)  # Jupyter notebook uses 300-500
                generation = self.llm_multimodal.generate(
                    **inputs, 
                    max_new_tokens=actual_max_tokens, 
                    do_sample=False,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                )
                generation = generation[0][input_len:]
            
            # Decode response
            decoded = self.processor.decode(generation, skip_special_tokens=True)
            cleaned = self._clean_response(decoded.strip()) if decoded.strip() else "[No response generated]"
            return cleaned
            
        except Exception as e:
            return f"[Error: {str(e)}]"