"""
AI Generation Functions using Ollama
"""
import os
import json
import logging
import requests
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
# Use llama3.2:3b for faster CPU inference (2x faster than 8b, runs on all specs)
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")


def generate(
    prompt: str,
    system_prompt: Optional[str] = None,
    model: str = None,
    temperature: float = 0.3,
    max_tokens: int = 1000,
    **kwargs  # Accept other parameters and ignore them
) -> str:
    """
    Generate text response from LLaMA via Ollama (optimized for 3B model)
    
    Args:
        prompt: User prompt/question
        system_prompt: System instructions (optional)
        model: Model name (defaults to llama3.2:3b)
        temperature: Sampling temperature (0.0-1.0, lower = more deterministic)
        max_tokens: Maximum tokens to generate (reduced for faster 3B inference)
    
    Returns:
        Generated text response
    """
    if model is None:
        model = DEFAULT_MODEL
    
    try:
        url = f"{OLLAMA_HOST}/api/generate"
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                "top_k": 40,
                "top_p": 0.9
            }
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        logger.info(f"Generating response with model: {model} (temp={temperature})")
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        
        result = response.json()
        return result.get("response", "")
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Ollama generation error: {e}")
        raise RuntimeError(f"Failed to generate response: {e}")


def generate_json(
    prompt: str,
    system_prompt: Optional[str] = None,
    model: str = None,
    examples: Optional[list] = None,
    temperature: float = 0.1,
    max_tokens: int = 1000,
    **kwargs  # Accept other parameters and ignore them
) -> Dict[str, Any]:
    """
    Generate structured JSON response from LLaMA via Ollama
    
    Args:
        prompt: User prompt/question
        system_prompt: System instructions
        model: Model name (defaults to llama3.2:3b)
        examples: Few-shot learning examples (optional)
        temperature: Sampling temperature (0.0-1.0, lower = more deterministic)
        max_tokens: Maximum tokens to generate
    
    Returns:
        Parsed JSON dict
    """
    if model is None:
        model = DEFAULT_MODEL
    
    # Build full prompt with examples if provided
    full_prompt = ""
    
    if examples:
        full_prompt += "Examples:\n\n"
        for i, example in enumerate(examples[:5], 1):  # Limit to 5 examples
            if isinstance(example, dict):
                if "user" in example and "assistant" in example:
                    full_prompt += f"{i}. Input: {example['user']} → Output: {example['assistant']}\n"
        full_prompt += "---\n\n"
    
    full_prompt += f"Process: {prompt}\nReturn ONLY valid JSON."
    
    try:
        url = f"{OLLAMA_HOST}/api/generate"
        
        payload = {
            "model": model,
            "prompt": full_prompt,
            "stream": False,
            "format": "json",  # Tell Ollama to return JSON
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                "top_k": 40,
                "top_p": 0.9
            }
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        logger.info(f"Generating JSON with model: {model} (temp={temperature})")
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        
        result = response.json()
        response_text = result.get("response", "")
        
        # Parse JSON from response
        try:
            parsed = json.loads(response_text)
            return parsed
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {response_text}")
            # Try to extract JSON from markdown code blocks
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0].strip()
                return json.loads(json_str)
            elif "```" in response_text:
                json_str = response_text.split("```")[1].split("```")[0].strip()
                return json.loads(json_str)
            else:
                raise ValueError(f"Invalid JSON response: {e}")
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Ollama generation error: {e}")
        raise RuntimeError(f"Failed to generate JSON: {e}")
