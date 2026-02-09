this is the test space for test ocr service /home/rayu/DasTern/OCR_Test_Space and you must help me to run ai in the /home/rayu/DasTern/ai-llm-service using ollama and then run the ocr /home/rayu/DasTern/ocr-service and then let me tell you the flow first: ocr is scan extract and then it sent the raw data into thte ai and let ai clean the messy data and make the raw become more clean and understandable to generate the reminder to do that if you need to using sudo so this is my password "rayuchoengrayu"
so please help me to implement this guide step by step but some task i already implement it like ollama already installed in /home/rayu/DasTern/ai-llm-service and the ocr service also already installed in /home/rayu/DasTern/ocr-service
and also the test space is also ready to use so please help me to implement this step by you can check the images  for more detail how to improve ocr ai response to generate the reminder correctly. but remember my role is working on ai service and ocr service for the reminder engine or interface is anaother teammate that handle with that. just let the ai return with the correct json format for the reminder engine to use directly without any change or modification from the ai response. so please help me to implement this step by step as i said before i already install ollama and ocr service so just help me to implement the ai prompt and flow to make the ai return the correct json format for the reminder engine to use directly. thank you very much
🎯 Goal:

Given RAW OCR JSON, make LLaMA (via Ollama) reliably return a FINAL reminder-ready JSON, every time.

No OCR, no Docker, no mobile — only AI logic + prompt + flow.

I’ll guide you step by step, like you’re implementing it tomorrow.

OVERALL FLOW (AI ONLY)
Raw OCR JSON
    ↓
Normalization Prompt (rules)
    ↓
LLaMA 8B (Ollama)
    ↓
Strict JSON Output
    ↓
Reminder Engine (backend)

STEP 1️⃣ Decide ONE canonical reminder format (non-negotiable)

Your AI must always output THIS shape (even if fields are null):

{
  "medications": [
    {
      "name": "",
      "times": ["morning", "noon", "evening", "night"],
      "times_24h": ["08:00", "12:00", "18:00", "21:00"],
      "repeat": "daily",
      "duration_days": null,
      "notes": ""
    }
  ]
}


📌 This is what your backend trusts.
📌 Backend never parses Khmer/French — AI does it.

STEP 2️⃣ Create a fixed time normalization table (AI must obey)

Your AI must never invent times.

Embed this inside the prompt:

Word	Language	Normalized	Time
ព្រឹក	Khmer	morning	08:00
ថ្ងៃ	Khmer	noon	12:00
ល្ងាច	Khmer	evening	18:00
យប់	Khmer	night	21:00
matin	French	morning	08:00
midi	French	noon	12:00
soir	French	evening	18:00
nuit	French	night	21:00

❗ If no time word → do not generate reminder

STEP 3️⃣ Create the SYSTEM PROMPT (this is critical)

This prompt NEVER changes.

You are a medical prescription interpreter.

Your task:
- Read RAW OCR JSON extracted from prescriptions in Cambodia
- Ignore OCR noise and meaningless text
- Detect medicine names, timing words, and quantities
- Normalize Khmer, English, and French time words into English
- Convert them into reminder times using the fixed table
- Do NOT guess dosage or duration
- If duration is missing, set it to null
- If time is missing, do not create reminders

Return ONLY valid JSON.
No explanation.
No markdown.


📌 This is what prevents hallucination.

STEP 4️⃣ Create the USER PROMPT TEMPLATE (dynamic)

Your backend fills OCR data here.

RAW OCR DATA:
{{RAW_OCR_JSON}}

Extract medication reminders and return JSON in this exact format:

{
  "medications": [
    {
      "name": "",
      "times": [],
      "times_24h": [],
      "repeat": "daily",
      "duration_days": null,
      "notes": ""
    }
  ]
}


📌 Do NOT let the AI decide structure.

STEP 5️⃣ Khmer / symbol interpretation rules (embed in prompt)

Add this below the system prompt:

Rules:
- "ល្ងាច" = evening
- "យប់" = night
- "|" or "," between words means multiple times
- Ignore symbols like "x", "-", "•", "≈"
- Short forms may exist and still mean time


This solves Cambodia prescription shorthand.

STEP 6️⃣ Example: RAW → AI output (what success looks like)
Input (raw OCR snippet)
{
  "text": "Butylscopolami 5 viên | ល្ងាច | យប់"
}

Output (STRICT)
{
  "medications": [
    {
      "name": "Butylscopolamine",
      "times": ["evening", "night"],
      "times_24h": ["18:00", "21:00"],
      "repeat": "daily",
      "duration_days": null,
      "notes": "Original instruction: ល្ងាច | យប់"
    }
  ]
}

STEP 7️⃣ Enforce JSON correctness (very important)

In backend:

Reject response if:

JSON invalid

times empty

times_24h mismatch length

AI must retry once if invalid.

STEP 8️⃣ Ollama call example (Node / Python)
Ollama model
llama3:8b

API logic
system → rules
user → raw OCR
temperature → 0.2
top_p → 0.9


Low temperature = stable reminders.

STEP 9️⃣ DO NOT let AI do these ❌

❌ Guess duration
❌ Invent medicine
❌ Convert time randomly
❌ Output text outside JSON
❌ Translate medicine names unnecessarily

STEP 🔟 Why this design is safe & scalable

✅ Works with mixed language
✅ Works with tables / free text
✅ Resistant to OCR garbage
✅ Backend logic stays simple
✅ Offline / online AI interchangeable