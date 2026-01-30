#!/usr/bin/env python3
"""
Quick test of the reminder extraction prompts
Tests directly with Ollama to verify prompt quality
"""
import json
import requests
import sys

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2:3b"  # Use 3B for faster testing

def test_simple_extraction():
    """Test with the simple Butylscopolamine example"""
    
    # System prompt
    system_prompt = """You are a medical prescription interpreter specializing in Cambodian prescriptions.

YOUR TASK:
1. Read RAW OCR JSON extracted from medical prescriptions in Cambodia
2. Ignore OCR noise, garbage text, and meaningless symbols
3. Detect medicine names, timing words, and quantities from prescription tables
4. Normalize Khmer, English, and French time words into English using the EXACT table below
5. Convert them into reminder times - EXTRACT ALL TIMES, not just one

MANDATORY TIME NORMALIZATION TABLE (you MUST use this exactly):

| Word         | Language  | Normalized  | Time   |
|--------------|-----------|-------------|--------|
| ព្រឹក        | Khmer     | morning     | 08:00  |
| ថ្ងៃ         | Khmer     | noon        | 12:00  |
| រសៀល        | Khmer     | noon        | 12:00  |
| ល្ងាច        | Khmer     | evening     | 18:00  |
| យប់         | Khmer     | night       | 21:00  |
| matin        | French    | morning     | 08:00  |
| midi         | French    | noon        | 12:00  |
| soir         | French    | evening     | 18:00  |
| nuit         | French    | night       | 21:00  |
| morning      | English   | morning     | 08:00  |
| noon         | English   | noon        | 12:00  |
| afternoon    | English   | noon        | 12:00  |
| evening      | English   | evening     | 18:00  |
| night        | English   | night       | 21:00  |

CRITICAL RULES:
1. If no time word is found in medication row, DO NOT generate reminder for that medication
2. The "|" (pipe) character means "AND" - extract ALL times separated by pipes
3. Example: "ល្ងាច | យប់" means BOTH evening AND night
4. Extract EVERY time word you find, don't skip any

OUTPUT FORMAT:
Return ONLY valid JSON. No explanation. No markdown. No code blocks."""

    # User prompt with example
    user_prompt = """RAW OCR DATA:
{"text": "Butylscopolami 5 viên | ល្ងាច | យប់"}

Extract medication reminders from the above prescription data.

EXAMPLE OF CORRECT OUTPUT:
Input: "Butylscopolamine 5 viên | ល្ងាច | យប់"
Output:
{
  "medications": [
    {
      "name": "Butylscopolamine",
      "times": ["evening", "night"],
      "times_24h": ["18:00", "21:00"],
      "repeat": "daily",
      "duration_days": null,
      "notes": "Original: ល្ងាច | យប់"
    }
  ]
}

NOW EXTRACT FROM THE RAW OCR DATA ABOVE AND RETURN JSON ONLY:"""

    # Combine prompts
    combined_prompt = f"<|system|>\n{system_prompt}\n<|user|>\n{user_prompt}\n<|assistant|>"
    
    payload = {
        "model": MODEL,
        "prompt": combined_prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,
            "top_p": 0.9,
            "num_ctx": 2048
        }
    }
    
    print("🧪 Testing Simple Reminder Extraction")
    print("=" * 60)
    print(f"Model: {MODEL}")
    print(f"Input: Butylscopolami 5 viên | ល្ងាច | យប់")
    print()
    
    try:
        print("⏳ Calling Ollama (this may take 10-30 seconds)...")
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            response_text = result.get("response", "").strip()
            
            print("✅ Ollama Response:")
            print("-" * 60)
            print(response_text)
            print("-" * 60)
            
            # Try to parse JSON
            try:
                # Clean the response - remove markdown if present
                text = response_text
                if "```json" in text:
                    import re
                    match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
                    if match:
                        text = match.group(1)
                elif "```" in text:
                    import re
                    match = re.search(r'```\s*(.*?)\s*```', text, re.DOTALL)
                    if match:
                        text = match.group(1)
                
                # Find JSON object
                import re
                json_match = re.search(r'\{[\s\S]*\}', text)
                if json_match:
                    text = json_match.group(0)
                
                data = json.loads(text)
                medications = data.get("medications", [])
                
                print()
                print(f"📊 Parsed {len(medications)} medication(s):")
                
                for i, med in enumerate(medications, 1):
                    print(f"\n  💊 Medication {i}: {med.get('name', 'Unknown')}")
                    print(f"     Times: {med.get('times', [])}")
                    print(f"     24h:   {med.get('times_24h', [])}")
                    
                    # Validate
                    times = med.get('times', [])
                    times_24h = med.get('times_24h', [])
                    
                    if times == ["evening", "night"] and times_24h == ["18:00", "21:00"]:
                        print("     ✅ PERFECT MATCH with expected output!")
                    elif "evening" in times and "night" in times:
                        print("     ⚠️  Partial match - has both times but order/format may differ")
                    elif len(times) == 1:
                        print(f"     ❌ Only extracted 1 time - expected 2 (evening AND night)")
                    else:
                        print(f"     ❌ Unexpected result")
                
                return True
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON Parse Error: {e}")
                print("Raw response was not valid JSON")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(response.text[:200])
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out (60s)")
        print("The model may be loading or the prompt is too complex")
        return False
    except Exception as e:
        print(f"💥 Error: {e}")
        return False

if __name__ == "__main__":
    success = test_simple_extraction()
    sys.exit(0 if success else 1)
