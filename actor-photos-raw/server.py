#!/usr/bin/env python3
"""Local server for FD3 face tagger — serves photos + accepts save POSTs."""
import json, os, sys
from http.server import HTTPServer, SimpleHTTPRequestHandler

PHOTO_DIR = os.path.dirname(os.path.abspath(__file__))
MAPPING_PATH = os.path.join(PHOTO_DIR, "fd3-actor-mapping.json")
PORT = 8199

class TaggerHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/save":
            length = int(self.headers["Content-Length"])
            body = self.rfile.read(length)
            data = json.loads(body)
            with open(MAPPING_PATH, "w") as f:
                json.dump(data, f, indent=2)
            count = len(data)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"saved": count, "path": MAPPING_PATH}).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

os.chdir(PHOTO_DIR)
server = HTTPServer(("0.0.0.0", PORT), TaggerHandler)
print(f"🚀 FD3 Tagger server running at:")
print(f"   http://localhost:{PORT}/face-tagger.html")
print(f"   Press Ctrl+C to stop")
server.serve_forever()
