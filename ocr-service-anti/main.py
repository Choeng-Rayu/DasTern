#!/usr/bin/env python
"""
Simple entry point to run the OCR Service.
Usage: python main.py [port]
"""

import sys
import os
import uvicorn

# Add parent directory to path so we can import app package
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    
    print(f"🚀 Starting OCR Service on http://127.0.0.1:{port}")
    print(f"📚 API Documentation: http://127.0.0.1:{port}/docs")
    
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=port,
        reload=True,
    )
