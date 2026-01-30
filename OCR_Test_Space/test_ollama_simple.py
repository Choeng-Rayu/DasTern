#!/usr/bin/env python3
"""
Improved test script to verify Ollama can extract reminders with Khmer time words.
Uses explicit instructions to return English time values.
"""

import requests
import json
import time

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2:3b"
TIMEOUT = 120

def test_ollama_improved():
    """Test Ollama with improved prompt for reminder extraction."""
    
    # Improved prompt with explicit instructions
    prompt = """You are a medication reminder extraction system. 

Extract information from this prescription text and return ONLY valid JSON:

Input: "Butylscopolami 5 viên | ល្ងាច | យប់"

Khmer to English translations:
- ល្ងាច = evening
- យប់ = night
- viên = tablets

Extract and return JSON in this exact format:
{
  "medications": [
    {
      "name": "string",
      "dosage": "string", 
      "times": ["morning", "noon", "evening", "night"],
      "quantity": "string"
    }
  ]
}

IMPORTANT RULES:
1. ONLY include time values that appear in the input text
2. Times MUST be in English: "morning", "noon", "evening", or "night"
3. Do NOT use Khmer words in the times array
4. Return ONLY the JSON object, no markdown, no explanations

Based on the input "Butylscopolami 5 viên | ល្ងាច | យប់", the times array should be: ["evening", "night"]"""

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    }
    
    print(f"Testing Ollama at {OLLAMA_URL}")
    print(f"Model: {MODEL}")
    print(f"Input text: 'Butylscopolami 5 viên | ល្ងាច | យប់'")
    print(f"Expected times: ['evening', 'night']")
    print("-" * 60)
    
    start_time = time.time()
    
    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=TIMEOUT
        )
        
        elapsed = time.time() - start_time
        
        print(f"\nResponse time: {elapsed:.2f} seconds")
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            generated_text = result.get('response', '')
            
            print(f"\nRaw response from Ollama:")
            print("-" * 60)
            print(generated_text)
            print("-" * 60)
            
            # Try to parse as JSON
            try:
                # Extract JSON from response (might have markdown code blocks)
                json_str = generated_text.strip()
                if '```json' in json_str:
                    json_str = json_str.split('```json')[1].split('```')[0]
                elif '```' in json_str:
                    parts = json_str.split('```')
                    if len(parts) >= 2:
                        json_str = parts[1]
                
                parsed = json.loads(json_str.strip())
                print(f"\n✓ Valid JSON: YES")
                print(f"\nParsed JSON:")
                print(json.dumps(parsed, indent=2, ensure_ascii=False))
                
                # Check if times are correctly extracted
                if 'medications' in parsed and len(parsed['medications']) > 0:
                    med = parsed['medications'][0]
                    times = med.get('times', [])
                    print(f"\n✓ Times extracted: {times}")
                    
                    has_evening = 'evening' in [t.lower() for t in times]
                    has_night = 'night' in [t.lower() for t in times]
                    
                    print(f"✓ Has 'evening' (ល្ងាច): {has_evening}")
                    print(f"✓ Has 'night' (យប់): {has_night}")
                    
                    if has_evening and has_night:
                        print("\n✓✓✓ SUCCESS: Both Khmer time words correctly translated to English!")
                    else:
                        print("\n✗✗✗ FAILED: Missing expected English time values")
                        print(f"   Got: {times}")
                        print(f"   Expected: ['evening', 'night']")
                else:
                    print("\n✗ No medications found in response")
                    
            except json.JSONDecodeError as e:
                print(f"\n✗ Valid JSON: NO")
                print(f"Error: {e}")
                print("Response was not valid JSON")
        else:
            print(f"\n✗ Error: HTTP {response.status_code}")
            print(response.text)
            
    except requests.exceptions.Timeout:
        elapsed = time.time() - start_time
        print(f"\n✗ TIMEOUT after {elapsed:.2f} seconds")
        print("Ollama did not respond within the timeout period")
    except requests.exceptions.ConnectionError:
        print(f"\n✗ CONNECTION ERROR: Could not connect to Ollama at {OLLAMA_URL}")
        print("Make sure Ollama is running on port 11434")
    except Exception as e:
        print(f"\n✗ Error: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_ollama_improved()
