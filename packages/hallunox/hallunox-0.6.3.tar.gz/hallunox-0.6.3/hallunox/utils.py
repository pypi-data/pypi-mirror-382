"""
Utility functions for HalluNox package.

This module provides helper functions for model downloading, logging setup,
and other common operations.
"""

import os
import sys
import logging
import urllib.request
from pathlib import Path
from typing import Optional


def setup_logging(level: str = "INFO") -> logging.Logger:
    """
    Set up enhanced logging configuration.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        Configured logger instance
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )
    logger = logging.getLogger("hallunox")
    return logger


def download_medgemma_model(
    model_name: str,
    save_dir: Optional[str] = None,
    filename: str = "best_model_med.pt"
) -> str:
    """
    Download MedGemma pre-trained model for 4b-it models.
    
    Args:
        model_name: Model name to check for 4b-it
        save_dir: Directory to save the model. If None, uses ~/.hallunox/models/
        filename: Name of the saved file
        
    Returns:
        Path to the downloaded model file
    """
    if "4b-it" not in model_name:
        raise ValueError(f"MedGemma model download only supported for 4b-it models, got: {model_name}")
    
    url = "https://storage.googleapis.com/courseai/best_model_med.pt"
    return download_model(url, save_dir, filename)


def download_model(
    url: str = "https://storage.googleapis.com/courseai/best_model_hl.pt",
    save_dir: Optional[str] = None,
    filename: str = "best_model.pt"
) -> str:
    """
    Download pre-trained model from the specified URL.
    
    Args:
        url: URL to download the model from
        save_dir: Directory to save the model. If None, uses ~/.hallunox/models/
        filename: Name of the saved file
        
    Returns:
        Path to the downloaded model file
    """
    logger = setup_logging()
    
    if save_dir is None:
        save_dir = os.path.expanduser("~/.hallunox/models")
    
    os.makedirs(save_dir, exist_ok=True)
    model_path = os.path.join(save_dir, filename)
    
    if os.path.exists(model_path):
        logger.info(f"✅ Model already exists at {model_path}")
        return model_path
    
    logger.info(f"📥 Downloading pre-trained model from {url}")
    logger.info(f"💾 Saving to {model_path}")
    
    try:
        # Download with progress indication
        def progress_hook(block_num, block_size, total_size):
            if total_size > 0:
                percent = min(100, (block_num * block_size / total_size) * 100)
                print(f"\rDownloading: {percent:.1f}%", end='', flush=True)
        
        urllib.request.urlretrieve(url, model_path, progress_hook)
        print()  # New line after progress
        
        # Verify download
        if os.path.exists(model_path) and os.path.getsize(model_path) > 0:
            logger.info(f"✅ Model downloaded successfully to {model_path}")
            size_mb = os.path.getsize(model_path) / (1024 * 1024)
            logger.info(f"📊 Model size: {size_mb:.1f} MB")
            return model_path
        else:
            raise RuntimeError("Downloaded file is empty or corrupted")
            
    except Exception as e:
        logger.error(f"❌ Failed to download model: {e}")
        if os.path.exists(model_path):
            os.remove(model_path)
        raise


def check_gpu_availability() -> dict:
    """
    Check GPU availability and CUDA compatibility.
    
    Returns:
        Dictionary with GPU information
    """
    import torch
    
    info = {
        "cuda_available": torch.cuda.is_available(),
        "cuda_version": None,
        "gpu_count": 0,
        "gpu_names": [],
        "recommended_device": "cpu"
    }
    
    if torch.cuda.is_available():
        info["cuda_version"] = torch.version.cuda
        info["gpu_count"] = torch.cuda.device_count()
        info["gpu_names"] = [torch.cuda.get_device_name(i) for i in range(info["gpu_count"])]
        info["recommended_device"] = "cuda"
    
    return info


def validate_model_requirements() -> bool:
    """
    Validate that all required dependencies are available.
    
    Returns:
        True if all requirements are met, False otherwise
    """
    logger = setup_logging()
    requirements_met = True
    
    # Check PyTorch
    try:
        import torch
        logger.info(f"✅ PyTorch: {torch.__version__}")
    except ImportError:
        logger.error("❌ PyTorch not available")
        requirements_met = False
    
    # Check Transformers
    try:
        import transformers
        logger.info(f"✅ Transformers: {transformers.__version__}")
    except ImportError:
        logger.error("❌ Transformers not available")
        requirements_met = False
    
    # Check FlagEmbedding
    try:
        from FlagEmbedding import BGEM3FlagModel
        logger.info("✅ FlagEmbedding: Available")
    except ImportError:
        logger.error("❌ FlagEmbedding not available. Install with: pip install -U FlagEmbedding")
        requirements_met = False
    
    # Check GPU
    gpu_info = check_gpu_availability()
    if gpu_info["cuda_available"]:
        logger.info(f"✅ CUDA: {gpu_info['cuda_version']} ({gpu_info['gpu_count']} GPU(s))")
        for i, name in enumerate(gpu_info["gpu_names"]):
            logger.info(f"   GPU {i}: {name}")
    else:
        logger.warning("⚠️ CUDA not available. CPU inference will be slower.")
    
    return requirements_met


def create_example_config() -> dict:
    """
    Create an example configuration for training or inference.
    
    Returns:
        Example configuration dictionary
    """
    return {
        "model": {
            "llm_model_id": "unsloth/Llama-3.2-3B-Instruct",
            "embed_model_id": "BAAI/bge-m3",
            "max_length": 512,
            "bge_max_length": 512,
            "use_fp16": True,
        },
        "training": {
            "batch_size": 8,
            "learning_rate": 5e-4,
            "max_epochs": 6,
            "warmup_steps": 300,
            "weight_decay": 1e-4,
            "gradient_accumulation_steps": 4,
            "max_grad_norm": 1.0,
        },
        "data": {
            "val_split": 0.15,
            "max_samples_per_dataset": 3000,
            "use_truthfulqa": True,
            "use_halueval": True,
            "use_fever": True,
            "use_xsum_factuality": True,
            "use_squad_v2": True,
            "use_natural_questions": True,
        },
        "confidence_thresholds": {
            "high_confidence": 0.65,
            "medium_confidence": 0.60,
            "low_confidence": 0.4,
        }
    }


def get_model_info(model_path: str) -> dict:
    """
    Get information about a trained model checkpoint.
    
    Args:
        model_path: Path to the model checkpoint
        
    Returns:
        Model information dictionary
    """
    import torch
    
    try:
        checkpoint = torch.load(model_path, map_location="cpu", weights_only=False)
        
        info = {
            "model_path": model_path,
            "config": checkpoint.get("config", {}),
            "epoch": checkpoint.get("epoch", "unknown"),
            "best_val_loss": checkpoint.get("best_val_loss", "unknown"),
            "metrics": checkpoint.get("metrics", {}),
        }
        
        # Add file size
        if os.path.exists(model_path):
            size_mb = os.path.getsize(model_path) / (1024 * 1024)
            info["file_size_mb"] = round(size_mb, 1)
        
        return info
        
    except Exception as e:
        return {"error": str(e), "model_path": model_path}


def format_confidence_report(results: dict) -> str:
    """
    Format prediction results into a human-readable report.
    
    Args:
        results: Results dictionary from HallucinationDetector.predict()
        
    Returns:
        Formatted report string
    """
    summary = results["summary"]
    predictions = results["predictions"]
    
    report = []
    report.append("🔍 HALLUCINATION DETECTION REPORT")
    report.append("=" * 50)
    report.append(f"Total Texts Analyzed: {summary['total_texts']}")
    report.append(f"Average Confidence: {summary['avg_confidence']:.4f}")
    report.append("")
    
    report.append("📊 CONFIDENCE DISTRIBUTION:")
    report.append(f"   High Confidence (≥0.65): {summary.get('high_confidence_count', 0)}")
    report.append(f"   Medium Confidence (0.60-0.65): {summary.get('medium_confidence_count', 0)}")
    report.append(f"   Low Confidence (0.4-0.60): {summary.get('low_confidence_count', 0)}")
    report.append(f"   Very Low Confidence (<0.4): {summary.get('very_low_confidence_count', 0)}")
    report.append("")
    
    report.append("📋 DETAILED RESULTS:")
    for i, pred in enumerate(predictions[:10]):  # Show first 10
        text_preview = pred["text"][:80] + ("..." if len(pred["text"]) > 80 else "")
        report.append(f"{i+1}. {text_preview}")
        report.append(f"   Confidence: {pred['confidence_score']:.4f} ({pred['interpretation']})")
        report.append(f"   Risk Level: {pred['risk_level']}")
        report.append(f"   Action: {pred.get('routing_action', 'N/A')}")
        report.append("")
    
    if len(predictions) > 10:
        report.append(f"... and {len(predictions) - 10} more results")
    
    return "\n".join(report)