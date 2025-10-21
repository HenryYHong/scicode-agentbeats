#!/usr/bin/env python3
"""
Railway.app AgentBeats Agent
Deployable version of SciCode Agent Beats for Railway.app
"""

import os
import json
import sys
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import threading
import time

class RailwayAgentBeatsHandler(BaseHTTPRequestHandler):
    """AgentBeats A2A Protocol handler for Railway deployment"""
    
    def __init__(self, *args, **kwargs):
        self.agent_type = "green"  # SciCode Agent Beats is an orchestrator
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests - agent status and health checks"""
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                "status": "ready",
                "agent_type": self.agent_type,
                "name": "SciCode Agent Beats",
                "capabilities": ["orchestration", "evaluation", "scientific", "a2a"],
                "version": "1.0.0",
                "description": "Scientific code generation agent using multi-agent framework",
                "deployment": "railway"
            }
            self.wfile.write(json.dumps(response).encode())
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"status": "healthy", "timestamp": time.time()}
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        """Handle POST requests - A2A agent interactions"""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            if content_length > 0:
                data = json.loads(post_data.decode('utf-8'))
            else:
                data = {}
            
            # A2A Protocol response following AgentBeats specifications
            response = {
                "status": "success",
                "agent_type": self.agent_type,
                "message": "SciCode Agent Beats ready for orchestration",
                "capabilities": ["orchestration", "evaluation", "scientific", "a2a"],
                "timestamp": time.time(),
                "agent_name": "SciCode Agent Beats"
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_error(500, f"Agent error: {str(e)}")
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {format % args}")

def run_railway_agent():
    """Run AgentBeats agent on Railway"""
    port = int(os.environ.get('PORT', 8000))
    
    print("🚀 Starting SciCode Agent Beats on Railway")
    print("=" * 50)
    print(f"🌐 Server running on port {port}")
    print("🎯 AgentBeats A2A Protocol Ready!")
    
    server_address = ('', port)
    httpd = HTTPServer(server_address, RailwayAgentBeatsHandler)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        httpd.shutdown()

if __name__ == '__main__':
    run_railway_agent()
