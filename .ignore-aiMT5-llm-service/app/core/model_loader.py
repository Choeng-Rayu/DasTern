"""
Model Loader - Core LLM Service
Responsibility: Load quantized LLaMA once, reuse across requests
"""

# TODO: from llama_cpp import Llama

# Global model instance
llm = None

def load_model(model_path: str = "models/llama/weights.gguf"):
    """
    Load LLaMA model once at startup
    
    Args:
        model_path: Path to GGUF quantized model
        
    Returns:
        Loaded model instance
    """
    global llm
    
    # TODO: Load model with llama-cpp-python
    # llm = Llama(
    #     model_path=model_path,
    #     n_ctx=4096,
    #     n_threads=8,
    #     n_gpu_layers=0  # Adjust based on GPU availability
    # )
    
    # TODO: Return model instance
    pass


def get_model():
    """
    Get loaded model instance
    
    Returns:
        LLM model instance
    """
    global llm
    if llm is None:
        raise RuntimeError("Model not loaded. Call load_model() first.")
    return llm
