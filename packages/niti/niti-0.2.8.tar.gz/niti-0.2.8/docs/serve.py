#!/usr/bin/env python3
"""
Simple script to build and serve Sphinx documentation locally.
"""

import os
import subprocess
import sys
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import threading
import time

def build_docs():
    """Build the Sphinx documentation."""
    print("Building documentation...")
    result = subprocess.run(["make", "html"], cwd=".", capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Build failed: {result.stderr}")
        return False
    print("Documentation built successfully!")
    return True

def serve_docs(port=9101):
    """Serve the documentation on localhost."""
    build_dir = Path("build/html")
    if not build_dir.exists():
        print("Build directory not found. Please build the docs first.")
        return
    
    os.chdir(build_dir)
    
    class QuietHTTPRequestHandler(SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            # Suppress log messages
            pass
    
    server = HTTPServer(("localhost", port), QuietHTTPRequestHandler)
    print(f"Serving documentation at http://localhost:{port}")
    print("Press Ctrl+C to stop the server")
    
    # Open browser after a short delay
    def open_browser():
        time.sleep(1)
        webbrowser.open(f"http://localhost:{port}")
    
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.shutdown()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--serve-only":
        serve_docs()
    else:
        if build_docs():
            serve_docs()