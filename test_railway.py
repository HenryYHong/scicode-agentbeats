#!/usr/bin/env python3
"""
Simple test server for Railway debugging
"""

import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class TestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = {"status": "test", "message": "Railway test server working"}
        self.wfile.write(json.dumps(response).encode())
    
    def log_message(self, format, *args):
        print(f"TEST: {format % args}")

def run_test_server():
    port = int(os.environ.get('PORT', 8000))
    print(f"🧪 Starting test server on port {port}")
    
    server_address = ('', port)
    httpd = HTTPServer(server_address, TestHandler)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Test server stopped")

if __name__ == '__main__':
    run_test_server()
