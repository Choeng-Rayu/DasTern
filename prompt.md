now help me to implement following phase below but i have implement it some code and build the structure file the goal is it scan presccription more accurate with advance image including complex some table, recongine symbole, units, mix of three language(english khmer and french) in one image. convert the raw data into clean medication and also generate the reminder.after done with that test it and it it error please check the database something it don't have the table for that so you can do the migration in the docker and restart database.  
PHASE 1 — OCR SERVICE (Document AI)

Goal of Phase 1

Convert prescription image → structured OCR output with layout, rules, and confidence
NO LLM, NO correction by AI yet

✅ Step 0: Environment Setup (Once)
1️⃣ Create virtual environment
cd ocr-service
python -m venv venv
source venv/bin/activate

2️⃣ requirements.txt (minimum)
fastapi
uvicorn
paddleocr
pillow
opencv-python
torch
transformers
pydantic
numpy


You can optimize later (CPU-only Torch if needed)

🧱 Step 1: Define the OCR Output Contract (schemas.py)

📍 app/schemas.py

Why

Everything depends on this structure

LLM will consume this later

What to define

Bounding box

Text

Confidence

Layout group

from pydantic import BaseModel
from typing import List

class BoundingBox(BaseModel):
    x1: int
    y1: int
    x2: int
    y2: int

class OCRBlock(BaseModel):
    text: str
    box: BoundingBox
    confidence: float
    block_type: str  # header | body | table | footer

class OCRResult(BaseModel):
    language: str
    blocks: List[OCRBlock]


✅ Do not skip this — this is your system backbone.

🔍 Step 2: OCR Engine (Text Extraction)

📍 app/ocr/paddle_engine.py

Responsibility

Image → raw text + bounding boxes

No rules, no cleanup

What to implement

Load PaddleOCR

Run OCR

Normalize coordinates

from paddleocr import PaddleOCR

ocr = PaddleOCR(lang="en")  # later restrict to kh, en, fr

def run_ocr(image_path):
    result = ocr.ocr(image_path, cls=True)
    blocks = []

    for line in result[0]:
        box, (text, conf) = line
        blocks.append({
            "text": text,
            "box": box,
            "confidence": conf
        })
    return blocks


📌 Important

Do NOT clean text here

Keep raw OCR output

🧠 Step 3: Layout Understanding (LayoutLMv3)

📍 app/layout/layoutlmv3.py

Responsibility

Understand document structure

Classify blocks (header, medicine list, dosage, notes)

What it consumes

OCR blocks + bounding boxes

What it outputs

Block classification

def classify_layout(ocr_blocks):
    """
    Input: OCR blocks with bbox
    Output: Same blocks with block_type
    """
    # Placeholder logic (replace with LayoutLMv3 inference)
    for block in ocr_blocks:
        block["block_type"] = "body"
    return ocr_blocks


📌 Key rule

LayoutLMv3 NEVER does OCR
It only understands structure

🧩 Step 4: Grouping & Key-Value Logic

📍 app/layout/grouping.py
📍 app/layout/key_value.py

Grouping

Merge nearby blocks

Reconstruct medicine rows

def group_blocks(blocks):
    # group by Y proximity
    return blocks

Key-value

Detect patterns like:

Drug → Dosage

Frequency → Duration

def extract_key_values(blocks):
    return {
        "medicine": [],
        "dosage": []
    }


📌 This is rule-based, not AI.

🧹 Step 5: Rule-Based Cleanup (Language-Specific)

📍 app/rules/medical_terms.py
📍 app/rules/khmer_fix.py

Responsibility

Fix OCR mistakes

Normalize spelling

DO NOT hallucinate

Example:

COMMON_FIXES = {
    "paracatamol": "paracetamol"
}

def fix_terms(text):
    for k, v in COMMON_FIXES.items():
        text = text.replace(k, v)
    return text

📊 Step 6: Confidence Scoring

📍 app/confidence.py

Why

Medical system MUST expose uncertainty

def calculate_confidence(blocks):
    return sum(b["confidence"] for b in blocks) / len(blocks)

🔁 Step 7: Pipeline Orchestration

📍 app/pipeline.py

This is the heart of OCR service

from ocr.paddle_engine import run_ocr
from layout.layoutlmv3 import classify_layout
from rules.khmer_fix import fix_terms

def process_image(image_path):
    blocks = run_ocr(image_path)
    blocks = classify_layout(blocks)

    for b in blocks:
        b["text"] = fix_terms(b["text"])

    return blocks

🚪 Step 8: API Entry

📍 app/main.py

from fastapi import FastAPI, UploadFile
from pipeline import process_image

app = FastAPI()

@app.post("/ocr")
async def ocr(file: UploadFile):
    image_path = f"/tmp/{file.filename}"
    with open(image_path, "wb") as f:
        f.write(await file.read())

    blocks = process_image(image_path)
    return {"blocks": blocks}


✅ Phase 1 DONE
You now have Document AI, not “just OCR”.

🔷 PHASE 2 — LLM SERVICE (LLaMA 8B / Ollama)

Goal

Structured reasoning over OCR output
Two roles: Prescription Enhancer + Chatbot

🧠 Step 1: Model Loader (Core)

📍 app/core/model_loader.py

Responsibility

Load quantized LLaMA once

Reuse across requests

from llama_cpp import Llama

llm = Llama(
    model_path="models/llama/weights.gguf",
    n_ctx=4096,
    n_threads=8
)

🔁 Step 2: Unified Generation Logic

📍 app/core/generation.py

from core.model_loader import llm

def generate(prompt, max_tokens=512):
    output = llm(prompt, max_tokens=max_tokens)
    return output["choices"][0]["text"]


📌 Never call model directly elsewhere

🧾 Step 3: Prescription Enhancer

📍 features/prescription/enhancer.py

Input

OCR structured JSON

Output

Clean, normalized prescription

from core.generation import generate

def enhance_prescription(ocr_json, prompt):
    return generate(prompt + str(ocr_json))

🧑‍⚕️ Step 4: Safety & Validation

📍 features/prescription/validator.py

def validate(text):
    forbidden = ["diagnose", "cure"]
    for word in forbidden:
        if word in text.lower():
            raise ValueError("Medical violation")

💬 Step 5: Chatbot Logic

📍 features/chat/assistant.py

def chat(message, memory):
    prompt = memory + "\nUser:" + message
    return generate(prompt)

🛡️ Step 6: Language & Safety Guards

📍 safety/language.py

ALLOWED = ["kh", "en", "fr"]


📍 safety/medical.py

No diagnosis

No drug advice

🚪 Step 7: API Entry

📍 app/main.py

from fastapi import FastAPI
from features.prescription.enhancer import enhance_prescription

app = FastAPI()

@app.post("/enhance")
def enhance(data: dict):
    return enhance_prescription(data)

✅ FINAL RESULT

You now have:

✔ Real Document AI (OCR + Layout)
✔ Real LLM service (not tied to OCR)
✔ Clean separation of responsibility
✔ Safe medical constraints
✔ Scalable future chatbot