"""
Model Loader - Load and cache MT5 model
"""
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Global model cache
_model = None
_tokenizer = None
_device = None

def load_mt5_model():
    """
    Load MT5 model and tokenizer into memory
    Called once on service startup
    """
    global _model, _tokenizer, _device
    
    if _model is not None:
        logger.info("Model already loaded")
        return _model, _tokenizer, _device
    
    try:
        # Determine device
        _device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {_device}")
        
        # Model path - adjust as needed
        base_path = Path(__file__).parent.parent / "models" / "mt5-small"
        tokenizer_path = base_path / "tokenizer"
        model_path = base_path / "model"

        tokenizer_files = [
            tokenizer_path / "spiece.model",
            tokenizer_path / "tokenizer.json",
            tokenizer_path / "tokenizer.model"
        ]
        model_files = [
            model_path / "pytorch_model.bin",
            model_path / "model.safetensors",
            model_path / "config.json"
        ]
        has_tokenizer = any(p.exists() for p in tokenizer_files)
        has_model = any(p.exists() for p in model_files)

        if has_tokenizer and has_model:
            logger.info(f"Loading tokenizer from: {tokenizer_path}")
            logger.info(f"Loading model from: {model_path}")
            _tokenizer = AutoTokenizer.from_pretrained(str(tokenizer_path), use_fast=False)
            _model = AutoModelForSeq2SeqLM.from_pretrained(str(model_path))
        elif base_path.exists() and (base_path / "config.json").exists():
            logger.info(f"Loading model from: {base_path}")
            _tokenizer = AutoTokenizer.from_pretrained(str(base_path), use_fast=False)
            _model = AutoModelForSeq2SeqLM.from_pretrained(str(base_path))
        else:
            # Fallback to downloading from HuggingFace
            logger.warning(f"Model not found at {base_path}, downloading from HuggingFace...")
            _tokenizer = AutoTokenizer.from_pretrained("google/mt5-small", use_fast=False)
            _model = AutoModelForSeq2SeqLM.from_pretrained("google/mt5-small")
            # Save locally so future runs do not re-download
            tokenizer_path.mkdir(parents=True, exist_ok=True)
            model_path.mkdir(parents=True, exist_ok=True)
            _tokenizer.save_pretrained(str(tokenizer_path))
            _model.save_pretrained(str(model_path))
        
        _model.to(_device)
        _model.eval()  # Set to evaluation mode
        
        logger.info("Model loaded successfully!")
        return _model, _tokenizer, _device
        
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}")
        raise

def get_model():
    """Get the loaded model, tokenizer, and device"""
    global _model, _tokenizer, _device
    
    if _model is None:
        load_mt5_model()
    
    return _model, _tokenizer, _device
