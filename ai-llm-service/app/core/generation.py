"""
<<<<<<< HEAD
Generation Module
Unified generation logic for all LLM tasks
"""

import logging
import requests
from typing import Optional, Dict, Any, List

from .model_loader import get_ollama_host, get_model_name, is_model_ready

logger = logging.getLogger(__name__)

# Generation defaults
DEFAULT_TEMPERATURE = 0.3  # Low temperature for medical accuracy
DEFAULT_MAX_TOKENS = 1024
DEFAULT_TIMEOUT = 60  # seconds
=======
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
>>>>>>> 479e2f047f47a189e6575eb2c4ec1dee4038fac6


def generate(
    prompt: str,
<<<<<<< HEAD
    system_prompt: str = None,
    temperature: float = DEFAULT_TEMPERATURE,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    timeout: int = DEFAULT_TIMEOUT
) -> Optional[str]:
    """
    Generate text using the LLM.
    
    Args:
        prompt: User prompt
        system_prompt: System instructions
        temperature: Sampling temperature (0.0 to 1.0)
        max_tokens: Maximum tokens to generate
        timeout: Request timeout in seconds
        
    Returns:
        Generated text or None if failed
    """
    if not is_model_ready():
        logger.warning("Model not ready, attempting generation anyway")
    
    try:
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        response = requests.post(
            f"{get_ollama_host()}/api/chat",
            json={
                "model": get_model_name(),
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            },
            timeout=timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result.get("message", {}).get("content", "")
            logger.debug(f"Generated {len(content)} characters")
            return content
        else:
            logger.error(f"Generation failed: {response.status_code} - {response.text}")
            return None
            
    except requests.Timeout:
        logger.error(f"Generation timed out after {timeout}s")
        return None
    except Exception as e:
        logger.error(f"Generation error: {e}")
        return None
=======
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
>>>>>>> 479e2f047f47a189e6575eb2c4ec1dee4038fac6


def generate_json(
    prompt: str,
<<<<<<< HEAD
    system_prompt: str = None,
    temperature: float = 0.1,  # Even lower for JSON
    timeout: int = DEFAULT_TIMEOUT
) -> Optional[Dict[str, Any]]:
    """
    Generate and parse JSON response from LLM.
    
    Args:
        prompt: User prompt
        system_prompt: System instructions (should mention JSON output)
        temperature: Sampling temperature
        timeout: Request timeout
        
    Returns:
        Parsed JSON dict or None if failed
    """
    import json
    
    # Add JSON instruction to system prompt
    json_system = (system_prompt or "") + "\nYou MUST respond with valid JSON only. No explanation."
    
    result = generate(
        prompt=prompt,
        system_prompt=json_system,
        temperature=temperature,
        timeout=timeout
    )
    
    if not result:
        return None
    
    try:
        # Try to extract JSON from response
        result = result.strip()
        
        # Handle markdown code blocks
        if result.startswith("```json"):
            result = result[7:]
        if result.startswith("```"):
            result = result[3:]
        if result.endswith("```"):
            result = result[:-3]
        
        return json.loads(result.strip())
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON: {e}")
        logger.debug(f"Raw response: {result}")
        return None


def generate_with_context(
    prompt: str,
    context: List[Dict[str, str]],
    system_prompt: str = None,
    temperature: float = DEFAULT_TEMPERATURE
) -> Optional[str]:
    """
    Generate with conversation context.
    
    Args:
        prompt: Current user prompt
        context: List of previous messages [{"role": "user/assistant", "content": "..."}]
        system_prompt: System instructions
        temperature: Sampling temperature
        
    Returns:
        Generated text or None
    """
    try:
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add context
        messages.extend(context)
        
        # Add current prompt
        messages.append({"role": "user", "content": prompt})
        
        response = requests.post(
            f"{get_ollama_host()}/api/chat",
            json={
                "model": get_model_name(),
                "messages": messages,
                "stream": False,
                "options": {"temperature": temperature}
            },
            timeout=DEFAULT_TIMEOUT
        )
        
        if response.status_code == 200:
            return response.json().get("message", {}).get("content", "")
        return None
        
    except Exception as e:
        logger.error(f"Context generation error: {e}")
        return None

=======
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
>>>>>>> 479e2f047f47a189e6575eb2c4ec1dee4038fac6
