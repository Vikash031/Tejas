"""
Local HTTP Server for HAL Tejas Mk1 3D Viewer & GeoFS Test Bed
Serves 3D assets, textures, and aircraft definition with proper CORS and MIME types.
"""

import os
import sys
import http.server
import socketserver
import webbrowser

PORT = 8080
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class GeoFSTestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT_DIR, **kwargs)

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def end_headers(self):
        # Enable CORS and Chrome Private Network Access (PNA)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Access-Control-Allow-Private-Network', 'true')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        super().end_headers()

    def guess_type(self, path):
        if path.endswith(".glb"):
            return "model/gltf-binary"
        if path.endswith(".gltf"):
            return "model/gltf+json"
        if path.endswith(".json"):
            return "application/json"
        return super().guess_type(path)

def run_server():
    os.chdir(ROOT_DIR)
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(("", PORT), GeoFSTestHandler) as httpd:
        url = f"http://localhost:{PORT}/viewer/index.html"
        print("=" * 65)
        print(" HAL TEJAS Mk1 - LOCAL 3D VIEWER & GEOFS SERVER")
        print("=" * 65)
        print(f" [x] Local Server active at: http://localhost:{PORT}")
        print(f" [x] Open 3D Viewer:         {url}")
        print(f" [x] Aircraft Definition:    http://localhost:{PORT}/aircraft.json")
        print(f" [x] Master 3D Model:        http://localhost:{PORT}/export/tejas_mk1.glb")
        print("=" * 65)
        print(" Press Ctrl+C in terminal to stop server.\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")

if __name__ == "__main__":
    run_server()
