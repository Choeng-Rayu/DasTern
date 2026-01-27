#!/usr/bin/env python3
"""
Simple HTTP server for OCR test interface
"""

import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

PORT = 8090
DIRECTORY = Path(__file__).parent

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

if __name__ == "__main__":
    os.chdir(DIRECTORY)
    
    with socketserver.TCPServer(("", PORT), CORSHTTPRequestHandler) as httpd:
        print(f"🌐 OCR Test Interface Server running at:")
        print(f"   http://localhost:{PORT}")
        print(f"   http://127.0.0.1:{PORT}")
        print(f"\n📁 Serving files from: {DIRECTORY}")
        print(f"\n🔗 OCR Service endpoints:")
        print(f"   Simple OCR: http://localhost:8004/ocr/simple")
        print(f"   Full Pipeline: http://localhost:8004/ocr/process")
        print(f"   Health Check: http://localhost:8004/")
        print(f"\n🚀 Opening browser...")
        
        # Try to open browser
        try:
            webbrowser.open(f'http://localhost:{PORT}')
        except:
            pass
            
        print(f"\n⏹️  Press Ctrl+C to stop the server")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print(f"\n🛑 Server stopped")
            httpd.shutdown()
