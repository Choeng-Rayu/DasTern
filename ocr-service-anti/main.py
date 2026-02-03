#!/usr/bin/env python
"""
Simple entry point to run the OCR Service.
Usage: python main.py [port]
"""

import sys
import os
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path so we can import app package
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    # Priority: CLI arg > ENV var > default
    host = os.getenv("OCR_SERVICE_HOST", "127.0.0.1")
    port = int(sys.argv[1]) if len(sys.argv) > 1 else int(os.getenv("OCR_SERVICE_PORT", "8000"))
    
    print(f"🚀 Starting OCR Service on http://{host}:{port}")
    print(f"📚 API Documentation: http://{host}:{port}/docs")
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=True,
    )
