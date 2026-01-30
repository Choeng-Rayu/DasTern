"""
Chat Assistant - Medical chatbot using MT5
"""
import logging
from pathlib import Path
from .model_loader import get_model

logger = logging.getLogger(__name__)

def load_prompt_template(template_name: str) -> str:
    """Load prompt template from file"""
    prompt_path = Path(__file__).parent / "prompts" / f"{template_name}.txt"
    
    if prompt_path.exists():
        return prompt_path.read_text(encoding="utf-8")
    else:
        logger.warning(f"Prompt template not found: {template_name}")
        return ""

def chat_with_assistant(message: str, language: str = "en", context: dict = None) -> dict:
    """
    Chat with medical assistant using MT5
    
    Args:
        message: User's message
        language: Language code (en, km, fr)
        context: Optional context (prescription data, etc.)
        
    Returns:
        dict with response and metadata
    """
    try:
        model, tokenizer, device = get_model()
        
        # Load appropriate prompt template
        system_prompt = load_prompt_template("chatbot")
        
        # Construct input with context
        if context:
            input_text = f"{system_prompt}\n\nContext: {context}\n\nUser: {message}\n\nAssistant:"
        else:
            input_text = f"{system_prompt}\n\nUser: {message}\n\nAssistant:"
        
        # Generate response
        inputs = tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        outputs = model.generate(
            **inputs,
            max_length=256,
            num_beams=4,
            temperature=0.7,
            do_sample=True,
            top_p=0.9
        )
        
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        return {
            "response": response,
            "language": language,
            "confidence": 0.85,  # Placeholder - implement proper scoring
            "metadata": {
                "model": "mt5-small",
                "service": "ai-llm-service"
            }
        }
        
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        raise
