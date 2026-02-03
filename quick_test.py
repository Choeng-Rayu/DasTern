import requests
import sys

print("Testing services...")

# Test OCR
try:
    r = requests.get("http://localhost:8000/", timeout=5)
    print(f"✅ OCR Service: {r.json()['service']}")
except Exception as e:
    print(f"❌ OCR Service: {e}")
    sys.exit(1)

# Test AI
try:
    r = requests.get("http://localhost:8001/health", timeout=5)
    data = r.json()
    print(f"✅ AI Service: {data['status']} (Ollama: {data['ollama_connected']})")
except Exception as e:
    print(f"❌ AI Service: {e}")
    sys.exit(1)

print("\n✅ All services healthy!")
print("Ready to test Flutter app.")
