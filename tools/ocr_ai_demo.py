"""Demo: OCR Service -> AI LLM Service (text correction)

Usage: run with a Python that has access to stdlib only.
Edit IMAGE_PATH if needed.
"""
from __future__ import annotations

import base64
import json
import urllib.request
from pathlib import Path

OCR_URL = "http://localhost:8000/ocr/base64"
AI_URL = "http://localhost:8001/api/v1/correct"
IMAGE_PATH = Path(__file__).parent.parent / "ocr-service" / "images_for_Test_yu" / "image2.png"


def post_json(url: str, payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> None:
    if not IMAGE_PATH.exists():
        raise FileNotFoundError(f"Image not found: {IMAGE_PATH}")

    image_b64 = base64.b64encode(IMAGE_PATH.read_bytes()).decode("utf-8")

    ocr_payload = {
        "image_base64": image_b64,
        "languages": ["eng", "khm", "fra"],
        "lenient_quality": True
    }

    ocr_result = post_json(OCR_URL, ocr_payload)
    raw_text = ocr_result.get("full_text", "")

    ai_payload = {
        "raw_text": raw_text,
        "language": "en",
        "context": {"source": "ocr-service"}
    }

    ai_result = post_json(AI_URL, ai_payload)

    print("=== OCR Raw Text ===")
    print(raw_text)
    print("\n=== AI Corrected Text ===")
    print(ai_result.get("corrected_text", ""))


if __name__ == "__main__":
    main()
